// Randomized test: fills every slot of every section from the same slot in a randomly chosen fixed test.
// All fixed tests share one layout per section (the build checks this), so counts and types always match.
var GRE_RANDOM = (function () {
  // a slot is a run of consecutive questions sharing a passage, table or chart; otherwise one question (same rule as build.py slot_layout)
  function slotsOf(section) {
    var slots = [], last = null;
    section.questions.forEach(function (q) {
      var g = q.passage || q.table || q.chart || null;
      if (g && g === last) slots[slots.length - 1].push(q.id); else slots.push([q.id]);
      last = g;
    });
    return slots;
  }

  function indexTests(tests, sharedKeys) {
    var ix = { q: {}, passages: {}, tables: {}, charts: {}, essays: {}, testIds: [], meta: {}, slots: {}, shared: sharedKeys || [] };
    tests.forEach(function (t) {
      ix.testIds.push(t.id);
      ix.essays[t.id] = t.essay;
      ["passages", "tables", "charts"].forEach(function (k) { for (var key in (t[k] || {})) ix[k][key] = t[k][key]; });
      for (var sk in t.sections) {
        var s = t.sections[sk];
        if (!ix.meta[sk]) ix.meta[sk] = { measure: s.measure, minutes: s.minutes, label: s.label };
        s.questions.forEach(function (q) { ix.q[q.id] = q; });
        (ix.slots[sk] = ix.slots[sk] || []).push(slotsOf(s));
      }
    });
    return ix;
  }

  function compose(ix, rand) {
    var out = { sections: {}, essayFrom: ix.testIds[Math.floor(rand() * ix.testIds.length)] };
    for (var sk in ix.slots) {
      var perTest = ix.slots[sk];
      if (ix.shared.indexOf(sk) >= 0) { out.sections[sk] = [].concat.apply([], perTest[0]); continue; }
      var ids = [];
      perTest[0].forEach(function (_, i) { ids = ids.concat(perTest[Math.floor(rand() * perTest.length)][i]); });
      out.sections[sk] = ids;
    }
    return out;
  }

  function materialize(comp, ix, id) {
    var t = { id: id, title: "Randomized test", blurb: "A new mix of questions drawn from all the practice tests.",
      order: ["V1", "V2", "Q1", "Q2"], essay: ix.essays[comp.essayFrom] || ix.essays[ix.testIds[0]],
      passages: ix.passages, tables: ix.tables, charts: ix.charts, sections: {}, version: "random", random: true };
    for (var sk in comp.sections) {
      var m = ix.meta[sk] || { measure: sk.charAt(0) === "Q" ? "Quant" : "Verbal" };
      t.sections[sk] = { measure: m.measure, minutes: m.minutes, label: m.label,
        questions: comp.sections[sk].map(function (qid) { return ix.q[qid] || { id: qid, type: "removed" }; }) };
    }
    return t;
  }

  return { indexTests: indexTests, compose: compose, materialize: materialize };
})();
if (typeof module !== "undefined") module.exports = GRE_RANDOM;
