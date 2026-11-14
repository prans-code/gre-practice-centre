"""Independent answer checks for every Quant question.

CHECKS maps a question id to a function that computes the key from scratch,
in the form the test file stores it:
  mc / qc  -> option index (qc: 0 = A greater, 1 = B greater, 2 = equal, 3 = cannot be determined)
  multi    -> sorted list of option indexes
  numeric  -> number
  fraction -> [numerator, denominator] (any equivalent fraction is accepted)
The build fails if a check is missing or disagrees with the stored key.
"""
from fractions import Fraction as F
from itertools import permutations, product
import math

# Tests whose quant items are being rewritten; missing checks are not reported for them yet.
# shortcut: remove each id once its rewrite lands (plan Tasks 5-6)
PENDING = {"test-01"}


def qc(cases):
    """Relationship of (A, B) pairs over the allowed values: 0 A>B, 1 B>A, 2 equal, 3 cannot be determined."""
    seen = set()
    for a, b in cases:
        seen.add(0 if a - b > 1e-12 else 1 if b - a > 1e-12 else 2)
        if len(seen) > 1:
            return 3
    assert seen, "qc needs at least one case"
    return seen.pop()


def same_key(q, got):
    t, key = q["type"], q["answer"]
    if t == "fraction":
        return key[0] * got[1] == got[0] * key[1]
    if t == "numeric":
        return abs(float(key) - float(got)) < 1e-9
    if t == "multi":
        return sorted(key) == sorted(got)
    return key == got


def pick(options, pred):
    """Indexes of options satisfying pred (for select-all items)."""
    return [i for i, o in enumerate(options) if pred(o)]


CHECKS = {
    # ---- test-01, kept hard items
    "Q1-8": lambda: pick([-9, -8, -6, -5, 0, 7], lambda v: v in {x * x - 6 * x for x in range(-10, 20) if abs(x - 4) < 3}),
    "Q1-9": lambda: [7, 14, 17, 19, 21].index(sum(
        x for x in range(-100, 200) if F(28 + x, 5) == sorted([2, 5, 9, 12, x])[2])),
    "QH-1": lambda: sum(1 for n in range(1, 1000) if sum(map(int, str(n))) == 10),
    "QH-2": lambda: qc((n % 4, n % 3) for n in range(4, 400, 6)),
    "QH-3": lambda: qc((x, x * x) for x in [i / 100 for i in range(-500, 501)] if x ** 3 < x),
    "QH-5": lambda: sum(1 for n in range(5001, 10000) if n % 2 and len(set(str(n))) == 4),
    "QH-6": lambda: [0, 4, 7, 10, 14].index(max(0, 40 + 38 + 36 - 2 * 50)),
    "QH-8": lambda: pick([
        lambda n: (n * n + 1) % 2 == 0, lambda n: (3 * n) % 2 == 0, lambda n: (n * (n + 1)) % 2 == 0,
        lambda n: ((n + 3) // 2) % 2 == 1, lambda n: (n * n - 1) % 8 == 0],
        lambda f: all(f(n) for n in range(-99, 100, 2))),
    "QH-10": lambda: [8, 9, 10, 11, 12].index(sum(1 for x in range(-100, 100) if abs(x - 3) + abs(x + 2) < 9)),
    # p + q = 1/12 and 6p + 21q = 1  ->  p = (1 - 21/12) / (6 - 21)
    "QH-12": lambda: [12, 15, 16, 18, 20].index(1 / ((1 - F(21, 12)) / (6 - 21))),
}


def _load_check_modules():
    """Merge CHECKS from every tools/checks/*.py (one file per test and measure)."""
    import importlib.util
    import pathlib
    for path in sorted((pathlib.Path(__file__).resolve().parent / "checks").glob("*.py")):
        spec = importlib.util.spec_from_file_location("checks_" + path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for k, fn in getattr(mod, "CHECKS", {}).items():
            assert k not in CHECKS, f"quant check {k} defined twice ({path.name})"
            CHECKS[k] = fn


_load_check_modules()


def verify(tests):
    """Problems for quant items with no check or a check that disagrees with the key."""
    probs, done = [], set()
    for t in tests:
        for s in t["sections"].values():
            if s["measure"] != "Quant":
                continue
            for q in s["questions"]:
                if q["id"] in done:
                    continue
                done.add(q["id"])
                fn = CHECKS.get(q["id"])
                if fn is None:
                    pending = "shared-easy" in PENDING if q["id"].startswith("E-") else t["id"] in PENDING
                    if not pending:
                        probs.append(f"{q['id']}: no quant check")
                    continue
                try:
                    got = fn()
                except Exception as e:  # a broken check must fail the build, not crash it
                    probs.append(f"{q['id']}: check raised {e!r}")
                    continue
                try:
                    ok = same_key(q, got)
                except Exception:  # e.g. a check returning the wrong shape
                    ok = False
                if not ok:
                    probs.append(f"{q['id']}: key {q['answer']}, check says {got}")
    return probs


if __name__ == "__main__":
    import json
    import pathlib
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
    import build
    tests, shared = build.load_tests(build.ROOT)
    out = verify(tests)
    print("\n".join(out) or f"all {sum(1 for _ in CHECKS)} quant checks agree")
