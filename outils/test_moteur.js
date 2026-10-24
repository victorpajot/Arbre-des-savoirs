// Test du cycle complet : node outils/test_moteur.js
const fs = require("fs"), path = require("path"), assert = require("assert");
const M = require("../web/moteur.js");
const d = n => JSON.parse(fs.readFileSync(path.join(__dirname, "../data", n), "utf8"));
const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"));
let t = new Date(2026, 9, 24, 9, 0).getTime();
const P = M.nouvellePartie(t);
const jour = 86400000;
const res = (id, n, ok) => M.tirerQuestions(C, P, id, n).map((q, i) => ({ id: q.id, correct: i < ok }));

assert.equal(M.statut(C, P, "math.arithmetique", t).etat, "disponible");
assert.equal(M.statut(C, P, "math.proportions", t).etat, "verrouillee");
let r = M.terminerQuiz(C, P, "math.arithmetique", res("math.arithmetique", 5, 3), t);
assert.equal(r.issue, "echec");
assert.deepEqual(r.nouveauxSucces.map(s => s.id), ["tour-de-pise"]);
r = M.terminerQuiz(C, P, "math.arithmetique", res("math.arithmetique", 5, 5), t);
assert.equal(r.issue, "maitrisee"); assert.equal(r.xp, 70);
assert.deepEqual(r.nouveauxSucces.map(s => s.id).sort(), ["eureka", "premier-pas"]);
assert.equal(M.statut(C, P, "math.proportions", t).etat, "disponible");
assert.equal(M.rappelsDus(C, P, t).length, 0);
// Rappel dû le lendemain à minuit
t += jour; assert.equal(M.rappelsDus(C, P, t).length, 1);
r = M.terminerRappel(C, P, "math.arithmetique", res("math.arithmetique", 3, 2), t);
assert.equal(r.issue, "reussi"); assert.equal(M.joursEntre(t, r.prochainRappel), 3);
assert.equal(M.xpParStat(C, P).logique, 75);
// Maîtriser proportions, puis perdre arithmétique : proportions est gelée, logique (rang 4) reste verrouillée
r = M.terminerQuiz(C, P, "math.proportions", res("math.proportions", 5, 4), t);
assert.equal(r.issue, "maitrisee");
r = M.terminerQuiz(C, P, "math.probabilites", res("math.probabilites", 5, 4), t);
assert.equal(M.statut(C, P, "math.logique", t).etat, "disponible");
t += 3 * jour;
r = M.terminerRappel(C, P, "math.arithmetique", res("math.arithmetique", 3, 1), t);
assert.equal(r.issue, "perdue"); assert.equal(r.xpPerdue, 75);
assert.ok(r.nouveauxSucces.some(s => s.id === "lucide"));
assert.equal(M.statut(C, P, "math.arithmetique", t).etat, "disponible");
assert.equal(M.statut(C, P, "math.proportions", t).gelee, true);
assert.equal(M.statut(C, P, "math.logique", t).etat, "verrouillee");
r = M.terminerQuiz(C, P, "math.arithmetique", res("math.arithmetique", 5, 4), t);
assert.ok(r.nouveauxSucces.some(s => s.id === "resilience"));
assert.equal(M.statut(C, P, "math.proportions", t).gelee, false);
// Questions récentes évitées
const vues = P.competences["math.arithmetique"].recentes;
const tir = M.tirerQuestions(C, P, "math.arithmetique", 5).map(q => q.id);
assert.ok(tir.every(id => !vues.includes(id)));
// Correction numérique
const qn = C.questionParId["phys.ondes.q03"];
assert.ok(M.corriger(qn, "1 000")); assert.ok(M.corriger(qn, "1020,0")); assert.ok(!M.corriger(qn, "abc"));
// Suggestion : la stat la plus faible
assert.equal(M.suggestion(C, P, t).stat !== "logique", true);
// Migration
assert.equal(M.migrer(JSON.parse(JSON.stringify(P))).compteurs.perdues, 1);
assert.equal(M.migrer({ format: 99 }), null);
console.log("OK : cycle quiz → rappel → perte → regain, succès, gel, tirage, correction");
// Chrono : +5 XP par bonne réponse chronométrée
{
  const P2 = M.nouvellePartie(t);
  const r2 = M.terminerQuiz(C, P2, "phys.unites", M.tirerQuestions(C, P2, "phys.unites", 5).map(q => ({ id: q.id, correct: true, chrono: true })), t);
  assert.equal(r2.xp, 50 + 20 + 25);
  console.log("OK : bonus chrono");
}
