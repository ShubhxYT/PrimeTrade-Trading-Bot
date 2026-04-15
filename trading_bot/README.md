# Binance Futures Testnet Trading Bot

A Python CLI application for placing MARKET, LIMIT, and Stop-Limit orders on Binance USDT-M Futures Testnet with structured logging and full error handling.

---

## Setup

### 1. Clone and install

```bash
git clone <repo-url>
cd trading_bot
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in:
```
BINANCE_API_KEY=<your testnet API key>
BINANCE_API_SECRET=<your testnet API secret>
BINANCE_BASE_URL=https://demo-fapi.binance.com
```

Get testnet credentials at: https://testnet.binancefuture.com

### 3. Verify installation

```bash
trading-bot --help
```

---

## Running Examples

### Market order
```bash
trading-bot BTCUSDT BUY MARKET 0.001
```

### Limit order
```bash
trading-bot BTCUSDT SELL LIMIT 0.001 --price 99999
```

### Stop-Limit order (Bonus)
```bash
trading-bot BTCUSDT BUY STOP_LIMIT 0.001 --price 31000 --stop-price 30500
```

### With custom time-in-force and log level
```bash
trading-bot BTCUSDT BUY LIMIT 0.001 --price 90000 --time-in-force IOC --log-level DEBUG
```

### Alternative (without `pip install -e .`)
```bash
cd trading_bot
python -m bot.cli BTCUSDT BUY MARKET 0.001
```

---

## Running Tests

```bash
# Unit tests — no credentials needed
pytest tests/unit/ -v

# Integration tests — requires .env with valid credentials
pytest -m integration -v
```

---

## Assumptions

1. **Quantity precision**: The bot validates `quantity > 0` but does not fetch the exchange `LOT_SIZE` filter for each symbol. Binance will reject quantities with too many decimal places — use ≤ 3 decimal places for BTCUSDT (e.g., `0.001`).

2. **Stop-Limit type on USDT-M Futures**: The correct Binance API value is `type="STOP"` with both `price` (limit fill price) and `stopPrice` (trigger price). `"STOP_LIMIT"` is used for COIN-M Futures and will be rejected here.

3. **Testnet base URL**: `https://demo-fapi.binance.com` — override via `BINANCE_BASE_URL` in `.env`.

4. **Log file location**: Writes to `logs/trading_bot.log` (relative to working directory) with 5 MB rotation and 3 backups.

5. **Integration test orders**: The LIMIT integration test places an order far from market price (`$9,999,999`) so it rests without filling. Cancel open testnet orders manually if needed.
