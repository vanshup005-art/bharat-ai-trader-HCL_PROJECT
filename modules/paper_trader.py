"""
Paper Trading Simulation Engine for Indian Equities.
Maintains persistent portfolio state, order logs, and live mark-to-market valuations
with atomic file locking and strict parameter validation.
"""
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any

from utils.security import (
    validate_order_params, atomic_write_json, safe_read_json
)
from utils.logger import get_logger
from config.settings import DEFAULT_INITIAL_PAPER_CAPITAL

logger = get_logger()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
PORTFOLIO_FILE = os.path.join(DATA_DIR, "paper_portfolio.json")


def get_default_portfolio(initial_capital: float = DEFAULT_INITIAL_PAPER_CAPITAL) -> Dict[str, Any]:
    """Generate default initial portfolio structure."""
    return {
        "cash_balance": float(initial_capital),
        "initial_capital": float(initial_capital),
        "holdings": {},  # symbol -> {"quantity": int, "avg_cost": float}
        "realized_pnl": 0.0,
        "orders": []
    }


def load_paper_portfolio() -> Dict[str, Any]:
    """Load portfolio state safely with corruption recovery."""
    return safe_read_json(PORTFOLIO_FILE, get_default_portfolio())


def save_paper_portfolio(portfolio: Dict[str, Any]) -> bool:
    """Persist portfolio state atomically."""
    return atomic_write_json(PORTFOLIO_FILE, portfolio)


def reset_paper_portfolio(initial_capital: float = DEFAULT_INITIAL_PAPER_CAPITAL) -> Dict[str, Any]:
    """Reset paper account balance and clear trade history."""
    portfolio = get_default_portfolio(initial_capital)
    save_paper_portfolio(portfolio)
    logger.info(f"Reset paper portfolio with capital ₹{initial_capital:,.2f}")
    return portfolio


def execute_paper_order(
    symbol: str,
    action: str,  # "BUY" or "SELL"
    quantity: int,
    current_price: float
) -> Tuple[bool, str]:
    """
    Execute simulated market order with rigorous security validation
    and atomic persistence.
    """
    portfolio = load_paper_portfolio()
    cash = float(portfolio.get("cash_balance", 0.0))
    curr_holding = portfolio.get("holdings", {}).get(symbol, {"quantity": 0, "avg_cost": 0.0})
    curr_shares = int(curr_holding.get("quantity", 0))

    # Validate parameters
    is_valid, validation_msg = validate_order_params(
        action=action,
        quantity=quantity,
        price=current_price,
        cash_balance=cash,
        current_shares=curr_shares
    )
    if not is_valid:
        return False, validation_msg

    qty = int(quantity)
    price = float(current_price)
    total_cost = round(qty * price, 2)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if action == "BUY":
        portfolio["cash_balance"] = round(cash - total_cost, 2)
        total_shares = curr_shares + qty
        new_avg = round(((curr_shares * curr_holding["avg_cost"]) + total_cost) / total_shares, 2)

        portfolio["holdings"][symbol] = {
            "quantity": total_shares,
            "avg_cost": new_avg
        }

        order_record = {
            "timestamp": timestamp,
            "symbol": symbol,
            "action": "BUY",
            "quantity": qty,
            "price": round(price, 2),
            "total_value": total_cost,
            "status": "FILLED"
        }
        portfolio["orders"].append(order_record)
        save_paper_portfolio(portfolio)
        logger.info(f"Executed BUY {qty} {symbol} @ ₹{price:,.2f}")
        return True, f"Successfully executed BUY of {qty} shares of {symbol} at ₹{price:,.2f} (Total: ₹{total_cost:,.2f})."

    elif action == "SELL":
        cost_basis = qty * curr_holding["avg_cost"]
        trade_pnl = round(total_cost - cost_basis, 2)

        portfolio["cash_balance"] = round(cash + total_cost, 2)
        portfolio["realized_pnl"] = round(float(portfolio.get("realized_pnl", 0.0)) + trade_pnl, 2)
        remaining_qty = curr_shares - qty

        if remaining_qty == 0:
            portfolio["holdings"].pop(symbol, None)
        else:
            portfolio["holdings"][symbol]["quantity"] = remaining_qty

        order_record = {
            "timestamp": timestamp,
            "symbol": symbol,
            "action": "SELL",
            "quantity": qty,
            "price": round(price, 2),
            "total_value": total_cost,
            "pnl": trade_pnl,
            "status": "FILLED"
        }
        portfolio["orders"].append(order_record)
        save_paper_portfolio(portfolio)
        logger.info(f"Executed SELL {qty} {symbol} @ ₹{price:,.2f} | PnL: ₹{trade_pnl:+,.2f}")
        return True, f"Successfully executed SELL of {qty} shares of {symbol} at ₹{price:,.2f} (P&L: ₹{trade_pnl:+,.2f})."

    return False, "Unrecognized action."


def get_portfolio_summary(current_prices: Dict[str, float]) -> Dict[str, Any]:
    """Calculate live mark-to-market portfolio statistics."""
    portfolio = load_paper_portfolio()
    cash = float(portfolio.get("cash_balance", 0.0))
    holdings_table = []
    total_stock_value = 0.0
    total_unrealized_pnl = 0.0

    for symbol, data in portfolio.get("holdings", {}).items():
        qty = int(data.get("quantity", 0))
        avg_cost = float(data.get("avg_cost", 0.0))
        market_price = float(current_prices.get(symbol, avg_cost))

        invested = qty * avg_cost
        curr_val = qty * market_price
        unrealized = curr_val - invested
        pct_change = ((market_price - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0.0

        total_stock_value += curr_val
        total_unrealized_pnl += unrealized

        holdings_table.append({
            "Symbol": symbol,
            "Quantity": qty,
            "Avg Price (₹)": round(avg_cost, 2),
            "Current Price (₹)": round(market_price, 2),
            "Invested (₹)": round(invested, 2),
            "Market Value (₹)": round(curr_val, 2),
            "Unrealized P&L (₹)": round(unrealized, 2),
            "Return (%)": round(pct_change, 2)
        })

    total_portfolio_value = cash + total_stock_value
    initial_cap = float(portfolio.get("initial_capital", DEFAULT_INITIAL_PAPER_CAPITAL))
    net_pnl = total_portfolio_value - initial_cap
    total_return_pct = (net_pnl / initial_cap * 100) if initial_cap > 0 else 0.0

    return {
        "cash_balance": round(cash, 2),
        "holdings_value": round(total_stock_value, 2),
        "total_portfolio_value": round(total_portfolio_value, 2),
        "realized_pnl": round(float(portfolio.get("realized_pnl", 0.0)), 2),
        "unrealized_pnl": round(total_unrealized_pnl, 2),
        "net_pnl": round(net_pnl, 2),
        "total_return_pct": round(total_return_pct, 2),
        "holdings": holdings_table,
        "recent_orders": list(reversed(portfolio.get("orders", [])))[:20]
    }
