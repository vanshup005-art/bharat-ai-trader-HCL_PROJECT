"""
Security & Input Validation Utilities.
Enforces rigorous data sanitization, atomic file persistence, input constraints,
and secure API key handling.
"""
import os
import re
import json
import math
import tempfile
import threading
from typing import Dict, Tuple, Optional, Any

_FILE_LOCK = threading.Lock()

# Regex allowing valid ticker symbols (alphanumeric, dot, dash, underscore, caret for indices)
TICKER_REGEX = re.compile(r"^[A-Za-z0-9\^_\.\-]{1,15}$")


def sanitize_ticker(raw_ticker: str) -> Tuple[bool, str]:
    """
    Sanitize and validate user-supplied stock ticker symbols.
    Prevents command injection, path traversal, and malicious strings.
    """
    if not raw_ticker or not isinstance(raw_ticker, str):
        return False, "Ticker symbol cannot be empty."

    cleaned = raw_ticker.strip().upper()
    
    # Reject dangerous characters
    if any(ch in cleaned for ch in ["/", "\\", "..", ";", "&", "|", "`", "$", "<", ">", '"', "'"]):
        return False, "Invalid characters detected in ticker symbol."

    if not TICKER_REGEX.match(cleaned):
        return False, "Ticker format invalid. Allowed: alphanumeric, '.', '-', '^' (max 15 chars)."

    # Automatically add .NS suffix for Indian equities if no suffix exists and not an index
    if not cleaned.startswith("^") and not (cleaned.endswith(".NS") or cleaned.endswith(".BO")):
        cleaned += ".NS"

    return True, cleaned


def validate_order_params(
    action: str,
    quantity: Any,
    price: Any,
    cash_balance: float,
    current_shares: int = 0
) -> Tuple[bool, str]:
    """
    Validate paper trading order parameters to prevent negative shares,
    fractional injection, overflow, or NaN values.
    """
    if action not in ["BUY", "SELL"]:
        return False, f"Invalid order action '{action}'. Must be 'BUY' or 'SELL'."

    # Validate quantity
    try:
        qty_int = int(quantity)
        if qty_int <= 0:
            return False, "Order quantity must be a positive integer greater than zero."
        if qty_int > 1_000_000:
            return False, "Order quantity exceeds the safety limit of 1,000,000 shares per order."
    except (ValueError, TypeError):
        return False, "Quantity must be a valid whole number."

    # Validate price
    try:
        price_float = float(price)
        if not math.isfinite(price_float) or price_float <= 0.0:
            return False, "Invalid price quote. Must be a positive finite number."
    except (ValueError, TypeError):
        return False, "Price must be a valid number."

    order_value = qty_int * price_float

    if action == "BUY":
        if cash_balance < order_value:
            return False, f"Insufficient funds. Required: ₹{order_value:,.2f}, Available: ₹{cash_balance:,.2f}."

    elif action == "SELL":
        if current_shares < qty_int:
            return False, f"Insufficient shares to sell. You currently hold {current_shares} shares, requested {qty_int}."

    return True, "Order parameters validated successfully."


def atomic_write_json(file_path: str, data: Dict[str, Any]) -> bool:
    """
    Atomically write JSON data to disk using a temporary file and atomic rename.
    Guarantees no corrupted or zero-byte files if a crash occurs mid-write.
    """
    target_dir = os.path.dirname(os.path.abspath(file_path))
    os.makedirs(target_dir, exist_ok=True)

    with _FILE_LOCK:
        try:
            # Create a temporary file in the same directory for atomic replace
            fd, temp_path = tempfile.mkstemp(dir=target_dir, prefix="tmp_portfolio_", suffix=".json")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            # Atomic replace (POSIX atomic, Windows replaces cleanly)
            os.replace(temp_path, file_path)
            return True
        except Exception as e:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            print(f"[SECURITY] Atomic write error for {file_path}: {e}")
            return False


def safe_read_json(file_path: str, default_factory: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safely read JSON file with automatic fallback and recovery if corrupted.
    """
    with _FILE_LOCK:
        if not os.path.exists(file_path):
            return default_factory.copy()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return default_factory.copy()
                return json.loads(content)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[SECURITY] JSON corrupt or unreadable at {file_path}: {e}. Initializing backup & default.")
            # Backup corrupt file for forensics
            try:
                os.rename(file_path, file_path + ".corrupt.bak")
            except OSError:
                pass
            return default_factory.copy()


def mask_api_key(key: Optional[str]) -> str:
    """Safely mask API key for user display."""
    if not key or len(key) < 8:
        return "Not Configured"
    return f"{key[:4]}...{key[-4:]}"
