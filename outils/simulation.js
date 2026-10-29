// Simulation d'une longue partie (node outils/simulation.js [packs éteints…]) : sert aux tests des packs.
// Joue des centaines d'épreuves comme le bouton « Jouer » (choix de l'IA, quiz ou rappel, plateau), avec des packs
// éteints ou non, et renvoie la partie. Une exception ici = un pack éteint casse le moteur.
const fs = require("fs"), path = require("path");
const M = require("../web/moteur.js");
const FICHIERS = ["regles.json", "skills.json", "questions.json", "succes.json", "commentaires.json", "objets.json", "avatar.json",
  "ia.json", "plateau.json", "frise.json", "bibliotheque.json", "ennemis.json", "atomes.json", "packs.json"];

function charger() {
  const d = {};
  for (const f of FICHIERS) d[f] = JSON.parse(fs.readFileSync(path.join(__dirname, "../data", f), "utf8"));
  return d;
}

function contenu(brut, off) {
  const d = M.filtrerPacks(brut, brut["packs.json"], off);
  return M.indexerContenu(d["regles.json"], d["skills.json"], d["questions.json"], d["succes.json"], { commentaires: d["commentaires.json"], objets: d["objets.json"],
    avatar: d["avatar.json"], ia: d["ia.json"], plateau: d["plateau.json"], frise: d["frise.json"], bibliotheque: d["bibliotheque.json"], ennemis: d["ennemis.json"], atomes: d["atomes.json"] });
}

// Un générateur pseudo-aléatoire fixe : la même graine rejoue la même partie.
function graine(n) { return () => ((n = (n * 1103515245 + 12345) % 2147483648) / 2147483648); }

function jouer(C, P, epreuves, t, alea) {
  const jour = 86400000;
  for (let i = 0; i < epreuves; i++) {
    if (i % 4 === 3) t += jour;
    M.noterVisite(C, P, t); M.verifierRecompenses(C, P, t);
    if (M.jeuFerme(C, P, t)) { P.punition = null; continue; }
    if (P.duel && M.duelBloquant(P)) { const qs = M.tirerDuel(C, P, t, alea); M.terminerDuel(C, P, qs.map(() => ({ correct: alea() < 0.9 })), t, alea, qs.length); continue; }
    const s = M.atomeSauvage(C, P);
    if (s) { M.tirerCombat(C, P); M.terminerCombat(C, P, alea() < 0.7 ? 3 : 1, t, [], false); continue; }
    if (M.piegeEnAttente && M.piegeEnAttente(P)) { const q = M.questionPiege(C, P, alea); M.repondrePiege(C, P, !!q && alea() < 0.6, t); continue; }
    const c = M.choixIA(C, P, t);
    if (!c) { t += jour; continue; }
    const n = c.type === "rappel" ? C.regles.rappels.questions_par_rappel : M.questionsQuiz(C, P, t);
    const res = M.tirerQuestions(C, P, c.comp.id, n, alea).map(q => ({ id: q.id, correct: alea() < 0.85 }));
    if (c.type === "rappel") M.terminerRappel(C, P, c.comp.id, res, t, { jouer: true, total: n });
    else M.terminerQuiz(C, P, c.comp.id, res, t, { jouer: true, total: n, duree: 90000 });
    t += 3600000;
  }
  return t;
}

if (require.main === module) {
  const brut = charger(), off = process.argv.slice(2);
  const C = contenu(brut, off);
  const P = M.nouvellePartie(new Date(2026, 9, 1, 9).getTime());
  P.options = { tousArbres: true };
  jouer(C, P, 400, P.cree, graine(7));
  process.stdout.write(JSON.stringify(P));
}
module.exports = { charger, contenu, jouer, graine };
