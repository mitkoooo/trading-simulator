from datetime import datetime
from typing import Callable, Dict, Iterable, Optional

from engine.order_book.order import Order
from engine.order_book.order_book import OrderBook
from engine.order_book.price_level import PriceLevel

from .stock import Stock
from .trade import Trade


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
            raise KeyError("The symbol does not exist")
        
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
            self.remove_order(order_id)
            

        return order.status == "cancelled"   

    def remove_order(self, order_id: str) -> None:
        order = self.order_lookup[order_id]
        self.order_books[order.symbol].remove_order(order)

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

    def match_orders(self, symbol: str) -> Optional[Trade]:
        """Match buy and sell orders in the specified symbol's order book.

        Args:
            symbol (str): The stock symbol for which to perform matching.

        Returns:
            Trade or None: Executed trade or `None` if no suitable match_orders

        Examples:
            >>> data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
            >>> exchange = Exchange(market_data=data)
            >>> o = Order(trader_id=1,symbol="AAPL",order_type="buy", quantity=42, limit_price=100.0)
            >>> exchange.add_order(o)
            >>> exchange.match_orders("AAPL")
            []

        """
        order_book = self.order_books.get(symbol, None)
        
        if not order_book:
            raise KeyError(f"No existing order book for this symbol. (got {symbol})")

        t_n_p = self._select_taker_and_predicate(order_book)

        if t_n_p is None:
            return None
        taker, maker_levels, price_cross = t_n_p
    
        maker = self._find_maker(taker, maker_levels, price_cross)

        # No valid maker found → restore and exit
        if maker is None:
            return None
        
        # Build the trade
        return self._build_trade(taker, maker, symbol)


    def _select_taker_and_predicate(self, order_book: OrderBook) -> Optional[
    tuple[Order, Iterable[PriceLevel], Callable[[Order], bool]]]:
        """Decide which side provides the taker order and return:
        - taker_side: "buy" or "sell"
        - taker: the Order object
        - maker_levels: the sequence of PriceLevel buckets to scan
        - price_cross: predicate testing whether a candidate crosses the taker’s price
        """
        mb = order_book.market_buys.peek()
        ms = order_book.market_sells.peek()
        if mb or ms:
            if not ms or (mb and ms and (mb.timestamp, mb.sequence) < (ms.timestamp, ms.sequence)):
                taker = mb
                maker_levels = order_book._sell_levels.values()
                assert taker
            else:
                taker = ms
                maker_levels = order_book._buy_levels.values()
                assert taker
            price_cross = lambda m: True

            return (taker, maker_levels, price_cross)
        else:
            best_buy, best_sell = (
                order_book.peek_best_buy(),
                order_book.peek_best_sell(),
            )
        
            if not best_buy or not best_sell:
                return None

            if (
                best_buy.limit_price is not None and 
                best_sell.limit_price is not None and 
                best_buy.limit_price < best_sell.limit_price
            ):
                return None

            buy_is_later = (best_buy.timestamp, best_buy.sequence) > (best_sell.timestamp, best_sell.sequence)
                
            # Decide taker (the one that arrived later)
            if buy_is_later:
                taker = best_buy
                maker_levels = order_book._sell_levels.values()
                price_cross = lambda m: taker.limit_price >= m.limit_price if taker.limit_price else True
            elif not buy_is_later:
                taker = best_sell
                maker_levels = order_book._buy_levels.values()
                price_cross = lambda m: m.limit_price >= taker.limit_price if taker.limit_price else True
            else:
                raise RuntimeError("No valid taker could be determined")

            return (taker, maker_levels, price_cross)

    def _find_maker(self, taker: Order, maker_levels: Iterable[PriceLevel], price_cross: Callable[[Order], bool]) -> Optional[Order]:
        """Walk price levels in priority order, then within each level walk FIFO,
        skipping same‐trader and non‐crossing orders.  Returns the first valid maker
        or None if no match exists.
        """
        maker = None

        for lvl in maker_levels:
            for candidate in lvl:
                if not price_cross(candidate):
                    break

                if candidate.trader_id == taker.trader_id:
                    # same trader → buffer and keep scanning
                    continue

                maker = candidate
                break
            if maker:
                break

        return maker

    def _build_trade(self, taker: Order, maker: Order, symbol: str) -> Trade:
        """Compute exec_qty and exec_price (with error if price is None),
        adjust quantities on the two orders, and return a Trade object.
        """
        if taker.order_type == "buy":
            best_buy, best_sell = taker, maker
        else:
            best_buy, best_sell = maker, taker

        orig_buy_qty = best_buy.quantity
        orig_sell_qty = best_sell.quantity
        exec_qty = min(orig_buy_qty, orig_sell_qty)
        exec_price = maker.limit_price

        if not exec_price:
            raise ValueError("Execution price unexpectedly None")

        new_trade = Trade(
            best_buy,
            best_sell,
            symbol,
            exec_qty,
            exec_price,
        )

        best_buy.quantity -= exec_qty
        best_sell.quantity -= exec_qty

        return new_trade

        

    def verify_symbol(self, symbol) -> None:
        if symbol not in self.market_data:
            raise KeyError(f"The symbol '{symbol}' does not exist")
