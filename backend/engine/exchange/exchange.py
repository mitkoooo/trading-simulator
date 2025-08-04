import asyncio
from collections.abc import Callable
from datetime import datetime

from engine.exchange.participant_info import ParticipantInfo
from engine.exchange.risk_gateway import RiskGateway
from engine.instruments.stock import Stock
from engine.market_data.quote import MarketQuote
from engine.order_book.order import Order
from engine.order_book.order_book import OrderBook
from engine.order_book.price_level import PriceLevel
from engine.trade import Trade


class Exchange:
    """A central entity matching buy/sell orders and tracking trade history.

    Responsibilities:
      - Maintain order books for each stock symbol.
      - Enqueue orders arriving from traders.
      - Execute price ticks and process order matching.

    Attributes:
        market_data (Dict[str, Stock]):
            Current market price and history for each symbol.

        order_books (Dict[str, OrderBook]):
            Order book per symbol for managing open orders.

        current_time (datetime):
            Timestamp of the last processed tick.

        order_lookup (Dict[str, Order]):
            Global order look-up by `order_id`

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

    def __init__(self) -> None:
        """Initialize the Exchange with market data and prepare order books.

        Examples:
            >>> data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
            >>> exchange = Exchange(market_data=data)

        """
        self.name: str = "GhostSwap"
        self.instruments: dict[str, Stock] = {}
        self.order_books: dict[str, OrderBook] = {}
        self.market_participants: dict[str, ParticipantInfo] = {}

        self._book_queues: dict[str, asyncio.Queue[tuple[str, Order]]] = {}
        self._book_tasks: list[asyncio.Task] = []

        self.trade_num: tuple = (0, datetime.now())
        self.avg_service_time = 0

        self.risk_gateaway = RiskGateway()

        self.order_lookup: dict[str, Order] = {}
        self.quotes: dict[str, MarketQuote] = {}
        self._subscriptions: dict[str, list[Callable]] = {}

        self.current_time = datetime.now()

    def register_instrument(self, stock: Stock) -> None:
        """Register a new instrument on the exchange.

        Args:
            stock (Stock): Capital stock of the company.
        
        Raises:
            (KeyError): If instrument already registered.

        """
        if stock.symbol in self.instruments:
            msg = f"Instrument already registered. got ({stock.symbol})"
            raise KeyError(msg)

        self.instruments[stock.symbol] = stock
        self.order_books[stock.symbol] = OrderBook()
        self._book_queues[stock.symbol] = asyncio.Queue()

    def register_participant(self, mpid: str, info: ParticipantInfo) -> None:
        """Register a new market participant on the exchange.

        Args:
            mpid (str):
                A unique market participant identifier.
            info (ParticipantInfo):
                Permissions and information about market participant.

        Raises:
            (KeyError): If market participant is already registered.

        """
        mp = self.market_participants.get(mpid, None)
        if mp:
            msg = f"The market participant with {mpid} is already registered."
            raise KeyError(msg)
        else:
            self.market_participants[mpid] = info

    def start(self) -> None:
        """Boot the exchange to process and route orders.

        Under the hood create book worker `asyncio.Task` for each symbol.
        """
        for symbol, queue in self._book_queues.items():
            task = asyncio.create_task(self._book_worker(symbol, queue))
            self._book_tasks.append(task)

    async def stop(self) -> None:
        """Stop the exchange from processing and routing orders.

        Under the hood cancel all book worker `asyncio.Task`.
        """
        for t in self._book_tasks:
            t.cancel()
        await asyncio.gather(*self._book_tasks, return_exceptions=True)

    async def _book_worker(self, symbol: str, queue: asyncio.Queue) -> None:
        """Process a symbol's order book events from an internal queue.

        Args:
            symbol (str):
                Ticker symbol (e.g. AAPL or MSFT).

            queue (asyncio.Queue):
                An `asyncio.Queue` yielding tuples of (cmd, order), 
                where cmd is "add" or "remove" and order is the `Order`.

        Raises:
            (RuntimeError): If removing an order fails.

        """
        order_book: OrderBook = self.order_books[symbol]

        while True:
            try:
                cmd, order = await queue.get()
                if cmd == "add":
                    order_book.add_order(order)
                    self.emit_book_update(order.symbol)
                elif cmd == "remove":
                    order_book.remove_order(order)
                    self.emit_book_update(order.symbol)
            except RuntimeError:
                msg = "Could not remove the order"
                raise RuntimeError(msg) from RuntimeError

            queue.task_done()
            # after each mutation, run matching and publish quotes
            while True:
                trade = self.match_orders(symbol)
                if not trade:
                    break

                for order in [trade.buy_order, trade.sell_order]:
                    if order.quantity > 0:
                        order.status = "partially_filled"
                    else:
                        order_book.remove_order(order)
                        order.status = "filled"

                self.emit_trade(trade)
               
    async def add_order(self, order: Order) -> None:
        """Enqueue an Order in its respective order book for later matching.

        Args:
            order (Order): The order to add to the order book.

        Examples:
            >>> data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
            >>> exchange = Exchange(market_data=data)
            >>> o = Order(trader_id=1,symbol="AAPL",order_type="buy",
            >>>           quantity=42, limit_price=100.0)
            >>> exchange.add_order(o)
            >>> exchange.order_books["AAPL"].buy_size()
            1

        """
        if order.symbol not in self.instruments:
            raise KeyError("The symbol does not exist")

        await self._book_queues[order.symbol].put(("add", order))
        self.order_lookup[order.order_id] = order

    async def cancel_order(self, order_id: str) -> bool:
        """Mark `order` as cancelled.

        The order will not be processed by the matching engine.

        Attributes:
            order_id (Order):
                `order_id` of `Order` to be cancelled

        Returns:
            (bool):
                True if order has been cancelled, false if failed to cancel.

        """
        if order_id not in self.order_lookup:
            msg = f"""An order with this `order_id` does not exist.
                      (got {order_id})"""
            raise KeyError(msg)

        order = self.order_lookup[order_id]

        if order.status != "filled":
            order.status = "cancelled"
            await self._remove_order(order_id)

        return order.status == "cancelled"

    async def _remove_order(self, order_id: str) -> None:
        """Remove order from the exchange's order books.

        Emits a `book_update` event to all its subscribers.
        
        Args:
            order_id (str):
                id of `Order` to remove.

        """
        order = self.order_lookup[order_id]
        await self._book_queues[order.symbol].put(("remove", order))

    def subscribe(self, topic: str, handler: Callable) -> None:
        """Subscribe a market participant's handler function to an event.

        Args:
            topic (str):
                Topic to subscribe `handler` to

            handler (Callable):
                Function to subcribe to `topic`

        """
        self._subscriptions.setdefault(topic, []).append(handler)

    def _dispatch(self, topic: str,
                  event_payload: MarketQuote | Trade) -> None:
        """Dispatch an event onto the event bus to all its subscribers.

        Args:
            topic (str):
                Event name to dispatch the payload to.

            event_payload (any):
                Payload for subscribed handler functions.

        """
        for handler in self._subscriptions.get(topic, []):
            handler(event_payload)

        # For topic wide channel subscriptions e.g. "trade:*"
        base, _, spec = topic.partition(":")

        if spec != "*" and ":" in spec:
            ticker, _, mpid = spec.partition(":")

            for subwildcard in [f"{base}:*:{mpid}", f"{base}:{ticker}"]:
                for handler in self._subscriptions.get(subwildcard, []):
                    handler(event_payload)

        wildcard = f"{base}:*"
        for handler in self._subscriptions.get(wildcard, []):
            handler(event_payload)

    def emit_book_update(self, symbol: str) -> None:
        """Emit a `book_update` event that is dispatched to its subscribers.

        Submits latest `MarketQuote` as event payload.

        Args:
            symbol (str):
                A ticker symbol (e.g. AAPL or MSFT).

        """
        topic = f"book_update:{symbol}"
        order_book = self.order_books[symbol]

        # Construct MarketQuote to emit

        bid = order_book.peek_best_buy()
        bid_size = order_book.buy_size()
        ask = order_book.peek_best_sell()
        ask_size = order_book.sell_size()
        last_price = order_book.last_trade_price
        ts = datetime.now()

        bid_price = bid.limit_price if bid else 0
        ask_price = ask.limit_price if ask else 0

        quote = MarketQuote(
            symbol,
            bid_price,
            bid_size,
            ask_price,
            ask_size,
            last_price,
            timestamp=ts,
        )

        event_payload = quote
        self.quotes[symbol] = quote

        self._dispatch(topic, event_payload)

    def emit_trade(self, trade: Trade) -> None:
        """Emit a `trade` that is dispatched to its subscribers.

        Submits `trade` as event payload.

        Args:
            trade (Trade):
                `Trade` object to emit.

        """
        mpids = [trade.buy_order.mpid, trade.sell_order.mpid]
        symbol = trade.symbol
        topic = f"trade:{symbol}"

        order_book = self.order_books[symbol]
        bid = order_book.peek_best_buy()
        bid_size = order_book.buy_size()
        ask = order_book.peek_best_sell()
        ask_size = order_book.sell_size()
        last_price = trade.price
        ts = datetime.now()

        bid_price = bid.limit_price if bid else 0
        ask_price = ask.limit_price if ask else 0

        quote = MarketQuote(
            symbol,
            bid_price,
            bid_size,
            ask_price,
            ask_size,
            last_price,
            timestamp=ts,
        )
        self.quotes[symbol] = quote

        for mpid in mpids:
            self._dispatch(topic + ":" + mpid, trade)

    def match_orders(self, symbol: str) -> Trade | None:
        """Match buy and sell orders in the specified symbol's order book.

        Args:
            symbol (str): The stock symbol for which to perform matching.

        Returns:
            Trade or None: Executed trade or `None` if no suitable match_orders

        Examples:
            >>> data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
            >>> exchange = Exchange(market_data=data)
            >>> o = Order(trader_id=1,symbol="AAPL",order_type="buy",
            >>>           quantity=42, limit_price=100.0)
            >>> exchange.add_order(o)
            >>> exchange.match_orders("AAPL")
            []

        """
        order_book = self.order_books.get(symbol, None)

        if not order_book:
            msg = f"No existing order book for this symbol. (got {symbol})"
            raise KeyError(msg)

        t_n_p = self._select_taker_and_predicate(order_book)

        if t_n_p is None:
            return None
        taker, maker_levels, price_cross = t_n_p

        maker = self._find_maker(maker_levels, price_cross)

        # No valid maker found → restore and exit
        if maker is None:
            return None
        
        # Build the trade
        trade = self._build_trade(taker, maker, symbol)

        self.trade_num = (self.trade_num[0] + 1, self.trade_num[1])

        total_seconds = (datetime.now() - self.trade_num[1]).total_seconds()

        delta = int(total_seconds * 1000)

        self.avg_service_time = (
            self.avg_service_time * (self.trade_num[0] - 1) + delta
        ) / self.trade_num[0]

        if self.trade_num[0] % 100 == 0:
            print(f"""Trades handled so far:
                        {self.trade_num[0]}
                      Time passed since last 100:
                        {delta} ms
                      Avg service time for 100 orders:
                        {self.avg_service_time} ms""")

        self.trade_num = (self.trade_num[0], datetime.now())

        # Store last trade price in the order book
        self.order_books[symbol].last_trade_price = trade.price

        return trade

    def _select_taker_and_predicate(
        self,
        order_book: OrderBook,
    ) -> tuple[Order, list[PriceLevel], Callable[[Order], bool]] | None:
        """Decide which side provides the taker order.
        
        Args:
            order_book (OrderBook):
                `OrderBook` in which orders are matched.

        Returns:
            taker:
                `Order` to be taker.

            taker_side (Literal["buy", "sell"):
                "buy" or "sell"

            maker_levels (list[PriceLevel]):
                PriceLevel bucket list to scan for a maker.

            price_cross (Callable):
                Predicate testing price-crossing.

        """
        market = self._select_market_taker(order_book)
        if market:
            return market

        return self._select_limit_taker(order_book)

    def _select_market_taker(
        self, order_book: OrderBook
    ) -> tuple[
        Order, list[PriceLevel], Callable[[Order], bool]
    ] | None:
        mb = order_book.market_buys.peek()
        ms = order_book.market_sells.peek()
        if not (mb or ms):
            return None

        if ((not ms) or (mb
            and (mb.timestamp, mb.sequence)
                < (ms.timestamp, ms.sequence))
        ):
            taker = mb
            maker_lvls = list(order_book._sell_levels.values())
        else:
            taker = ms
            maker_lvls = list(order_book._buy_levels.values())

        assert taker, "Market-order taker is None"

        def always_cross(_: Order) -> bool:
            return True

        return taker, maker_lvls, always_cross

    def _select_limit_taker(
        self, order_book: OrderBook
    ) -> tuple[
        Order, list[PriceLevel], Callable[[Order], bool]
    ] | None:
        best_buy = order_book.peek_best_buy()
        best_sell = order_book.peek_best_sell()
        if not best_buy or not best_sell:
            return None
        assert best_buy.limit_price and best_sell.limit_price


        if best_buy.limit_price < best_sell.limit_price:
            return None

        buy_later = (
            best_buy.timestamp, best_buy.sequence
        ) > (
            best_sell.timestamp, best_sell.sequence
        )

        if buy_later:
            taker = best_buy
            maker_lvls = list(order_book._sell_levels.values())

            def price_cross(m: Order) -> bool:
                assert m.limit_price is not None
                if taker.limit_price is None:
                    return True
                return taker.limit_price >= m.limit_price
        else:
            taker = best_sell
            maker_lvls = list(order_book._buy_levels.values())

            def price_cross(m: Order) -> bool:
                assert m.limit_price is not None
                if taker.limit_price is None:
                    return True
                return m.limit_price >= taker.limit_price

        assert taker, "Limit-order taker is None"
        return taker, maker_lvls, price_cross

    def _find_maker(
        self,
        maker_levels: list[PriceLevel],
        price_cross: Callable[[Order], bool],
    ) -> Order | None:
        """Find a suitable maker `Order` from list of `PriceLevel` buckets.

        Walk price levels in priority order, then within each level walk FIFO.

        Returns:
            maker (`Order` or None):
                Maker `Order`, or None if no matches.

        """
        maker = None

        for lvl in maker_levels:
            for candidate in lvl:
                if not price_cross(candidate):
                    break

                maker = candidate
                break
            if maker:
                break

        return maker

    def _build_trade(self, taker: Order, maker: Order, symbol: str) -> Trade:
        """Build a new trade based on `taker` and `maker`.
        
        Args:
            taker (Order):
                Taker `Order` of the trade

            maker (Order):
                Maker `Order` of the trade

            symbol (str):
                A ticker symbol of the trade.

        Returns:
            (Trade): `Trade` object.

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

        best_buy.quantity -= exec_qty
        best_sell.quantity -= exec_qty

        new_trade = Trade(
            best_buy,
            best_sell,
            symbol,
            exec_qty,
            exec_price,
        )

        return new_trade
