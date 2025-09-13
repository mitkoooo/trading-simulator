from datetime import date
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel

DATA_PATH = Path(__file__).parent.parent / "config" / "market_data.yml"

class DailySummary(BaseModel):
    symbol: str
    date: date
    open: float
    previous_close: float



@lru_cache(maxsize=1)
def _load_all_data() -> dict[str, dict[str, dict]]:
    """Return a nested dict.

    { "YYYY-MM-DD": { "SYMBOL": {open:…, previous_close:…}, … }, … }

    """
    with DATA_PATH.open() as f:
        raw = yaml.safe_load(f) or {}
    return raw

def get_daily_summary(symbol: str,
                      for_date: date | None = None) -> DailySummary | None:
    d = (for_date or date.today())
    day_block = _load_all_data().get(d)
    if not day_block or symbol not in day_block:
        return None
    data = day_block[symbol]
    return DailySummary(symbol=symbol, date=d, **data)
