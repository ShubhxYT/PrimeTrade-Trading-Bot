from enum import Enum
from typing import Optional


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LIMIT = "STOP_LIMIT"


class TimeInForce(str, Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"


def validate_order_params(
    side: OrderSide,
    order_type: OrderType,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> None:
    """Validate order parameters; raise ValueError on invalid combinations."""
    if quantity <= 0:
        raise ValueError(f"quantity must be > 0, got {quantity}")

    if order_type == OrderType.LIMIT:
        if price is None:
            raise ValueError("price is required for LIMIT orders")

    if order_type == OrderType.STOP_LIMIT:
        if price is None:
            raise ValueError("price (limit price) is required for STOP_LIMIT orders")
        if stop_price is None:
            raise ValueError(
                "stop_price (trigger price) is required for STOP_LIMIT orders"
            )
