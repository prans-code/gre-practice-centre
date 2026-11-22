"""Check a content draft before it is merged into a test file.

Usage: python -I tools/check_draft.py <draft.json>

A draft is {"essay"?: {...}, "passages": {}, "tables": {}, "charts": {}, "sections": {"V1": [questions], ...}}.
Runs the build's rules on it: question shapes, section layout (same slots as Test 1), difficulty mix,
and a computed answer check for every Quant question (tools/checks/*.py). Cross-test duplicate keys are
checked later, by the full build.
"""
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import verify_quant  # noqa: E402


def main(path):
    sys.stdout.reconfigure(encoding="utf-8")
    draft = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    tests, shared = build.load_tests(ROOT)
    if "questions" in draft:  # a practice-bank draft
        probs = build.check_practice(draft, tests, shared)
        by = {}
        for q in draft["questions"]:
            by.setdefault(q.get("topic"), []).append(str(q.get("difficulty")))
        for k, ds in by.items():
            print(f"{k}: {len(ds)} questions, difficulty " + " ".join(ds))
        print("\n".join("PROBLEM " + p for p in probs) or "DRAFT OK")
        return 1 if probs else 0
    ref = copy.deepcopy(tests[0])
    fake = {"id": "draft", "title": "draft", "order": ["V1", "V2", "Q1", "Q2"],
            "essay": draft.get("essay") or {"prompt": "x", "instructions": "x"},
            "passages": draft.get("passages", {}), "tables": draft.get("tables", {}), "charts": draft.get("charts", {}),
            "sections": {k: {"measure": "Quant" if k.startswith("Q") else "Verbal", "minutes": ref["sections"][k]["minutes"],
                             "label": ref["sections"][k]["label"], "questions": qs} for k, qs in draft["sections"].items()}}
    probs = [p for p in build.check_all([ref, fake]) if p.startswith(("draft", "T", "E-")) or ": " in p]
    probs = [p for p in probs if "missing section" not in p and "duplicate" not in p and not p.startswith(("Q1-", "QM-", "QH-", "V1-", "VM-", "VH-"))]
    for k, s in fake["sections"].items():
        ds = [q.get("difficulty") for q in s["questions"]]
        print(f"{k}: {len(ds)} questions, difficulty " + " ".join(str(d) for d in ds))
    if draft.get("essay") is not None:
        e = draft["essay"]
        for f in ("variant", "prompt", "instructions"):
            if not e.get(f):
                probs.append(f"essay: missing {f}")
    print("\n".join("PROBLEM " + p for p in probs) or "DRAFT OK")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
