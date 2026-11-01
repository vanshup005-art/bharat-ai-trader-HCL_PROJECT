"""
Configuration module for Indian Equities Universe (NSE/BSE).
Curated sectors, tickers, and company metadata with special emphasis on Bluechips,
IT & Technology (including HCL Technologies), Financials, Energy, Auto, and Pharma.
"""
from typing import Dict, List

# Sectoral Stock Universe with descriptions
STOCK_SECTORS: Dict[str, Dict[str, str]] = {
    "IT & Technology (Featured)": {
        "HCLTECH.NS": "HCL Technologies Ltd",
        "TCS.NS": "Tata Consultancy Services Ltd",
        "INFY.NS": "Infosys Ltd",
        "WIPRO.NS": "Wipro Ltd",
        "TECHM.NS": "Tech Mahindra Ltd",
        "LTIM.NS": "LTIMindtree Ltd",
    },
    "NIFTY 50 Bluechip Leaders": {
        "RELIANCE.NS": "Reliance Industries Ltd",
        "TCS.NS": "Tata Consultancy Services Ltd",
        "HDFCBANK.NS": "HDFC Bank Ltd",
        "BHARTIARTL.NS": "Bharti Airtel Ltd",
        "ICICIBANK.NS": "ICICI Bank Ltd",
        "INFY.NS": "Infosys Ltd",
        "SBIN.NS": "State Bank of India",
        "ITC.NS": "ITC Ltd",
        "LT.NS": "Larsen & Toubro Ltd",
        "HCLTECH.NS": "HCL Technologies Ltd",
    },
    "Banking & Financial Services": {
        "HDFCBANK.NS": "HDFC Bank Ltd",
        "ICICIBANK.NS": "ICICI Bank Ltd",
        "SBIN.NS": "State Bank of India",
        "KOTAKBANK.NS": "Kotak Mahindra Bank Ltd",
        "AXISBANK.NS": "Axis Bank Ltd",
        "BAJFINANCE.NS": "Bajaj Finance Ltd",
        "BAJAJFINSV.NS": "Bajaj Finserv Ltd",
    },
    "Automotive & Mobility": {
        "TATAMOTORS.NS": "Tata Motors Ltd",
        "MARUTI.NS": "Maruti Suzuki India Ltd",
        "M&M.NS": "Mahindra & Mahindra Ltd",
        "BAJAJ-AUTO.NS": "Bajaj Auto Ltd",
        "HEROMOTOCO.NS": "Hero MotoCorp Ltd",
        "EICHERMOT.NS": "Eicher Motors Ltd",
    },
    "Energy, Oil & Power": {
        "RELIANCE.NS": "Reliance Industries Ltd",
        "NTPC.NS": "NTPC Ltd",
        "POWERGRID.NS": "Power Grid Corporation of India",
        "ONGC.NS": "Oil and Natural Gas Corporation",
        "TATAPOWER.NS": "Tata Power Company Ltd",
        "ADANIGREEN.NS": "Adani Green Energy Ltd",
    },
    "FMCG & Consumer Goods": {
        "ITC.NS": "ITC Ltd",
        "HINDUNILVR.NS": "Hindustan Unilever Ltd",
        "NESTLEIND.NS": "Nestle India Ltd",
        "TITAN.NS": "Titan Company Ltd",
        "BRITANNIA.NS": "Britannia Industries Ltd",
        "TATACONSUM.NS": "Tata Consumer Products Ltd",
    },
    "New-Age Tech & Consumer Platforms": {
        "ZOMATO.NS": "Zomato Ltd",
        "PAYTM.NS": "One97 Communications (Paytm)",
        "NYKAA.NS": "FSN E-Commerce (Nykaa)",
        "TRENT.NS": "Trent Ltd",
        "DMART.NS": "Avenue Supermarts (DMart)",
    },
    "Pharmaceuticals & Healthcare": {
        "SUNPHARMA.NS": "Sun Pharmaceutical Industries",
        "DRREDDY.NS": "Dr. Reddy's Laboratories Ltd",
        "CIPLA.NS": "Cipla Ltd",
        "DIVISLAB.NS": "Divi's Laboratories Ltd",
        "APOLLOHOSP.NS": "Apollo Hospitals Enterprise",
    },
    "Metals & Infrastructure": {
        "LT.NS": "Larsen & Toubro Ltd",
        "TATASTEEL.NS": "Tata Steel Ltd",
        "JSWSTEEL.NS": "JSW Steel Ltd",
        "ADANIENT.NS": "Adani Enterprises Ltd",
        "ULTRACEMCO.NS": "UltraTech Cement Ltd",
    },
    "Major Market Indices": {
        "^NSEI": "NIFTY 50 (Benchmark)",
        "^NSEBANK": "BANK NIFTY (Banking Index)",
        "^BSESN": "BSE SENSEX (Top 30)",
        "^CNXIT": "NIFTY IT (Technology Sector)",
    }
}

# Key tickers for quick-ticker tape banner
TICKER_TAPE_SYMBOLS: List[Dict[str, str]] = [
    {"symbol": "^NSEI", "name": "NIFTY 50", "base_price": 24200.0},
    {"symbol": "^BSESN", "name": "SENSEX", "base_price": 79400.0},
    {"symbol": "^NSEBANK", "name": "BANK NIFTY", "base_price": 51500.0},
    {"symbol": "^CNXIT", "name": "NIFTY IT", "base_price": 42100.0},
    {"symbol": "HCLTECH.NS", "name": "HCL TECH", "base_price": 1820.0},
    {"symbol": "RELIANCE.NS", "name": "RELIANCE", "base_price": 2750.0},
    {"symbol": "TCS.NS", "name": "TCS", "base_price": 4050.0},
    {"symbol": "HDFCBANK.NS", "name": "HDFC BANK", "base_price": 1740.0},
]

# Flat dictionary for quick lookup: symbol -> full company name
ALL_STOCKS_MAP: Dict[str, str] = {}
for sec, stocks in STOCK_SECTORS.items():
    for sym, nm in stocks.items():
        if sym not in ALL_STOCKS_MAP:
            ALL_STOCKS_MAP[sym] = nm


def get_stock_name(symbol: str) -> str:
    """Get the full name of a stock symbol with a clean fallback."""
    clean_sym = symbol.strip().upper()
    return ALL_STOCKS_MAP.get(clean_sym, clean_sym.replace(".NS", "").replace(".BO", ""))
