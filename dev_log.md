# Trading Simulator Development Log

**Project Start Date:** May 2025

**Owner / Maintainer:** Vadim Mitko

---

## Table of Contents

1. [Week 1 (May 23 - May 30, 2025)](#week-1-may-23---may-30-2025)

2. [Week 2 (May 31 - June 6, 2025)](#week-2-may-31---june-6-2025)

3. [Week 3 (June 7 - June 13, 2025)](#week-3-june-7---june-13-2025)

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

## Week 2: May 31 - June 6, 2025

### ▶ Objectives

- Build out core matching engine with price‐time priority

- Introduce a `Portfolio` model and integrate it into `Trader`

- Implement trade application logic to update cash, positions, and reserved assets

- Expand unit‐test coverage for order matching and portfolio valuation

- Refine the CLI’s portfolio and price display formatting

- Keep documentation and doctest examples up‐to‐date

### ✔ Achievements this Week

- Added `Portfolio` class, refactored `Trader` to use it, and stubbed out the `Trade` model

- Added `Portfolio.value` tests and fixed reserved‐shares calculation

- Enhanced `Exchange.match_orders` to use a sequence‐based FIFO alongside price and timestamp priority

- Implemented `apply_trade` to correctly update reserved cash/shares and actual holdings on trade execution

- Added unit tests for `Exchange.match_orders` covering price‐time priority edge cases

- Fixed doctest examples and typos in OrderBook and Trade documentation

- Refined CLI output formatting for portfolio tables and price displays

### ⚠ Blockers & Challenges

- FIFO + price‐time logic: combining sequence numbers with price‐priority in the matching engine required careful ordering

- Partial‐fill reservations: correctly un‐reserving and re‐reserving cash/shares in apply_trade posed edge‐case complexity

- Test coverage: crafting deterministic tests for matching and valuation logic uncovered missing branches and off-by-one errors

- Doc‐sync: keeping doctest snippets accurate as APIs evolved took extra rounds of manual fixes

### Lessons Learned

- Implemented a heap‐based priority queue for the order book, using price as the primary key and a monotonically increasing sequence counter as a tiebreaker to enforce FIFO within equal prices.

- Learned to push, pop, and peek from separate buy/sell heaps with `Order.__lt__` method to maintain correct matching order efficiently.

- Designed `Order.__lt__` to drive the heap comparison directly by implementing `price → timestamp → sequence logic`, avoiding tuple keys and simplifying the matching engine.

- Discovered that customizing comparator logic and thoroughly testing heap operations is essential to prevent subtle mismatches under edge cases.

## Week 3: June 7 - June 13, 2025

### ▶ Objectives

- Build out CLI session management: enforce login, add a help command

- Expose portfolio via CLI: implement portfolio command

- Enhance domain model: introduce a Position class with avg_price and unrealized P/L

- Strengthen test coverage: cover reservation logic and bolster match_orders tests

### ✔ Achievements this Week

– Added `Position` class to track per‐symbol average price and unrealized P/L in portfolios

– CLI: Implemented a login‐based terminal requiring login <trader_id> before other commands

– CLI: Added a help command to re-display available commands

– CLI: Introduced portfolio command (no longer echoes trader ID)

– Tests: Refactored and expanded match_orders unit tests to cover edge cases and priority fixes

– Tests: Added portfolio tests for reserving and un-reserving assets, verifying reserved cash/shares logic

### ⚠ Blockers & Challenges

- Session gating: Ensuring all commands enforce login without duplicating checks in each handler

- P/L calculation: Computing a correct running average price and unrealized P/L in Position under partial fills

- Test determinism: Stabilizing match_orders tests when FIFO and price‐priority logic interact in edge cases

- CLI ergonomics: Balancing concise command syntax with clear feedback (help text, error messages)

### Lessons Learned

- Undertook a broad codebase refactor—extracting a dedicated `Session` class, splitting engine, application, and `CLI` layers, and adopting dependency-injection patterns—to make the code more modular, testable, and maintainable.

- Designed and implemented reservation logic for traders: tracked `reserved_cash` and `reserved_positions`, applied delta-based unreserve/refund/reserve steps on partial fills, and ensured consistent state updates in `apply_trade`.
