from typing import Dict, Literal

from engine.broker.power_ledger import PowerLedger
from engine.exchange.exchange import Exchange
from engine.order_book.order import Order
from engine.position import Position
from engine.trade import Trade
from engine.trader import Trader


class Broker:
    """Orchestrates order submission, cancellation, and trade settlement between traders and the exchange.

    The Broker maintains a registry of `Trader` instances and uses a `PowerLedger` to
    reserve and release cash or shares as orders are submitted, cancelled, or filled.
    It submits validated orders to the `Exchange` and finalizes both buy and sell sides
    of each `Trade`, updating trader portfolios and pending‐order logs.

    Attributes:
        exchange (Exchange): The matching engine where orders are enqueued and trades are generated.
        traders (Dict[int, Trader]): Maps trader IDs to their `Trader` objects, holding portfolios and logs.
        power_ledger (PowerLedger): Manages reservations and releases of cash and shares for pending orders.

    """

    def __init__(self, exchange: Exchange, mpid: str) -> None:
        self.mpid = mpid
        self.exchange = exchange
        self.traders: Dict[str, Trader] = {}
        self.active_orders: Dict[str, str] = {}  # order.mpid -> trader_id
        self.power_ledger = PowerLedger(exchange, self.traders)
        self.exchange.subscribe(f"trade:*:{self.mpid}", self.settle_trade)
        self.exchange.subscribe(
            "book_update:*", self.power_ledger.consume_quote
        )

    def register_trader(self, trader: Trader) -> None:
        """Add a new trader to the broker’s registry.

        Args:
            trader (Trader): The trader to register.

        Raises:
            ValueError: If a trader with the same `trader_id` is already registered.

        """
        if trader.trader_id in self.traders:
            raise ValueError(
                f"Trader ID {trader.trader_id} already registered"
            )

        self.traders[trader.trader_id] = trader

    async def submit_order(
        self,
        trader_id: str,
        symbol: str,
        order_type: Literal["buy", "sell"],
        quantity: int,
        limit_price: float | None,
    ) -> Order:
        """Validate and submit a  order to the exchange.

        1. Verifies that the submitting trader is registered.
        2. Reserves cash (for buy orders) or shares (for sell orders) via the PowerLedger.
        3. Forwards the order to the Exchange.
        4. Records the order in the trader’s `pending_orders`.

        Args:
            order (Order): The order to submit.

        Raises:
            KeyError: If the `order.trader_id` is not registered.
            ValueError: If `order.order_type` is not 'buy' or 'sell'.

        """
        trader = self.traders.get(trader_id, None)
        if not trader:
            raise KeyError(
                f"Trader with this trader id does not exist. (got {trader_id}"
            )

        order = Order(self.mpid, symbol, order_type, quantity, limit_price)

        self.active_orders[order.order_id] = trader_id

        if order.order_type == "buy":
            self.power_ledger.reserve_cash(trader_id, order)
        elif order.order_type == "sell":
            self.power_ledger.reserve_shares(trader_id, order)
        else:
            raise ValueError("Unknown order type.")

        await self.exchange.add_order(order)

        trader.pending_orders[order.order_id] = order

        return order

    async def cancel_order(self, order_id: str) -> None:
        """Cancel a trader’s pending order and free reserved funds or shares.

        Calls the exchange to cancel the order, removes it from the trader’s
        pending orders, marks it as 'cancelled', and releases any reserved
        cash (for buys) or shares (for sells).

        Args:
            order_id (str): Identifier of the pending order to cancel.

        Returns:
            bool: True if cancellation succeeded, False otherwise.

        Raises:
            KeyError: If no such trader is registered or the order is not pending.
            RuntimeError: If the exchange refuses to cancel (unexpected).
            ValueError: If the order’s type is neither 'buy' nor 'sell'.

        """
        order = self.exchange.order_lookup[order_id]

        trader_id = self.active_orders[order_id]

        trader: Trader | None = self.traders.get(trader_id, None)

        if not trader:
            raise KeyError(
                f"Trader with this trader id does not exist. (got {trader_id}"
            )
        if order.order_id not in trader.pending_orders:
            raise KeyError(
                f"An order with the provided `order_id` does not exist. (got {order_id})"
            )

        # Remove the pending order
        status = await self.exchange.cancel_order(order_id)

        if not status:
            raise RuntimeError("Couldn't cancel the order")

        cancelled_order = trader.pending_orders.pop(order_id)
        cancelled_order.status = "cancelled"

        del self.active_orders[order_id]

        if order.order_type == "buy":
            self.power_ledger.release_cash(trader_id, cancelled_order)
        elif order.order_type == "sell":
            self.power_ledger.release_shares(trader_id, cancelled_order)
        else:
            raise ValueError("Unknown order type.")

        return

    def settle_trade(self, trade: Trade):
        """Settle a matched trade or cancel on buyer failure.

        Attempts to finalize the buy side first. If the buyer cannot pay or reservation
        is missing, the buy order is cancelled, quantities are restored, and the trade
        is marked ‘cancelled’. Otherwise, finalizes the sell side, marks the trade
        ‘fulfilled’, and re-queues or removes any partially or fully filled orders.

        Args:
            trade (Trade): The trade to settle, containing `buy_order`, `sell_order`,
                `quantity`, and `price`.

        Raises:
            KeyError: If reserved cash for the buy order is missing.
            RuntimeError: If the buyer’s available cash is insufficient.

        """
        try:
            trader_id = self.active_orders.get(trade.buy_order.order_id, None)
            if trader_id and trader_id in self.traders:
                self.finalize_buy(trade)
        except (KeyError, RuntimeError):  # In case market price order fails
            # Restore the order quantities
            trade.buy_order.quantity += trade.quantity
            trade.sell_order.quantity += trade.quantity

            # Cancel the trade and the buy order
            trade.status = "cancelled"

            # Cancel the finalization of the trade

            return

        trader_id = self.active_orders.get(trade.sell_order.order_id, None)
        if trader_id and trader_id in self.traders:
            self.finalize_sell(trade)
        trade.status = "fulfilled"

    def finalize_buy(self, trade: Trade):
        """Apply the financial effects of the buy side of a trade.

        Unreserves the cash reservation for the buy order, deducts the trade cost
        from the trader’s cash balance, and updates or creates their position
        at the executed price. Updates pending order quantity or logs a filled order.

        Args:
            trade (Trade): The trade whose `buy_order`, `quantity`, and `price`
                determine the cash movement.

        Raises:
            KeyError: If no cash was reserved for this order.
            RuntimeError: If the trader’s cash balance is insufficient to cover cost.

        """
        order = trade.buy_order
        trader_id = self.active_orders[order.order_id]
        trader = self.traders[trader_id]

        price = trade.price
        qty = trade.quantity
        symbol = trade.symbol
        order_id = order.order_id

        # Ensure we have keys in positions
        pos = trader.portfolio.positions.setdefault(
            symbol,
            Position(symbol, 0, price),
        )

        # Total cash originally set aside:
        old_reservation = self.power_ledger.get_reserved_cash(order_id)

        if not old_reservation:
            raise KeyError(
                "Cash has mistakingly not been reserved for this order."
            )

        # Calculate the actual cost
        actual_cost = qty * price

        if actual_cost > trader.portfolio.cash:
            # BLOCK Trade
            raise RuntimeError(
                "Buyer does not have enough cash to fulfill the order."
            )

        # Unreserve the cash
        self.power_ledger.release_cash(trader_id, order)

        trader.portfolio.cash -= actual_cost

        # Get old values to update the running avg
        old_qty, old_avg = pos.qty, pos.avg_price
        # Add the shares in
        pos.qty += qty
        # Calculate new avg
        pos.avg_price = (old_avg * old_qty + qty * price) / pos.qty

        # Bookkeeping
        if order.quantity == 0:
            del trader.pending_orders[order.order_id]
            trader.transaction_log.append(order)

            del self.active_orders[order.order_id]
        else:
            self.power_ledger.reserve_cash(trader_id, order)
            trader.pending_orders[order.order_id].quantity = order.quantity

    def finalize_sell(self, trade: Trade):
        """Apply the financial effects of the sell side of a trade.

        Unreserves the share reservation for the sell order, deducts sold shares
        from the trader’s position, credits proceeds to their cash balance, and
        updates or removes the position if it becomes empty. Updates pending order
        quantity or logs a filled order.

        Args:
            trade (Trade): The trade whose `sell_order`, `quantity`, and `price`
                determine the share and cash movement.

        Raises:
            KeyError: If no share reservation exists for this order.

        """
        order = trade.sell_order

        print(order)

        trader_id = self.active_orders[order.order_id]
        trader = self.traders[trader_id]

        price = trade.price
        qty = trade.quantity
        symbol = trade.symbol

        # Ensure we have keys in positions
        pos = trader.portfolio.positions.setdefault(
            symbol,
            Position(symbol, 0, price),
        )

        # Unreserve the shares
        self.power_ledger.release_shares(trader_id, order)

        proceeds = qty * price

        trader.portfolio.positions[symbol].qty -= qty
        trader.portfolio.cash += proceeds

        if (
            pos.qty == 0
            and self.power_ledger.get_reserved_shares(order.order_id) == 0
        ):
            trader.portfolio.positions.pop(symbol, None)

        # Bookkeeping
        if order.quantity == 0:
            trader.pending_orders.pop(order.order_id)
            trader.transaction_log.append(order)

            self.active_orders.pop(order.order_id)
        else:
            self.power_ledger.reserve_shares(trader_id, order)
            trader.pending_orders[order.order_id].quantity = order.quantity
