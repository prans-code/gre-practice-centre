"""Build the GRE Practice Centre.

Reads every tests/test-*.json, validates it, shuffles verbal answer options
with a fixed seed (so answer positions are random but stable), adds the
scoring configuration, and writes:
  - src/artifact.html          (published as the private web link)
  - GRE-Practice-Centre.html   (offline copy for this PC)
  - index.html                 (same page, served by GitHub Pages)

Run:  python -I src/build.py
"""
import hashlib
import json
import pathlib
import random
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import verify_quant  # noqa: E402
SECTIONS = {"V1": 12, "V2E": 15, "V2M": 15, "V2H": 15, "Q1": 12, "Q2E": 15, "Q2M": 15, "Q2H": 15}
TYPES = {"tc", "se", "mc", "multi", "sentence", "qc", "numeric", "fraction"}
problems = []


def fail(msg):
    problems.append(msg)


# ---------------------------------------------------------------- scoring
# Assumptions (ETS does not publish these for the shorter test):
#  - three section-2 tiers; routing on section-1 raw score (out of 12)
#  - one conversion shape for Verbal and Quant
#  - medium tier is linear from 130 (0 correct) to 170 (27 correct);
#    harder tier scores up to 4 points more, easier tier up to 4 points less,
#    tapering to zero at the ends (ETS's 2011 example: the same raw score
#    scaled to 146 / 149 / 153 on the easy / medium / hard routes).
ROUTING = {"easierMax": 4, "mediumMax": 8}


def conv(tier, r):
    med = 130 + 40 * r / 27
    if tier == "harder":
        s = med + 4 * min(1, (27 - r) / 13.5)
    elif tier == "easier":
        # easier sections are very easy, so a perfect second section is worth less: tops out near 150
        s = med - 8 * min(1, r / 19)
    else:
        s = med
    return max(130, min(170, int(s + 0.5)))


CONVERSION = {t: [conv(t, r) for r in range(28)] for t in ("easier", "medium", "harder")}
REACH = {"easier": range(0, ROUTING["easierMax"] + 16),
         "medium": range(ROUTING["easierMax"] + 1, ROUTING["mediumMax"] + 16),
         "harder": range(ROUTING["mediumMax"] + 1, 28)}
for t, rng in REACH.items():
    vals = [CONVERSION[t][r] for r in rng]
    if any(b < a for a, b in zip(vals, vals[1:])):
        fail(f"conversion not monotonic for {t}")
for r in range(28):
    if not (CONVERSION["easier"][r] <= CONVERSION["medium"][r] <= CONVERSION["harder"][r]):
        fail(f"tier order broken at raw {r}")
if [r for r in REACH["harder"] if CONVERSION["harder"][r] == 170] != [27] and \
        [r for r in REACH["harder"] if CONVERSION["harder"][r] == 170] != [26, 27]:
    fail("170 must need 26-27 correct on the harder tier")

CONFIG = {
    "routing": ROUTING,
    "conversion": CONVERSION,
    "extraUncertainty": 2,
    "difficultyNames": {"1": "Very easy", "2": "Easy", "3": "Medium", "4": "Hard", "5": "Very hard"},
    # ETS GRE Guide to the Use of Scores 2026-27, Table 1B/1C (tested 1 July 2022 - 30 June 2025)
    "percentiles": {
        "Verbal": {170: 99, 169: 99, 168: 98, 167: 97, 166: 96, 165: 95, 164: 93, 163: 90, 162: 88, 161: 85, 160: 82, 159: 79, 158: 76, 157: 72, 156: 68, 155: 64, 154: 59, 153: 54, 152: 48, 151: 43, 150: 39, 149: 34, 148: 30, 147: 27, 146: 24, 145: 21, 144: 18, 143: 16, 142: 14, 141: 11, 140: 10, 139: 8, 138: 6, 137: 5, 136: 4, 135: 3, 134: 2, 133: 2, 132: 1, 131: 1, 130: 0},
        "Quant": {170: 89, 169: 85, 168: 80, 167: 75, 166: 72, 165: 67, 164: 63, 163: 60, 162: 57, 161: 53, 160: 50, 159: 47, 158: 45, 157: 42, 156: 39, 155: 37, 154: 34, 153: 31, 152: 29, 151: 26, 150: 23, 149: 21, 148: 19, 147: 16, 146: 14, 145: 12, 144: 10, 143: 9, 142: 7, 141: 6, 140: 5, 139: 4, 138: 3, 137: 2, 136: 2, 135: 1, 134: 1, 133: 1, 132: 0, 131: 0, 130: 0},
        "AW": {"6.0": 99, "5.5": 98, "5.0": 93, "4.5": 85, "4.0": 63, "3.5": 40, "3.0": 16, "2.5": 7, "2.0": 3, "1.5": 1, "1.0": 1, "0.5": 0, "0.0": 0},
    },
    # ETS Table 4C: conditional standard error of measurement
    "csem": {"Verbal": [[130, 4.3], [135, 3.9], [140, 3.3], [145, 2.9], [150, 2.7], [155, 2.5], [160, 2.5], [165, 2.6], [170, 1.7]],
             "Quant": [[130, 4.2], [135, 3.6], [140, 3.0], [145, 2.8], [150, 2.7], [155, 2.6], [160, 2.7], [165, 2.5], [170, 1.2]]},
}
# the app uses "Verbal" / "Quant" keys; JSON turns int keys into strings, which JS reads fine


# ---------------------------------------------------------------- tests
def sentences(test, key):
    p = test["passages"].get(key)
    if p is None:
        return None
    return [s for para in p["paragraphs"] for s in para] if isinstance(p, dict) else p


def shuffle_q(q):
    """Shuffle verbal options with a seed from the question id; remap the key."""
    rng = random.Random(int(hashlib.sha256(q["id"].encode()).hexdigest(), 16))
    t = q["type"]
    if t == "tc":
        new_blanks, new_ans = [], []
        for col, a in zip(q["blanks"], q["answer"]):
            order = list(range(len(col)))
            rng.shuffle(order)
            new_blanks.append([col[i] for i in order])
            new_ans.append(order.index(a))
        q["blanks"], q["answer"] = new_blanks, new_ans
    elif t in ("se", "multi", "mc"):
        order = list(range(len(q["options"])))
        rng.shuffle(order)
        q["options"] = [q["options"][i] for i in order]
        q["answer"] = order.index(q["answer"]) if t == "mc" else sorted(order.index(a) for a in q["answer"])


LETTER_REF = re.compile(r"\b(option|choice|answer)\s+\(?[A-F]\)?\b|\([A-E]\)", re.I)


def check_test(test, shared_keys=()):
    tid = test.get("id")
    for k in ("id", "title", "order", "essay", "passages", "sections"):
        if k not in test:
            fail(f"{tid}: missing {k}")
    if sorted(test["order"]) != ["Q1", "Q2", "V1", "V2"] or test["order"].index("V1") > test["order"].index("V2") or test["order"].index("Q1") > test["order"].index("Q2"):
        fail(f"{tid}: bad order {test['order']}")
    test["essay"].setdefault("minutes", 30)
    ids = set()
    for key, n in SECTIONS.items():
        sec = test["sections"].get(key)
        if not sec:
            fail(f"{tid}: missing section {key}")
            continue
        qs = sec["questions"]
        if len(qs) != n:
            fail(f"{tid} {key}: {len(qs)} questions, expected {n}")
        for q in qs:
            qid, t = q.get("id"), q.get("type")
            if qid in ids:
                fail(f"{tid}: duplicate id {qid}")
            ids.add(qid)
            if t not in TYPES:
                fail(f"{qid}: bad type {t}")
                continue
            if q.get("difficulty") not in (1, 2, 3, 4, 5):
                fail(f"{qid}: difficulty missing or invalid")
            for f in ("skill", "explain"):
                if not q.get(f):
                    fail(f"{qid}: missing {f}")
            if sec["measure"] == "Verbal" and LETTER_REF.search(q.get("explain", "")):
                fail(f"{qid}: explanation refers to an option letter (options are shuffled)")
            if t == "tc":
                b = q["blanks"]
                if len(b) == 1 and len(b[0]) != 5 or len(b) > 1 and any(len(c) != 3 for c in b) or len(q["answer"]) != len(b):
                    fail(f"{qid}: text completion shape wrong")
            if t == "se" and (len(q["options"]) != 6 or len(set(q["answer"])) != 2):
                fail(f"{qid}: sentence equivalence needs 6 options and 2 answers")
            if t == "mc" and not 0 <= q["answer"] < len(q["options"]):
                fail(f"{qid}: answer index out of range")
            if t == "multi" and (not q["answer"] or max(q["answer"]) >= len(q["options"])):
                fail(f"{qid}: multi answer out of range")
            if t == "multi" and q.get("passage") and len(q["options"]) != 3:
                fail(f"{qid}: reading select-all must have 3 options")
            if t == "qc" and q["answer"] not in (0, 1, 2, 3):
                fail(f"{qid}: qc answer must be 0-3")
            if q.get("passage") and sentences(test, q["passage"]) is None:
                fail(f"{qid}: unknown passage {q['passage']}")
            if t == "sentence" and not 0 <= q["answer"] < len(sentences(test, q["passage"]) or []):
                fail(f"{qid}: sentence index out of range")
            if q.get("table") and q["table"] not in test.get("tables", {}):
                fail(f"{qid}: unknown table")
            if q.get("chart") and q["chart"] not in test.get("charts", {}):
                fail(f"{qid}: unknown chart")
            if t == "fraction" and (len(q["answer"]) != 2 or q["answer"][1] == 0):
                fail(f"{qid}: fraction answer wrong")
            if sec["measure"] == "Verbal" and key not in shared_keys:
                shuffle_q(q)
    # answer-position spread after shuffling
    pos = [q["answer"] for s in test["sections"].values() for q in s["questions"] if q["type"] == "mc"]
    if pos and max(pos.count(i) for i in set(pos)) > 0.45 * len(pos):
        fail(f"{tid}: single-answer key positions too uneven {sorted(pos)}")
    tc0 = [a == 0 for s in test["sections"].values() for q in s["questions"] if q["type"] == "tc" for a in q["answer"]]
    if tc0 and sum(tc0) > 0.5 * len(tc0):
        fail(f"{tid}: too many text-completion answers in the first position")


def slot_layout(section):
    """One tuple of question types per slot; a slot is a run sharing a passage/table/chart, else one question."""
    slots, last = [], None
    for q in section["questions"]:
        g = q.get("passage") or q.get("table") or q.get("chart")
        if g and g == last:
            slots[-1] = slots[-1] + (q["type"],)
        else:
            slots.append((q["type"],))
        last = g
    return slots


def parse_layout(spec):
    """'qc mc [mc multi]' -> [('qc',), ('mc',), ('mc', 'multi')]; brackets = one passage/table/chart set."""
    slots, group = [], None
    for tok in spec.replace("[", " [ ").replace("]", " ] ").split():
        if tok == "[":
            group = []
        elif tok == "]":
            slots.append(tuple(group))
            group = None
        elif group is not None:
            group.append(tok)
        else:
            slots.append((tok,))
    return slots


# Fixed slot layout of every section, close to the real test: Quant opens with its comparison block and has one
# data set; Verbal is about half reading, with one argument paragraph and one select-the-sentence item per test.
_V2 = "tc tc tc tc se se se se [mc mc multi sentence] [mc multi] [mc]"
_Q2 = "qc qc qc qc qc mc mc numeric multi mc fraction mc [mc numeric multi]"
LAYOUT = {k: parse_layout(v) for k, v in {
    "V1": "tc tc tc tc se se [mc multi mc] [mc] [mc mc]", "V2E": _V2, "V2M": _V2, "V2H": _V2,
    "Q1": "qc qc qc qc mc numeric multi mc fraction [mc mc multi]", "Q2E": _Q2, "Q2M": _Q2, "Q2H": _Q2}.items()}


def mix_ok(key, diffs):
    """Difficulty mix per section (design doc, section 4)."""
    n = lambda lo, hi: sum(lo <= d <= hi for d in diffs)
    if key in ("V1", "Q1"):
        return n(3, 4) >= 8 * len(diffs) / 12 and n(5, 5) >= 1 and n(1, 2) <= 2
    if key in ("V2H", "Q2H"):
        return n(4, 5) >= 10 * len(diffs) / 15 and n(1, 2) == 0
    if key in ("V2M", "Q2M"):
        return n(3, 4) >= 11 * len(diffs) / 15 and n(1, 1) == 0
    return n(2, 3) == len(diffs)  # V2E, Q2E


# shortcut: mix not enforced on these until their content is rewritten (plan Tasks 5-6); remove then
MIX_PENDING = {"test-01", "shared-easy"}


def check_all(tests, shared=None):
    """Validate every test plus cross-test rules; returns the list of problems."""
    global problems
    saved, problems = problems, []
    try:
        shared_keys = tuple(shared["sections"]) if shared else ()
        seen_ids, seen_keys = {}, {}
        if shared:
            for s in shared["sections"].values():
                for q in s["questions"]:
                    seen_ids[q["id"]] = "shared-easy"
            for kind in ("passages", "tables", "charts"):
                for k in shared.get(kind, {}):
                    seen_keys[(kind, k)] = "shared-easy"
            for k, s in shared["sections"].items():
                if "shared-easy" not in MIX_PENDING and not mix_ok(k, [q["difficulty"] for q in s["questions"]]):
                    fail(f"shared-easy {k} difficulty mix off")
        for t in tests:
            check_test(t, shared_keys)
            for k, s in t["sections"].items():
                if k in shared_keys:
                    continue
                for q in s["questions"]:
                    if q["id"] in seen_ids and seen_ids[q["id"]] != t["id"]:
                        fail(f"{t['id']}: duplicate id {q['id']} (also in {seen_ids[q['id']]})")
                    seen_ids[q["id"]] = t["id"]
                if t["id"] not in MIX_PENDING and not mix_ok(k, [q["difficulty"] for q in s["questions"]]):
                    fail(f"{t['id']}: {k} difficulty mix off")
            for kind in ("passages", "tables", "charts"):
                for k in t.get(kind, {}):
                    if shared and k in shared.get(kind, {}):
                        continue
                    if (kind, k) in seen_keys:
                        fail(f"{t['id']}: duplicate {kind[:-1]} key {k} (also in {seen_keys[(kind, k)]})")
                    seen_keys[(kind, k)] = t["id"]
        for t in tests:
            for k, s in t["sections"].items():
                if k in LAYOUT and (k not in shared_keys and t["id"] not in MIX_PENDING) and slot_layout(s) != LAYOUT[k]:
                    fail(f"{t['id']}: {k} layout differs from the section spec")
        if shared and "shared-easy" not in MIX_PENDING:
            for k, s in shared["sections"].items():
                if slot_layout(s) != LAYOUT[k]:
                    fail(f"shared-easy: {k} layout differs from the section spec")
        problems.extend(verify_quant.verify(tests))
        return problems
    finally:
        problems = saved


def merge_shared(test, shared):
    """Copy the shared easy sections and their passages/tables/charts into a test (same objects, no copy)."""
    for k, s in shared["sections"].items():
        test["sections"][k] = s
    for kind in ("passages", "tables", "charts"):
        test.setdefault(kind, {}).update(shared.get(kind, {}))


def load_tests(root):
    """Read tests/test-*.json and tests/shared-easy.json; returns (tests, shared)."""
    shared_path = root / "tests" / "shared-easy.json"
    shared = json.loads(shared_path.read_text(encoding="utf-8")) if shared_path.exists() else None
    if shared:
        for s in shared["sections"].values():
            if s["measure"] == "Verbal":
                for q in s["questions"]:
                    shuffle_q(q)  # once, so every test shows the same order
    tests = []
    for path in sorted((root / "tests").glob("test-*.json")):
        raw = path.read_text(encoding="utf-8")
        t = json.loads(raw)
        t["version"] = hashlib.sha256((raw + json.dumps(shared, sort_keys=True)).encode()).hexdigest()[:10]  # changes when the test or shared file changes
        if shared:
            merge_shared(t, shared)
        tests.append(t)
    return tests, shared


CONFIG["version"] = hashlib.sha256(json.dumps([ROUTING, CONVERSION]).encode()).hexdigest()[:10]


def main():
    tests, shared = load_tests(ROOT)
    probs = problems + check_all(tests, shared)

    if "--table" in sys.argv:
        print("raw  easier medium harder")
        for r in range(28):
            print(f"{r:>3}  " + "  ".join(f"{CONVERSION[t][r] if r in REACH[t] else '  - ':>6}" for t in ("easier", "medium", "harder")))

    if probs:
        print("BUILD FAILED:")
        for p in probs:
            print(" -", p)
        sys.exit(1)

    data = {"config": CONFIG, "tests": tests, "shared": list(shared["sections"]) if shared else []}
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    random_js = (ROOT / "src" / "random.js").read_text(encoding="utf-8")
    html = (ROOT / "src" / "app.html").read_text(encoding="utf-8").replace("__RANDOM_JS__", random_js).replace("__DATA__", payload)
    (ROOT / "src" / "artifact.html").write_text(html, encoding="utf-8")
    local = ('<!doctype html>\n<html lang="en-GB">\n<head>\n<meta charset="utf-8">\n'
             '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
             + html.replace("<style>", "<style>\n[hidden]{display:none!important}", 1)
             .replace('<div id="bar"', '</head>\n<body>\n<div id="bar"', 1)
             + "\n</body>\n</html>\n")
    (ROOT / "GRE-Practice-Centre.html").write_text(local, encoding="utf-8")
    (ROOT / "index.html").write_text(local, encoding="utf-8")  # served by GitHub Pages
    print(f"Built {len(tests)} test(s): {', '.join(t['id'] for t in tests)} ({len(local):,} bytes)")


if __name__ == "__main__":
    main()
