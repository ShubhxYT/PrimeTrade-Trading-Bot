"""
log_parser.py — parse trading_bot rotating log for order response records.

Log line format (from logging_config.py):
    YYYY-MM-DD HH:MM:SS | LEVEL    | logger.name | message

Order response lines look like:
    2026-04-15 12:00:01 | INFO     | bot.client | Order response | {'orderId': 123, ...}

The payload is a Python dict literal (single-quoted strings, Python bools),
so we use ast.literal_eval instead of json.loads.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pandas as pd

# Matches a full log line and captures timestamp, level, logger name, message
_LOG_LINE_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
    r"\s*\|\s*(?P<level>\w+)\s*\|\s*(?P<logger>[^|]+)\s*\|\s*(?P<message>.+)$"
)

# Matches an "Order response" message and captures the dict payload
_ORDER_RESPONSE_RE = re.compile(r"^Order response \| (?P<payload>\{.+\})$")

_COLUMNS = [
    "timestamp",
    "orderId",
    "status",
    "executedQty",
    "avgPrice",
    "symbol",
    "side",
    "type",
    "origQty",
    "price",
]

_EMPTY_DF = pd.DataFrame(columns=_COLUMNS)


def parse_log(log_path: str) -> pd.DataFrame:
    """
    Read *log_path* line-by-line and return a DataFrame of order records.

    Returns an empty DataFrame (with correct columns) when:
    - the file does not exist
    - the file is empty
    - no order response lines are found
    """
    path = Path(log_path)
    if not path.exists() or path.stat().st_size == 0:
        return _EMPTY_DF.copy()

    records: list[dict] = []

    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip()
            m = _LOG_LINE_RE.match(line)
            if not m:
                continue
            msg = m.group("message").strip()
            om = _ORDER_RESPONSE_RE.match(msg)
            if not om:
                continue
            try:
                payload: dict = ast.literal_eval(om.group("payload"))
            except (ValueError, SyntaxError):
                continue
            records.append(
                {
                    "timestamp": m.group("timestamp"),
                    "orderId": payload.get("orderId"),
                    "status": payload.get("status"),
                    "executedQty": payload.get("executedQty"),
                    "avgPrice": payload.get("avgPrice"),
                    "symbol": payload.get("symbol"),
                    "side": payload.get("side"),
                    "type": payload.get("type"),
                    "origQty": payload.get("origQty"),
                    "price": payload.get("price"),
                }
            )

    if not records:
        return _EMPTY_DF.copy()

    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S")
    for col in ("executedQty", "avgPrice", "origQty", "price"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
