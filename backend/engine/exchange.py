from datetime import datetime
from typing import Dict, List, Optional

from .order_book import OrderBook
from .stock import Stock
from .order import Order
from .trade import Trade
from .trader import Trader


class Exchange:
    """A central exchange for matching buy and sell orders and tracking trade history.

    Responsibilities:
      - Maintain order books for each stock symbol.
      - Enqueue orders arriving from traders.
      - Execute price ticks and process order matching.

    Attributes:
        market_data (Dict[str, Stock]): Current market price and history for each symbol.
        order_books (Dict[str, OrderBook]): Order book per symbol for managing open orders.
        current_time (datetime): Timestamp of the last processed tick.
        order_lookup (Dict[str, Order]): Global order look-up by `order_id`

    Examples:
        >>> from engine.trader import Trader
        >>> data = {"MTKO": Stock("MTKO", 100.0)}
        >>> exchange = Exchange(market_data=data)
        >>> t = Trader(trader_id=1, starting_balance=10000.0)
        >>> o = t.place_order("MTKO", "buy", 42, 10.0)
        >>> exchange.add_order(o)
        >>> exchange.process_tick()
        >>> trades = exchange.match_orders("MTKO")
    """

    def __init__(
        self,
        market_data: Dict[str, Stock],
    ):
        """Initialize the Exchange with market data and prepare order books.

        Examples:
            >>> data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
            >>> exchange = Exchange(market_data=data)
        """
        self.traders: Dict[int, Trader] = {}
        self.market_data = market_data
        self.order_books: Dict[str, OrderBook] = {
            symbol: OrderBook() for symbol in market_data.keys()
        }
        self.order_lookup: Dict[str, Order] = {}
        self.current_time = datetime.now()

    def add_order(self, order: Order) -> None:
        """Enqueue an Order in its respective order book for later matching.

        Args:
            order (Order): The order to add to the order book.

        Examples:
            >>> data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
            >>> exchange = Exchange(market_data=data)
            >>> o = Order(trader_id=1,symbol="AAPL",order_type="buy", quantity=42, limit_price=100.0)
            >>> exchange.add_order(o)
            >>> exchange.order_books["AAPL"].buy_size()
            1
        """
        if order.symbol not in self.market_data:
            raise KeyError(f"The symbol does not exist")

        self.order_books[order.symbol].add_order(order)
        self.order_lookup[order.order_id] = order

    def cancel_order(self, order_id: str) -> bool:
        """Mark `order` as cancelled.

        The order will not be processed by the matching engine.

        Attributes:
            order_id (Order): `order_id` of `Order` to be cancelled
        
        Returns:
            (bool): True if order has been cancelled, false if failed to cancel (already filled).
        """
        if order_id not in self.order_lookup:
            raise KeyError(f"An order with this `order_id` does not exist. (got {order_id})")

        order = self.order_lookup[order_id]

        if order.status != "filled":
            order.status = "cancelled"

        return order.status == "cancelled"   

    

    def register_trader(self, trader: Trader) -> None:
        """Register trader in a stock exchange"""
        if trader.trader_id in self.traders:
            raise ValueError(f"Trader ID {trader.trader_id} already registered")

        self.traders[trader.trader_id] = trader

    def process_tick(
        self,
    ) -> None:
        """Advance the exchange clock and update market prices based on stocks.

        Examples:
        >>> data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
        >>> exchange = Exchange(market_data=data)
        >>> before = [s.price for s in exchange.market_data.values()]
        >>> exchange.process_tick()
        >>> after = [s.price for s in exchange.market_data.values()]
        >>> any(b != a for b, a in zip(before, after))
        True
        """
        self.current_time = datetime.now()

        for stock in self.market_data.values():
            nxt = stock.simulate_price_tick()
            stock.update_price(nxt)

    def match_orders(self, symbol: str) -> List[Trade]:
        """Match buy and sell orders in the specified symbol's order book.

        Args:
            symbol (str): The stock symbol for which to perform matching.

        Returns:
            List[Trade]: Empty list but later in the project list of executed trades for this symbol.

        Examples:
            >>> data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
            >>> exchange = Exchange(market_data=data)
            >>> o = Order(trader_id=1,symbol="AAPL",order_type="buy", quantity=42, limit_price=100.0)
            >>> exchange.add_order(o)
            >>> exchange.match_orders("AAPL")
            []
        """

        order_book = self.order_books.get(symbol)
        trades: List[Trade] = []

        while True:
            best_buy, best_sell = (
                order_book.peek_best_buy(),
                order_book.peek_best_sell(),
            )
            

            print(f"Buy size: {order_book.buy_size()}")
            print(f"Sell size: {order_book.sell_size()}")

            if not best_buy or not best_sell:
                break

            if best_buy.limit_price < best_sell.limit_price:
                break

            # 1) Decide taker (the one that arrived later)
            if (best_buy.timestamp, best_buy.sequence) > (
                best_sell.timestamp,
                best_sell.sequence,
            ):
                taker_side = "buy"
                taker = best_buy
                maker_peek = order_book.peek_best_sell
                maker_pop = order_book.pop_best_sell
                maker_push = order_book.add_order
                price_cross = lambda m: taker.limit_price >= m.limit_price
                exec_price = lambda m: m.limit_price
            else:
                taker_side = "sell"
                taker = best_sell
                maker_peek = order_book.peek_best_buy
                maker_pop = order_book.pop_best_buy
                maker_push = order_book.add_order
                price_cross = lambda m: m.limit_price >= taker.limit_price
                exec_price = lambda m: m.limit_price
            
            # 2) Scan the maker heap for a valid counterparty
            skipped: List[Order] = []
            maker: Optional[Order] = None
            while taker.quantity > 0:
                candidate = maker_peek()
                if not candidate or not price_cross(candidate):
                    break

                maker_pop()
                if candidate.trader_id == taker.trader_id:
                    # same trader → buffer and keep scanning
                    skipped.append(candidate)
                    continue

                maker = candidate
                break

            # 3) No valid maker found → restore and exit
            if maker is None:
                for o in skipped:
                    maker_push(o)
                break

            print(f"Buy size: {order_book.buy_size()}")
            print(f"Sell size: {order_book.sell_size()}")

            # 4) Execute the trade
            if taker_side == "buy":
                best_buy, best_sell = taker, maker
            else:
                best_buy, best_sell = maker, taker

            orig_buy_qty = best_buy.quantity
            orig_sell_qty = best_sell.quantity
            exec_qty = min(orig_buy_qty, orig_sell_qty)
            exec_price = best_sell.limit_price

            new_trade = Trade(
                best_buy,
                best_sell,
                symbol,
                exec_qty,
                exec_price,
                orig_buy_qty,
                orig_sell_qty,
            )

            best_buy.quantity -= exec_qty
            best_sell.quantity -= exec_qty

            # If any side has still shares, reinsert it
            for order in [best_buy, best_sell]:
                if order.quantity > 0:
                    order.status = "partially_filled"
                    if order == maker:
                        order_book.add_order(order)
                else:
                    order.status = "filled"
                    if order != maker:
                        if order.order_type == "buy":
                            order_book.pop_best_buy()
                        else:
                            order_book.pop_best_sell()

            seller_id, buyer_id = best_sell.trader_id, best_buy.trader_id

            seller, buyer = self.traders[seller_id], self.traders[buyer_id]

            seller.update_portfolio(new_trade), buyer.update_portfolio(new_trade)

            trades.append(new_trade)

            # 6) Restore any skipped same‐trader orders
            for o in skipped:
                order_book.add_order(o)

        return trades

    def verify_symbol(self, symbol) -> None:
        if symbol not in self.market_data:
            raise KeyError(f"The symbol '{symbol}' does not exist")
