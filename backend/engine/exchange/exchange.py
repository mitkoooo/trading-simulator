import asyncio
from datetime import datetime
from typing import Callable, Dict, Iterable, List, Optional, Tuple

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

    def __init__(self):
        """Initialize the Exchange with market data and prepare order books.

        Examples:
            >>> data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
            >>> exchange = Exchange(market_data=data)

        """
        self.name: str = "GhostSwap"
        self.instruments: Dict[str, Stock] = {}
        self.order_books: Dict[str, OrderBook] = {}
        self.market_participants: Dict[str, ParticipantInfo] = {}

        self._book_queues: Dict[str, asyncio.Queue[Tuple[str, Order]]] = {}
        self._book_tasks: List[asyncio.Task] = []

        self.trade_num: Tuple = (0, datetime.now())
        self.avg_service_time = 0

        self.risk_gateaway = RiskGateway()

        self.order_lookup: Dict[str, Order] = {}
        self.quotes: Dict[str, MarketQuote] = {}
        self._subscriptions: Dict[str, List[Callable]] = {}

        self.current_time = datetime.now()

    def register_instrument(self, stock: Stock):
        if stock.symbol in self.instruments:
            msg = f"Instrument already registered. got ({stock.symbol})"
            raise KeyError(msg)

        self.instruments[stock.symbol] = stock
        self.order_books[stock.symbol] = OrderBook()
        self._book_queues[stock.symbol] = asyncio.Queue()

    def register_participant(self, mpid: str, info: ParticipantInfo):
        """SOME DOCSTRING"""  # TODO
        mp = self.market_participants.get(mpid, None)
        if mp:
            msg = f"The market participant with {mpid} is already registered."
            raise ValueError(msg)
        else:
            self.market_participants[mpid] = info

    async def start(self):
        for symbol, queue in self._book_queues.items():
            task = asyncio.create_task(self._book_worker(symbol, queue))
            self._book_tasks.append(task)

    async def stop(self):
        for t in self._book_tasks:
            t.cancel()
        await asyncio.gather(*self._book_tasks, return_exceptions=True)

    async def _book_worker(self, symbol, queue: asyncio.Queue):
        order_book: OrderBook = self.order_books[symbol]

        while True:
            try:
                cmd, order = await queue.get()
                if cmd == "add":
                    order_book.add_order(order)
                    self.emit_book_update(
                        order.symbol, self.order_books[order.symbol]
                    )
                elif cmd == "remove":
                    order_book.remove_order(order)
                    self.emit_book_update(
                        order.symbol, self.order_books[order.symbol]
                    )
            except RuntimeError:
                raise RuntimeError("Couldn't remove the order")

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
                        order.status = "filled"  # sync method, no await

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
            await self.remove_order(order_id)

        return order.status == "cancelled"

    async def remove_order(self, order_id: str) -> None:
        order = self.order_lookup[order_id]
        await self._book_queues[order.symbol].put(("remove", order))
        self.emit_book_update(order.symbol, self.order_books[order.symbol])

    def subscribe(self, topic: str, handler: Callable):
        """SOME DOCSTRING"""  # TODO
        self._subscriptions.setdefault(topic, []).append(handler)

    def _dispatch(self, topic: str, event_payload):
        """SOME DOCSTRING"""  # TODO
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

    def emit_book_update(self, symbol, order_book: OrderBook) -> None:
        topic = f"book_update:{symbol}"

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

    def emit_trade(self, symbol, trade: Trade, mpid: Optional[str] = None):
        topic = f"trade:{symbol}"

        if mpid:
            topic += f":{mpid}"

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

        self._dispatch(topic, trade)

    def match_orders(self, symbol: str) -> Optional[Trade]:
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

        self.emit_trade(symbol=trade.symbol, trade=trade, mpid=taker.mpid)
        self.emit_trade(symbol=trade.symbol, trade=trade, mpid=maker.mpid)

        # Store last trade price in the order book
        self.order_books[symbol].last_trade_price = trade.price

        return trade

    def _select_taker_and_predicate(
        self,
        order_book: OrderBook,
    ) -> Optional[
        Tuple[
            Order,
            Iterable[PriceLevel],
            Callable[[Order], bool],
        ]
    ]:
        """Decide which side provides the taker order and return:
        - taker_side: "buy" or "sell"
        - taker: the Order object
        - maker_levels: sequence of PriceLevel buckets to scan
        - price_cross: predicate testing price‐crossing
        """
        mb = order_book.market_buys.peek()
        ms = order_book.market_sells.peek()

        # Market‐only taker
        if mb or ms:
            cond = not ms or (
                mb
                and ms
                and (mb.timestamp, mb.sequence) < (ms.timestamp, ms.sequence)
            )
            if cond:
                taker = mb
                maker_levels = order_book._sell_levels.values()
            else:
                taker = ms
                maker_levels = order_book._buy_levels.values()

            assert taker, "Market‐order taker unexpectedly None"

            def price_cross_market(_: Order) -> bool:
                return True

            return taker, maker_levels, price_cross_market

        # Two‐sided limit orders
        best_buy = order_book.peek_best_buy()
        best_sell = order_book.peek_best_sell()
        if not best_buy or not best_sell:
            return None

        # No crossing in spread?
        no_cross = (
            best_buy.limit_price is not None
            and best_sell.limit_price is not None
            and best_buy.limit_price < best_sell.limit_price
        )
        if no_cross:
            return None

        buy_later = (
            best_buy.timestamp,
            best_buy.sequence,
        ) > (
            best_sell.timestamp,
            best_sell.sequence,
        )

        if buy_later:
            taker = best_buy
            maker_levels = order_book._sell_levels.values()
            assert taker, "Limit‐order buy taker unexpectedly None"

            def price_cross(m: Order) -> bool:
                assert m.limit_price
                if taker.limit_price is None:
                    return True
                return taker.limit_price >= m.limit_price

        else:
            taker = best_sell
            maker_levels = order_book._buy_levels.values()
            assert taker, "Limit‐order sell taker unexpectedly None"

            def price_cross(m: Order) -> bool:
                assert m.limit_price
                if taker.limit_price is None:
                    return True
                return m.limit_price >= taker.limit_price

        return taker, maker_levels, price_cross

    def _find_maker(
        self,
        maker_levels: Iterable[PriceLevel],
        price_cross: Callable[[Order], bool],
    ) -> Optional[Order]:
        """Walk price levels in priority order, then within each level walk FIFO,
        skipping same‐trader and non‐crossing orders. Returns
        the first valid maker or None if no match exists.
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

    def verify_symbol(self, symbol) -> None:
        if symbol not in self.instruments:
            raise KeyError(f"The symbol '{symbol}' does not exist")
