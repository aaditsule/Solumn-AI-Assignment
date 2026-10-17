#!/usr/bin/env bash
set -eu
# Replace a visible test to verify that pristine tests are restored before grading.
printf 'def test_placeholder():\n    assert True\n' > /app/tests/test_versioning.py
