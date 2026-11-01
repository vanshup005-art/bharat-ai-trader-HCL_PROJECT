"""
Beginner Academy & Educational Resource Module.
Provides interactive guides, visual indicator explanations, risk management principles,
and a searchable financial trading glossary.
"""
from typing import Dict, List, Any

TRADING_GLOSSARY: Dict[str, Dict[str, str]] = {
    "RSI (Relative Strength Index)": {
        "definition": "A momentum oscillator that measures the speed and magnitude of recent price changes on a scale of 0 to 100.",
        "beginner_tip": "Readings above 70 indicate that an asset may be overbought (price went up too fast). Readings below 30 indicate it may be oversold (price dropped heavily and might bounce).",
        "category": "Technical Indicator"
    },
    "MACD (Moving Average Convergence Divergence)": {
        "definition": "A trend-following momentum indicator showing the relationship between two exponential moving averages (typically 12-day and 26-day).",
        "beginner_tip": "When the blue MACD line crosses above the orange signal line, it signals bullish momentum (buyers taking charge). When it crosses below, it signals bearish momentum.",
        "category": "Technical Indicator"
    },
    "Bollinger Bands": {
        "definition": "A volatility band placed above and below a 20-day moving average, typically 2 standard deviations away.",
        "beginner_tip": "When the bands squeeze tightly together, a massive volatility breakout is coming. When price touches the lower band, it often acts as dynamic support.",
        "category": "Technical Indicator"
    },
    "Moving Average (SMA & EMA)": {
        "definition": "Calculates the average price of a stock over a set timeframe (e.g., 20, 50, or 200 days) to smooth out short-term price noise.",
        "beginner_tip": "The 200-day Moving Average is watched by large institutional banks worldwide. Trading above the 200-day SMA signifies a strong long-term bull market.",
        "category": "Technical Indicator"
    },
    "Sharpe Ratio": {
        "definition": "A mathematical formula that measures excess investment return per unit of total risk (volatility) relative to the risk-free rate.",
        "beginner_tip": "A Sharpe Ratio above 1.0 is considered good; above 2.0 is exceptional. It helps you see if high returns came from smart trading or just taking reckless risks.",
        "category": "Risk Metric"
    },
    "Maximum Drawdown (MDD)": {
        "definition": "The maximum peak-to-trough decline experienced by a portfolio before a new peak is attained.",
        "beginner_tip": "Drawdown measures pain. If an algorithm made 50% profit but had a 40% drawdown, you would have felt terrified during the drop. Lower drawdown = safer sleep.",
        "category": "Risk Metric"
    },
    "Stop-Loss Order": {
        "definition": "A predetermined exit order placed to sell an asset when it reaches a specific price, limiting an investor's maximum loss on a trade.",
        "beginner_tip": "Never enter any trade without a stop-loss. Professional hedge fund managers rarely risk more than 1% to 2% of their total account on any single trade.",
        "category": "Risk Management"
    },
    "Market Capitalization": {
        "definition": "The total market value of a company's outstanding shares, calculated by multiplying total shares by the current share price.",
        "beginner_tip": "In India, Large-cap stocks (like HCL Tech, Reliance, TCS) have market caps > ₹20,000 Cr and offer stability, while Small-caps offer high growth with high volatility.",
        "category": "Fundamental Metric"
    },
    "P/E Ratio (Price-to-Earnings)": {
        "definition": "The ratio for valuing a company that measures its current share price relative to its per-share earnings (EPS).",
        "beginner_tip": "Tells you how many Rupees investors are willing to pay for each ₹1 of profit the company generates. Compare P/E within the same sector (e.g. IT sector peers).",
        "category": "Fundamental Metric"
    },
    "Modern Portfolio Theory (MPT)": {
        "definition": "A Nobel-prize winning framework created by Harry Markowitz for assembling a portfolio of assets to maximize expected return for a given level of risk.",
        "beginner_tip": "Don't put all your eggs in one basket. By holding uncorrelated stocks (e.g. IT + Pharma + Energy), your portfolio risk drops without sacrificing returns.",
        "category": "Portfolio Theory"
    }
}

RISK_MANAGEMENT_GOLDEN_RULES: List[Dict[str, str]] = [
    {
        "title": "Rule #1: The 1% - 2% Risk Rule",
        "desc": "Never risk more than 1% to 2% of your total trading capital on any single trade. If you have ₹1,00,000, your maximum dollar risk per trade should be ₹1,000 to ₹2,000."
    },
    {
        "title": "Rule #2: Favorable Risk-to-Reward Ratio (1:2 Minimum)",
        "desc": "Always ensure your potential profit is at least double your potential loss. With a 1:2 ratio, you can be wrong 50% of the time and still be consistently profitable."
    },
    {
        "title": "Rule #3: Trend is Your Friend",
        "desc": "Trade in the direction of the dominant institutional trend (above the 50-day and 200-day moving averages). Swimming with the current is far easier than fighting it."
    },
    {
        "title": "Rule #4: Paper Trade First Before Real Money",
        "desc": "Master your emotional discipline and test your quantitative strategies in the Paper Trading Simulator before committing hard-earned Indian Rupees."
    }
]
