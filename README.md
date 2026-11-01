# 🇮🇳 BharatAI Trader — AI-Powered Indian Equities Web Platform

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50.0-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.6.1-F7931E.svg)](https://scikit-learn.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20GenAI-2.5%20Flash%20%7C%20Pro-4285F4.svg)](https://ai.google.dev/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o%20%7C%20o1--mini-00A67E.svg)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**BharatAI Trader** is an institutional-grade, beginner-friendly financial technology web application engineered for the Indian equity markets (NSE/BSE). It unifies quantitative finance, machine learning directional forecasting, multi-model generative AI intelligence, strategy backtesting, atomic paper trading, and Modern Portfolio Theory (MPT) optimization.

> [!NOTE]
> **Prepared for:** HCL Career Shaper Submission  
> **Special Spotlight:** Features in-depth quantitative coverage of **HCL Technologies Ltd (`HCLTECH.NS`)** and India's top technology and bluechip constituents.

---

## 🌟 Key Upgraded Features

### 1. 📊 Live Watchlist & Market Pulse Scanner
- Batch scanner across curated Indian sectors: **IT & Technology (HCL Tech, TCS, Infosys, Wipro, LTIMindtree)**, **NIFTY 50 Bluechips**, **Banking & Financials**, **Automotive**, **Energy**, and **Pharma**.
- Real-time animated **Top Market Ticker Tape** displaying live quotes and percentage changes for benchmark indices and flagship stocks.

### 2. 📈 Modern Technical Candlestick Analysis
- Institutional multi-panel Plotly charts with:
  - **Moving Averages:** SMA 20, SMA 50, SMA 200 (Golden cross & death cross detection)
  - **Volatility & Envelopes:** Bollinger Bands (2 std dev) and Average True Range (ATR)
  - **Momentum:** RSI (14), MACD & Signal histogram, Stochastic Oscillator (%K, %D)
  - **Volume Intelligence:** Volume Weighted Average Price (VWAP) and institutional volume spikes

### 3. 🧠 Upgraded Multi-Model Generative AI Market Intelligence
- **Google Gemini Integration:** Supports state-of-the-art `gemini-2.5-flash` (recommended default), `gemini-2.5-pro`, and `gemini-1.5-pro`.
- **OpenAI Integration:** Supports `gpt-4o`, `gpt-4o-mini`, and `o1-mini`.
- **Zero-Key Offline Fallback:** Built-in Quantitative Rule Engine that works 100% offline with zero API keys required.
- **Beginner ELI5 Summaries:** Every AI report includes a 2-sentence plain-English breakdown alongside institutional support/resistance pivots, bullish catalysts, and bearish invalidation levels.
- **SEBI Educational Disclaimer:** Strict regulatory compliance notice appended to every report.

### 4. 🔮 Predictive ML Direction Classifier & Institutional Anomaly Radar
- **Random Forest Classifier (100 Trees):** Predicts 1-Day and 5-Day directional probabilities with complete feature importance transparency.
- **Isolation Forest Anomaly Radar:** Detects hidden institutional activity, flagging *Whale Buying Surges*, *Distribution Selloffs*, and *Volatility Shocks*.

### 5. 🧪 Algorithmic Strategy Backtester with Beginner Presets
- Pre-configured strategy templates: *Beginner Safe (Low Risk)*, *Momentum Breakout*, *Mean Reversion Dip Buyer*, and *Institutional Multi-Factor Ensemble*.
- Rigorous risk metrics: CAGR, Sharpe Ratio (relative to RBI 6.50% repo rate), Sortino Ratio (downside risk), Maximum Drawdown (MDD), Win Rate, and interactive Equity Curves.

### 6. 💼 Thread-Safe Live Paper Trading Simulator (₹ INR)
- Simulated ₹5,00,000 INR virtual wallet for risk-free practice.
- Real-time BUY and SELL execution with instant mark-to-market P&L.
- **Security & Reliability:** Atomic disk writing (`mkstemp` + `os.replace`) with thread locking to prevent file corruption.

### 7. 🎯 Modern Portfolio Theory (MPT) & AI Robo-Advisory
- 2,500+ Monte Carlo runs plotting the **Markowitz Efficient Frontier**.
- Numerical SciPy SLSQP optimization computing **Maximum Sharpe** and **Minimum Volatility** allocations.
- Dynamic Robo-Advisor tailoring asset allocation to *Conservative*, *Moderate*, and *Aggressive* risk profiles.
- Interactive correlation heatmaps.

### 8. 🎓 Beginner Academy & Trading 101
- **Searchable Trading Glossary:** Plain-English definitions and beginner tips for financial terms.
- **4 Golden Rules of Risk Management:** Capital preservation guidelines.
- **Indicator Interpretation Cheat Sheet.**

---

## 📁 Modular File-Folder Architecture

```
ai-trading-platform/
├── app.py                      # Main Streamlit Web Application
├── requirements.txt            # Python dependencies
├── .env.example                # Safe environment variable configuration template
├── README.md                   # Repository documentation
│
├── config/                     # Configuration and Master Data
│   ├── __init__.py
│   ├── settings.py             # Global constants, supported AI models, risk presets
│   └── stocks.py               # Comprehensive Indian stock universe & sectoral mappings
│
├── modules/                    # Core Business Logic & Analytics Engines
│   ├── __init__.py
│   ├── data_loader.py          # NSE/BSE data fetcher, indicator engine, synthetic fallback
│   ├── ai_assistant.py         # Multi-model LLM analyst (Gemini, OpenAI, Quant Engine)
│   ├── ml_forecaster.py        # Random Forest direction forecaster & Isolation Forest radar
│   ├── backtester.py           # Algorithmic strategy backtester (Sharpe, Sortino, Drawdown)
│   ├── paper_trader.py         # Virtual ₹ INR wallet with atomic disk persistence
│   ├── portfolio_optimizer.py  # Modern Portfolio Theory (MPT) & Robo-Advisory
│   ├── charting.py             # Plotly financial charts with fintech styling
│   └── educational.py          # Beginner Academy, trading glossary, and golden rules
│
├── utils/                      # Security, Sanitization & Logging Utilities
│   ├── __init__.py
│   ├── security.py             # Input regex sanitizers, order validators, atomic JSON writes
│   └── logger.py               # Structured, privacy-safe application logger
│
├── tests/                      # Automated Verification & Quality Assurance
│   ├── __init__.py
│   └── test_platform.py        # 9 automated unit and integration tests (100% pass)
│
├── docs/                       # Project Documentation & Submission Artifacts
│   ├── PROJECT_REPORT.md       # Comprehensive HCL Career Shaper Submission Report
│   ├── ARCHITECTURE.md         # System Architecture & Flowcharts
│   └── USER_GUIDE.md           # Step-by-Step Evaluator & User Manual
│
└── data/                       # Local State & Persistence
    └── paper_portfolio.json    # Thread-safe virtual portfolio state
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.9+ installed.

### 2. Activate Virtual Environment
```bash
cd /Users/vanshgupta/.gemini/antigravity/scratch/ai-trading-platform
source venv/bin/activate
```

### 3. Run Automated Tests
```bash
python3 tests/test_platform.py
```
*(All 9 unit and integration tests pass with 100% success rate).*

### 4. Launch the Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🔒 Security Audit & Reliability Protections

1. **Regex Whitelist Input Sanitization:** Tickers are validated via `^[A-Za-z0-9\^_\.\-]{1,15}$`. Shell characters, path traversal (`../`), and script tags are strictly rejected.
2. **Atomic Disk Persistence:** Thread-locked atomic writes (`tmp` file + `os.replace`) guarantee that portfolio data never corrupts during power loss.
3. **Safe API Key Shielding:** API keys can be loaded via `.env` or input through the UI with automatic masking (`AIza...4x9B`).
4. **Resilient Offline Fallback:** If internet access is unavailable or Yahoo Finance is throttled, the platform smoothly activates its synthetic market generator.

---

## 📄 Submission Documentation
- **[HCL Career Shaper Project Report](file:///Users/vanshgupta/.gemini/antigravity/scratch/ai-trading-platform/docs/PROJECT_REPORT.md)**
- **[System Architecture Documentation](file:///Users/vanshgupta/.gemini/antigravity/scratch/ai-trading-platform/docs/ARCHITECTURE.md)**
- **[Beginner & Evaluator User Manual](file:///Users/vanshgupta/.gemini/antigravity/scratch/ai-trading-platform/docs/USER_GUIDE.md)**
