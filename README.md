# Binance Futures Testnet Trading Bot

Python CLI for placing **MARKET**, **LIMIT**, and **STOP-LIMIT** orders on Binance USDT-M Futures Testnet with structured logging and full error handling.

## Setup

```bash
git clone <repo-url> && cd trading_bot
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env
# Edit .env with your testnet API key and secret
```

**Get testnet credentials**: https://testnet.binancefuture.com

## Usage

```bash
trading-bot SYMBOL SIDE ORDER_TYPE QUANTITY [OPTIONS]

# Market Order
trading-bot BTCUSDT BUY MARKET 0.001

# Limit Order
trading-bot BTCUSDT SELL LIMIT 0.001 --price 99999

# Stop-Limit Order (Bonus)
trading-bot BTCUSDT BUY STOP_LIMIT 0.001 --price 31000 --stop-price 30500

# With time-in-force
trading-bot BTCUSDT BUY LIMIT 0.001 --price 42000 --time-in-force IOC
```

**Options**: `--price` (LIMIT/STOP_LIMIT), `--stop-price` (STOP_LIMIT), `--time-in-force` {GTC,IOC,FOK}, `--log-level` {DEBUG,INFO,WARNING,ERROR}

## Testing

```bash
pytest -v                      # All tests
pytest tests/unit/ -v          # Unit only (no credentials)
pytest tests/integration/ -v   # Integration (requires .env)
```

## Project Structure

```
trading_bot/
├── bot/
│   ├── cli.py           # CLI entry point (Typer)
│   ├── client.py        # Binance API wrapper
│   ├── orders.py        # Order service & validation
│   ├── validators.py    # Input validation & Enums
│   └── logging_config.py # Logging with rotation
├── tests/ (unit/ + integration/)
├── logs/ (auto-created)
├── pyproject.toml
└── requirements.txt
```

## Architecture

- **Client** (`client.py`): Wraps python-binance, handles authentication
- **Orders** (`orders.py`): Constructs & places validated orders
- **Validators** (`validators.py`): Input validation, Enums (OrderSide, OrderType, TimeInForce)
- **CLI** (`cli.py`): Typer-based parsing, error handling, pretty printing
- **Logging** (`logging_config.py`): File rotation (5MB, 3 backups) to `logs/trading_bot.log`

## Bonus Features

✨ **Stop-Limit Orders** — Conditional orders with trigger + limit price  
✨ **Configurable Time-in-Force** — GTC, IOC, FOK support  
✨ **Streamlit UI** — `pip install -e ".[ui]"` && `streamlit run streamlit_app/app.py`

## Key Assumptions

1. **Quantity Precision**: Use ≤3 decimals for BTCUSDT (e.g., `0.001`)
2. **STOP_LIMIT on USDT-M**: Uses `type="STOP"` with `price` + `stopPrice`
3. **Testnet URL**: `https://testnet.binancefuture.com` (override via `BINANCE_BASE_URL`)
4. **Logs**: Written to `logs/trading_bot.log` with rotation
5. **Integration Tests**: LIMIT orders placed far from market (`$9,999,999`) to rest
6. **Error Handling**: Network/API errors logged & re-raised with context

## Resources

- [Binance Futures Docs](https://binance-docs.github.io/apidocs/futures/)
- [Testnet](https://testnet.binancefuture.com)
- [python-binance](https://github.com/binance/binance-connector-python)
- [Typer](https://typer.tiangolo.com)

**Submission**: PrimeTrade Python Developer Intern Assignment
