from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from engine.position import Position


class ParticipantType(Enum):
    """Enum of types of market participants allowed on the exchange.

    Attributes:
        DIRECT_MEMBER (str):
            Market participant that has direct account with clearing system.
        
        SYSTEM (str):
            System market participant that seeds intial orders.

        SPONSORED (str):
            Business or an individual who is provided access by
            a market participant.

    """

    DIRECT_MEMBER = "direct_member"
    SYSTEM = "system"
    SPONSORED = "sponsored_client"


class MarginCategory(Enum):
    """Categories of margin requirements for different trading strategies.
    
    Attributes:
        STANDARD_EQUITY (str):
            Traditional long/short stock positions without
            standard margin (e.g., 50% initial).

        DAY_TRADER_EQUIV (str):
            Intraday equity positions with reduced margin and
            higher equity minimums.

        OPTION_WRITES (str):
            Covered options using the underlying as collateral.
        UNSECURED_LEVERAGE (str):
            High-risk margin (e.g., crypto), often without secured collateral.

        FUTURES (str):
            Regulated futures with exchange-set initial, maintenance,
            and variation margins.

    """

    # typical long/short stock positions
    STANDARD_EQUITY = "standard_equity"

    # reduced intraday requirements, T+0
    DAY_TRADER_EQUIV = "day_trader_equiv"

    # covered calls, margin against underlying
    OPTION_WRITES = "option_writes"

    # special high-risk lines, e.g. crypto
    UNSECURED_LEVERAGE = "unsecured_leverage"

    # regulated futures contracts
    FUTURES = "futures"


@dataclass
class ParticipantInfo:
    """Represents a market participant's identity and permissions.

    Attributes:
        mpid (str):
            Unqiue market participant identifier.

        display_name (str):
            Name of the participant.

        ptype (ParticipantType):
            Participant type (e.g. clearing firm, sponsored account).

        sponsor_broker (str or None):
            Sponsor MPID if this participant trades with other firm support.

        allowed_symbols (list[str]):
            List of security symbols the participant may trade.

        max_order_size (dict[str, int]):
            Per-symbol maximum order quantity limits.

        max_notional_per_minute (float):
            Value cap on trades per minute to control flow.

        max_msgs_per_second (int):
            Message throughput limit (submissions, cancels, modifications).

        margin_category (MarginCategory):
            Risk category defining margin rules.

        price_band_limit (float or None):
            Permitted price deviation from reference before rejection.

        clearing_member_id (str or None):
            Identifier for the clearing firm backing this participant.

        settlement_account (str or None):
            Settlement account used for post-trade settlement.

        active_order_count (int):
            How many orders are open right now.
 
        last_heartbeat (datetime or none):
            Timestamp of the last heartbeat from this participant.

        orders_in (int):
            Total number of orders submitted.

        cancels_in (int):
            Total number of cancellations received.

        trades_out (int):
            Number of executed trades routed out.

        last_error_code (str or None):
            Most recent error code (if any).

        initial_cash (float):
            Collateral cash allocated at session start.

        initial_positions (dict[str, Position]):
            Starting securities positions (symbol → Position).

    """

    # - IDENTITY & ROUTING -
    mpid: str
    display_name: str
    ptype: ParticipantType
    sponsor_broker: str | None = None  # if SPONSORED, which broker MPID

    # - PERMISSION & CONTROLS -
    allowed_symbols: list[str] = field(default_factory=list)
    max_order_size: dict[str, int] = field(default_factory=dict)

    # Per minute cap of the dollar value of everything a participant trades.
    # If they buy 100 shares at $150, that's $15,000 of notional
    max_notional_per_minute: float = float("inf")

    # Every order submission, modification, or cancellation is a message.
    max_msgs_per_second: int = 1_000

    # - PRETRADE RISK SETTINGS -
    margin_category: MarginCategory = MarginCategory.STANDARD_EQUITY
    # e.g. ±5% around reference price
    price_band_limit: float | None = 0.05

    # - CLEARING & SETTLEMENT -
    clearing_member_id: str | None = None
    settlement_account: str | None = None

    # - TELEMETRY & AUDITING -
    active_order_count: int = 0
    last_heartbeat: datetime | None = None
    orders_in: int = 0
    cancels_in: int = 0
    trades_out: int = 0
    last_error_code: str | None = None

    # - INITIAL COLLATERAL -
    initial_cash: float = 0.0

    # SYMBOL -> SHARES
    initial_positions: dict[str, Position] = field(default_factory=dict)
