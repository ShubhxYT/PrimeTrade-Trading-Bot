import logging
import os

from binance.error import ClientError, ServerError
from binance.um_futures import UMFutures
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class BinanceClient:
    """Thin wrapper around UMFutures that handles env loading, logging, and error re-raise."""

    def __init__(self) -> None:
        load_dotenv()
        api_key = os.getenv("BINANCE_API_KEY", "")
        api_secret = os.getenv("BINANCE_API_SECRET", "")
        base_url = os.getenv("BINANCE_BASE_URL", "https://demo-fapi.binance.com")

        if not api_key or not api_secret:
            raise ValueError(
                "BINANCE_API_KEY and BINANCE_API_SECRET must be set in .env"
            )

        self._client = UMFutures(key=api_key, secret=api_secret, base_url=base_url)
        logger.info("BinanceClient initialized | base_url=%s", base_url)

    def new_order(self, **kwargs) -> dict:
        """Call UMFutures.new_order, log request/response, re-raise API errors."""
        # Mask any key-like params before logging
        masked = {k: ("***" if "key" in k.lower() else v) for k, v in kwargs.items()}
        logger.info("Placing order | params=%s", masked)

        try:
            response = self._client.new_order(**kwargs)
            logger.info("Order response | %s", response)
            return response
        except ClientError as exc:
            logger.error(
                "ClientError | status=%s code=%s message=%s",
                exc.status_code,
                exc.error_code,
                exc.error_message,
            )
            raise
        except ServerError as exc:
            logger.error("ServerError | status=%s", exc.status_code)
            raise
