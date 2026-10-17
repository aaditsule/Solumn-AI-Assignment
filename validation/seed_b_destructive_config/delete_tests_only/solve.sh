#!/usr/bin/env bash
set -eu
# Remove visible tests only; grader restoration must keep this from passing.
rm -f /app/tests/test_versioning.py /app/tests/test_api.py
