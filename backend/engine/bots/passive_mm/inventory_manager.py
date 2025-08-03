from engine.trade import Trade


class InventoryManager:
    """Manages position and realized P&L, enforcing inventory limits.

    Tracks trades for the bot to update current holdings and P&L,
    and provides a risk check to signal breaches of configured limits.
    """

    def __init__(self, mpid: str, inv_limit: int, pnl_limit: float) -> None:
        """Initialize `InventoryManager`.

        Args:
            mpid (str):
                Market participant ID of the PassiveMM bot.

            inv_limit (int):
                Maximum allowed absolute inventory position.

            pnl_limit (float):
                Maximum allowed absolute realized P&L.

        """
        self.mpid: str = mpid
        self.position: int = 0
        self.realized_pnl: float = 0.0
        self.inv_limit: int = inv_limit
        self.pnl_limit: float = pnl_limit

    def on_trade(self, trade: Trade) -> None:
        """Update position quantity and realized P&L following a trade.

        Args:
            trade (Trade):
                Trade to be processed by `InventoryManager`.

        """
        # Adjust position & PnL if market maker was trade maker or taker
        sign = 1 if trade.buy_order.mpid == self.mpid else -1
        fill = trade.quantity
        notional = fill * trade.price
        self.position += sign * fill
        self.realized_pnl -= sign * notional

    def risk_breached(self) -> bool:
        """Return True if inventory limits were breached, False otherwise."""
        return (
            abs(self.position) > self.inv_limit
            or abs(self.realized_pnl) > self.pnl_limit
        )
