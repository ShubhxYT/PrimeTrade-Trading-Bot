"""
app.py — Trading Bot Streamlit dashboard (read-only).

Run from the repo root:
    streamlit run streamlit_app/app.py

Override the default log path via env var:
    LOG_PATH=/path/to/trading_bot.log streamlit run streamlit_app/app.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Ensure the script's own directory is in sys.path so log_parser is importable
# whether running via `streamlit run streamlit_app/app.py` or `python -m streamlit run ...`
_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from log_parser import parse_log  # noqa: E402

# ── Constants ────────────────────────────────────────────────────────────────

DEFAULT_LOG_PATH = str(
    Path(__file__).parent.parent / "trading_bot" / "logs" / "trading_bot.log"
)

STATUS_ICONS: dict[str, str] = {
    "FILLED": "🟢",
    "NEW": "🔵",
    "PARTIALLY_FILLED": "🟡",
    "CANCELED": "🔴",
    "REJECTED": "🔴",
    "EXPIRED": "⚫",
}

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Trading Bot Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state initialisation ─────────────────────────────────────────────

if "log_path" not in st.session_state:
    st.session_state["log_path"] = os.environ.get("LOG_PATH", DEFAULT_LOG_PATH)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("⚙️ Config")

    log_path_input = st.text_input(
        "Log file path",
        value=st.session_state["log_path"],
        help="Absolute or relative path to trading_bot.log",
    )
    st.session_state["log_path"] = log_path_input

    if st.button("🔄 Reload data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.subheader("🔐 Env Config")
    for _var in ("BINANCE_API_KEY", "BINANCE_API_SECRET", "BINANCE_BASE_URL"):
        _set = bool(os.environ.get(_var))
        st.text(f"{'✅' if _set else '❌'}  {_var}")

    st.divider()
    st.caption("Read-only dashboard — no order placement.")

# ── Cached data loader ────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def load_orders(log_path: str) -> pd.DataFrame:
    """Load and cache parsed orders from the log file (TTL = 30 s)."""
    return parse_log(log_path)

# ── Main tabs ─────────────────────────────────────────────────────────────────

tab_overview, tab_logs = st.tabs(["📊 Overview", "📄 Log Viewer"])

# ── Overview tab ──────────────────────────────────────────────────────────────

with tab_overview:
    st.header("Order History")

    df = load_orders(st.session_state["log_path"])

    if df.empty:
        st.info(
            "No order records found in the log file. "
            "Run the trading bot to populate data, then click **Reload data**."
        )
    else:
        # ── KPI metrics row ───────────────────────────────────────────────────
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Orders", len(df))

        filled_count = int((df["status"] == "FILLED").sum())
        col2.metric("Filled Orders", filled_count)

        avg_exec = df["executedQty"].mean()
        col3.metric(
            "Avg Executed Qty",
            f"{avg_exec:.6f}" if pd.notna(avg_exec) else "—",
        )

        st.divider()

        # ── Order history table ───────────────────────────────────────────────
        display_df = df.copy()

        # Prepend status icon to status text
        display_df["status"] = display_df["status"].apply(
            lambda s: f"{STATUS_ICONS.get(str(s), '⚪')} {s}" if pd.notna(s) else "—"
        )

        # Format timestamp as string for display
        display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

        st.dataframe(
            display_df[
                [
                    "timestamp",
                    "orderId",
                    "symbol",
                    "side",
                    "type",
                    "status",
                    "origQty",
                    "executedQty",
                    "avgPrice",
                    "price",
                ]
            ],
            use_container_width=True,
            hide_index=True,
            column_config={
                "timestamp": st.column_config.TextColumn("Time"),
                "orderId": st.column_config.NumberColumn("Order ID", format="%d"),
                "symbol": st.column_config.TextColumn("Symbol"),
                "side": st.column_config.TextColumn("Side"),
                "type": st.column_config.TextColumn("Type"),
                "status": st.column_config.TextColumn("Status"),
                "origQty": st.column_config.NumberColumn("Orig Qty", format="%.6f"),
                "executedQty": st.column_config.NumberColumn("Exec Qty", format="%.6f"),
                "avgPrice": st.column_config.NumberColumn("Avg Price", format="%.2f"),
                "price": st.column_config.NumberColumn("Limit Price", format="%.2f"),
            },
        )

        st.divider()

        # ── Executed Qty over time line chart ─────────────────────────────────
        st.subheader("Executed Qty Over Time")

        chart_df = df[df["executedQty"] > 0].copy()

        if chart_df.empty:
            st.info("No filled orders to chart yet.")
        else:
            fig = px.line(
                chart_df.sort_values("timestamp"),
                x="timestamp",
                y="executedQty",
                color="symbol",
                markers=True,
                labels={
                    "timestamp": "Time",
                    "executedQty": "Executed Qty",
                    "symbol": "Symbol",
                },
                title="Executed Quantity per Order",
            )
            fig.update_layout(legend_title_text="Symbol", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

# ── Log Viewer tab ────────────────────────────────────────────────────────────

with tab_logs:
    st.header("Log Viewer")

    col_filter, col_toggle = st.columns([3, 1])

    with col_filter:
        level_filter: str = st.selectbox(
            "Filter by level",
            options=["ALL", "INFO", "WARNING", "ERROR"],
            index=0,
            label_visibility="visible",
        )

    with col_toggle:
        auto_refresh: bool = st.toggle("Auto-refresh (5 s)", value=False)

    log_path = Path(st.session_state["log_path"])

    if not log_path.exists():
        st.warning(f"Log file not found: `{log_path}`")
    else:
        with log_path.open(encoding="utf-8", errors="replace") as fh:
            raw_lines = fh.readlines()

        if level_filter == "ALL":
            filtered_lines = raw_lines
        else:
            # Match the padded level format used by logging_config.py e.g. "| INFO     |"
            filtered_lines = [ln for ln in raw_lines if f"| {level_filter}" in ln]

        tail_lines = filtered_lines[-200:]
        tail_text = "".join(tail_lines) if tail_lines else "(no matching log lines)"

        st.text_area(
            label="log_tail",
            value=tail_text,
            height=500,
            disabled=True,
            label_visibility="collapsed",
        )

        st.caption(
            f"Showing {len(tail_lines)} of {len(filtered_lines)} matching lines "
            f"(level: {level_filter}) — total lines in file: {len(raw_lines)}"
        )

    # Auto-refresh: sleep then rerun; the toggle state is preserved in session state
    if auto_refresh:
        time.sleep(5)
        st.rerun()
