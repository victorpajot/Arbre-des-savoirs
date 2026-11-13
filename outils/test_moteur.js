// Test du cycle complet : node outils/test_moteur.js
const fs = require("fs"), path = require("path"), assert = require("assert");
const M = require("../web/moteur.js");
// v36 : une partie neuve tire ses cases dans les arbres allumés. Les tests historiques jouent sur l'ancien plateau
// fixe (les 63 cases dans l'ordre, comme une sauvegarde d'avant) ; « plateau tiré » plus bas teste le tirage.
const nouvellePartieTiree = M.nouvellePartie;
M.nouvellePartie = function (t) { const P = nouvellePartieTiree(t); P.plateau.route = Array.from({ length: 63 }, (_, i) => i + 1); return P; };
// v19 : 4 succès au plus par épreuve ; les suivants tombent aux vérifications d'après.
const vider = (C, P, t) => { for (let i = 1; i <= 12; i++) M.verifierRecompenses(C, P, t + i); };
const succesPuis = (r, C, P, t) => r.nouveauxSucces.map(s => s.id).concat(...[1, 2, 3, 4, 5].map(i => M.verifierRecompenses(C, P, t + i).succes.map(s => s.id)));
const dBrut = n => JSON.parse(fs.readFileSync(path.join(__dirname, "../data", n), "utf8"));
// Les savoirs propres à l'île (arbres « en chantier » du pack ile : le feu, Ressources, Météo) n'existent qu'en mode Île.
// Les tests historiques jouent sans eux, comme le mode Parcours ; les tests des âges les chargent avec dBrut.
const CHANTIER = dBrut("regles.json").stats.filter(x => x.chantier).map(x => x.id);
const COMPS_CHANTIER = dBrut("skills.json").competences.filter(k => CHANTIER.includes(k.stat)).map(k => k.id);
const d = n => {
  const x = dBrut(n);
  if (n === "regles.json") x.stats = x.stats.filter(s => !CHANTIER.includes(s.id));
  if (n === "skills.json") x.competences = x.competences.filter(k => !CHANTIER.includes(k.stat));
  if (n === "questions.json") x.questions = x.questions.filter(q => !COMPS_CHANTIER.includes(q.competence));
  return x;
};
const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
  { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json") });
let t = new Date(2026, 9, 24, 9, 0).getTime();
const P = M.nouvellePartie(t);
const jour = 86400000;
const res = (id, n, ok) => M.tirerQuestions(C, P, id, n).map((q, i) => ({ id: q.id, correct: i < ok }));

assert.equal(M.statut(C, P, "math.origines", t).etat, "disponible");
assert.equal(M.statut(C, P, "math.egypte", t).etat, "verrouillee");
let r = M.terminerQuiz(C, P, "math.origines", res("math.origines", 5, 3), t);
assert.equal(r.issue, "echec");
assert.deepEqual(r.nouveauxSucces.map(s => s.id).filter(id => id !== "honte-1"), ["tour-de-pise"]);
r = M.terminerQuiz(C, P, "math.origines", res("math.origines", 5, 5), t);
assert.equal(r.issue, "maitrisee"); assert.equal(r.xp, 70);
// v19 : deux récompenses au plus par épreuve ordinaire ; les autres tombent ensuite.
assert.ok(r.nouveauxSucces.length <= 2);
{ const ids = succesPuis(r, C, P, t); for (const id of ["kushim", "premier-pas"]) assert.ok(ids.includes(id), id); }
// v6 : objets et accessoires deviennent du butin gagnable ; ici, sans plateau, aucun ne tombe
assert.deepEqual(r.nouveauxObjets, []);
assert.ok(P.gagnables["objets:boulier"] && P.gagnables["accessoires:lunettes-rondes"]);
assert.ok(r.contextes.includes("quiz_parfait_facile"));
assert.equal(M.statut(C, P, "math.egypte", t).etat, "disponible");
assert.equal(M.rappelsDus(C, P, t).length, 0);
// Rappel dû le lendemain à minuit
t += jour; assert.equal(M.rappelsDus(C, P, t).length, 1);
r = M.terminerRappel(C, P, "math.origines", res("math.origines", 3, 2), t);
assert.equal(r.issue, "reussi"); assert.equal(M.joursEntre(t, r.prochainRappel), 3);
assert.equal(M.xpParStat(C, P).logique, 75);
// Maîtriser proportions, puis perdre arithmétique : proportions est gelée, algèbre (rang 4) reste verrouillée
r = M.terminerQuiz(C, P, "math.egypte", res("math.egypte", 5, 4), t);
assert.equal(r.issue, "maitrisee");
r = M.terminerQuiz(C, P, "math.babylone", res("math.babylone", 5, 4), t);
assert.equal(M.statut(C, P, "math.geometrie", t).etat, "disponible");
t += 3 * jour;
r = M.terminerRappel(C, P, "math.origines", res("math.origines", 3, 1), t);
assert.equal(r.issue, "perdue"); assert.equal(r.xpPerdue, 75);
assert.ok(succesPuis(r, C, P, t).includes("lucide"));
assert.equal(M.statut(C, P, "math.origines", t).etat, "disponible");
assert.equal(M.statut(C, P, "math.egypte", t).gelee, true);
assert.equal(M.statut(C, P, "math.archimede", t).etat, "verrouillee");
r = M.terminerQuiz(C, P, "math.origines", res("math.origines", 5, 4), t);
assert.ok(succesPuis(r, C, P, t).includes("resilience"));
assert.equal(M.statut(C, P, "math.egypte", t).gelee, false);
// Questions récentes évitées
const vues = P.competences["math.origines"].recentes;
const tir = M.tirerQuestions(C, P, "math.origines", 5).map(q => q.id);
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
                   "sci.egypte": { maitrise: true, maitriseDepuis: t0, palier: 0, prochainRappel: t0 + jour, xp: 60 },
                   "sci.soigner": { maitrise: true, maitriseDepuis: t0, palier: 0, prochainRappel: t0 + jour, xp: 60 } },
    options: { chrono: false } };
  const P3 = M.migrer(JSON.parse(JSON.stringify(v1)));
  assert.equal(P3.format, 4);
  assert.equal(P3.compteurs.quizParfaits, 1); assert.equal(P3.compteurs.quizJoues, 0);
  assert.deepEqual(P3.avatar, { tete: null, visage: null, main: null, savant: null });
  // Atomes compte désormais pour Alchimie ; le corps humain n'est pas gelé par la nouvelle branche Savoir
  const xp = M.xpParStat(C, P3);
  assert.equal(xp.alchimie, 70); assert.equal(xp.savoir, 120);
  assert.equal(M.statut(C, P3, "sci.egypte", t0).gelee, false);
  assert.equal(M.statut(C, P3, "sci.genetique", t0).etat, "verrouillee");
  assert.equal(M.statut(C, P3, "chim.feu", t0).etat, "disponible");
  const rec = M.verifierRecompenses(C, P3, t0);
  assert.ok(rec.gagnables.some(o => o.id === "tableau-mendeleiev"));
  // Quiz raté en 20 s, à 3 h du matin, avec des réponses éclair : la panoplie moqueuse
  const nuit = new Date(2026, 9, 25, 3, 0).getTime();
  const qs = M.tirerQuestions(C, P3, "chim.feu", 5).map(q => ({ id: q.id, correct: false, ms: 900 }));
  let r3 = M.terminerQuiz(C, P3, "chim.feu", qs, nuit, { duree: 20000 });
  // v19 : au plus 2 récompenses par épreuve ordinaire ; le reste tombe ensuite (ici aux visites suivantes).
  assert.ok(r3.nouveauxSucces.length <= 2, "2 récompenses au plus");
  const ids = succesPuis(r3, C, P3, nuit);
  for (const id of ["dix-pour-cent", "insomniaque", "table-rase", "neutrinos", "tour-de-pise"]) assert.ok(ids.includes(id), id);
  assert.ok(P3.gagnables["accessoires:chapeau-alu"], "chapeau gagnable après la panoplie moqueuse");
  assert.deepEqual(r3.contextes.slice(0, 2), ["quiz_zero", "nuit"]);
  const rep = M.replique(C, P3, r3.contextes, () => 0);
  assert.equal(rep.contexte, "quiz_zero"); assert.equal(P3.repliques.quiz_zero[0], rep.id);
  assert.notEqual(M.replique(C, P3, ["quiz_zero"], () => 0).id, rep.id);
  // Trois échecs d'affilée sur le même quiz
  M.terminerQuiz(C, P3, "chim.feu", qs, nuit);
  r3 = M.terminerQuiz(C, P3, "chim.feu", qs, nuit);
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
  // Victor (2026-10-31) : les événements tirés à chaque pas sont testés à part ; ici, des pas sans surprise.
  const EVENEMENTS = R.evenements; R.evenements = null;
  const t0 = new Date(2026, 9, 26, 10, 0).getTime();
  const tous = (P, id, ok, chrono) => M.tirerQuestions(C3, P, id, 5).map((q, i) => ({ id: q.id, correct: i < ok, chrono: !!chrono }));

  // Barème annoncé = barème appliqué, avec et sans bonus du jour
  {
    const P = M.nouvellePartie(t0);
    const bonus = M.bonusDuJour(C3, P, t0);
    assert.equal(M.bonusDuJour(C3, P, t0 + 3600000), bonus, "bonus stable dans la journée");
    for (const id of ["math.origines", "phys.machines", "philo.presocratiques"]) {
      const Q = M.nouvellePartie(t0);
      const v = M.valeurEpreuve(C3, Q, { type: "quiz", comp: id }, t0);
      assert.equal(v.base, R.valeurs.quiz_rang["1"]);
      assert.equal(v.duJour, C3.parId[id].stat === M.bonusDuJour(C3, Q, t0) ? R.bonus.du_jour : 0);
      const r = M.terminerQuiz(C3, Q, id, tous(Q, id, 4), t0);
      assert.equal(r.plateau.a - r.plateau.de, v.total, id + " : réussi, non parfait");
      assert.equal(r.plateau.valeurs.total, v.total);
    }
    const Q = M.nouvellePartie(t0);
    const v = M.valeurEpreuve(C3, Q, { type: "quiz", comp: "math.origines" }, t0);
    let r = M.terminerQuiz(C3, Q, "math.origines", tous(Q, "math.origines", 3), t0);
    assert.equal(r.plateau.a, 1, "quiz raté : on reste sur place");
    r = M.terminerQuiz(C3, Q, "math.origines", tous(Q, "math.origines", 5, true), t0);
    assert.equal(r.plateau.valeur, v.total + R.bonus.parfait + R.bonus.chrono, "parfait et chrono");
  }

  // Victor (2026-10-31) : rappel raté, le pion reste sur place (plus de recul).
  {
    const P = M.nouvellePartie(t0);
    M.terminerQuiz(C3, P, "math.origines", tous(P, "math.origines", 4), t0);
    const avant = P.plateau.position;
    const r = M.terminerRappel(C3, P, "math.origines", tous(P, "math.origines", 0).slice(0, 3), t0 + 86400000);
    assert.equal(r.plateau.a, avant);
    assert.equal(P.compteurs.reculs, 0);
  }

  // Victor (2026-10-31) : plus de case spéciale fixe ; un piège posé en jeu sur une case applique sa règle, une fois.
  {
    const P = M.nouvellePartie(t0); M.deplacer(C3, P, 0, t0, "test");
    const rt = P.plateau.route;
    const poser = (i, sp) => { P.plateau.speciaux[rt[i]] = Object.assign({ evenement: true }, sp); };
    cases.filter(k => k.special).forEach(k => assert.equal(!!M.specialDe(C3, P, k.n), false, "case " + k.n + " : plus de règle fixe"));
    P.plateau.idx = 5; P.plateau.position = rt[5];
    poser(6, { type: "recul", n: 3 });
    let dep = M.deplacer(C3, P, 1, t0, "test");
    assert.equal(P.plateau.idx, 3, "recul de 3"); assert.equal(P.compteurs.reculs, 1);
    assert.equal(M.specialDe(C3, P, rt[6]), null, "un piège tiré ne sert qu'une fois");
    poser(4, { type: "quarantaine", n: 1 });
    M.deplacer(C3, P, 1, t0, "test"); assert.equal(P.plateau.quarantaine, 1);
    dep = M.deplacer(C3, P, 1, t0, "test"); assert.equal(dep.a, dep.de, "quarantaine : une épreuve réussie sans bouger");
    M.deplacer(C3, P, 1, t0, "test"); assert.equal(P.plateau.idx, 5);
    poser(6, { type: "prison" });
    M.deplacer(C3, P, 1, t0, "test"); assert.equal(P.plateau.prison, 1);
    assert.equal(M.deplacer(C3, P, 1, t0, "test").a, rt[6], "prison : on ne bouge plus");
    const r = M.terminerQuiz(C3, P, "math.origines", tous(P, "math.origines", 5), t0);
    assert.equal(P.plateau.prison, 0); assert.ok(r.plateau.contextes.includes("prison_liberation"));
    assert.equal(r.plateau.a, rt[7], "libéré par un quiz parfait, et on avance d'une case");
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
    assert.equal(P.plateau.tours, 1);
    // Victor (2026-11-02) : le pion attend sur l'arrivée jusqu'au choix « Refaire un tour ».
    if (C3.plateau.parcours) { assert.equal(P.plateau.position, R.arrivee, "le pion reste sur l'arrivée"); assert.ok(M.choisirSuite(C3, P, "tour", t0).ok); assert.equal(P.plateau.idx, 0, "puis repart du début du nouveau parcours"); }
    else assert.equal(P.plateau.position, R.depart);
    assert.ok(fini.contextes.includes("tour_fini"));
    assert.ok(P.succes["tour-complet"]);
    const rec = M.verifierRecompenses(C3, P, t0);
    // v15 : seules les cases où le pion s'est arrêté dévoilent leur date et leurs livres.
    // Une date dont la case a quitté le plateau (le Web, 2026-10-30) se débloque à son époque : hors de ce contrôle.
    const casesFrise = C3.evenements.filter(e => e.case && C3.plateau.cases.some(k => k.n === e.case));
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
    for (let i = 0; i < 11; i++) P.succes["test-" + i] = t0;
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
    M.accorderPartie(C3, P);  // la case 1 (le feu) a quitté le plateau : la partie se recale sur la première case
    const rec = M.verifierRecompenses(C3, P, t0);
    assert.ok(!rec.evenements.some(e => e.id === "ebbinghaus"), "1885 attend que le pion atteigne le XIXe siècle");
    const kx = C3.plateau.cases.find(k => k.epoque === "xixe"), xixe = kx.n;
    P.plateau.atteinte = xixe; P.plateau.anneeMax = kx.annee;
    assert.ok(M.verifierRecompenses(C3, P, t0).evenements.some(e => e.id === "ebbinghaus"), "date débloquée une fois l'époque atteinte");
    P.plateau.atteinte = 1; P.plateau.tours = 1;
    assert.ok(M.dateAtteinte(C3, P, { annee: 1990 }), "après un tour, plus de limite");
    P.plateau.tours = 0;
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
  assert.equal(C4.parStat.logique.length, 20);
  assert.equal(C4.regles.xp.paliers_niveau.length - 1, 20);

  // Le second losange s'ouvre quand le sommet du premier est maîtrisé
  {
    const P = M.nouvellePartie(t0);
    const L = C4.parStat.logique.map(k => k.id);
    for (const id of L.slice(0, 4)) M.terminerQuiz(C4, P, id, tous(P, id, 5), t0);
    assert.equal(M.statut(C4, P, L[4], t0).etat, "disponible");
    assert.equal(M.statut(C4, P, L[5], t0).etat, "verrouillee");
    vider(C4, P, t0);
    assert.ok(P.succes["branche-logique"], "le premier losange suffit au succès de branche");
    M.terminerQuiz(C4, P, L[4], tous(P, L[4], 5), t0);
    assert.equal(M.statut(C4, P, L[7], t0).etat, "verrouillee");
    // plus-ultra : la première compétence de rang 5 maîtrisée
    const r5 = L.findIndex(id => C4.parId[id].rang >= 5);
    for (const id of L.slice(5, r5)) M.terminerQuiz(C4, P, id, tous(P, id, 5), t0);
    vider(C4, P, t0);
    const r = M.terminerQuiz(C4, P, L[r5], tous(P, L[r5], 5), t0);
    assert.ok(succesPuis(r, C4, P, t0).includes("plus-ultra"));
    for (const id of L.slice(r5 + 1)) M.terminerQuiz(C4, P, id, tous(P, id, 5), t0);
    vider(C4, P, t0);
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
  assert.ok(C4.avatar.savants.length >= 81, "v18 : au moins quatre-vingt-un savants");
  assert.ok(C4.competences.every(k => C4.avatar.savants.some(s => s.theme === k.stat)), "v18 : chaque arbre a ses savants");
  assert.deepEqual(M.verifierRecompenses(C4, P, t0).savants, []);
  // Hypatie arrive avec le ciel de Ptolémée (elle a édité l'Almageste)
  P.competences["astro.ptolemee"] = { maitrise: true, maitriseDepuis: t0, palier: 0, prochainRappel: t0 + 86400000, xp: 70 };
  // Victor (2026-11-08) : liée à la case. Ailleurs, elle attend ; après l'épreuve de Ptolémée, elle arrive.
  assert.deepEqual(M.verifierRecompenses(C4, P, t0).savants, [], "pas loin de sa case");
  P.lot = { t: t0, n: 0, r: 0, theme: "cosmos", comp: "astro.ptolemee" };
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

  // v16 : crédits des succès, fixés par l'IA ; pots-de-vin, toujours plus
  {
    const P = M.nouvellePartie(t0);
    assert.equal(P.credits.solde, 0);
    const sc = C5.succes.find(x => x.id === "premier-pas");
    P.competences["math.origines"] = { maitrise: true, maitriseDepuis: t0, palier: 1, prochainRappel: t0 + 86400000, xp: 20 };
    const rec = M.verifierRecompenses(C5, P, t0);
    const cr = rec.credits.find(c => c.succes === "premier-pas");
    assert.ok(cr && cr.base === M.tarifSucces(C5, sc) && cr.mot && cr.mot.fr, "un succès rapporte des crédits, avec un mot de l'IA");
    assert.ok(cr.mot.fr.endsWith(C5.ia.credits.piques["premier-pas"].fr), "v32 : la phrase parle du sujet du succès");
    assert.equal(P.credits.solde, rec.credits.reduce((a, c) => a + c.n, 0));
    const tarifs = C5.succes.map(x => M.tarifSucces(C5, x));
    assert.ok(Math.max(...tarifs) > Math.min(...tarifs), "le tarif dépend du genre de succès");
    P.credits.solde = 100;
    assert.equal(M.potPossible(C5, P, 500, t0).raison, "solde");
    let r = M.corrompre(C5, P, 10, t0);
    assert.equal(r.issue, "premier"); assert.ok(r.gain > 0); assert.equal(P.credits.solde, 90 + r.recompenses.credits.reduce((a, c) => a + c.n, 0));
    assert.equal(M.corrompre(C5, P, 5, t0).raison, "jour", "un pot-de-vin par jour");
    const j = 86400000;
    r = M.corrompre(C5, P, 20, t0 + j); assert.equal(r.issue, "genereux"); assert.ok(!r.plateau, "plus que son record : de la faveur, plus d'avance (Victor, 2026-10-31)");
    r = M.corrompre(C5, P, 20, t0 + 2 * j); assert.equal(r.issue, "egal"); assert.ok(!r.plateau);
    const avant = M.faveurIA(C5, P, t0 + 3 * j).valeur;
    r = M.corrompre(C5, P, 5, t0 + 3 * j); assert.equal(r.issue, "radin");
    assert.ok(M.faveurIA(C5, P, t0 + 3 * j).valeur < avant, "moins que son record : elle se vexe");
    assert.ok(r.piege && P.plateau.speciaux[r.piege].ia, "et pose un piège");
    assert.equal(P.credits.record, 20, "elle retient le record");
    const v = M.migrer(JSON.parse(JSON.stringify(Object.assign({}, P, { credits: undefined }))), C5);
    assert.ok(v.credits.solde > 0, "migration : crédits rétroactifs pour les succès déjà obtenus");
    const av = M.faveurIA(C5, P, t0 + 4 * j).valeur;
    const ag = M.agacerIA(C5, P, 3, true, t0 + 4 * j);
    assert.ok(ag && ag.perte === Math.min(C5.ia.credits.agacement.max, 3 * C5.ia.credits.agacement.par_erreur + C5.ia.credits.agacement.epreuve_ratee));
    assert.ok(M.faveurIA(C5, P, t0 + 4 * j).valeur === Math.max(0, av - ag.perte), "les erreurs font baisser sa faveur");
    const sf = M.agacerIA(C5, P, 0, false, t0 + 4 * j);
    assert.equal(sf.gain, C5.ia.credits.agacement.sans_faute, "sans faute, un peu plus de faveur");
    assert.equal(sf.apres.valeur, Math.min(100, sf.avant.valeur + sf.gain));
    console.log("OK : v16 crédits des succès et pots-de-vin");
  }

  // v17 : ultimatum de l'IA
  {
    const P = M.nouvellePartie(t0);
    ["math.origines", "phys.unites", "sci.methode"].forEach(id => { P.competences[id] = { maitrise: true, maitriseDepuis: t0, palier: 1, prochainRappel: t0 + 86400000, xp: 400 }; });
    P.credits.solde = 100;
    const nv = M.niveauGlobal(C5, P); assert.ok(nv >= 2);
    assert.equal(M.tenterUltimatum(C5, P, t0, () => 0.99), null, "pas à tous les coups");
    assert.equal(M.tenterUltimatum(C5, P, t0 + 86400000, () => 0), null, "pas deux jours de suite");
    // Réglage de partie « ultimatum »: false (proposé par un pack, ou choisi par le joueur) : jamais d'ultimatum.
    P.options.reglages = { ultimatum: false };
    assert.equal(M.tenterUltimatum(C5, P, t0 + 4 * 86400000, () => 0), null, "réglage : pas d'ultimatum");
    // Réglage « ton » : Alyca parle sur ce ton (« ton.enfant.* »), y compris à l'accueil.
    P.options.reglages = { ton: "enfant" };
    assert.ok(/^ton\.enfant\./.test(M.repliqueDuJour(C5, P, t0).contexte || ""), "ton enfant à l'accueil");
    const re = M.replique(C5, P, ["quiz_parfait"], () => 0);
    assert.ok(re && C5.commentairesPar["ton.enfant.quiz_parfait"].some(l => l.id === re.id), "ton enfant après un sans-faute");
    delete P.options.reglages;
    const u = M.tenterUltimatum(C5, P, t0 + 4 * 86400000, () => 0);
    assert.ok(u && u.demande >= 70, "une grosse somme");
    let r = M.repondreUltimatum(C5, P, true, t0 + 4 * 86400000);
    assert.ok(r.ok && P.credits.solde === 100 - u.demande);
    P.credits.solde = 500;
    const u2 = M.tenterUltimatum(C5, P, t0 + 8 * 86400000, () => 0);
    assert.ok(u2.demande >= Math.ceil(u.demande * 1.5), "payer fait monter la prochaine exigence");
    r = M.repondreUltimatum(C5, P, false, t0 + 8 * 86400000);
    assert.equal(P.credits.solde, 500 + u2.demande, "refuser : elle verse la somme");
    assert.ok(r.niveauApres < r.niveauAvant && r.perdus > 0, "mais retire de vrais niveaux");
    console.log("OK : v17 ultimatum de l'IA");
  }

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
    // La case 1 (le feu) a quitté le plateau (Victor, 2026-11-08) : le pion part de la plus ancienne case.
    P.plateau.position = C5.plateau.cases.slice().sort((a, b) => a.annee - b.annee)[0].n; P.plateau.route = null;
    const c = M.choixIA(C5, P, t0);
    assert.equal(c.type, "quiz"); assert.ok(["case", "hors_case"].includes(c.raison));
    assert.equal(M.choixIA(C5, P, t0).comp.id, c.comp.id, "même choix tant qu'on n'a pas joué");
    const r = M.terminerQuiz(C5, P, c.comp.id, juste(P, c.comp.id, 5, 5), t0, { jouer: true });
    const sans = M.valeurEpreuve(C5, P, { type: "quiz", comp: c.comp.id }, t0).total + C5.plateau.regles.bonus.parfait;
    // v19 : bonus du bouton Jouer tiré entre 0 et 4.
    assert.equal(r.plateau.bonusJouer, 0); assert.equal(r.plateau.valeur, 1, "une case par épreuve réussie");
    // v31 : un rappel d'un autre arbre n'attend plus que son arbre… sauf s'il est très en retard.
    // Victor (2026-10-31) : « une case = un quiz » : sur sa case, la compétence acquise revient en rappel.
    const t1 = P.competences[c.comp.id].prochainRappel + 3 * jour;
    P.plateau.position = +Object.keys(C5.plateau.competences_cases).find(n => C5.plateau.competences_cases[n].includes(c.comp.id));
    const c2 = M.choixIA(C5, P, t1);
    assert.equal(c2.type, "rappel"); assert.equal(c2.comp.id, c.comp.id);
    // v15 : une case d'arbre fermé lance son premier quiz ; raté, l'arbre reste fermé ; réussi, il s'ouvre.
    {
      // La première case de l'arbre Rhétorique : les Maximes de Ptahhotep (l'écriture est passée à la Logique).
      const nP = C5.plateau.cases.find(k => k.id === "ptahhotep").n;
      const O = M.nouvellePartie(t0); O.plateau.position = nP;
      const x = M.choixIA(C5, O, t0);
      // Victor (2026-10-31) : la compétence évoquée par la case passe avant la porte de l'arbre, même arbre fermé.
      const ev = C5.plateau.competences_cases[nP] || [];
      if (ev.length) { assert.equal(x.raison, "case"); assert.ok(ev.includes(x.comp.id)); } else assert.equal(x.raison, "ouvre_arbre");
      assert.equal(x.stat, "eloquence");
      M.terminerQuiz(C5, O, x.comp.id, juste(O, x.comp.id, 5, 0), t0);
      assert.ok(!M.arbreOuvert(C5, O, "eloquence"), "raté : toujours fermé");
      O.plateau.position = nP;
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
      // Victor (2026-11-01) : quand l'épreuve a son propre livre en attente, c'est lui qui tombe.
      const L = M.nouvellePartie(t0); L.plateau.position = 4;
      C5.livres.forEach(l => { L.gagnables["livres:" + l.id] = { famille: "livres", id: l.id, depuis: t0 }; });
      const lie = M.butinOuvert(C5, L).filter(b => b.famille === "livres").map(b => b.chose).slice(-1)[0];
      const autre = M.tirerButin(C5, L, { type: "quiz", comp: lie.competence }, t0, () => 0.001);
      assert.ok(autre && (autre.chose.competence === lie.competence || (autre.chose.condition || {}).id === lie.competence), "butin rattaché à l'épreuve d'abord");
      // Victor (2026-11-03) : un livre ne tombe que sur le quiz ou le rappel de sa compétence, à coup sûr, et toutes époques.
      const V = M.nouvellePartie(t0); V.plateau.position = 4;
      C5.livres.forEach(l => { V.gagnables["livres:" + l.id] = { famille: "livres", id: l.id, depuis: t0 }; });
      for (let i = 0; i < 30; i++) {
        const d = M.tirerButin(C5, V, { type: i % 2 ? "duel" : "chrono" }, t0, () => 0.01 * i);
        assert.ok(!d || d.famille !== "livres", "pas de livre sur un duel ni un Chrono");
      }
      const recent = C5.livres.filter(l => Number(l.annee) > 1800 && l.lot <= 1)[0];
      V.lot = null;
      const r = M.tirerButin(C5, V, { type: "rappel", comp: recent.competence }, t0, () => 0.999);
      assert.ok(r && r.famille === "livres" && r.chose.competence === recent.competence, "le rappel de sa compétence donne le livre, même hors époque");
    }
    // v15 : la case du pion dicte l'arbre de l'épreuve ; arbre sans rien de jouable, l'IA improvise hors case.
    const Q = M.nouvellePartie(t0);
    C5.plateau.cases.forEach(k => {
      Q.plateau.position = k.n;
      const x = M.choixIA(C5, Q, t0);
      const jouable = M.disponibles(C5, Q, t0).some(c => c.stat === k.stat);
      const ferme = !M.arbreOuvert(C5, Q, k.stat);
      // Victor (2026-10-31) : la case évoque une compétence non acquise, même verrouillée : c'est elle qu'on joue.
      const ev = (C5.plateau.competences_cases[k.n] || []).filter(id => C5.parId[id] && !(Q.competences[id] && Q.competences[id].maitrise));
      if (ev.length) { assert.equal(x.raison, "case", "case " + k.n); assert.ok(ev.includes(x.comp.id), "compétence de la case " + k.n); assert.equal(x.kase.n, k.n); return; }
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
    v4.competences["math.origines"] = { maitrise: true, palier: 2, xp: 90, prochainRappel: t0 };
    const p = M.migrer(v4, C5);
    assert.ok(!("masqueChoisi" in p)); assert.equal(p.farce, null); assert.equal(p.competences["math.origines"].xp, 90);
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

  // Victor (2026-10-31) : une épreuve réussie vaut une case, quel que soit le rang, sans bonus Jouer.
  {
    const k3 = C6.competences.filter(k => k.rang === 3)[0];
    const P = M.nouvellePartie(t0);
    assert.equal(M.valeurEpreuve(C6, P, { type: "quiz", comp: k3.id }, t0).total, 1);
    assert.equal(M.valeurEpreuve(C6, P, { type: "rappel", comp: k3.id }, t0).total, 1);
    const k1 = C6.competences.filter(k => k.rang === 1)[0];
    const r = M.terminerQuiz(C6, P, k1.id, juste(P, k1.id, 5, 5), t0, { jouer: true, alea: () => 0.99 });
    assert.equal(r.plateau.valeur, 1, "une case"); assert.equal(r.plateau.bonusJouer, 0, "plus de bonus Jouer");
  }

  // Simulation : au plus un butin par épreuve, aucun lot avant son tour, collection incomplète au tour 7
  {
    // Les événements de route (duels, pièges…) ne sont pas joués par cette simulation du butin.
    const EV6 = C6.plateau.regles.evenements; C6.plateau.regles.evenements = null;
    let seed = 7; const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
    const P = M.nouvellePartie(t0); let t = t0;
    const butin = () => ["objets", "livres", "accessoires", "masques"].reduce((n, f) => n + Object.keys(P[f]).length, 0);
    const lot = {}; ["objets", "livres"].forEach(f => C6[f].forEach(x => { if (x.lot) lot[f + ":" + x.id] = x.lot; }));
    C6.avatar.accessoires.forEach(x => { lot["accessoires:" + x.id] = x.lot; }); C6.ia.masques.forEach(x => { if (x.lot) lot["masques:" + x.id] = x.lot; });
    let collectionAuTour7 = null;
    for (let j = 0; j < 400 && P.plateau.tours < 8; j++) {
      // Un joueur qui gâte l'IA : sa faveur reste moyenne (furieuse, elle ralentirait tout le parcours).
      P.faveur = { valeur: 60, maj: t };
      M.verifierRecompenses(C6, P, t);
      const faire = M.rappelsDus(C6, P, t).map(k => ({ comp: k, type: "rappel" }));
      for (let n = 0; n < 3; n++) { const c = M.choixIA(C6, P, t); if (c && (c.type === "quiz" || c.raison === "revision" || c.evoque)) faire.push(c); }
      for (const c of faire) {
        if (c.type === "quiz" && c.raison !== "ouvre_arbre" && !c.horsOrdre && !M.disponibles(C6, P, t).some(k => k.id === c.comp.id)) continue;
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
    C6.plateau.regles.evenements = EV6;
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

// v7 : trois arbres fondamentaux, les autres s'ouvrent sur le parcours ; surnom de l'IA
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json") };
  const C7 = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const t0 = new Date(2026, 10, 2, 10, 0).getTime();
  const P = M.nouvellePartie(t0);
  // Les arbres du pack CP (pour enfants, éteint par défaut en jeu) sont ici chargés sans filtre : ils sont mis de côté.
  assert.deepEqual(C7.stats.filter(s => M.arbreOuvert(C7, P, s.id) && !s.id.startsWith("cp-")).map(s => s.id).sort(), ["logique", "mecanique", "savoir"]);
  assert.equal(M.statut(C7, P, "rhet.argument", t0).etat, "fermee");
  assert.ok(!M.disponibles(C7, P, t0).some(c => c.stat === "eloquence"), "pas de quiz dans un arbre fermé");
  assert.ok(!C7.succes.some(s => s.ouvre), "plus aucun succès n'ouvre un arbre");
  P.options.tousArbres = true;
  assert.equal(M.statut(C7, P, "rhet.argument", t0).etat !== "fermee", true, "mode test : tout est ouvert");
  P.options.tousArbres = false;
  P.succes["pionnier-ciceron"] = t0;
  assert.ok(M.arbreOuvert(C7, P, "eloquence"), "une partie qui avait l'ancien succès pionnier garde son arbre");
  // Chaque arbre fermé a sa porte : une case du parcours à lui, dont l'épreuve réussie l'ouvre.
  C7.stats.filter(s => !M.arbreOuvert(C7, M.nouvellePartie(t0), s.id)).forEach(s => assert.ok(C7.plateau.cases.some(k => k.stat === s.id), s.id + " a une case sur le parcours"));
  const O = M.nouvellePartie(t0);
  O.competences[C7.parStat.alchimie[0].id] = { maitrise: true, maitriseDepuis: t0 };
  assert.ok(M.arbreOuvert(C7, O, "alchimie") && !M.arbreOuvert(C7, O, "cosmos"), "une compétence maîtrisée ouvre son arbre, pas les autres");
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
  R.succes[C7.succes[0].id] = t0;
  const s = M.surnom(C7, R, t0);
  assert.ok(s.succes && s.texte.indexOf(s.succes.nom.fr) >= 0, "surnom tiré du succès");
  assert.ok(M.surnom(C7, R, t0 + 3 * 86400000).succes == null, "le succès s'efface après un jour");
  console.log("OK : v7 arbres fondamentaux, arbres ouverts sur le parcours, surnom de l'IA");
}

// v7 lot 2 : ennemis sur la route, duels, bestiaire, cadeaux à l'IA
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json") };
  const C8 = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const t0 = new Date(2026, 10, 3, 10, 0).getTime();
  const P = M.nouvellePartie(t0);
  P.plateau.position = 2;
  // v18 : le sophiste attend case 4 (l'écriture) : un pas de 4 s'arrête dessus, il reste 2 cases.
  let dep = M.avancerPion(C8, P, 4, t0);
  assert.equal(P.plateau.position, 4);
  assert.deepEqual([P.duel.ennemi, P.duel.reste, P.duel.pret], ["sophiste", 2, true]);
  assert.ok(dep.etapes.some(e => e.type === "ennemi"));
  let qs = M.tirerDuel(C8, P, t0, Math.random);
  assert.equal(qs.length, 5);
  assert.ok(qs.every(m => m.ennemi === "sophiste"));
  // Défaite : le pion reste, le duel reste ouvert (revanche obligatoire) et l'ennemi vole des crédits.
  P.credits.solde = 100;
  let r = M.terminerDuel(C8, P, qs.map((m, i) => ({ id: m.id, correct: i > 0 })), t0);
  assert.equal(r.gagne, false);
  assert.equal(P.plateau.position, 4);
  assert.equal(P.duel.pret, true); assert.ok(M.duelBloquant(P));
  assert.equal(r.vol, 15); assert.equal(P.credits.solde, 85);
  assert.equal(P.bestiaire.sophiste.defaites, 1);
  dep = M.avancerPion(C8, P, 3, t0 + 1000);
  assert.equal(P.plateau.position, 4, "le pion ne passe pas sans duel");
  assert.deepEqual([P.duel.reste, P.duel.pret], [3, true]);
  // Victoire : l'ennemi part, le pion finit son trajet, succès et butin.
  const qs2 = M.tirerDuel(C8, P, t0, Math.random);
  assert.ok(qs2.every(m => !qs.some(q => q.id === m.id)), "d'abord des affirmations jamais vues");
  r = M.terminerDuel(C8, P, qs2.map(m => ({ id: m.id, correct: true })), t0 + 2000, () => 0);
  assert.ok(r.gagne && r.premiere);
  assert.equal(P.plateau.position, 7);
  assert.equal(P.duel, null);
  assert.ok(P.succes["vaincu-sophiste"]);
  assert.ok(!M.ennemisPlateau(C8, P)[4], "l'ennemi vaincu quitte le plateau");
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
    assert.notDeepEqual(cases.sort((a, b) => a - b), [4, 15, 34, 39, 43, 52, 61], "les postes glissent");
    // v18 : chacun se poste sur une case de son thème quand il en reste une de libre.
    const surTheme = Object.keys(en).filter(n => M.caseN(C8, n).stat === C8.ennemiParId[en[n]].theme).length;
    assert.ok(surTheme >= 6, "ennemis sur les cases de leur thème : " + surTheme);
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
  if (c.effet.de != null) assert.equal(M.specialDe(C8, G, c.effet.de), null);
  assert.equal(M.specialDe(C8, G, c.effet.vers).type, c.effet.regle);
  console.log("OK : v7 ennemis, duels, bestiaire, cadeaux à l'IA");
}

// v8 : cases pièges (recul, téléportation, révision forcée)
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json") };
  const C9 = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const t0 = new Date(2026, 9, 28, 10, 0).getTime(), J = 86400000;
  // Victor (2026-10-31) : les pièges ne sont plus fixes, on les pose sur la route (place i) ; pas d'événement tiré ici.
  C9.plateau.regles.evenements = null;
  const sur = (i, pas, sp, P) => {
    P = P || M.nouvellePartie(t0); P.plateau.ennemis = {}; M.deplacer(C9, P, 0, t0, "test");
    const rt = P.plateau.route; P.plateau.speciaux[rt[i]] = Object.assign({ evenement: true }, sp);
    P.plateau.idx = i - pas; P.plateau.position = rt[i - pas];
    return [P, M.deplacer(C9, P, pas, t0, "test")];
  };
  const rtDe = P => P.plateau.route;
  // Téléportation : retour à une case plus ancienne de la route.
  const P0 = M.nouvellePartie(t0); M.deplacer(C9, P0, 0, t0, "test"); const rt0 = P0.plateau.route;
  let [P, dep] = sur(12, 2, { type: "teleport", vers: rt0[4] }, P0);
  assert.equal(dep.a, rt0[4]); assert.equal(dep.etapes[0].type, "teleport"); assert.equal(dep.etapes[0].n, 8);
  // Recul de deux cases.
  [P, dep] = sur(8, 1, { type: "recul", n: 2 });
  assert.equal(dep.a, rtDe(P)[6]); assert.equal(dep.etapes[0].type, "recul");
  // Révision forcée sans compétence maîtrisée : rien.
  [P, dep] = sur(11, 1, { type: "revision" });
  assert.equal(dep.etapes[0].type, "revision_vide"); assert.equal(P.revision, undefined);
  // Avec deux compétences maîtrisées : l'IA prend celle dont le rappel est le plus lointain.
  P = M.nouvellePartie(t0);
  P.competences["math.origines"] = { maitrise: true, palier: 2, xp: 90, prochainRappel: t0 + 3 * J, maitriseDepuis: t0 - 9 * J };
  P.competences["math.chine"] = { maitrise: true, palier: 3, xp: 90, prochainRappel: t0 + 20 * J, maitriseDepuis: t0 - 30 * J };
  [P, dep] = sur(11, 1, { type: "revision" }, P);
  assert.equal(P.revision.comp, "math.chine");
  assert.equal(M.choixIA(C9, P, t0).raison, "revision");
  dep = M.deplacer(C9, P, 1, t0, "quiz");
  assert.equal(dep.a, rtDe(P)[11], "bloqué tant que la révision n'est pas faite"); assert.equal(dep.etapes[0].type, "bloque_revision");
  const qs = M.tirerQuestions(C9, P, "math.chine", 3);
  let r = M.terminerRappel(C9, P, "math.chine", qs.map(q => ({ id: q.id, correct: true })), t0);
  assert.ok(r.revision); assert.equal(P.revision, null); assert.equal(P.competences["math.chine"].palier, 3, "pas de palier gagné");
  assert.ok(r.contextes.includes("revision_reussie")); assert.equal(r.plateau.a, rtDe(P)[11], "pion libéré sur sa case, qui garde son quiz (une case = un quiz)");
  // Révision ratée : la compétence reste, son rappel devient dû.
  [P, dep] = sur(14, 1, { type: "revision" }, P);
  const cible = P.revision.comp;
  r = M.terminerRappel(C9, P, cible, M.tirerQuestions(C9, P, cible, 3).map(q => ({ id: q.id, correct: false })), t0 + 1000);
  assert.ok(P.competences[cible].maitrise, "pas de perte"); assert.equal(P.competences[cible].prochainRappel, t0 + 1000);
  assert.equal(r.plateau, null); assert.ok(r.contextes.includes("revision_ratee"));
  assert.ok(M.rappelsDus(C9, P, t0 + 2000).some(k => k.id === cible));
  // Case cadeau : un objet sans épreuve, montré dans les récompenses.
  P = M.nouvellePartie(t0); M.verifierRecompenses(C9, P, t0);
  P.gagnables["objets:boulier"] = { famille: "objets", id: "boulier", depuis: t0 };
  [P, dep] = sur(5, 2, { type: "cadeau" }, P);
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
  // S'arrêter sur une case où Alyca a posé un atome le fait apparaître (Victor, 2026-10-31 : plus de case Mendeleïev fixe).
  P.plateau.speciaux = { 53: { type: "mendeleiev" } };
  P.plateau.position = 51;
  let dep = M.deplacer(CA, P, 2, t0, "test");
  assert.equal(dep.a, 53); assert.equal(dep.etapes[0].type, "atome"); assert.equal(dep.etapes[0].case, 53);
  assert.equal(P.sauvages.length, 1);
  const s = M.atomeSauvage(CA, P); assert.ok(s.element.symbole);
  // Les trois questions : une seule bonne réponse chacune, quatre choix distincts.
  for (let k = 0; k < 40; k++) {
    P.sauvages[0].z = 1 + (k * 7) % 118;
    const cb = M.tirerCombat(CA, P, Math.random);
    assert.equal(cb.questions.length, 4);
    assert.equal(cb.questions[2].type, "place"); assert.equal(cb.questions[2].reponse, cb.element.z);
    cb.questions.filter(q => q.type !== "place").forEach(q => {
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
  assert.ok([0, 1, 2, 3, 4, 5, 6, 7].flatMap(i => M.verifierSucces(CA, P, t0 + 100 + i)).some(x => x.id === "gaz-nobles"));
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
  P.competences["math.chine"] = { maitrise: true, palier: 1, xp: 50, prochainRappel: tF + J, maitriseDepuis: t0 };
  const v = M.valeurEpreuve(CF, P, { type: "quiz", comp: "math.chine" }, tF);
  // Victor (2026-10-31) : plus de case de moins ; furieuse, les mauvaises rencontres sont plus fréquentes.
  const EVc = CF.plateau.regles.evenements.chance; assert.equal(v.total, 1); assert.ok(EVc.furieuse > EVc.contente && EVc.contente > EVc.comblee);
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
  assert.equal(M.valeurEpreuve(CF, P, { type: "quiz", comp: "math.chine" }, tF).total, 1);
  P.punition = null; assert.ok(M.repliqueDuJour(CF, P, tF).contexte === "faveur_comblee");
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
  // Héron (Victor, 2026-10-31) : toujours une case, mais moins de surprises sur la route.
  P.competences["math.chine"] = { maitrise: true, palier: 1, xp: 50, prochainRappel: t1 + J, maitriseDepuis: t0 };
  imposer(["heron"], t1); assert.equal(M.valeurEpreuve(CM, P, { type: "quiz", comp: "math.chine" }, t1).total, 1);
  assert.equal(M.reglesDuJour(CM, P, t1).avance, 1); assert.ok(X.plateau.regles.evenements.par_avance_masque < 0);
  // Perceptron : un piège de recul est sans effet.
  const R = X.plateau.regles;
  let caseRecul = 21;
  P.plateau.speciaux = Object.assign(P.plateau.speciaux || {}, { 21: { type: "recul", n: 2 } });
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
  const obj = X.objets.objets.find(o => o.bonus.type === "butin");
  assert.ok(!X.objets.objets.some(o => o.bonus && o.bonus.type === "case"), "plus d'objet qui fait avancer (Victor, 2026-10-31)");
  P2.objets[obj.id] = t0; P2.avatar.main = obj.id;
  P2.competences["math.chine"] = { maitrise: true, palier: 1, xp: 50, prochainRappel: t0 + 99 * J, maitriseDepuis: t0 };
  let bonus = 0;
  for (let k = 0; k < 40; k++) {
    P2.plateau.position = R.depart;
    const r = M.jouerPlateau(CM, P2, { type: "quiz", comp: "math.chine" }, { reussi: true }, t0 + k * 1000);
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
  // Horloge du jeu calée sur t0 : sans cela, l'absence comptée jusqu'à aujourd'hui rend l'IA furieuse et change ses répliques.
  const P = M.nouvellePartie(t0); P.plateau.ennemis = {}; P.decalage = t0 - Date.now();
  const qs = CH.questions.filter(q => q.competence === "math.chine").slice(0, 5);
  const res = qs.map((q, i) => ({ id: q.id, correct: i >= 2, rep: i < 2 ? 99 : null }));
  const r = M.terminerQuiz(CH, P, "math.chine", res, t0, { alea: () => 0.99 });
  assert.equal(P.oublis.length, 2); assert.equal(P.oublis[0].rep, 99); assert.equal(P.compteurs.hontes, 2);
  assert.ok(r.nouveauxSucces.some(s => s.id === "honte-1"));
  let mur = M.murDeLaHonte(CH, P, t0 + 3600000);
  assert.equal(mur.aujourdhui.length, 2); assert.equal(mur.restantes, 2); assert.equal(mur.aujourdhui[0].question.competence, "math.chine");
  assert.equal(M.repliqueDuJour(CH, P, t0 + 3600000).contexte, "mur_honte");
  // La même question ratée deux fois le même jour n'apparaît qu'une fois.
  M.terminerQuiz(CH, P, "math.chine", res, t0 + 5 * 3600000, { alea: () => 0.99 });
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
  M.terminerQuiz(CH, P, "math.archimede", CH.questions.filter(q => q.competence === "math.archimede").slice(0, 5).map(q => ({ id: q.id, correct: false })), t0 + 31 * J, { alea: () => 0.99 });
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
  P.competences["astro.ptolemee"] = { maitrise: true, maitriseDepuis: T, xp: 10 };
  P.competences["phys.optique"] = { maitrise: true, maitriseDepuis: T, xp: 10 };
  // Victor (2026-11-08) : chacun sur l'épreuve de sa compétence (une case, deux épreuves de suite ici).
  const lot = (t, comp) => { P.lot = { t, n: 0, r: 0, theme: null, comp }; };
  lot(T + 1, "astro.ptolemee");
  const la = M.verifierRecompenses(CS, P, T + 1);
  lot(T + 2, "phys.optique");
  const a = la, b = M.verifierRecompenses(CS, P, T + 2);
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
  const oubli = 30; P.plateau.speciaux = Object.assign(P.plateau.speciaux || {}, { 30: { type: "oubli" } });
  P.plateau.position = oubli - 2; P.plateau.visites[oubli - 2] = 1;
  // Victor (2026-11-01, « Recul fixe ») : même quand toutes les cases derrière ont été vues, le trou de mémoire fait reculer de 5.
  for (let k = 1; k < oubli; k++) P.plateau.visites[k] = 1;
  const dep = M.deplacer(CP, P, 2, T, "test");
  const et = dep.etapes.find(e => e.type === "oubli");
  assert.ok(et && et.n === 5 && !dep.etapes.some(e => e.type === "oubli_vide"), "trou de mémoire : recul fixe de 5 cases");
  // Un pas seulement
  P = M.nouvellePartie(T); P.plateau.ennemis = {}; CP.plateau.regles.evenements = null;
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

{
  // v18 : la case du pion donne le ton. Butin, apartés, masques, farces et répliques suivent le thème.
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json") };
  const CT = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const T = Date.UTC(2026, 0, 5, 9);
  // Tout porte un thème : objets, savants, masques, ennemis ; chaque arbre a ses cases, ses savants, ses masques ou ses objets.
  assert.ok(CT.objets.every(o => o.theme) && CT.avatar.savants.every(s => s.theme) && CT.ia.masques.every(m => m.theme) && CT.ennemis.every(e => e.theme));
  CT.regles.stats.forEach(s => {
    // Un pack peut n'avoir aucune case à lui : il lui faut au moins une case qui évoque une de ses compétences.
    const evoque = Object.values(CT.plateau.competences_cases || {}).some(l => l.some(id => CT.parId[id] && CT.parId[id].stat === s.id));
    assert.ok(CT.plateau.cases.some(k => k.stat === s.id) || evoque, "des cases " + s.id);
    assert.ok(CT.commentairesPar["theme_reussi@" + s.id] && CT.commentairesPar["theme_rate@" + s.id] && CT.commentairesPar["theme_jouer@" + s.id], "répliques " + s.id);
  });
  assert.ok(CT.competences.every(k => CT.succes.some(s => s.condition.type === "competence_maitrisee" && s.condition.id === k.id)), "un succès par compétence");
  // Victor (2026-11-08) : un objet ne tombe que sur l'épreuve ou la case qui le désigne, jamais ailleurs.
  {
    const o = CT.objets.find(x => x.condition && x.condition.type === "competence_maitrisee" && x.lot === 1), autre = CT.competences.find(k => k.id !== o.condition.id && !CT.objets.some(x => x.condition && x.condition.id === k.id));
    let lies = 0, ailleurs = 0;
    for (let i = 0; i < 40; i++) {
      const P = M.nouvellePartie(T);
      P.journal = new Array(i).fill({ t: T, type: "quiz", xp: 1 });
      P.gagnables["objets:" + o.id] = { famille: "objets", id: o.id, depuis: T };
      const b = M.tirerButin(CT, P, { type: "quiz", comp: o.condition.id }, T + i, () => 0.01);
      if (b && b.chose.id === o.id) lies++;
      const P2 = M.nouvellePartie(T);
      P2.gagnables["objets:" + o.id] = { famille: "objets", id: o.id, depuis: T };
      const b2 = M.tirerButin(CT, P2, { type: "quiz", comp: autre.id }, T + i, () => 0.01);
      if (b2 && b2.chose.id === o.id) ailleurs++;
    }
    assert.ok(lies > 30, "l'objet tombe sur l'épreuve de sa compétence : " + lies);
    assert.equal(ailleurs, 0, "jamais sur une autre épreuve");
  }
  // Aparté : avec un objet Cosmos et un objet Logique, l'IA sort surtout celui du thème.
  {
    const P = M.nouvellePartie(T); P.objets = { "lunette-galilee": T, "boulier": T };
    let cos = 0, n = 0;
    for (let i = 0; i < 200; i++) { const a = M.aparte(CT, P, "moqueuse", "g" + i, "cosmos"); if (a && a.objet) { n++; if (a.objet.id === "lunette-galilee") cos++; } }
    assert.ok(n > 50 && cos / n > 0.65, "aparté du thème : " + cos + "/" + n);
  }
  // Répliques : une réussite en Cosmos prend souvent une ligne d'astronomie, sous l'expression de la réussite.
  {
    const P = M.nouvellePartie(T); let th = 0;
    for (let i = 0; i < 60; i++) { P.journal.push({ t: T, type: "quiz", xp: 1 }); const r = M.replique(CT, P, ["quiz_reussi"], null, null, "cosmos"); if (r.id.indexOf("theme-reussi-cosmos") === 0) { th++; assert.equal(r.contexte, "quiz_reussi"); } assert.equal(r.theme, "cosmos"); }
    assert.ok(th > 20 && th < 55, "lignes d'arbre : " + th + "/60");
  }
  // Masque : parmi les masques gagnés qui vont au ton, elle prend souvent celui du thème.
  {
    const P = M.nouvellePartie(T); P.masques = { theatre: T, talos: T, eliza: T, kismet: T, "machine-analytique": T };
    let emp = 0;
    for (let i = 0; i < 100; i++) if (M.themeDe(M.masquePourTon(CT, P, "moqueuse", "m" + i, "empathie")) === "empathie") emp++;
    assert.ok(emp > 55, "masque du thème : " + emp + "/100");
  }
  // Farce : après un échec en Empathie, la tenue d'Empathie a la priorité. v25 : plus jamais un savant entier.
  {
    const P = M.nouvellePartie(T); P.savants = { "william-james": T, "galilee": T, "pasteur": T };
    const f = M.tenterFarce(CT, P, T, () => 0, "empathie");
    assert.deepEqual([f.type, f.id], ["tenue", "rose-bonbon"]);
    for (let i = 0; i < 200; i++) { const g = M.tenterFarce(CT, P, T, Math.random); if (g) assert.ok(g.type === "tenue" || g.type === "accessoire", "farce " + g.type); }
    const v = JSON.parse(JSON.stringify(P)); v.farce = { type: "savant", id: "galilee", depuis: T, jusqua: T + 3600e3 };
    assert.equal(M.migrer(v, CT).farce, null, "une ancienne farce savant est levée");
  }
  console.log("OK : v18 thèmes : butin, apartés, répliques, masques et farces suivent la case");
}
// v19 : un atome sauvage arrête le pion sur sa case ; capturé ou laissé partir, le pion finit son trajet.
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") };
  const CA = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const T = new Date(2026, 9, 27, 10).getTime();
  const P = M.nouvellePartie(T); P.plateau.ennemis = {};
  const rt = P.plateau.route || Array.from({ length: 63 }, (_, i) => i + 1); P.plateau.route = rt;
  P.plateau.speciaux = { 31: { type: "mendeleiev" } };
  const i31 = rt.indexOf(31); P.plateau.idx = i31 - 2; P.plateau.position = rt[i31 - 2];
  let dep = M.deplacer(CA, P, 5, T, "test");
  assert.equal(P.plateau.position, 31, "arrêt sur la case Mendeleïev");
  const ap = dep.etapes.find(e => e.type === "atome");
  assert.ok(ap && ap.arret && ap.reste === 3, "3 cases restent");
  assert.equal(M.atomeSauvage(CA, P).reste, 3);
  const f = M.laisserPartir(CA, P, T + 1);
  assert.ok(f.plateau && f.plateau.cause === "atome");
  assert.equal(P.plateau.idx, i31 + 3, "laissé partir : le pion finit son trajet");
  assert.equal((P.sauvages || []).length, 0);
  console.log("OK : v19 l'atome arrête le pion, le trajet reprend ensuite");
}
// v19 : la boutique de l'IA. Achats à l'aveugle, parmi ce qu'on n'a pas ; parcours modifiable.
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") };
  const CB = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const T = new Date(2026, 9, 27, 11).getTime();
  const P = M.nouvellePartie(T); P.credits.solde = 30;
  assert.equal(M.acheter(CB, P, "objet", T).raison, "solde");
  P.credits.solde = 1000;
  const avant = M.enRayon(CB, P, "objet").length;
  const r = M.acheter(CB, P, "objet", T);
  assert.ok(r.ok && P.objets[r.chose.id]); assert.equal(P.credits.solde, 960); assert.equal(M.enRayon(CB, P, "objet").length, avant - 1);
  const m = M.acheter(CB, P, "masque", T + 1); assert.ok(m.ok && P.masques[m.chose.id] != null);
  // Chasser : le prochain ennemi quitte la route ; convoquer : un ennemi de plus devant le pion.
  const en = M.ennemisPlateau(CB, P), nb = Object.keys(en).length;
  const ch = M.acheter(CB, P, "chasser", T + 2); assert.ok(ch.ok && !M.ennemisPlateau(CB, P)[ch.case]);
  const cv = M.acheter(CB, P, "convoquer", T + 3); assert.ok(cv.ok); assert.equal(Object.keys(M.ennemisPlateau(CB, P)).length, nb);
  // Faveur d'un arbre : l'IA pioche dedans pour les prochaines épreuves.
  const a = M.acheter(CB, P, "arbre", T + 4, "mecanique"); assert.ok(a.ok);
  const c = M.choixIA(CB, P, T + 4); assert.equal(c.comp.stat, "mecanique"); assert.ok(c.achat);
  console.log("OK : v19 boutique de l'IA, achats à l'aveugle et parcours");
}
// v20 : articles de poche (joker, droit à l'erreur, relance, désarmement) et emplettes de l'IA.
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") };
  const CP = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const T = new Date(2026, 9, 27, 12).getTime();
  const P = M.nouvellePartie(T); P.credits.solde = 1000;
  ["joker", "erreur", "relance", "desarme"].forEach(a => assert.ok(M.acheter(CP, P, a, T).ok, a));
  for (let i = 0; i < 4; i++) M.acheter(CP, P, "joker", T);
  assert.equal(M.enPoche(P, "joker"), 5); assert.equal(M.acheter(CP, P, "joker", T).raison, "vide", "5 jokers au plus");
  // Joker : deux mauvais choix effacés sur un QCM à quatre choix, jamais la bonne réponse.
  const q = { type: "qcm", choix: ["a", "b", "c", "d"], reponse: 2 };
  const ef = M.joker(q, () => 0.3); assert.equal(ef.length, 2); assert.ok(ef.indexOf(2) < 0);
  assert.equal(M.joker({ type: "vrai_faux", reponse: true }), null);
  assert.ok(M.utiliser(P, "joker", T)); assert.equal(M.enPoche(P, "joker"), 4);
  // Désarmement : le pion s'arrête sur un recul et ne recule pas.
  P.plateau.ennemis = {}; const rt = P.plateau.route || Array.from({ length: 63 }, (_, i) => i + 1); P.plateau.route = rt;
  P.plateau.speciaux = P.plateau.speciaux || {}; P.plateau.speciaux[rt[5]] = { type: "recul", n: 3 };
  P.plateau.idx = 3; P.plateau.position = rt[3];
  const dep = M.deplacer(CP, P, 2, T, "test");
  assert.ok(dep.etapes.some(e => e.type === "piege_desarme")); assert.equal(P.plateau.idx, 5); assert.equal(M.enPoche(P, "desarme"), 0);
  // Relance : l'atome en attente change d'élément.
  P.sauvages = [{ z: 1, case: 31, depuis: T }];
  const rl = M.relancerAtome(CP, P, T); assert.ok(rl && rl.apres.z !== 1 && P.sauvages[0].z === rl.apres.z); assert.equal(M.enPoche(P, "relance"), 0);
  // Emplettes : l'argent de l'ultimatum payé va dans sa bourse ; elle choisit, pas au hasard.
  const Q = M.nouvellePartie(T); Q.credits.solde = 500; Q.ultimatum = { demande: 400, niveaux: 2, depuis: T };
  M.repondreUltimatum(CP, Q, true, T); assert.equal(Q.credits.ia, 400);
  assert.equal(M.emplettesIA(CP, Q, T, () => 0.9), null, "une chance sur deux");
  assert.equal(M.emplettesIA(CP, Q, T + 1000, () => 0), null, "une fois par jour");
  const types = {};
  for (let j = 1; j <= 12; j++) {
    const e = M.emplettesIA(CP, Q, T + j * 86400000, () => 0); if (!e) continue;
    types[e.type] = (types[e.type] || 0) + 1;
    if (e.type === "objet") { const o = CP.objets.find(x => x.id === e.id); assert.equal(Q.objetIA, e.id); assert.ok(o.cadeau.eclat >= 2, "elle prend ce qui brille"); }
    if (e.type === "farce") assert.equal(M.farceActive(Q, e.t).id, e.id);
    if (e.type === "masque") assert.ok(Q.masques[e.id] != null);
    assert.ok(e.mot && e.mot.fr);
  }
  assert.ok(Q.credits.ia >= 0 && Q.credits.depensesIA > 0);
  assert.ok(M.empletteAVoir(Q));
  // Le premier objet est le plus brillant : éclat 3.
  const R = M.nouvellePartie(T); R.credits.ia = 40; const CE = JSON.parse(JSON.stringify(CP.ia.credits.emplettes));
  CP.ia.credits.emplettes.poids = { objet: 1 };
  const e1 = M.emplettesIA(CP, R, T, () => 0); assert.equal(e1.type, "objet"); assert.equal(CP.objets.find(x => x.id === e1.id).cadeau.eclat, 3);
  CP.ia.credits.emplettes = CE;
  console.log("OK : v20 articles de poche et emplettes de l'IA " + JSON.stringify(types));
}
// Victor (2026-10-31) : plus de bonus du bouton Jouer, quelle que soit l'humeur.
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") };
  const CF = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const T = new Date(2026, 9, 28, 9).getTime();
  const P = M.nouvellePartie(T); P.faveur = { valeur: 2, maj: T };
  assert.equal(M.bornesBonusJouer(CF, P, T).max, 0);
  P.faveur = { valeur: 90, maj: T }; assert.equal(M.bornesBonusJouer(CF, P, T).max, 0);
  console.log("OK : plus de bonus Jouer");
}
// Victor (2026-10-31) : les cases des arbres allumés, rangées par date, coupées au réglage « Cases par tour » (24) ;
// le tour suivant reprend après la dernière case ; toutes vues, c'est la victoire et l'histoire recommence.
{
  const X = { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"),
    plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json"), donjons: d("donjons.json") };
  const CR = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), X);
  const T = new Date(2026, 9, 28, 10).getTime();
  const boucler = (P, v) => { P.faveur = { valeur: v, maj: T }; P.plateau.ennemis = {}; P.duel = null; P.sauvages = []; const rt = M.routeTour(CR, P); P.plateau.idx = rt.length - 2; P.plateau.position = rt[rt.length - 2]; return M.deplacer(CR, P, 3, T, "test"); };
  const arr = CR.plateau.cases.find(k => k.arrivee).n;
  const pool = CR.plateau.cases.filter(k => k.n !== arr).sort((a, b) => a.annee - b.annee || a.n - b.n).map(k => k.n);
  const P = M.nouvellePartie(T); P.plateau.route = null; P.plateau.idx = null;
  assert.equal(M.casesParTour(CR, P), 24, "24 cases par défaut");
  const rt = M.routeTour(CR, P);
  assert.equal(rt.length, 25); assert.deepEqual(rt.slice(0, 24), pool.slice(0, 24), "les plus anciennes d'abord, par date"); assert.equal(rt[24], arr);
  assert.equal(Object.keys(M.ennemisPlateau(CR, P)).length, 0, "plus d'ennemi posté d'avance");
  const d1 = boucler(P, 95); assert.ok(d1.etapes.some(e => e.type === "tour_fini"));
  const tf = d1.etapes.find(e => e.type === "tour_fini");
  assert.ok(tf.case > 0 && tf.faveur && M.faveurIA(CR, P, T).valeur === 100, "v32 : arrivée nommée, faveur en hausse (plafonnée à 100)");
  assert.ok(!tf.victoire);
  const s1 = P.plateau.parcoursSuivant; assert.ok(s1 && s1.palier === "comblee");
  assert.deepEqual(s1.cases.slice(0, 24), pool.slice(24, 48), "le tour suivant reprend après la dernière case");
  assert.equal(M.choisirSuite(CR, P, "donjon", T).raison, "ferme", "aucun donjon ouvert");
  // Détour par le donjon : il s'ouvre, et le tour suivant est déjà posé pour le retour.
  P.options.donjons = ["ordinateur"];
  const sd = M.choisirSuite(CR, P, "donjon", T);
  assert.ok(sd.ok && sd.donjon === "ordinateur" && sd.entree.ok && sd.entree.premiere, "détour par le donjon");
  delete P.options.donjons;
  assert.deepEqual(M.routeTour(CR, P), s1.cases); assert.equal(P.plateau.position, pool[24]);
  // Réglage : 12 cases par tour.
  P.options.casesTour = 12; assert.equal(M.casesParTour(CR, P), 12);
  boucler(P, 50); assert.deepEqual(P.plateau.parcoursSuivant.cases.slice(0, 12), pool.slice(48, 60));
  P.options.casesTour = 48;
  let fin = null;
  for (let k = 0; k < 20 && !fin; k++) { M.choisirSuite(CR, P, "tour", T); fin = boucler(P, 50).etapes.find(e => e.type === "tour_fini" && e.victoire); }
  assert.ok(fin, "toutes les cases vues : victoire"); assert.equal(P.compteurs.victoires, 1);
  assert.equal(P.plateau.parcoursSuivant.cases[0], pool[0], "et l'histoire recommence au début");
  console.log("OK : parcours chronologique, coupé au réglage, victoire au bout");
}

// v25 : Alyca donne son nom la première fois qu'elle est comblée, et le garde.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  const T = Date.UTC(2026, 9, 1, 8), J = 86400000;
  const P = M.nouvellePartie(T);
  M.faveurIA(C, P, T); assert.equal(M.nomIA(C, P), null, "pas de nom au départ");
  P.faveur = { valeur: 90, maj: T }; M.faveurIA(C, P, T);
  assert.equal(P.alyca.vu, false); assert.equal(M.nomIA(C, P), null, "pas de nom avant la scène de révélation"); P.alyca.vu = T; assert.equal(M.nomIA(C, P), "Alyca");
  P.faveur = { valeur: 5, maj: T + J }; M.faveurIA(C, P, T + 2 * J);
  assert.equal(M.nomIA(C, P), "Alyca", "fâchée, elle garde son nom donné");
  assert.equal(M.migrer(JSON.parse(JSON.stringify(P)), C).alyca.depuis, T);
  console.log("OK : v25 Alyca révèle son nom, pour de bon");
}

// Victor (2026-10-31) : plus d'achat « Avancer d'une case ».
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  const T = Date.UTC(2026, 9, 1, 8);
  const P = M.nouvellePartie(T); P.credits.solde = 200;
  assert.ok(!M.acheter(C, P, "avancer", T).ok); assert.equal(P.credits.solde, 200);
  assert.ok(!C.boutique || !(C.boutique.articles || C.boutique).some || !(C.boutique.articles || C.boutique).some(a => a.id === "avancer"));
  console.log("OK : plus d'achat Avancer d'une case");
}

// v27 : furieuse, l'IA est sèche ; à 0, le jeu ferme jusqu'au lendemain, où sa faveur remonte d'elle-même.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  const T = new Date(2026, 9, 1, 10).getTime(), J = 86400000, F = d("ia.json").faveur;
  const P = M.nouvellePartie(T); P.decalage = T - Date.now();
  P.faveur = { valeur: 10, maj: T };
  for (const [ctx, attendu] of [["ennemi", "furieuse_ennemi"], ["quiz_reussi", "furieuse_reussi"], ["jouer_case", "furieuse_jouer"], ["masque", "furieuse_defaut"]]) {
    const r = M.replique(C, P, [ctx], () => 0.3);
    assert.equal(r.contexte, attendu, ctx + " → " + attendu);
    assert.ok(!/Arbitrage officiel/.test(r.texte.fr));
  }
  assert.equal(M.replique(C, P, ["pot_radin"]).contexte, "pot_radin", "le pot-de-vin garde ses lignes");
  assert.equal(M.repliqueDuJour(C, P, T).contexte.indexOf("furieuse") >= 0 || M.repliqueDuJour(C, P, T).contexte === "faveur_furieuse", true);
  assert.equal(M.jeuFerme(C, P, T), false, "furieuse mais encore ouverte");
  // L'absence seule ne la fait pas tomber à 0.
  assert.equal(M.faveurIA(C, P, T + 30 * J).valeur, 1); assert.equal(M.jeuFerme(C, P, T + 30 * J), false);
  // Les erreurs la font tomber à 0 : enfermé au mur de la honte, le jeu fermé tant que la peine court.
  P.faveur = { valeur: 3, maj: T };
  M.agacerIA(C, P, 5, true, T + 3600e3);
  assert.equal(M.faveurIA(C, P, T + 3600e3).valeur, 0); assert.ok(M.jeuFerme(C, P, T + 5 * 3600e3));
  assert.equal(P.punition.restant, F.mur.nulle * 60000);
  assert.equal(M.repliqueDuJour(C, P, T + 5 * 3600e3).contexte, "mur_force");
  assert.equal(M.enRayon(C, P, "avancer", T + 5 * 3600e3).length, 0, "pas d'avance achetée, enfermé");
  // Le temps hors du mur ne compte pas ; seul purger (mur affiché) fait avancer la peine.
  assert.ok(M.jeuFerme(C, P, T + 10 * 3600e3));
  assert.equal(M.purger(P, F.mur.nulle * 60000 - 1000), 1000); assert.equal(M.purger(P, 1000), 0);
  assert.equal(M.jeuFerme(C, P, T + 10 * 3600e3), false, "peine purgée, on rejoue");
  // Le lendemain, elle remonte d'elle-même et le dit.
  const f = M.faveurIA(C, P, T + J);
  assert.equal(f.valeur, F.remontee); assert.equal(M.jeuFerme(C, P, T + J), false);
  assert.equal(M.repliqueDuJour(C, P, T + J).contexte, "faveur_remontee");
  console.log("OK : v27 IA furieuse sèche ; v28 à 0, enfermé au mur, remontée le lendemain");
}

// v28 : chaque chute sous un palier enferme au mur, de plus en plus longtemps dans la journée.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  const T = new Date(2026, 9, 2, 10).getTime(), F = d("ia.json").faveur;
  const P = M.nouvellePartie(T); P.decalage = T - Date.now();
  P.faveur = { valeur: 50, maj: T }; M.faveurIA(C, P, T);
  assert.equal(P.punition || null, null, "pas de peine au départ");
  M.agacerIA(C, P, 10, true, T + 1000);                       // contente → boudeuse (ou plus bas)
  const p1 = P.punition; assert.ok(p1 && p1.restant >= F.mur.boudeuse * 60000);
  M.purger(P, p1.restant);
  P.faveur = { valeur: 25, maj: T + 2000 }; M.faveurIA(C, P, T + 2000);
  P.faveur = { valeur: 15, maj: T + 3000 }; M.faveurIA(C, P, T + 3000);  // → furieuse : 2e chute du jour, doublée
  assert.equal(P.punition.restant, F.mur.furieuse * 60000 * 2);
  // Un cadeau la fait remonter : pas de peine en remontant.
  M.purger(P, P.punition.restant);
  P.faveur = { valeur: 80, maj: T + 4000 }; M.faveurIA(C, P, T + 4000);
  assert.equal(P.punition, null);
  assert.ok(M.migrer(JSON.parse(JSON.stringify(P)), C));
  // Victor (2026-11-08) : seulement des compétences croisées (jouées, ratées ou dont on a vu la case), jamais à venir.
  const avantJeu = M.fichesImposees(C, P, T, 3), cc = C.plateau.competences_cases, ici = cc[P.plateau.position] || [];
  assert.ok(avantJeu.every(k => ici.includes(k.id)), "partie neuve : rien que la case de départ");
  const jouees = C.competences.filter(k => k.fiche && !ici.includes(k.id)).slice(0, 3);
  jouees.forEach(k => { P.competences[k.id] = { maitrise: false }; });
  const fi = M.fichesImposees(C, P, T, 3);
  assert.equal(fi.length, 3, "trois fiches imposées");
  assert.ok(fi.every(k => P.competences[k.id] || ici.includes(k.id)), "fiches des compétences croisées seulement");
  console.log("OK : v28 chutes de faveur, peines au mur qui doublent");
}

// v29 : un rappel réussi au mur la radoucit d'un point, plafonné par jour.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  const A = C.ia.credits.agacement, T = Date.UTC(2026, 9, 29, 9);
  const P = M.nouvellePartie(T - 86400000);
  P.faveur = { valeur: 30, maj: T };
  let total = 0;
  for (let i = 0; i < A.rappel_mur_jour + 3; i++) { const r = M.radoucirIA(C, P, T + i * 1000); total += r.gain; }
  assert.equal(total, A.rappel_mur_jour, "plafond du jour");
  assert.ok(M.radoucirIA(C, P, T + 9000).plafond);
  assert.equal(M.radoucirIA(C, P, T + 86400000).gain, A.rappel_mur, "le lendemain, ça repart");
  console.log("OK : v29 rappels du mur qui radoucissent l'IA");
}

// v29 : peine plafonnée à mur_max minutes ; chaque rattrapage réussi au mur retire une minute.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  const T = new Date(2026, 9, 3, 10).getTime(), F = d("ia.json").faveur;
  const P = M.nouvellePartie(T); P.decalage = T - Date.now();
  P.faveur = { valeur: 50, maj: T }; M.faveurIA(C, P, T);
  P.faveur = { valeur: 30, maj: T + 1000 }; M.faveurIA(C, P, T + 1000);    // boudeuse : 2 min
  P.faveur = { valeur: 10, maj: T + 2000 }; M.faveurIA(C, P, T + 2000);    // furieuse, 2e chute : 10 min, plafonné
  P.faveur = { valeur: 0, maj: T + 3000 }; M.faveurIA(C, P, T + 3000);     // 0, 3e chute : rien au-delà du plafond
  assert.equal(P.punition.restant, F.mur_max * 60000, "plafond de la peine");
  assert.equal(M.questionRattrapage(C, P, T + 3500, () => 0), null, "rien de croisé : pas de rattrapage");
  P.competences[C.competences[0].id] = { maitrise: false };  // une compétence jouée
  const q = M.questionRattrapage(C, P, T + 4000, () => 0);
  assert.ok(q, "une question de rattrapage");
  assert.equal(q.competence, C.competences[0].id, "tirée dans ce qu'on a croisé");
  assert.equal(M.questionRattrapage(C, P, T + 4000, () => 0.99).id, q.id, "gardée jusqu'à la réponse");
  let r = M.repondreRattrapage(C, P, false, T + 5000);
  assert.equal(r.gagne, 0); assert.equal(P.punition.restant, F.mur_max * 60000, "ratée : rien de retiré");
  M.questionRattrapage(C, P, T + 6000);
  r = M.repondreRattrapage(C, P, true, T + 7000);
  assert.equal(P.punition.restant, (F.mur_max - F.mur_rattrapage) * 60000, "réussie : une minute de moins");
  assert.ok(r.replique);
  M.purger(P, P.punition.restant - 30000);
  M.questionRattrapage(C, P, T + 8000);
  r = M.repondreRattrapage(C, P, true, T + 9000);
  assert.ok(r.libere && P.punition === null && !M.jeuFerme(C, P, T + 9000), "la dernière minute libère");
  console.log("OK : v29 peine plafonnée, rattrapage au mur");
}

// v30 : enfermé, une question à retenter réussie retire aussi une minute.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  const T = new Date(2026, 9, 4, 10).getTime(), J = 86400000;
  const P = M.nouvellePartie(T - 2 * J); P.decalage = T - Date.now();
  const qs = C.questions.filter(q => q.competence === "math.chine").slice(0, 2);
  M.terminerQuiz(C, P, "math.chine", qs.map(q => ({ id: q.id, correct: false })), T - J, { alea: () => 0.99 });
  P.faveur = { valeur: 50, maj: T }; M.faveurIA(C, P, T);
  P.punition = { restant: 300000, total: 300000, palier: "furieuse", rang: 2, depuis: T, n: 1 };
  const x = M.murDeLaHonte(C, P, T).avant[0];
  M.faveurIA(C, P, T + 1000); const avant = P.punition.restant;
  const r = M.retenterOubli(C, P, x.index, true, T + 1000);
  assert.equal(r.peine.gagne, 60000); assert.equal(P.punition.restant, avant - 60000, "une minute de moins");
  assert.ok(P.oublis[x.index].essai >= P.punition.depuis);
  console.log("OK : v30 questions à retenter qui comptent pour la peine");
}

// v31 : un duel gagné la ravit (duel_gagne), bien plus qu'un sans-faute.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  const T = new Date(2026, 9, 5, 10).getTime(), A = C.ia.credits.agacement;
  const P = M.nouvellePartie(T); P.decalage = T - Date.now(); P.faveur = { valeur: 40, maj: T };
  const g = M.agacerIA(C, P, 0, false, T, "duel_gagne");
  assert.equal(g.gain, A.duel_gagne); assert.ok(A.duel_gagne > A.sans_faute); assert.equal(g.raison, "duel_gagne");
  assert.equal(M.agacerIA(C, P, 0, false, T).gain, A.sans_faute);
  console.log("OK : v31 duel gagné, faveur ravie");
}

// v31 : la case évoque des compétences précises ; verrouillées, l'IA passe par un prérequis qui y mène.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  const T = new Date(2026, 9, 6, 10).getTime();
  const P = M.nouvellePartie(T); P.decalage = T - Date.now();
  const mendel = C.plateau.cases.find(k => k.id && C.plateau.competences_cases[k.n].includes("sci.genetique") && /Mendel/.test(k.titre.fr));
  P.plateau.position = mendel.n;
  const x = M.choixIA(C, P, T);
  assert.equal(x.stat, "savoir");
  const dispo = M.disponibles(C, P, T).some(c => c.id === "sci.genetique");
  // Victor (2026-10-31) : même verrouillée, la compétence de la case est jouée (l'ambre sur la case de l'ambre).
  assert.equal(x.comp.id, "sci.genetique", "la case donne sa propre compétence");
  if (!dispo) assert.ok(x.horsOrdre, "verrouillée : jouée hors ordre");
  if (!dispo) {
    const k = C.parId["sci.genetique"];
    M.terminerQuiz(C, P, k.id, Array.from({ length: 5 }, (_, i) => ({ id: "q" + i, correct: true })), T, { total: 5 });
    const st = M.statut(C, P, k.id, T);
    assert.equal(st.etat, "maitrisee"); assert.ok(st.horsOrdre && st.gelee, "acquise hors ordre, ne débloque pas la suite");
    assert.ok(C.competences.filter(c => c.prerequis.includes(k.id)).every(c => M.statut(C, P, c.id, T).etat !== "disponible"), "la suite reste fermée");
  }
  console.log("OK : v31 case → compétence évoquée (" + x.comp.id + ")");
}

// Victor (2026-10-31) : « une case = un quiz ». Déjà acquise, la compétence de la case revient en rappel anticipé :
// réussi, ni palier ni échéance ne bougent ; raté, il devient dû sans perdre la compétence.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  const T = new Date(2026, 9, 6, 10).getTime();
  const P = M.nouvellePartie(T); P.decalage = T - Date.now();
  const n = +Object.keys(C.plateau.competences_cases).find(k => C.plateau.competences_cases[k].includes("elec.torpille"));
  P.plateau.position = n;
  const x0 = M.choixIA(C, P, T);
  assert.equal(x0.comp.id, "elec.torpille"); assert.equal(x0.type, "quiz");
  M.terminerQuiz(C, P, "elec.torpille", Array.from({ length: 5 }, (_, i) => ({ id: "q" + i, correct: true })), T, { total: 5 });
  P.plateau.position = n; P.revision = null;
  const x = M.choixIA(C, P, T + 60000);
  assert.equal(x.comp.id, "elec.torpille", "la case garde son quiz"); assert.equal(x.type, "rappel");
  const e = P.competences["elec.torpille"], ech = e.prochainRappel, pal = e.palier || 0;
  const ok = M.terminerRappel(C, P, "elec.torpille", [0, 1, 2].map(i => ({ id: "q" + i, correct: true })), T + 120000, { total: 3 });
  assert.ok(ok.anticipe && ok.issue === "reussi"); assert.equal(e.prochainRappel, ech); assert.equal(e.palier || 0, pal);
  const ko = M.terminerRappel(C, P, "elec.torpille", [0, 1, 2].map(i => ({ id: "q" + i, correct: false })), T + 180000, { total: 3 });
  assert.equal(ko.issue, "echec"); assert.ok(e.maitrise, "gardée"); assert.equal(e.prochainRappel, T + 180000, "rappel dû");
  console.log("OK : une case = un quiz (rappel anticipé sur sa case)");
}

// Victor (2026-10-31) : une épreuve sur 3, Alyca impose un rappel dû (pion sur place) ; elle propose ensuite d'enchaîner
// les rappels en attente contre une prime, versée seulement si tous sont réussis.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  C.plateau.regles.evenements = null;
  const T = new Date(2026, 9, 8, 10).getTime(), J = 86400000, N = C.regles.rappels.force_tous;
  const P = M.nouvellePartie(T); P.decalage = T - Date.now();
  const ids = ["elec.ambre", "elec.torpille", "elec.boussole"];
  ids.forEach(id => { P.competences[id] = { maitrise: true, palier: 1, prochainRappel: T - J, xp: 10, maitriseDepuis: T - 5 * J }; });
  const libre = +Object.keys(C.plateau.competences_cases).find(n => !C.plateau.competences_cases[n].some(id => ids.includes(id)) && !C.plateau.competences_cases[n].some(id => id.startsWith("elec.")));
  P.plateau.position = libre; P.depuisRappel = N - 1;
  assert.notEqual(M.choixIA(C, P, T).raison, "rappel_force", "pas encore");
  P.depuisRappel = N;
  const x = M.choixIA(C, P, T);
  assert.equal(x.raison, "rappel_force"); assert.ok(ids.includes(x.comp.id));
  const pos = P.plateau.position;
  const r = M.terminerRappel(C, P, x.comp.id, [0, 1, 2].map(i => ({ id: "q" + i, correct: true })), T, { total: 3, jouer: true });
  assert.ok(r.horsCase); assert.equal(P.plateau.position, pos, "le pion reste sur sa case"); assert.equal(P.depuisRappel, 0);
  const sp = M.serieProposable(C, P, T); assert.equal(sp.n, 2);
  M.lancerSerie(C, P, T);
  const solde = P.credits.solde;
  for (let i = 0; i < 2; i++) {
    const y = M.choixIA(C, P, T + i); assert.equal(y.raison, "serie"); assert.equal(y.serie.n, i + 1);
    const ry = M.terminerRappel(C, P, y.comp.id, [0, 1, 2].map(j => ({ id: "s" + j, correct: true })), T + i, { total: 3, jouer: true });
    if (i === 1) { assert.ok(ry.serie.fini && ry.serie.credits === sp.prime); }
  }
  assert.equal(P.credits.solde - solde >= sp.prime, true, "prime versée"); assert.equal(P.serie, null);
  // Victor (2026-11-11) : en série le pion ne bouge pas, et un raté laisse reprendre la série avec les rappels restants.
  {
    const Q = JSON.parse(JSON.stringify(P)), T2 = T + 400 * 86400000;
    const dus = M.rappelsDus(C, Q, T2); assert.ok(dus.length >= 3, "au moins 3 rappels dus");
    assert.equal(M.serieReprenable(C, Q, T2), null, "rien à reprendre sans série rompue");
    M.lancerSerie(C, Q, T2);
    const pos2 = Q.plateau.position, a = M.choixIA(C, Q, T2);
    const ra = M.terminerRappel(C, Q, a.comp.id, [0, 1, 2].map(j => ({ id: "t" + j, correct: false })), T2, { total: 3, jouer: true });
    assert.ok(ra.serie.rate && ra.horsCase); assert.equal(Q.serie, null); assert.equal(Q.plateau.position, pos2);
    const rp = M.serieReprenable(C, Q, T2); assert.ok(rp && rp.n === ra.serie.reste && rp.n >= 2);
    assert.equal(M.serieReprenable(C, Q, T2 + 2 * 86400000), null, "la reprise ne vaut que le jour même");
    M.reprendreSerie(C, Q, T2); assert.equal(Q.serie.total, rp.n); assert.equal(Q.serieRompue, null);
    const b = M.choixIA(C, Q, T2 + 1); assert.equal(b.raison, "serie"); assert.equal(b.serie.n, 1);
    const rb = M.terminerRappel(C, Q, b.comp.id, [0, 1, 2].map(j => ({ id: "u" + j, correct: true })), T2 + 1, { total: 3, jouer: true });
    assert.ok(!rb.serie.fini && rb.horsCase); assert.equal(Q.plateau.position, pos2, "le pion ne bouge pas pendant la série");
  }
  console.log("OK : rappel imposé une épreuve sur " + N + ", série de révisions et sa prime (" + sp.prime + ")");
}

// Victor (2026-10-31) : une année à taper est juste à 50 ans près.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), {});
  const q = C.questions.find(q => q.id === "elec.boussole.q10");
  assert.ok(q.annee); assert.ok(M.corriger(q, String(q.reponse - 50)) && M.corriger(q, String(q.reponse + 50)));
  assert.ok(!M.corriger(q, String(q.reponse + 51)));
  assert.ok(!C.questions.find(q => q.id === "math.inde.q05").annee, "un âge n'est pas une année");
  console.log("OK : années à 50 ans près (" + C.questions.filter(q => q.annee).length + " questions)");
}

// v31 : réussie avec des fautes, la faveur monte quand même un peu ; ratée, elle baisse.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  const T = new Date(2026, 9, 7, 10).getTime(), A = C.ia.credits.agacement;
  const P = M.nouvellePartie(T); P.decalage = T - Date.now(); P.faveur = { valeur: 40, maj: T };
  const r = M.agacerIA(C, P, 1, false, T);
  assert.equal(r.gain, A.reussi); assert.equal(r.raison, "reussi"); assert.equal(M.faveurIA(C, P, T).valeur, 40 + A.reussi);
  assert.ok(M.agacerIA(C, P, 1, true, T).perte > 0, "ratée : elle s'agace");
  console.log("OK : v31 réussite avec fautes, faveur positive");
}

// v32 : « Piège ! » Une case piège arrête le pion sur une question difficile ; juste, le piège est déjoué ; faux, il se déclenche.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  const T = new Date(2026, 9, 7, 10).getTime();
  C.plateau.regles.evenements = null;
  const prep = () => { const P = M.nouvellePartie(T); P.decalage = T - Date.now(); P.plateau.ennemis = {}; P.sauvages = []; P.plateau.speciaux = { 21: { type: "recul", n: 2 } }; const rt = M.routeTour(C, P); const i = rt.indexOf(21); P.plateau.idx = i - 1; P.plateau.position = rt[i - 1]; return P; };
  let P = prep();
  let dep = M.deplacer(C, P, 1, T, "quiz");
  assert.ok(dep.etapes.some(e => e.type === "piege") && P.plateau.position === 21 && M.piegeEnAttente(P), "le pion s'arrête sur le piège");
  const q = M.questionPiege(C, P, () => 0.3);
  assert.ok(q.type !== "vrai_faux" && C.parId[q.competence].rang >= 5, "question difficile");
  assert.ok(M.deplacer(C, P, 2, T, "quiz").etapes.some(e => e.type === "bloque_piege") && P.plateau.position === 21, "bloqué tant que la question attend");
  const rate = M.repondrePiege(C, P, false, T);
  assert.ok(!rate.dejoue && P.plateau.position < 21 && !M.piegeEnAttente(P) && rate.plateau.etapes.some(e => e.type === "recul"), "raté : le recul s'applique");
  P = prep(); M.deplacer(C, P, 1, T, "quiz"); M.questionPiege(C, P);
  const ok = M.repondrePiege(C, P, true, T);
  assert.ok(ok.dejoue && P.plateau.position === 21 && !M.piegeEnAttente(P), "juste : le piège est déjoué");
  console.log("OK : v32 question piège");
}

// v34 : Chrono, le jeu des siècles. Créneaux sans an zéro, réservoir des choses débloquées, case qui sert d'épreuve,
// partie offerte par Alyca, niveaux par événement, crédits juste / proche / rapide.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  // Les dates approchées (champ date) ne se jouent qu'au siècle : test à part (C_DATES) ; le reste du bloc les traite en années.
  const C_DATES = Object.assign({}, C, { evenements: C.evenements.map(e => Object.assign({}, e)) });
  C.evenements.forEach(e => { delete e.date; }); (C.livres || []).forEach(l => { delete l.date; });
  const R = M.reglesChrono(C), T = new Date(2026, 9, 7, 10).getTime();
  // Créneaux : siècles au sens propre, pas d'an zéro, Préhistoire à part.
  assert.equal(M.creneau(1901, 100), 19); assert.equal(M.creneau(2000, 100), 19); assert.equal(M.creneau(2001, 100), 20);
  assert.equal(M.creneau(1, 100), 0); assert.equal(M.creneau(-1, 100), -1); assert.equal(M.creneau(-100, 100), -1); assert.equal(M.creneau(-101, 100), -2);
  assert.equal(M.creneau(1, 1) - M.creneau(-1, 1), 1, "de 1 av. J.-C. à l'an 1 : un an");
  assert.equal(M.creneau(1689, 10), M.creneau(1680, 10)); assert.notEqual(M.creneau(1690, 10), M.creneau(1689, 10));
  assert.equal(M.creneau(-590, 10), M.creneau(-581, 10)); assert.notEqual(M.creneau(-580, 10), M.creneau(-581, 10));
  assert.equal(M.creneau(-400000, 100, R.prehistoire), M.creneau(-20000, 100, R.prehistoire), "une seule Préhistoire");
  for (const pas of [100, 50, 10, 1]) for (const k of [-45, -41, -2, -1, 0, 1, 19, 20, 168, 2025]) assert.equal(M.creneau(M.anneeDuCreneau(k, pas), pas), k, pas + "/" + k);
  assert.equal(M.texteCreneau(16, 100), "XVIIe siècle"); assert.equal(M.texteCreneau(0, 100), "Ier siècle"); assert.equal(M.texteCreneau(-6, 100), "VIe siècle av. J.-C.");
  assert.equal(M.texteCreneau(M.creneau(1687, 50), 50), "2de moitié du XVIIe siècle"); assert.equal(M.texteCreneau(M.creneau(1687, 10), 10), "1680-1689");
  assert.equal(M.texteCreneau(M.creneau(-585, 1), 1), "585 av. J.-C.");

  const prep = () => {
    const P = M.nouvellePartie(T); P.decalage = T - Date.now(); P.plateau.ennemis = {}; P.sauvages = []; P.faveur = { valeur: 60, maj: T };
    for (const e of C.evenements.slice(0, 12)) P.evenements[e.id] = T;
    P.savants.aristote = T;
    // Victor (2026-11-01) : Chrono ne puise que dans ce qui tient aux compétences apprises ; ici, toutes.
    const cc = C.plateau.competences_cases, ids = new Set();
    for (const e of C.evenements.slice(0, 12)) {
      if (e.condition.type === "competence_maitrisee") ids.add(e.condition.id);
      else (cc[String(e.condition.n)] || [C.parStat[e.stat][0].id]).forEach(id => ids.add(id));
    }
    ids.add(C.parStat[C.avatar.savants.find(s => s.id === "aristote").theme][0].id);
    ids.forEach(id => { P.competences[id] = { maitrise: true, maitriseDepuis: T, palier: 6, prochainRappel: T + 400 * 86400000, xp: 80 }; });
    // Les succès que ces compétences ouvrent sont déjà là : le lot reste libre pour ceux de Chrono.
    for (let i = 0; i < 60; i++) { P.lot = null; const r = M.verifierRecompenses(C, P, T - 1); if (!r.succes.length && !r.savants.length && !r.livres.length) break; } P.lot = null; P.savants = { aristote: T }; P.livres = {}; P.objets = {};
    return P;
  };
  { const N = prep(); N.competences = {};
    assert.equal(M.reservoirChrono(C, N).length, 0, "rien sans compétence apprise"); }
  let P = prep();
  const pool = M.reservoirChrono(C, P);
  assert.ok(C.evenements.slice(0, 12).every(e => pool.some(x => x.cle === "frise:" + e.id)) && pool.some(x => x.cle === "savant:aristote"), "les 12 dates et Aristote, chacun lié à une compétence apprise"); assert.ok(pool.every(x => x.texte == null || !/\d{3,4}/.test(x.texte)), "pas de phrase qui donne la date");
  assert.ok(pool.find(x => x.id === "feu").max === 1, "la Préhistoire reste au siècle");
  { const Q = prep(), approx = C_DATES.evenements.find(e => e.date && e.annee > -10000); Q.evenements[approx.id] = T;
    assert.equal(M.reservoirChrono(C_DATES, Q).find(x => x.id === approx.id).max, 1, "date approchée : Chrono ne demande que le siècle"); }
  // Rien sans case ni offre ; trop peu d'éléments : pas de partie.
  assert.equal(M.lancerChrono(C, P, "case", T), null); assert.equal(M.lancerChrono(C, P, "alyca", T), null);
  const vide = M.nouvellePartie(T); vide.decalage = T - Date.now();
  assert.equal(M.chronoSpontane(C, vide, T, () => 0), false, "réservoir trop maigre");

  // Case Chrono : le pion s'y arrête, Jouer lance la partie ; 3 justes sur 5, il avance.
  // Victor (2026-10-31) : plus de case Chrono fixe ; Alyca en pose une sur la route (ici, à la main).
  C.plateau.regles.evenements = null;
  P.plateau.speciaux = { [R.cases[0]]: { type: "chrono" } };
  const rt = M.routeTour(C, P), i14 = rt.indexOf(R.cases[0]);
  P.plateau.idx = i14 - 2; P.plateau.position = rt[i14 - 2];
  let dep = M.deplacer(C, P, 2, T, "quiz");
  assert.ok(dep.etapes.some(e => e.type === "chrono") && M.chronoEnAttente(P), "arrêt sur la case Chrono");
  assert.ok(M.deplacer(C, P, 0, T, "quiz").etapes.length === 0 && M.chronoEnAttente(P));
  let j = M.lancerChrono(C, P, "case", T, () => 0.4);
  assert.equal(j.questions.length, R.evenements);
  const siecles = j.questions.map(q => M.creneau(q.debut, 100, R.prehistoire));
  assert.equal(new Set(siecles).size, siecles.length, "pas deux fois le même siècle");
  assert.strictEqual(M.lancerChrono(C, P, "case", T), j, "une partie commencée se reprend");
  const credAvant = P.credits.solde;
  const rep = [];
  j.questions.forEach((q, i) => {
    const k = M.creneau(q.debut, 100, R.prehistoire);
    // 3 justes (dont 1 rapide), 1 proche, 1 faux
    const annee = i < 3 ? q.debut : i === 3 ? M.anneeDuCreneau(k + 1, 100) : M.anneeDuCreneau(k + 5, 100);
    rep.push(M.repondreChrono(C, P, annee, i === 0 ? 3000 : 20000, T));
  });
  assert.deepEqual(rep.map(r => r.verdict), ["juste", "juste", "juste", "proche", "faux"]);
  assert.ok(rep[0].rapide && !rep[1].rapide);
  assert.equal(M.repondreChrono(C, P, 1500, 1000, T), null, "plus de question");
  const posAvant = P.plateau.position;
  let fin = M.terminerChrono(C, P, T, () => 0.99);
  assert.ok(fin.reussi && !fin.parfait && fin.points === 2 * 3 + 1 + 1, "points : 3 justes, 1 rapide, 1 proche");
  assert.equal(P.credits.solde - credAvant >= fin.credits, true);
  assert.ok(fin.plateau && P.plateau.position !== posAvant && !M.chronoEnAttente(P), "réussi : le pion avance");
  assert.ok(fin.plateau.valeurs.base === 1, "une case, comme toute épreuve");
  assert.equal(P.siecles.parties, 1);
  assert.ok(M.verifierRecompenses(C, P, T + 1).succes.concat(fin.recompenses.succes).some(s => s.id === "chrono-1") || P.succes["chrono-1"], "succès de la première partie");
  // Le faux est retenu, il revient en tête au prochain tirage.
  const rate = j.questions[4].cle;
  assert.ok(P.siecles.fiches[rate].rate);

  // Échec sur la case : la case est consommée, le pion ne bouge pas.
  P = prep(); P.plateau.speciaux = { [R.cases[0]]: { type: "chrono" } }; P.plateau.idx = i14 - 2; P.plateau.position = rt[i14 - 2]; M.deplacer(C, P, 2, T, "quiz");
  j = M.lancerChrono(C, P, "case", T, () => 0.1);
  j.questions.forEach(q => M.repondreChrono(C, P, M.anneeDuCreneau(M.creneau(q.debut, 100, R.prehistoire) + 9, 100), 20000, T));
  const ici = P.plateau.position; fin = M.terminerChrono(C, P, T);
  assert.ok(!fin.reussi && P.plateau.position === ici && !M.chronoEnAttente(P) && fin.agacement && fin.agacement.perte > 0);

  // Alyca : une offre par jour au plus ; partie bonus, le pion ne bouge pas.
  // Victor (2026-11-01) : Chrono revient d'abord sur les cases déjà passées.
  { const V = prep(); V.plateau.idx = 6; const ev = C.evenements.slice(0, 12).filter(e => e.case && e.case !== V.plateau.position && e.id !== "feu").slice(0, 2);  // le feu et Ishango se disputent l'unique place de la Préhistoire
    V.plateau.visites = {}; ev.forEach(e => { V.plateau.visites[e.case] = 1; });
    V.siecles = undefined; M.etatChrono(V).offre = M.cleJour(T);
    const jv = M.lancerChrono(C, V, "alyca", T, () => 0.5);
    assert.ok(ev.every(e => jv.questions.some(q => q.cle === "frise:" + e.id)), "les dates des cases passées d'abord"); }
  // Victor (2026-11-01) : jamais avant la 5e case du premier tour, et coupé par le réglage « Jeu Chrono ».
  P = prep(); P.plateau.idx = 2;
  assert.equal(M.chronoPossible(C, P), false, "pas de Chrono au tout début");
  assert.equal(M.chronoSpontane(C, P, T, () => 0.1), false);
  P.plateau.idx = 5; assert.equal(M.chronoPossible(C, P), true, "Chrono possible dès la 5e case");
  P.options.jeuChrono = false;
  assert.equal(M.chronoPossible(C, P), false, "réglage coupé");
  assert.equal(M.chronoSpontane(C, P, T, () => 0.1), false);
  P = prep(); P.plateau.idx = 5;
  assert.equal(M.chronoSpontane(C, P, T, () => 0.9), false);
  assert.equal(M.chronoSpontane(C, P, T, () => 0.1), true); assert.ok(M.offreChrono(P, T));
  j = M.lancerChrono(C, P, "alyca", T, () => 0.5);
  const pos = P.plateau.position;
  j.questions.forEach(q => M.repondreChrono(C, P, q.debut, 1000, T));
  fin = M.terminerChrono(C, P, T);
  assert.ok(fin.parfait && fin.points === 5 * 3 + R.points.parfait && P.plateau.position === pos && !fin.plateau);
  assert.ok(fin.agacement && fin.agacement.gain > 0, "sans faute : elle est ravie");
  assert.ok(!M.offreChrono(P, T) && M.chronoSpontane(C, P, T, () => 0) === false, "une fois par jour");
  assert.equal(M.chronoSpontane(C, P, T + 86400000, () => 0), true, "le lendemain, elle recommence");

  // Niveaux : deux justes de suite font monter d'un cran, une erreur fait redescendre ; le savant : siècle de sa vie.
  P = prep(); const s = M.etatChrono(P);
  const ar = M.reservoirChrono(C, P).find(x => x.id === "aristote");
  assert.ok(ar.debut === -384 && ar.fin === -322);
  // Assez de parties pour que des événements reviennent (le réservoir s'épuise d'abord).
  for (let n = 0; n < 8; n++) {
    s.offre = M.cleJour(T); s.joueJour = null;
    j = M.lancerChrono(C, P, "alyca", T + n, () => 0.5);
    j.questions.forEach(q => M.repondreChrono(C, P, q.id === "aristote" && q.pas >= 50 ? -330 : q.debut, 20000, T + n));
    M.terminerChrono(C, P, T + n);
  }
  const maxDe = {}; M.reservoirChrono(C, P).forEach(x => { maxDe[x.cle] = x.max; });
  assert.ok(Object.keys(s.fiches).every(k => s.fiches[k].niveau >= Math.min(2, maxDe[k]) || s.fiches[k].vus < 2), "deux justes : demi-siècle");
  const f2 = Object.keys(s.fiches).find(k => s.fiches[k].niveau >= 2);
  s.fiches[f2].niveau = 4;
  s.offre = M.cleJour(T); s.joueJour = null; s.fiches[f2].rate = true;
  j = M.lancerChrono(C, P, "alyca", T + 5, () => 0.5);
  const q4 = j.questions.find(q => q.cle === f2);
  assert.ok(q4 && (q4.pas === 1 || q4.niveau < 4), "le raté passe en tête, au niveau de sa fiche");
  if (q4.pas === 1) {
    j.questions.forEach(q => M.repondreChrono(C, P, q === q4 ? (q.naissance ? q.debut : q.debut) + 4 : q.debut, 20000, T + 5));
    assert.equal(j.reponses[j.questions.indexOf(q4)].verdict, "proche", "année : à 5 ans près, proche");
  }
  // Migration : une ancienne partie n'a pas de Chrono et n'en souffre pas.
  const vieille = JSON.parse(JSON.stringify(prep())); delete vieille.siecles;
  const mig = M.migrer(vieille, C); assert.equal(mig.siecles, null); assert.ok(!M.chronoEnAttente(mig));
  console.log("OK : v34 Chrono, le jeu des siècles");
}

// Victor (2026-10-31) : à chaque pas, Alyca tire parfois un événement qu'elle pose sur la case suivante ; plus souvent fâchée.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  const T = new Date(2026, 9, 7, 10).getTime();
  const neuve = (t, v) => { const P = M.nouvellePartie(t); P.plateau.route = null; P.plateau.idx = null; P.decalage = t - Date.now(); P.faveur = { valeur: v, maj: t }; M.routeTour(C, P); return P; };
  const tirages = v => {
    const vus = {}; let n = 0;
    for (let k = 0; k < 400; k++) {
      const t = T + k * 7919, P = neuve(t, v), e = M.tirerEvenement(C, P, t, null);
      if (!e) continue;
      n++; vus[e.quoi] = (vus[e.quoi] || 0) + 1;
      const suivante = P.plateau.route[1]; assert.equal(e.case, suivante, "sur la case suivante");
      if (e.quoi === "ennemi") assert.ok(M.ennemisPlateau(C, P)[suivante]); else assert.ok(M.specialDe(C, P, suivante).evenement);
    }
    return { n, vus };
  };
  const doux = tirages(90), dur = tirages(5);
  assert.ok(doux.n > 30 && doux.n < 140, "comblée : " + doux.n + " / 400");
  assert.ok(dur.n > doux.n, "furieuse : plus de rencontres (" + dur.n + ")");
  assert.ok((dur.vus.ennemi || 0) > (doux.vus.ennemi || 0) && (dur.vus.piege || 0) > (doux.vus.piege || 0));
  // Sans le pack ennemis, pas d'ennemi tiré.
  const sansE = Object.assign({}, C, { ennemis: [], placement: null });
  for (let k = 0; k < 100; k++) { const t = T + k * 7919, P = neuve(t, 5), e = M.tirerEvenement(sansE, P, t, null); assert.ok(!e || e.quoi !== "ennemi"); }
  // Un vrai pas : l'ennemi tiré garde la case suivante, le pion y entre et le duel commence.
  let vu = false;
  for (let k = 0; k < 300 && !vu; k++) {
    const t = T + k * 104729, P = neuve(t, 5);
    const dep = M.deplacer(C, P, 1, t, "quiz"), ev = dep.etapes.find(e => e.type === "surgit");
    if (ev && ev.quoi === "ennemi") {
      vu = true;
      assert.ok(P.duel && P.duel.case === P.plateau.position && P.plateau.position === ev.case && P.duel.reste === 0, "l'ennemi garde la case");
      assert.ok(dep.etapes.some(e => e.type === "ennemi"));
    }
  }
  assert.ok(vu, "un ennemi finit par surgir");
  console.log("OK : événements tirés à chaque pas " + JSON.stringify({ doux, dur }));
}

// v34 : sans assez d'éléments datés, une case Chrono ne retient pas le pion.
{
  const C = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json") });
  const T = new Date(2026, 9, 7, 10).getTime(), R = M.reglesChrono(C);
  const P = M.nouvellePartie(T); P.decalage = T - Date.now(); P.plateau.ennemis = {}; P.sauvages = [];
  C.plateau.regles.evenements = null; P.plateau.speciaux = { [R.cases[0]]: { type: "chrono" } };
  const rt = M.routeTour(C, P), i = rt.indexOf(R.cases[0]); P.plateau.idx = i - 1; P.plateau.position = rt[i - 1];
  const dep = M.deplacer(C, P, 1, T, "quiz");
  assert.ok(dep.etapes.some(e => e.type === "chrono_vide") && !M.chronoEnAttente(P));
  // Le tirage spontané est stable d'un affichage à l'autre.
  for (const e of C.evenements.slice(0, 12)) P.evenements[e.id] = T;
  const a = M.chronoSpontane(C, P, T), b = M.chronoSpontane(C, P, T); assert.equal(a, b);
  console.log("OK : v34 case Chrono sans réservoir");
}
{
  // v34 (Victor) : les ratés d'un combat d'atome vont au mur de la honte, avec l'astuce du numéro atomique.
  const CA = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
    { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), atomes: d("atomes.json") });
  const T = new Date(2026, 9, 29, 10).getTime();
  // Chaque élément a ses trois questions au mur ; le numéro s'écrit au clavier.
  CA.atomes.elements.forEach(e => {
    const n = CA.questionParId["atome." + e.z + ".numero"], sy = CA.questionParId["atome." + e.z + ".symbole"], ou = CA.questionParId["atome." + e.z + ".ou"];
    assert.ok(n && sy && ou && n.competence === "sci.atomes" && n.type === "numerique" && n.reponse === e.z);
    assert.equal(sy.choix[sy.reponse].fr, e.symbole);
    // Au mur, la question seule doit dire de quel atome on parle (Victor).
    [n, sy, ou, CA.questionParId["atome." + e.z + ".place"]].forEach(q => assert.ok(q.enonce.fr.includes(e.nom.fr || e.nom), q.id + " : " + q.enonce.fr));
    // L'image : ses voisins sont bien z - 1 et z + 1.
    const a = M.astuceNumero(CA.atomes, e);
    assert.deepEqual(a.voisins, [e.z - 1, e.z + 1].filter(z => z >= 1 && z <= 118)); assert.ok(a.texte.includes("n° " + e.z) && a.illustration.startsWith("<svg"));
    // Leurres du numéro éloignés d'au moins 12 entre eux et de la bonne réponse.
    const zs = n.type === "numerique" ? M.tirerCombat(CA, { sauvages: [{ z: e.z, case: 1 }], atomes: {} }, Math.random).questions[1].choix.map(Number) : [];
    zs.forEach((x, i) => zs.forEach((y, k) => { if (i < k) assert.ok(Math.abs(x - y) >= 12, e.z + " : " + zs); }));
  });
  // Les questions du mur ne se glissent pas dans les quiz ordinaires.
  assert.ok((CA.questionsPar["sci.atomes"] || []).every(q => !q.id.startsWith("atome.")));
  assert.equal(M.atomeDit(CA.atomes, "numero", "24").symbole, "Cr");
  assert.equal(M.atomeDit(CA.atomes, "symbole", "Cl").z, 17);
  const P = M.nouvellePartie(T); P.sauvages = [{ z: 26, case: 53, depuis: T }];
  const cb = M.tirerCombat(CA, P, () => 0.4);
  const symFaux = cb.questions[0].choix.find(c => c !== "Fe");
  M.terminerCombat(CA, P, 1, T, [{ type: "numero", rep: "24" }, { type: "symbole", rep: symFaux }]);
  const mur = M.murDeLaHonte(CA, P, T);
  assert.equal(mur.aujourdhui.length, 2);
  const eN = P.oublis.find(o => o.q === "atome.26.numero"), eS = P.oublis.find(o => o.q === "atome.26.symbole");
  assert.equal(eN.rep, "24"); assert.equal(eN.src, "atome"); assert.equal(eN.comp, "sci.atomes");
  const qS = CA.questionParId["atome.26.symbole"];
  assert.equal(typeof eS.rep === "string" ? eS.rep : qS.choix[eS.rep].fr, symFaux);
  // Retentable le lendemain, au clavier : 26 l'efface.
  assert.equal(M.retenterOubli(CA, P, P.oublis.indexOf(eN), true, T), null);
  const r = M.retenterOubli(CA, P, P.oublis.indexOf(eN), M.corriger(CA.questionParId["atome.26.numero"], "26"), T + 86400000);
  assert.ok(r.efface);
  // Les couches d'électrons : somme = Z, et la lecture du dessin redonne la ligne et la colonne de chaque atome.
  CA.atomes.elements.forEach(e => {
    const L = M.lectureCouches(CA.atomes, e);
    assert.equal(L.couches.reduce((a, b) => a + b, 0), e.z, e.symbole);
    assert.equal(L.ligne, e.periode, e.symbole);
    if (e.groupe) assert.equal(L.colonne, e.groupe, e.symbole + " " + L.couches);
    assert.ok(M.dessinCouches(CA.atomes, e).startsWith("<svg"));
  });
  // Placer l'atome : une question du combat, retentable au mur en touchant la case.
  const qp = CA.questionParId["atome.26.place"];
  assert.ok(qp && qp.type === "place" && M.corriger(qp, 26) && M.corriger(qp, "26") && !M.corriger(qp, 27));
  // L'indice : une récompense de moins, pas de faveur gagnée sur une capture.
  {
    const PI = M.nouvellePartie(T); PI.sauvages = [{ z: 8, case: 53, depuis: T }];
    const ri = M.terminerCombat(CA, PI, 4, T, [], true);
    assert.ok(ri.capture && ri.indice && ri.agacement === null && PI.lot.cap === 1);
  }
  // Le kit du chasseur s'achète une fois à la boutique, et reste.
  {
    const CK = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
      { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), atomes: d("atomes.json"), ennemis: d("ennemis.json") });
    const PK = M.nouvellePartie(T); PK.credits.solde = 100;
    PK.credits.solde = 250;
    const a = M.acheter(CK, PK, "kit", T);
    assert.ok(a.ok && PK.kit === T && PK.credits.solde === 150, JSON.stringify(a));
    // Une fois pour toutes : plus en rayon.
    assert.equal(M.enRayon(CK, PK, "kit", T).length, 0); assert.ok(!M.acheter(CK, PK, "kit", T).ok);
  }
  // Le guide du tableau : cinq étapes, sourcées.
  assert.equal(CA.atomes.guide.etapes.length, 5); assert.ok(CA.atomes.guide.source.includes("eduscol"));
  console.log("OK : v34 atomes ratés au mur, astuce du numéro, guide du tableau");
}

// Victor (2026-10-30) : deux épreuves ratées de suite sur la même compétence, l'IA impose la masterclass,
// levée seulement quand on l'a lue jusqu'au dernier chapitre ; une réussite remet le compteur à zéro.
{
  const T0 = new Date(2026, 9, 24, 9, 0).getTime();
  const PM = M.nouvellePartie(T0);
  const rate = M.tirerQuestions(C, PM, "math.origines", 5).map((q) => ({ id: q.id, correct: false, rep: 0 }));
  M.terminerQuiz(C, PM, "math.origines", rate, T0);
  assert.ok(!M.masterclassImposee(C, PM), "un seul échec n'impose rien");
  M.terminerQuiz(C, PM, "math.origines", rate, T0 + 1000);
  const mi = M.masterclassImposee(C, PM);
  assert.ok(mi && mi.id === "math.origines" && mi.rates.length === 5);
  assert.ok(!M.masterclassLue(PM, "math.egypte") && M.masterclassImposee(C, PM), "une autre leçon ne lève rien");
  assert.ok(M.masterclassLue(PM, "math.origines") && !M.masterclassImposee(C, PM));
  // Les repères d'histoire de chaque chapitre recopient mot pour mot son texte vérifié.
  C.competences.forEach(function (k) { (k.masterclass ? k.masterclass.chapitres : []).forEach(function (ch) {
    const corps = ch.texte.map((x) => x.fr).join(" ");
    (ch.reperes || []).forEach((h) => assert.ok(corps.includes(h.fr), k.id + "/" + ch.id));
  }); });
  console.log("OK : masterclass imposée après deux échecs, repères d'histoire");
}

// Donjons (Victor, 2026-11-02) : ateliers dans l'ordre, manipulation puis questions, pièces posées, bugs à chasser,
// panne au rappel raté, allumage ; ouvert par Logique + Étincelle réussies, ou choisi dans la nouvelle partie.
{
  const T0 = new Date(2026, 10, 2, 9, 0).getTime();
  const CD = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
    { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), donjons: d("donjons.json") });
  const PD = M.nouvellePartie(T0);
  const maitriser = (ids) => ids.forEach((id) => { PD.competences[id] = Object.assign(PD.competences[id] || {}, { maitrise: true, maitriseDepuis: T0 }); });
  assert.ok(!M.donjonOuvert(CD, PD, "ordinateur"), "fermé au départ");
  PD.options.donjons = ["ordinateur"]; assert.ok(M.donjonOuvert(CD, PD, "ordinateur"), "ouvert par le réglage de nouvelle partie");
  delete PD.options.donjons;
  maitriser(CD.parStat.logique.map((k) => k.id));
  assert.ok(!M.donjonOuvert(CD, PD, "ordinateur"), "la Logique seule ne suffit pas");
  maitriser(CD.parStat.etincelle.map((k) => k.id));
  assert.ok(M.donjonOuvert(CD, PD, "ordinateur"), "Logique + Étincelle réussies");
  // Victor (2026-11-08) : avec le plateau, il suffit de réussir la dernière case de chaque arbre du donjon.
  {
    const CDp = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
      { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), donjons: d("donjons.json"), plateau: d("plateau.json") });
    const Q = M.nouvellePartie(T0), dern = s => CDp.plateau.competences_cases[M.derniereCase(CDp, s).n];
    assert.ok(!M.donjonOuvert(CDp, Q, "ordinateur"), "fermé au départ");
    dern("logique").forEach(id => { Q.competences[id] = { maitrise: true, maitriseDepuis: T0 }; });
    assert.ok(!M.donjonOuvert(CDp, Q, "ordinateur"), "la dernière case de la Logique seule ne suffit pas");
    dern("etincelle").forEach(id => { Q.competences[id] = { maitrise: true, maitriseDepuis: T0 }; });
    assert.ok(M.donjonOuvert(CDp, Q, "ordinateur"), "dernières cases de la Logique et de l'Étincelle réussies");
    assert.ok(Object.keys(Q.competences).length < CDp.parStat.logique.length, "sans réussir tout l'arbre");
  }
  assert.ok(M.entrerDonjon(CD, PD, "ordinateur", T0).premiere);
  const dj = M.donjonDe(CD, "ordinateur");
  let tt = T0, bugs = 0, sansBug = () => 0.99;
  dj.ateliers.forEach((a, i) => {
    assert.equal(M.atelierCourant(CD, PD, "ordinateur").id, a.id, "ateliers dans l'ordre");
    const ep = M.epreuveAtelier(CD, PD, "ordinateur", () => 0);
    assert.ok(ep.ok && ep.atelier.id === a.id);
    assert.equal(M.finirAtelier(CD, PD, "ordinateur", [], tt).raison, "manipulation", "pas de questions avant la manipulation");
    assert.ok(!M.verifierEpreuve(CD, PD, "ordinateur", ep.n, "faux", tt).juste);
    // La réponse attendue, même tapée en texte, passe.
    const att = ep.instance.attendu, rep = Array.isArray(att) ? att.map(String) : String(att);
    assert.ok(M.verifierEpreuve(CD, PD, "ordinateur", ep.n, rep, tt).juste, a.id + " : réponse attendue acceptée");
    const qa = M.questionsAtelier(CD, PD, "ordinateur");
    let fin;
    if (qa.mode === "quiz") {
      assert.ok(qa.competence.startsWith("inf."), "quiz ordinaire sur la compétence nouvelle");
      M.terminerQuiz(CD, PD, qa.competence, M.tirerQuestions(CD, PD, qa.competence, 5).map((q) => ({ id: q.id, correct: true })), tt);
      fin = M.finirAtelier(CD, PD, "ordinateur", null, tt, i === 2 ? () => 0 : sansBug);
    } else {
      assert.equal(qa.questions.length, dj.questions_atelier, "contrôle sur une compétence déjà maîtrisée");
      const rate = M.finirAtelier(CD, PD, "ordinateur", qa.questions.map((q) => ({ id: q.id, correct: false })), tt);
      assert.ok(rate.ok && !rate.reussi, "contrôle raté : rien n'est posé");
      assert.equal(M.finirAtelier(CD, PD, "ordinateur", [], tt).raison, "manipulation", "raté : on refait la manipulation");
      M.verifierEpreuve(CD, PD, "ordinateur", ep.n, att, tt);
      fin = M.finirAtelier(CD, PD, "ordinateur", qa.questions.map((q) => ({ id: q.id, correct: true })), tt, sansBug);
    }
    assert.ok(fin.reussi && fin.poses.length === a.composants.length, a.id + " : pièces posées");
    if (fin.bug) {
      bugs++;
      assert.equal(M.epreuveAtelier(CD, PD, "ordinateur").raison, "bug", "le bug passe avant l'atelier suivant");
      const q1 = M.questionBug(CD, PD, "ordinateur", () => 0);
      assert.ok(q1 && M.questionBug(CD, PD, "ordinateur") === q1, "même question jusqu'à la réponse");
      assert.ok(!M.chasserBug(CD, PD, "ordinateur", false, tt).chasse);
      assert.ok(M.chasserBug(CD, PD, "ordinateur", true, tt).chasse);
    }
    tt += 60000;
  });
  assert.equal(bugs, 1, "un bug tiré, un bug chassé"); assert.equal(PD.donjons.ordinateur.bugsChasses, 1);
  assert.ok(!M.atelierCourant(CD, PD, "ordinateur"), "toutes les pièces posées");
  // Un rappel raté sur le binaire : la pièce tombe en panne, l'ordinateur ne s'allume pas.
  Object.assign(PD.competences["inf.binaire"], { maitrise: false, perdue: true });
  const panne = M.allumer(CD, PD, "ordinateur", tt);
  assert.equal(panne.raison, "panne"); assert.deepEqual(panne.pannes.map((p) => p.piece.id), ["binaire", "ual"], "le binaire perdu met en panne le code et l'UAL");
  PD.competences["inf.binaire"].maitrise = true;
  assert.ok(M.bilanDonjon(CD, PD, "ordinateur").pret, "réparée au rappel réussi");
  assert.ok(M.allumer(CD, PD, "ordinateur", tt).ok); assert.equal(M.allumer(CD, PD, "ordinateur", tt).raison, "deja");
  for (let i = 0; i < 40 && !PD.succes["ordinateur-allume"]; i++) M.verifierRecompenses(CD, PD, tt + i);
  ["premiere-piece", "ordinateur-allume"].forEach((id) => assert.ok(PD.succes[id], "succès " + id));
  assert.ok(!PD.succes["chasseur-de-bugs"], "trois bugs pour le chasseur");
  // La partie se sauvegarde et se relit avec son donjon.
  const relue = M.migrer(JSON.parse(JSON.stringify(PD)), CD);
  assert.ok(relue.donjons.ordinateur.allume && M.migrer({ format: 1 }, CD).donjons, "migration");
  assert.ok(M.repliqueDonjon(CD, "ordinateur", "allumage").fr);
  console.log("OK : donjon de l'ordinateur, 14 ateliers, bug, panne, allumage");
}

// Le Procès (Victor, 2026-11-02) : ouvert par l'Éloquence réussie (ou choisi), huit salles notées, verdict, appel.
{
  const T0 = new Date(2026, 10, 2, 9, 0).getTime();
  const CP = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
    { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), donjons: d("donjons.json") });
  const PP = M.nouvellePartie(T0);
  assert.ok(!M.procesOuvert(CP, PP, "roscius"));
  CP.parStat.eloquence.forEach((k) => { PP.competences[k.id] = { maitrise: true, maitriseDepuis: T0 }; });
  assert.ok(M.procesOuvert(CP, PP, "roscius"), "ouvert par l'Éloquence réussie");
  assert.ok(M.entreesDonjons(CP, PP).some((e) => e.sorte === "proces" && e.id === "roscius"));
  assert.ok(M.entrerProces(CP, PP, "roscius", T0).premiere);
  const pr = M.procesDe(CP, "roscius");
  // Les meilleurs choix de chaque salle.
  const meilleur = (opts) => opts.reduce((b, o, i) => (o.points > opts[b].points ? i : b), 0);
  const parfait = (s) => s.type === "choix" ? meilleur(s.options)
    : s.type === "multi" ? s.options.map((o, i) => [o.points, i]).sort((a, b) => b[0] - a[0]).slice(0, s.choisir).map((x) => x[1])
    : s.type === "ordre" ? s.items.map((_, i) => i) : s.echanges.map((e) => meilleur(M.optionsEchange(pr, e)));
  const pire = (s) => s.type === "choix" ? s.options.findIndex((o) => !o.points)
    : s.type === "multi" ? s.options.map((o, i) => [o.points, i]).sort((a, b) => a[0] - b[0]).slice(0, s.choisir).map((x) => x[1])
    : s.type === "ordre" ? ((it) => it.map((_, i) => it.length - 1 - i))(M.itemsSalle(pr, s, PP.proces.roscius.choix)) : s.echanges.map((e) => M.optionsEchange(pr, e).findIndex((o) => !o.points));
  assert.equal(M.repondreSalle(CP, PP, "roscius", [0, 0, 1], T0).raison, "reponse", "le dossier refuse un fait choisi deux fois");
  assert.equal(M.verdictProces(CP, PP, "roscius", T0).raison, "salles", "pas de verdict avant la dernière salle");
  pr.salles.forEach((s) => { const r = M.repondreSalle(CP, PP, "roscius", pire(s), T0); assert.ok(r.ok && r.lecon, s.id); });
  const perdu = M.verdictProces(CP, PP, "roscius", T0 + 1);
  assert.ok(perdu.ok && !perdu.acquitte && perdu.vrai.source, "mauvaise plaidoirie : condamnée");
  assert.ok(perdu.votes.length === pr.jury.length && perdu.votes.filter((v) => v.acquitte).length < 4, "condamnée : pas de majorité pour acquitter");
  assert.equal(M.salleProces(CP, PP, "roscius").id, pr.salles[0].id, "l'appel repart de la première salle");
  pr.salles.forEach((s) => { const r = M.repondreSalle(CP, PP, "roscius", parfait(s), T0 + 2); assert.equal(r.points, r.max, s.id + " : le meilleur choix vaut le maximum"); });
  const gagne = M.verdictProces(CP, PP, "roscius", T0 + 3);
  assert.ok(gagne.acquitte && gagne.total === gagne.max, "plaidoirie parfaite : acquittée");
  assert.ok(gagne.votes.every((v) => v.acquitte), "plaidoirie parfaite : le jury unanime");
  // Procès v2 : la clôture de l'audience reprend la péroraison et la dernière phrase, avec leurs points d'audience.
  const aud = pr.salles.find((s) => s.type === "audience"), clo = aud.echanges.filter((e) => e.reprend);
  assert.ok(clo.length === 2 && clo.every((e) => M.optionsEchange(pr, e).length >= 2 && e.adversaire), "péroraisons de l'adversaire puis la tienne");
  { const sp = pr.salles.find((s) => s.selon); assert.equal(M.itemsSalle(pr, sp, { [sp.selon]: 3 }).length, sp.variantes[3].length, "les parties suivent le type de plan"); }
  pr.salles.forEach((s) => { if (s.type === "choix" || s.type === "multi") assert.ok(s.options.every((o) => o.plus && o.moins), s.id + " : avantages et inconvénients de chaque choix"); });
  // Un verdict juste au seuil : 4 voix au moins pour acquitter.
  { const pts = {}; let tot = 0; const sc = M.scoreProces(CP, PP, "roscius");
    pr.salles.forEach((s) => { const m = M.maxSalle(s, pr); const p = Math.min(m, Math.max(0, sc.seuil - tot)); pts[s.id] = p; tot += p; });
    assert.ok(M.votesJury(pr, pts, true).filter((v) => v.acquitte).length >= 4, "acquittée au seuil : majorité");
    assert.ok(M.votesJury(pr, pts, false).filter((v) => v.acquitte).length <= 3, "condamnée : minorité"); }
  for (let i = 0; i < 40 && !(PP.succes["acquittement"] && PP.succes["en-appel"]); i++) M.verifierRecompenses(CP, PP, T0 + 10 + i);
  assert.ok(PP.succes["acquittement"] && PP.succes["en-appel"], "succès du Procès");
  assert.ok(M.migrer(JSON.parse(JSON.stringify(PP)), CP).proces.roscius.acquitte, "migration");
  { const IX = { packs: [{ id: "socle", sorte: "socle" }, { id: "a", requiert: ["socle"] }, { id: "b", requiert: ["socle", "a"], reglages: { allume: false } }, { id: "dj", sorte: "jeu", requiert: ["socle", "b"] }] };
    const dem = M.allumerPack(IX, ["a", "dj", "x"], "dj"), off = M.packsEteints(IX, dem);
    assert.ok(!off.dj && !off.b && !off.a && dem.includes("x") && dem.includes("+b"), "cocher un donjon allume les domaines qu'il demande"); }
  console.log("OK : le Procès, dix salles, jury, verdict, appel");
}

// Victor (2026-11-03) : création du personnage et pouvoirs débloqués par les succès et les niveaux.
{
  const CA = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
    { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json") });
  const cr = CA.avatar.creation, T0 = new Date(2026, 10, 3, 9, 0).getTime();
  const PA = M.nouvellePartie(T0);
  assert.equal(M.apparence(CA, PA), null, "sans création, l'avatar d'avant");
  for (const e of cr.especes) {
    assert.equal(e.corps.length, 48, e.id); assert.ok(e.corps.every((l) => l.length === 40), e.id);
    assert.ok(e.teintes.length >= 1, e.id);
  }
  for (const g of ["regards", "coiffures", "barbes", "tenues"]) for (const x of cr[g]) assert.equal(x.pixels.length, 48, g + " " + x.id);
  PA.succes.insomniaque = T0;
  assert.ok(M.choisirApparence(CA, PA, { espece: "chat", teinte: "tigre", regard: "louche", coiffure: "crete", cheveux: "rose", barbe: "guidon", tenue: "pyjama", couleur: "fluo" }));
  let ap = M.apparence(CA, PA);
  assert.equal(ap.espece.id, "chat"); assert.equal(ap.teinte.id, "tigre"); assert.equal(ap.regard.id, "louche"); assert.equal(ap.tenue.id, "pyjama");
  assert.equal(ap.couleurs.X, "#9BE22B"); assert.equal(ap.couleurs.Z, "#9BE22B", "pyjama assorti : le bas suit la couleur");
  M.choisirApparence(CA, PA, { espece: "robot", teinte: "inconnue", regard: "louche", tenue: "inconnue" });
  ap = M.apparence(CA, PA);
  assert.equal(ap.teinte.id, "chrome"); assert.equal(ap.regard, null, "le robot a ses propres yeux"); assert.equal(PA.apparence.tenue, ap.tenue ? ap.tenue.id : "blazer");
  M.choisirApparence(CA, PA, { espece: "humain", tenue: "rang" });
  assert.equal(M.apparence(CA, PA).tenue, null, "tenue du rang");
  assert.ok(M.migrer(JSON.parse(JSON.stringify(PA)), CA).apparence.espece === "humain");

  // Pouvoirs : verrouillés au départ, débloqués par succès + niveau, rechargés chaque jour ou chaque semaine.
  assert.ok(M.pouvoirs(CA, PA, T0).every((e) => !e.debloque));
  assert.equal(M.utiliserPouvoir(CA, PA, "rasoir", T0), false);
  PA.succes.eureka = T0; PA.succes.cloche = T0; PA.succes["dix-competences"] = T0;
  assert.equal(M.pouvoir(CA, PA, "rasoir", T0).debloque, false, "il faut aussi le niveau global 3");
  const ids = CA.competences.filter((k) => k.stat === "logique").map((k) => k.id);
  ids.forEach((id) => { PA.competences[id] = { maitrise: true, xp: 400, palier: 1, prochainRappel: T0 + 30 * jour }; });
  assert.ok(M.niveauGlobal(CA, PA) >= 10);
  const etat = Object.fromEntries(M.pouvoirs(CA, PA, T0).map((e) => [e.pouvoir.id, e]));
  assert.ok(etat.rasoir.debloque && etat.pascaline.debloque && etat.demon.debloque && etat.palais.debloque);
  const nr = etat.rasoir.max, nd = etat.demon.max; assert.ok(nr >= 1 && nd >= 1);
  assert.equal(M.annoncerPouvoirs(CA, PA, T0).length, 4); assert.equal(M.annoncerPouvoirs(CA, PA, T0).length, 0, "annoncés une seule fois");
  for (let i = 0; i < nr; i++) assert.ok(M.utiliserPouvoir(CA, PA, "rasoir", T0 + i)); assert.equal(M.utiliserPouvoir(CA, PA, "rasoir", T0 + 1000), false, "charges du jour épuisées");
  assert.ok(M.utiliserPouvoir(CA, PA, "rasoir", T0 + jour), "rechargé le lendemain");
  for (let i = 0; i < nd; i++) assert.ok(M.utiliserPouvoir(CA, PA, "demon", T0 + i)); assert.equal(M.utiliserPouvoir(CA, PA, "demon", T0 + jour), false, "charges de la semaine épuisées");
  assert.ok(M.utiliserPouvoir(CA, PA, "demon", T0 + 7 * jour), "rechargé la semaine suivante");
  // Le palais de mémoire sauve un rappel raté : la compétence reste, le rappel est dû tout de suite.
  const id = ids[0]; PA.competences[id].prochainRappel = T0 - jour;
  const qs = M.tirerQuestions(CA, PA, id, 3).map((q) => ({ id: q.id, correct: false }));
  const rr = M.terminerRappel(CA, PA, id, qs, T0, { total: 3, palais: true });
  assert.ok(rr.palais && rr.issue === "echec"); assert.ok(PA.competences[id].maitrise); assert.equal(PA.competences[id].prochainRappel, T0);
  while (M.utiliserPouvoir(CA, PA, "palais", T0)) {}
  const rr2 = M.terminerRappel(CA, PA, id, qs, T0 + 1, { total: 3, palais: true });
  assert.equal(rr2.issue, "perdue", "plus de charge cette semaine : la compétence est perdue");
  console.log("OK : création du personnage (15 espèces) et 4 pouvoirs (déblocage, recharge, palais de mémoire)");
}

// Victor (2026-11-03) : toge ou blouse d'écolier au départ, tenues gagnées par succès, humeur d'Alyca sur la garde-robe.
{
  const CH = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
    { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json") });
  const T0 = new Date(2026, 10, 3, 9, 0).getTime(), PH = M.nouvellePartie(T0), cr = CH.avatar.creation;
  assert.deepEqual(cr.tenues.filter((x) => x.depart).map((x) => x.id).sort(), ["ecolier", "toge"]);
  M.choisirApparence(CH, PH, { espece: "humain", tenue: "smoking" });
  assert.equal(PH.apparence.tenue, "ecolier", "tenue verrouillée refusée");
  assert.deepEqual(M.annoncerTenues(CH, PH, T0), []);
  PH.succes["deux-nobel"] = T0;
  assert.deepEqual(M.annoncerTenues(CH, PH, T0).map((x) => x.id), ["smoking"]); assert.deepEqual(M.annoncerTenues(CH, PH, T0), []);
  M.choisirApparence(CH, PH, { espece: "humain", tenue: "smoking" }); assert.equal(PH.apparence.tenue, "smoking");
  PH.avatar.visage = "monocle";
  const fav = (v) => { PH.faveur = { valeur: v, maj: T0 }; };
  fav(5); let h = M.humeurPerso(CH, PH, T0, () => 0.1);
  assert.equal(h.type, "confisque_tenue", "furieuse : la tenue gagnée d'abord"); assert.equal(h.cible.id, "smoking");
  assert.equal(M.humeurPerso(CH, PH, T0 + 1000, () => 0.9).type, "confisque_tenue", "décidé pour la journée et ce palier");
  fav(60); assert.equal(M.humeurPerso(CH, PH, T0 + 2000, () => 0.1), null, "contente : elle rend tout");
  assert.equal(M.humeurPersoActive(PH, T0 + 2000), null);
  fav(95); h = M.humeurPerso(CH, PH, T0 + 3000, () => 0.1); assert.equal(h.type, "retouche");
  M.choisirApparence(CH, PH, { espece: "humain", tenue: "toge" });
  fav(5); PH.humeurPerso = null; h = M.humeurPerso(CH, PH, T0 + 4000, () => 0.1);
  assert.equal(h.type, "confisque_accessoire", "toge de départ : elle prend l'accessoire"); assert.equal(h.cible.id, "monocle");
  assert.equal(M.humeurPersoActive(PH, T0 + jour), null, "le lendemain, tout revient");
  console.log("OK : tenues de départ, tenues gagnées, humeur d'Alyca sur la garde-robe");
}

// L'île (Victor, 2026-11-10) : son état se déduit des compétences. Une compétence maîtrisée pose son installation et
// attire des habitants ; un rappel dû la met en alerte, un rappel en retard en panne, une compétence perdue à l'abandon.
{
  const CI = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
    { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ile: d("ile.json") });
  assert.ok(M.ilePresente(CI)); assert.equal(M.ile(C, M.nouvellePartie(0), 0), null);
  let ti = new Date(2026, 10, 10, 9, 0).getTime();
  const PI = M.nouvellePartie(ti), H = CI.ile.regles.habitants;
  const bon = (id, n) => M.tirerQuestions(CI, PI, id, n).map(q => ({ id: q.id, correct: true }));
  // Les quartiers sont des lieux : la grue de la Mécanique se pose au port, et chaque compétence a un seul quartier.
  const quartier = () => M.ile(CI, PI, ti).quartiers.find(q => q.id === "port");
  const inst = id => quartier().installations.find(x => x.comp === id);
  assert.equal(M.ile(CI, PI, ti).quartiers.reduce((s, q) => s + q.installations.length, 0), CI.competences.length);
  assert.ok(new Set(M.ile(CI, PI, ti).quartiers.find(q => q.id === "ville").installations.map(x => x.stat)).size > 1, "un quartier reçoit plusieurs arbres");
  // Sans installation écrite, une compétence va dans le quartier de son arbre : l'électricité à la centrale.
  { const sans = JSON.parse(JSON.stringify(d("ile.json"))); sans.installations = sans.installations.filter(x => x.comp !== "elec.torpille");
    const CS = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"), { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ile: sans });
    assert.ok(M.ile(CS, PI, ti).quartiers.find(q => q.id === "centrale").installations.some(x => x.comp === "elec.torpille" && !x.propre)); }
  // Chaque compétence a son installation écrite (nom et usage), dans un quartier choisi pour elle.
  assert.ok(M.ile(CI, PI, ti).quartiers.every(q => q.installations.every(x => x.propre && x.usage)), "toutes les installations sont écrites");
  assert.equal(M.ile(CI, PI, ti).quartiers.filter(q => q.centre).length, 1);
  assert.equal(M.ile(CI, PI, ti).habitants, 0);
  assert.equal(inst("phys.machines").etat, "friche"); assert.ok(inst("phys.machines").usage && inst("phys.machines").dessin);
  // Un quiz raté ne change rien sur l'île ; réussi, l'installation se pose et ses habitants arrivent.
  let ri = M.terminerQuiz(CI, PI, "phys.machines", bon("phys.machines", 5).map(x => ({ id: x.id, correct: false })), ti);
  assert.equal(ri.ile, null);
  ri = M.terminerQuiz(CI, PI, "phys.machines", bon("phys.machines", 5), ti);
  assert.equal(ri.ile.avant, "friche"); assert.equal(ri.ile.apres, "marche");
  // L'île est vierge au départ : la première installation d'un quartier le fonde.
  assert.ok(M.ile(CI, M.nouvellePartie(ti), ti).quartiers.every(q => !q.fonde));
  assert.ok(ri.ile.fondation && quartier().fonde);
  // Le lieu porte le nom de son stade : rudimentaire à la fondation, son nom complet quand toutes ses options sont ouvertes.
  const stades = CI.ile.quartiers.find(q => q.id === "port").stades;
  assert.equal(stades.length, quartier().options.length + 1); assert.equal(quartier().nom, stades[0]); assert.notDeepEqual(quartier().nom, quartier().nomFinal); assert.equal(M.ile(CI, PI, ti).quartiers.filter(q => q.fonde).length, 1);
  assert.equal(inst("phys.machines").etat, "marche"); assert.equal(quartier().posees, 1);
  // Un quartier fondé est un chantier : personne n'y vit avant que son premier palier soit ouvert.
  assert.equal(ri.ile.habitants, 0); assert.ok(!quartier().habitable); assert.equal(quartier().manque, quartier().options[0].installations - 1);
  const voisines = quartier().installations.filter(x => x.comp !== "phys.machines").slice(0, quartier().options[0].installations);
  voisines.forEach(x => { PI.competences[x.comp] = { maitrise: true, prochainRappel: ti + 400 * 86400000, palier: 1, xp: 1 }; });
  assert.ok(quartier().habitable); assert.equal(inst("phys.machines").places, H.installation + H.par_rang);
  // Le rappel devient dû : alerte, les habitants restent ; trop de retard : panne, la moitié s'en va.
  const du = PI.competences["phys.machines"].prochainRappel;
  ti = du + 3600e3; assert.equal(inst("phys.machines").etat, "alerte"); assert.equal(inst("phys.machines").places, H.installation + H.par_rang);
  ti = du + CI.ile.regles.panne_jours * 86400000 + 3600e3; assert.equal(inst("phys.machines").etat, "panne");
  assert.equal(inst("phys.machines").places, Math.round((H.installation + H.par_rang) * H.panne));
  // Rappel réussi : réparée. Rappel raté : à l'abandon, plus personne.
  ri = M.terminerRappel(CI, PI, "phys.machines", bon("phys.machines", 3), ti);
  assert.equal(ri.ile.avant, "panne"); assert.equal(ri.ile.apres, "marche");
  ti = PI.competences["phys.machines"].prochainRappel + 3600e3;
  delete PI.population; assert.ok(M.ile(CI, PI, ti).habitants > 0, "une partie d'avant la démographie retrouve ses habitants");
  ri = M.terminerRappel(CI, PI, "phys.machines", bon("phys.machines", 3).map(x => ({ id: x.id, correct: false })), ti);
  assert.equal(ri.ile.apres, "abandon"); assert.equal(inst("phys.machines").places, 0); assert.equal(inst("phys.machines").etat, "abandon");
  assert.ok(ri.ile.habitants < ri.ile.habitantsAvant);
  quartier().installations.forEach(x => { delete PI.competences[x.comp]; });
  // Les options du quartier s'ouvrent par paliers d'installations en marche, chacune avec sa prime d'habitants ;
  // l'épreuve qui franchit le palier l'annonce. Une compétence sans installation écrite pose son emblème.
  assert.ok(quartier().options.length && quartier().options.every(o => !o.ouverte));
  const seuil = quartier().options[0].installations, aPoser = quartier().installations.slice(0, seuil);
  aPoser.slice(0, seuil - 1).forEach(x => { PI.competences[x.comp] = { maitrise: true, prochainRappel: ti + 86400000, palier: 1, xp: 1 }; });
  assert.ok(!quartier().options[0].ouverte);
  const dern = aPoser[seuil - 1], hAvant = M.ile(CI, PI, ti).places;
  PI.competences[dern.comp] = { maitrise: true, prochainRappel: ti + 86400000, palier: 1, xp: 1 };
  assert.ok(quartier().options[0].ouverte && !quartier().options[1].ouverte);
  assert.equal(hAvant, 0, "sous le palier, le quartier reste vide");
  assert.equal(M.ile(CI, PI, ti).places, aPoser.reduce((s, x) => s + H.installation + H.par_rang * x.rang, 0) + H.option, "au palier, toutes les places s'ouvrent");
  CI.competences.forEach(k => { PI.competences[k.id] = { maitrise: true, prochainRappel: ti + 86400000, palier: 1, xp: 1 }; });
  const tout = M.ile(CI, PI, ti); assert.equal(tout.places, tout.capacite);
  assert.ok(tout.quartiers.every(q => q.options.every(o => o.ouverte)), "tout maîtriser ouvre toutes les options");
  assert.ok(tout.quartiers.every(q => JSON.stringify(q.nom) === JSON.stringify(q.nomFinal)), "au dernier stade, le lieu porte son nom complet");
  const sans = tout.quartiers.flatMap(q => q.installations).find(x => !x.propre);
  if (sans) assert.ok(sans.nom && !sans.usage);
  // L'objectif du jour suit le plateau : le quartier visé est celui de l'épreuve que le jeu propose, et la réussir
  // tient l'objectif. Manqué, la plus belle installation du quartier passe en veille le lendemain, sans rien perdre.
  {
    const CP = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
      { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ile: d("ile.json"), plateau: d("plateau.json") });
    let tj = new Date(2026, 10, 12, 9, 0).getTime();
    const PJ = M.nouvellePartie(tj), bonJ = (id, n) => M.tirerQuestions(CP, PJ, id, n).map(q => ({ id: q.id, correct: true }));
    let ob = M.objectifIle(CP, PJ, tj), choix = M.choixIA(CP, PJ, tj);
    assert.equal(ob.type, "epreuve"); assert.ok(!ob.reussi);
    assert.equal(ob.prochain.comp, choix.comp.id, "l'objectif propose l'épreuve de la case, jamais une autre");
    const cible = ob.quartier;
    assert.ok(M.ile(CP, PJ, tj).quartiers.find(q => q.id === cible).installations.some(x => x.comp === choix.comp.id), "le quartier visé est celui de cette épreuve");
    assert.equal(M.objectifIle(CP, PJ, tj + 3600e3).quartier, cible, "le même quartier toute la journée");
    // Jour 1 manqué, avec une installation qui tourne déjà dans le quartier visé : elle passe en veille le lendemain.
    const deja = M.ile(CP, PJ, tj).quartiers.find(q => q.id === cible).installations.find(x => x.comp !== choix.comp.id);
    PJ.competences[deja.comp] = { maitrise: true, prochainRappel: tj + 30 * 86400000, palier: 1, xp: 1 };
    tj += 86400000; ob = M.objectifIle(CP, PJ, tj);
    assert.equal(ob.veille, deja.comp, "objectif manqué : une installation en veille");
    const vue = M.ile(CP, PJ, tj).quartiers.find(q => q.id === cible).installations.find(x => x.comp === deja.comp);
    assert.equal(vue.etat, "veille");
    assert.ok(M.estMaitrisee(PJ, deja.comp), "la veille ne fait rien perdre");
    // Une épreuve ratée ne tient pas l'objectif ; réussie, il est tenu : crédits, veille levée, annonce dans le bilan.
    const jeu = ob.prochain.comp;
    let rj = M.terminerQuiz(CP, PJ, jeu, bonJ(jeu, 5).map(x => ({ id: x.id, correct: false })), tj);
    assert.ok(!rj.ile && !M.objectifIle(CP, PJ, tj).reussi);
    const avantC = PJ.credits.gagnes; rj = M.terminerQuiz(CP, PJ, jeu, bonJ(jeu, 5), tj);
    assert.ok(rj.ile && rj.ile.objectif && rj.ile.objectif.reussi, "le bilan annonce l'objectif tenu");
    assert.ok(PJ.credits.gagnes - avantC >= CP.ile.regles.objectif.credits);
    assert.equal(M.objectifIle(CP, PJ, tj).veille, null);
    assert.equal(M.ile(CP, PJ, tj).quartiers.flatMap(q => q.installations).find(x => x.comp === deja.comp).etat, "marche");
    const g2 = PJ.credits.gagnes, nx = M.choixIA(CP, PJ, tj);
    if (nx && nx.type === "quiz") { const r3 = M.terminerQuiz(CP, PJ, nx.comp.id, bonJ(nx.comp.id, 5), tj); assert.ok(!r3.ile || !r3.ile.objectif, "la prime ne tombe qu'une fois par jour"); }
  }
  // Piège déclenché : une part des habitants fuit ; chaque épreuve réussie en ramène, jusqu'au retour de tous.
  { const PX = M.nouvellePartie(ti);
    CI.competences.forEach(k => { PX.competences[k.id] = { maitrise: true, prochainRappel: ti + 30 * 86400000, palier: 1, xp: 1 }; });
    const plein = M.ile(CI, PX, ti).habitants, RP = CI.ile.regles.piege;
    assert.equal(plein, M.ile(CI, PX, ti).places, "une île découverte toute bâtie est pleine");
    const ex = M.exodeIle(CI, PX, ti);
    assert.equal(ex.partis, Math.round(plein * RP.part)); assert.equal(PX.exil, ex.partis);
    const I1 = M.ile(CI, PX, ti);
    assert.equal(I1.exil, PX.exil); assert.equal(I1.habitants, plein - ex.partis, "les partis manquent sur l'île");
    assert.equal(I1.habitants, I1.population.enfants + I1.population.adultes + I1.population.anciens);
    const id = CI.competences[0].id, exilAvant = PX.exil;
    const rr = M.terminerRappel(CI, PX, id, M.tirerQuestions(CI, PX, id, 3).map(q => ({ id: q.id, correct: true })), ti);
    assert.equal(PX.exil, exilAvant - RP.retour); assert.equal(rr.ile.revenus, RP.retour); assert.equal(M.ile(CI, PX, ti).habitants, plein - ex.partis + RP.retour); }
  // Démographie (Victor, 2026-11-10) : Leslie, Verhulst, Lotka-Volterra, liés aux aménagements.
  // La famine mortelle et les aléas (2026-11-12) ont leur propre test, plus bas : ici, la démographie seule.
  const FAMINE = CI.ile.regles.ressources.famine_mort, ALEAS = CI.ile.regles.aleas.chance; CI.ile.regles.ressources.famine_mort = 0; CI.ile.regles.aleas.chance = 0;
  { const JOUR = 86400000, DM = CI.ile.regles.demographie;
    const bati = (f) => { const p = M.nouvellePartie(ti); CI.competences.filter(f || (() => true)).forEach(k => { p.competences[k.id] = { maitrise: true, prochainRappel: ti + 900 * JOUR, palier: 1, xp: 1 }; }); return p; };
    const vide = p => { p.population = { jour: "", t: ti, e: 0, a: 0, v: 0, p: 0, journal: null }; return p; };
    const quartierDe = {}; M.ile(CI, bati(), ti).quartiers.forEach(q => q.installations.forEach(x => { quartierDe[x.comp] = q.id; }));
    // Une île bâtie mais vide : les pionniers débarquent, puis la population grandit sans dépasser les places (Verhulst).
    const PD = vide(bati()); let Id = M.ile(CI, PD, ti + JOUR);
    assert.equal(Id.habitants, DM.pionniers); assert.equal(Id.population.journal.arrivees, DM.pionniers);
    let prec = Id.habitants, pic = 0;
    for (let j = 2; j <= 120; j++) { Id = M.ile(CI, PD, ti + j * JOUR); assert.ok(Id.habitants <= Id.places, "jamais plus d'habitants que de places"); pic = Math.max(pic, Id.habitants);
      assert.equal(Id.habitants, Id.population.enfants + Id.population.adultes + Id.population.anciens); if (j < 10) { assert.ok(Id.habitants > prec, "l'île se peuple"); prec = Id.habitants; } }
    assert.ok(Id.habitants > 0.8 * Id.places && Id.population.enfants > 0 && Id.population.anciens > 0, "bien équipée, l'île approche de sa capacité, avec ses trois âges");
    assert.ok(Id.population.journal.naissances > 0 && Id.population.journal.anciens > 0, "le journal du jour compte naissances et décès");
    // Le même jour, rien ne bouge ; la même histoire redonne la même île (aucun hasard à sauvegarder).
    const fige = JSON.stringify(PD.population); M.ile(CI, PD, ti + 120 * JOUR + 3600e3); assert.equal(JSON.stringify(PD.population), fige);
    const PD2 = vide(bati()); for (let j = 1; j <= 120; j++) M.ile(CI, PD2, ti + j * JOUR); assert.equal(JSON.stringify(PD2.population), fige);
    // Plus on ajoute d'aménagements, moins on meurt : sans la centrale, les anciens meurent davantage.
    const sansCentrale = M.ile(CI, vide(bati(k => quartierDe[k.id] !== "centrale")), ti + JOUR).population;
    assert.equal(sansCentrale.niveaux.anciens, 0); assert.ok(sansCentrale.mortalite.anciens > 3 * Id.population.mortalite.anciens);
    assert.ok(Object.values(Id.population.niveaux).every(n => n > 0.5 && n < 1));
    // Une longue absence n'est rattrapée que sur quelques jours.
    const PA = vide(bati()); assert.equal(M.ile(CI, PA, ti + 300 * JOUR).population.journal.jours, DM.rattrapage);
    // Lotka-Volterra : sans agora ni campus, les faux savoirs prolifèrent dès que l'île dépasse ce qu'elle sait protéger,
    // et la ramènent vers ce seuil ; un duel gagné les fait reculer.
    const PL = vide(bati(k => quartierDe[k.id] !== "agora" && quartierDe[k.id] !== "campus")); let Il, maxP = 0;
    for (let j = 1; j <= 200; j++) { Il = M.ile(CI, PL, ti + j * JOUR); maxP = Math.max(maxP, Il.population.parasites); }
    assert.equal(Il.population.niveaux.defense, 0); assert.ok(Il.places > 3 * Il.population.seuilParasites);
    assert.ok(maxP > 0 && Il.population.parasites > 0, "les faux savoirs s'installent"); assert.ok(Il.habitants / Il.places < Id.habitants / Id.places - 0.05, "ils retiennent la population sous ce qu'une île défendue atteint");
    const avantDuel = PL.population.p; assert.ok(M.chasserParasites(CI, PL) > 0 && PL.population.p < avantDuel);
    assert.ok(Id.population.parasites === 0 || Id.habitants <= Id.population.seuilParasites * 1.2, "défendue, l'île tient les faux savoirs à distance");
    // Des installations perdues : les places manquent, des habitants partent jour après jour.
    const PP = bati(); const pleine = M.ile(CI, PP, ti).habitants;
    CI.competences.filter(k => quartierDe[k.id] === "ville").forEach(k => { delete PP.competences[k.id]; });
    const Ip = M.ile(CI, PP, ti + JOUR); assert.ok(Ip.places < pleine && Ip.population.journal.departs > 0 && Ip.habitants < pleine && Ip.habitants > Ip.places, "le départ est progressif");
    // Une épreuve réussie qui ajoute des places en remplit une partie tout de suite.
    const PN = vide(bati(k => quartierDe[k.id] === "port" && k.id !== "phys.machines")); M.ile(CI, PN, ti);
    const rn = M.terminerQuiz(CI, PN, "phys.machines", M.tirerQuestions(CI, PN, "phys.machines", 5).map(q => ({ id: q.id, correct: true })), ti);
    assert.ok(rn.ile.attires > 0 && rn.ile.habitants === rn.ile.habitantsAvant + rn.ile.attires); }
  // Chantiers à matériaux et monuments (Victor, 2026-11-10) : contenu complet, avec atomes et plateau.
  { const CT = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
      { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ile: d("ile.json"), atomes: d("atomes.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ia: d("ia.json") });
    const PT = M.nouvellePartie(ti);
    CT.competences.forEach(k => { PT.competences[k.id] = { maitrise: true, prochainRappel: ti + 30 * 86400000, palier: 1, xp: 1 }; });
    const port = () => M.ile(CT, PT, ti).quartiers.find(q => q.id === "port");
    assert.ok(port().options[0].ouverte && !port().options[1].ouverte && port().options[1].pret, "sans son matériau, le chantier reste fermé");
    assert.ok(!port().options[2].ouverte, "les chantiers s'ouvrent dans l'ordre");
    const zs = d("ile.json").quartiers.flatMap(q => q.options.flatMap(o => (o.materiaux || []).map(m => m.z)));
    assert.ok(zs.every(z => CT.atomes.elements.some(e => e.z === z)), "chaque matériau est un élément du tableau");
    PT.atomes = {}; zs.forEach(z => { PT.atomes[z] = { capture: ti, rencontres: 1, fuites: 0 }; });
    assert.ok(M.ile(CT, PT, ti).quartiers.every(q => q.options.every(o => o.ouverte)), "tous les matériaux livrés, tout ouvre");
    // Monuments : trois choses d'une époque datées juste au Chrono, et le monument se dresse avec ses habitants.
    const I0 = M.ile(CT, PT, ti); assert.equal(I0.monuments.length, 6); assert.ok(I0.monuments.every(m => !m.bati));
    const anciens = CT.evenements.filter(e => e.annee != null && e.annee < 476).slice(0, 3);
    PT.siecles = { fiches: {} }; anciens.forEach(e => { PT.siecles.fiches["frise:" + e.id] = { niveau: 1, serie: 1, vus: 1, justes: 1 }; });
    const I1 = M.ile(CT, PT, ti), mo = I1.monuments.find(m => m.epoque === "antiquite");
    assert.ok(mo.bati && mo.dates.length === 3 && I1.monuments.filter(m => m.bati).length === 1);
    assert.equal(I1.places - I0.places, mo.habitants);
    assert.equal(I1.places + 5 * mo.habitants, I1.capacite, "il reste cinq monuments à bâtir"); }
  CI.ile.regles.ressources.famine_mort = FAMINE; CI.ile.regles.aleas.chance = ALEAS;
  console.log("île : quartiers par fonction, installations, alerte, panne, abandon, habitants, options, objectif du jour, démographie");
}

// Victor (2026-11-11) : monuments à la gloire des sciences, bâtis après trois jours joués d'affilée.
{
  const CG = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
    { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ile: d("ile.json") });
  const J = 86400000, t0 = new Date(2026, 10, 11, 9, 0).getTime(), PG = M.nouvellePartie(t0), R = CG.ile.regles.gloire;
  assert.equal(R.jours, 3);
  assert.equal(M.suivreGloire(CG, PG, "phys.machines", t0, "acquis", 5, 5), null, "un seul jour : rien");
  assert.equal(M.suivreGloire(CG, PG, "phys.machines", t0 + J, null), null);
  PG.competences["phys.machines"] = { maitrise: true, maitriseDepuis: t0, prochainRappel: t0 + 30 * J, palier: 1, xp: 10 };
  const avant = M.ile(CG, PG, t0 + 2 * J).capacite;
  const g1 = M.suivreGloire(CG, PG, "phys.machines", t0 + 2 * J, null);
  assert.ok(g1 && g1.type === "gloire" && g1.comp === "phys.machines" && g1.serie === 3 && g1.forme === "stele" && g1.actif);
  assert.equal(M.ile(CG, PG, t0 + 2 * J).capacite - avant, R.habitants, "le monument apporte ses places");
  assert.ok(M.ile(CG, PG, t0 + 2 * J).quartiers.find(q => q.id === g1.quartier).gloires.length === 1);
  // Trois jours de plus, et le dernier fait est un échec : une colonne brisée, relevée quand le savoir est regagné.
  assert.equal(M.suivreGloire(CG, PG, "phys.aristote", t0 + 3 * J, "perdue", 1, 3), null);
  assert.equal(M.suivreGloire(CG, PG, "phys.aristote", t0 + 4 * J, null), null);
  const g2 = M.suivreGloire(CG, PG, "phys.aristote", t0 + 5 * J, null);
  assert.ok(g2 && g2.type === "lecon" && g2.forme === "obelisque" && !g2.releve && !g2.actif && g2.serie === 6);
  PG.competences["phys.aristote"] = { maitrise: true, maitriseDepuis: t0 + 6 * J, prochainRappel: t0 + 30 * J, palier: 1, xp: 10 };
  assert.ok(M.gloiresIle(CG, PG).find(x => x.id === g2.id).releve, "colonne relevée");
  // Un jour sauté : la série repart de un.
  M.suivreGloire(CG, PG, "phys.archimede", t0 + 8 * J, "acquis", 5, 5);
  assert.equal(PG.gloire.serie, 1); assert.equal(M.gloiresIle(CG, PG).length, 2);
  // Victor (2026-11-11) : de vrais monuments du monde. Celui du savoir d'abord, sinon un autre du même arbre, jamais deux fois.
  CG.ile.gloires.forEach(g => assert.ok(CG.parId[g.comp] && g.histoire.fr.length > 80 && g.source, "monument réel complet : " + g.id));
  assert.ok(g1.reel && CG.parId[g1.reel.comp].stat === CG.parId["phys.machines"].stat, "à défaut, un monument du même arbre");
  assert.ok(g2.reel && g2.reel.id !== g1.reel.id, "pas deux fois le même monument");
  const PR = M.nouvellePartie(t0);
  M.suivreGloire(CG, PR, "sci.vaccins", t0, "acquis", 5, 5); M.suivreGloire(CG, PR, "sci.vaccins", t0 + J, null);
  const g3 = M.suivreGloire(CG, PR, "sci.vaccins", t0 + 2 * J, null);
  assert.equal(g3.reel.id, "mon-jenner", "le monument du savoir lui-même");
  console.log("OK : monuments à la gloire des sciences (série de jours, gloire, leçon relevée, vrais monuments)");
}

// Victor (2026-11-12) : ressources de l'île, aménagements bâtis avec les crédits, savants en visite.
{
  const CR = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
    { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ile: d("ile.json"), atomes: d("atomes.json") });
  const J = 86400000, t0 = new Date(2026, 10, 12, 9, 0).getTime();
  function partie() {
    const P = M.nouvellePartie(t0); P.credits.solde = 1000;
    CR.competences.filter(k => ["mecanique", "savoir", "logique", "cosmos"].includes(k.stat) && k.rang <= 4).forEach(k => { P.competences[k.id] = { maitrise: true, maitriseDepuis: t0, prochainRappel: t0 + 400 * J, palier: 1, xp: 5 }; });
    M.ile(CR, P, t0); return P;
  }
  const P = partie(), I0 = M.ile(CR, P, t0);
  assert.ok(I0.ressources && I0.ressources.stocks.nourriture > 0, "des réserves au départ");
  assert.equal(M.etatAmenagement(CR, P, "mine", t0).savoir, "chim.metaux", "la mine demande de savoir travailler les métaux");
  assert.ok(!M.etatAmenagement(CR, P, "carriere", t0).possible || P.ressources.stocks.bois >= 15);
  const avant = P.credits.solde, r = M.construireIle(CR, P, "ferme", t0);
  assert.ok(r.ok && P.credits.solde === avant - 40 && M.ile(CR, P, t0).ressources.batis.ferme === 1, "la ferme se paie en crédits");
  assert.equal(M.ile(CR, P, t0).ressources.total, 6, "six postes");
  P.ressources.stocks.bois = 100; P.ressources.stocks.pierre = 100;
  const pl = M.ile(CR, P, t0).places; M.construireIle(CR, P, "maisons", t0);
  assert.equal(M.ile(CR, P, t0).places - pl, 25, "les maisons ajoutent leurs places");
  // Sans nourriture, l'île ne grandit pas comme une île nourrie.
  const affame = partie(), nourri = partie();
  for (let i = 0; i < 6; i++) M.construireIle(CR, nourri, "ferme", t0);
  affame.ressources.stocks.nourriture = 0; nourri.ressources.stocks.nourriture = 0;
  for (let j = 1; j <= 40; j++) { M.ile(CR, affame, t0 + j * J); M.ile(CR, nourri, t0 + j * J); }
  assert.ok(M.ile(CR, nourri, t0 + 40 * J).habitants > M.ile(CR, affame, t0 + 40 * J).habitants, "la famine freine la population");
  assert.ok(affame.ressources.journal.famine > 0 && nourri.ressources.stocks.nourriture > 0);
  // Les visiteurs : une réponse par jour, des crédits si elle est juste.
  const c0 = P.credits.solde, v1 = M.repondreVisiteur(CR, P, "archimede", true, t0);
  assert.equal(v1.credits, CR.ile.regles.visiteurs.credits); assert.equal(P.credits.solde, c0 + v1.credits);
  assert.ok(M.repondreVisiteur(CR, P, "archimede", true, t0).deja, "une seule question par jour");
  assert.equal(M.repondreVisiteur(CR, P, "archimede", false, t0 + J).credits, 0, "le lendemain, une autre ; ratée, rien");
  console.log("OK : ressources de l'île (aménagements, maisons, famine) et savants en visite");
}

// Victor (2026-11-12, « Deux modes au choix ») : en mode Île, le pion ne bouge plus ; l'île propose duels, atomes, Chrono.
{
  const CM = M.indexerContenu(d("regles.json"), d("skills.json"), d("questions.json"), d("succes.json"),
    { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ennemis: d("ennemis.json"), atomes: d("atomes.json"), ile: d("ile.json") });
  const tm = new Date(2026, 10, 12, 9, 0).getTime(), PM = M.nouvellePartie(tm); PM.mode = "ile";
  const rs = (id, n, ok) => M.tirerQuestions(CM, PM, id, n).map((q, i) => ({ id: q.id, correct: i < ok }));
  const pos = PM.plateau.position, rq = M.terminerQuiz(CM, PM, "math.origines", rs("math.origines", 5, 5), tm, { jouer: true });
  assert.equal(rq.plateau, null, "pas de plateau en mode Île");
  assert.equal(PM.plateau.position, pos, "le pion ne bouge pas");
  assert.ok(rq.ile && rq.ile.installation, "l'épreuve bâtit sur l'île");
  assert.equal(M.enRayon(CM, PM, "avance", tm).length, 0, "rien à acheter pour le pion");
  assert.ok(M.defiIle(CM, PM, tm) && PM.duel.pret, "un faux savoir à défier");
  assert.equal(M.defiIle(CM, PM, tm), null, "un défi à la fois, un par jour");
  PM.duel = null; assert.equal(M.defiIle(CM, PM, tm), null);
  const s = M.chercherMateriau(CM, PM, 14, tm); assert.ok(s && s.z === 14 && s.reste === 0, "le matériau se cherche en combat d'atome");
  PM.mode = "parcours"; assert.equal(M.chercherMateriau(CM, PM, 6, tm), null, "pas en mode Parcours");
  console.log("OK : mode Île (pion immobile, défis, matériaux)");
}

// Victor (2026-11-12) : l'île par âges. Le feu d'abord, puis les besoins du village ; un monde fini (forêt, poissons),
// l'effondrement possible, et des aléas que les savoirs météo annoncent.
{
  const CA = M.indexerContenu(dBrut("regles.json"), dBrut("skills.json"), dBrut("questions.json"), d("succes.json"),
    { commentaires: d("commentaires.json"), objets: d("objets.json"), avatar: d("avatar.json"), ia: d("ia.json"), plateau: d("plateau.json"), frise: d("frise.json"), bibliotheque: d("bibliotheque.json"), ile: d("ile.json") });
  const J = 86400000, t0 = new Date(2026, 10, 12, 9, 0).getTime();
  const sait = (P, id, t) => { P.competences[id] = { maitrise: true, maitriseDepuis: t || t0, prochainRappel: (t || t0) + 400 * J, palier: 1, xp: 5 }; if (id === "ile.feu") P.epreuves = { feu: t || t0, hache: t || t0 }; };
  const P = M.nouvellePartie(t0); P.mode = "ile"; P.credits.solde = 2000;
  // Le campement : seul le feu est proposé.
  let G = M.agesIle(CA, P);
  assert.equal(G.age.id, "survivants"); assert.equal(G.age.besoins[0].savoirs[0], "ile.feu");
  assert.equal(M.statut(CA, P, "ile.feu", t0).etat, "disponible", "le feu est le premier savoir");
  assert.equal(M.statut(CA, P, "math.origines", t0).etat, "verrouillee", "rien d'autre avant le feu");
  assert.deepEqual(M.disponibles(CA, P, t0).map(k => k.id), ["ile.feu"]);
  assert.equal(M.choixIA(CA, P, t0).comp.id, "ile.feu", "l'île propose le feu");
  for (const k of CA.competences.filter(k => ["ile.feu", "res.cueillir", "res.cultiver", "meteo.ciel"].includes(k.id)))
    assert.ok(CA.questions.filter(q => q.competence === k.id).length >= 10, k.id + " a ses questions");
  const rf = M.terminerQuiz(CA, P, "ile.feu", M.tirerQuestions(CA, P, "ile.feu", 5).map(q => ({ id: q.id, correct: true })), t0, { jouer: true });
  assert.equal(rf.issue, "maitrisee");
  // Le campement (Victor, 2026-11-12 : une transition plus douce) : six besoins, rien de durable à bâtir.
  // Victor (2026-11-13) : le feu appris, il reste à le faire. L'épreuve unique garde la porte du campement.
  G = M.agesIle(CA, P);
  assert.equal(G.age.id, "survivants"); assert.equal(G.age.epreuve, "feu"); assert.equal(G.age.pret, false);
  assert.equal(M.passerAge(CA, P, t0), null, "pas de passage sans l'épreuve");
  assert.equal(M.choixIA(CA, P, t0), null, "rien d'autre à jouer que l'épreuve");
  const ef = M.epreuveIle(CA, "feu");
  assert.deepEqual(ef.etapes.map(e => e.type), ["frappes", "jauge", "equation"]);
  { // L'équation des données est équilibrée, et chaque pas mène au bon coefficient.
    const e = ef.etapes[2], coef = e.depart.slice(); e.pas.forEach(x => { assert.ok(x.choix.includes(x.bon)); coef[x.cible] = x.bon; });
    const compte = c => { const o = {}; e.molecules.forEach((m, j) => { if (m.cote === c) for (const a in m.atomes) o[a] = (o[a] || 0) + coef[j] * m.atomes[a]; }); return o; };
    assert.deepEqual(compte("g"), compte("d")); e.molecules.forEach(m => { const o = {}; m.dessin.forEach(a => { o[a] = (o[a] || 0) + 1; }); assert.deepEqual(o, m.atomes, m.formule + " : le dessin compte les mêmes atomes"); }); assert.deepEqual(compte("g"), { Fe: 4, S: 8, O: 22 });
  }
  { // La quête : quatre objets à ramasser sur la carte, une fois chacun.
    let qu = M.queteIle(CA, P, "feu"); assert.deepEqual(qu.objets.map(o => o.id), ["silex", "pyrite", "amadou", "branchages"]); assert.equal(qu.reste, 4);
    assert.equal(M.ramasserIle(CA, P, "feu", "silex", t0).quete.reste, 3); assert.equal(M.ramasserIle(CA, P, "feu", "silex", t0), null); assert.equal(M.ramasserIle(CA, P, "feu", "caillou", t0), null);
    ["pyrite", "amadou", "branchages"].forEach(o => M.ramasserIle(CA, P, "feu", o, t0)); assert.ok(M.queteIle(CA, P, "feu").complete);
    qu.objets.forEach(o => { const dx = (o.position[0] - 0.5) / 0.43, dy = (o.position[1] - 0.51) / 0.44; assert.ok(dx * dx + dy * dy < 0.8, o.id + " est sur la terre ferme"); });
  }
  assert.equal(M.epreuveFaite(P, "feu"), false);
  assert.equal(M.reussirEpreuve(CA, P, "feu", t0).premiere, true); assert.equal(M.reussirEpreuve(CA, P, "feu", t0 + 5).premiere, false);
  assert.equal(P.epreuves.feu, t0); assert.equal(M.reussirEpreuve(CA, P, "inconnue", t0), null);
  { // Une partie déjà au campement ne doit pas l'épreuve.
    const P2 = JSON.parse(JSON.stringify(P)); delete P2.epreuves; P2.ageIle = 1;
    assert.equal(M.agesIle(CA, P2).age.id, "campement"); assert.equal(M.agesIle(CA, P2).ages[0].epreuve, null);
  }
  G = M.agesIle(CA, P);
  assert.equal(G.age.id, "campement"); assert.equal(G.age.besoins.length, 6);
  assert.equal(M.statut(CA, P, "astro.nebra", t0).etat, "disponible");
  assert.equal(M.statut(CA, P, "math.origines", t0).etat, "verrouillee", "compter attend le village");
  assert.equal(M.choixIA(CA, P, t0).besoin, "ciel");
  M.ile(CA, P, t0); sait(P, "astro.nebra");
  assert.equal(M.etatAmenagement(CA, P, "ferme", t0).age, 2, "pas de ferme au campement, même avec son savoir");
  assert.ok(!M.etatAmenagement(CA, P, "ferme", t0).possible);
  assert.equal(M.etatAmenagement(CA, P, "hutte", t0).age, null);
  ["sci.soigner", "res.cueillir", "meteo.ciel", "mnemo.sansecrire", "mus.instruments"].forEach(id => sait(P, id));
  M.ile(CA, P, t0);
  // Le village : les savoirs de ses besoins s'ouvrent, pas le rang 2, ni un rang 1 sans besoin.
  G = M.agesIle(CA, P);
  assert.equal(G.age.id, "village"); assert.equal(G.age.besoins.length, 6);
  assert.equal(M.statut(CA, P, "math.origines", t0).etat, "disponible");
  assert.equal(M.statut(CA, P, "math.babylone", t0).etat, "verrouillee", "le rang 2 attend la cité");
  assert.equal(M.statut(CA, P, "inf.pascaline", t0).etat, "verrouillee", "un savoir sans besoin attend son âge");
  const ch = M.choixIA(CA, P, t0); assert.equal(ch.raison, "besoin"); assert.equal(ch.besoin, "nourrir", "se nourrir demande les premières récoltes"); assert.equal(ch.comp.id, "res.cultiver");
  assert.equal(M.etatAmenagement(CA, P, "ferme", t0).savoir, "res.cultiver", "pas de ferme sans les premières récoltes");
  // Victor (2026-11-12) : ni le ciel des premiers peuples ni les poissons électriques ne nourrissent le village.
  assert.equal(M.statut(CA, P, "elec.torpille", t0).etat, "verrouillee", "les poissons électriques attendent leur âge");
  // Un aménagement demande son savoir : pas de rangée de maisons sans les machines simples.
  M.ile(CA, P, t0);
  assert.equal(M.etatAmenagement(CA, P, "maisons", t0).savoir, "phys.machines");
  assert.ok(M.construireIle(CA, P, "foyer", t0).ok, "le feu permet le foyer");
  sait(P, "res.cultiver"); sait(P, "phys.machines");
  assert.equal(M.etatAmenagement(CA, P, "ferme", t0).savoir, null);
  G = M.agesIle(CA, P); assert.ok(G.age.besoins.filter(b => b.id === "nourrir")[0].couvert); assert.equal(G.age.couverts, 2);
  assert.equal(M.etatAmenagement(CA, P, "ferme", t0).age, null, "au village, la ferme se bâtit");
  assert.deepEqual(G.age.besoins.filter(b => b.id === "batir")[0].amenagements, ["bucheron", "carriere", "maisons"]);
  // Victor (2026-11-12) : Transmettre et Décider ensemble sont optionnels. On les propose avant de passer ; négligés,
  // ils coûtent des savoirs oubliés et des émeutes.
  {
    const P2 = JSON.parse(JSON.stringify(P)); ["math.origines", "chim.feu"].forEach(id => sait(P2, id));
    let g = M.agesIle(CA, P2); assert.equal(g.age.id, "village"); assert.equal(g.age.requis, 4); assert.equal(g.age.couverts, 4);
    assert.ok(g.age.pret, "les besoins requis sont couverts : le passage attend la décision"); assert.deepEqual(g.age.negliges.map(b => b.id), ["transmettre", "decider"]);
    M.ile(CA, P2, t0); for (let d = 1; d <= 20; d++) assert.equal(M.ile(CA, P2, t0 + d * J).troubles.length, 0, "au village, pas encore de troubles");
    assert.equal(M.passerAge(CA, P2, t0 + 20 * J).age.id, "cite"); assert.equal(M.passerAge(CA, P2, t0 + 20 * J), null);
    let oublis = 0, emeutes = 0, morts = 0;
    for (let d = 21; d <= 80; d++) M.ile(CA, P2, t0 + d * J).troubles.forEach(f => { if (f.type === "oubli") { oublis++; assert.ok(P2.competences[f.comp].prochainRappel <= t0 + d * J, "le rappel du savoir oublié est dû"); } else { emeutes++; morts += f.morts; } });
    assert.ok(oublis > 0, "des savoirs s'oublient"); assert.ok(emeutes > 0 && morts > 0, "des émeutes tuent");
    const P3 = JSON.parse(JSON.stringify(P2)); ["rhet.origines", "coll.ruche"].forEach(id => sait(P3, id, t0 + 80 * J));
    M.ile(CA, P3, t0 + 80 * J); for (let d = 81; d <= 110; d++) assert.equal(M.ile(CA, P3, t0 + d * J).troubles.length, 0, "besoins couverts : plus de troubles");
  }
  // Tous les besoins couverts : la cité s'ouvre (et reste ouverte si un savoir se perd).
  ["math.origines", "chim.feu", "rhet.origines", "coll.ruche"].forEach(id => sait(P, id));
  G = M.ile(CA, P, t0).ages; assert.equal(G.age.id, "cite"); assert.equal(P.ageIle, 3);
  delete P.competences["coll.ruche"]; assert.equal(M.agesIle(CA, P).age.id, "cite", "un âge atteint le reste");
  assert.ok(!M.agesIle(CA, P).ages[2].complet, "mais le besoin est à rétablir");
  sait(P, "coll.ruche");
  // Victor (2026-11-12) : à partir du village, un nouveau quartier s'ouvre par une question ou des crédits.
  {
    const Iq = M.ile(CA, P, t0), feu = Iq.quartiers.find(q => q.installations.some(x => x.comp === "ile.feu"));
    assert.ok(feu.fonde && !feu.aOuvrir, "le quartier du feu est là depuis le campement");
    const ferme = Iq.quartiers.find(q => q.aOuvrir); assert.ok(ferme && !ferme.fonde && ferme.habitants === 0, "un quartier attend d'être ouvert, sans habitants");
    // Victor (2026-11-13) : avant le verrou, un explorateur repère le site, à l'emplacement qu'on choisit.
    assert.ok(ferme.aExplorer && M.ouvrirQuartier(CA, P, ferme.id, "credits", null, t0).refus === "site", "pas d'ouverture sans repérage");
    assert.equal(M.repererSite(CA, P, ferme.id, feu.position, t0).refus, "proche", "pas sur un autre quartier");
    assert.equal(M.repererSite(CA, P, ferme.id, [0.99, 0.5], t0).refus, "hors");
    const libre = [[0.5, 0.2], [0.3, 0.4], [0.3, 0.75], [0.7, 0.8]].find(c => !M.siteRefuse(CA, P, ferme.id, c, t0));
    assert.ok(M.repererSite(CA, P, ferme.id, libre, t0).ok); assert.deepEqual(M.ile(CA, P, t0).quartiers.find(q => q.id === ferme.id).position, libre, "le quartier se pose où on l'a choisi");
    assert.ok(!M.ile(CA, P, t0).quartiers.find(q => q.id === ferme.id).aExplorer);
    CA.ile.quartiers.forEach(q => { if (q.id !== ferme.id) { P.sites[q.id] = { t: t0, position: q.position }; } });
    const eq = M.questionQuartier(CA, P, ferme.id, t0); assert.ok(eq.question && eq.credits === 60 && eq.payable);
    assert.equal(M.ouvrirQuartier(CA, P, ferme.id, "question", false, t0).juste, false);
    const e2 = M.questionQuartier(CA, P, ferme.id, t0 + J); assert.ok(!e2.question && e2.credits === 60, "ratée : pas de seconde question, prix entier");
    assert.equal(M.ouvrirQuartier(CA, P, ferme.id, "question", true, t0).refus, "deja");
    let solde = P.credits.solde; assert.ok(M.ouvrirQuartier(CA, P, ferme.id, "credits", null, t0).ouvert); assert.equal(P.credits.solde, solde - 60);
    assert.ok(M.ile(CA, P, t0).quartiers.find(q => q.id === ferme.id).fonde, "payé : le quartier est fondé");
    // Une bonne réponse divise le prix par deux.
    M.ile(CA, P, t0).quartiers.filter(q => q.aOuvrir).forEach(q => {
      assert.equal(M.ouvrirQuartier(CA, P, q.id, "question", true, t0).credits, 30);
      solde = P.credits.solde; assert.ok(M.ouvrirQuartier(CA, P, q.id, "credits", null, t0).ouvert); assert.equal(P.credits.solde, solde - 30); });
    P.credits.solde = 0; delete P.quartiers[ferme.id]; assert.equal(M.ouvrirQuartier(CA, P, ferme.id, "credits", null, t0).refus, "credits"); P.quartiers[ferme.id] = t0; P.credits.solde = 2000;
    assert.ok(!M.ile(CA, P, t0).quartiers.some(q => q.aOuvrir));
  }
  // Victor (2026-11-12) : trois freins à la population, le plus bas l'emporte (savoirs, toits, plafond de l'âge).
  {
    const Ql = M.nouvellePartie(t0); Ql.mode = "ile"; sait(Ql, "ile.feu"); Ql.epreuves = { feu: t0 }; Ql.credits.solde = 1000;
    let Il = M.ile(CA, Ql, t0); assert.ok(Il.limites && Il.limites.toits === 15 && Il.limites.plafond === 40, "campement : 15 dormeurs sans toit, 40 au plus");
    assert.equal(Il.places, Math.min(Il.limites.savoirs, 15)); 
    Ql.ressources.stocks.bois = 100; for (let i = 0; i < 4; i++) assert.ok(M.construireIle(CA, Ql, "foyer", t0).ok);
    Il = M.ile(CA, Ql, t0); assert.equal(Il.limites.toits, 55); assert.ok(Il.places <= 40, "le campement plafonne à 40");
    CA.competences.filter(k => k.rang === 1).forEach(k => sait(Ql, k.id));
    Il = M.ile(CA, Ql, t0); assert.equal(Il.limites.plafond, 400, "la cité plafonne à 400"); assert.equal(Il.limites.frein, "toits"); assert.equal(Il.places, 55, "sans maisons, les savoirs n'attirent personne de plus");
  }
  // La cueillette est risquée : un campement qui ne vit que d'elle y perd des adultes, jour après jour.
  { const Qc = M.nouvellePartie(t0); Qc.mode = "ile"; sait(Qc, "ile.feu"); Qc.epreuves = { feu: t0 }; M.ile(CA, Qc, t0);
    assert.equal(M.ile(CA, Qc, t0).ressources.effets.cueillette, 1, "tout vient de la cueillette");
    let mc = 0; for (let d = 1; d <= 40; d++) mc += M.ile(CA, Qc, t0 + d * J).population.journal.cueillette || 0;
    assert.ok(mc > 0, "des cueilleurs n'en reviennent pas"); }
  delete CA.ile.regles.limites;
  // Un monde fini : la pêche puise dans les bancs, qui repoussent ; trop de pêcheries les vident, l'effort les ménage.
  const peche = () => { const Q = M.nouvellePartie(t0); Q.mode = "ile"; Q.credits.solde = 5000;
    CA.competences.filter(k => k.rang === 1).forEach(k => sait(Q, k.id)); M.ile(CA, Q, t0);
    Q.population.a = 300; Q.ressources.stocks.bois = 1000; Q.ressources.stocks.nourriture = 5000; Q.quartiers = {}; CA.ile.quartiers.forEach(q => { Q.quartiers[q.id] = t0; }); return Q; };
  CA.ile.regles.aleas.chance = 0;
  // Victor (2026-11-13) : le camp de bûcherons attend l'épreuve « Former une hache », elle-même précédée d'une quête.
  { const Qh = peche(); delete Qh.epreuves.hache;
    assert.deepEqual(M.epreuvesEnAttente(CA, Qh), ["hache"], "la hache attend dès le village");
    const eh = M.etatAmenagement(CA, Qh, "bucheron", t0); assert.ok(!eh.possible && eh.epreuve === "hache", "pas de bûcherons sans hache");
    const rh = M.construireIle(CA, Qh, "bucheron", t0); assert.ok(!rh || !rh.ok, "le chantier refuse le camp de bûcherons");
    const qh = M.queteIle(CA, Qh, "hache"); assert.equal(qh.reste, 4); qh.objets.forEach(o => M.ramasserIle(CA, Qh, "hache", o.id, t0));
    assert.ok(M.queteIle(CA, Qh, "hache").complete, "quête de la hache bouclée");
    assert.ok(M.reussirEpreuve(CA, Qh, "hache", t0).premiere); assert.deepEqual(M.epreuvesEnAttente(CA, Qh), []);
    const eh2 = M.etatAmenagement(CA, Qh, "bucheron", t0); assert.ok(eh2.possible && !eh2.epreuve, "la hache faite, le camp se bâtit");
    const hab0 = M.ile(CA, Qh, t0).habitants, px = M.perdreExplorateur(CA, Qh, t0);
    assert.ok(px.perdu === 1 && px.habitants === hab0 - 1 && Qh.explorateurs === 1, "un explorateur pris : un habitant de moins");
    { const Qv = M.nouvellePartie(t0); Qv.mode = "ile"; M.ile(CA, Qv, t0); Qv.population.e = 0; Qv.population.a = 2; Qv.population.v = 0; assert.equal(M.perdreExplorateur(CA, Qv, t0).perdu, 0, "jamais les deux derniers"); }
    { const b0 = M.baiesIle(CA, Qh, t0), n0 = Qh.ressources.stocks.nourriture; assert.equal(b0.reste, 6);
      const cb = M.cueillirBaies(CA, Qh, [0, 3], t0); assert.ok(cb.n === 2 && cb.nourriture === 10 && Qh.ressources.stocks.nourriture === n0 + 10, "deux buissons rapportés : dix vivres");
      assert.equal(M.cueillirBaies(CA, Qh, [0], t0).n, 0, "un buisson ne se cueille qu'une fois par jour"); assert.equal(M.baiesIle(CA, Qh, t0).reste, 4);
      assert.equal(M.baiesIle(CA, Qh, t0 + 2 * J).reste, 6, "les baies repoussent"); }
    const EH = M.epreuveIle(CA, "hache"); assert.deepEqual(EH.etapes.map(e => e.type), ["frappes", "frotter", "assemblage"]);
    const as = EH.etapes[2]; assert.deepEqual(as.ordre.slice().sort(), as.pieces.map(x => x.id).sort(), "l'ordre d'assemblage nomme toutes les pièces"); }
  // Victor (2026-11-12) : un aménagement ne se bâtit que dans son quartier, qu'il faut d'abord ouvrir.
  { const Q0 = peche(); delete Q0.quartiers.port;
    const e0 = M.etatAmenagement(CA, Q0, "pecherie", t0); assert.ok(!e0.possible && e0.ferme && e0.ferme.id === "port" && e0.ferme.aOuvrir, "port fermé : pas de pêcherie");
    assert.ok(!M.construireIle(CA, Q0, "pecherie", t0).ok);
    Q0.sites = { port: { t: t0, position: CA.ile.quartiers.find(q => q.id === "port").position } };
    assert.ok(M.ouvrirQuartier(CA, Q0, "port", "credits", null, t0).ouvert);
    const r0 = M.construireIle(CA, Q0, "pecherie", t0); assert.ok(r0.ok && r0.quartier === "port", "port ouvert : la pêcherie s'y bâtit");
    // Une pêcherie bâtie au village avant la règle rejoint le port, qui s'ouvre sans frais.
    const Q9 = peche(); delete Q9.quartiers.port; Q9.ressources.batis.push({ id: "pecherie", q: "ville", t: t0 });
    const I9 = M.ile(CA, Q9, t0); assert.equal(Q9.ressources.batis.filter(b => b.id === "pecherie")[0].q, "port"); assert.ok(I9.quartiers.find(q => q.id === "port").fonde); }
  // Victor (2026-11-13) : chantier exceptionnel, une fois par jour, au risque d'épuiser la ressource.
  { const Qx = peche(); const b0 = Qx.ressources.stocks.bois, f0 = Qx.ressources.nature.foret;
    const rx = M.chantierExceptionnel(CA, Qx, "foret", t0); assert.ok(rx.ok && rx.pris === 120 && rx.gain === 60, "grande coupe : 20 % de la forêt, 60 bois");
    assert.equal(Qx.ressources.stocks.bois, b0 + 60); assert.equal(Qx.ressources.nature.foret, f0 - 120);
    assert.ok(!M.chantierExceptionnel(CA, Qx, "foret", t0).ok, "une seule par jour");
    Qx.ressources.nature.foret = 50; const r2 = M.chantierExceptionnel(CA, Qx, "foret", t0 + J); assert.ok(r2.ok && r2.vide && Qx.ressources.nature.foret === 0, "la coupe de trop rase la forêt"); }
  const Q1 = peche(), Q2 = peche();
  for (let i = 0; i < 4; i++) { assert.ok(M.construireIle(CA, Q1, "pecherie", t0).ok); M.construireIle(CA, Q2, "pecherie", t0); }
  const n0 = M.ile(CA, Q1, t0).ressources.nature.filter(x => x.id === "poisson")[0];
  assert.equal(n0.stock, 500); assert.ok(n0.pris > n0.durable && !n0.soutenable && n0.jours > 0, "quatre pêcheries prennent plus que la repousse");
  assert.equal(M.reglerEffort(CA, Q2, "pecherie", 0.25, t0), 0.25);
  assert.ok(M.ile(CA, Q2, t0).ressources.nature.filter(x => x.id === "poisson")[0].soutenable, "au quart de l'effort, la pêche est durable");
  for (let j = 1; j <= 60; j++) { Q1.ressources.stocks.nourriture = 5000; Q2.ressources.stocks.nourriture = 5000; M.ile(CA, Q1, t0 + j * J); M.ile(CA, Q2, t0 + j * J); }
  const f1 = M.ile(CA, Q1, t0 + 60 * J).ressources.nature.filter(x => x.id === "poisson")[0], f2 = M.ile(CA, Q2, t0 + 60 * J).ressources.nature.filter(x => x.id === "poisson")[0];
  assert.ok(f1.part < 0.25 && (f1.etat === "rouge" || f1.etat === "epuise"), "les bancs trop pêchés s'effondrent");
  assert.ok(f2.part > 0.45 && f2.etat === "vert", "les bancs ménagés tiennent");
  assert.ok(M.ile(CA, Q1, t0 + 60 * J).ressources.prod.nourriture < M.ile(CA, Q2, t0 + 60 * J).ressources.prod.nourriture, "et à la fin, on pêche moins qu'en ménageant");
  // Effondrement : forêt rasée, bancs vidés, pas de ferme. La faim vide l'île ; les aménagements tombent, les savoirs restent.
  const Q3 = peche(); for (let i = 0; i < 3; i++) M.construireIle(CA, Q3, "bucheron", t0); M.construireIle(CA, Q3, "foyer", t0);
  Q3.ressources.nature.foret = 0; Q3.ressources.nature.poisson = 0; Q3.ressources.stocks.nourriture = 0;
  const natif = CA.ile.nature.map(x => x.retour); CA.ile.nature.forEach(x => { x.retour = 0; });
  let j3 = 0; while (M.ile(CA, Q3, t0 + (++j3) * J).habitants > 0 && j3 < 400) { /* la faim fait son œuvre */ }
  CA.ile.nature.forEach((x, i) => { x.retour = natif[i]; });
  assert.ok(j3 < 400 && Q3.ressources.effondrement && Q3.ressources.effondrement.perdus === 3, "l'île affamée se vide et perd ses aménagements");
  assert.deepEqual(Q3.ressources.batis.map(b => b.id), ["foyer"], "il reste le foyer"); assert.ok(M.estMaitrisee(Q3, "phys.machines"), "et les savoirs");
  // Un arbre en chantier (un seul savoir) ne compte pas comme une branche complète.
  { const Qs = M.nouvellePartie(t0); Qs.mode = "ile"; Qs.epreuves = { feu: t0 }; Qs.competences["ile.feu"] = { maitrise: true, maitriseDepuis: t0, prochainRappel: t0 + 400 * J, palier: 1, xp: 5 };
    assert.ok(!M.conditionRemplie(CA, Qs, { type: "branches_completes", n: 1 }, t0), "le feu seul ne complète pas une branche"); }
  // Les aléas : annoncés la veille à qui sait lire le ciel ; préparé, rien n'est perdu ; sinon un aménagement tombe.
  const alea = (prepare, sansSavoir) => { const Q = peche(); if (sansSavoir) delete Q.competences["meteo.ciel"];
    M.construireIle(CA, Q, "pecherie", t0); M.construireIle(CA, Q, "ferme", t0); M.forcerAlea(CA, Q, "tempete", t0);
    const an = M.ile(CA, Q, t0).alea.annonce;
    if (prepare) assert.ok(M.preparerAlea(CA, Q, true, t0).pret);
    return { Q, an, apres: M.ile(CA, Q, t0 + J) }; };
  const a1 = alea(false);
  assert.ok(a1.an && a1.an.id === "tempete" && a1.an.savoir === "meteo.ciel" && a1.an.cibles.includes("pecherie"), "la tempête est annoncée la veille");
  assert.equal(a1.apres.alea.dernier.perdu, "pecherie", "sans préparation, la tempête emporte la pêcherie"); assert.equal(a1.apres.ressources.batis.pecherie, 0); assert.equal(a1.apres.ressources.batis.ferme, 1);
  const a2 = alea(true);
  assert.ok(a2.apres.alea.dernier.evite && a2.apres.ressources.batis.pecherie === 1, "préparée, l'île ne perd rien");
  const a3 = alea(false, true);
  assert.equal(a3.an, null, "sans savoir météo, pas d'annonce"); assert.equal(a3.apres.alea.dernier.perdu, "pecherie");
  const Q4 = peche(); M.construireIle(CA, Q4, "pecherie", t0); M.forcerAlea(CA, Q4, "tempete", t0);
  assert.equal(M.preparerAlea(CA, Q4, false, t0).pret, false); assert.equal(M.preparerAlea(CA, Q4, true, t0), null, "une seule tentative");
  assert.ok(M.ile(CA, Q4, t0).alea.annonce.essaye);
  // Pendant une absence, aucun aléa ne frappe.
  const Q5 = peche(); M.construireIle(CA, Q5, "pecherie", t0); Q5.aleas = { force: { jour: "2026-11-15", id: "tempete" } };
  M.ile(CA, Q5, t0 + 5 * J); assert.equal(Q5.ressources.batis.filter(b => b.id === "pecherie").length, 1, "pas d'aléa pendant une absence");
  // Le mode Parcours ne connaît pas les âges.
  const PP = M.nouvellePartie(t0); assert.notEqual(M.statut(CA, PP, "math.babylone", t0).age, 2);
  console.log("OK : île par âges (feu, besoins, savoirs requis), monde fini (bancs, effort, effondrement), aléas annoncés");
}
