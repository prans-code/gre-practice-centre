/* Practice-by-topic helpers: pure functions shared by the app (inlined by build.py) and node tests.
   A log maps question id -> {qid, ok, at (ISO time), tries, secs}; the later `at` wins when two copies meet. */
var GRE_PRACTICE = (function () {
  function mergeLog(a, b) {
    var r = {}, k;
    for (k in a) r[k] = a[k];
    for (k in b) if (!r[k] || b[k].at > r[k].at) r[k] = b[k];
    return r;
  }
  function newerThan(local, remote) {
    var out = [];
    for (var k in local) if (!remote[k] || local[k].at > remote[k].at) out.push(local[k]);
    return out;
  }
  function shuffle(a, rand) {
    for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(rand() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  // opts: {measure, topic: a topic name | "mixed" | "missed", n}. Returns question ids; a passage/table/chart set is never split.
  function pick(bank, topics, opts, log, rand) {
    var pool = bank.questions.filter(function (q) {
      if (topics[q.topic] !== opts.measure) return false;
      if (opts.topic === "missed") return !!(log[q.id] && log[q.id].ok === false);
      return opts.topic === "mixed" || q.topic === opts.topic;
    });
    var units = [], last = null;
    pool.forEach(function (q) {
      var g = q.passage || q.table || q.chart || null;
      if (g && g === last) units[units.length - 1].push(q.id); else units.push([q.id]);
      last = g;
    });
    var fresh = [], seen = [];
    units.forEach(function (u) { (u.some(function (id) { return log[id]; }) ? seen : fresh).push(u); });
    var ordered = shuffle(fresh, rand).concat(shuffle(seen, rand)), out = [];
    for (var i = 0; i < ordered.length && out.length < opts.n; i++) out = out.concat(ordered[i]);
    return out;
  }
  function stats(bank, topics, measure, log) {
    var st = {};
    bank.questions.forEach(function (q) {
      if (topics[q.topic] !== measure) return;
      var s = st[q.topic] || (st[q.topic] = { total: 0, seen: 0, correct: 0 }), e = log[q.id];
      s.total++;
      if (e) { s.seen++; if (e.ok) s.correct++; }
    });
    return st;
  }
  return { mergeLog: mergeLog, newerThan: newerThan, pick: pick, stats: stats };
})();
if (typeof module !== "undefined") module.exports = GRE_PRACTICE;
