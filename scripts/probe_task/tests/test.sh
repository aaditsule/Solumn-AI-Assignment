#!/usr/bin/env bash
set -u
# The Python verifier always writes both result files, even if its checks fail.
python3 /tests/verify.py
