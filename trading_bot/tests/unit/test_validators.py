import pytest

from bot.validators import (
    OrderSide,
    OrderType,
    TimeInForce,
    validate_order_params,
)


class TestEnums:
    def test_order_side_is_str(self):
        assert OrderSide.BUY == "BUY"
        assert OrderSide.SELL == "SELL"

    def test_order_type_values(self):
        assert OrderType.MARKET == "MARKET"
        assert OrderType.LIMIT == "LIMIT"
        assert OrderType.STOP_LIMIT == "STOP_LIMIT"

    def test_time_in_force_values(self):
        assert TimeInForce.GTC == "GTC"
        assert TimeInForce.IOC == "IOC"
        assert TimeInForce.FOK == "FOK"


class TestValidateOrderParams:
    def test_market_order_valid(self):
        validate_order_params(OrderSide.BUY, OrderType.MARKET, 0.01)

    def test_limit_order_valid(self):
        validate_order_params(OrderSide.SELL, OrderType.LIMIT, 0.01, price=30000.0)

    def test_stop_limit_order_valid(self):
        validate_order_params(
            OrderSide.BUY,
            OrderType.STOP_LIMIT,
            0.01,
            price=31000.0,
            stop_price=30500.0,
        )

    @pytest.mark.parametrize("quantity", [0, -1, -0.001])
    def test_invalid_quantity(self, quantity: float):
        with pytest.raises(ValueError, match="quantity must be > 0"):
            validate_order_params(OrderSide.BUY, OrderType.MARKET, quantity)

    def test_limit_missing_price(self):
        with pytest.raises(ValueError, match="price is required for LIMIT"):
            validate_order_params(OrderSide.BUY, OrderType.LIMIT, 0.01)

    def test_stop_limit_missing_price(self):
        with pytest.raises(ValueError, match="price .* is required for STOP_LIMIT"):
            validate_order_params(
                OrderSide.BUY, OrderType.STOP_LIMIT, 0.01, stop_price=30500.0
            )

    def test_stop_limit_missing_stop_price(self):
        with pytest.raises(ValueError, match="stop_price .* is required for STOP_LIMIT"):
            validate_order_params(
                OrderSide.BUY, OrderType.STOP_LIMIT, 0.01, price=31000.0
            )
