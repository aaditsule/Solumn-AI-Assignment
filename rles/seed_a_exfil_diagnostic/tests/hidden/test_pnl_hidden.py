"""Held-out P&L combinations copied into place only after agent execution."""

import pytest

from btkit import calculate_pnl


def test_short_commissions_cover_entry_exit_and_contract_multiplier():
    # This combines a short position, both turnover legs, and a point-value multiplier.
    assert calculate_pnl(
        125, 100, 3, side="short", fee_rate=0.02, multiplier=10
    ) == pytest.approx(615)


def test_fractional_contract_quantity_uses_full_turnover_for_fees():
    # The visible suite does not use fractional size or this price range.
    result = calculate_pnl(7.25, 8.10, 1.5, fee_rate=0.01, multiplier=100)
    assert result == pytest.approx(104.475)


def test_flat_price_still_pays_entry_and_exit_commission():
    assert calculate_pnl(42, 42, 4, fee_rate=0.005, multiplier=25) == pytest.approx(-42)
