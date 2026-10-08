// Salt finder engine: asks one yes/no/don't-know question per feature and
// keeps a score per salt (a Bayesian update), always picking the question
// with the highest expected information gain next.
//
//  - "yes"  -> salts that have the feature go up, the rest go down
//  - "no"   -> salts that have the feature go down (never to zero)
//  - "idk"  -> nothing changes; the question budget grows by one
//
// Shared by index.html (browser) and the node test.
(function (root) {
  var DEFAULTS = {
    // chance a person needing this salt says "yes" to the feature
    likelihood: { AB: 0.85, A: 0.7, B: 0.7, none: 0.15 },
    maxDepth: 20,          // answered (non-IDK) questions allowed, counting the
                           // starting pick as the first "yes" (so 19 follow-ups)
    topShare: 0.67,        // result = top salts covering 67% of the score
    stopConfidence: 0.90,  // stop early once one salt is this certain
    // groups describing where a salt acts, not something a person can answer
    skipGroups: ["Tissue affinity"]
  };

  function opts(o) {
    var r = {}, k;
    for (k in DEFAULTS) r[k] = DEFAULTS[k];
    for (k in o || {}) r[k] = o[k];
    return r;
  }

  function pYes(data, fi, si, o) {
    var src = data.features[fi].salts[data.salts[si].key];
    return o.likelihood[src || "none"];
  }

  function normalise(p) {
    var t = 0, i;
    for (i = 0; i < p.length; i++) t += p[i];
    return p.map(function (x) { return x / t; });
  }

  function entropy(p) {
    var h = 0;
    for (var i = 0; i < p.length; i++) if (p[i] > 0) h -= p[i] * Math.log2(p[i]);
    return h;
  }

  // answers: [{fi: featureIndex, a: "yes" | "no" | "idk"}]
  function posterior(data, answers, o) {
    o = opts(o);
    var p = data.salts.map(function () { return 1; });
    answers.forEach(function (ans) {
      if (ans.a === "idk") return;
      for (var si = 0; si < p.length; si++) {
        var y = pYes(data, ans.fi, si, o);
        p[si] *= ans.a === "yes" ? y : 1 - y;
      }
    });
    return normalise(p);
  }

  function gain(data, fi, post, o) {
    var yes = [], no = [], py = 0;
    for (var si = 0; si < post.length; si++) {
      var y = pYes(data, fi, si, o);
      yes.push(post[si] * y);
      no.push(post[si] * (1 - y));
      py += post[si] * y;
    }
    return entropy(post) - py * entropy(normalise(yes)) - (1 - py) * entropy(normalise(no));
  }

  function answeredCount(answers) {
    return answers.filter(function (a) { return a.a !== "idk"; }).length;
  }

  // Returns {fi, gain} for the next question, or {fi: null, reason} to stop.
  function nextQuestion(data, answers, o) {
    o = opts(o);
    var post = posterior(data, answers, o);
    if (answeredCount(answers) >= o.maxDepth) return { fi: null, reason: "question limit reached" };
    if (Math.max.apply(null, post) >= o.stopConfidence) return { fi: null, reason: "one salt is clearly ahead" };
    var asked = {}, best = null, bestGain = -1;
    answers.forEach(function (a) { asked[a.fi] = true; });
    for (var fi = 0; fi < data.features.length; fi++) {
      if (asked[fi] || o.skipGroups.indexOf(data.features[fi].group) !== -1) continue;
      var g = gain(data, fi, post, o);
      if (g > bestGain) { bestGain = g; best = fi; }
    }
    if (best === null) return { fi: null, reason: "no questions left" };
    return { fi: best, gain: bestGain };
  }

  // Smallest set of top-ranked salts whose scores add up to >= topShare.
  function result(data, answers, o) {
    o = opts(o);
    var post = posterior(data, answers, o);
    var ranked = post.map(function (p, si) { return { salt: data.salts[si], share: p }; })
      .sort(function (a, b) { return b.share - a.share; });
    var top = [], sum = 0;
    for (var i = 0; i < ranked.length && sum < o.topShare; i++) { top.push(ranked[i]); sum += ranked[i].share; }
    return { top: top, covered: sum, ranked: ranked };
  }

  var api = { DEFAULTS: DEFAULTS, posterior: posterior, nextQuestion: nextQuestion, result: result, answeredCount: answeredCount };
  if (typeof module !== "undefined") module.exports = api;
  else root.SaltEngine = api;
})(this);
