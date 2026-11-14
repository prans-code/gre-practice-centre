"""Fixture for tools/test_build.py: proves check modules in this folder are loaded."""
from verify_quant import qc

CHECKS = {"SELFTEST-1": lambda: qc([(1, 2), (2, 1)])}
