from typing import Dict

from engine.trader import Trader


class Session:
    """Keeps track of the active trader on the exchange."""

    def __init__(self, traders: Dict[int, Trader]):
        self._traders: Dict[int, Trader] = traders
        self._active_trader: Trader | None = None

    def login(self, trader_id: int) -> None:
        """Login into the session with `trader_id`

        Args:
          trader_id (int): ID of the current trader

        Raises:
            (ValueError): If `trader_id` is not registered.
        """

        if trader_id not in self._traders:
            raise ValueError(f"No such existing trader: {trader_id}")

        self._active_trader = self._traders[trader_id]

    def logout(self) -> None:
        """Logs out the current trader.

        Raises:
            (RuntimeError): If no trader is currently logged in
        """
        if not self._active_trader:
            raise RuntimeError("Cannot log out: no trader is currently logged in.")

        self._active_trader = None

    def require_active(self) -> Trader:
        """Returns currently active trader, raises `RuntimeError` if None

        Returns:
          (Trader): Currently active trader.

        Raises:
          (RuntimeError): If the user is not currently logged in
        """
        if not self._active_trader:
            raise RuntimeError("The user is currently not logged in")

        return self._active_trader

    @property
    def active_trader(self) -> Trader:
        """Currently logged in trader"""
        return self._active_trader
