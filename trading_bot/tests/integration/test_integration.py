import os

import pytest

from bot.client import BinanceClient
from bot.orders import OrderService
from bot.validators import OrderSide


@pytest.mark.integration
class TestLiveTestnet:
    """
    Live testnet integration tests.
    Opt-in: pytest -m integration
    Requires BINANCE_API_KEY and BINANCE_API_SECRET in .env
    """

    @pytest.fixture(autouse=True)
    def require_credentials(self):
        if not os.getenv("BINANCE_API_KEY") or not os.getenv("BINANCE_API_SECRET"):
            pytest.skip(
                "BINANCE_API_KEY / BINANCE_API_SECRET not set — skipping integration tests"
            )

    @pytest.fixture
    def service(self) -> OrderService:
        return OrderService(BinanceClient())

    def test_place_market_order(self, service: OrderService):
        result = service.place_market_order("BTCUSDT", OrderSide.BUY, 0.001)
        assert result["orderId"] is not None
        assert result["status"] in ("FILLED", "PARTIALLY_FILLED", "NEW")

    def test_place_limit_order_far_from_market(self, service: OrderService):
        # Price far from market so the order rests as NEW without filling
        result = service.place_limit_order(
            "BTCUSDT", OrderSide.SELL, 0.001, price=9_999_999.0
        )
        assert result["orderId"] is not None
        assert result["status"] == "NEW"

    def test_place_stop_limit_order(self, service: OrderService):
        result = service.place_stop_limit_order(
            "BTCUSDT",
            OrderSide.BUY,
            0.001,
            price=100_000.0,
            stop_price=99_000.0,
        )
        assert result["orderId"] is not None
