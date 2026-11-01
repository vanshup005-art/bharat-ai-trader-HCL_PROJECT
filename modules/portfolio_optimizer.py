"""
Portfolio Optimization & AI Robo-Advisory Module.
Implements Modern Portfolio Theory (MPT), Markowitz Efficient Frontier,
Maximum Sharpe & Minimum Volatility optimization via SciPy.
"""
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import yfinance as yf
import streamlit as st

from config.settings import DEFAULT_RISK_FREE_RATE, CACHE_TTL_SECONDS
from utils.logger import get_logger

logger = get_logger()


def fetch_multi_asset_data(tickers: List[str], period: str = "1y", force_synthetic: bool = False) -> pd.DataFrame:
    """Download daily adjusted close prices for multiple Indian tickers with synthetic fallback."""
    valid_tickers = [t.strip().upper() for t in tickers if t.strip()]
    if not valid_tickers:
        return pd.DataFrame()

    if not force_synthetic:
        try:
            data = yf.download(valid_tickers, period=period, auto_adjust=True, progress=False)
            if "Close" in data.columns:
                df_close = data["Close"]
            else:
                df_close = data

            if isinstance(df_close, pd.Series):
                df_close = df_close.to_frame(name=valid_tickers[0])

            df_close = df_close.dropna(how="all").ffill().bfill()
            if not df_close.empty and len(df_close.columns) >= 2:
                return df_close
        except Exception as e:
            logger.warning(f"Multi-asset yfinance download failed: {e}. Generating correlated synthetic prices.")

    # Synthetic realistic correlated prices for offline/demo mode
    days = 252
    dates = pd.date_range(end=pd.Timestamp.now().normalize(), periods=days, freq="B")
    mock_dict = {}
    np.random.seed(42)

    # Base common market factor
    market_factor = np.random.normal(0.0004, 0.012, days)

    for t in valid_tickers:
        beta = np.random.uniform(0.7, 1.4)
        idio_vol = np.random.uniform(0.008, 0.016)
        idio_ret = np.random.normal(0.0001, idio_vol, days)
        total_daily_ret = (beta * market_factor) + idio_ret

        base = 1820.0 if "HCL" in t else (4000.0 if "TCS" in t else (2750.0 if "RELIANCE" in t else 1500.0))
        mock_dict[t] = base * np.exp(np.cumsum(total_daily_ret))

    return pd.DataFrame(mock_dict, index=dates)


def portfolio_performance(weights: np.ndarray, mean_returns: np.ndarray, cov_matrix: np.ndarray, rf: float = DEFAULT_RISK_FREE_RATE):
    """Calculate annualized return, volatility, and Sharpe ratio for given asset weights."""
    returns = np.sum(mean_returns * weights) * 252
    volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
    sharpe = (returns - rf) / (volatility + 1e-9)
    return returns, volatility, sharpe


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def optimize_portfolio(
    tickers: List[str],
    period: str = "1y",
    num_portfolios: int = 2500,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    force_synthetic: bool = False
) -> Dict[str, Any]:
    """
    Run Modern Portfolio Theory (MPT) optimization and Monte Carlo simulation.
    """
    df_close = fetch_multi_asset_data(tickers, period=period, force_synthetic=force_synthetic)
    if df_close.empty or len(df_close.columns) < 2:
        return {"error": "At least 2 valid stocks with historical price data are required for portfolio diversification."}

    valid_cols = list(df_close.columns)
    returns_df = df_close.pct_change().dropna()
    mean_returns = returns_df.mean().values
    cov_matrix = returns_df.cov().values
    num_assets = len(valid_cols)

    # 1. Monte Carlo Simulation for visual efficient frontier
    sim_returns = []
    sim_volatilities = []
    sim_sharpes = []

    np.random.seed(101)
    for _ in range(num_portfolios):
        w = np.random.random(num_assets)
        w /= np.sum(w)
        ret, vol, sh = portfolio_performance(w, mean_returns, cov_matrix, risk_free_rate)
        sim_returns.append(ret)
        sim_volatilities.append(vol)
        sim_sharpes.append(sh)

    # 2. Precise Numerical Optimization (SciPy SLSQP)
    # Target 1: Maximize Sharpe Ratio
    def neg_sharpe(weights):
        return -portfolio_performance(weights, mean_returns, cov_matrix, risk_free_rate)[2]

    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0})
    bounds = tuple((0.0, 1.0) for _ in range(num_assets))
    init_guess = num_assets * [1.0 / num_assets]

    opt_sharpe = minimize(neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    max_sharpe_weights = opt_sharpe.x if opt_sharpe.success else init_guess
    ms_ret, ms_vol, ms_sharpe = portfolio_performance(max_sharpe_weights, mean_returns, cov_matrix, risk_free_rate)

    # Target 2: Minimum Volatility
    def min_vol(weights):
        return portfolio_performance(weights, mean_returns, cov_matrix, risk_free_rate)[1]

    opt_vol = minimize(min_vol, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    min_vol_weights = opt_vol.x if opt_vol.success else init_guess
    mv_ret, mv_vol, mv_sharpe = portfolio_performance(min_vol_weights, mean_returns, cov_matrix, risk_free_rate)

    # Target 3: Equal Weighted
    eq_weights = np.array([1.0 / num_assets] * num_assets)
    eq_ret, eq_vol, eq_sharpe = portfolio_performance(eq_weights, mean_returns, cov_matrix, risk_free_rate)

    # Format allocations
    max_sharpe_alloc = {col: round(float(w) * 100, 1) for col, w in zip(valid_cols, max_sharpe_weights)}
    min_vol_alloc = {col: round(float(w) * 100, 1) for col, w in zip(valid_cols, min_vol_weights)}
    equal_alloc = {col: round(float(w) * 100, 1) for col, w in zip(valid_cols, eq_weights)}

    # Correlation Matrix
    corr_matrix = returns_df.corr().round(2).to_dict()

    return {
        "tickers": valid_cols,
        "max_sharpe": {
            "expected_return": round(float(ms_ret) * 100, 2),
            "volatility": round(float(ms_vol) * 100, 2),
            "sharpe_ratio": round(float(ms_sharpe), 2),
            "weights": max_sharpe_alloc
        },
        "min_volatility": {
            "expected_return": round(float(mv_ret) * 100, 2),
            "volatility": round(float(mv_vol) * 100, 2),
            "sharpe_ratio": round(float(mv_sharpe), 2),
            "weights": min_vol_alloc
        },
        "equal_weight": {
            "expected_return": round(float(eq_ret) * 100, 2),
            "volatility": round(float(eq_vol) * 100, 2),
            "sharpe_ratio": round(float(eq_sharpe), 2),
            "weights": equal_alloc
        },
        "simulation": {
            "returns": [round(float(r) * 100, 2) for r in sim_returns[:1500]],
            "volatilities": [round(float(v) * 100, 2) for v in sim_volatilities[:1500]],
            "sharpes": [round(float(s), 2) for s in sim_sharpes[:1500]],
        },
        "correlation_matrix": corr_matrix
    }


def generate_robo_advice(opt_result: Dict[str, Any], risk_profile: str) -> str:
    """Generate automated Robo-Advisor recommendation based on user risk level."""
    if "error" in opt_result:
        return opt_result["error"]

    if risk_profile == "Conservative (Low Risk)":
        target = opt_result["min_volatility"]
        strategy_desc = "Capital Preservation & Volatility Minimization"
        weights = target["weights"]
        eli5_advice = "Your priority is safeguarding capital. The model heavily allocates to low-volatility, defensive bluechips to minimize drawdowns during market corrections."
    elif risk_profile == "Aggressive (High Growth)":
        target = opt_result["max_sharpe"]
        strategy_desc = "Alpha Maximization & Risk-Adjusted Momentum"
        weights = target["weights"]
        eli5_advice = "Your priority is maximizing wealth creation. The model concentrates capital in high-Sharpe growth champions, accepting moderate short-term fluctuations."
    else:  # Moderate (Balanced)
        strategy_desc = "Balanced Growth with Downside Hedging"
        ms_w = opt_result["max_sharpe"]["weights"]
        mv_w = opt_result["min_volatility"]["weights"]
        weights = {k: round((ms_w[k] + mv_w[k]) / 2, 1) for k in ms_w}
        target = {
            "expected_return": round((opt_result["max_sharpe"]["expected_return"] + opt_result["min_volatility"]["expected_return"]) / 2, 2),
            "volatility": round((opt_result["max_sharpe"]["volatility"] + opt_result["min_volatility"]["volatility"]) / 2, 2),
            "sharpe_ratio": round((opt_result["max_sharpe"]["sharpe_ratio"] + opt_result["min_volatility"]["sharpe_ratio"]) / 2, 2)
        }
        eli5_advice = "A golden-middle allocation: combines steady dividend compounding bluechips with momentum leaders to offer smooth capital appreciation."

    top_holdings = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    top_3_str = ", ".join([f"**{t}** ({w}%)" for t, w in top_holdings if w > 5][:4])

    return f"""### 🤖 AI Robo-Advisor Allocation Blueprint: `{risk_profile}`

**Mandate:** {strategy_desc}

- **💡 Beginner Summary (ELI5):** {eli5_advice}
- **Target Annual Expected Return:** **{target['expected_return']}%**
- **Expected Annual Volatility (Risk):** **{target['volatility']}%**
- **Optimal Sharpe Ratio:** **{target['sharpe_ratio']}**
- **Core Anchor Holdings:** {top_3_str}

#### 📋 Execution & Rebalancing Protocol
1. **Quarterly Review:** Rebalance portfolio weights if any asset drifts by more than ±5% from its model target.
2. **Liquid Cash Buffer:** Keep 5% to 10% in liquid overnight funds for opportunistic deployment during NIFTY pullbacks.
3. **Correlation Vigilance:** Ensure assets maintain low correlation (< 0.6) to guarantee true portfolio diversification benefits.
"""
