from engine.order_book.market_order_queue import MarketOrderQueue
from engine.order_book.order_book import OrderBook
from engine.order_book.order import Order


def test_market_order_queue_adds_order():
    market_o_queue = MarketOrderQueue()

    o = Order(mpid="BR01", symbol="AAPL", order_type="buy", quantity=40)

    market_o_queue.enqueue(o)

    assert len(market_o_queue) == 1


def test_market_order_queue_remove_order():
    market_o_queue = MarketOrderQueue()

    o = Order(mpid="BR01", symbol="AAPL", order_type="buy", quantity=40)

    market_o_queue.enqueue(o)

    assert len(market_o_queue) == 1

    market_o_queue.remove(o)

    assert len(market_o_queue) == 0


def test_market_order_queue_is_empty():
    market_o_queue = MarketOrderQueue()

    assert market_o_queue.is_empty()

    o = Order(mpid="BR01", symbol="AAPL", order_type="buy", quantity=40)

    market_o_queue.enqueue(o)

    assert not market_o_queue.is_empty()


def test_market_order_queue_get_item():
    market_o_queue = MarketOrderQueue()

    o1 = Order(mpid="BR01", symbol="AAPL", order_type="buy", quantity=40)
    o2 = Order(mpid="BR02", symbol="AAPL", order_type="buy", quantity=40)
    o3 = Order(mpid="BR03", symbol="AAPL", order_type="buy", quantity=40)

    market_o_queue.enqueue(o1)
    market_o_queue.enqueue(o2)
    market_o_queue.enqueue(o3)

    assert market_o_queue[0] == o1
    assert market_o_queue[-1] == o3
    assert market_o_queue[1] == o2

    try:
        market_o_queue[40]
    except IndexError:
        assert True


def test_order_book_empty_pop():
    order_book = OrderBook()
    assert order_book.pop_best_buy() is None
    assert order_book.pop_best_sell() is None


def test_order_book_insert_pop():
    o1 = Order("BR01", "AAPL", "buy", 1, 42.0)
    o2 = Order("BR01", "AAPL", "sell", 1, 42.0)
    order_book = OrderBook()

    order_book.add_order(o1)
    order_book.add_order(o2)

    assert order_book.pop_best_buy() == o1
    assert order_book.pop_best_sell() == o2


def test_order_book_buy_priority():
    o1 = Order("BR01", "AAPL", "buy", 1, 42.0)
    o2 = Order("BR01", "AAPL", "buy", 1, 50.0)
    o3 = Order("BR01", "AAPL", "buy", 1, 42.0)
    o4 = Order("BR01", "AAPL", "buy", 1, 42.0)

    order_book = OrderBook()

    order_book.add_order(o1)
    order_book.add_order(o2)

    assert order_book.pop_best_buy() == o2

    order_book.add_order(o3)

    assert order_book.pop_best_buy() == o1

    order_book.add_order(o4)

    assert order_book.pop_best_buy() == o3
    assert order_book.pop_best_buy() == o4


def test_order_book_sell_priority():
    o1 = Order("BR01", "AAPL", "sell", 1, 42.0)
    o2 = Order("BR01", "AAPL", "sell", 1, 50.0)
    o3 = Order("BR01", "AAPL", "sell", 1, 50.0)
    o4 = Order("BR01", "AAPL", "sell", 1, 50.0)

    order_book = OrderBook()

    order_book.add_order(o1)
    order_book.add_order(o2)

    assert order_book.pop_best_sell() == o1

    order_book.add_order(o3)

    assert order_book.pop_best_sell() == o2

    order_book.add_order(o4)

    assert order_book.pop_best_sell() == o3
    assert order_book.pop_best_sell() == o4


def test_order_book_side_independence():
    o1 = Order("BR01", "AAPL", "sell", 1, 42.0)
    o2 = Order("BR01", "AAPL", "buy", 1, 50.0)

    order_book = OrderBook()

    order_book.add_order(o1)
    order_book.add_order(o2)

    assert order_book.pop_best_buy() == o2
    assert order_book.pop_best_sell() == o1
