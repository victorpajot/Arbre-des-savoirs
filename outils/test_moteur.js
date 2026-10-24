// Test du cycle complet : node outils/test_moteur.js
const fs = require("fs"), path = require("path"), assert = require("assert");
const M = require("../web/moteur.js");
const d = n => JSON.parse(fs.readFileSync(path.join(__dirname, "../data", n), "utf8"));
const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
  { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json") });
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
assert.deepEqual(r.nouveauxSucces.map(s => s.id).sort(), ["einstein-notes", "eureka", "premier-pas"]);
assert.deepEqual(r.nouveauxObjets.map(o => o.id), ["boulier"]);
assert.deepEqual(r.nouveauxAccessoires.map(a => a.id), ["lunettes-rondes", "coiffure-einstein"]);
assert.ok(r.contextes.includes("quiz_parfait_facile"));
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

// v2 : migration d'une partie v1, nouvelles branches, compteurs moqueurs, narrateur, avatar
{
  const t0 = new Date(2026, 9, 24, 9, 0).getTime();
  const v1 = { format: 1, cree: t0, maj: t0, decalage: 0, succes: { "premier-pas": t0 }, jours: ["2026-10-24"], journal: [],
    compteurs: { quizParfaits: 1, quizRates: 0, rappelsReussis: 0, serieRappels: 0, perdues: 0, regagnees: 0 },
    competences: { "sci.atomes": { maitrise: true, maitriseDepuis: t0, palier: 0, prochainRappel: t0 + jour, xp: 70 },
                   "sci.evolution": { maitrise: true, maitriseDepuis: t0, palier: 0, prochainRappel: t0 + jour, xp: 60 },
                   "sci.methode": { maitrise: true, maitriseDepuis: t0, palier: 0, prochainRappel: t0 + jour, xp: 60 } },
    options: { chrono: false } };
  const P3 = M.migrer(JSON.parse(JSON.stringify(v1)));
  assert.equal(P3.format, 2);
  assert.equal(P3.compteurs.quizParfaits, 1); assert.equal(P3.compteurs.quizJoues, 0);
  assert.deepEqual(P3.avatar, { tete: null, visage: null, main: null });
  // Atomes compte désormais pour Alchimie ; Évolution n'est pas gelée par la nouvelle branche Savoir
  const xp = M.xpParStat(C, P3);
  assert.equal(xp.alchimie, 70); assert.equal(xp.savoir, 120);
  assert.equal(M.statut(C, P3, "sci.evolution", t0).gelee, false);
  assert.equal(M.statut(C, P3, "sci.genetique", t0).etat, "verrouillee");
  assert.equal(M.statut(C, P3, "chim.liaisons", t0).etat, "disponible");
  const rec = M.verifierRecompenses(C, P3, t0);
  assert.ok(rec.objets.some(o => o.id === "tableau-mendeleiev"));
  // Quiz raté en 20 s, à 3 h du matin, avec des réponses éclair : la panoplie moqueuse
  const nuit = new Date(2026, 9, 25, 3, 0).getTime();
  const qs = M.tirerQuestions(C, P3, "chim.liaisons", 5).map(q => ({ id: q.id, correct: false, ms: 900 }));
  let r3 = M.terminerQuiz(C, P3, "chim.liaisons", qs, nuit, { duree: 20000 });
  const ids = r3.nouveauxSucces.map(s => s.id);
  for (const id of ["dix-pour-cent", "insomniaque", "table-rase", "neutrinos", "tour-de-pise"]) assert.ok(ids.includes(id), id);
  assert.ok(r3.nouveauxAccessoires.some(a => a.id === "chapeau-alu"));
  assert.deepEqual(r3.contextes.slice(0, 2), ["quiz_zero", "nuit"]);
  const rep = M.replique(C, P3, r3.contextes, () => 0);
  assert.equal(rep.contexte, "quiz_zero"); assert.equal(P3.repliques[0], rep.id);
  assert.notEqual(M.replique(C, P3, ["quiz_zero"], () => 0).id, rep.id);
  // Trois échecs d'affilée sur le même quiz
  M.terminerQuiz(C, P3, "chim.liaisons", qs, nuit);
  r3 = M.terminerQuiz(C, P3, "chim.liaisons", qs, nuit);
  assert.ok(r3.nouveauxSucces.some(s => s.id === "perseverance"));
  // Mode test, retour après absence, réplique du jour
  assert.ok(M.avancerHorloge(C, P3, 7).succes.some(s => s.id === "voyageur-temporel"));
  assert.equal(M.noterVisite(C, P3, nuit + 20 * jour).succes.some(s => s.id === "schrodinger"), true);
  assert.equal(M.repliqueDuJour(C, P3, nuit + 20 * jour).contexte, "retour");
  // Rang d'avatar
  assert.equal(M.rangAvatar(C, P3).id, "etudiant");
  console.log("OK : migration v1 → v2, nouvelles branches, succès moqueurs, objets, accessoires, narrateur");
}
