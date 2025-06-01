from engine.order_book import OrderBook
from engine.order import Order
from datetime import datetime


def test_order_book_empty_pop():
    order_book = OrderBook()
    assert order_book.pop_best_buy() == None
    assert order_book.pop_best_sell() == None


def test_order_book_insert_pop():
    o1 = Order(1, "AAPL", "buy", 1, 42.0)
    o2 = Order(1, "AAPL", "sell", 1, 42.0)
    order_book = OrderBook()

    order_book.add_order(o1)
    order_book.add_order(o2)

    assert order_book.pop_best_buy() == o1
    assert order_book.pop_best_sell() == o2


def test_order_book_buy_priority():
    o1 = Order(1, "AAPL", "buy", 1, 42.0, timestamp=datetime(2025, 1, 1, 0, 2))
    o2 = Order(1, "AAPL", "buy", 1, 50.0, timestamp=datetime(2025, 1, 1, 0, 1))
    o3 = Order(1, "AAPL", "buy", 1, 42.0, timestamp=datetime(2025, 1, 1, 0, 0))
    o4 = Order(1, "AAPL", "buy", 1, 42.0, timestamp=datetime(2025, 1, 1, 0, 2))

    order_book = OrderBook()

    order_book.add_order(o1)
    order_book.add_order(o2)

    assert order_book.pop_best_buy() == o2

    order_book.add_order(o3)

    assert order_book.pop_best_buy() == o3

    order_book.add_order(o4)

    assert order_book.pop_best_buy() == o1
    assert order_book.pop_best_buy() == o4


def test_order_book_sell_priority():
    o1 = Order(1, "AAPL", "sell", 1, 42.0, timestamp=datetime(2025, 1, 1, 0, 2))
    o2 = Order(1, "AAPL", "sell", 1, 50.0, timestamp=datetime(2025, 1, 1, 0, 1))
    o3 = Order(1, "AAPL", "sell", 1, 50.0, timestamp=datetime(2025, 1, 1, 0, 0))
    o4 = Order(1, "AAPL", "sell", 1, 50.0, timestamp=datetime(2025, 1, 1, 0, 1))

    order_book = OrderBook()

    order_book.add_order(o1)
    order_book.add_order(o2)

    assert order_book.pop_best_sell() == o1

    order_book.add_order(o3)

    assert order_book.pop_best_sell() == o3

    order_book.add_order(o4)

    assert order_book.pop_best_sell() == o2
    assert order_book.pop_best_sell() == o4


def test_order_book_side_independence():
    o1 = Order(1, "AAPL", "sell", 1, 42.0, timestamp=datetime(2025, 1, 1, 0, 2))
    o2 = Order(1, "AAPL", "buy", 1, 50.0, timestamp=datetime(2025, 1, 1, 0, 1))

    order_book = OrderBook()

    order_book.add_order(o1)
    order_book.add_order(o2)

    assert order_book.pop_best_buy() == o2
    assert order_book.pop_best_sell() == o1
