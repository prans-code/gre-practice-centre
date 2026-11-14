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


CHECKS = {}  # filled from tools/checks/*.py


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


if __name__ != "__main__":  # the runner below goes through build, which imports this module by name
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
    out = build.verify_quant.verify(tests)
    print("\n".join(out) or f"all {len(build.verify_quant.CHECKS)} quant checks agree")
