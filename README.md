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
- **Libraries**: `heapq`, `pandas`, `datetime`, `streamlit` (optional), `pytest`
- **Design Paradigms**: Modular OOP, event-driven simulation, separation of concerns

---

## Repository Structure

```bash
    trading-simulator/
    ├── engine/
    ├── data/
    ├── scripts/
    ├── tests/
    ├── main.py
    └── README.md
```

---

## Setup Instructions

### Prerequisites

- Python 3.11 or newer
- `pip`, `venv`, or `poetry` for dependency management

### Installation

```bash
git clone https://github.com/vadimmitko/trading-simulator.git
cd trading-simulator
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

---

## Usage

To simulate a trading session:

```bash
python main.py
```

To evaluate a custom bot strategy or run performance tests:

```bash
python scripts/sample_bot.py
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
