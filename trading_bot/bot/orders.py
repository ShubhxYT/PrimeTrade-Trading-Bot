import logging
from typing import Optional

from bot.client import BinanceClient
from bot.validators import OrderSide, OrderType, TimeInForce

logger = logging.getLogger(__name__)


class OrderService:
    """Handles construction and dispatch of USDT-M Futures orders."""

    def __init__(self, client: BinanceClient) -> None:
        self._client = client

    def place_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
    ) -> dict:
        kwargs = {
            "symbol": symbol,
            "side": side.value,
            "type": "MARKET",
            "quantity": quantity,
        }
        response = self._client.new_order(**kwargs)
        return self._extract_result(response)

    def place_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        price: float,
        time_in_force: TimeInForce = TimeInForce.GTC,
    ) -> dict:
        kwargs = {
            "symbol": symbol,
            "side": side.value,
            "type": "LIMIT",
            "timeInForce": time_in_force.value,
            "quantity": quantity,
            "price": price,
        }
        response = self._client.new_order(**kwargs)
        return self._extract_result(response)

    def place_stop_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        price: float,
        stop_price: float,
        time_in_force: TimeInForce = TimeInForce.GTC,
    ) -> dict:
        # USDT-M Futures Stop-Limit uses type="STOP" (not "STOP_LIMIT")
        # price = limit fill price; stopPrice = trigger price
        kwargs = {
            "symbol": symbol,
            "side": side.value,
            "type": "STOP",
            "timeInForce": time_in_force.value,
            "quantity": quantity,
            "price": price,
            "stopPrice": stop_price,
        }
        response = self._client.new_order(**kwargs)
        return self._extract_result(response)

    @staticmethod
    def _extract_result(response: dict) -> dict:
        return {
            "orderId": response.get("orderId"),
            "status": response.get("status"),
            "executedQty": response.get("executedQty"),
            "avgPrice": response.get("avgPrice"),
            "symbol": response.get("symbol"),
            "side": response.get("side"),
            "type": response.get("type"),
            "origQty": response.get("origQty"),
            "price": response.get("price"),
        }
