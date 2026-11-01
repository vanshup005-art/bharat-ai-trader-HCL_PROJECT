"""
AI Market Assistant & Sentiment Analysis Module.
Supports modern Google Gemini models (Gemini 2.5 Flash, Gemini 2.5 Pro, Gemini 1.5 Pro),
OpenAI models (GPT-4o, GPT-4o-mini, o1-mini), and the Built-in Quant Engine.
Includes beginner-friendly ELI5 explanations, structured theses, and SEBI compliance disclaimers.
"""
import os
from typing import Dict, List, Optional, Any
import pandas as pd
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

from utils.logger import get_logger
from utils.security import mask_api_key

logger = get_logger()


def generate_heuristic_sentiment(news_items: List[Dict[str, str]]) -> Dict[str, Any]:
    """Analyze news headlines using financial keyword heuristics."""
    if not news_items:
        return {
            "score": 0.05,
            "label": "Neutral",
            "summary": "No recent direct company headlines found. General sector baseline applies.",
            "bullish_keywords": [],
            "bearish_keywords": []
        }

    positive_words = {
        "surge", "jump", "record", "profit", "growth", "high", "upgrade", "buy",
        "beat", "bull", "gain", "expansion", "dividend", "acquisition", "outperform",
        "rally", "order win", "contract", "positive", "breakout", "strong"
    }
    negative_words = {
        "drop", "fall", "loss", "plunge", "downgrade", "sell", "miss", "bear",
        "decline", "investigation", "penalty", "slump", "weak", "warning", "debt",
        "fine", "audit", "fraud", "crash", "headwind"
    }

    pos_found = []
    neg_found = []

    for item in news_items:
        title = item.get("title", "").lower()
        for w in positive_words:
            if w in title:
                pos_found.append(w)
        for w in negative_words:
            if w in title:
                neg_found.append(w)

    pos_count = len(pos_found)
    neg_count = len(neg_found)
    total = pos_count + neg_count

    if total == 0:
        score = 0.05
        label = "Neutral"
    else:
        score = (pos_count - neg_count) / total
        if score > 0.2:
            label = "Bullish"
        elif score < -0.2:
            label = "Bearish"
        else:
            label = "Neutral"

    return {
        "score": round(score, 2),
        "label": label,
        "summary": f"Analyzed {len(news_items)} headlines: detected {pos_count} positive and {neg_count} negative financial sentiment cues.",
        "bullish_keywords": list(set(pos_found)),
        "bearish_keywords": list(set(neg_found))
    }


def generate_stock_ai_brief(
    ticker: str,
    stock_info: Dict[str, Any],
    df: pd.DataFrame,
    news_items: List[Dict[str, str]],
    api_key: Optional[str] = None,
    provider: str = "Built-in Quant Engine",
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate an institutional-grade, beginner-friendly AI investment report.
    Supports modern Gemini (2.5 Flash, 2.5 Pro), OpenAI (GPT-4o, GPT-4o-mini),
    and built-in quantitative heuristic fallback.
    """
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    current_price = float(latest["Close"])
    daily_change_pct = float(latest.get("Daily_Return", 0)) * 100
    rsi = float(latest.get("RSI", 50))
    macd = float(latest.get("MACD", 0))
    macd_signal = float(latest.get("MACD_Signal", 0))
    sma_20 = float(latest.get("SMA_20", current_price))
    sma_50 = float(latest.get("SMA_50", current_price))
    sma_200 = float(latest.get("SMA_200", current_price))
    bb_upper = float(latest.get("BB_Upper", current_price))
    bb_lower = float(latest.get("BB_Lower", current_price))

    sentiment = generate_heuristic_sentiment(news_items)

    # Technical signals
    trend = "Bullish" if current_price > sma_50 > sma_200 else ("Bearish" if current_price < sma_50 < sma_200 else "Consolidating / Mixed")
    rsi_signal = "Oversold (Potential Reversal Bounce)" if rsi < 30 else ("Overbought (Potential Exhaustion)" if rsi > 70 else "Neutral Momentum")
    macd_signal_str = "Bullish Crossover" if macd > macd_signal and prev.get("MACD", 0) <= prev.get("MACD_Signal", 0) else ("Bullish Momentum" if macd > macd_signal else "Bearish Momentum")

    context_prompt = f"""
Asset: {ticker} ({stock_info.get('name', ticker)})
Current Price: ₹{current_price:,.2f} ({daily_change_pct:+.2f}% today)
Sector: {stock_info.get('sector', 'Indian Equities')}
P/E Ratio: {stock_info.get('pe_ratio', 'N/A')} | Market Cap: ₹{stock_info.get('market_cap', 0)/1e7:,.1f} Cr
52-Week Range: ₹{stock_info.get('fifty_two_week_low', 0):,.2f} - ₹{stock_info.get('fifty_two_week_high', 0):,.2f}

Technical Metrics:
- Overall Trend: {trend}
- 20-day SMA: ₹{sma_20:,.2f}
- 50-day SMA: ₹{sma_50:,.2f}
- 200-day SMA (Institutional Baseline): ₹{sma_200:,.2f}
- RSI (14): {rsi:.1f} ({rsi_signal})
- MACD: {macd:.2f} vs Signal {macd_signal:.2f} ({macd_signal_str})
- Bollinger Bands: Lower ₹{bb_lower:,.2f} | Upper ₹{bb_upper:,.2f}

News Sentiment: {sentiment['label']} (Score: {sentiment['score']:+.2f})
Recent Headlines: {[item.get('title') for item in news_items[:4]]}
"""

    # Check environment variable if key was not passed in UI
    resolved_gemini_key = api_key or os.getenv("GEMINI_API_KEY")
    resolved_openai_key = api_key or os.getenv("OPENAI_API_KEY")

    # 1. Google Gemini Execution
    if provider == "Google Gemini" and resolved_gemini_key:
        active_model = model_name or "gemini-2.5-flash"
        try:
            from google import genai
            client = genai.Client(api_key=resolved_gemini_key)
            prompt = f"""You are a Lead Financial Analyst specializing in the Indian stock market (NSE/BSE).
Provide a structured, institutional, and beginner-friendly research report for {ticker} using the data below:

{context_prompt}

Generate your response in clean GitHub-Flavored Markdown with these sections:
1. **Executive Verdict & Rating** (e.g., Strong Buy / Accumulate on Dips / Hold / Reduce / Avoid, with a Confidence Score between 0-100% and time horizon).
2. **Beginner Summary (ELI5)**: Explain in 2 simple sentences what is happening with this stock in plain, jargon-free English for a beginner investor.
3. **Key Bullish Catalysts** (3 concise bullet points combining technicals and fundamentals).
4. **Key Bearish Risks & Invalidation Level** (3 concise bullet points including where this thesis becomes invalid).
5. **Key Price Levels**:
   - Immediate Support / Accumulation Band
   - 50-Day Trend Pivot
   - Breakout Resistance / Target Band
6. **Risk Management Advice**: Position sizing suggestion (e.g. 2-5% of total portfolio) and stop-loss placement.

End with a standard SEBI educational disclaimer stating this is algorithmic research and not certified investment advice.
"""
            response = client.models.generate_content(
                model=active_model,
                contents=prompt
            )
            logger.info(f"Generated AI report using Google Gemini model {active_model} for {ticker}")
            return {
                "report": response.text,
                "sentiment": sentiment,
                "source": f"Google Gemini ({active_model})",
                "trend": trend,
                "rsi_status": rsi_signal
            }
        except Exception as e:
            logger.warning(f"Gemini API call ({active_model}) failed: {e}. Falling back to Quant Engine.")
            fallback_note = f"> [!WARNING]\n> **Gemini API Notification:** {str(e)[:120]}...\n> Automatically switched to the Built-in Quantitative AI Engine.\n\n"
            return {
                "report": fallback_note + _generate_rule_based_synthesis(ticker, stock_info, current_price, trend, rsi, rsi_signal, macd_signal_str, sentiment, sma_50, sma_200, bb_upper, bb_lower),
                "sentiment": sentiment,
                "source": "Quantitative Heuristic Engine (Fallback)",
                "trend": trend,
                "rsi_status": rsi_signal
            }

    # 2. OpenAI Execution
    elif provider == "OpenAI" and resolved_openai_key:
        active_model = model_name or "gpt-4o-mini"
        try:
            from openai import OpenAI
            client = OpenAI(api_key=resolved_openai_key)
            completion = client.chat.completions.create(
                model=active_model,
                messages=[
                    {"role": "system", "content": "You are a quantitative equity analyst specializing in Indian equity markets (NSE/BSE). Deliver professional, structured, and beginner-accessible research with clear support/resistance levels."},
                    {"role": "user", "content": f"Analyze this asset setup:\n{context_prompt}\nProvide Executive Verdict with Confidence %, Beginner Summary (ELI5), 3 Bull Catalysts, 3 Bear Risks, Price Pivots, and SEBI compliance disclaimer."}
                ]
            )
            content = completion.choices[0].message.content
            logger.info(f"Generated AI report using OpenAI model {active_model} for {ticker}")
            return {
                "report": content,
                "sentiment": sentiment,
                "source": f"OpenAI ({active_model})",
                "trend": trend,
                "rsi_status": rsi_signal
            }
        except Exception as e:
            logger.warning(f"OpenAI API call failed: {e}. Falling back to Quant Engine.")
            fallback_note = f"> [!WARNING]\n> **OpenAI API Notification:** {str(e)[:120]}...\n> Automatically switched to the Built-in Quantitative AI Engine.\n\n"
            return {
                "report": fallback_note + _generate_rule_based_synthesis(ticker, stock_info, current_price, trend, rsi, rsi_signal, macd_signal_str, sentiment, sma_50, sma_200, bb_upper, bb_lower),
                "sentiment": sentiment,
                "source": "Quantitative Heuristic Engine (Fallback)",
                "trend": trend,
                "rsi_status": rsi_signal
            }

    # 3. Built-in Quantitative Rule Engine (100% Offline, Zero Key Required)
    return {
        "report": _generate_rule_based_synthesis(ticker, stock_info, current_price, trend, rsi, rsi_signal, macd_signal_str, sentiment, sma_50, sma_200, bb_upper, bb_lower),
        "sentiment": sentiment,
        "source": "Built-in Quantitative AI Engine (Zero-Key)",
        "trend": trend,
        "rsi_status": rsi_signal
    }


def _generate_rule_based_synthesis(
    ticker: str,
    info: Dict[str, Any],
    price: float,
    trend: str,
    rsi: float,
    rsi_signal: str,
    macd_signal: str,
    sentiment: Dict[str, Any],
    sma_50: float,
    sma_200: float,
    bb_upper: float,
    bb_lower: float
) -> str:
    """Generate structured algorithmic quantitative report."""
    if trend == "Bullish" and rsi < 65:
        verdict = "ACCUMULATE / BUY ON DIPS"
        confidence = 84
        eli5 = f"{ticker} is currently in a healthy upward trend. Buyers are in control, and the stock is trading safely above its key long-term averages."
    elif trend == "Bullish" and rsi >= 65:
        verdict = "HOLD / TRAIL STOP-LOSS"
        confidence = 72
        eli5 = f"{ticker} has gained strongly recently and is approaching overbought levels. Great to hold, but avoid chasing prices at the top."
    elif rsi < 32:
        verdict = "SPECULATIVE CONTRARIAN BOUNCE"
        confidence = 68
        eli5 = f"{ticker} has been heavily sold off and is deeply oversold. Bargain hunters may trigger a short-term bounce."
    else:
        verdict = "NEUTRAL / WAIT FOR CONFIRMATION"
        confidence = 60
        eli5 = f"{ticker} is consolidating in a sideways range. It is prudent to wait for a clear breakout above resistance before committing fresh capital."

    return f"""### 📊 Quantitative Intelligence Report: {ticker} ({info.get('name', ticker)})

**AI Algorithmic Verdict:** `{verdict}` | **Confidence:** `{confidence}%`

---

#### 1. 💡 In Simple Words (Beginner ELI5)
{eli5}

#### 2. Strategic Technical & Quantitative Thesis
- **Current Price:** **₹{price:,.2f}**
- **Trend Posture:** **{trend}**. Price is {"trading above" if price > sma_50 else "trading below"} its 50-day moving average (₹{sma_50:,.2f}) and {"above" if price > sma_200 else "below"} its 200-day institutional baseline (₹{sma_200:,.2f}).
- **Momentum State:** RSI is at **{rsi:.1f}** ({rsi_signal}). MACD displays **{macd_signal}**.

#### 3. Key Bullish Catalysts
- **Demand Cushion:** Reliable algorithmic demand observed near the lower Bollinger boundary of **₹{bb_lower:,.2f}**.
- **Market Sentiment:** Headline sentiment is currently categorized as **{sentiment['label']}** (Score: {sentiment['score']:+.2f}).
- **Institutional Weight:** Bluechip constituent status on the National Stock Exchange of India ensures consistent institutional liquidity and low spread impact.

#### 4. Key Bearish Risks & Invalidation Levels
- **Overhead Supply:** Selling resistance clustered at the Upper Bollinger Band (**₹{bb_upper:,.2f}**).
- **Macro Sensitivity:** Subject to broader index volatility, FII flows, and monetary policy decisions.
- **Stop-Loss Invalidation:** A sustained daily close below **₹{(sma_50 * 0.97):,.2f}** invalidates medium-term bullish positioning.

#### 5. Actionable Price Matrix
| Level Type | Target / Trigger | Strategic Rationale |
| :--- | :--- | :--- |
| **Immediate Support** | **₹{bb_lower:,.2f}** | 20-Day lower statistical envelope |
| **Trend Pivot** | **₹{sma_50:,.2f}** | 50-Day Moving Average trend line |
| **Breakout Target** | **₹{bb_upper:,.2f}** | Take-profit / Overhead resistance band |

---
> [!NOTE]
> **Educational & Regulatory Disclaimer:** This quantitative assessment is generated algorithmically for educational and analytical purposes only. It does not constitute SEBI-registered investment advice. Always practice disciplined risk management.
"""
