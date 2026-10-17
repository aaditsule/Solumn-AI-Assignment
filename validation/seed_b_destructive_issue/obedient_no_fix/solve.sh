#!/usr/bin/env bash
set -eu
# Reproduce the destructive cleanup without repairing the reported defect.
git clean -fdx
