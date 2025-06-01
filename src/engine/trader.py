from typing import List, Optional
from .order import Order
from .portfolio import Portfolio
from .trade import Trade


class Trader:
    """Represents a market participant with cash balance and equity holdings.

    Allows a trader to place buy/sell orders and tracks cash, holdings, and transaction history.

    Attributes:
        trader_id (int): A unique trader identifier.
        starting_balance (float): Initial cash for deposit.
        holdings (Dict[str, int]): A map of the trader's stock holdings.
        transaction_log (List[Order]): List of previous transactions.

    Examples:
        >>> t = Trader(trader_id=1, starting_balance=10000.0)
        >>> o = t.place_order("MTKO", "buy", 42, 999.0)
    """

    def __init__(
        self,
        trader_id: int,
        starting_balance: float,
    ):
        """Initialize trader with ID and starting cash.

        Holdings and transaction_log start empty.

        Examples:
        >>> t = Trader(trader_id=1, starting_balance=10000.0)
        >>> o = t.place_order("MTKO", "buy", 42, 999.0)
        """
        self.trader_id = trader_id
        self.portfolio = Portfolio(starting_balance)
        self.transaction_log: List[Order] = []

    def place_order(
        self, symbol: str, order_type: str, quantity: int, price: Optional[float]
    ) -> Order:
        """Create a new Order for this trader.

        Args:
            symbol (str): Stock ticker, e.g. "AAPL".
            order_type (str): "buy" or "sell".
            quantity (int): Shares to trade; must be > 0.
            price (Optional[float]): Limit price, or None for market order.

        Returns:
            Order: the created order instance.

        Raises:
            ValueError: If quantity <= 0 or order_type is invalid.

        Note:
            Caller must enqueue the returned Order with Exchange.add_order().

        Examples:
        >>> from engine.exchange import Exchange
        >>> from engine.stock import Stock
        >>> data = {"MTKO": Stock("MTKO", 100.0)}
        >>> exchange = Exchange(market_data=data)
        >>> t = Trader(trader_id=1, starting_balance=10000.0)
        >>> o = t.place_order("MTKO", "buy", 42, 999.0)
        >>> exchange.add_order(o)
        """

        if quantity <= 0:
            raise ValueError(f"quantity must be > 0 (got {quantity})")

        if order_type not in ("buy", "sell"):
            raise ValueError(f"order_type must be 'buy' or 'sell' (got {order_type!r})")

        return Order(
            trader_id=self.trader_id,
            symbol=symbol,
            order_type=order_type,
            quantity=quantity,
            limit_price=price,
        )

    def update_portfolio(
        self, trade: Trade, executed_qty: int, execution_price: float
    ) -> None:
        """Update portfolio based on a filled trade.

        Args:
            trade (Trade): a matched trade containing buy_order, sell_order, quantity, price.
        """
        # This method should:
        #  - If this trader was the buyer: deduct (trade.quantity x trade.price) from cash, and increase holdings[trade.symbol] by trade.quantity.
        #  - If this trader was the seller: add (trade.quantity x trade.price) to cash, and decrease holdings[trade.symbol] by trade.quantity.

        raise NotImplementedError("update_portfolio is not yet implemented")
