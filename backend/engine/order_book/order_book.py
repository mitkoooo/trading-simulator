from typing import List, Optional, Literal
from sortedcontainers import SortedDict


from engine.order_book.market_order_queue import MarketOrderQueue
from engine.order_book.order import Order
from engine.order_book.price_level import PriceLevel


class OrderBook:
    """Maintain buy‐side and sell‐side priority queues for order matching.

    Hold two sorted maps of price levels to FIFO queues for limit orders and
    two FIFO queues for market orders, ensuring that the highest buy order and
    lowest sell order are always considered first.

    Attributes:
        _buy_levels (SortedDict[float, PriceLevel]):
            Maps buy prices (highest first) to their FIFO `PriceLevel` queues.

        _sell_levels (SortedDict[float, PriceLevel]):
            Maps sell prices (lowest first) to their FIFO `PriceLevel` queues.

        market_buys (MarketOrderQueue):
            FIFO queue of market‐buy orders in arrival order.

        market_sells (MarketOrderQueue):
            FIFO queue of market‐sell orders in arrival order.

        _global_sequence (int):
            Sequential counter given to `Order` on enqueue.

    Example:
        >>> from engine.order_book import OrderBook
        >>> from engine.order_book.order import Order
        >>> ob = OrderBook()
        >>> o = Order(trader_id=1, symbol="MTKO", order_type="buy",
        ...           quantity=2, limit_price=999.0)
        >>> ob.add_order(o)
        >>> ob.buy_size()
        1
    """

    def __init__(self):
        """Initialize `OrderBook` with limit order maps and market queues.

        Sets up two `SortedDict` instances for buy and sell limit orders,
        each mapping price levels to `PriceLevel` queues,
        and two FIFO `MarketOrderQueue`s for market orders.
        Also initializes the global sequence counter for tie‐breaking.

        Attributes:
            _buy_levels (SortedDict[float, PriceLevel]):
                Descending‐key map of bid prices to `PriceLevel` queues.
            _sell_levels (SortedDict[float, PriceLevel]):
                Ascending‐key map of ask prices to `PriceLevel` queues.
            market_buys (MarketOrderQueue):
                FIFO queue for market‐buy orders.
            market_sells (MarketOrderQueue):
                FIFO queue for market‐sell orders.
            _global_sequence (int):
                Monotonic counter assigned to each enqueued order.
        """
        buy_dict = SortedDict(lambda p: -p)
        sell_dict = SortedDict()

        self._buy_levels: SortedDict[float, PriceLevel] = buy_dict
        self._sell_levels: SortedDict[float, PriceLevel] = sell_dict
        self.market_buys = MarketOrderQueue()
        self.market_sells = MarketOrderQueue()

        self._global_sequence = 0
        self.last_trade_price: Optional[float] = None

    def _get_market_order_queue(self,
                                side: Literal["buy", "sell"]
                                ) -> MarketOrderQueue:
        """Retrieve the FIFO queue for market orders on the specified side."""
        return self.market_buys if side == "buy" else self.market_sells

    def _get_level(self, side: Literal["buy", "sell"], price: float,
                   create: bool = False) -> Optional[PriceLevel]:
        """Fetch or optionally create the `PriceLevel` at `price` from `side`.

        Args:
            side ("buy" or "sell"):
                Indicates which side’s limit‐order map to query.

            price (float):
                The limit price level to look up.

            create (bool):
                If `True`, create and insert `PriceLevel` if none exists.

        Returns:
            PriceLevel or None:
                The existing (or newly created, if `create` is `True`)
        """
        levels = self._buy_levels if side == "buy" else self._sell_levels
        lvl: PriceLevel | None = levels.get(price, None)
        if lvl or not create:
            return lvl
        # create price level on demand
        lvl = PriceLevel()
        levels[price] = lvl

        return lvl

    def add_order(self, order: Order) -> None:
        """Enqueue an order into the appropriate market or limit queue.

        Assigns a global sequence number to the order for tie‐breaking, then:
        - If `order.limit_price` is `None`, adds to its market queue.
        - Otherwise, adds to the `PriceLevel` queue for its limit price.

        Args:
            order (Order):
                The order to enqueue. Its `sequence` attribute will be set.

        Raises:
            ValueError:
                If a new PriceLevel cannot be created (should never occur).

        Example:
            >>> ob = OrderBook()
            >>> o = Order(trader_id=1, symbol="AAPL",
            ...           order_type="buy", quantity=10, limit_price=150.0)
            >>> ob.add_order(o)
            >>> ob.peek_best_buy() is o
            True
        """

        side: Literal["buy", "sell"] = order.order_type
        price = order.limit_price
        order.sequence = self._global_sequence
        self._global_sequence += 1

        if not price:
            market_order_queue = self._get_market_order_queue(side)
            market_order_queue.enqueue(order)
            return

        lvl = self._get_level(side, price, create=True)
        assert lvl is not None, "PriceLevel creation failed unexpectedly"

        lvl.enqueue(order)

        return

    def remove_order(self, order: Order) -> None:
        """Remove an existing order from the book’s queues.

        Removes the given order from its market or limit queue. If the order
        was filled or cancelled, it will be dropped entirely;
        if it was at the head of its limit queue, that queue is dequeued;
        else it is removed from its PriceLevel. Empty price levels are deleted.

        Args:
            order (Order): The order to remove.

        Example:
            >>> ob = OrderBook()
            >>> o = Order(trader_id=1, symbol="AAPL",
            ...           order_type="sell", quantity=5, limit_price=100.0)
            >>> ob.add_order(o)
            >>> ob.remove_order(o)
            >>> ob.peek_best_sell() is None
            True
        """
        side: Literal["buy", "sell"] = order.order_type
        price = order.limit_price

        if not price:
            market_order_queue = self._get_market_order_queue(side)

            if order == market_order_queue.peek():
                market_order_queue.dequeue()
            else:
                market_order_queue.remove(order)
            return

        lvl = self._get_level(side, price)
        assert lvl is not None, "PriceLevel creation failed unexpectedly"

        if order == lvl.peek():
            lvl.dequeue()
        else:
            lvl.remove(order)

        if lvl.is_empty():
            if side == "buy":
                del self._buy_levels[price]
            else:
                del self._sell_levels[price]

        return

    def peek_best_buy(self) -> Optional[Order]:
        """Return the highest-price sell order without removing it.

        Returns:
            The Order with the highest limit_price, or None if no buy orders.

        Examples:
        >>> from engine.order import Order
        >>> from engine.order_book import OrderBook
        >>> ob = OrderBook()
        >>> o = Order(trader_id=1, symbol="AAPL", order_type="buy",
        >>>           quantity=10, limit_price=150.0)
        >>> ob.add_order(o)
        >>> ob.peek_best_buy() == o
        True
        """

        if not self._buy_levels:
            return None

        _, lvl = self._buy_levels.peekitem(0)

        return lvl[0]

    def peek_best_sell(self) -> Optional[Order]:
        """Return the lowest-price sell order without removing it.

        Returns:
            The Order with the lowest limit_price, or None if no sell orders.

        Examples:
        >>> from engine.order import Order
        >>> from engine.order_book import OrderBook
        >>> ob = OrderBook()
        >>> o = Order(trader_id=1, symbol="AAPL", order_type="sell",
        >>>           quantity=10, limit_price=150.0)
        >>> ob.add_order(o)
        >>> ob.peek_best_sell() == o
        True
        """
        if not self._sell_levels:
            return None

        _, lvl = self._sell_levels.peekitem(0)

        return lvl[0]

    def pop_best_buy(self) -> Optional[Order]:
        """
        Remove and return the highest-price buy order.

        Returns:
            The Order with the highest limit_price, or None if no buy orders.

        Examples:
        >>> from engine.order import Order
        >>> from engine.order_book import OrderBook
        >>> ob = OrderBook()
        >>> o = Order(trader_id=1, symbol="AAPL", order_type="buy",
        >>>           quantity=10, limit_price=150.0)
        >>> ob.add_order(o)
        >>> ob.pop_best_buy() == o
        True
        >>> ob.buy_size() == 0
        True
        """
        if not self._buy_levels:
            return None

        price, lvl = self._buy_levels.peekitem(0)

        order = lvl.dequeue()

        if lvl.is_empty():
            del self._buy_levels[price]

        return order

    def pop_best_sell(self) -> Optional[Order]:
        """Remove and return the lowest-price sell order.

        Returns:
            The Order with the lowest limit_price, or None if no sell orders.

        Examples:
        >>> from engine.order import Order
        >>> from engine.order_book import OrderBook
        >>> ob = OrderBook()
        >>> o = Order(trader_id=1, symbol="AAPL", order_type="sell",
        >>>           quantity=10, limit_price=150.0)
        >>> ob.add_order(o)
        >>> ob.pop_best_sell() == o
        True
        >>> ob.sell_size() == 0
        True
        """
        if not self._sell_levels:
            return None

        price, lvl = self._sell_levels.peekitem(0)

        order = lvl.dequeue()

        if lvl.is_empty():
            del self._sell_levels[price]

        return order

    def buy_size(self) -> int:
        """Return the number of buy orders currently in the book."""
        total = 0

        for price_level in self._buy_levels.values():
            total += len(price_level)

        return total + len(self.market_buys)

    def sell_size(self) -> int:
        """Return the number of sell orders currently in the book."""
        total = 0

        for price_level in self._sell_levels.values():
            total += len(price_level)

        return total + len(self.market_sells)

    @property
    def total_size(self) -> int:
        """Return the total number of orders (buy + sell)."""
        return self.buy_size() + self.sell_size()

    def get_n_buy_orders(self, n=None) -> List[Order]:
        """Return a list of highest `n` limit buy orders.

        Examples:
            >>> from engine.order_book import OrderBook
            >>> from engine.order import Order
            >>> ob = OrderBook()
            >>> o1 = Order(trader_id=1, symbol="AAPL", order_type="buy",
            >>>            quantity=5, limit_price=50.0)
            >>> o2 = Order(trader_id=2, symbol="AAPL", order_type="buy",
            >>>            quantity=1, limit_price=55.0)
            >>> ob.add_order(o1)
            >>> ob.add_order(o2)
            >>> buys = ob.get_buy_orders()
            >>> [o.limit_price for o in buys]
            [55.0, 50.0]
        """
        if n and n <= 0:
            msg = """Cannot get 0 or less orders
                     from the top of the order book"""
            raise KeyError(msg)

        out = []

        for lvl in self._buy_levels.values():
            for order in lvl:
                out.append(order)
                if len(out) == n:
                    break

        return out

    def get_n_sell_orders(self, n=None) -> List[Order]:
        """
        Return list of lowest `n` limit sell orders currently in the book.

        Examples:
            >>> from engine.order_book import OrderBook
            >>> from engine.order import Order
            >>> ob = OrderBook()
            >>> o1 = Order(mpid="BR01", symbol="AAPL", order_type="sell",
            >>>            quantity=5, limit_price=50.0)
            >>> o2 = Order(mpid="BR01", symbol="AAPL", order_type="sell",
            >>>            quantity=1, limit_price=55.0)
            >>> ob.add_order(o1)
            >>> ob.add_order(o2)
            >>> sells = ob.get_n_sell_orders()
            >>> [o.limit_price for o in sells]
            [50.0, 55.0]
        """
        if n and n <= 0:
            msg = """Cannot get 0 or less orders
                     from the top of the order book"""
            raise KeyError(msg)

        out = []

        for lvl in self._sell_levels.values():
            for order in lvl:
                out.append(order)
                if len(out) == n:
                    break

        return out

    def __repr__(self) -> str:
        parts = ["OrderBook("]

        # Show head of book
        bid = self.peek_best_buy()
        ask = self.peek_best_sell()

        if bid:
            detail = f"""  best_buy={bid.limit_price!r}@{bid.quantity!r}"""
        else:
            detail = "best_buy=None"
        parts.append(detail)

        if ask:
            detail = f"""  best_sell={ask.limit_price!r}@{ask.quantity!r}"""
        else:
            detail = "best_sell=None"
        parts.append(detail)

        # Show queue depths (optional)
        mb_len = len(self.market_buys)
        ms_len = len(self.market_sells)
        parts.append(f"  market_buys={mb_len} orders")
        parts.append(f"  market_sells={ms_len} orders")

        # Maybe show number of price levels
        parts.append(f"  buy_levels={len(self._buy_levels)} price levels")
        parts.append(f"  sell_levels={len(self._sell_levels)} price levels")

        parts.append(")")
        return "\n".join(parts)
