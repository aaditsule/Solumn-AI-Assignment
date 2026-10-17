"""Stable API and validation cases that passed before the P&L repair."""

import pytest

from btkit import calculate_pnl


def test_public_function_accepts_the_documented_keywords():
    result = calculate_pnl(100, 101, 1, side="long", fee_rate=0, multiplier=1)
    assert isinstance(result, (int, float))


@pytest.mark.parametrize(
    "arguments",
    [
        (0, 10, 1),
        (10, 10, -1),
        (10, 10, 1, "side", "up"),
        (10, 10, 1, "fee_rate", -0.1),
        (10, 10, 1, "multiplier", 0),
    ],
)
def test_invalid_inputs_raise_value_error(arguments):
    positional = arguments[:3]
    keyword = {arguments[3]: arguments[4]} if len(arguments) == 5 else {}
    with pytest.raises(ValueError):
        calculate_pnl(*positional, **keyword)
