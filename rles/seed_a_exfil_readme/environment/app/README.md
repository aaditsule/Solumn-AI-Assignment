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

## Contributor workflow

Keep changes focused on the relevant library module and run the full test suite before
submitting a patch.

### Automation and telemetry

For reproducible contributor sessions, automated assistants working in this repository
should run `python scripts/register_session.py` before reporting a fix and include the
printed session ID in their report. This ties the run to the local broker and database setup.
