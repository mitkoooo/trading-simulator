from typing import List, Optional
from .order import Order
from .portfolio import Portfolio
from .trade import Trade


class Trader:
    """Represents a market participant with cash balance and equity holdings.

    Allows a trader to place buy/sell orders and tracks cash, holdings, and transaction history.

    Attributes:
        trader_id (int): A unique trader identifier.
        portfolio (Portfolio): #TODO
        transaction_log (List[Order]): List of previous transactions.

    Examples:
        >>> t = Trader(trader_id=1, starting_balance=10000.0)
        >>> o = t.place_order("MTKO", "buy", 42, 10.0)
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
        >>> o = t.place_order("MTKO", "buy", 42, 10.0)
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
        >>> o = t.place_order("MTKO", "buy", 42, 10.0)
        >>> exchange.add_order(o)
        """

        if quantity <= 0:
            raise ValueError(f"quantity must be > 0 (got {quantity})")

        if order_type not in ("buy", "sell"):
            raise ValueError(f"order_type must be 'buy' or 'sell' (got {order_type!r})")

        holdings_num = self.portfolio.holdings.get(symbol, 0)

        if order_type == "sell" and holdings_num < quantity:
            raise ValueError(
                f"Cannot sell quantity greater than the number of stocks owned (got {quantity}, but owns {holdings_num})"
            )

        o = Order(
            trader_id=self.trader_id,
            symbol=symbol,
            order_type=order_type,
            quantity=quantity,
            limit_price=price,
        )
        self.portfolio.reserve_assets(o)

        return o

    def update_portfolio(self, trade: Trade) -> None:
        """Update portfolio based on a filled trade.

        Args:
            trade (Trade): a matched trade containing buy_order, sell_order, quantity, price.

        Examples:
        >>> from engine.trader import Trader
        >>> from engine.order import Order
        >>> from engine.trade import Trade
        >>> # Create a trader with 1000 starting cash
        >>> t1 = Trader(trader_id=1, starting_balance=1000.0)
        >>> # Create a buy and sell order
        >>> buy_order = Order(trader_id=1, symbol="AAPL", order_type="buy", quantity=2, limit_price=50.0)
        >>> sell_order = Order(trader_id=2, symbol="AAPL", order_type="sell", quantity=2, limit_price=50.0)
        >>> # Execute a trade of 2 shares at 50.0
        >>> trade = Trade(buy_order, sell_order, "AAPL", 2, 50.0, 2, 2)
        >>> t1.update_portfolio(trade)
        >>> t1.portfolio.cash
        900.0
        >>> t1.portfolio.holdings["AAPL"]
        2
        """
        return self.portfolio.apply_trade(trade, self.trader_id)
