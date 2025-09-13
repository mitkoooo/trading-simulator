from dataclasses import dataclass, field
from datetime import date
from typing import Literal


@dataclass
class OrderInfo:
    """."""  #TODO
    
    mpid: str 
    symbol: str 
    order_type: Literal["buy", "sell"]
    fill_qty: int
    avg_fill_price: float | None
    status: Literal["pending", "partially_filled", "filled", "cancelled"]
    order_id: str
    timestamp: date

    # This will be set automatically after initialization
    remaining_qty: int = field(init=False)

    def __post_init__(self) -> None:
        """Keep internal counter for number of shares left to fill."""
        # By default, remaining_qty equals fill_qty
        self.remaining_qty = self.fill_qty
