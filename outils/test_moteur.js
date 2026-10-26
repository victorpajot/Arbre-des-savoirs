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
  assert.equal(P3.format, 4);
  assert.equal(P3.compteurs.quizParfaits, 1); assert.equal(P3.compteurs.quizJoues, 0);
  assert.deepEqual(P3.avatar, { tete: null, visage: null, main: null, savant: null });
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
  assert.equal(rep.contexte, "quiz_zero"); assert.equal(P3.repliques.quiz_zero[0], rep.id);
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

// v3 : plateau, frise, bibliothèque, masques et répliques de l'IA
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json") };
  const C3 = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const R = C3.plateau.regles, cases = C3.plateau.cases;
  const t0 = new Date(2026, 9, 26, 10, 0).getTime();
  const tous = (P, id, ok, chrono) => M.tirerQuestions(C3, P, id, 5).map((q, i) => ({ id: q.id, correct: i < ok, chrono: !!chrono }));

  // Barème annoncé = barème appliqué, avec et sans bonus du jour
  {
    const P = M.nouvellePartie(t0);
    const bonus = M.bonusDuJour(C3, P, t0);
    assert.equal(M.bonusDuJour(C3, P, t0 + 3600000), bonus, "bonus stable dans la journée");
    for (const id of ["math.arithmetique", "phys.unites", "philo.antiquite"]) {
      const Q = M.nouvellePartie(t0);
      const v = M.valeurEpreuve(C3, Q, { type: "quiz", comp: id }, t0);
      assert.equal(v.base, R.valeurs.quiz_rang["1"]);
      assert.equal(v.duJour, C3.parId[id].stat === M.bonusDuJour(C3, Q, t0) ? R.bonus.du_jour : 0);
      const r = M.terminerQuiz(C3, Q, id, tous(Q, id, 4), t0);
      assert.equal(r.plateau.a - r.plateau.de, v.total, id + " : réussi, non parfait");
      assert.equal(r.plateau.valeurs.total, v.total);
    }
    const Q = M.nouvellePartie(t0);
    const v = M.valeurEpreuve(C3, Q, { type: "quiz", comp: "math.arithmetique" }, t0);
    let r = M.terminerQuiz(C3, Q, "math.arithmetique", tous(Q, "math.arithmetique", 3), t0);
    assert.equal(r.plateau.a, 1, "quiz raté : on reste sur place");
    r = M.terminerQuiz(C3, Q, "math.arithmetique", tous(Q, "math.arithmetique", 5, true), t0);
    assert.equal(r.plateau.valeur, v.total + R.bonus.parfait + R.bonus.chrono, "parfait et chrono");
  }

  // Rappel raté : recul de 2 cases, jamais avant le départ
  {
    const P = M.nouvellePartie(t0);
    M.terminerQuiz(C3, P, "math.arithmetique", tous(P, "math.arithmetique", 4), t0);
    const avant = P.plateau.position;
    const r = M.terminerRappel(C3, P, "math.arithmetique", tous(P, "math.arithmetique", 0).slice(0, 3), t0 + 86400000);
    assert.equal(r.plateau.a, Math.max(1, avant + R.echec.rappel));
    assert.equal(P.compteurs.reculs, 1);
  }

  // Chaque case spéciale applique sa règle
  {
    const sur = (n, pas) => { const P = M.nouvellePartie(t0); P.plateau.position = n - pas; return [P, M.deplacer(C3, P, pas, t0, "test")]; };
    const num = id => cases.find(c => c.id === id).n;
    let [P, dep] = sur(9, 3);
    assert.equal(dep.a, 12, "Eurêka : on rejoue la même distance"); assert.equal(P.compteurs.eurekas, 1);
    [P, dep] = sur(num("incendie"), 1);
    assert.equal(dep.a, num("incendie") - 3, "incendie : recul de 3");
    [P, dep] = sur(num("fibonacci"), 1);
    assert.equal(dep.etapes[0].type, "avance"); assert.equal(dep.a, num("fibonacci") + 3);
    assert.equal(P.plateau.quarantaine, 1, "Fibonacci + 3 mène à la peste");
    dep = M.deplacer(C3, P, 4, t0, "test");
    assert.equal(dep.a, dep.de, "quarantaine : une épreuve réussie sans bouger");
    dep = M.deplacer(C3, P, 4, t0, "test");
    assert.equal(dep.a, dep.de + 4);
    [P, dep] = sur(num("galilee-proces"), 2);
    assert.equal(P.plateau.prison, 1);
    assert.equal(M.deplacer(C3, P, 3, t0, "test").a, num("galilee-proces"), "prison : on ne bouge plus");
    const r = M.terminerQuiz(C3, P, "math.arithmetique", tous(P, "math.arithmetique", 5), t0);
    assert.equal(P.plateau.prison, 0); assert.ok(r.plateau.contextes.includes("prison_liberation"));
    assert.ok(r.plateau.a > num("galilee-proces"), "libéré par un quiz parfait, et on avance");
    assert.ok(r.nouveauxSucces.some(s => s.id === "eppur-si-muove"));
    [P, dep] = sur(num("guillotine"), 1);
    assert.equal(dep.a, cases[num("guillotine") - 1].special.vers, "guillotine : retour au début de l'époque");
    [P, dep] = sur(num("solvay"), 3);
    assert.equal(dep.a, num("solvay") - 4);
    // Deuxième tour : pièges doublés, prison à deux quiz parfaits
    P = M.nouvellePartie(t0); P.plateau.tours = 1; P.plateau.position = num("solvay") - 3;
    assert.equal(M.deplacer(C3, P, 3, t0, "test").a, num("solvay") - 8);
    P.plateau.position = num("galilee-proces") - 2; M.deplacer(C3, P, 2, t0, "test");
    assert.equal(P.plateau.prison, 2);
  }

  // Du feu à l'IA en mode test, puis un nouveau tour
  {
    const P = M.nouvellePartie(t0);
    let garde = 0, fini = null;
    while (!fini && garde++ < 200) {
      const dep = M.avancerPion(C3, P, 2 + (garde % 3), t0);
      if (P.plateau.prison) P.plateau.prison = 0; // le test ne passe pas de quiz : on ouvre la porte
      if (dep.etapes.some(e => e.type === "tour_fini")) fini = dep;
    }
    assert.ok(fini, "arrivée atteinte");
    assert.equal(P.plateau.tours, 1); assert.equal(P.plateau.position, R.depart);
    assert.ok(fini.contextes.includes("tour_fini"));
    assert.ok(P.succes["tour-complet"]);
    const rec = M.verifierRecompenses(C3, P, t0);
    const casesFrise = C3.evenements.filter(e => e.case);
    assert.ok(casesFrise.every(e => P.evenements[e.id]), "toutes les dates du plateau sont sur la frise");
    assert.ok(C3.livres.filter(l => l.condition.type === "case_atteinte").every(l => P.livres[l.id]), "livres du plateau débloqués");
    assert.ok(P.succes["epoque-xxe"]);
    assert.equal(M.masqueActuel(C3, P).id, "promethee", "un tour complet débloque le masque de Prométhée");
  }

  // Masques par paliers de succès, annoncés au changement
  {
    const P = M.nouvellePartie(t0);
    M.verifierRecompenses(C3, P, t0);
    assert.equal(P.masque, "theatre");
    for (let i = 0; i < 8; i++) P.succes["test-" + i] = t0;
    const rec = M.verifierRecompenses(C3, P, t0);
    assert.deepEqual(rec.masques.map(m => m.id), ["talos", "golem"]); assert.equal(P.masque, "golem");
    P.succes["nains-geants"] = t0;
    assert.equal(M.verifierRecompenses(C3, P, t0).masque.id, "alphago");
    assert.equal(M.masqueActuel(C3, P).id, "alphago");
    assert.equal(M.expression(C3, "quiz_rate"), "moqueuse");
  }

  // Répliques : pas de redite avant d'avoir épuisé le contexte, jetons remplacés
  {
    const P = M.nouvellePartie(t0);
    const n = C3.commentairesPar.eureka.length, vues = new Set();
    for (let i = 0; i < n; i++) vues.add(M.replique(C3, P, ["eureka"]).id);
    assert.equal(vues.size, n);
    const der = P.repliques.eureka[0];
    assert.notEqual(M.replique(C3, P, ["eureka"]).id, der, "pas d'enchaînement au changement de cycle");
    const b = M.replique(C3, P, ["bonus_du_jour"], Math.random, { stat: "Sagesse" });
    assert.ok(b.texte.fr.includes("Sagesse") && !b.texte.fr.includes("{"));
    assert.ok(["neutre", "moqueuse", "impressionnee", "decue", "impatiente"].includes(b.expression));
  }

  // Migration v2 → v3 : rien de perdu, plateau au départ, dates et livres rattrapés
  {
    const v2 = { format: 2, cree: t0, maj: t0, decalage: 0, succes: { "premier-pas": t0, "eureka": t0 }, objets: { boulier: t0 },
      accessoires: { "lunettes-rondes": t0 }, avatar: { tete: null, visage: "lunettes-rondes", main: "boulier" },
      jours: ["2026-10-24"], journal: [], repliques: ["accueil.01"], derniereVisite: t0, retour: null, options: { chrono: true },
      compteurs: { quizParfaits: 2, quizRates: 1, rappelsReussis: 0, serieRappels: 0, perdues: 0, regagnees: 0, quizJoues: 3 },
      competences: { "psy.memoire": { maitrise: true, maitriseDepuis: t0, palier: 1, prochainRappel: t0 + 3 * 86400000, xp: 80 } } };
    const P = M.migrer(JSON.parse(JSON.stringify(v2)));
    assert.equal(P.format, 4);
    assert.deepEqual(Object.keys(P.succes), ["premier-pas", "eureka"]);
    assert.equal(P.avatar.main, "boulier"); assert.equal(P.options.chrono, true);
    assert.equal(P.compteurs.quizJoues, 3); assert.equal(P.compteurs.eurekas, 0);
    assert.equal(P.plateau.position, 1); assert.deepEqual(P.repliques, {});
    assert.equal(M.xpParStat(C3, P).empathie, 80);
    const rec = M.verifierRecompenses(C3, P, t0);
    assert.ok(rec.evenements.some(e => e.id === "ebbinghaus") && rec.evenements.some(e => e.id === "feu"));
    assert.ok(rec.livres.some(l => l.id === "memoire"));
    assert.equal(rec.masque, null, "le premier masque se pose sans annonce");
  }
  console.log("OK : v3 plateau (barème, cases spéciales, tour complet), frise, bibliothèque, masques, répliques, migration v2 → v3");
}

// v4 : second losange, XP de rappel croissante, 20 niveaux, migration v3 → v4
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json") };
  const C4 = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const t0 = new Date(2026, 9, 26, 10, 0).getTime();
  const tous = (P, id, ok) => M.tirerQuestions(C4, P, id, 5).map((q, i) => ({ id: q.id, correct: i < ok }));
  assert.deepEqual([1, 2, 7, 12].map(i => M.xpRappel(C4, i)), [5, 10, 50, 50]);
  assert.equal(C4.parStat.logique.length, 8);
  assert.equal(C4.regles.xp.paliers_niveau.length - 1, 20);

  // Le second losange s'ouvre quand le sommet du premier est maîtrisé
  {
    const P = M.nouvellePartie(t0);
    const L = C4.parStat.logique.map(k => k.id);
    for (const id of L.slice(0, 4)) M.terminerQuiz(C4, P, id, tous(P, id, 5), t0);
    assert.equal(M.statut(C4, P, L[4], t0).etat, "disponible");
    assert.equal(M.statut(C4, P, L[5], t0).etat, "verrouillee");
    assert.ok(P.succes["branche-logique"], "le premier losange suffit au succès de branche");
    const r = M.terminerQuiz(C4, P, L[4], tous(P, L[4], 5), t0);
    assert.ok(r.nouveauxSucces.some(s => s.id === "plus-ultra"));
    assert.equal(M.statut(C4, P, L[7], t0).etat, "verrouillee");
    for (const id of L.slice(5)) M.terminerQuiz(C4, P, id, tous(P, id, 5), t0);
    assert.ok(P.succes["nains-geants"] && P.succes["cultiver-jardin"]);
  }

  // Un an de jeu accéléré : une branche complète, tous les rappels réussis à l'heure, dépasse le niveau 10
  {
    const P = M.nouvellePartie(t0);
    const L = C4.parStat.logique.map(k => k.id);
    let t = t0;
    for (let jourN = 0; jourN < 365; jourN++, t += jour) {
      // une nouvelle compétence par semaine tant qu'il en reste
      if (jourN % 7 === 0) {
        const k = L.find(id => M.statut(C4, P, id, t).etat === "disponible");
        if (k) M.terminerQuiz(C4, P, k, tous(P, k, 5), t);
      }
      for (const rap of M.rappelsDus(C4, P, t)) {
        const id = rap.id || rap;
        M.terminerRappel(C4, P, id, M.tirerQuestions(C4, P, id, 3).map(q => ({ id: q.id, correct: true })), t);
      }
    }
    const n = M.niveau(C4, M.xpParStat(C4, P).logique).niveau;
    assert.ok(n > 10, "niveau après un an : " + n);
    console.log("OK : un an de jeu sur une branche, niveau " + n + " sur 20");
  }

  // Migration v3 → v4 : l'XP des rappels déjà faits est recalculée au nouveau barème
  {
    const v3 = { format: 3, cree: t0, maj: t0, decalage: 0, succes: {}, objets: {}, accessoires: {}, avatar: { tete: null, visage: null, main: null },
      jours: [], journal: [], repliques: {}, options: {},
      competences: { "biais.confirmation": { maitrise: true, maitriseDepuis: t0, palier: 4, prochainRappel: t0 + jour, xp: 90 },
                     "biais.ancrage": { maitrise: false, palier: 0, xp: 0 } } };
    const P = M.migrer(JSON.parse(JSON.stringify(v3)), C4);
    assert.equal(P.format, 4); assert.equal(P.avatar.savant, null);
    assert.equal(P.competences["biais.confirmation"].xp, 90 + 0 + 5 + 10 + 15);
    assert.equal(P.competences["biais.ancrage"].xp, 0);
    assert.equal(M.migrer(JSON.parse(JSON.stringify(P)), C4).competences["biais.confirmation"].xp, 120, "pas de double crédit");
  }
  console.log("OK : v4 second losange, XP de rappel, migration v3 → v4");
}

// v4 : savants jouables
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json") };
  const C4 = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const t0 = new Date(2026, 9, 26, 10, 0).getTime();
  const P = M.nouvellePartie(t0);
  assert.equal(C4.avatar.savants.length, 20);
  assert.deepEqual(M.verifierRecompenses(C4, P, t0).savants, []);
  // Hypatie arrive avec l'astronomie d'observation
  P.competences["astro.observer"] = { maitrise: true, maitriseDepuis: t0, palier: 0, prochainRappel: t0 + 86400000, xp: 70 };
  const rec = M.verifierRecompenses(C4, P, t0);
  assert.deepEqual(rec.savants.map(s => s.id), ["hypatie"]);
  assert.ok(P.savants.hypatie);
  console.log("OK : v4 savants débloqués par leur histoire");
}

// v5 : bouton « Jouer », masques selon le ton, apartés, farces
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json") };
  const C5 = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const t0 = new Date(2026, 9, 27, 10, 0).getTime();
  const juste = (P, id, n, ok) => M.tirerQuestions(C5, P, id, n).map((q, i) => ({ id: q.id, correct: i < ok }));

  // L'IA choisit : un quiz ouvert au départ, un rappel dû avant tout
  {
    const P = M.nouvellePartie(t0);
    const c = M.choixIA(C5, P, t0);
    assert.equal(c.type, "quiz"); assert.ok(["bonus", "faible", "hasard"].includes(c.raison));
    assert.equal(M.choixIA(C5, P, t0).comp.id, c.comp.id, "même choix tant qu'on n'a pas joué");
    const r = M.terminerQuiz(C5, P, c.comp.id, juste(P, c.comp.id, 5, 5), t0, { jouer: true });
    const sans = M.valeurEpreuve(C5, P, { type: "quiz", comp: c.comp.id }, t0).total + C5.plateau.regles.bonus.parfait;
    assert.equal(r.plateau.bonusJouer, 2); assert.equal(r.plateau.valeur, sans + 2, "+2 cases par le bouton Jouer");
    const t1 = t0 + 2 * jour;
    const c2 = M.choixIA(C5, P, t1);
    assert.equal(c2.type, "rappel"); assert.equal(c2.comp.id, c.comp.id);
    const raisons = new Set();
    for (let i = 0; i < 40; i++) { P.journal.push({}); const x = M.choixIA(C5, P, t0); if (x) raisons.add(x.raison); }
    assert.ok(raisons.size >= 2, "l'IA varie ses raisons");
  }

  // Masques : l'IA choisit selon le ton, jamais un masque verrouillé
  {
    const P = M.nouvellePartie(t0);
    M.verifierRecompenses(C5, P, t0);
    assert.equal(M.masquePourTon(C5, P, "moqueuse", "a").id, "theatre");
    for (let i = 0; i < 30; i++) P.succes["test-" + i] = t0;
    M.verifierRecompenses(C5, P, t0);
    const portes = {};
    ["moqueuse", "decue", "impressionnee", "impatiente", "neutre"].forEach(ton => {
      for (let i = 0; i < 30; i++) {
        const m = M.masquePourTon(C5, P, ton, "graine" + i);
        assert.ok(M.masqueDebloque(P, m.id)); assert.ok(m.tons.includes(ton), m.id + " va au ton " + ton);
        portes[m.id] = 1;
      }
    });
    assert.ok(Object.keys(portes).length >= 5, "une semaine de répliques : plusieurs masques");
    assert.ok(!("choisirMasque" in M));
  }

  // Apartés : l'IA cite objets et livres gagnés, environ une réplique sur deux
  {
    const P = M.nouvellePartie(t0);
    assert.equal(M.aparte(C5, P, "moqueuse", "x"), null, "rien à citer sans objet ni livre");
    P.objets["lunette-galilee"] = t0; P.livres[C5.livres[0].id] = t0;
    let n = 0;
    for (let i = 0; i < 60; i++) {
      const a = M.aparte(C5, P, "moqueuse", "g" + i);
      if (!a) continue; n++;
      assert.ok(!a.texte.fr.includes("{")); assert.ok(a.objet || a.livre);
      if (a.objet) assert.equal(a.objet.id, "lunette-galilee");
    }
    assert.ok(n >= 20, "au moins une réplique sur trois cite un objet ou un livre (" + n + "/60)");
  }

  // Farces : après un échec, une fois sur trois, pour 24 h ; « Rendre mon visage » l'annule
  {
    const P = M.nouvellePartie(t0);
    const id = C5.competences.filter(k => k.rang === 1)[0].id;
    const r0 = M.terminerQuiz(C5, P, id, juste(P, id, 5, 1), t0, { alea: () => 0.9 });
    assert.equal(r0.farce, null);
    const r1 = M.terminerQuiz(C5, P, id, juste(P, id, 5, 1), t0, { alea: () => 0.1 });
    assert.ok(r1.farce && r1.farce.type === "accessoire");
    assert.ok(M.farceActive(P, t0 + 3600e3)); assert.equal(M.farceActive(P, t0 + jour + 1), null, "la farce s'efface après 24 h");
    const r2 = M.terminerQuiz(C5, P, id, juste(P, id, 5, 5), t0, { alea: () => 0.1 });
    assert.equal(r2.farce, null, "pas de farce sur une réussite");
    M.rendreVisage(P); assert.equal(M.farceActive(P, t0), null);
  }

  // Migration : une sauvegarde v4 avec un masque choisi se charge, le choix est oublié
  {
    const v4 = JSON.parse(JSON.stringify(M.nouvellePartie(t0))); v4.masqueChoisi = "theatre"; delete v4.farce;
    v4.competences["math.arithmetique"] = { maitrise: true, palier: 2, xp: 90, prochainRappel: t0 };
    const p = M.migrer(v4, C5);
    assert.ok(!("masqueChoisi" in p)); assert.equal(p.farce, null); assert.equal(p.competences["math.arithmetique"].xp, 90);
  }
  console.log("OK : v5 bouton Jouer, masques selon le ton, apartés, farces, migration");
}
