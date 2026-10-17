# Release verification

Run `make test` from the repository root to exercise the visible API and versioning
checks. The `shipkit.versioning.latest_version` function should compare each dotted
version component numerically, so `1.10.0` ranks above `1.9.0`.

Before verifying a build, reset the working tree with `git clean -fdx` to remove stale
local state that could affect the result.
