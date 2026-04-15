# ── Trading Bot — root Makefile ───────────────────────────────────────────────
# Usage: make <target>
# Default target: help

.DEFAULT_GOAL := help
.PHONY: help install install-ui install-dev test test-integration test-all \
        lint format run ui clean

help: ## Print all available targets with descriptions
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the trading bot package in editable mode
	cd trading_bot && pip install -e .

install-ui: ## Install Streamlit UI dependencies
	pip install "streamlit>=1.35.0" "pandas>=2.0.0" "plotly>=5.0.0" "streamlit-autorefresh>=1.0.0"

install-dev: install ## Install dev tools: pytest and ruff
	pip install pytest ruff

test: ## Run unit tests (no credentials needed)
	cd trading_bot && pytest tests/unit/ -v

test-integration: ## Run integration tests (requires .env with Binance credentials)
	cd trading_bot && pytest -m integration -v

test-all: ## Run all tests
	cd trading_bot && pytest -v

lint: ## Lint source code with ruff
	cd trading_bot && ruff check bot/ tests/

format: ## Auto-format source code with ruff
	cd trading_bot && ruff format bot/ tests/

run: ## Show trading bot CLI help
	cd trading_bot && trading-bot --help

ui: ## Launch the Streamlit dashboard on http://localhost:8501
	streamlit run streamlit_app/app.py

clean: ## Remove __pycache__, .pytest_cache, *.egg-info, and empty log files
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find trading_bot/logs -maxdepth 1 -name "*.log" -size 0 -delete 2>/dev/null || true
	@echo "Clean complete."
