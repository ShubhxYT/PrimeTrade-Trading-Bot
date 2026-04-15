import pytest
from unittest.mock import MagicMock

from bot.orders import OrderService
from bot.validators import OrderSide, TimeInForce

_MOCK_RESPONSE = {
    "orderId": 123456,
    "status": "NEW",
    "executedQty": "0",
    "avgPrice": "0",
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
    "origQty": "0.01",
    "price": "0",
}


@pytest.fixture
def service(mock_client: MagicMock) -> OrderService:
    mock_client.new_order.return_value = _MOCK_RESPONSE
    return OrderService(mock_client)


class TestMarketOrder:
    def test_calls_client_with_correct_kwargs(
        self, service: OrderService, mock_client: MagicMock
    ):
        service.place_market_order("BTCUSDT", OrderSide.BUY, 0.01)
        mock_client.new_order.assert_called_once_with(
            symbol="BTCUSDT",
            side="BUY",
            type="MARKET",
            quantity=0.01,
        )

    def test_returns_structured_dict(self, service: OrderService):
        result = service.place_market_order("BTCUSDT", OrderSide.BUY, 0.01)
        assert result["orderId"] == 123456
        assert result["status"] == "NEW"
        assert "executedQty" in result
        assert "avgPrice" in result


class TestLimitOrder:
    def test_calls_client_with_correct_kwargs(
        self, service: OrderService, mock_client: MagicMock
    ):
        service.place_limit_order("BTCUSDT", OrderSide.SELL, 0.01, 99000.0)
        mock_client.new_order.assert_called_once_with(
            symbol="BTCUSDT",
            side="SELL",
            type="LIMIT",
            timeInForce="GTC",
            quantity=0.01,
            price=99000.0,
        )

    def test_custom_time_in_force(
        self, service: OrderService, mock_client: MagicMock
    ):
        service.place_limit_order(
            "BTCUSDT", OrderSide.BUY, 0.01, 90000.0, time_in_force=TimeInForce.IOC
        )
        assert mock_client.new_order.call_args[1]["timeInForce"] == "IOC"


class TestStopLimitOrder:
    def test_uses_type_stop(self, service: OrderService, mock_client: MagicMock):
        service.place_stop_limit_order(
            "BTCUSDT", OrderSide.BUY, 0.01, price=31000.0, stop_price=30500.0
        )
        kwargs = mock_client.new_order.call_args[1]
        assert kwargs["type"] == "STOP"

    def test_camelcase_stop_price(self, service: OrderService, mock_client: MagicMock):
        service.place_stop_limit_order(
            "BTCUSDT", OrderSide.SELL, 0.01, price=28000.0, stop_price=28500.0
        )
        kwargs = mock_client.new_order.call_args[1]
        assert "stopPrice" in kwargs
        assert "stop_price" not in kwargs
        assert kwargs["stopPrice"] == 28500.0

    def test_both_price_and_stop_price_present(
        self, service: OrderService, mock_client: MagicMock
    ):
        service.place_stop_limit_order(
            "BTCUSDT", OrderSide.BUY, 0.01, price=31000.0, stop_price=30500.0
        )
        kwargs = mock_client.new_order.call_args[1]
        assert kwargs["price"] == 31000.0
        assert kwargs["stopPrice"] == 30500.0
