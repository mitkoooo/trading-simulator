from typing import Dict

from engine.broker.power_ledger import PowerLedger
from engine.order import Order
from engine.position import Position
from engine.trade import Trade
from engine.trader import Trader
from engine.exchange import Exchange

class Broker:
    """TODO"""

    def __init__(self, exchange: Exchange) -> None:
        self.exchange = exchange
        self.traders: Dict[int, Trader] = {}
        self.power_ledger = PowerLedger(exchange, self.traders)
  

    def register_trader(self, trader: Trader) -> None:
        """Register trader in a stock exchange"""
        if trader.trader_id in self.traders:
            raise ValueError(f"Trader ID {trader.trader_id} already registered")

        self.traders[trader.trader_id] = trader


    def submit_order(self, order: Order) -> None:
        """Validates and submits a `Trader` order to `Exchange`."""
      
        tid = order.trader_id
        trader = self.traders.get(tid, None)
        if not trader:
            raise KeyError(f"Trader with this trader id does not exist. (got {tid}")


        if order.order_type == "buy":
            # FLAG
            self.power_ledger.reserve_cash(order)
        elif order.order_type == "sell":
            self.power_ledger.reserve_shares(order)
        else:
            raise ValueError("Unknown order type.")


        self.exchange.add_order(order)

        trader.pending_orders[order.order_id] = order


    def cancel_order(self, order_id: str) -> bool:
        """Cancels a pending order with `order_id`.
        
        Cancelled order will be removed from `pending_orders` of `Trader` who owns it. 

        Attributes:
            order_id (str): `order_id` of `Order` to be cancelled
        """

        order = self.exchange.order_lookup[order_id]

        tid: int = order.trader_id
        trader: Trader | None = self.traders.get(tid, None)

        if not trader:
            raise KeyError(f"Trader with this trader id does not exist. (got {tid}")
        if order.order_id not in trader.pending_orders:
            raise KeyError(f"An order with the provided `order_id` does not exist. (got {order_id})")

        status = self.exchange.cancel_order(order_id)

        if not status:
            return status

        # Remove the pending order 
        cancelled_order = trader.pending_orders.pop(order_id)
        cancelled_order.status = "cancelled"

        if order.order_type == "buy":
            self.power_ledger.release_cash(cancelled_order)
        elif order.order_type == "sell":
            self.power_ledger.release_shares(cancelled_order)
        else:
            raise ValueError("Unknown order type.")

        return status

    def settle_trade(self, trade: Trade):
        """TODO"""

        try:
            self.finalize_buy(trade)
        except:    # In case market price order fails
            # Restore the order quantities
            trade.buy_order.quantity += trade.quantity
            trade.sell_order.quantity += trade.quantity

            # Cancel the trade and the buy order(?)
            trade.status = "cancelled"
            self.cancel_order(trade.buy_order.order_id)
            
            # Cancel the finalization of the trade
            return           
            
        self.finalize_sell(trade)
        trade.status = "fulfilled"

        # If any side has still shares, reinsert it
        for order in [trade.buy_order, trade.sell_order]:
            if order.quantity > 0:
                order.status = "partially_filled"
                # Reinsert the maker back into order book
                self.submit_order(order)
            else:
                order.status = "filled"


    def finalize_buy(self, trade: Trade):
        order = trade.buy_order
        trader = self.traders[order.trader_id]

        price  = trade.price
        qty    = trade.quantity
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
            raise KeyError("Cash has mistakingly not been reserved for this order.")


        # Calculate the actual cost
        actual_cost = qty * price

        if actual_cost > trader.portfolio.cash:
            # BLOCK Trade
            raise RuntimeError("Buyer does not have enough cash to fulfill the order.")

        # Unreserve the cash
        self.power_ledger.release_cash(order)

        trader.portfolio.cash -= actual_cost

        # Get old values to update the running avg
        old_qty, old_avg = pos.qty, pos.avg_price
        # Add the shares in
        pos.qty += qty
        # Calculate new avg
        pos.avg_price = (old_avg * old_qty + qty * price) / pos.qty

        # Bookkeeping
        if order.quantity == 0:
            trader.pending_orders.pop(order.order_id)
            trader.transaction_log.append(order)
        else:
            trader.pending_orders[order.order_id].quantity = order.quantity
    
    def finalize_sell(self, trade: Trade):
        order = trade.sell_order

        trader = self.traders[order.trader_id]

        price  = trade.price
        qty    = trade.quantity
        symbol = trade.symbol

        # Ensure we have keys in positions
        pos = trader.portfolio.positions.setdefault(
            symbol,
            Position(symbol, 0, price),
        )

        # Unreserve the shares
        self.power_ledger.release_shares(order)
        
        proceeds = qty * price

        trader.portfolio.positions[symbol].qty -= qty 
        trader.portfolio.cash += proceeds

        if pos.qty == 0 and self.power_ledger.get_reserved_shares(order.order_id) == 0:
            trader.portfolio.positions.pop(symbol, None)
   
        # Bookkeeping
        if order.quantity == 0:
            trader.pending_orders.pop(order.order_id)
            trader.transaction_log.append(order)
        else:
            trader.pending_orders[order.order_id].quantity = order.quantity


