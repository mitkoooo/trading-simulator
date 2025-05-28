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

- **Language**: Python 3.11+
- **Libraries**: `pandas`, `streamlit`, `pytest`
- **Design Paradigms**: Modular OOP, event-driven simulation, separation of concerns

---

## Repository Structure

```bash
trading-simulator/
├── engine/
├── data/
├── scripts/
├── cli/
├── view/
├── tests/
├── logging_config.py
├── main.py
└── README.md
```

---

## Setup Instructions

### Prerequisites

- Python 3.11 or newer
- `pip`, `venv` for dependency management

### Clone & install dependencies

```bash
git clone https://github.com/vadimmitko/trading-simulator.git
cd trading-simulator
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

---

## Usage

Start the CLI:

```bash
python main.py
```

You’ll see:

```text
Welcome to York Stock Exchange. To continue please enter one of the following commands:

    next - To update stock prices
    match - To match orders
    status - To display pending orders
    buy - To buy a stock
    sell - To sell a stock
    quit - to exit York Stock Exchange
```

Use the commands

```text
>>> next
AAPL: $150.23
MSFT: $295.12
…
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

## Week 1 Design

Week 1 uses a uniform ±1% stub; in Week 8 we’ll swap in Gaussian GBM via tick_model.
