// Self-checks for src/practice.js. Run: node tools/test_practice.js
const assert = require("assert");
const P = require("../src/practice.js");

const bank = {
  passages: { "p-a": ["S."], "p-cr": ["Arg."] }, tables: {}, charts: {},
  questions: [
    { id: "q1", topic: "Geometry" }, { id: "q2", topic: "Geometry" }, { id: "q3", topic: "Statistics" },
    { id: "v1", topic: "Reading comprehension", passage: "p-a" }, { id: "v2", topic: "Reading comprehension", passage: "p-a" },
    { id: "v3", topic: "Reading comprehension", passage: "p-a" }, { id: "v4", topic: "Critical reasoning", passage: "p-cr" },
    { id: "v5", topic: "Text completion" },
  ],
};
const topics = { Geometry: "Quant", Statistics: "Quant", "Reading comprehension": "Verbal", "Critical reasoning": "Verbal", "Text completion": "Verbal" };
function seeded(s) { return function () { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; }; }
const e = (qid, ok, at) => ({ qid: qid, ok: ok, at: at, tries: 1, secs: 30 });

const T = {
  merge_keeps_later_entry() {
    const m = P.mergeLog({ q1: e("q1", false, "2026-01-01"), q2: e("q2", true, "2026-01-05") }, { q1: e("q1", true, "2026-01-03"), q3: e("q3", true, "2026-01-02") });
    assert.strictEqual(m.q1.ok, true); assert.strictEqual(m.q2.ok, true); assert.strictEqual(m.q3.ok, true);
    assert.deepStrictEqual(Object.keys(m).sort(), ["q1", "q2", "q3"]);
  },
  merge_does_not_mutate() {
    const a = { q1: e("q1", false, "2026-01-01") };
    P.mergeLog(a, { q1: e("q1", true, "2026-01-03") });
    assert.strictEqual(a.q1.ok, false);
  },
  newer_than_lists_only_local_updates() {
    const local = { q1: e("q1", true, "2026-01-04"), q2: e("q2", true, "2026-01-01"), q3: e("q3", false, "2026-01-02") };
    const remote = { q1: e("q1", false, "2026-01-03"), q2: e("q2", true, "2026-01-01") };
    assert.deepStrictEqual(P.newerThan(local, remote).map(x => x.qid).sort(), ["q1", "q3"]);
  },
  pick_filters_measure_and_topic() {
    const s = P.pick(bank, topics, { measure: "Quant", topic: "Geometry", n: 5 }, {}, seeded(3));
    assert.deepStrictEqual(s.slice().sort(), ["q1", "q2"]);
  },
  pick_mixed_takes_whole_measure() {
    const s = P.pick(bank, topics, { measure: "Verbal", topic: "mixed", n: 20 }, {}, seeded(5));
    assert.deepStrictEqual(s.slice().sort(), ["v1", "v2", "v3", "v4", "v5"]);
  },
  pick_keeps_passage_sets_together_and_runs_over() {
    for (let k = 1; k < 30; k++) {
      const s = P.pick(bank, topics, { measure: "Verbal", topic: "mixed", n: 1 }, {}, seeded(k));
      const i = s.indexOf("v1");
      if (i >= 0) assert.deepStrictEqual(s.slice(i, i + 3), ["v1", "v2", "v3"]);
      else assert.strictEqual(s.length, 1);
    }
  },
  pick_prefers_unseen() {
    const log = { q1: e("q1", true, "2026-01-01") };
    for (let k = 1; k < 20; k++) assert.deepStrictEqual(P.pick(bank, topics, { measure: "Quant", topic: "Geometry", n: 1 }, log, seeded(k)), ["q2"]);
  },
  pick_missed_only_wrong_answers() {
    const log = { q1: e("q1", false, "2026-01-01"), q2: e("q2", true, "2026-01-01"), v2: e("v2", false, "2026-01-01") };
    assert.deepStrictEqual(P.pick(bank, topics, { measure: "Quant", topic: "missed", n: 10 }, log, seeded(2)), ["q1"]);
    assert.deepStrictEqual(P.pick(bank, topics, { measure: "Verbal", topic: "missed", n: 10 }, log, seeded(2)), ["v2"]);
  },
  stats_per_topic() {
    const log = { q1: e("q1", false, "2026-01-01"), q2: e("q2", true, "2026-01-01") };
    const st = P.stats(bank, topics, "Quant", log);
    assert.deepStrictEqual(st.Geometry, { total: 2, seen: 2, correct: 1 });
    assert.deepStrictEqual(st.Statistics, { total: 1, seen: 0, correct: 0 });
    assert.strictEqual(st["Text completion"], undefined);
  },
  log_ignores_ids_not_in_bank() {
    const log = { gone: e("gone", false, "2026-01-01") };
    assert.deepStrictEqual(P.pick(bank, topics, { measure: "Quant", topic: "missed", n: 5 }, log, seeded(1)), []);
  },
};

let n = 0;
for (const [name, fn] of Object.entries(T)) { fn(); n++; }
console.log("practice: all passed (" + n + ")");
