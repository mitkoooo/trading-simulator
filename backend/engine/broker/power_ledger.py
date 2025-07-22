from typing import Dict, Optional
from math import log1p

from engine.exchange.exchange import Exchange
from engine.position import Position
from engine.trader import Trader
from engine.order_book.order import Order

class PowerLedger:
    """Manage reservations of cash and shares for orders.

    The PowerLedger tracks reserved cash for buy orders and reserved shares
    for sell orders, ensuring that funds or holdings are set aside when orders
    are submitted and released when orders are cancelled or filled.

    Attributes:
        exchange (Exchange): The matching engine providing order books and market data.
        traders (Dict[int, Trader]): Mapping of trader IDs to `Trader` objects with portfolios.
        _reserved_cash (Dict[str, float]): Maps order IDs to the amount of cash reserved for buy orders.
        _reserved_shares (Dict[str, int]): Maps order IDs to the quantity of shares reserved for sell orders.
    """
    def __init__(self, exchange: Exchange, traders: Dict[str, Trader]):
        self.exchange = exchange
        self.traders = traders

        self._reserved_cash: Dict[str, float] = {}    # order_id -> cash amount
        self._reserved_shares: Dict[str, int] = {}    # order_id -> share number


    def reserve_cash(self, trader_id: str, order: Order) -> None:
        """Reserve cash for a new buy order.

        Deducts an estimated cost from the trader’s cash balance and reserves
        it under the order ID.

        Args:
            order (Order): A buy order requiring cash reservation.

        Raises:
            KeyError: If the trader is not registered.
            ValueError: If `order.order_type` is not 'buy' or if the trader’s
                cash balance is insufficient.
        """       
        trader = self.traders.get(trader_id, None)
        if not trader:
            raise KeyError(f"Trader with this trader id does not exist. (got {trader_id}")

        if order.order_type != "buy":
            raise ValueError("Cannot reserve cash for a sell order.")
       
        quantity = order.quantity
        limit_price = order.limit_price
        symbol = order.symbol

        cost_estimate = quantity * limit_price if limit_price else self.estimate_market_buy_cost(symbol, quantity)
        
        if trader.portfolio.cash < cost_estimate:
            raise ValueError("Insufficient cash to place buy order.")
        # Reserve cash
        trader.portfolio.cash -= cost_estimate
        self._reserved_cash[order.order_id] = cost_estimate

        return


    def release_cash(self, trader_id:str,  order: Order) -> None:
        """Release reserved cash back to the trader’s balance.

        Returns the full reserved amount for the given buy order ID to the
        trader’s cash, removing the reservation record.

        Args:
            order (Order): A previously reserved buy order.

        Raises:
            KeyError: If the trader is not registered
        """
        trader = self.traders.get(trader_id, None)
        if not trader:
            raise KeyError(f"Trader with this trader id does not exist. (got {trader_id}")

        
        reserved_amount = self._reserved_cash.pop(order.order_id)
        trader.portfolio.cash += reserved_amount

        return


    def reserve_shares(self, trader_id: str, order: Order) -> None:
        """Reserve shares for a new sell order.

        Deducts the order’s quantity from the trader’s position and reserves
        it under the order ID.

        Args:
            order (Order): A sell order requiring share reservation.

        Raises:
            KeyError: If the trader is not registered or does not hold the shares.
            ValueError: If `order.order_type` is not 'sell' or the trader’s
                position is insufficient.
        """
        trader = self.traders.get(trader_id, None)
        if not trader:
            raise KeyError(f"Trader with this trader id does not exist. (got {trader_id}")

        if order.order_type != "sell":
            raise ValueError("Cannot reserve shares for a buy order.")

        quantity = order.quantity
        symbol = order.symbol
        position = trader.portfolio.positions.get(symbol, None)
        
        if not position:
            raise KeyError("Cannot reserve shares that the trader does not own.")

        held = position.qty

        if held < quantity:
            raise ValueError("Insufficient shares to place sell order.")

        trader.portfolio.positions[symbol].qty -= quantity

        self._reserved_shares[order.order_id] = self._reserved_shares.get(order.order_id, 0) + quantity

        return


    def release_shares(self, trader_id:str, order: Order) -> None:
        """Release reserved shares back to the trader’s position.

        Returns the full reserved share quantity for the given sell order
        back to the trader’s position, removing the reservation record.

        Args:
            order (Order): A previously reserved sell order.

        Raises:
            KeyError: If the trader is not registered.
        """        
        trader = self.traders.get(trader_id, None)
        if not trader:
            raise KeyError(f"Trader with this trader id does not exist. (got {trader_id}")

        symbol = order.symbol
        position: Position | None = trader.portfolio.positions.get(symbol)
        reserved_quantity: int = self._reserved_shares.pop(order.order_id)

        if not position:
            raise KeyError("Cannot unreserve the shares that the trader does not own.")

        position.qty += reserved_quantity

        return 


    def estimate_market_buy_cost(self, symbol: str, quantity: int):
        """Estimate the total cost of a market-price buy order.

        Walks the sell-side order book until the requested quantity is covered,
        summing limit prices, then applies a slippage buffer.

        Args:
            symbol (str): The stock symbol to buy.
            quantity (int): The number of shares to estimate.

        Returns:
            float: Estimated cost including slippage buffer.

        Raises:
            ValueError: If book liquidity is insufficient to fill the request.
        """
        order_book = self.exchange.order_books.get(symbol, None)
        assert order_book
        # Not the most efficient method. If later causes problems,
        # try to approximate n based of quantity and order_book statistics
        sell_orders = order_book.get_n_sell_orders()

        remaining = quantity
        expected_cost = 0.0
        
        for sell in sell_orders:
            if sell.limit_price is None: # Market price sells dont contribute information
                continue

            fill_quantity = min(remaining, sell.quantity)
            expected_cost += fill_quantity * sell.limit_price
            remaining -= fill_quantity

            if remaining <= 0:
                break

        if remaining > 0:
            raise ValueError("Not enough market surplus liquidity to estimate cost.")

        return expected_cost * (1 + self._compute_slippage_buffer(symbol))

    def _compute_slippage_buffer(self, symbol: str) -> float:
        """Compute a safety margin for market‐buy cost estimates.

        Calculates a slippage buffer based on baseline percentage, current
        volatility, and book depth.

        Args:
            symbol (str): The stock symbol for which to compute slippage.

        Returns:
            float: A slippage factor (e.g. between 0.01 and 0.05).
        """
        BASE_LINE = 0.01

        stock = self.exchange.market_data.get(symbol, None)
        assert stock
        order_book = self.exchange.order_books.get(symbol, None)
        assert order_book

        # Scale depth to [0, 1]-ish range using log
        liquidity_penalty = 1 / (1 + log1p(order_book.sell_size())) # shrinks fast
        
        slippage_buffer = BASE_LINE + stock.volatility * liquidity_penalty

        return min(slippage_buffer, 0.05) # cap at 5%

    def get_reserved_shares(self, order_id: str) -> Optional[int]:
        """Get the quantity of shares reserved for a given order ID.

        Args:
            order_id (str): The identifier of the sell order.

        Returns:
            int or None: Reserved share count, or None if no reservation exists.
        """
        return self._reserved_shares.get(order_id, None)

    def get_reserved_cash(self, order_id: str) -> Optional[float]:
        """Get the amount of cash reserved for a given order ID.

        Args:
            order_id (str): The identifier of the buy order.

        Returns:
            float or None: Reserved cash amount, or None if no reservation exists.
        """
        return self._reserved_cash.get(order_id, None)
