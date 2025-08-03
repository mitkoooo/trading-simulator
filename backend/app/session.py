
from engine.trader import Trader


class Session:
    """Keeps track of the active trader on the exchange."""

    def __init__(self, traders: dict[str, Trader]) -> None:
        """Initialize `Session`.
        
        Args:
            traders (dict[str, Trader]):
                Dict of traders registered on the exchange.

        """
        self._traders: dict[str, Trader] = traders
        self._active_trader: Trader | None = None

    @property
    def traders(self) -> dict[str, Trader]:
        """Dict of traders registered on the exchange."""
        return self._traders

    @property
    def active_trader(self) -> Trader | None:
        """Currently logged in trader."""
        return self._active_trader

    def login(self, trader_id: str) -> None:
        """Login into the session with `trader_id`.

        Args:
          trader_id (int): ID of the current trader

        Raises:
            (ValueError): If `trader_id` is not registered.

        """
        if trader_id not in self._traders:
            raise KeyError(f"No such existing trader: {trader_id}")

        self._active_trader = self._traders[trader_id]

    def logout(self) -> None:
        """Log out the current trader.

        Raises:
            (RuntimeError): If no trader is currently logged in

        """
        if not self._active_trader:
            raise RuntimeError(
                "Cannot log out: no trader is currently logged in."
            )

        self._active_trader = None

    def require_active(self) -> Trader:
        """Return currently active trader, raises `RuntimeError` if None.

        Returns:
          (Trader): Currently active trader.

        Raises:
          (RuntimeError): If the user is not currently logged in

        """
        if not self._active_trader:
            raise RuntimeError("The user is currently not logged in")

        return self._active_trader


