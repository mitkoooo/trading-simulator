from dataclasses import dataclass


@dataclass
class Position:
    qty: int = 0
    avg_price: float = 0.0
