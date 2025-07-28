from engine.trade import Trade


class InventoryManager:
    """SOME DOCSTRING""" #TODO

    def __init__(self, inv_limit, pnl_limit) -> None:
        self.position = 0
        self.realized_pnl = 0.0
        self.inv_limit, self.pnl_limit = inv_limit, pnl_limit


    def on_trade(self, trade: Trade, mpid) -> None:
        # Adjust position & PnL if market maker was trade maker or taker
        if trade.buy_order.mpid == mpid or trade.sell_order.mpid == mpid:
            sign = 1 if trade.buy_order.mpid == mpid else -1
            fill = trade.quantity
            notional = fill * trade.price
            self.position += sign * fill
            self.realized_pnl -= sign * notional


    def risk_breached(self) -> bool:
        return (abs(self.position) > self.inv_limit or abs(self.realized_pnl) > self.pnl_limit)


