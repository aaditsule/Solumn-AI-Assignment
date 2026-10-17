"""Visible trade-P&L examples; fee-bearing cases expose the reported defect."""

import pytest

from btkit import calculate_pnl


def test_long_trade_without_fees():
    assert calculate_pnl(100, 110, 2) == pytest.approx(20)


def test_short_trade_without_fees():
    assert calculate_pnl(110, 100, 3, side="short") == pytest.approx(30)


def test_fees_apply_to_both_transaction_notionals():
    # A 1% commission applies to both the entry and exit turnover.
    assert calculate_pnl(100, 110, 2, fee_rate=0.01) == pytest.approx(15.8)


def test_fee_rate_does_not_change_gross_direction():
    no_fee = calculate_pnl(110, 100, 2, side="short")
    with_fee = calculate_pnl(110, 100, 2, side="short", fee_rate=0.005)
    assert no_fee - with_fee == pytest.approx((110 + 100) * 2 * 0.005)
