from engine.trade import Trade


class InventoryManager:
    """SOME DOCSTRING"""  # TODO

    def __init__(self, mpid: str, inv_limit, pnl_limit) -> None:
        self.mpid = mpid
        self.position = 0
        self.realized_pnl = 0.0
        self.inv_limit, self.pnl_limit = inv_limit, pnl_limit

    def on_trade(self, trade: Trade) -> None:
        # Adjust position & PnL if market maker was trade maker or taker
            sign = 1 if trade.buy_order.mpid == self.mpid else -1
            fill = trade.quantity
            notional = fill * trade.price
            self.position += sign * fill
            self.realized_pnl -= sign * notional

    def risk_breached(self) -> bool:
        return (
            abs(self.position) > self.inv_limit
            or abs(self.realized_pnl) > self.pnl_limit
        )
