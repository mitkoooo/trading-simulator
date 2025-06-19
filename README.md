# Stock Trading Simulator

This project implements a discrete-time stock trading simulator designed to model the behavior of a simplified exchange environment. It provides a priority–queue–based matching engine for buy and sell orders, portfolio tracking for users, and infrastructure for evaluating strategies over historical price data.

---

## Features

- **Matching Engine**  
  Custom-built order book using max- and min-heaps to simulate price-time priority matching of buy and sell orders.

- **Market Simulation**  
  Time-stepped engine capable of replaying historical stock price data and processing market events deterministically.

- **Portfolio Management**  
  Per-user asset tracking, cash balance updates, and transaction logs for auditability.

- **Strategy API**  
  Interface for automated trading bots to interact with the market based on user-defined heuristics or models.

- **Profit Optimization Tool**  
  Integration of Kadane’s algorithm and dynamic programming to determine optimal trade windows.

- **Performance Metrics**  
  Tools for computing profitability, drawdown, and Sharpe ratio of trading strategies.

- **Extensible Architecture**  
  Designed for future support of multiple instruments, order types (e.g., stop-loss), and real-time GUI dashboards.

---

## Technologies Used

- **Language**: Python 3.11+, TypeScript 5.8.3+
- **Libraries**: `FastApi` for backend, `React` + `TailwindCSS` for frontend
- **Design Paradigms**: Modular OOP, event-driven simulation, separation of concerns

---

## Repository Structure

```bash
trading-simulator/
├── backend/                    # Python “engine” & API
│   ├── app/
│   ├── cli/
│   ├── engine/
│   ├── view/
│   ├── main.py
│   ├── logging_config.py
│   ├── pyproject.toml
│   ├── poetry.lock
│   └── Dockerfile
├── frontend/                   # TypeScript React/Vite or Next.js UI
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── yarn.lock
│   ├── vite.config.ts
│   └── Dockerfile
├── data/                       # historical CSV feeds, sample data
├── scripts/                    # helper scripts (e.g. migrations, ETL)
├── docker-compose.yml
├── tests/
└── README.md
```

---

## Setup Instructions

### Prerequisites

- **Docker & Docker Compose**  
  Install Docker Desktop (macOS/Windows) or `docker.io` + `docker-compose` (Linux) so you can spin up both services with a single command.

- **Python 3.11+ & Poetry** (backend)  
  We use Poetry to manage and lock Python dependencies.

  ```bash
  # Install Poetry (if not already)
  curl -sSL https://install.python-poetry.org | python3 -
  ```

- **Node.js 18+ & Yarn** (frontend)
  The UI is built with Vite (or Next.js) and uses Yarn to lock JS deps.

```bash
# macOS/Linux

npm install --global yarn
```

### Clone & get up and running

```bash
git clone https://github.com/vadimmitko/trading-simulator.git
cd trading-simulator

# 1) Backend
cd backend
poetry install          # installs Python deps into the container or virtualenv

# 2) Frontend
cd ../frontend
yarn install            # installs JS deps

# 3) Start everything
cd ..
docker-compose up --build
```

After Docker builds and starts:

- Backend API ➜ http://localhost:8000 (interactive docs at /docs)

- Frontend UI ➜ http://localhost:3000

## Using the backend CLI

Start the CLI:

```bash
python main.py
```

You’ll see:

```text
YORK STOCK EXCHANGE TERMINAL

Please log in with your Trader ID before issuing any other commands.

    login      — Authenticate using your Trader ID
    logout     - Log out the trader
    help       — Display this menu
    next       — Refresh market data
    match      — Execute order matching
    portfolio  — View your portfolio holdings and P&L
    status     — Show pending orders
    buy        — Place a buy order
    sell       — Place a sell order
    quit       — Exit the terminal
```

Use the commands

```text
>>> next
AAPL: $150.23
MSFT: $295.12
…
>>> buy AAPL 5 150.00

Order placed for AAPL.

>>> status
[2025-05-28 10:15:00] Pending Buy Order: 5 shares of AAPL at $150.00.

>>> match AAPL
No trades yet

>>> quit
Thank you for using York Stock Exchange.
```

---

## Testing

Run the full unit test suite using:

```bash
pytest
```

---

## Future Enhancements

- Support for multiple financial instruments
- Stop-loss and limit order types
- Historical backtesting for strategy validation
- Streamlit-based graphical dashboard

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## Author

**Vadim Mitko**  
Computer Science Undergraduate, University of York

Email: [vadim@mitko.me](vadim@mitko.me)

GitHub: [github.com/mitkoooo](https://github.com/mitkoooo)

LinkedIn: [linkedin.com/in/vadim-mitko-b021772a1/](https://linkedin.com/in/vadim-mitko-b021772a1/)

## Week 1 Complete

#### Core CLI & Engine

- **Interactive CLI** with commands:

  - `next` — advance prices
  - `buy SYMBOL QTY PRICE` / `sell SYMBOL QTY PRICE` — enqueue orders
  - `status` — list pending orders
  - `match SYMBOL` — stubbed matching engine

- **Uniform ±1% tick stub** for Week 1 (will swap to Gaussian GBM in Week 8).

#### Observability

- **Structured logging** of every command (file handler, custom formatter).
- **Smoke test** driving the CLI via subprocess to catch errors.

#### Quality & Documentation

- **Unit tests** covering all `engine/` classes and CLI validation logic (≥ 80 % coverage).
- **Docstrings** on every public method + executable examples passing `pytest --doctest-modules`.

---

### Quick demo

```text
$ python main.py
Welcome to York Stock Exchange!

>>> next
AAPL: $150.23
MSFT: $295.12

>>> buy AAPL 5 150.00
Order placed for AAPL.

Cash balance: $999250.00
Holdings: {'AAPL': 5}

>>> status
[2025-05-28 10:15:00] Pending Buy Order: 5 shares of AAPL at $150.00.

>>> match AAPL
No trades yet

>>> quit
Thank you for using York Stock Exchange.
```
