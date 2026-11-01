"""
Data loader and technical indicators calculation for Indian Equities.
Supports NSE/BSE tickers via yfinance with caching, synthetic demo mode,
watchlist batch summaries, and extensive indicator calculations.
"""
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st

from config.stocks import STOCK_SECTORS, ALL_STOCKS_MAP, get_stock_name
from config.settings import CACHE_TTL_SECONDS
from utils.security import sanitize_ticker
from utils.logger import get_logger

logger = get_logger()


def generate_synthetic_stock_data(ticker: str, period: str = "1y") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Generate realistic synthetic market data for offline demo mode or network fallbacks."""
    days_map = {"1mo": 30, "3mo": 90, "6mo": 180, "1y": 252, "2y": 504, "5y": 1260}
    n_days = days_map.get(period, 252)
    np.random.seed(abs(hash(ticker)) % (2**32 - 1))

    # Base price based on ticker
    if "HCLTECH" in ticker:
        base_price = 1820.0
    elif "TCS" in ticker:
        base_price = 4050.0
    elif "RELIANCE" in ticker:
        base_price = 2750.0
    elif "HDFC" in ticker:
        base_price = 1740.0
    elif "INFY" in ticker:
        base_price = 1850.0
    elif "^" in ticker:
        base_price = 24200.0 if "NSEI" in ticker else 79400.0
    else:
        base_price = 2200.0

    drift = 0.0004
    vol = 0.015

    returns = np.random.normal(drift, vol, n_days)
    price_series = base_price * np.exp(np.cumsum(returns))
    dates = pd.date_range(end=pd.Timestamp.now().normalize(), periods=n_days, freq="B")

    highs = price_series * (1 + np.abs(np.random.normal(0.005, 0.003, n_days)))
    lows = price_series * (1 - np.abs(np.random.normal(0.005, 0.003, n_days)))
    opens = (highs + lows) / 2 + np.random.normal(0, 3, n_days)
    volumes = np.random.randint(500000, 3500000, size=n_days).astype(float)
    
    # Inject deliberate institutional volume surges for anomaly testing
    burst_indices = np.random.choice(n_days, size=int(n_days * 0.05), replace=False)
    volumes[burst_indices] *= np.random.uniform(2.5, 4.0, size=len(burst_indices))

    df = pd.DataFrame({
        "Date": dates,
        "Open": opens,
        "High": highs,
        "Low": lows,
        "Close": price_series,
        "Volume": volumes
    })
    df = compute_technical_indicators(df)

    company_name = get_stock_name(ticker)
    info = {
        "name": company_name,
        "sector": "Indian Equities (NSE/BSE)",
        "industry": "Constituent Bluechip",
        "currency": "INR",
        "current_price": round(float(price_series[-1]), 2),
        "market_cap": 12500000000000,
        "pe_ratio": round(np.random.uniform(20.0, 32.0), 1),
        "pb_ratio": round(np.random.uniform(3.0, 6.5), 1),
        "fifty_two_week_high": round(float(highs.max()), 2),
        "fifty_two_week_low": round(float(lows.min()), 2),
        "dividend_yield": 1.45,
        "summary": f"{company_name} ({ticker}) is one of India's premier enterprises listed on the National Stock Exchange of India (NSE).",
    }
    return df, info


def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Compute standard and advanced technical indicators on historical price dataframe."""
    df = df.copy()
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # Moving Averages
    df["SMA_20"] = close.rolling(window=20, min_periods=1).mean()
    df["SMA_50"] = close.rolling(window=50, min_periods=1).mean()
    df["SMA_200"] = close.rolling(window=200, min_periods=1).mean()
    df["EMA_12"] = close.ewm(span=12, adjust=False).mean()
    df["EMA_26"] = close.ewm(span=26, adjust=False).mean()

    # RSI (Relative Strength Index - 14)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
    rs = gain / (loss + 1e-9)
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD & Signal line
    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    # Bollinger Bands (20 periods, 2 std dev)
    rolling_mean_20 = close.rolling(window=20, min_periods=1).mean()
    rolling_std_20 = close.rolling(window=20, min_periods=1).std().fillna(0)
    df["BB_Upper"] = rolling_mean_20 + (rolling_std_20 * 2)
    df["BB_Lower"] = rolling_mean_20 - (rolling_std_20 * 2)
    df["BB_Middle"] = rolling_mean_20

    # ATR (Average True Range - 14)
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(window=14, min_periods=1).mean()

    # Stochastic Oscillator (14, 3, 3)
    low_14 = low.rolling(14, min_periods=1).min()
    high_14 = high.rolling(14, min_periods=1).max()
    df["Stoch_K"] = 100 * ((close - low_14) / ((high_14 - low_14) + 1e-9))
    df["Stoch_D"] = df["Stoch_K"].rolling(3, min_periods=1).mean()

    # VWAP Approximation
    typical_price = (high + low + close) / 3.0
    df["VWAP"] = (typical_price * volume).cumsum() / (volume.cumsum() + 1e-9)

    # Volume Moving Average & Spike Indicator
    df["Vol_SMA_20"] = volume.rolling(window=20, min_periods=1).mean()
    df["Vol_Spike"] = volume > (df["Vol_SMA_20"] * 1.5)

    # Daily Return
    df["Daily_Return"] = close.pct_change().fillna(0)

    return df


def _fetch_stock_data_uncached(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
    force_synthetic: bool = False
) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
    """Fetch raw stock data with fallback to synthetic."""
    is_valid, sanitized = sanitize_ticker(ticker)
    if not is_valid:
        logger.warning(f"Invalid ticker requested: {ticker}")
        return None, None

    ticker = sanitized

    if force_synthetic:
        return generate_synthetic_stock_data(ticker, period=period)

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        if df is None or df.empty:
            logger.info(f"Direct yfinance fetch returned empty for {ticker}. Engaging synthetic generator.")
            return generate_synthetic_stock_data(ticker, period=period)

        df.reset_index(inplace=True)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
        elif "Datetime" in df.columns:
            df["Date"] = pd.to_datetime(df["Datetime"]).dt.tz_localize(None)

        info = {}
        try:
            raw_info = stock.info
            info = {
                "name": raw_info.get("longName") or raw_info.get("shortName") or get_stock_name(ticker),
                "sector": raw_info.get("sector", "Indian Equities"),
                "industry": raw_info.get("industry", "NSE Stock"),
                "currency": raw_info.get("currency", "INR"),
                "current_price": raw_info.get("currentPrice") or (float(df["Close"].iloc[-1]) if not df.empty else 0),
                "market_cap": raw_info.get("marketCap", 0),
                "pe_ratio": raw_info.get("trailingPE", "N/A"),
                "pb_ratio": raw_info.get("priceToBook", "N/A"),
                "fifty_two_week_high": raw_info.get("fiftyTwoWeekHigh", float(df["High"].max()) if not df.empty else 0),
                "fifty_two_week_low": raw_info.get("fiftyTwoWeekLow", float(df["Low"].min()) if not df.empty else 0),
                "dividend_yield": (raw_info.get("dividendYield") or 0) * 100,
                "summary": raw_info.get("longBusinessSummary", f"{get_stock_name(ticker)} is an Indian corporate constituent listed on NSE."),
            }
        except Exception:
            last_close = float(df["Close"].iloc[-1]) if not df.empty else 0
            info = {
                "name": get_stock_name(ticker),
                "sector": "Indian Equities",
                "industry": "NSE Stock",
                "currency": "INR",
                "current_price": last_close,
                "market_cap": 0,
                "pe_ratio": "N/A",
                "pb_ratio": "N/A",
                "fifty_two_week_high": float(df["High"].max()) if not df.empty else 0,
                "fifty_two_week_low": float(df["Low"].min()) if not df.empty else 0,
                "dividend_yield": 0.0,
                "summary": f"{get_stock_name(ticker)} price data fetched directly from market ticker.",
            }

        df = compute_technical_indicators(df)
        return df, info
    except Exception as e:
        logger.warning(f"Error fetching data for {ticker}: {e}. Falling back to synthetic simulation.")
        return generate_synthetic_stock_data(ticker, period=period)


# Streamlit cached wrapper for high performance
@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_stock_data(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
    force_synthetic: bool = False
) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
    """Cached accessor for historical stock data."""
    return _fetch_stock_data_uncached(ticker, period, interval, force_synthetic)


def fetch_stock_news(ticker: str) -> List[Dict[str, str]]:
    """Fetch recent news articles for a ticker using yfinance with safe fallbacks."""
    try:
        stock = yf.Ticker(ticker)
        news_items = stock.news
        results = []
        if news_items:
            for item in news_items[:6]:
                title = item.get("title") or item.get("content", {}).get("title", "No Title Available")
                publisher = item.get("publisher") or item.get("content", {}).get("provider", {}).get("displayName", "Financial Express")
                link = item.get("link") or item.get("content", {}).get("canonicalUrl", {}).get("url", "#")
                pub_time = item.get("providerPublishTime") or item.get("content", {}).get("pubDate", "Recent")

                results.append({
                    "title": title,
                    "publisher": publisher,
                    "link": link,
                    "time": str(pub_time)
                })
        return results
    except Exception as e:
        logger.info(f"News fetch note for {ticker}: {e}")
        return []


def fetch_watchlist_summary(tickers: List[str], force_synthetic: bool = False) -> pd.DataFrame:
    """Fetch high-level overview metrics for a list of stocks to display a live tracker."""
    rows = []
    for sym in tickers:
        df, info = fetch_stock_data(sym, period="1mo", force_synthetic=force_synthetic)
        if df is not None and not df.empty:
            curr = float(df["Close"].iloc[-1])
            prev = float(df["Close"].iloc[-2]) if len(df) > 1 else curr
            chg = curr - prev
            chg_pct = (chg / prev) * 100 if prev else 0.0
            rsi = float(df["RSI"].iloc[-1])
            sma20 = float(df["SMA_20"].iloc[-1])
            trend = "Bullish 🟢" if curr >= sma20 else "Bearish 🔴"
            rsi_tag = "Oversold 💎" if rsi < 30 else ("Overbought ⚠️" if rsi > 70 else "Neutral ⚖️")

            rows.append({
                "Symbol": sym,
                "Company Name": info.get("name", sym),
                "Price (₹)": round(curr, 2),
                "Change (₹)": round(chg, 2),
                "Change (%)": round(chg_pct, 2),
                "RSI (14)": round(rsi, 1),
                "RSI Status": rsi_tag,
                "Trend": trend,
                "Volume (Shares)": f"{int(df['Volume'].iloc[-1]):,}"
            })
    return pd.DataFrame(rows)
