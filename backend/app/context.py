from logging import Logger

from app.session import Session
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
                self, session: Session, 
                broker: Broker,
                exchange: Exchange,
                logger: Logger | None = None,
            ):
        """Instantiate AppContext class

        Args:
        session (Session): Currently active user session.
        broker (Broker): The broker on the stock exchange.
        exchange (Exchange): The stock exchange.
        logger (Logger): The logger to log user's actions.
        """
        self.session = session
        self.broker = broker
        self.exchange = exchange
        self.logger = logger
