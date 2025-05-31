# Trading Simulator Development Log

**Project Start Date:** May 2025

**Owner / Maintainer:** Vadim Mitko

---

## Table of Contents

1. [Week 1 (May 23 - May 30, 2025)](#week-1-may-23---may-30-2025)

---

## Week 1: May 23 – May 30, 2025

### ▶ Objectives

- Finalize CLI prototype (basic `next`, `buy`, `sell`, `match`, `status`, `quit`) commands.
- Stub out core classes (`Order`, `OrderBook`, `Trader`, `Exchange`, `Stock`, ).
- Stubbed `match_orders()` in `exchange.py` (function signature created, but no actual matching logic yet).
- Write initial test unit tests for class stubs
- Document project structure and CLI usage in `README.md`.

### ✔ Achievements this Week

- **CLI Loop & Commands**

  - Implemented `CLI` class with `CLI.run()` method that runs a `while` loop to parse user input and dispatch to command handlers.
  - Commands handled:
    - `next` → advance market clock
    - `buy <symbol> <qty> <price>` → place limit-buy order
    - `sell <symbol> <qty> <price>` → enqueue limit-sell order
    - `match <symbol>` → match equity sellers with buyers (stubbed but not yet functional)
    - `status` → display pending orders in the exchange
    - `quit` → exit gracefully
  - Added error messaging for invalid commands (e.g., input "privet" returns "Unknown command. Please try again.")

- **Core Class Stubs**

  - Created `order.py` with an `Order` dataclass (`trader_id`, `symbol`, `order_type`, `quantity`, `limit_price`, `timestamp`).
  - Created `order_book.py` with `OrderBook` class containing `add_order().`
  - Stubbed `trader.py`:
    - `Trader` class has `cash_balance` and `holdings` attributes and can `place_holder()`.
  - Stubbed `exchange.py`:
    - `Exchange` class with methods `add_order(...)` and stubbed `match_orders()`.
    - Created `stock.py` with dataclass `Stock` (`symbol`, `price`, `history`, `tick_model`, `volatility`).

- **Unit tests**

  - `tests/engine/test_exchange.py`: verifies that `Exchange.add_order()` appends to the correct `OrderBook` and that `match_orders()` stub does not crash.
  - `tests/engine/test_order.py`: Ensures an invalid `limit_price` or negative quantity raises `ValueError`.
  - `tests/engine/test_stock.py`: Checks that `simulate_price_tick()` updates `Stock.price` and appends to `history`.
  - `tests/cli/*`: Validates dispatch commands for CLI and verifies helper methods.

- **Documentation**

  - Updated `README.md` to describe project layout:

  ```bash
  trading-simulator/
  ├── src/
  │   ├── cli/
  │   ├── engine/
  │   ├── view/
  │   ├── logging_config.py
  │   └── main.py
  ├── data/
  ├── scripts/
  ├── tests/
  └── README.md
  ```

  - Added CLI usage examples (how to run, example commands).

### ⚠ Blockers & Challenges

- **Refactoring Core Classes**  
  Initial stubs lacked key fields (e.g. `Order.trader_id`, `Stock.history`), so I paused to think about which features might be missing and added these attributes before writing any logic.

- **Defining Week 1 Scope**  
  I chose to defer portfolio tracking and partial fills, focusing only on main CLI turn-based commands to have clear and connected plan in mind about what features to implement.

- **High Test Coverage Needs**  
  Writing tests for stubs uncovered edge cases (e.g., negative tick prices, empty book behavior), delaying implementation until signatures and docstrings were clarified.

### Lessons Learned

- **TDD Payoff**: Writing tests against stub methods first highlighted missing edge‐case considerations (e.g., empty‐book behavior) early.
- **Docstring Utility**: Embedding example usage in docstrings served as both documentation and basic tests when running `pytest --doctest-glob="*.py"`.
