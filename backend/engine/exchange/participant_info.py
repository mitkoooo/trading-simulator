from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

class ParticipantType(Enum):
    """SOME DOCSTRING""" #TODO
    DIRECT_MEMBER = "direct_member"
    BROKER = "broker"
    SYSTEM = "system"
    SPONSORED = "sponsored_client"

class MarginCategory(Enum):
    """SOME DOCSTRING""" #TODO
    STANDARD_EQUITY    = "standard_equity"  # typical long/short stock positions
    DAY_TRADER_EQUIV   = "day_trader_equiv"  # reduced intraday requirements, T+0
    OPTION_WRITES      = "option_writes"  # covered calls, margin against underlying
    UNSECURED_LEVERAGE = "unsecured_leverage"  # special high‑risk lines, e.g. crypto
    FUTURES            = "futures"  # regulated futures contracts


@dataclass
class ParticipantInfo:
    """SOME DOCSTRING""" #TODO


    # - IDENTITY & ROUTING -
    mpid: str
    display_name: str
    ptype: ParticipantType
    sponsor_broker: Optional[str] = None # if SPONSORED, which broker MPID


    # - PERMISSION & CONTROLS - 
    allowed_symbols: List[str] = field(default_factory=list)
    max_order_size: Dict[str, int] = field(default_factory=dict)

    # Per minute cap of the dollar value of everything a participant trades.
    # If they buy 100 shares at $150, that’s $15 000 of notional
    max_notional_per_minute: float = float("inf")  

    # Every order submission, modification, or cancellation is a message.
    max_msgs_per_second: int = 1_000


    # - PRETRADE RISK SETTINGS - 
    margin_category: MarginCategory = MarginCategory.STANDARD_EQUITY
    # e.g. ±5% around reference price
    price_band_limit: float | None = 0.05      


    # - CLEARING & SETTLEMENT - 
    clearing_member_id: Optional[str] = None
    settlement_account: Optional[str] = None
    

    # - TELEMETRY & AUDITING - 
    active_order_count: int = 0 
    last_heartbeat: Optional[datetime] = None
    orders_in: int = 0 
    cancels_in: int = 0 
    trades_out: int = 0 
    last_error_code: Optional[str] = None


    # - INITIAL COLLATERAL - 
    initial_cash: float = 0.0
    initial_positions: Dict[str, int] = field(default_factory=dict) # SYMBOL --> SHARES


