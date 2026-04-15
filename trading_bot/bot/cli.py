from __future__ import annotations

import logging
from typing import Optional

import typer

from binance.error import ClientError, ServerError

from bot.client import BinanceClient
from bot.logging_config import setup_logging
from bot.orders import OrderService
from bot.validators import OrderSide, OrderType, TimeInForce, validate_order_params

app = typer.Typer(
    add_completion=False,
    help="Binance USDT-M Futures testnet trading bot.",
)


@app.command("place-order")
def place_order(
    symbol: str = typer.Argument(..., help="Trading pair, e.g. BTCUSDT"),
    side: OrderSide = typer.Argument(..., help="BUY or SELL"),
    order_type: OrderType = typer.Argument(..., help="MARKET, LIMIT, or STOP_LIMIT"),
    quantity: float = typer.Argument(..., help="Order quantity"),
    price: Optional[float] = typer.Option(
        None, "--price", help="Limit price (required for LIMIT and STOP_LIMIT)"
    ),
    stop_price: Optional[float] = typer.Option(
        None, "--stop-price", help="Stop/trigger price (required for STOP_LIMIT)"
    ),
    time_in_force: TimeInForce = typer.Option(
        TimeInForce.GTC, "--time-in-force", help="Time in force: GTC, IOC, FOK"
    ),
    log_level: str = typer.Option("INFO", "--log-level", help="Logging verbosity"),
) -> None:
    setup_logging(log_level=log_level)
    logger = logging.getLogger(__name__)

    # ── Validate ──────────────────────────────────────────────────────────────
    try:
        validate_order_params(
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except ValueError as exc:
        typer.secho(f"Validation error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    # ── Request summary ───────────────────────────────────────────────────────
    _divider = "─" * 52
    typer.echo(f"\n{_divider}")
    typer.secho("  ORDER REQUEST SUMMARY", bold=True)
    typer.echo(_divider)
    typer.echo(f"  Symbol     : {symbol}")
    typer.echo(f"  Side       : {side.value}")
    typer.echo(f"  Type       : {order_type.value}")
    typer.echo(f"  Quantity   : {quantity}")
    if price is not None:
        typer.echo(f"  Price      : {price}")
    if stop_price is not None:
        typer.echo(f"  Stop Price : {stop_price}")
    if order_type != OrderType.MARKET:
        typer.echo(f"  TIF        : {time_in_force.value}")
    typer.echo(_divider + "\n")

    # ── Place order ───────────────────────────────────────────────────────────
    try:
        client = BinanceClient()
        service = OrderService(client)

        if order_type == OrderType.MARKET:
            result = service.place_market_order(symbol, side, quantity)
        elif order_type == OrderType.LIMIT:
            result = service.place_limit_order(
                symbol, side, quantity, price, time_in_force
            )
        else:  # STOP_LIMIT
            result = service.place_stop_limit_order(
                symbol, side, quantity, price, stop_price, time_in_force
            )

    except ValueError as exc:
        typer.secho(f"Configuration error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except ClientError as exc:
        typer.secho(
            f"API error [{exc.error_code}]: {exc.error_message}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
    except ServerError as exc:
        typer.secho(
            f"Server error (HTTP {exc.status_code})", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1)
    except Exception as exc:
        typer.secho(f"Unexpected error: {exc}", fg=typer.colors.RED, err=True)
        logger.exception("Unexpected error placing order")
        raise typer.Exit(code=1)

    # ── Response ──────────────────────────────────────────────────────────────
    typer.echo(_divider)
    typer.secho("  ORDER RESPONSE", bold=True)
    typer.echo(_divider)
    typer.echo(f"  Order ID     : {result.get('orderId')}")
    typer.echo(f"  Status       : {result.get('status')}")
    typer.echo(f"  Executed Qty : {result.get('executedQty')}")
    typer.echo(f"  Avg Price    : {result.get('avgPrice')}")
    typer.echo(_divider)
    typer.secho("\n  Order placed successfully!\n", fg=typer.colors.GREEN, bold=True)
