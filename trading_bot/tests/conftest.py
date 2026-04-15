import pytest
from unittest.mock import MagicMock

from bot.client import BinanceClient


@pytest.fixture
def mock_client() -> MagicMock:
    """MagicMock standing in for BinanceClient across all unit tests."""
    return MagicMock(spec=BinanceClient)
