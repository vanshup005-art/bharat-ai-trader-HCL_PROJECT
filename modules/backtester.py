"""
Automated Algorithmic Strategy Backtesting Engine.
Calculates risk-adjusted metrics, trade logs, and equity curves
with beginner-friendly performance explanations.
"""
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd

from config.settings import DEFAULT_RISK_FREE_RATE, DEFAULT_BROKERAGE_PCT


def run_backtest(
    df: pd.DataFrame,
    strategy_name: str,
    initial_capital: float = 100000.0,
    fee_pct: float = DEFAULT_BROKERAGE_PCT,
    stop_loss_pct: float = 0.0,
    take_profit_pct: float = 0.0,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    **strategy_params
) -> Dict[str, Any]:
    """
    Execute backtest simulation on historical OHLCV data.
    """
    initial_capital = max(float(initial_capital), 1000.0)
    data = df.copy().reset_index(drop=True)
    n = len(data)
    if n < 30:
        return {"error": "Insufficient historical data points (minimum 30 trading bars required)."}

    # Generate signals: 1 for Long Position, 0 for Flat/Cash
    signals = np.zeros(n)

    if strategy_name == "SMA Crossover":
        fast = int(strategy_params.get("fast_ma", 20))
        slow = int(strategy_params.get("slow_ma", 50))
        fast_series = data["Close"].rolling(window=fast, min_periods=1).mean()
        slow_series = data["Close"].rolling(window=slow, min_periods=1).mean()
        signals = np.where(fast_series > slow_series, 1, 0)

    elif strategy_name == "RSI Mean Reversion":
        oversold = float(strategy_params.get("oversold", 30))
        overbought = float(strategy_params.get("overbought", 70))
        rsi = data["RSI"].values
        in_pos = False
        for i in range(1, n):
            if not in_pos and rsi[i] < oversold:
                in_pos = True
            elif in_pos and rsi[i] > overbought:
                in_pos = False
            signals[i] = 1 if in_pos else 0

    elif strategy_name == "MACD Momentum":
        macd = data["MACD"].values
        signal = data["MACD_Signal"].values
        signals = np.where(macd > signal, 1, 0)

    elif strategy_name == "Bollinger Bands Bounce":
        close = data["Close"].values
        lower = data["BB_Lower"].values
        upper = data["BB_Upper"].values
        in_pos = False
        for i in range(1, n):
            if not in_pos and close[i] <= lower[i]:
                in_pos = True
            elif in_pos and close[i] >= upper[i]:
                in_pos = False
            signals[i] = 1 if in_pos else 0

    elif strategy_name == "AI Quantitative Ensemble":
        # Combo: Close > SMA50 AND RSI between 35 and 68 AND MACD > Signal
        c1 = data["Close"] > data["SMA_50"]
        c2 = (data["RSI"] >= 35) & (data["RSI"] <= 68)
        c3 = data["MACD"] > data["MACD_Signal"]
        signals = np.where(c1 & c2 & c3, 1, 0)
    else:
        signals = np.ones(n)

    # Shift signals by 1 bar to prevent lookahead bias (trade executes next day)
    signals = np.roll(signals, 1)
    signals[0] = 0

    cash = initial_capital
    position = 0.0  # units of shares
    entry_price = 0.0
    entry_date = None
    trades = []
    equity_curve = []

    dates = data["Date"].values if "Date" in data.columns else data.index.values
    prices = data["Close"].values

    for i in range(n):
        curr_price = float(prices[i])
        curr_date = dates[i]
        target_signal = signals[i]

        # Stop Loss / Take Profit check
        if position > 0 and (stop_loss_pct > 0 or take_profit_pct > 0):
            pnl_pct = (curr_price - entry_price) / (entry_price + 1e-9)
            if stop_loss_pct > 0 and pnl_pct <= -stop_loss_pct:
                target_signal = 0
            elif take_profit_pct > 0 and pnl_pct >= take_profit_pct:
                target_signal = 0

        # Execution logic
        # Buy Signal (Cash -> Long)
        if target_signal == 1 and position == 0:
            trade_cost = cash * (1 - fee_pct)
            shares = trade_cost / curr_price
            position = shares
            cash = 0.0
            entry_price = curr_price
            entry_date = curr_date

        # Sell Signal (Long -> Cash)
        elif target_signal == 0 and position > 0:
            proceeds = position * curr_price * (1 - fee_pct)
            trade_pnl = proceeds - (position * entry_price)
            trade_return = (curr_price - entry_price) / (entry_price + 1e-9)

            trades.append({
                "Entry Date": str(pd.to_datetime(entry_date).date()),
                "Exit Date": str(pd.to_datetime(curr_date).date()),
                "Entry Price (₹)": round(entry_price, 2),
                "Exit Price (₹)": round(curr_price, 2),
                "Shares": round(position, 2),
                "P&L (₹)": round(trade_pnl, 2),
                "Return (%)": round(trade_return * 100, 2),
                "Win": trade_pnl > 0
            })
            cash = proceeds
            position = 0.0
            entry_price = 0.0
            entry_date = None

        current_equity = cash + (position * curr_price)
        equity_curve.append(current_equity)

    final_equity = equity_curve[-1]
    total_return_pct = ((final_equity - initial_capital) / initial_capital) * 100

    # Benchmark (Buy and Hold)
    benchmark_return_pct = ((prices[-1] - prices[0]) / (prices[0] + 1e-9)) * 100
    benchmark_curve = initial_capital * (prices / prices[0])

    # Convert equity curve to series for metrics
    eq_series = pd.Series(equity_curve)
    daily_returns = eq_series.pct_change().fillna(0)

    # Days & CAGR
    total_days = max(1, (pd.to_datetime(dates[-1]) - pd.to_datetime(dates[0])).days)
    years = total_days / 365.25
    cagr = (((final_equity / initial_capital) ** (1 / max(years, 0.1))) - 1) * 100 if final_equity > 0 else -100

    # Sharpe Ratio
    rf_daily = risk_free_rate / 252
    excess_returns = daily_returns - rf_daily
    sharpe = np.sqrt(252) * (excess_returns.mean() / (daily_returns.std() + 1e-9))

    # Sortino Ratio
    downside_returns = daily_returns[daily_returns < 0]
    downside_std = downside_returns.std() if len(downside_returns) > 0 else 1e-9
    sortino = np.sqrt(252) * (excess_returns.mean() / (downside_std + 1e-9))

    # Maximum Drawdown
    rolling_max = eq_series.cummax()
    drawdown = (eq_series - rolling_max) / rolling_max
    max_drawdown_pct = abs(float(drawdown.min())) * 100

    # Trade stats
    num_trades = len(trades)
    winning_trades = [t for t in trades if t["Win"]]
    win_rate = (len(winning_trades) / num_trades * 100) if num_trades > 0 else 0.0

    gross_profits = sum(t["P&L (₹)"] for t in winning_trades)
    gross_losses = abs(sum(t["P&L (₹)"] for t in trades if not t["Win"]))
    profit_factor = (gross_profits / (gross_losses + 1e-9)) if gross_losses > 0 else (gross_profits if gross_profits > 0 else 1.0)

    return {
        "strategy": strategy_name,
        "initial_capital": initial_capital,
        "final_capital": round(final_equity, 2),
        "net_profit": round(final_equity - initial_capital, 2),
        "total_return_pct": round(total_return_pct, 2),
        "benchmark_return_pct": round(benchmark_return_pct, 2),
        "cagr_pct": round(cagr, 2),
        "sharpe_ratio": round(sharpe, 2),
        "sortino_ratio": round(sortino, 2),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
        "win_rate_pct": round(win_rate, 1),
        "total_trades": num_trades,
        "profit_factor": round(profit_factor, 2),
        "trades": trades,
        "equity_curve": equity_curve,
        "benchmark_curve": benchmark_curve.tolist(),
        "dates": [str(pd.to_datetime(d).date()) for d in dates]
    }
