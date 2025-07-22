from collections import deque
from typing import Deque, List, Optional

from engine.order_book.order_book import OrderBook


class MarketDataHandler:
    """SOME DOCSTRING""" #TODO

    def __init__(self, hist_len=200) -> None:
        self.mid_history: Deque[float] = deque(maxlen=hist_len) 
        self.buy_size = self.sell_size = 0


    def on_book_update(self, order_book: OrderBook) -> None:
        # Guard clause for when either side is empty
        if order_book.buy_size() == 0 or order_book.sell_size() == 0:
            return

        # Get order book depth for calculating depth imbalance later on.
        self.buy_size = order_book.buy_size()
        self.sell_size = order_book.sell_size()

        # Compute mid-price so you can estimate volatility and center your quotes.
        best_buy = order_book.peek_best_buy()
        best_sell = order_book.peek_best_sell()
        assert best_buy and best_sell, ValueError("The order book is unexpectedly empty")
        assert best_buy.limit_price and best_sell.limit_price, ValueError("The market order is unexpectedly in PriceLevel map")

        m_t = (best_buy.limit_price + best_sell.limit_price) / 2

        self.mid_history.append(m_t)

        return


    def get_mid(self) -> Optional[float]:
        return self.mid_history[-1] if self.mid_history else None


    def get_depth_imbalance(self) -> float:
        total = self.buy_size + self.sell_size or 1
        return (self.buy_size - self.sell_size) / total
   

    def get_mid_history(self) -> List[float]:
        return list(self.mid_history)
