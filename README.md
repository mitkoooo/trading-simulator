# Stock Exchange Simulator

This project implements a discrete-time stock exchange simulator designed to model the behavior of a simplified exchange environment. It provides a priority–queue–based matching engine for buy and sell orders, portfolio tracking for users.

---

## Features

- **Matching Engine**  
  A custom order book that maintains sorted maps of buy and sell prices each pointing to FIFO queues of limit orders,
  alongside separate FIFO queues for market‐price buys and sells—fully enforcing price‐time priority.

- **Portfolio Management**  
  Per-user asset tracking, cash balance updates, and transaction logs for auditability.

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
│   ├── scripts/                    # helper scripts (e.g. bootstrap)
│   ├── main.py
│   ├── logging_config.py
│   ├── pyproject.toml
│   ├── uv.lock
│   └── Dockerfile
├── frontend/                   # TypeScript React UI
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── yarn.lock
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── tests/
└── README.md
```

---

## Setup Instructions

### Prerequisites

- **Docker & Docker Compose**  
  Install Docker Desktop (macOS/Windows) or `docker.io` + `docker-compose` (Linux) so you can spin up both services with a single command.

- **Python 3.11+ & UV** (backend)  
  UV is used to manage and lock Python dependencies.

  ```bash
  # Install UV (if not already)
  curl -LsSf https://astral.sh/uv/install.sh | sh
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
cd stock-exchange-sim

# 1) Backend
cd backend
uv sync          # installs Python deps into the container or virtualenv

# 2) Frontend
cd ../frontend
bun install            # installs JS deps

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
python backend/main.py
```

You’ll see:

```text
STOCK EXCHANGE TERMINAL

Please log in with your Trader ID before issuing any other commands.

    login      — Authenticate using your Trader ID
    logout     - Log out the trader
    help       — Display this menu
    next       — Refresh market data
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

>>> quit
Thank you for using Stock Exchange.
```

---

## Testing

Run the full unit test suite using:

```bash
uv run pytest
```

---

## Future Enhancements

- Support for multiple financial instruments
- Historical backtesting for strategy validation

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
