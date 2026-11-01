# 🏛 System Architecture: BharatAI Trader

This document details the architectural design, data pipelines, security layers, and component interactions of **BharatAI Trader**.

---

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PRESENTATION LAYER                                    │
│                 Streamlit Web UI (Fintech Dark Theme with Glassmorphic Cards)            │
│  ┌───────────────────────┬──────────────────────┬────────────────────────────────────┐  │
│  │  Live Watchlist Tape  │ Candlestick Charts   │ Multimodal AI Investment Brief     │  │
│  ├───────────────────────┼──────────────────────┼────────────────────────────────────┤  │
│  │  ML Direction Radar   │ Strategy Backtester  │ Paper Trading Wallet (₹ INR)       │  │
│  ├───────────────────────┴──────────────────────┴────────────────────────────────────┤  │
│  │  Markowitz Efficient Frontier Portfolio Optimizer │ Beginner Academy & Glossary   │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                APPLICATION / BUSINESS LOGIC                             │
│  ┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────────────┐  │
│  │   modules/data_loader │ │  modules/ai_assistant │ │      modules/ml_forecaster    │  │
│  │  - yfinance cached API│ │  - Google Gemini 2.5  │ │  - Random Forest Direction    │  │
│  │  - Indicator Engine   │ │  - OpenAI GPT-4o      │ │  - Isolation Forest Anomalies │  │
│  │  - Synthetic Fallback │ │  - Quant Rule Engine  │ │  - Feature Importance Ranks   │  │
│  └───────────────────────┘ └───────────────────────┘ └───────────────────────────────┘  │
│  ┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────────────┐  │
│  │   modules/backtester  │ │  modules/paper_trader │ │ modules/portfolio_optimizer   │  │
│  │  - Signal Execution   │ │  - Virtual Wallet     │ │  - Modern Portfolio Theory    │  │
│  │  - Risk Ratios (Sharpe│ │  - Order Validation   │ │  - Monte Carlo Simulation     │  │
│  │  - Equity Curves      │ │  - Live Mark-to-Market│ │  - SciPy SLSQP Optimization   │  │
│  └───────────────────────┘ └───────────────────────┘ └───────────────────────────────┘  │
└───────────────────────────────────────────┬─────────────────────────────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           SECURITY, PERSISTENCE & CONFIG LAYER                          │
│  ┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────────────┐  │
│  │    utils/security     │ │     config/stocks     │ │       data/paper_portfolio    │  │
│  │  - Regex Sanitization │ │  - Stock Sectors      │ │  - Atomic tempfile + replace  │  │
│  │  - Order Guard        │ │  - HCL Tech, Bluechips│ │  - Thread-locked write        │  │
│  │  - API Key Masking    │ │  - Benchmark Indices  │ │  - Corruption auto-recovery   │  │
│  └───────────────────────┘ └───────────────────────┘ └───────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. End-to-End Data Pipeline

```
1. USER SELECTION
   User selects or types an NSE symbol (e.g. "HCLTECH.NS" or "RELIANCE.NS").
                     │
                     ▼
2. SECURITY SANITIZATION (utils.security.sanitize_ticker)
   - Verifies against regex: ^[A-Za-z0-9\^_\.\-]{1,15}$
   - Strips malicious command injection / path traversal characters
   - Formats symbol with .NS suffix
                     │
                     ▼
3. CACHED DATA FETCHING (modules.data_loader.fetch_stock_data)
   - Checks Streamlit memory cache (@st.cache_data with 300s TTL)
   - Attempts Yahoo Finance download (history + info)
   - If offline or throttled: activates high-fidelity synthetic Geometric Brownian Motion engine
                     │
                     ▼
4. TECHNICAL INDICATOR COMPUTATION (modules.data_loader.compute_technical_indicators)
   - Calculates SMA (20, 50, 200), EMA (12, 26)
   - Calculates RSI (14), MACD & Signal line, Stochastic (%K, %D)
   - Calculates Bollinger Bands (2 std dev), ATR (14), and VWAP
                     │
                     ▼
5. PARALLEL ANALYTICAL CONSUMPTION
   ├── 5A. Plotly Visualization (modules.charting) -> Interactive Candlestick Chart
   ├── 5B. Machine Learning (modules.ml_forecaster) -> Random Forest & Isolation Forest
   ├── 5C. Generative AI (modules.ai_assistant) -> Gemini 2.5 / GPT-4o / Quant Engine Report
   ├── 5D. Strategy Backtester (modules.backtester) -> Simulates rule returns & Sharpe
   └── 5E. Paper Trader (modules.paper_trader) -> Matches market quote for virtual orders
```

---

## 3. Atomic State Persistence Model

To prevent file corruption or zero-byte race conditions in paper trading, the platform implements an **atomic write pattern**:

```
[Virtual Order Placed]
        │
        ▼
[Acquire Thread Lock (_FILE_LOCK)]
        │
        ▼
[Validate Parameters (Positive qty, finite price, cash check)]
        │
        ▼
[Create Temporary File (tmp_portfolio_XXXX.json in data/ dir)]
        │
        ▼
[Write JSON Content & Flush Buffer (f.flush() + os.fsync())]
        │
        ▼
[Atomic Replace (os.replace(temp_path, target_path))]
        │
        ▼
[Release Thread Lock]
```
- **Atomicity:** The destination file (`data/paper_portfolio.json`) always transitions instantaneously from the previous valid state to the new valid state.
- **Auto-Recovery:** If the JSON file is ever modified externally with invalid syntax, `safe_read_json` backs up the corrupt file as `.corrupt.bak` and re-initializes a clean default wallet.
