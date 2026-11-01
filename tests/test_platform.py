"""
Comprehensive Automated Test Suite for BharatAI Trader.
Validates security sanitizers, data loaders, ML forecaster,
backtesting calculations, paper trading, and portfolio optimization.
"""
import sys
import os
import unittest
import numpy as np
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.security import (
    sanitize_ticker, validate_order_params, atomic_write_json, safe_read_json, mask_api_key
)
from config.stocks import STOCK_SECTORS, ALL_STOCKS_MAP, get_stock_name
from config.settings import DEFAULT_INITIAL_PAPER_CAPITAL
from modules.data_loader import (
    generate_synthetic_stock_data, compute_technical_indicators, fetch_watchlist_summary
)
from modules.ai_assistant import generate_stock_ai_brief, generate_heuristic_sentiment
from modules.ml_forecaster import train_and_forecast_trend, detect_market_anomalies
from modules.backtester import run_backtest
from modules.paper_trader import (
    reset_paper_portfolio, execute_paper_order, get_portfolio_summary, load_paper_portfolio
)
from modules.portfolio_optimizer import (
    portfolio_performance, optimize_portfolio, generate_robo_advice
)
from modules.educational import TRADING_GLOSSARY, RISK_MANAGEMENT_GOLDEN_RULES


class TestBharatAITrader(unittest.TestCase):

    def test_security_sanitization(self):
        """Verify ticker sanitization rejects malicious characters and adds suffixes."""
        # Valid tickers
        ok, res = sanitize_ticker("hcltech")
        self.assertTrue(ok)
        self.assertEqual(res, "HCLTECH.NS")

        ok, res = sanitize_ticker("^NSEI")
        self.assertTrue(ok)
        self.assertEqual(res, "^NSEI")

        # Invalid / Malicious inputs
        ok, res = sanitize_ticker("HCL; rm -rf /")
        self.assertFalse(ok)

        ok, res = sanitize_ticker("<script>alert(1)</script>")
        self.assertFalse(ok)

        ok, res = sanitize_ticker("../../etc/passwd")
        self.assertFalse(ok)

        ok, res = sanitize_ticker("")
        self.assertFalse(ok)

    def test_security_order_validation(self):
        """Verify paper trading order validation catches negative, zero, and overflow values."""
        # Valid BUY
        ok, _ = validate_order_params("BUY", 10, 1500.0, cash_balance=50000.0)
        self.assertTrue(ok)

        # Invalid: Negative shares
        ok, _ = validate_order_params("BUY", -5, 1500.0, cash_balance=50000.0)
        self.assertFalse(ok)

        # Invalid: Insufficient funds
        ok, _ = validate_order_params("BUY", 100, 1500.0, cash_balance=5000.0)
        self.assertFalse(ok)

        # Invalid: Insufficient shares for SELL
        ok, _ = validate_order_params("SELL", 50, 1500.0, cash_balance=5000.0, current_shares=10)
        self.assertFalse(ok)

        # Invalid: Non-finite price
        ok, _ = validate_order_params("BUY", 10, float("nan"), cash_balance=50000.0)
        self.assertFalse(ok)

    def test_stock_universe(self):
        """Verify stock universe contains IT Leaders including HCL Tech."""
        self.assertIn("IT & Technology (Featured)", STOCK_SECTORS)
        self.assertIn("HCLTECH.NS", STOCK_SECTORS["IT & Technology (Featured)"])
        self.assertEqual(get_stock_name("HCLTECH.NS"), "HCL Technologies Ltd")
        self.assertGreater(len(ALL_STOCKS_MAP), 30)

    def test_data_loader_and_indicators(self):
        """Verify synthetic data generator and technical indicators calculations."""
        df, info = generate_synthetic_stock_data("HCLTECH.NS", period="1y")
        self.assertFalse(df.empty)
        self.assertGreaterEqual(len(df), 200)
        self.assertEqual(info["name"], "HCL Technologies Ltd")

        # Verify indicators exist
        for col in ["SMA_20", "SMA_50", "SMA_200", "RSI", "MACD", "MACD_Signal", "BB_Upper", "BB_Lower", "ATR", "VWAP", "Stoch_K"]:
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].isna().all())

    def test_ml_forecaster(self):
        """Verify Random Forest directional classifier and Isolation Forest anomaly radar."""
        df, _ = generate_synthetic_stock_data("TCS.NS", period="1y")
        fc = train_and_forecast_trend(df, horizon="1D")
        self.assertNotIn("error", fc)
        self.assertIn("prob_up", fc)
        self.assertIn("prob_down", fc)
        self.assertAlmostEqual(fc["prob_up"] + fc["prob_down"], 100.0, delta=0.5)

        anom_df = detect_market_anomalies(df)
        self.assertIn("Is_Anomaly", anom_df.columns)
        self.assertIn("Anomaly_Type", anom_df.columns)

    def test_strategy_backtester(self):
        """Verify algorithmic strategy backtesting engine."""
        df, _ = generate_synthetic_stock_data("RELIANCE.NS", period="1y")
        res = run_backtest(
            df,
            strategy_name="SMA Crossover",
            initial_capital=100000.0,
            fast_ma=10,
            slow_ma=30,
            stop_loss_pct=0.03,
            take_profit_pct=0.08
        )
        self.assertNotIn("error", res)
        self.assertIn("total_return_pct", res)
        self.assertIn("sharpe_ratio", res)
        self.assertIn("max_drawdown_pct", res)
        self.assertEqual(len(res["equity_curve"]), len(df))

    def test_paper_trading_simulator(self):
        """Verify paper trading wallet, buy/sell flow, and atomic persistence."""
        reset_paper_portfolio(DEFAULT_INITIAL_PAPER_CAPITAL)
        port = load_paper_portfolio()
        self.assertEqual(port["cash_balance"], DEFAULT_INITIAL_PAPER_CAPITAL)

        # BUY 10 HCLTECH @ ₹1800
        ok, msg = execute_paper_order("HCLTECH.NS", "BUY", 10, 1800.0)
        self.assertTrue(ok)

        summary = get_portfolio_summary({"HCLTECH.NS": 1850.0})
        self.assertEqual(summary["cash_balance"], DEFAULT_INITIAL_PAPER_CAPITAL - 18000.0)
        self.assertEqual(summary["holdings_value"], 18500.0)
        self.assertEqual(summary["unrealized_pnl"], 500.0)

        # SELL 10 HCLTECH @ ₹1850
        ok, msg = execute_paper_order("HCLTECH.NS", "SELL", 10, 1850.0)
        self.assertTrue(ok)
        port_after = load_paper_portfolio()
        self.assertNotIn("HCLTECH.NS", port_after["holdings"])
        self.assertEqual(port_after["realized_pnl"], 500.0)

    def test_portfolio_optimizer_mpt(self):
        """Verify Modern Portfolio Theory (MPT) and Robo-Advisory."""
        tickers = ["HCLTECH.NS", "TCS.NS", "INFY.NS", "RELIANCE.NS"]
        opt_res = optimize_portfolio(tickers, period="1y", force_synthetic=True)
        self.assertNotIn("error", opt_res)
        self.assertIn("max_sharpe", opt_res)
        self.assertIn("min_volatility", opt_res)

        advice = generate_robo_advice(opt_res, "Moderate (Balanced)")
        self.assertIn("AI Robo-Advisor Allocation Blueprint", advice)

    def test_educational_module(self):
        """Verify trading glossary and risk management golden rules."""
        self.assertGreaterEqual(len(TRADING_GLOSSARY), 8)
        self.assertIn("RSI (Relative Strength Index)", TRADING_GLOSSARY)
        self.assertGreaterEqual(len(RISK_MANAGEMENT_GOLDEN_RULES), 4)


if __name__ == "__main__":
    unittest.main()
