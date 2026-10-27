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
assert.deepEqual(r.nouveauxSucces.map(s => s.id).filter(id => id !== "honte-1"), ["tour-de-pise"]);
r = M.terminerQuiz(C, P, "math.arithmetique", res("math.arithmetique", 5, 5), t);
assert.equal(r.issue, "maitrisee"); assert.equal(r.xp, 70);
assert.deepEqual(r.nouveauxSucces.map(s => s.id).sort(), ["einstein-notes", "eureka", "premier-pas"]);
// v6 : objets et accessoires deviennent du butin gagnable ; ici, sans plateau, aucun ne tombe
assert.deepEqual(r.nouveauxObjets, []);
assert.ok(P.gagnables["objets:boulier"] && P.gagnables["accessoires:lunettes-rondes"] && P.gagnables["accessoires:coiffure-einstein"]);
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
  assert.ok(rec.gagnables.some(o => o.id === "tableau-mendeleiev"));
  // Quiz raté en 20 s, à 3 h du matin, avec des réponses éclair : la panoplie moqueuse
  const nuit = new Date(2026, 9, 25, 3, 0).getTime();
  const qs = M.tirerQuestions(C, P3, "chim.liaisons", 5).map(q => ({ id: q.id, correct: false, ms: 900 }));
  let r3 = M.terminerQuiz(C, P3, "chim.liaisons", qs, nuit, { duree: 20000 });
  const ids = r3.nouveauxSucces.map(s => s.id);
  for (const id of ["dix-pour-cent", "insomniaque", "table-rase", "neutrinos", "tour-de-pise"]) assert.ok(ids.includes(id), id);
  assert.ok(P3.gagnables["accessoires:chapeau-alu"], "chapeau gagnable après la panoplie moqueuse");
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
    dep = M.deplacer(C3, P, 3, t0, "test");
    assert.equal(dep.a, dep.de + 3);
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
      const dep = M.avancerPion(C3, P, 2 + (garde % 3) + (garde % 7 === 0 ? 1 : 0), t0);
      if (P.plateau.prison) P.plateau.prison = 0; // le test ne passe pas de quiz : on ouvre la porte
      if (dep.etapes.some(e => e.type === "tour_fini")) fini = dep;
    }
    assert.ok(fini, "arrivée atteinte");
    assert.equal(P.plateau.tours, 1); assert.equal(P.plateau.position, R.depart);
    assert.ok(fini.contextes.includes("tour_fini"));
    assert.ok(P.succes["tour-complet"]);
    const rec = M.verifierRecompenses(C3, P, t0);
    // v15 : seules les cases où le pion s'est arrêté dévoilent leur date et leurs livres.
    const casesFrise = C3.evenements.filter(e => e.case);
    assert.ok(casesFrise.every(e => !!P.evenements[e.id] === !!P.plateau.visites[e.case]), "une date par case foulée, aucune par case survolée");
    assert.ok(casesFrise.some(e => !P.evenements[e.id]), "des cases survolées restent cachées");
    assert.ok(C3.livres.filter(l => l.condition.type === "case_atteinte").every(l => !P.plateau.visites[l.condition.n] || P.livres[l.id] || P.gagnables["livres:" + l.id]), "livres des cases foulées gagnables");
    assert.ok(P.succes["epoque-xxe"]);
    assert.ok(P.masques.promethee || P.gagnables["masques:promethee"], "un tour complet rend gagnable le masque de Prométhée");
  }

  // Masques par paliers de succès, annoncés au changement
  {
    const P = M.nouvellePartie(t0);
    M.verifierRecompenses(C3, P, t0);
    assert.equal(P.masque, "theatre");
    for (let i = 0; i < 8; i++) P.succes["test-" + i] = t0;
    const rec = M.verifierRecompenses(C3, P, t0);
    assert.deepEqual(rec.gagnables.map(m => m.id), ["talos", "golem"]); assert.equal(P.masque, "theatre");
    const ouverts = M.butinOuvert(C3, P).map(b => b.chose.id);
    const b = M.tirerButin(C3, P, { type: "rappel" }, t0, () => 0);
    assert.equal(b.famille, "masques"); assert.ok(ouverts.includes(b.chose.id));
    assert.equal(M.masqueActuel(C3, P).id, b.chose.id, "le masque tombé devient le dernier gagné");
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
    assert.ok(rec.gagnables.some(l => l.id === "memoire"));
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
  assert.equal(C4.avatar.savants.length, 40, "v7 : quarante savants");
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

  // Une seule case : l'arbre choisi par le joueur, rien dans un arbre fermé
  {
    const P = M.nouvellePartie(t0);
    const ouverts = C5.stats.filter(s => M.arbreOuvert(C5, P, s.id)), ferme = C5.stats.find(s => !M.arbreOuvert(C5, P, s.id));
    ouverts.forEach(s => { const c = M.choixArbre(C5, P, t0, s.id); if (c) assert.equal(c.comp.stat, s.id, "compétence de l'arbre choisi"); });
    assert.ok(ouverts.some(s => M.choixArbre(C5, P, t0, s.id)), "au moins un arbre jouable au départ");
    if (ferme) assert.equal(M.choixArbre(C5, P, t0, ferme.id), null, "arbre fermé : rien");
    console.log("OK : une seule case, arbre au choix");
  }

  // L'IA choisit : un quiz ouvert au départ, un rappel dû avant tout
  {
    const P = M.nouvellePartie(t0);
    const c = M.choixIA(C5, P, t0);
    assert.equal(c.type, "quiz"); assert.ok(["case", "hors_case"].includes(c.raison));
    assert.equal(M.choixIA(C5, P, t0).comp.id, c.comp.id, "même choix tant qu'on n'a pas joué");
    const r = M.terminerQuiz(C5, P, c.comp.id, juste(P, c.comp.id, 5, 5), t0, { jouer: true });
    const sans = M.valeurEpreuve(C5, P, { type: "quiz", comp: c.comp.id }, t0).total + C5.plateau.regles.bonus.parfait;
    assert.equal(r.plateau.bonusJouer, 2); assert.equal(r.plateau.valeur, sans + 2, "+2 cases par le bouton Jouer");
    const t1 = t0 + 2 * jour;
    const c2 = M.choixIA(C5, P, t1);
    assert.equal(c2.type, "rappel"); assert.equal(c2.comp.id, c.comp.id);
    // v15 : une case d'arbre fermé lance son premier quiz ; raté, l'arbre reste fermé ; réussi, il s'ouvre.
    {
      const O = M.nouvellePartie(t0); O.plateau.position = 4;
      const x = M.choixIA(C5, O, t0);
      assert.equal(x.raison, "ouvre_arbre"); assert.equal(x.stat, "eloquence");
      M.terminerQuiz(C5, O, x.comp.id, juste(O, x.comp.id, 5, 0), t0);
      assert.ok(!M.arbreOuvert(C5, O, "eloquence"), "raté : toujours fermé");
      O.plateau.position = 4;
      M.terminerQuiz(C5, O, x.comp.id, juste(O, x.comp.id, 5, 5), t0 + 1000);
      assert.ok(M.arbreOuvert(C5, O, "eloquence"), "réussi : ouvert");
    }
    // v15 : pas de livre anachronique ; un livre tiré vient de l'époque de la case quand il y en a.
    {
      const B = M.nouvellePartie(t0); B.plateau.position = 4;
      C5.livres.forEach(l => { B.gagnables["livres:" + l.id] = { famille: "livres", id: l.id, depuis: t0 }; });
      assert.ok(M.butinOuvert(C5, B).filter(b => b.famille === "livres").every(b => Number(b.chose.annee) <= 475), "rien après l'Antiquité en case 4");
      for (let i = 0; i < 20; i++) {
        const b = M.tirerButin(C5, B, { type: "duel" }, t0, () => 0.01 * i);
        if (b && b.famille === "livres") assert.ok(Number(b.chose.annee) <= 475);
      }
    }
    // v15 : la case du pion dicte l'arbre de l'épreuve ; arbre sans rien de jouable, l'IA improvise hors case.
    const Q = M.nouvellePartie(t0);
    C5.plateau.cases.forEach(k => {
      Q.plateau.position = k.n;
      const x = M.choixIA(C5, Q, t0);
      const jouable = M.disponibles(C5, Q, t0).some(c => c.stat === k.stat);
      const ferme = !M.arbreOuvert(C5, Q, k.stat);
      assert.equal(x.raison, ferme ? "ouvre_arbre" : jouable ? "case" : "hors_case", "case " + k.n);
      if (ferme) { assert.equal(x.comp.stat, k.stat); assert.equal(x.comp.rang, 1); }
      if (jouable) assert.equal(x.comp.stat, k.stat, "épreuve de l'arbre de la case " + k.n);
      assert.equal(x.kase.n, k.n);
    });
  }

  // Masques : l'IA choisit selon le ton, jamais un masque verrouillé
  {
    const P = M.nouvellePartie(t0);
    M.verifierRecompenses(C5, P, t0);
    assert.equal(M.masquePourTon(C5, P, "moqueuse", "a").id, "theatre");
    for (let i = 0; i < 30; i++) P.succes["test-" + i] = t0;
    M.verifierRecompenses(C5, P, t0);
    Object.values(P.gagnables).forEach(g => { if (g.famille === "masques") P.masques[g.id] = t0; });
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

// v6 : butin rare par lots de tour, avance au rang, savant incarné automatique
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json") };
  const C6 = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const t0 = new Date(2026, 9, 28, 10, 0).getTime();
  const juste = (P, id, n, ok) => M.tirerQuestions(C6, P, id, n).map((q, i) => ({ id: q.id, correct: i < ok }));

  // Avance = rang de la compétence ; +2 par le bouton Jouer
  {
    const k3 = C6.competences.filter(k => k.rang === 3)[0];
    const P = M.nouvellePartie(t0);
    assert.equal(M.valeurEpreuve(C6, P, { type: "quiz", comp: k3.id }, t0).total, 3);
    assert.equal(M.valeurEpreuve(C6, P, { type: "rappel", comp: k3.id }, t0).total, 3);
    const k1 = C6.competences.filter(k => k.rang === 1)[0];
    const r = M.terminerQuiz(C6, P, k1.id, juste(P, k1.id, 5, 5), t0, { jouer: true, alea: () => 0.99 });
    assert.equal(r.plateau.valeur, 3, "rang 1 + 2 pour Jouer, sans bonus parfait");
  }

  // Simulation : au plus un butin par épreuve, aucun lot avant son tour, collection incomplète au tour 7
  {
    let seed = 7; const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
    const P = M.nouvellePartie(t0); let t = t0;
    const butin = () => ["objets", "livres", "accessoires", "masques"].reduce((n, f) => n + Object.keys(P[f]).length, 0);
    const lot = {}; ["objets", "livres"].forEach(f => C6[f].forEach(x => { if (x.lot) lot[f + ":" + x.id] = x.lot; }));
    C6.avatar.accessoires.forEach(x => { lot["accessoires:" + x.id] = x.lot; }); C6.ia.masques.forEach(x => { if (x.lot) lot["masques:" + x.id] = x.lot; });
    let collectionAuTour7 = null;
    for (let j = 0; j < 400 && P.plateau.tours < 8; j++) {
      M.verifierRecompenses(C6, P, t);
      const faire = M.rappelsDus(C6, P, t).map(k => ({ comp: k, type: "rappel" }));
      for (let n = 0; n < 3; n++) { const c = M.choixIA(C6, P, t); if (c && (c.type === "quiz" || c.raison === "revision")) faire.push(c); }
      for (const c of faire) {
        if (c.type === "quiz" && !M.disponibles(C6, P, t).some(k => k.id === c.comp.id)) continue;
        const avant = butin(), reliques = Object.keys(P.objets).filter(id => !lot["objets:" + id]).length;
        const q = M.tirerQuestions(C6, P, c.comp.id, c.type === "rappel" ? 3 : 5).map(x => ({ id: x.id, correct: rnd() < 0.85 }));
        const res = (c.type === "rappel" ? M.terminerRappel : M.terminerQuiz)(C6, P, c.comp.id, q, t, { jouer: true, alea: rnd });
        const nouvellesReliques = Object.keys(P.objets).filter(id => !lot["objets:" + id]).length - reliques;
        const cadeaux = res.plateau ? res.plateau.etapes.filter(e => e.type === "cadeau").length : 0;
        assert.ok(butin() - avant - nouvellesReliques <= 1 + cadeaux, "au plus un butin par épreuve, plus les cases cadeau");
        ["objets", "livres", "accessoires", "masques"].forEach(f => Object.keys(P[f]).forEach(id => {
          const l = lot[f + ":" + id];
          if (l && P[f][id] === t) assert.ok(l <= P.plateau.tours + 1, id + " (lot " + l + ") tombé au tour " + (P.plateau.tours + 1));
        }));
        if (P.plateau.tours === 7 && collectionAuTour7 == null) collectionAuTour7 = butin();
      }
      t += 86400000;
    }
    const total = C6.objets.length + C6.livres.length + C6.avatar.accessoires.length + C6.ia.masques.length;
    assert.ok(collectionAuTour7 != null && collectionAuTour7 < total, "collection incomplète après 7 tours (" + collectionAuTour7 + "/" + total + ")");
  }

  // Savant : le dernier débloqué, sans choix du joueur
  {
    const P = M.nouvellePartie(t0);
    assert.equal(M.savantActuel(C6, P), null);
    P.savants.hypatie = t0; P.savants.archimede = t0 + 1000;
    assert.equal(M.savantActuel(C6, P).id, "archimede");
    P.avatar.savant = "hypatie";
    assert.equal(M.savantActuel(C6, P).id, "archimede", "le choix manuel est ignoré");
  }
  console.log("OK : v6 butin par lots, avance au rang, savant automatique");
}

// v7 : trois arbres fondamentaux, les autres s'ouvrent par un succès pionnier ; surnom de l'IA
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json") };
  const C7 = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const t0 = new Date(2026, 10, 2, 10, 0).getTime();
  const P = M.nouvellePartie(t0);
  assert.deepEqual(C7.stats.filter(s => M.arbreOuvert(C7, P, s.id)).map(s => s.id).sort(), ["logique", "mecanique", "savoir"]);
  assert.equal(M.statut(C7, P, "rhet.argument", t0).etat, "fermee");
  assert.ok(!M.disponibles(C7, P, t0).some(c => c.stat === "eloquence"), "pas de quiz dans un arbre fermé");
  assert.equal(M.pionnierDe(C7, "eloquence").id, "pionnier-ciceron");
  P.options.tousArbres = true;
  assert.equal(M.statut(C7, P, "rhet.argument", t0).etat !== "fermee", true, "mode test : tout est ouvert");
  P.options.tousArbres = false;
  P.succes["pionnier-ciceron"] = t0;
  assert.ok(M.arbreOuvert(C7, P, "eloquence"));
  const Q = M.nouvellePartie(t0);
  Q.competences["rhet.argument"] = { xp: 10 };
  assert.ok(M.arbreOuvert(C7, Q, "eloquence"), "une partie existante garde ses arbres");

  // Surnom : humeur selon la dernière entrée du journal, ou le succès tout juste obtenu
  const R = M.nouvellePartie(t0);
  assert.equal(M.surnom(C7, R, t0).ton, "neutre");
  R.journal.push({ type: "quiz", bonnes: 5, total: 5, xp: 30, t: t0 - 5000 });
  R.journal.push({ type: "quiz", bonnes: 0, total: 5, xp: 0, t: t0 - 1000 });
  assert.equal(M.surnom(C7, R, t0).ton, "moqueuse", "la dernière entrée compte");
  R.journal.push({ type: "rappel", bonnes: 0, total: 3, xp: -10, t: t0 });
  assert.equal(M.surnom(C7, R, t0).ton, "decue");
  R.succes["pionnier-ciceron"] = t0;
  const s = M.surnom(C7, R, t0);
  assert.ok(s.succes && s.texte.indexOf(s.succes.nom.fr) >= 0, "surnom tiré du succès");
  assert.ok(M.surnom(C7, R, t0 + 3 * 86400000).succes == null, "le succès s'efface après un jour");
  console.log("OK : v7 arbres fondamentaux, pionniers, surnom de l'IA");
}

// v7 lot 2 : ennemis sur la route, duels, bestiaire, cadeaux à l'IA
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json") };
  const C8 = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const t0 = new Date(2026, 10, 3, 10, 0).getTime();
  const P = M.nouvellePartie(t0);
  P.plateau.position = 5;
  // Le sophiste attend case 7 : un pas de 4 s'arrête dessus, il reste 2 cases.
  let dep = M.avancerPion(C8, P, 4, t0);
  assert.equal(P.plateau.position, 7);
  assert.deepEqual([P.duel.ennemi, P.duel.reste, P.duel.pret], ["sophiste", 2, true]);
  assert.ok(dep.etapes.some(e => e.type === "ennemi"));
  let qs = M.tirerDuel(C8, P, t0, Math.random);
  assert.equal(qs.length, 5);
  assert.ok(qs.every(m => m.ennemi === "sophiste"));
  // Défaite : le pion reste, le duel attend la prochaine épreuve réussie.
  let r = M.terminerDuel(C8, P, qs.map((m, i) => ({ id: m.id, correct: i > 0 })), t0);
  assert.equal(r.gagne, false);
  assert.equal(P.plateau.position, 7);
  assert.equal(P.duel.pret, false);
  assert.equal(P.bestiaire.sophiste.defaites, 1);
  dep = M.avancerPion(C8, P, 3, t0 + 1000);
  assert.equal(P.plateau.position, 7, "le pion ne passe pas sans duel");
  assert.deepEqual([P.duel.reste, P.duel.pret], [3, true]);
  // Victoire : l'ennemi part, le pion finit son trajet, succès et butin.
  const qs2 = M.tirerDuel(C8, P, t0, Math.random);
  assert.ok(qs2.every(m => !qs.some(q => q.id === m.id)), "d'abord des affirmations jamais vues");
  r = M.terminerDuel(C8, P, qs2.map(m => ({ id: m.id, correct: true })), t0 + 2000, () => 0);
  assert.ok(r.gagne && r.premiere);
  assert.equal(P.plateau.position, 10);
  assert.equal(P.duel, null);
  assert.ok(P.succes["vaincu-sophiste"]);
  assert.ok(!M.ennemisPlateau(C8, P)[7], "l'ennemi vaincu quitte le plateau");
  assert.deepEqual([P.bestiaire.sophiste.victoires, P.bestiaire.sophiste.serie, P.bestiaire.sophiste.meilleure], [1, 1, 1]);
  // Un recul fait oublier le duel.
  P.plateau.position = 13; M.avancerPion(C8, P, 4, t0);
  assert.equal(P.duel.ennemi, "platiste");
  M.avancerPion(C8, P, -2, t0);
  assert.equal(P.duel, null);
  // Fin de tour : les ennemis reviennent.
  P.duel = null; P.plateau.position = 62; delete M.ennemisPlateau(C8, P)[61];
  M.avancerPion(C8, P, 3, t0);
  assert.equal(P.plateau.tours, 1);
  // v15 : sept ennemis reviennent, choisis par l'IA, sur des postes décalés ; jamais la réserve ni une case spéciale.
  {
    const en = M.ennemisPlateau(C8, P), cases = Object.keys(en).map(Number), ids = Object.values(en);
    assert.equal(cases.length, 7); assert.equal(new Set(ids).size, 7);
    assert.ok(!ids.includes(C8.reserve));
    assert.ok(cases.every(n => n > 2 && n < 63 && !M.specialDe(C8, P, n)));
    assert.notDeepEqual(cases.sort((a, b) => a - b), [7, 15, 26, 34, 44, 52, 61], "les postes glissent");
    const nouveaux = ids.filter(id => !P.bestiaire[id]).length;
    assert.ok(nouveaux >= 5, "l'IA préfère les ennemis jamais affrontés");
  }

  // Cadeaux : un par jour, une fois par objet.
  const G = M.nouvellePartie(t0);
  G.objets = { "plaque-hubble": t0, "boulier": t0, "alambic": t0, "des-pascal": t0 };
  let c = M.donnerObjet(C8, G, "plaque-hubble", t0);
  assert.equal(c.effet.type, "avance"); assert.equal(G.plateau.position, 4);
  assert.equal(M.donnerObjet(C8, G, "boulier", t0 + 1000), null, "un seul cadeau par jour");
  assert.equal(M.cadeauPossible(C8, G, "plaque-hubble", t0 + 86400000).raison, "recent");
  c = M.donnerObjet(C8, G, "boulier", t0 + 86400000);
  assert.equal(G.objetIA, "boulier", "l'IA garde le boulier");
  c = M.donnerObjet(C8, G, "alambic", t0 + 2 * 86400000, () => 0);
  assert.equal(c.effet.type, "ennemi"); assert.equal(c.effet.ennemi.id, "charlatan", "le charlatan sort de la réserve");
  assert.equal(M.ennemisPlateau(C8, G)[c.effet.case], "charlatan");
  c = M.donnerObjet(C8, G, "des-pascal", t0 + 3 * 86400000, () => 0);
  assert.equal(c.effet.type, "echange");
  assert.equal(M.specialDe(C8, G, c.effet.de), null);
  assert.equal(M.specialDe(C8, G, c.effet.vers).type, c.effet.regle);
  console.log("OK : v7 ennemis, duels, bestiaire, cadeaux à l'IA");
}

// v8 : cases pièges (recul, téléportation, révision forcée)
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json") };
  const C9 = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const t0 = new Date(2026, 9, 28, 10, 0).getTime(), J = 86400000;
  const sur = (n, pas, P) => { P = P || M.nouvellePartie(t0); P.plateau.ennemis = {}; P.plateau.position = n - pas; return [P, M.deplacer(C9, P, pas, t0, "test")]; };
  // Téléportation : Montaigne renvoie chez Averroès.
  let [P, dep] = sur(32, 2);
  assert.equal(dep.a, 24); assert.equal(dep.etapes[0].type, "teleport"); assert.equal(dep.etapes[0].n, 8);
  // Recul : le zéro de Brahmagupta.
  [P, dep] = sur(21, 1);
  assert.equal(dep.a, 19); assert.equal(dep.etapes[0].type, "recul");
  // Révision forcée sans compétence maîtrisée : rien.
  [P, dep] = sur(11, 1);
  assert.equal(dep.etapes[0].type, "revision_vide"); assert.equal(P.revision, undefined);
  // Avec deux compétences maîtrisées : l'IA prend celle dont le rappel est le plus lointain.
  P = M.nouvellePartie(t0);
  P.competences["math.arithmetique"] = { maitrise: true, palier: 2, xp: 90, prochainRappel: t0 + 3 * J, maitriseDepuis: t0 - 9 * J };
  P.competences["math.probabilites"] = { maitrise: true, palier: 3, xp: 90, prochainRappel: t0 + 20 * J, maitriseDepuis: t0 - 30 * J };
  [P, dep] = sur(11, 1, P);
  assert.equal(P.revision.comp, "math.probabilites");
  assert.equal(M.choixIA(C9, P, t0).raison, "revision");
  dep = M.deplacer(C9, P, 3, t0, "quiz");
  assert.equal(dep.a, 11, "bloqué tant que la révision n'est pas faite"); assert.equal(dep.etapes[0].type, "bloque_revision");
  const qs = M.tirerQuestions(C9, P, "math.probabilites", 3);
  let r = M.terminerRappel(C9, P, "math.probabilites", qs.map(q => ({ id: q.id, correct: true })), t0);
  assert.ok(r.revision); assert.equal(P.revision, null); assert.equal(P.competences["math.probabilites"].palier, 3, "pas de palier gagné");
  assert.ok(r.contextes.includes("revision_reussie")); assert.ok(r.plateau.a > 11);
  // Révision ratée : la compétence reste, son rappel devient dû.
  [P, dep] = sur(42, 1, P);
  const cible = P.revision.comp;
  r = M.terminerRappel(C9, P, cible, M.tirerQuestions(C9, P, cible, 3).map(q => ({ id: q.id, correct: false })), t0 + 1000);
  assert.ok(P.competences[cible].maitrise, "pas de perte"); assert.equal(P.competences[cible].prochainRappel, t0 + 1000);
  assert.equal(r.plateau, null); assert.ok(r.contextes.includes("revision_ratee"));
  assert.ok(M.rappelsDus(C9, P, t0 + 2000).some(k => k.id === cible));
  // Case cadeau : un objet sans épreuve, montré dans les récompenses.
  P = M.nouvellePartie(t0); M.verifierRecompenses(C9, P, t0);
  P.gagnables["objets:boulier"] = { famille: "objets", id: "boulier", depuis: t0 };
  [P, dep] = sur(5, 2, P);
  assert.equal(dep.etapes[0].type, "cadeau"); assert.ok(P.objets[dep.etapes[0].id]);
  const rec = M.verifierRecompenses(C9, P, t0);
  assert.ok(rec.objets.some(o => o.id === dep.etapes[0].id), "le cadeau apparaît dans les récompenses");
  assert.equal(M.verifierRecompenses(C9, P, t0).objets.length, 0, "une seule fois");
  console.log("OK : v8 pièges, téléportation, révision forcée, cases cadeau");
}

// v9 : jeu de Mendeleïev (atomes sauvages, combat en trois questions, tableau périodique)
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") };
  const CA = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const t0 = new Date(2026, 9, 28, 10, 0).getTime();
  let P = M.nouvellePartie(t0); P.plateau.ennemis = {};
  // S'arrêter sur la case 53 fait apparaître un atome ; la traverser aussi (54 est un eurêka qui relance).
  P.plateau.position = 51;
  let dep = M.deplacer(CA, P, 2, t0, "test");
  assert.equal(dep.a, 53); assert.equal(dep.etapes[0].type, "atome"); assert.equal(dep.etapes[0].case, 53);
  assert.equal(P.sauvages.length, 1);
  const s = M.atomeSauvage(CA, P); assert.ok(s.element.symbole);
  // Les trois questions : une seule bonne réponse chacune, quatre choix distincts.
  for (let k = 0; k < 40; k++) {
    P.sauvages[0].z = 1 + (k * 7) % 118;
    const cb = M.tirerCombat(CA, P, Math.random);
    assert.equal(cb.questions.length, 3);
    cb.questions.forEach(q => {
      assert.equal(new Set(q.choix).size, q.choix.length, q.enonce + " " + q.choix);
      assert.ok(q.choix.length === 4, q.enonce + " " + q.choix);
      assert.ok(q.reponse >= 0);
    });
    assert.equal(cb.questions[0].choix[cb.questions[0].reponse], cb.element.symbole);
  }
  P.sauvages[0].z = 26;
  // Une seule bonne réponse : l'atome s'enfuit.
  let r = M.terminerCombat(CA, P, 1, t0);
  assert.ok(!r.capture); assert.equal(P.sauvages.length, 0); assert.ok(!M.estCapture(P, 26)); assert.equal(P.compteurs.atomesEnfuis, 1);
  // Deux bonnes réponses : capturé, premier succès.
  P.sauvages.push({ z: 26, case: 53, depuis: t0 });
  r = M.terminerCombat(CA, P, 2, t0 + 1);
  assert.ok(r.capture && r.premiere); assert.ok(M.estCapture(P, 26));
  assert.ok(r.recompenses.succes.some(x => x.id === "atome-1"));
  // Un atome capturé ne réapparaît pas tant qu'il en reste d'autres ; trois au plus en attente.
  for (let k = 0; k < 4; k++) { P.plateau.position = 52; dep = M.deplacer(CA, P, 1, t0 + 10 + k, "test"); }
  assert.equal(P.sauvages.length, 3); assert.equal(dep.etapes[0].type, "atome_plein");
  assert.ok(P.sauvages.every(x => x.z !== 26)); assert.equal(new Set(P.sauvages.map(x => x.z)).size, 3);
  // Famille complète : les gaz nobles.
  [2, 10, 18, 36, 54, 86, 118].forEach(z => { P.atomes[z] = { capture: t0, rencontres: 1, fuites: 0 }; });
  assert.ok(M.verifierSucces(CA, P, t0 + 100).some(x => x.id === "gaz-nobles"));
  // Migration : une ancienne partie gagne un tableau vide.
  const vieux = M.migrer(JSON.parse(JSON.stringify(Object.assign(M.nouvellePartie(t0), { atomes: undefined, sauvages: undefined }))));
  assert.deepEqual(vieux.atomes, {}); assert.deepEqual(vieux.sauvages, []);
  console.log("OK : v9 jeu de Mendeleïev, atomes sauvages, combat, tableau périodique");
}

// v10 : faveur de l'IA, cadeaux qui brillent, pièges de l'IA furieuse
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") };
  const CF = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const F = X.ia.faveur, t0 = new Date(2026, 9, 28, 10, 0).getTime(), J = 86400000;
  let P = M.nouvellePartie(t0); P.plateau.ennemis = {};
  let f = M.faveurIA(CF, P, t0);
  assert.equal(f.valeur, F.depart); assert.equal(f.palier.id, "contente");
  // Elle baisse chaque jour sans cadeau.
  f = M.faveurIA(CF, P, t0 + 3 * J); assert.equal(f.valeur, F.depart - 3 * F.baisse_par_jour); assert.equal(f.palier.id, "boudeuse");
  f = M.faveurIA(CF, P, t0 + 6 * J); assert.equal(f.palier.id, "furieuse");
  // Furieuse : butin nul, une case de moins, et un piège par jour devant le pion.
  const tF = t0 + 6 * J;
  P.competences["math.probabilites"] = { maitrise: true, palier: 1, xp: 50, prochainRappel: tF + J, maitriseDepuis: t0 };
  const v = M.valeurEpreuve(CF, P, { type: "quiz", comp: "math.probabilites" }, tF);
  assert.equal(v.faveur, -1);
  P.plateau.position = 2;
  const c = M.piegeIA(CF, P, tF);
  assert.ok(c > 2 && c <= 7); assert.equal(M.specialDe(CF, P, c).type, "recul"); assert.ok(M.specialDe(CF, P, c).ia);
  assert.equal(M.piegeIA(CF, P, tF + 1000), null, "un seul piège par jour");
  // Un cadeau éblouissant la fait remonter.
  const brillant = X.objets.objets.find(o => o.cadeau.eclat === 3), terne = X.objets.objets.find(o => o.cadeau.eclat === 1);
  P.objets[brillant.id] = t0; P.objets[terne.id] = t0;
  let r = M.donnerObjet(CF, P, brillant.id, tF, () => 0.5);
  assert.equal(r.eclat, 3); assert.equal(r.gain, F.gains["3"]); assert.equal(r.faveur.valeur, Math.min(100, r.avant.valeur + F.gains["3"]));
  assert.equal(M.cadeauPossible(CF, P, terne.id, tF + 1000).raison, "jour", "un cadeau par jour");
  // Le même objet : pas avant le délai de lassitude, puis pour moitié moins.
  assert.equal(M.cadeauPossible(CF, P, brillant.id, tF + 3 * J).raison, "recent");
  r = M.donnerObjet(CF, P, brillant.id, tF + F.lassitude_jours * J, () => 0.5);
  assert.ok(r.repete); assert.equal(r.gain, Math.round(F.gains["3"] / 2));
  // Comblée : une case de plus.
  P.faveur = { valeur: 90, maj: tF }; assert.equal(M.faveurIA(CF, P, tF).palier.id, "comblee");
  assert.equal(M.valeurEpreuve(CF, P, { type: "quiz", comp: "math.probabilites" }, tF).faveur, 1);
  assert.ok(M.repliqueDuJour(CF, P, tF).contexte === "faveur_comblee");
  const vieux = M.migrer(JSON.parse(JSON.stringify(Object.assign(M.nouvellePartie(t0), { faveur: undefined }))));
  assert.equal(vieux.faveur, null);
  console.log("OK : v10 faveur de l'IA, cadeaux brillants, pièges de l'IA");
}

// v11 : les masques du jour changent les règles, les objets tenus donnent des coups de pouce
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") };
  const CM = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const t0 = new Date(2026, 9, 28, 10, 0).getTime(), J = 86400000, Q = CM.regles.quiz.questions_par_quiz;
  const parId = {}; X.ia.masques.forEach(m => { parId[m.id] = m; });
  assert.ok(X.ia.masques.every(m => m.caractere && m.regles && m.texte_regles));
  assert.ok(X.objets.objets.every(o => o.citation && o.citation.texte && o.citation.source && o.bonus));
  let P = M.nouvellePartie(t0);
  X.ia.masques.forEach(m => { P.masques[m.id] = t0; });
  // 1 à 3 masques par jour, stables dans la journée, tirés parmi les caractères que permet la faveur.
  const vus = new Set();
  for (let k = 0; k < 30; k++) {
    const t = t0 + k * J; P.faveur = { valeur: 90, maj: t };
    const ms = M.masquesDuJour(CM, P, t);
    assert.ok(ms.length >= 1 && ms.length <= 3); vus.add(ms.length);
    assert.ok(ms.every(m => m.caractere !== "cruel"), "comblée : pas de masque cruel");
    assert.deepEqual(M.masquesDuJour(CM, P, t + 3600000).map(m => m.id), ms.map(m => m.id));
  }
  assert.ok(vus.size > 1, "le nombre de masques varie d'un jour à l'autre");
  const tF = t0 + 40 * J; P.faveur = { valeur: 5, maj: tF };
  assert.ok(M.masquesDuJour(CM, P, tF).every(m => m.caractere === "cruel"), "furieuse : masques cruels");
  // Règles cumulées.
  const imposer = (ids, t) => { P.masquesJour = { jour: M.cleJour(t), ids, renfort: null }; };
  const t1 = t0 + 50 * J; P.faveur = { valeur: 50, maj: t1 };
  imposer(["promethee", "golem", "tete-airain"], t1);
  let rj = M.reglesDuJour(CM, P, t1);
  assert.equal(rj.butin, 4); assert.equal(rj.avance, -1); assert.equal(rj.questions, -1); assert.equal(rj.echec, 2);
  assert.equal(M.questionsQuiz(CM, P, t1), Q - 1);
  imposer(["finale", "turc"], t1); assert.equal(M.questionsQuiz(CM, P, t1), Math.min(8, Q + 3));
  imposer(["homoncule"], t1); assert.equal(M.seuilAtome(CM, P, t1), Math.max(1, X.atomes.regles.seuil - 1));
  imposer(["tubes"], t1); assert.equal(M.seuilAtome(CM, P, t1), Math.min(X.atomes.regles.questions, X.atomes.regles.seuil + 1));
  // Héron : une case de plus à l'épreuve réussie.
  P.competences["math.probabilites"] = { maitrise: true, palier: 1, xp: 50, prochainRappel: t1 + J, maitriseDepuis: t0 };
  imposer(["theatre"], t1); const base = M.valeurEpreuve(CM, P, { type: "quiz", comp: "math.probabilites" }, t1).total;
  imposer(["heron"], t1); assert.equal(M.valeurEpreuve(CM, P, { type: "quiz", comp: "math.probabilites" }, t1).total, base + 1);
  // Perceptron : un piège de recul est sans effet.
  const R = X.plateau.regles;
  let caseRecul = null;
  for (let c = R.depart + 1; c < R.arrivee; c++) { const sp = M.specialDe(CM, P, c); if (sp && sp.type === "recul") { caseRecul = c; break; } }
  P.plateau.ennemis = {}; P.plateau.position = caseRecul - 1;
  imposer(["perceptron"], t1);
  let dep = M.deplacer(CM, P, 1, t1, "test");
  assert.ok(dep.etapes.some(e => e.type === "piege_evite")); assert.equal(P.plateau.position, caseRecul);
  // Bombe : les ennemis ne barrent plus la route.
  P.plateau.position = R.depart; P.plateau.ennemis = { [R.depart + 1]: CM.ennemis[0].id };
  imposer(["bombe"], t1); dep = M.deplacer(CM, P, 1, t1, "test");
  assert.equal(P.plateau.position, R.depart + 1); assert.ok(!P.duel, "pas de duel quand les ennemis sont absents");
  // Talos : un ennemi de renfort se poste devant le pion.
  const t2 = t0 + 60 * J; P.faveur = { valeur: 50, maj: t2 }; P.plateau.position = R.depart + 1; P.plateau.ennemis = {};
  P.masquesJour = null;
  const garde = X.ia.masques.filter(m => m.id !== "talos").map(m => m.id);
  garde.forEach(id => { delete P.masques[id]; }); P.masques.talos = t0;
  const ms = M.masquesDuJour(CM, P, t2);
  assert.deepEqual(ms.map(m => m.id), ["talos"]);
  const rf = P.masquesJour.renfort; assert.ok(rf && rf.case >= P.plateau.position + 2 && rf.case <= P.plateau.position + 8);
  assert.equal(P.plateau.ennemis[rf.case], rf.ennemi);
  // Objet tenu : bonus parfois, butin assuré au tirage suivant.
  const P2 = M.nouvellePartie(t0); P2.plateau.ennemis = {};
  const obj = X.objets.objets.find(o => o.bonus.type === "case");
  P2.objets[obj.id] = t0; P2.avatar.main = obj.id;
  P2.competences["math.probabilites"] = { maitrise: true, palier: 1, xp: 50, prochainRappel: t0 + 99 * J, maitriseDepuis: t0 };
  let bonus = 0;
  for (let k = 0; k < 40; k++) {
    P2.plateau.position = R.depart;
    const r = M.jouerPlateau(CM, P2, { type: "quiz", comp: "math.probabilites" }, { reussi: true }, t0 + k * 1000);
    if (r.etapes.some(e => e.type === "bonus_objet")) bonus++;
  }
  assert.ok(bonus > 2 && bonus < 25, "bonus de l'objet de temps en temps (" + bonus + "/40)");
  // Migration.
  const vieux = M.migrer(JSON.parse(JSON.stringify(Object.assign(M.nouvellePartie(t0), { masquesJour: undefined, butinAssure: undefined }))));
  assert.equal(vieux.masquesJour, null); assert.equal(vieux.butinAssure, false);
  console.log("OK : v11 masques du jour, règles cumulées, renfort, objets tenus");
}

// v12 : le mur de la honte
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") };
  const CH = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const t0 = new Date(2026, 9, 28, 10, 0).getTime(), J = 86400000;
  assert.ok(CH.competences.every(k => k.fiche && k.fiche.essentiel.length >= 3 && k.fiche.schema.startsWith("<svg")));
  const P = M.nouvellePartie(t0); P.plateau.ennemis = {};
  const qs = CH.questions.filter(q => q.competence === "math.probabilites").slice(0, 5);
  const res = qs.map((q, i) => ({ id: q.id, correct: i >= 2, rep: i < 2 ? 99 : null }));
  const r = M.terminerQuiz(CH, P, "math.probabilites", res, t0, { alea: () => 0.99 });
  assert.equal(P.oublis.length, 2); assert.equal(P.oublis[0].rep, 99); assert.equal(P.compteurs.hontes, 2);
  assert.ok(r.nouveauxSucces.some(s => s.id === "honte-1"));
  let mur = M.murDeLaHonte(CH, P, t0 + 3600000);
  assert.equal(mur.aujourdhui.length, 2); assert.equal(mur.restantes, 2); assert.equal(mur.aujourdhui[0].question.competence, "math.probabilites");
  assert.equal(M.repliqueDuJour(CH, P, t0 + 3600000).contexte, "mur_honte");
  // La même question ratée deux fois le même jour n'apparaît qu'une fois.
  M.terminerQuiz(CH, P, "math.probabilites", res, t0 + 5 * 3600000, { alea: () => 0.99 });
  assert.equal(M.murDeLaHonte(CH, P, t0 + 6 * 3600000).aujourdhui.length, 2);
  // On ne retente pas le jour même.
  const i0 = M.murDeLaHonte(CH, P, t0 + 6 * 3600000).aujourdhui[0].index;
  assert.equal(M.retenterOubli(CH, P, i0, true, t0 + 7 * 3600000), null, "pas le jour même");
  // Le lendemain, elles passent dans les jours précédents, à retenter.
  mur = M.murDeLaHonte(CH, P, t0 + J);
  assert.equal(mur.aujourdhui.length, 0); assert.equal(mur.avant.length, 2); assert.equal(mur.aRetenter, 2);
  assert.notEqual((M.repliqueDuJour(CH, P, t0 + J) || {}).contexte, "mur_honte");
  const ia = mur.avant[0].index;
  let rt = M.retenterOubli(CH, P, ia, false, t0 + J);
  assert.ok(!rt.efface && rt.replique.contexte === "honte_ratee");
  rt = M.retenterOubli(CH, P, ia, true, t0 + J + 1000);
  assert.ok(rt.efface); assert.equal(P.compteurs.hontesEffacees, 1);
  assert.equal(M.retenterOubli(CH, P, ia, true, t0 + J + 2000), null, "déjà effacée");
  assert.equal(M.murDeLaHonte(CH, P, t0 + J + 3000).aRetenter, 1, "les deux épingles de la même question sont effacées");
  // Après 30 jours, elles quittent le mur.
  M.terminerQuiz(CH, P, "math.logique", CH.questions.filter(q => q.competence === "math.logique").slice(0, 5).map(q => ({ id: q.id, correct: false })), t0 + 31 * J, { alea: () => 0.99 });
  assert.ok(P.oublis.every(e => e.t >= t0 + J), "plus de 30 jours : retiré du mur");
  const vieux = M.migrer(JSON.parse(JSON.stringify(Object.assign(M.nouvellePartie(t0), { oublis: undefined }))));
  assert.deepEqual(vieux.oublis, []);
  console.log("OK : v12 mur de la honte, retenter, fiches de révision");
}

{
  // v15 : une épreuve perdue d'avance est coupée, et le bilan compte toutes ses questions.
  assert.equal(M.epreuvePerdue(C, "quiz", 2, 3, 5), false, "2/3 puis 2 justes : 4/5, ça passe");
  assert.equal(M.epreuvePerdue(C, "quiz", 1, 3, 5), true, "1/3 : 3/5 au mieux, perdu");
  assert.equal(M.epreuvePerdue(C, "duel", 2, 3, 5), true);
  assert.equal(M.epreuvePerdue(C, "duel", 3, 3, 5), false);
  assert.equal(M.epreuvePerdue(C, "atome", 0, 2, 3, 2), true);
  const T = Date.UTC(2026, 0, 5, 9), P = M.nouvellePartie(T), id = C.competences.find(k => k.rang === 1).id;
  const qs = C.questionsPar[id].slice(0, 3);
  const r = M.terminerQuiz(C, P, id, qs.map((q, i) => ({ id: q.id, correct: i === 0 })), T, { total: 5 });
  assert.equal(r.total, 5); assert.equal(r.issue, "echec");
  console.log("OK : v15 épreuves coupées quand elles sont perdues");
}

{
  // v15 : au plus un savant, un livre ou un objet par épreuve ; le suivant attend.
  const X = { avatar: d("avatar.json"), objets: d("objets.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json") };
  const CS = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const T = Date.UTC(2026, 0, 5, 9), P = M.nouvellePartie(T);
  M.verifierRecompenses(CS, P, T);
  P.competences["astro.observer"] = { maitrise: true, maitriseDepuis: T, xp: 10 };
  P.competences["phys.ondes"] = { maitrise: true, maitriseDepuis: T, xp: 10 };
  const a = M.verifierRecompenses(CS, P, T + 1), b = M.verifierRecompenses(CS, P, T + 2);
  assert.equal(a.savants.length + a.objets.length + a.livres.length, 1, "un seul déblocage d'un coup");
  assert.ok(b.savants.length + b.objets.length + b.livres.length <= 1);
  assert.ok(P.savants.hypatie && P.savants["ibn-al-haytham"], "le second savant vient ensuite");
  console.log("OK : v15 une récompense (savant, livre, objet) par épreuve");
}

{
  // v15 : cases cachées, trou de mémoire, renvoi par un ennemi, compteur du tour, un seul pas.
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json") };
  const CP = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const T = Date.UTC(2026, 0, 5, 9);
  let P = M.nouvellePartie(T);
  P.plateau.ennemis = {};
  M.deplacer(CP, P, 3, T, "test");
  assert.ok(M.caseDecouverte(P, 4) && !M.caseDecouverte(P, 2) && !M.caseDecouverte(P, 3), "cases survolées cachées");
  const oubli = CP.plateau.cases.find(k => k.special && k.special.type === "oubli").n;
  P.plateau.position = oubli - 2; P.plateau.visites[oubli - 2] = 1;
  const dep = M.deplacer(CP, P, 2, T, "test");
  const et = dep.etapes.find(e => e.type === "oubli");
  assert.ok(et && !P.plateau.visites[et.vers - 0] === false && et.vers >= oubli - 15 && et.vers < oubli, "trou de mémoire : retour à une case jamais vue, 15 cases au plus");
  // Un pas seulement
  P = M.nouvellePartie(T); P.plateau.ennemis = {};
  const id = CP.competences.find(k => k.rang === 1).id, qs = CP.questionsPar[id].slice(0, 5);
  const r = M.terminerQuiz(CP, P, id, qs.map(q => ({ id: q.id, correct: true })), T, { jouer: true, uneCase: true });
  assert.equal(r.plateau.a, 2, "un seul pas"); assert.equal(P.plateau.coups, 1);
  // Record de tour
  P.plateau.position = CP.plateau.regles.arrivee - 1; P.plateau.coups = 9;
  const fin = M.deplacer(CP, P, 3, T, "test").etapes.find(e => e.type === "tour_fini");
  assert.equal(fin.coups, 9); assert.ok(fin.record); assert.equal(P.plateau.meilleur, 9); assert.equal(P.plateau.coups, 0);
  // Renvoi par un ennemi vainqueur
  P = M.nouvellePartie(T);
  P.plateau.position = 20; P.plateau.visites[20] = 1;
  P.duel = { ennemi: "ussher", case: 20, reste: 3, pret: true, depuis: T };
  const du = M.terminerDuel(CP, P, [{ id: "x", correct: false }], T, undefined, 5);
  assert.ok(du.plateau && du.plateau.a < 20 && !P.duel, "Ussher renvoie le pion en arrière");
  assert.equal(du.total, 5);
  console.log("OK : v15 cases cachées, trou de mémoire, renvoi, compteur du tour, un seul pas");
}

{
  // v15 : l'IA retouche exceptionnellement la route : raccourci après un quiz parfait, détour par les cases survolées après un échec.
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json") };
  const CP = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const T = Date.UTC(2026, 0, 5, 9), jamais = () => 0.99, toujours = () => 0;
  let P = M.nouvellePartie(T);
  assert.equal(M.routeTour(CP, P).length, 63);
  assert.equal(M.remanierRoute(CP, P, { reussi: true, parfait: true }, T, jamais), null, "rare : pas à chaque fois");
  const r = M.remanierRoute(CP, P, { reussi: true, parfait: true }, T, toujours);
  assert.ok(r && r.type === "raccourci" && r.cases.length >= 1 && M.routeTour(CP, P).length === 63 - r.cases.length);
  assert.ok(r.cases.every(n => M.routeTour(CP, P).indexOf(n) < 0), "cases retirées de la route");
  assert.equal(M.remanierRoute(CP, P, { reussi: false }, T, toujours), null, "au plus une fois par tour");
  P = M.nouvellePartie(T); P.plateau.ennemis = {};
  M.deplacer(CP, P, 6, T, "test");
  const ici = P.plateau.position;
  const dt = M.remanierRoute(CP, P, { reussi: false }, T, toujours);
  assert.ok(dt && dt.type === "detour" && dt.cases.every(n => n < ici && !P.plateau.visites[n]));
  const rt = M.routeTour(CP, P);
  assert.deepEqual(rt.slice(P.plateau.idx + 1, P.plateau.idx + 1 + dt.cases.length), dt.cases, "remises juste devant le pion");
  const dep = M.deplacer(CP, P, 1, T, "test");
  assert.equal(dep.a, dt.cases[0], "le pion s'y arrête au pas suivant");
  console.log("OK : v15 route retouchée par l'IA, rarement");
}
