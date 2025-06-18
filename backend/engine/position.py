from dataclasses import dataclass


@dataclass
class Position:
    """Represent a position in a trader's portfolio.

    Keeps track of the quantity held, along with the average price they were bought at.

    Attributes:
        qty (int): Quantity held.
        avg_price (float): Average price of held positions.

    Examples:
        >>> p = Position(qty=42, avg_price=100.0)
        >>> p.qty
        42
        >>> p.avg_price
        100.0
    """

    qty: int = 0
    avg_price: float = 0.0
