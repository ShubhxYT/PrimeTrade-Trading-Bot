# Binance Futures Testnet Trading Bot

A production-ready Python CLI application for placing **MARKET**, **LIMIT**, and **STOP-LIMIT** orders on Binance USDT-M Futures Testnet. Features structured logging, comprehensive error handling, full test coverage, and an optional Streamlit UI.

**Submission for**: PrimeTrade Python Developer Intern Assignment

---

## 🎯 Features

- ✅ **Market Orders** — Execute immediate orders at best available price
- ✅ **Limit Orders** — Set custom fill price with configurable time-in-force (GTC, IOC, FOK)
- ✅ **Stop-Limit Orders** — Trigger orders at specified stop price (Bonus feature)
- ✅ **Comprehensive Validation** — Input validation, price sanity checks, error recovery
- ✅ **Structured Logging** — File rotation, multiple log levels, API request/response tracking
- ✅ **Full Test Suite** — Unit tests + integration tests with mock API
- ✅ **Clean Architecture** — Separated concerns (client, orders, validators, CLI)
- ✅ **Streamlit UI** (Bonus) — Web-based dashboard for order placement and monitoring

---

## 📋 Prerequisites

- **Python 3.10+** (tested on 3.10, 3.11, 3.12)
- **Binance Testnet Account** (free, created at [https://testnet.binancefuture.com](https://testnet.binancefuture.com))
- **API Credentials** (generate from account settings on testnet)

---

## 🚀 Quick Start

### 1. Install

```bash
# Clone the repository
git clone <repo-url>
cd trading_bot

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate           # macOS/Linux
# OR
.venv\Scripts\activate              # Windows

# Install in editable mode with dependencies
pip install -e .
```

### 2. Configure Credentials

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` with your testnet API credentials:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
BINANCE_BASE_URL=https://testnet.binancefuture.com
```

**Get testnet credentials:**
1. Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Sign up or log in
3. Navigate to **API Management** → **Create New Key**
4. Copy **API Key** and **Secret Key** to `.env`

### 3. Verify Installation

```bash
trading-bot --help
```

You should see the CLI help menu. Ready to place orders!

---

## 📖 Usage

### Command Format

```bash
trading-bot SYMBOL SIDE ORDER_TYPE QUANTITY [OPTIONS]
```

**Arguments:**
- `SYMBOL`: Trading pair (e.g., `BTCUSDT`, `ETHUSDT`)
- `SIDE`: `BUY` or `SELL`
- `ORDER_TYPE`: `MARKET`, `LIMIT`, or `STOP_LIMIT`
- `QUANTITY`: Order size (must be positive)

**Options:**
- `--price FLOAT`: Limit price (required for LIMIT and STOP_LIMIT)
- `--stop-price FLOAT`: Trigger price (required for STOP_LIMIT)
- `--time-in-force {GTC,IOC,FOK}`: Order duration (default: GTC)
- `--log-level {DEBUG,INFO,WARNING,ERROR}`: Logging verbosity (default: INFO)

### Examples

#### Market Order (Buy 0.001 BTC immediately)
```bash
trading-bot BTCUSDT BUY MARKET 0.001
```

**Output:**
```
═══════════════════════════════════════════════════════════════
  ORDER PLACED SUCCESSFULLY
═══════════════════════════════════════════════════════════════
Order ID:        12345678
Status:          FILLED
Symbol:          BTCUSDT
Side:            BUY
Type:            MARKET
Quantity:        0.001
Executed Qty:    0.001
Average Price:   42500.00 USDT
═══════════════════════════════════════════════════════════════
```

#### Limit Order (Sell 0.001 BTC at $99,999)
```bash
trading-bot BTCUSDT SELL LIMIT 0.001 --price 99999
```

#### Stop-Limit Order (Buy 0.001 BTC when price hits $30,500, fill at $31,000)
```bash
trading-bot BTCUSDT BUY STOP_LIMIT 0.001 --price 31000 --stop-price 30500
```

#### IOC (Immediate-or-Cancel) Limit Order
```bash
trading-bot BTCUSDT BUY LIMIT 0.001 --price 42000 --time-in-force IOC
```

#### With Debug Logging
```bash
trading-bot BTCUSDT BUY MARKET 0.001 --log-level DEBUG
```

#### Alternative (Direct Python module, no pip install needed)
```bash
python -m bot.cli BTCUSDT BUY MARKET 0.001
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest -v
```

### Unit Tests Only (No credentials required)
```bash
pytest tests/unit/ -v
```

### Integration Tests (Requires valid .env)
```bash
pytest tests/integration/ -v
```

### Test Coverage
```bash
pytest --cov=bot tests/
```

**Test Files:**
- `tests/unit/test_cli.py` — CLI argument parsing and formatting
- `tests/unit/test_orders.py` — Order validation and construction
- `tests/unit/test_validators.py` — Input validation logic
- `tests/integration/test_integration.py` — Full order lifecycle with Binance API

---

## 📁 Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── cli.py                 # CLI entry point (Typer)
│   ├── client.py              # Binance API wrapper
│   ├── orders.py              # Order service & construction logic
│   ├── validators.py          # Input validation, Enums (OrderSide, OrderType, etc.)
│   └── logging_config.py      # Logging setup with file rotation
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── unit/
│   │   ├── test_cli.py
│   │   ├── test_orders.py
│   │   └── test_validators.py
│   └── integration/
│       └── test_integration.py
├── logs/                      # Auto-created; stores trading_bot.log
├── pyproject.toml             # Project metadata & dependencies
├── requirements.txt           # Pinned versions for reproducibility
├── .env.example               # Template for environment variables
├── .gitignore                 # Excludes .env, venv/, logs/, etc.
└── README.md                  # This file
```

---

## 🔧 Architecture

### Client Layer (`client.py`)
- Wraps `python-binance` connector
- Handles API authentication
- Manages request/response lifecycle
- Propagates Binance API errors

### Order Service (`orders.py`)
- Constructs validated order payloads
- Applies business logic (e.g., price formatting for LIMIT orders)
- Places orders via client
- Formats responses for display

### Validators (`validators.py`)
- Enum definitions: `OrderSide`, `OrderType`, `TimeInForce`
- Input validation: quantity > 0, STOP_LIMIT requires both prices
- Type coercion and error messages

### CLI (`cli.py`)
- Typer-based argument parsing
- Pretty-prints order summaries and responses
- Manages logging setup per invocation
- Error handling and user feedback

### Logging (`logging_config.py`)
- File-based logging with 5 MB rotation (3 backups)
- Structured logs with timestamps, levels, module names
- Sensitive data redaction (API keys, secrets not logged)

---

## 📊 Logging Output

Logs are written to `logs/trading_bot.log`. Example:

```
2025-01-15 10:23:45,123 | INFO     | bot.client | Placing MARKET order: BTCUSDT BUY 0.001
2025-01-15 10:23:45,234 | DEBUG    | bot.client | Request payload: {...}
2025-01-15 10:23:46,567 | INFO     | bot.client | Order filled: 12345678, Qty=0.001, AvgPrice=42500
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Required | Default | Example |
|----------|----------|---------|---------|
| `BINANCE_API_KEY` | Yes | — | `your_key_here` |
| `BINANCE_API_SECRET` | Yes | — | `your_secret_here` |
| `BINANCE_BASE_URL` | No | `https://testnet.binancefuture.com` | `https://demo-fapi.binance.com` |

**Note:** The official testnet endpoint changed — both URLs are supported for compatibility.

---

## 🎓 Key Assumptions

1. **Quantity Precision**  
   - Bot validates `quantity > 0` but does NOT fetch per-symbol LOT_SIZE filters
   - Use ≤3 decimal places for BTCUSDT (e.g., `0.001`)
   - Binance will reject invalid precision with a clear error

2. **STOP_LIMIT Implementation**  
   - USDT-M Futures uses `type="STOP"` with `price` (limit) + `stopPrice` (trigger)
   - This differs from COIN-M Futures; orders will fail if precision is wrong
   - See Binance docs: [Futures Order Types](https://binance-docs.github.io/apidocs/futures/en/#new-order-trade)

3. **Testnet Base URL**  
   - Primary: `https://testnet.binancefuture.com`
   - Legacy: `https://demo-fapi.binance.com` (still functional)
   - Override via `BINANCE_BASE_URL` in `.env`

4. **Log Storage**  
   - Logs stored in `logs/trading_bot.log` (relative to working directory)
   - Rotates at 5 MB with 3 backups kept
   - Create `logs/` directory manually if needed

5. **Integration Test Orders**  
   - LIMIT test places order far from market (`$9,999,999`) so it rests without filling
   - Clean up testnet orders manually via Binance UI if needed
   - No funds deducted for resting orders on testnet

6. **Error Handling**  
   - Network errors → Logged and re-raised with context
   - Invalid input → Caught before API call, clear validation message
   - Binance API errors → Parsed and displayed to user

---

## 🎁 Bonus Features Implemented

### ✨ Stop-Limit Orders
- Full support for conditional orders with trigger + limit price
- Properly constructs USDT-M Futures `type="STOP"` payload
- Example: `trading-bot BTCUSDT BUY STOP_LIMIT 0.001 --price 31000 --stop-price 30500`

### ✨ Configurable Time-in-Force
- **GTC** (Good-Till-Cancel, default) — Order stays open until filled or canceled
- **IOC** (Immediate-or-Cancel) — Fills or cancels immediately
- **FOK** (Fill-or-Kill) — All-or-nothing, cancels if full qty unavailable
- Example: `trading-bot BTCUSDT BUY LIMIT 0.001 --price 42000 --time-in-force IOC`

### ✨ Streamlit Web UI (Optional)
Interactive web dashboard for order placement:

```bash
pip install -e ".[ui]"                    # Install UI dependencies
streamlit run streamlit_app/app.py
```

Features:
- Real-time order form with validation
- Order history display
- Price charts and market data
- One-click order placement

---

## 🐛 Troubleshooting

### `ModuleNotFoundError: No module named 'bot'`
```bash
pip install -e .
```

### `BINANCE_API_KEY not found`
```bash
# Ensure .env exists in working directory
cp .env.example .env
# Fill in your testnet API key and secret
```

### `APIError: Unauthorized — invalid key, IP, or permissions`
- Verify API key/secret are copied correctly (no extra spaces)
- Check IP whitelist on Binance (testnet may allow all IPs)
- Generate a new key pair and try again

### `decimal precision is over the maximum: 8`
- Reduce decimal places in `--price` or `QUANTITY`
- Example: `0.001` instead of `0.00000001`

### Order stuck in logs but not placed
- Check `.env` file is correctly set
- Enable debug logging: `--log-level DEBUG`
- Verify testnet account has USDT balance

---

## 📝 Sample Log Files

See `logs/trading_bot.log` for:
- ✅ One MARKET order (sample included in repo)
- ✅ One LIMIT order (sample included in repo)
- ✅ Full request/response traces
- ✅ Validation failures
- ✅ Error handling examples

---

## 📚 Resources

- **Binance Futures API Docs**: [https://binance-docs.github.io/apidocs/futures/](https://binance-docs.github.io/apidocs/futures/)
- **Testnet**: [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
- **python-binance**: [https://github.com/binance/binance-connector-python](https://github.com/binance/binance-connector-python)
- **Typer CLI**: [https://typer.tiangolo.com](https://typer.tiangolo.com)

---

## 📜 License

This project is submitted as part of the PrimeTrade Python Developer Intern assignment. Use for educational and evaluation purposes.

---

## ✉️ Questions?

For issues or clarifications, please refer to the assignment requirements or contact the PrimeTrade hiring team.

**Last Updated**: April 2025
