from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from bot.cli import app

runner = CliRunner()


def _make_result(order_type: str = "MARKET") -> dict:
    return {
        "orderId": 789,
        "status": "FILLED" if order_type == "MARKET" else "NEW",
        "executedQty": "0.01" if order_type == "MARKET" else "0",
        "avgPrice": "95234.10" if order_type == "MARKET" else "0",
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": order_type,
        "origQty": "0.01",
        "price": "0",
    }


class TestCLIValidation:
    def test_zero_quantity_exits_1(self):
        result = runner.invoke(app, ["BTCUSDT", "BUY", "MARKET", "0"])
        assert result.exit_code == 1

    def test_limit_missing_price_exits_1(self):
        result = runner.invoke(
            app, ["BTCUSDT", "BUY", "LIMIT", "0.01"]
        )
        assert result.exit_code == 1

    def test_stop_limit_missing_stop_price_exits_1(self):
        result = runner.invoke(
            app,
            ["BTCUSDT", "BUY", "STOP_LIMIT", "0.01", "--price", "31000"],
        )
        assert result.exit_code == 1


class TestCLISuccess:
    @patch("bot.cli.setup_logging")
    @patch("bot.cli.OrderService")
    @patch("bot.cli.BinanceClient")
    def test_market_order_prints_order_id(
        self, mock_client_cls, mock_service_cls, mock_setup
    ):
        mock_svc = MagicMock()
        mock_svc.place_market_order.return_value = _make_result("MARKET")
        mock_service_cls.return_value = mock_svc

        result = runner.invoke(
            app, ["BTCUSDT", "BUY", "MARKET", "0.01"]
        )
        assert result.exit_code == 0
        assert "789" in result.output
        assert "FILLED" in result.output

    @patch("bot.cli.setup_logging")
    @patch("bot.cli.OrderService")
    @patch("bot.cli.BinanceClient")
    def test_limit_order_success(
        self, mock_client_cls, mock_service_cls, mock_setup
    ):
        mock_svc = MagicMock()
        mock_svc.place_limit_order.return_value = _make_result("LIMIT")
        mock_service_cls.return_value = mock_svc

        result = runner.invoke(
            app,
            ["BTCUSDT", "SELL", "LIMIT", "0.01", "--price", "99999"],
        )
        assert result.exit_code == 0
        assert "789" in result.output

    @patch("bot.cli.setup_logging")
    @patch("bot.cli.OrderService")
    @patch("bot.cli.BinanceClient")
    def test_stop_limit_order_success(
        self, mock_client_cls, mock_service_cls, mock_setup
    ):
        mock_svc = MagicMock()
        mock_svc.place_stop_limit_order.return_value = _make_result("STOP")
        mock_service_cls.return_value = mock_svc

        result = runner.invoke(
            app,
            [
                "BTCUSDT", "BUY", "STOP_LIMIT", "0.01",
                "--price", "31000",
                "--stop-price", "30500",
            ],
        )
        assert result.exit_code == 0


class TestCLIApiErrors:
    @patch("bot.cli.setup_logging")
    @patch("bot.cli.OrderService")
    @patch("bot.cli.BinanceClient")
    def test_client_error_exits_1(
        self, mock_client_cls, mock_service_cls, mock_setup
    ):
        from binance.error import ClientError

        mock_svc = MagicMock()
        mock_svc.place_market_order.side_effect = ClientError(
            400, -1121, "Invalid symbol.", {}
        )
        mock_service_cls.return_value = mock_svc

        result = runner.invoke(
            app, ["BADPAIR", "BUY", "MARKET", "0.01"]
        )
        assert result.exit_code == 1
