from logging import Logger

from app.session import Session
from engine.bots.bot_manager import BotManager
from engine.broker.broker import Broker
from engine.exchange.exchange import Exchange


class AppContext:
    """Keeps track of the exchange, the current active user, and of the logger

    Attributes:
      session (Session): Currently active user session.
      exchange (Exchange): The stock Exchange.
      logger (Logger): The logger to log user's actions.

    """

    def __init__(
        self,
        session: Session,
        broker: Broker,
        exchange: Exchange,
        bot_manager: BotManager,
        logger: Logger | None = None,
    ):
        """Instantiate AppContext class.

        Args:
        session (Session): Currently active user session.
        broker (Broker): The broker on the stock exchange.
        exchange (Exchange): The stock exchange.
        logger (Logger): The logger to log user's actions.

        """
        self.session = session
        self.broker = broker
        self.exchange = exchange
        self.bot_manager = bot_manager
        self.logger = logger

    def __repr__(self):
        def n(x: list) -> int:  # helper for None-safe len
            return 0 if x is None else len(x)

        exch_name = getattr(self.exchange, "name", "Exchange")
        symbols = getattr(self.exchange, "order_books", {})
        parts = getattr(self.exchange, "market_participants", {})

        return (
            f"<AppContext exch='{exch_name}' "
            f"symbols={n(symbols)} participants={n(parts)}"
        )


# f"brokers={n(self.brokers)} bots={n(self.bots)} "
# f"risk_gateway={'on' if self.risk_gateway else 'off'} "
# f"clearing={'on' if self.clearing_house else 'off'} "
# f"configs={list(self.config_paths.keys())}>")
