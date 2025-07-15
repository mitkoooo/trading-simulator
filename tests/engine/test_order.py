from engine.order import Order
from app.context import AppContext


def test_order_constructor_invalid_qty():
    try:
        _ = Order(trader_id=1, symbol="AAPL", order_type="sell", quantity=-42)
        assert False
    except ValueError:
        assert True


def test_order_constructor_invalid_price():
    try:
        _ = Order(
            trader_id=1, symbol="AAPL", order_type="sell", quantity=42, limit_price=-100
        )
        assert False
    except ValueError:
        assert True


def test_order_constructor_invalid_order_type():
    try:
        _ = Order(
            trader_id=1, symbol="AAPL", order_type="foo", quantity=42, limit_price=-100
        )
        assert False
    except ValueError:
        assert True

def test_cancel_order(test_context: AppContext):
    SYMBOL = "AAPL"
    QUANTITY = 42 
    PRICE = 42.00

    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker 
    sample_exchange = test_context.exchange

    # Add an order
    o = sample_trader.create_order(SYMBOL, "buy", QUANTITY, PRICE)
    sample_broker.submit_order(o)

    # Check the prequisites
    assert sample_exchange.order_books[SYMBOL].buy_size() == 1

    # Cancel an order
    assert sample_broker.cancel_order(o.order_id)
    assert sample_exchange.order_lookup[o.order_id].status == "cancelled"

    # On best_buy peek the order is effectively mopped out
    sample_exchange.order_books[SYMBOL].peek_best_buy()
    
    assert sample_exchange.order_books[SYMBOL].buy_size() == 0

def test_cancel_order_invalid_id(test_context: AppContext):
    sample_exchange = test_context.exchange

    try:
        sample_exchange.cancel_order("fake_order_id")
    except Exception as e:
        assert type(e) == KeyError
        return

    # Assert false if error not returned
    assert False    

def test_cancel_fulfilled_order(test_context: AppContext):
    SYMBOL = "AAPL"
    QUANTITY = 42 
    PRICE = 42.00

    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker 
    sample_exchange = test_context.exchange

    # Add an order
    o = sample_trader.create_order(SYMBOL, "buy", QUANTITY, PRICE)
    sample_broker.submit_order(o)

    # Mutate order's status to fulfilled 
    sample_exchange.order_lookup[o.order_id].status = "filled"

    # Check the prequisites
    assert sample_exchange.order_books[SYMBOL].buy_size() == 1

    # Cancel an order
    assert not sample_exchange.cancel_order(o.order_id)





