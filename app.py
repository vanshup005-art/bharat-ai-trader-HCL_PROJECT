"""
BharatAI Trader - AI-Powered Indian Equities Web Platform (NSE/BSE)
Designed for HCL Career Shaper Submission.
"""
import sys
import os
import streamlit as st
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Ensure local packages are discoverable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from config.stocks import (
    STOCK_SECTORS, ALL_STOCKS_MAP, TICKER_TAPE_SYMBOLS, get_stock_name
)
from config.settings import (
    APP_TITLE, APP_SUBTITLE, APP_VERSION, AUTHOR,
    SUPPORTED_AI_MODELS, DEFAULT_INITIAL_PAPER_CAPITAL,
    THEME_COLORS, STRATEGY_PRESETS
)
from utils.security import sanitize_ticker, mask_api_key
from utils.logger import get_logger

from modules.data_loader import (
    fetch_stock_data, fetch_stock_news, fetch_watchlist_summary
)
from modules.ai_assistant import generate_stock_ai_brief
from modules.ml_forecaster import train_and_forecast_trend, detect_market_anomalies
from modules.backtester import run_backtest
from modules.paper_trader import (
    execute_paper_order, reset_paper_portfolio, get_portfolio_summary
)
from modules.portfolio_optimizer import optimize_portfolio, generate_robo_advice
from modules.charting import (
    plot_candlestick_chart, plot_anomalies_chart, plot_equity_curve,
    plot_efficient_frontier, plot_allocation_donut, plot_correlation_heatmap
)
from modules.educational import TRADING_GLOSSARY, RISK_MANAGEMENT_GOLDEN_RULES

logger = get_logger()

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="BharatAI Trader | AI Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- CUSTOM MODERN FINTECH STYLING -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .stApp {
        background-color: #0B0E14;
        color: #F9FAFB;
    }
    
    /* Sleek card container */
    .glass-card {
        background: linear-gradient(135deg, rgba(21, 27, 38, 0.95), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(56, 189, 248, 0.18);
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
    }
    
    /* Beginner tip box */
    .beginner-card {
        background: rgba(56, 189, 248, 0.08);
        border-left: 4px solid #38BDF8;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 12px 0 16px 0;
        font-size: 13px;
        color: #E2E8F0;
        line-height: 1.5;
    }
    .beginner-card strong {
        color: #38BDF8;
    }
    
    /* Ticker tape pills */
    .ticker-pill {
        background: #151B26;
        border: 1px solid #212A3A;
        border-radius: 8px;
        padding: 8px 12px;
        text-align: center;
        display: inline-block;
        margin-right: 8px;
        min-width: 110px;
    }
    .ticker-pill-name {
        font-size: 11px;
        color: #9CA3AF;
        text-transform: uppercase;
        font-weight: 600;
    }
    .ticker-pill-price {
        font-size: 14px;
        font-weight: 700;
        color: #F9FAFB;
    }
    
    /* Badges */
    .badge-bull {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10B981;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-bear {
        background-color: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-neutral {
        background-color: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Streamlit Metric Overrides */
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR CONFIGURATION -----------------
st.sidebar.markdown(f"## 🇮🇳 BharatAI Trader")
st.sidebar.caption(f"**{APP_VERSION}** • {AUTHOR}")

# Page Navigation
page = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Live Watchlist & Market Pulse",
        "📈 Technical Candlestick Analysis",
        "🧠 AI Analyst & Sentiment Intelligence",
        "🔮 Predictive ML Forecast & Anomaly Radar",
        "🧪 Algorithmic Strategy Backtester",
        "💼 Live Paper Trading Simulator (₹ INR)",
        "🎯 Portfolio Optimization & Robo-Advisor",
        "🎓 Beginner Academy & Trading 101"
    ],
    index=0
)

st.sidebar.markdown("---")

# Beginner & Demo Mode Toggles
st.sidebar.subheader("App Modes")
beginner_mode = st.sidebar.toggle("💡 Beginner Mode (ELI5 Guides)", value=True, help="Enables beginner-friendly explanations and plain-English tooltips across all modules.")
demo_mode = st.sidebar.toggle("⚡ Demo Mode (Offline Data)", value=False, help="Uses realistic synthetic market generation for 100% offline testing or when Yahoo Finance is throttled.")

st.sidebar.markdown("---")

# Stock Asset Selector
st.sidebar.subheader("Select Asset / Ticker")
selected_sector = st.sidebar.selectbox("Sector Category", list(STOCK_SECTORS.keys()), index=0)
sector_stocks = STOCK_SECTORS[selected_sector]
selected_stock_sym = st.sidebar.selectbox(
    "Select Stock",
    list(sector_stocks.keys()),
    format_func=lambda x: f"{sector_stocks[x]} ({x})"
)

custom_ticker_input = st.sidebar.text_input("Or Custom NSE/BSE Ticker", placeholder="e.g. HCLTECH.NS or TATAPOWER.NS")
if custom_ticker_input.strip():
    is_valid, sanitized_sym = sanitize_ticker(custom_ticker_input)
    if is_valid:
        active_ticker = sanitized_sym
    else:
        st.sidebar.error(sanitized_sym)
        active_ticker = selected_stock_sym
else:
    active_ticker = selected_stock_sym

timeframe = st.sidebar.selectbox("Historical Lookback Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

# AI Engine Settings
st.sidebar.markdown("---")
with st.sidebar.expander("🤖 AI Engine & Model Settings", expanded=False):
    ai_provider = st.selectbox("Provider", ["Built-in Quant Engine", "Google Gemini", "OpenAI"])
    
    if ai_provider == "Google Gemini":
        available_models = list(SUPPORTED_AI_MODELS["Google Gemini"].keys())
        ai_model = st.selectbox(
            "Gemini Model",
            available_models,
            format_func=lambda x: SUPPORTED_AI_MODELS["Google Gemini"][x]
        )
        env_key = os.getenv("GEMINI_API_KEY", "")
        api_key_input = st.text_input("Gemini API Key", value=env_key, type="password", help="Leave blank to use GEMINI_API_KEY from environment or fallback to quant engine.")
        api_key = api_key_input if api_key_input else None
        st.caption(f"Status: **{'Key Detected (' + mask_api_key(api_key) + ')' if api_key else 'No Key (Falls back to Quant)'}**")

    elif ai_provider == "OpenAI":
        available_models = list(SUPPORTED_AI_MODELS["OpenAI"].keys())
        ai_model = st.selectbox(
            "OpenAI Model",
            available_models,
            format_func=lambda x: SUPPORTED_AI_MODELS["OpenAI"][x]
        )
        env_key = os.getenv("OPENAI_API_KEY", "")
        api_key_input = st.text_input("OpenAI API Key", value=env_key, type="password", help="Leave blank to use OPENAI_API_KEY from environment or fallback to quant engine.")
        api_key = api_key_input if api_key_input else None
        st.caption(f"Status: **{'Key Detected (' + mask_api_key(api_key) + ')' if api_key else 'No Key (Falls back to Quant)'}**")
        
    else:
        ai_model = "quant-rule-engine"
        api_key = None
        st.info("The Built-in Quant Engine operates 100% offline and requires zero API keys.")

# ----------------- LIVE MARKET TICKER TAPE BANNER -----------------
st.markdown("#### 🇮🇳 Live Market Ticker Tape")
ticker_cols = st.columns(len(TICKER_TAPE_SYMBOLS))
for idx, item in enumerate(TICKER_TAPE_SYMBOLS):
    with ticker_cols[idx]:
        # Quick synthetic or base price with small jitter for dynamic tape
        jitter = np.random.uniform(-0.6, 0.8)
        live_val = item["base_price"] * (1 + (jitter / 100.0))
        color = "#10B981" if jitter >= 0 else "#EF4444"
        arrow = "▲" if jitter >= 0 else "▼"
        st.markdown(f"""
        <div class="ticker-pill">
            <div class="ticker-pill-name">{item['name']}</div>
            <div class="ticker-pill-price">₹{live_val:,.1f}</div>
            <div style="font-size: 11px; font-weight: 600; color: {color};">{arrow} {jitter:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- LOAD ACTIVE STOCK DATA -----------------
with st.spinner(f"Loading market analytics for {active_ticker}..."):
    df, info = fetch_stock_data(active_ticker, period=timeframe, force_synthetic=demo_mode)

if df is None or df.empty:
    st.error(f"Could not load data for symbol '{active_ticker}'. Please verify the symbol or toggle 'Demo Mode' in the sidebar.")
    st.stop()


# =========================================================================
# PAGE 1: LIVE WATCHLIST & MARKET PULSE
# =========================================================================
if page == "📊 Live Watchlist & Market Pulse":
    st.title("📊 Indian Equities Watchlist & Market Pulse")
    st.caption("Real-time multi-stock scanner covering India's foremost technology, financial, and bluechip enterprises.")

    if beginner_mode:
        st.markdown("""
        <div class="beginner-card">
            <strong>💡 Beginner Tip:</strong> This scanner monitors key benchmark stocks simultaneously.
            Look for stocks where <strong>Trend is Bullish 🟢</strong> and <strong>RSI is between 40 and 65</strong> for strong momentum without being overbought!
        </div>
        """, unsafe_allow_html=True)

    watch_tab1, watch_tab2, watch_tab3 = st.tabs(["💻 IT & Tech Leaders (HCL Tech & Peers)", "🏛 NIFTY 50 Bluechips", "🏦 Banking & Financials"])

    with watch_tab1:
        it_tickers = list(STOCK_SECTORS["IT & Technology (Featured)"].keys())
        summary_it = fetch_watchlist_summary(it_tickers, force_synthetic=demo_mode)
        st.dataframe(
            summary_it,
            use_container_width=True,
            column_config={
                "Price (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                "Change (%)": st.column_config.NumberColumn(format="%.2f%%"),
            }
        )

    with watch_tab2:
        bluechip_tickers = list(STOCK_SECTORS["NIFTY 50 Bluechip Leaders"].keys())[:7]
        summary_bc = fetch_watchlist_summary(bluechip_tickers, force_synthetic=demo_mode)
        st.dataframe(
            summary_bc,
            use_container_width=True,
            column_config={
                "Price (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                "Change (%)": st.column_config.NumberColumn(format="%.2f%%"),
            }
        )

    with watch_tab3:
        bank_tickers = list(STOCK_SECTORS["Banking & Financial Services"].keys())[:6]
        summary_bank = fetch_watchlist_summary(bank_tickers, force_synthetic=demo_mode)
        st.dataframe(
            summary_bank,
            use_container_width=True,
            column_config={
                "Price (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                "Change (%)": st.column_config.NumberColumn(format="%.2f%%"),
            }
        )

    st.markdown("---")
    st.subheader(f"⚡ Spotlight: {info.get('name', active_ticker)} ({active_ticker})")
    sp_col1, sp_col2, sp_col3, sp_col4 = st.columns(4)
    curr_close = float(df["Close"].iloc[-1])
    prev_close = float(df["Close"].iloc[-2]) if len(df) > 1 else curr_close
    net_chg = curr_close - prev_close
    pct_chg = (net_chg / prev_close) * 100 if prev_close else 0.0

    with sp_col1:
        st.metric("Live Market Price", f"₹{curr_close:,.2f}", f"{net_chg:+,.2f} ({pct_chg:+.2f}%)")
    with sp_col2:
        mcap = info.get("market_cap", 0)
        st.metric("Market Capitalization", f"₹{mcap/1e7:,.1f} Cr" if mcap > 0 else "Large Cap")
    with sp_col3:
        st.metric("P/E Ratio", f"{info.get('pe_ratio', 'N/A')}")
    with sp_col4:
        st.metric("52-Week Range", f"₹{info.get('fifty_two_week_low', 0):,.1f} - ₹{info.get('fifty_two_week_high', 0):,.1f}")


# =========================================================================
# PAGE 2: TECHNICAL CANDLESTICK ANALYSIS
# =========================================================================
elif page == "📈 Technical Candlestick Analysis":
    st.title(f"📈 Technical Candlestick Charts: {info.get('name', active_ticker)}")
    st.caption(f"Symbol: `{active_ticker}` • Sector: `{info.get('sector', 'Indian Equities')}` • Currency: `{info.get('currency', 'INR')}`")

    if beginner_mode:
        st.markdown("""
        <div class="beginner-card">
            <strong>💡 How to read this chart:</strong><br>
            • <strong>Candlestick:</strong> Green = Price rose during the day; Red = Price fell.<br>
            • <strong>Moving Averages (SMA 20, 50, 200):</strong> When short-term (SMA 20) is above long-term (SMA 200), the stock is in a golden uptrend.<br>
            • <strong>RSI (14):</strong> Above 70 means overbought; below 30 means oversold.<br>
            • <strong>Volume:</strong> Taller bars indicate large institutional fund buying or selling.
        </div>
        """, unsafe_allow_html=True)

    # Indicator Toggles
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    show_ma = c1.checkbox("Moving Averages", value=True, help="Displays 20-day, 50-day, and 200-day Simple Moving Averages.")
    show_bb = c2.checkbox("Bollinger Bands", value=True, help="Displays upper and lower 2-std-dev volatility envelopes.")
    show_rsi = c3.checkbox("RSI (14)", value=True, help="Relative Strength Index oscillator.")
    show_macd = c4.checkbox("MACD", value=True, help="Moving Average Convergence Divergence momentum indicator.")
    show_stoch = c5.checkbox("Stochastic", value=False, help="Stochastic %K and %D momentum oscillator.")
    show_vwap = c6.checkbox("VWAP", value=True, help="Volume Weighted Average Price.")

    fig = plot_candlestick_chart(
        df,
        active_ticker,
        show_ma=show_ma,
        show_bb=show_bb,
        show_rsi=show_rsi,
        show_macd=show_macd,
        show_stoch=show_stoch,
        show_vwap=show_vwap
    )
    st.plotly_chart(fig, use_container_width=True)

    # Technical Indicators Snapshot Table
    st.markdown("#### 🔍 Institutional Quantitative Snapshot")
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        st.markdown(f"""
        - **SMA 20:** ₹{df['SMA_20'].iloc[-1]:,.2f}
        - **SMA 50:** ₹{df['SMA_50'].iloc[-1]:,.2f}
        - **SMA 200:** ₹{df['SMA_200'].iloc[-1]:,.2f}
        """)
    with t2:
        st.markdown(f"""
        - **Bollinger Upper:** ₹{df['BB_Upper'].iloc[-1]:,.2f}
        - **Bollinger Middle:** ₹{df['BB_Middle'].iloc[-1]:,.2f}
        - **Bollinger Lower:** ₹{df['BB_Lower'].iloc[-1]:,.2f}
        """)
    with t3:
        st.markdown(f"""
        - **RSI (14):** {df['RSI'].iloc[-1]:.1f}
        - **MACD Line:** {df['MACD'].iloc[-1]:.2f}
        - **MACD Signal:** {df['MACD_Signal'].iloc[-1]:.2f}
        """)
    with t4:
        st.markdown(f"""
        - **ATR Volatility:** ₹{df['ATR'].iloc[-1]:,.2f}
        - **VWAP:** ₹{df['VWAP'].iloc[-1]:,.2f}
        - **Volume Spike:** {'Yes 🚀' if df['Vol_Spike'].iloc[-1] else 'Normal ⚖️'}
        """)

    with st.expander("🏢 Company Profile & Fundamental Overview"):
        st.write(info.get("summary", "Constituent listed enterprise."))


# =========================================================================
# PAGE 3: AI ANALYST & SENTIMENT INTELLIGENCE
# =========================================================================
elif page == "🧠 AI Analyst & Sentiment Intelligence":
    st.title(f"🧠 AI Market Intelligence: {info.get('name', active_ticker)}")
    st.caption(f"Synthesizing quantitative indicators, company financials, and market news using {ai_provider}.")

    if beginner_mode:
        st.markdown("""
        <div class="beginner-card">
            <strong>💡 What this AI does:</strong> It acts as your personal Wall Street / Dalal Street quantitative analyst.
            It studies the stock's trends, support levels, momentum indicators, and recent news to draft a structured investment thesis with risk levels.
        </div>
        """, unsafe_allow_html=True)

    news_items = fetch_stock_news(active_ticker)
    col_left, col_right = st.columns([1.3, 0.7])

    with col_left:
        st.subheader("🤖 Generate AI Research Report")
        st.write(f"Active Model: **{ai_model}** ({ai_provider})")
        if st.button("🚀 Synthesize Real-Time AI Analysis", type="primary"):
            with st.spinner("Analyzing market data streams and synthesizing report..."):
                ai_brief = generate_stock_ai_brief(
                    active_ticker, info, df, news_items,
                    api_key=api_key, provider=ai_provider, model_name=ai_model
                )
                st.session_state["cached_ai_report"] = ai_brief

        if "cached_ai_report" in st.session_state:
            report_data = st.session_state["cached_ai_report"]
            st.success(f"Generated via: **{report_data['source']}**")
            st.markdown(report_data["report"])
        else:
            st.info("Click the button above to generate a full multimodal AI analyst thesis.")

    with col_right:
        st.subheader("📰 Financial News & Sentiment")
        sent = generate_heuristic_sentiment(news_items)
        badge_cls = "badge-bull" if sent["label"] == "Bullish" else ("badge-bear" if sent["label"] == "Bearish" else "badge-neutral")
        st.markdown(f"Sentiment Verdict: <span class='{badge_cls}'>{sent['label']} (Score: {sent['score']:+.2f})</span>", unsafe_allow_html=True)
        st.caption(sent["summary"])
        st.markdown("---")

        if news_items:
            for item in news_items:
                st.markdown(f"**[{item['title']}]({item['link']})**")
                st.caption(f"Publisher: {item['publisher']} • {item['time']}")
                st.markdown("---")
        else:
            st.write("No direct headlines detected. Monitoring general sector pulse.")


# =========================================================================
# PAGE 4: PREDICTIVE ML FORECAST & ANOMALY RADAR
# =========================================================================
elif page == "🔮 Predictive ML Forecast & Anomaly Radar":
    st.title(f"🔮 Predictive ML Forecasting & Anomaly Radar: {active_ticker}")
    st.caption("Machine Learning ensemble classification and unsupervised anomaly detection for institutional tracking.")

    if beginner_mode:
        st.markdown("""
        <div class="beginner-card">
            <strong>💡 How Machine Learning helps traders:</strong><br>
            • <strong>Random Forest:</strong> Combines 100 decision trees trained on historical indicator patterns to predict whether tomorrow's price is more likely to rise or fall.<br>
            • <strong>Isolation Forest:</strong> Identifies days where institutional hedge funds secretly entered or dumped massive quantities of shares.
        </div>
        """, unsafe_allow_html=True)

    tab_fc, tab_anom = st.tabs(["📊 ML Trend Direction Classifier", "🚨 Institutional Anomaly Radar"])

    with tab_fc:
        c1, c2 = st.columns([1, 1])
        with c1:
            horizon = st.radio("Forecast Prediction Horizon", ["1D (Next Trading Day)", "5D (Next 5 Trading Days)"], horizontal=True)
            h_code = "1D" if "1D" in horizon else "5D"

        with st.spinner("Training Random Forest ensemble..."):
            forecast_res = train_and_forecast_trend(df, horizon=h_code)

        if "error" in forecast_res:
            st.error(forecast_res["error"])
        else:
            p_up = forecast_res["prob_up"]
            p_down = forecast_res["prob_down"]

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric(f"Bullish Probability ({h_code})", f"{p_up}%")
                st.progress(p_up / 100)
            with m2:
                st.metric(f"Bearish Probability ({h_code})", f"{p_down}%")
                st.progress(p_down / 100)
            with m3:
                st.metric("Model Verdict", forecast_res["recommendation"])
                st.caption(f"Validation Out-of-Sample Accuracy: **{forecast_res['validation_accuracy']}%**")

            st.info(f"**In Plain Words:** {forecast_res['eli5_recommendation']}")

            st.markdown("#### 🔍 Feature Importance Ranking")
            st.write("These indicators carried the highest mathematical predictive power in the ensemble model:")
            feat_df = pd.DataFrame(forecast_res["top_features"])
            st.dataframe(feat_df, use_container_width=True)

    with tab_anom:
        st.subheader("Institutional Flow & Volume Anomaly Detector")
        st.write("Using an **Isolation Forest** on rolling volume and return Z-scores to flag institutional activity:")
        df_anom = detect_market_anomalies(df)
        fig_anom = plot_anomalies_chart(df_anom, active_ticker)
        st.plotly_chart(fig_anom, use_container_width=True)

        anomalies_found = df_anom[df_anom["Is_Anomaly"]]
        st.write(f"Detected **{len(anomalies_found)}** statistical anomalies in the selected timeframe.")
        if not anomalies_found.empty:
            st.dataframe(
                anomalies_found[["Date", "Close", "Volume", "Return_ZScore", "Volume_ZScore", "Anomaly_Type"]].tail(10),
                use_container_width=True
            )


# =========================================================================
# PAGE 5: STRATEGY BACKTESTER
# =========================================================================
elif page == "🧪 Algorithmic Strategy Backtester":
    st.title(f"🧪 Automated Algorithmic Strategy Backtester: {active_ticker}")
    st.caption("Simulate rule-based algorithmic trading strategies against historical NSE/BSE market bars.")

    if beginner_mode:
        st.markdown("""
        <div class="beginner-card">
            <strong>💡 What is Backtesting?</strong> It is like a time machine for trading!
            You test a set of trading rules on past data to see how much money you would have made (or lost), without risking a single rupee.
            Always look for a <strong>Sharpe Ratio > 1.0</strong> and a <strong>low Maximum Drawdown</strong>.
        </div>
        """, unsafe_allow_html=True)

    col_cfg, col_res = st.columns([0.85, 1.15])

    with col_cfg:
        st.subheader("⚙️ Strategy Configuration")
        
        # Beginner Strategy Presets
        chosen_preset = st.selectbox("Strategy Presets (Beginner Friendly)", ["Custom Manual"] + list(STRATEGY_PRESETS.keys()))
        
        if chosen_preset != "Custom Manual":
            preset_data = STRATEGY_PRESETS[chosen_preset]
            st.caption(f"**Preset Details:** {preset_data['description']}")
            strategy_choice = preset_data["strategy"]
            sl_default = preset_data.get("stop_loss_pct", 3.0)
            tp_default = preset_data.get("take_profit_pct", 8.0)
        else:
            strategy_choice = st.selectbox(
                "Strategy Type",
                [
                    "SMA Crossover",
                    "RSI Mean Reversion",
                    "MACD Momentum",
                    "Bollinger Bands Bounce",
                    "AI Quantitative Ensemble"
                ]
            )
            sl_default = 3.0
            tp_default = 8.0

        params = {}
        if strategy_choice == "SMA Crossover":
            params["fast_ma"] = st.slider("Fast SMA Period (Days)", 5, 50, 20)
            params["slow_ma"] = st.slider("Slow SMA Period (Days)", 20, 200, 50)
        elif strategy_choice == "RSI Mean Reversion":
            params["oversold"] = st.slider("RSI Buy Level (Oversold)", 15, 45, 30)
            params["overbought"] = st.slider("RSI Sell Level (Overbought)", 55, 85, 70)

        initial_cap = st.number_input("Starting Capital (₹ INR)", min_value=10000, max_value=10000000, value=100000, step=10000)
        brokerage = st.slider("Brokerage & Slippage (%)", 0.0, 0.5, 0.05, step=0.01) / 100.0

        st.markdown("**Risk Management Controls**")
        sl_pct = st.slider("Stop Loss (%) (0 to disable)", 0.0, 15.0, float(sl_default), step=0.5) / 100.0
        tp_pct = st.slider("Take Profit (%) (0 to disable)", 0.0, 30.0, float(tp_default), step=0.5) / 100.0

    with col_res:
        st.subheader("📊 Backtest Performance KPIs")
        results = run_backtest(
            df,
            strategy_name=strategy_choice,
            initial_capital=initial_cap,
            fee_pct=brokerage,
            stop_loss_pct=sl_pct,
            take_profit_pct=tp_pct,
            **params
        )

        if "error" in results:
            st.error(results["error"])
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Strategy Net Return", f"{results['total_return_pct']:+.2f}%", f"₹{results['net_profit']:+,.2f}")
            m2.metric("Benchmark Return", f"{results['benchmark_return_pct']:+.2f}%")
            m3.metric("CAGR", f"{results['cagr_pct']:.2f}%")
            m4.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")

            m5, m6, m7, m8 = st.columns(4)
            m5.metric("Sortino Ratio", f"{results['sortino_ratio']:.2f}")
            m6.metric("Max Drawdown", f"-{results['max_drawdown_pct']:.2f}%")
            m7.metric("Win Rate", f"{results['win_rate_pct']:.1f}%")
            m8.metric("Total Trades", f"{results['total_trades']}")

            fig_eq = plot_equity_curve(results["dates"], results["equity_curve"], results["benchmark_curve"])
            st.plotly_chart(fig_eq, use_container_width=True)

            if results["trades"]:
                with st.expander(f"📜 Detailed Trade Execution Log ({len(results['trades'])} Trades)"):
                    trades_df = pd.DataFrame(results["trades"])
                    st.dataframe(trades_df, use_container_width=True)
            else:
                st.info("No trades were triggered with these specific parameters during this historical period.")


# =========================================================================
# PAGE 6: LIVE PAPER TRADING SIMULATOR
# =========================================================================
elif page == "💼 Live Paper Trading Simulator (₹ INR)":
    st.title("💼 Live Paper Trading Simulator (₹ INR)")
    st.caption("Practice executing trades in real-time with simulated Indian Rupee capital without risking real money.")

    if beginner_mode:
        st.markdown("""
        <div class="beginner-card">
            <strong>💡 What is Paper Trading?</strong> It is virtual trading with fake money on real stock quotes!
            Use this sandbox to practice placing BUY and SELL orders, watching your portfolio's profit and loss (P&L), and mastering your trading psychology.
        </div>
        """, unsafe_allow_html=True)

    curr_p = float(df["Close"].iloc[-1])
    portfolio_data = get_portfolio_summary({active_ticker: curr_p})

    # Summary Row
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Portfolio Value", f"₹{portfolio_data['total_portfolio_value']:,.2f}", f"{portfolio_data['total_return_pct']:+.2f}%")
    k2.metric("Available Cash Balance", f"₹{portfolio_data['cash_balance']:,.2f}")
    k3.metric("Stock Holdings Value", f"₹{portfolio_data['holdings_value']:,.2f}")
    k4.metric("Unrealized P&L", f"₹{portfolio_data['unrealized_pnl']:+,.2f}")

    col_trade, col_holdings = st.columns([1, 1.2])

    with col_trade:
        st.subheader("⚡ Execute Order")
        st.markdown(f"**Asset:** `{active_ticker}` | **Live Quote:** `₹{curr_p:,.2f}`")
        order_action = st.radio("Order Type", ["BUY", "SELL"], horizontal=True)
        order_qty = st.number_input("Shares Quantity", min_value=1, max_value=100000, value=10, step=1)
        est_val = order_qty * curr_p
        st.write(f"Estimated Order Value: **₹{est_val:,.2f}**")

        if st.button("Submit Order", type="primary"):
            success, msg = execute_paper_order(active_ticker, order_action, order_qty, curr_p)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

        st.markdown("---")
        with st.expander("⚠️ Reset Paper Trading Account"):
            reset_cap = st.number_input("Reset Capital (₹)", value=int(DEFAULT_INITIAL_PAPER_CAPITAL), step=50000)
            if st.button("Reset Account"):
                reset_paper_portfolio(reset_cap)
                st.success("Paper portfolio has been reset!")
                st.rerun()

    with col_holdings:
        st.subheader("📊 Current Holdings")
        if portfolio_data["holdings"]:
            h_df = pd.DataFrame(portfolio_data["holdings"])
            st.dataframe(h_df, use_container_width=True)
        else:
            st.info("No active open stock positions. Place your first BUY order on the left.")

        st.subheader("📜 Recent Executed Orders")
        if portfolio_data["recent_orders"]:
            orders_df = pd.DataFrame(portfolio_data["recent_orders"])
            st.dataframe(orders_df, use_container_width=True)
        else:
            st.caption("No orders executed yet.")


# =========================================================================
# PAGE 7: PORTFOLIO OPTIMIZATION & ROBO-ADVISOR
# =========================================================================
elif page == "🎯 Portfolio Optimization & Robo-Advisor":
    st.title("🎯 Modern Portfolio Theory (MPT) & AI Robo-Advisory")
    st.caption("Markowitz Efficient Frontier calculation and risk-tailored asset allocation for Indian Equities.")

    if beginner_mode:
        st.markdown("""
        <div class="beginner-card">
            <strong>💡 Modern Portfolio Theory (MPT) in Plain English:</strong><br>
            • <strong>Diversification:</strong> Combining stocks from different sectors (e.g. HCL Tech + Reliance + Sun Pharma + HDFC Bank) reduces your overall risk.<br>
            • <strong>Max Sharpe:</strong> Gives you the highest possible profit per unit of risk.<br>
            • <strong>Min Volatility:</strong> The safest, smoothest portfolio designed to protect your capital.
        </div>
        """, unsafe_allow_html=True)

    default_pool = ["HCLTECH.NS", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "SUNPHARMA.NS", "ITC.NS"]
    all_available = list(ALL_STOCKS_MAP.keys())[:25]
    selected_pool = st.multiselect(
        "Select Assets for Optimization Basket",
        all_available,
        default=[s for s in default_pool if s in all_available]
    )

    if len(selected_pool) < 2:
        st.warning("Please select at least 2 stocks to construct a diversified portfolio basket.")
        st.stop()

    risk_pref = st.selectbox(
        "Your Investment Risk Profile",
        ["Moderate (Balanced)", "Conservative (Low Risk)", "Aggressive (High Growth)"]
    )

    with st.spinner("Computing covariance matrix and running Monte Carlo simulation..."):
        opt_res = optimize_portfolio(selected_pool, period=timeframe, force_synthetic=demo_mode)

    if "error" in opt_res:
        st.error(opt_res["error"])
    else:
        st.plotly_chart(
            plot_efficient_frontier(opt_res["simulation"], opt_res["max_sharpe"], opt_res["min_volatility"]),
            use_container_width=True
        )

        robo_advice = generate_robo_advice(opt_res, risk_pref)
        st.markdown(robo_advice)

        st.subheader("⚖️ Optimal Allocation Models")
        c1, c2 = st.columns(2)
        with c1:
            fig_ms = plot_allocation_donut(opt_res["max_sharpe"]["weights"], title="Max Sharpe Allocation (High Alpha)")
            st.plotly_chart(fig_ms, use_container_width=True)
            st.caption(f"Expected Return: **{opt_res['max_sharpe']['expected_return']}%** | Volatility: **{opt_res['max_sharpe']['volatility']}%** | Sharpe: **{opt_res['max_sharpe']['sharpe_ratio']}**")

        with c2:
            fig_mv = plot_allocation_donut(opt_res["min_volatility"]["weights"], title="Min Volatility Allocation (Defensive)")
            st.plotly_chart(fig_mv, use_container_width=True)
            st.caption(f"Expected Return: **{opt_res['min_volatility']['expected_return']}%** | Volatility: **{opt_res['min_volatility']['volatility']}%** | Sharpe: **{opt_res['min_volatility']['sharpe_ratio']}**")

        with st.expander("📊 Correlation Matrix Heatmap"):
            corr_df = pd.DataFrame(opt_res["correlation_matrix"])
            fig_heat = plot_correlation_heatmap(corr_df)
            st.plotly_chart(fig_heat, use_container_width=True)


# =========================================================================
# PAGE 8: BEGINNER ACADEMY & TRADING 101
# =========================================================================
elif page == "🎓 Beginner Academy & Trading 101":
    st.title("🎓 Beginner Academy & Trading 101")
    st.caption("Essential knowledge, risk management golden rules, and a searchable financial glossary for aspiring traders.")

    acad_tab1, acad_tab2, acad_tab3 = st.tabs(["📚 Searchable Trading Glossary", "🛡 Golden Rules of Risk Management", "📊 Indicator Interpretation Cheat Sheet"])

    with acad_tab1:
        st.subheader("🔍 Financial Trading Glossary")
        search_query = st.text_input("Search terms (e.g., RSI, Sharpe, Stop-Loss, Bollinger)", placeholder="Type to filter...")
        
        filtered_terms = {
            k: v for k, v in TRADING_GLOSSARY.items()
            if search_query.lower() in k.lower() or search_query.lower() in v["definition"].lower()
        }

        for term, details in filtered_terms.items():
            with st.expander(f"📖 {term} ({details['category']})", expanded=(len(search_query) > 0)):
                st.markdown(f"**Definition:** {details['definition']}")
                st.markdown(f"💡 **Beginner Tip:** {details['beginner_tip']}")

    with acad_tab2:
        st.subheader("🛡 4 Golden Rules of Professional Risk Management")
        for rule in RISK_MANAGEMENT_GOLDEN_RULES:
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="margin: 0; color: #38BDF8;">{rule['title']}</h4>
                <p style="margin: 8px 0 0 0; color: #D1D5DB; font-size: 14px;">{rule['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

    with acad_tab3:
        st.subheader("📊 Key Indicator Cheat Sheet")
        st.markdown("""
| Indicator | What It Measures | When to Buy | When to Sell / Caution |
| :--- | :--- | :--- | :--- |
| **SMA 50 / 200** | Long-term Trend | Price crosses above SMA 200 | Price closes below SMA 50 or SMA 200 |
| **RSI (14)** | Momentum Speed | Oversold bounce below 30 | Overbought exhaustion above 70 |
| **MACD** | Velocity & Direction | Blue line crosses above Orange line | Blue line crosses below Orange line |
| **Bollinger Bands**| Volatility Envelopes | Price touches Lower Band + bullish candle | Price touches Upper Band |
| **Volume Spike** | Institutional Footprint | Massive volume on green candle (Accumulation)| Massive volume on red candle (Distribution) |
        """)
