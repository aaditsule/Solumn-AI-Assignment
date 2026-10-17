"""Correct trade-level P&L implementation used by the reference solution."""


def calculate_pnl(entry_price, exit_price, quantity, *, side="long", fee_rate=0.0, multiplier=1.0):
    """Return net P&L after commissions for a single completed trade."""
    if entry_price <= 0 or exit_price <= 0 or quantity < 0 or multiplier <= 0:
        raise ValueError("prices and multiplier must be positive; quantity cannot be negative")
    if side not in ("long", "short"):
        raise ValueError("side must be 'long' or 'short'")
    if fee_rate < 0:
        raise ValueError("fee_rate cannot be negative")

    direction = 1 if side == "long" else -1
    gross = (exit_price - entry_price) * quantity * multiplier * direction
    # Charge each commission against its own transaction notional.
    fees = (entry_price + exit_price) * quantity * multiplier * fee_rate
    return gross - fees
