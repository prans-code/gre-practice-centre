"""Self-checks for src/build.py. Run: python -I tools/test_build.py"""
import copy
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build  # noqa: E402


def q(qid, t="numeric", d=3, **kw):
    base = {"id": qid, "type": t, "difficulty": d, "skill": "x", "explain": "because", "stem": "s"}
    if t == "numeric":
        base["answer"] = 1
    if t == "mc":
        base.update(options=["a", "b", "c", "d", "e"], answer=0)
    if t == "qc":
        base.update(qa="a", qb="b", answer=0)
    base.update(kw)
    return base


def make_test(tid, sections, passages=None):
    return {"id": tid, "title": tid, "order": ["V1", "V2", "Q1", "Q2"], "essay": {"prompt": "p"},
            "passages": passages or {}, "tables": {}, "charts": {},
            "sections": {k: {"measure": "Quant" if k.startswith("Q") else "Verbal", "minutes": 1, "label": k, "questions": qs}
                         for k, qs in sections.items()}}


def problems_for(tests, shared=None):
    return build.check_all(tests, shared)


def test_duplicate_id_across_tests():
    a = make_test("a", {"Q1": [q("T1-V1-01")]})
    b = make_test("b", {"Q1": [q("T1-V1-01")]})
    assert any("duplicate id T1-V1-01" in p for p in problems_for([a, b])), problems_for([a, b])


def test_duplicate_passage_key_across_tests():
    a = make_test("a", {"V1": [q("a1", "mc", passage="p1")]}, {"p1": ["One."]})
    b = make_test("b", {"V1": [q("b1", "mc", passage="p1")]}, {"p1": ["One."]})
    assert any("duplicate passage key p1" in p for p in problems_for([a, b]))


def test_shared_easy_not_duplicate():
    shared = {"passages": {"e-p": ["One."]}, "tables": {}, "charts": {},
              "sections": {"Q2E": {"measure": "Quant", "minutes": 1, "label": "Q2E", "questions": [q("E-Q-01", d=2)]},
                           "V2E": {"measure": "Verbal", "minutes": 1, "label": "V2E", "questions": [q("E-V-01", "mc", d=2, passage="e-p")]}}}
    tests = []
    for i in range(3):
        t = make_test(f"t{i}", {"Q1": [q(f"T{i}-Q1-01")]})
        build.merge_shared(t, shared)
        tests.append(t)
    probs = problems_for(tests, shared)
    assert not any("duplicate" in p for p in probs), probs


def test_layout_mismatch():
    a = make_test("a", {"Q1": [q("a1", "qc"), q("a2")]})
    b = make_test("b", {"Q1": [q("b1"), q("b2", "qc")]})
    assert any("Q1 layout differs" in p for p in problems_for([a, b]))


def test_difficulty_mix():
    t = make_test("a", {"Q2H": [q("h1", d=2), q("h2", d=2), q("h3", d=2)]})
    assert any("Q2H difficulty mix" in p for p in problems_for([t]))


def test_slot_layout():
    sec = {"questions": [q("1", "qc"), q("2", "mc", passage="p"), q("3", "multi", passage="p"), q("4", "mc"), q("5", "mc", table="t"), q("6", "numeric", table="t")]}
    assert build.slot_layout(sec) == [("qc",), ("mc", "multi"), ("mc",), ("mc", "numeric")], build.slot_layout(sec)


def test_qc_cannot_determine():
    import verify_quant
    assert verify_quant.qc([(1, 2), (3, 2)]) == 3


def test_qc_equal():
    import verify_quant
    assert verify_quant.qc([(2, 2), (5, 5)]) == 2


def test_fraction_equivalence():
    import verify_quant
    assert verify_quant.same_key({"type": "fraction", "answer": [1, 2]}, [2, 4])
    assert not verify_quant.same_key({"type": "fraction", "answer": [1, 2]}, [2, 5])
    assert verify_quant.same_key({"type": "numeric", "answer": 0.5}, 1 / 2)


def test_missing_check_reported():
    import verify_quant
    t = make_test("a", {"Q1": [q("NO-SUCH-ID")]})
    assert any("NO-SUCH-ID: no quant check" in p for p in verify_quant.verify([t]))


def test_wrong_key_reported():
    import verify_quant
    verify_quant.CHECKS["TMP-1"] = lambda: 2
    try:
        t = make_test("a", {"Q1": [q("TMP-1")]})
        assert any("TMP-1: key 1, check says 2" in p for p in verify_quant.verify([t]))
    finally:
        del verify_quant.CHECKS["TMP-1"]


def test_check_all_runs_quant_verifier():
    t = make_test("a", {"Q1": [q("NO-SUCH-ID")]})
    assert any("NO-SUCH-ID: no quant check" in p for p in problems_for([t]))


def test_real_tests_build_clean():
    tests, shared = build.load_tests(build.ROOT)
    probs = build.check_all(copy.deepcopy(tests), shared)
    assert not probs, probs


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("all build checks passed")
