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


def check_test(test, path):
    tid = test.get("id", path.name)
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
            if sec["measure"] == "Verbal":
                shuffle_q(q)
    # answer-position spread after shuffling
    pos = [q["answer"] for s in test["sections"].values() for q in s["questions"] if q["type"] == "mc"]
    if pos and max(pos.count(i) for i in set(pos)) > 0.45 * len(pos):
        fail(f"{tid}: single-answer key positions too uneven {sorted(pos)}")
    tc0 = [a == 0 for s in test["sections"].values() for q in s["questions"] if q["type"] == "tc" for a in q["answer"]]
    if tc0 and sum(tc0) > 0.5 * len(tc0):
        fail(f"{tid}: too many text-completion answers in the first position")


CONFIG["version"] = hashlib.sha256(json.dumps([ROUTING, CONVERSION]).encode()).hexdigest()[:10]

tests = []
for path in sorted((ROOT / "tests").glob("test-*.json")):
    raw = path.read_text(encoding="utf-8")
    t = json.loads(raw)
    t["version"] = hashlib.sha256(raw.encode()).hexdigest()[:10]  # changes whenever the test file changes
    check_test(t, path)
    tests.append(t)

if "--table" in sys.argv:
    print("raw  easier medium harder")
    for r in range(28):
        print(f"{r:>3}  " + "  ".join(f"{CONVERSION[t][r] if r in REACH[t] else '  - ':>6}" for t in ("easier", "medium", "harder")))

if problems:
    print("BUILD FAILED:")
    for p in problems:
        print(" -", p)
    sys.exit(1)

payload = json.dumps({"config": CONFIG, "tests": tests}, ensure_ascii=False).replace("</", "<\\/")
html = (ROOT / "src" / "app.html").read_text(encoding="utf-8").replace("__DATA__", payload)
(ROOT / "src" / "artifact.html").write_text(html, encoding="utf-8")
local = ('<!doctype html>\n<html lang="en-GB">\n<head>\n<meta charset="utf-8">\n'
         '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
         + html.replace("<style>", "<style>\n[hidden]{display:none!important}", 1)
         .replace('<div id="bar"', '</head>\n<body>\n<div id="bar"', 1)
         + "\n</body>\n</html>\n")
(ROOT / "GRE-Practice-Centre.html").write_text(local, encoding="utf-8")
(ROOT / "index.html").write_text(local, encoding="utf-8")  # served by GitHub Pages
print(f"Built {len(tests)} test(s): {', '.join(t['id'] for t in tests)} ({len(local):,} bytes)")
