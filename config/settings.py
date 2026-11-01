"""
Global Application Configuration & Settings.
Centralizes app parameters, API model definitions, risk thresholds, and theme styling.
"""
import os
from typing import Dict, List

# Application Meta
APP_TITLE = "BharatAI Trader | AI-Powered Indian Equities Platform"
APP_SUBTITLE = "Institutional-Grade Quantitative, ML & Generative AI Platform for NSE/BSE"
APP_VERSION = "2.5.0-HCL-Edition"
AUTHOR = "HCL Career Shaper Submission"

# Supported Generative AI Models
SUPPORTED_AI_MODELS: Dict[str, Dict[str, str]] = {
    "Google Gemini": {
        "gemini-2.5-flash": "Gemini 2.5 Flash (Recommended: Ultra-fast, multimodal & precise)",
        "gemini-2.5-pro": "Gemini 2.5 Pro (Deep reasoning & complex macro synthesis)",
        "gemini-1.5-pro": "Gemini 1.5 Pro (Long context & institutional filings analysis)",
        "gemini-1.5-flash": "Gemini 1.5 Flash (Lightweight & high throughput)",
    },
    "OpenAI": {
        "gpt-4o": "GPT-4o (Flagship multimodal intelligence)",
        "gpt-4o-mini": "GPT-4o Mini (Cost-efficient & responsive)",
        "o1-mini": "o1-mini (Reasoning & quantitative logic specialist)",
    },
    "Built-in Quant Engine": {
        "quant-rule-engine": "Algorithmic Quant Heuristics (100% Offline, Zero-Key Required)",
    }
}

# Financial Constants
DEFAULT_INITIAL_PAPER_CAPITAL = 500000.0  # ₹5,00,000 INR
DEFAULT_RISK_FREE_RATE = 0.065           # 6.50% (RBI Benchmark Repo Rate)
DEFAULT_BROKERAGE_PCT = 0.0005           # 0.05% slippage + brokerage
CACHE_TTL_SECONDS = 300                  # 5-minute cache for market data

# UI Styling Palette
THEME_COLORS = {
    "background": "#0B0E14",
    "card_bg": "#151B26",
    "card_border": "#212A3A",
    "text_primary": "#F9FAFB",
    "text_secondary": "#9CA3AF",
    "bull_color": "#10B981",    # Emerald
    "bear_color": "#EF4444",    # Crimson
    "accent_primary": "#38BDF8",# Sky Blue
    "accent_gold": "#F59E0B",   # Amber
    "accent_purple": "#A855F7", # Purple
}

# Educational & Risk Management Presets
STRATEGY_PRESETS = {
    "Beginner Safe (Low Risk)": {
        "strategy": "SMA Crossover",
        "fast_ma": 20,
        "slow_ma": 50,
        "stop_loss_pct": 2.5,
        "take_profit_pct": 6.0,
        "description": "Smooth trend-following that filters out high-frequency noise."
    },
    "Momentum Breakout (Medium Risk)": {
        "strategy": "MACD Momentum",
        "stop_loss_pct": 3.5,
        "take_profit_pct": 9.0,
        "description": "Captures strong velocity moves when momentum accelerates."
    },
    "Mean Reversion Dip Buyer": {
        "strategy": "RSI Mean Reversion",
        "oversold": 28,
        "overbought": 72,
        "stop_loss_pct": 3.0,
        "take_profit_pct": 7.5,
        "description": "Buys oversold pullbacks and takes profit on overbought expansions."
    },
    "Institutional Multi-Factor Ensemble": {
        "strategy": "AI Quantitative Ensemble",
        "stop_loss_pct": 3.0,
        "take_profit_pct": 8.0,
        "description": "Blends Moving Average trend, RSI momentum, and MACD alignment."
    }
}
