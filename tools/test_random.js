// Self-checks for src/random.js. Run: node tools/test_random.js
const assert = require("assert");
const R = require("../src/random.js");

function sec(measure, qs) { return { measure: measure, minutes: 1, label: "L", questions: qs }; }
function mk(n) {
  const p = "t" + n;
  return {
    id: "test-0" + n, title: "T" + n, order: ["V1", "V2", "Q1", "Q2"], essay: { prompt: "essay " + n },
    passages: { [p + "-pa"]: ["S."] }, tables: {}, charts: {},
    sections: {
      V1: sec("Verbal", [{ id: p + "-v1", type: "tc" }, { id: p + "-v2", type: "mc", passage: p + "-pa" }, { id: p + "-v3", type: "multi", passage: p + "-pa" }, { id: p + "-v4", type: "se" }]),
      V2E: sec("Verbal", [{ id: "E-V-01", type: "tc" }]),
      Q1: sec("Quant", [{ id: p + "-q1", type: "qc" }, { id: p + "-q2", type: "numeric" }]),
    },
  };
}
const shared = { V2E: true }; // shared section objects are the same in every test
const tests = [mk(1), mk(2), mk(3)];
tests[1].sections.V2E = tests[0].sections.V2E; tests[2].sections.V2E = tests[0].sections.V2E;
const idx = R.indexTests(tests, ["V2E"]);
function seeded(s) { return function () { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; }; }

const T = {
  version_follows_fixed_tests() {
    const a = tests.map(t => Object.assign({}, t, { version: "v1" }));
    const b = a.map((t, i) => Object.assign({}, t, { version: i ? "v1" : "v2" }));
    const comp = R.compose(R.indexTests(a, ["V2E"]), seeded(7));
    const va = R.materialize(comp, R.indexTests(a, ["V2E"]), "random-1").version;
    assert.notStrictEqual(va, R.materialize(comp, R.indexTests(b, ["V2E"]), "random-1").version, "editing a fixed test must change the randomized version");
    assert.strictEqual(va, R.materialize(comp, R.indexTests(a, ["V2E"]), "random-1").version);
  },
  compose_counts() {
    for (let s = 1; s < 30; s++) {
      const c = R.compose(idx, seeded(s));
      assert.strictEqual(c.sections.V1.length, 4);
      assert.strictEqual(c.sections.Q1.length, 2);
    }
  },
  passage_set_kept_together() {
    for (let s = 1; s < 60; s++) {
      const v = R.compose(idx, seeded(s)).sections.V1;
      assert.strictEqual(v[1].split("-")[0], v[2].split("-")[0], v.join());
      assert.ok(v[1].endsWith("-v2") && v[2].endsWith("-v3"));
    }
  },
  mixes_tests() {
    const from = new Set();
    for (let s = 1; s < 40; s++) R.compose(idx, seeded(s)).sections.V1.forEach(function (id) { from.add(id.split("-")[0]); });
    assert.strictEqual(from.size, 3);
  },
  shared_sections_fixed() {
    assert.deepStrictEqual(R.compose(idx, seeded(7)).sections.V2E, ["E-V-01"]);
  },
  materialize_roundtrip() {
    const c = R.compose(idx, seeded(3)), t = R.materialize(c, idx, "random-1");
    assert.strictEqual(t.id, "random-1");
    assert.strictEqual(t.title, "Randomized test");
    assert.deepStrictEqual(t.sections.V1.questions.map(function (q) { return q.id; }), c.sections.V1);
    assert.strictEqual(t.sections.V1.measure, "Verbal");
    const pk = t.sections.V1.questions[1].passage;
    assert.ok(t.passages[pk], "passage of a sampled set must be present");
    assert.strictEqual(t.essay.prompt, idx.essays[c.essayFrom].prompt);
    assert.deepStrictEqual(t.order, ["V1", "V2", "Q1", "Q2"]);
  },
  materialize_missing_id() {
    const c = R.compose(idx, seeded(3));
    c.sections.Q1[0] = "gone-id";
    const q = R.materialize(c, idx, "random-2").sections.Q1.questions[0];
    assert.deepStrictEqual(q, { id: "gone-id", type: "removed" });
  },
};
for (const k in T) T[k]();
console.log("random: all passed");
