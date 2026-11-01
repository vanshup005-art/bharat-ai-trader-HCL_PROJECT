# 📖 BharatAI Trader — User Guide & Evaluator Manual

Welcome to **BharatAI Trader**, an AI-powered Indian Equities (NSE/BSE) Web Application designed for both quantitative analysts and beginner retail investors.

---

## 🚀 Quick Setup & Launch

### 1. Prerequisites
- Python 3.9 or higher.
- A virtual environment (already provided in the repository).

### 2. Launching the App
Open your terminal and navigate to the project root:

```bash
cd /Users/vanshgupta/.gemini/antigravity/scratch/ai-trading-platform
source venv/bin/activate
streamlit run app.py
```
The application will launch automatically in your default browser at `http://localhost:8501`.

---

## 🧭 Navigating the Platform

### 1. Top Market Ticker Tape
At the top of every page, a horizontal live ticker tape displays real-time quotes and percentage changes for key benchmark assets:
- **NIFTY 50** (`^NSEI`)
- **SENSEX** (`^BSESN`)
- **BANK NIFTY** (`^NSEBANK`)
- **NIFTY IT** (`^CNXIT`)
- **HCL Technologies** (`HCLTECH.NS`)
- **Reliance Industries** (`RELIANCE.NS`)
- **TCS** (`TCS.NS`)
- **HDFC Bank** (`HDFCBANK.NS`)

---

### 2. Page Guide

#### Page 1: 📊 Live Watchlist & Market Pulse
- Track major sectoral baskets: **IT & Technology (HCL Tech & Peers)**, **NIFTY 50 Bluechips**, and **Banking & Financials**.
- Instant overview of live prices, percentage changes, RSI status (Oversold / Overbought / Neutral), and institutional trends.

#### Page 2: 📈 Technical Candlestick Analysis
- Interactive, multi-panel Plotly charts.
- Use the checkboxes at the top of the chart to toggle:
  - Simple Moving Averages (20, 50, 200)
  - Bollinger Bands
  - RSI (14) Momentum
  - MACD & Histogram
  - Stochastic Oscillator (%K, %D)
  - VWAP (Volume Weighted Average Price)
- View the **Institutional Quantitative Snapshot** table below the chart.

#### Page 3: 🧠 AI Analyst & Sentiment Intelligence
- Click **"Synthesize Real-Time AI Analysis"** to generate a comprehensive investment report.
- Features:
  - **In Simple Words (ELI5):** 2-sentence plain English summary for beginners.
  - **Executive Verdict & Confidence Rating**
  - **Key Bullish Catalysts & Bearish Invalidation Levels**
  - **Actionable Price Matrix** (Support, Trend Pivot, Target)
  - **SEBI Educational Compliance Disclaimer**
- Supports Google Gemini, OpenAI, or the offline Built-in Quant Engine.

#### Page 4: 🔮 Predictive ML Forecast & Anomaly Radar
- **ML Trend Forecast Tab:**
  - Select 1-Day or 5-Day horizon.
  - View Random Forest Bullish vs. Bearish directional probability progress bars.
  - Inspect the **Feature Importance Ranking** to understand which technical indicators drove the prediction.
- **Institutional Anomaly Radar Tab:**
  - View price chart overlay highlighting statistical outliers flagged by the **Isolation Forest** model.
  - Identify institutional accumulation surges, heavy distribution selloffs, or volatility shocks.

#### Page 5: 🧪 Algorithmic Strategy Backtester
- Choose a beginner-friendly preset (e.g. *Beginner Safe (Low Risk)*, *Momentum Breakout*, *Mean Reversion Dip Buyer*) or customize your rules.
- Set starting capital, slippage/brokerage, and Stop-Loss / Take-Profit percentages.
- Review Sharpe Ratio, Sortino Ratio, Maximum Drawdown, Win Rate, and the interactive Equity Curve vs. NIFTY benchmark.

#### Page 6: 💼 Live Paper Trading Simulator (₹ INR)
- Start with a virtual capital wallet of **₹5,00,000 INR**.
- Select BUY or SELL, input share quantity, and click **"Submit Order"**.
- Orders are validated and executed in real-time, instantly updating your cash balance, stock holdings, and unrealized P&L.
- Order history is persistently stored on disk with atomic locking.

#### Page 7: 🎯 Portfolio Optimization & Robo-Advisor
- Select a basket of Indian stocks (e.g., HCL Tech, Reliance, TCS, HDFC Bank).
- Choose your risk profile (*Conservative*, *Moderate*, *Aggressive*).
- The platform computes the **Markowitz Efficient Frontier** via 2,500 Monte Carlo runs and SciPy SLSQP optimization.
- View Max Sharpe and Min Volatility asset allocation donut charts, correlation matrix, and personalized Robo-Advisor rebalancing rules.

#### Page 8: 🎓 Beginner Academy & Trading 101
- **Searchable Glossary:** Type any financial keyword (e.g. *RSI*, *Sharpe*, *Stop-Loss*, *P/E*) for an instant plain-English definition and beginner tip.
- **4 Golden Rules of Risk Management:** Essential principles for preserving trading capital.
- **Indicator Interpretation Cheat Sheet:** Quick reference guide for making informed trade decisions.

---

## 🔑 AI Configuration & Offline Mode

1. **Zero-Key Offline Mode (Default):**
   - The platform works immediately without any API keys using its **Built-in Quantitative Rule Engine**.
2. **Google Gemini (Optional):**
   - Expand **"🤖 AI Engine & Model Settings"** in the sidebar.
   - Select **Google Gemini** and choose `gemini-2.5-flash` or `gemini-2.5-pro`.
   - Paste your API key (or set `GEMINI_API_KEY` in `.env`).
3. **OpenAI (Optional):**
   - Select **OpenAI** and choose `gpt-4o` or `gpt-4o-mini`.
   - Paste your API key (or set `OPENAI_API_KEY` in `.env`).
4. **Demo Mode (Offline Testing):**
   - Toggle **"⚡ Demo Mode"** in the sidebar to simulate realistic market price action without relying on external internet connectivity.
