from logging import Logger

from app.session import Session
from engine.exchange import Exchange


class AppContext:
    """Keeps track of the exchange, the current active user, and of the logger

    Attributes:
      session (Session): Currently active user session.
      exchange (Exchange): The stock Exchange.
      logger (Logger): The logger to log user's actions.
    """

    def __init__(self, session: Session, exchange: Exchange, logger: Logger):
        """Instantiate AppContext class

        Args:
        session (Session): Currently active user session.
        exchange (Exchange): The stock Exchange.
        logger (Logger): The logger to log user's actions.
        """
        self.session = session
        self.exchange = exchange
        self.logger = logger
