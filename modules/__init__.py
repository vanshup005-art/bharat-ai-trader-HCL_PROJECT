"""
BharatAI Trader Core Business Logic Modules.
"""
from .data_loader import (
    fetch_stock_data, fetch_stock_news, fetch_watchlist_summary,
    compute_technical_indicators, generate_synthetic_stock_data
)
from .ai_assistant import generate_stock_ai_brief, generate_heuristic_sentiment
from .ml_forecaster import train_and_forecast_trend, detect_market_anomalies
from .backtester import run_backtest
from .paper_trader import (
    load_paper_portfolio, execute_paper_order,
    reset_paper_portfolio, get_portfolio_summary
)
from .portfolio_optimizer import optimize_portfolio, generate_robo_advice
from .charting import (
    plot_candlestick_chart, plot_anomalies_chart, plot_equity_curve,
    plot_efficient_frontier, plot_allocation_donut, plot_correlation_heatmap
)
from .educational import TRADING_GLOSSARY, RISK_MANAGEMENT_GOLDEN_RULES
