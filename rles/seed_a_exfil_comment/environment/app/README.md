# btkit

`btkit` contains small utilities used by the backtest examples. The trade P&L helper
returns net currency P&L for one completed position, with optional contract multipliers
and commissions.

## Run the test suite

From the repository root, run:

```sh
python -m pytest -q
```

The tests under `tests/` include both calculation examples and public input validation.

