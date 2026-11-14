// Tests des packs en jeu (node outils/test_packs.js) : chaque pack s'éteint sans casser le moteur et sans rien perdre.
const assert = require("assert"), fs = require("fs"), path = require("path");
const S = require("./simulation.js"), M = require("../web/moteur.js");
const brut = S.charger(), index = brut["packs.json"];
const packs = index.packs.filter(m => m.sorte !== "socle").map(m => m.id);
const ids = l => new Set(l.map(x => x.id));
const complet = S.contenu(brut, []);
assert.ok(complet.stats.length >= 10 && complet.atomes && complet.ennemis.length, "tout allumé : tout est là");

for (const id of packs) {
  const C = S.contenu(brut, [id]);
  // Ce que le pack apporte a disparu, le reste est intact.
  for (const [ou, proprios] of Object.entries(index.proprietaires)) {
    const siens = Object.keys(proprios).filter(k => proprios[k] === id);
    if (ou === "skills.json/competences") for (const k of siens) assert.ok(!C.parId[k], `${id} éteint : compétence ${k} encore là`);
    if (ou === "questions.json/questions") for (const k of siens) assert.ok(!C.questionParId[k], `${id} éteint : question ${k} encore là`);
    if (ou === "succes.json/succes") for (const k of siens) assert.ok(!C.parSucces[k], `${id} éteint : succès ${k} encore là`);
  }
  assert.ok(C.competences.every(k => k.prerequis.every(p => C.parId[p])), `${id} éteint : un prérequis pointe dans le vide`);
  // Une partie se joue pack éteint, puis continue pack rallumé, avec sa progression.
  const P = M.nouvellePartie(new Date(2026, 9, 1, 9).getTime());
  P.options = { tousArbres: true, packsOff: [id] };
  let t = S.jouer(complet, P, 25, P.cree, S.graine(5));
  const avant = JSON.stringify(P.competences);
  M.accorderPartie(C, P);
  t = S.jouer(C, P, 30, t, S.graine(9));
  M.accorderPartie(complet, P);
  S.jouer(complet, P, 10, t, S.graine(2));
  for (const k of Object.keys(JSON.parse(avant))) assert.ok(P.competences[k], `${id} : la compétence ${k} a été perdue`);
}

// Un jeu éteint met en veille ce qu'il avait en cours, et le rend au réveil.
{
  const P = M.nouvellePartie(Date.now());
  P.sauvages = [{ z: 8, case: 3 }]; P.duel = { ennemi: "sophiste", case: 4, pret: true };
  M.accorderPartie(S.contenu(brut, ["atomes", "ennemis"]), P);
  assert.deepEqual(P.sauvages, []); assert.equal(P.duel, null);
  M.accorderPartie(complet, P);
  assert.equal(P.sauvages[0].z, 8); assert.equal(P.duel.ennemi, "sophiste");
}

// Les dépendances : éteindre un pack éteint ceux qui le requièrent ; le socle ne s'éteint pas.
{
  const fictif = { packs: index.packs.concat([{ id: "fils", sorte: "domaine", requiert: ["socle", "mecanique"] }]) };
  const off = M.packsEteints(fictif, ["mecanique", "socle"]);
  assert.ok(off.mecanique && off.fils && !off.socle);
}

// Fil « Basile » : un pack « reglages »: { « allume »: false } reste éteint tant qu'on ne l'allume pas (« +cp ») ; une partie d'adulte ne le voit pas.
{
  assert.ok(M.packsEteints(index, []).cp, "le pack CP est éteint par défaut");
  assert.ok(!M.packsEteints(index, ["+cp"]).cp, "« +cp » l'allume");
  assert.ok(!complet.stats.some(s => s.id.startsWith("cp-")));
  assert.ok(S.contenu(brut, ["+cp"]).stats.some(s => s.id === "cp-calcul"));
  // La règle tient au manifeste, pas au nom du pack : tout pack qui déclare les mêmes réglages suit le même chemin, même chargé à part.
  const fictif = { packs: index.packs.concat([{ id: "ce1", sorte: "domaine", reglages: { allume: false, ton: "enfant", voix: true }, requiert: ["socle"] }]) };
  assert.ok(M.packsEteints(fictif, []).ce1 && !M.packsEteints(fictif, ["+ce1"]).ce1);
  const os = require("os"), { execFileSync } = require("child_process"), f = path.join(os.tmpdir(), "test-cp.pack.json");
  execFileSync("python3", [path.join(__dirname, "packs.py"), "paquet", "cp", f]);
  const paquet = JSON.parse(fs.readFileSync(f, "utf8")); fs.unlinkSync(f);
  assert.equal(paquet.manifeste.reglages.allume, false, "le paquet garde ses réglages");
  const sans = JSON.parse(JSON.stringify(M.filtrerPacks(brut, index, ["cp"]))), idx = JSON.parse(JSON.stringify(index));
  idx.packs = idx.packs.filter(m => m.id !== "cp");
  for (const ou of Object.keys(idx.proprietaires)) for (const k of Object.keys(idx.proprietaires[ou])) if (idx.proprietaires[ou][k] === "cp") delete idx.proprietaires[ou][k];
  M.ajouterPaquet(sans, idx, paquet);
  assert.ok(M.packsEteints(idx, []).cp && !M.packsEteints(idx, ["+cp"]).cp, "chargé à part, il reste éteint par défaut");
  // Réglages d'une nouvelle partie : ceux sur lesquels tous les domaines allumés s'accordent.
  const seuls = id => { const o = {}; fictif.packs.forEach(m => { if (m.sorte !== "socle" && m.id !== id && m.id !== "cp") o[m.id] = true; }); return o; };
  assert.deepEqual(M.reglagesDesPacks(fictif, seuls("ce1")), { ton: "enfant", voix: true });
  const ceEtCp = seuls("ce1"); delete ceEtCp.cp;
  assert.deepEqual(M.reglagesDesPacks(fictif, ceEtCp), { ton: "enfant", voix: true }, "deux packs d'accord : leurs réglages communs");
  assert.deepEqual(M.reglagesDesPacks(fictif, M.packsEteints(fictif, ["+ce1"])), {}, "avec un domaine adulte : rien ne change");
  console.log("OK : réglages des packs (éteint par défaut, réglages communs), quel que soit le pack");
}

// Victor (2026-11-09) : le jeu est modulable. La dramaturgie d'Alyca et les succès généraux sont des packs de jeu ; un
// domaine dit de quels jeux il se passe (« sans »), et le noyau se joue sans eux.
{
  const domaines = index.packs.filter(m => m.sorte === "domaine").map(m => m.id);
  const cpSeul = domaines.filter(id => id !== "cp").concat(["+cp"]);
  const off = M.packsEteints(index, cpSeul);
  for (const id of ["dramaturgie", "succes"]) assert.ok(off[id], `CP seul : ${id} écarté`);
  assert.ok(!M.packsEteints(index, cpSeul.concat(["+dramaturgie"])).dramaturgie, "le joueur la rallume (« +dramaturgie »)");
  assert.ok(!M.packsEteints(index, ["+cp"]).dramaturgie, "avec un domaine qui ne l'écarte pas, elle reste");
  assert.ok(!M.packsEteints(index, []).dramaturgie && !M.packsEteints(index, []).succes, "partie d'adulte : rien ne change");
  assert.deepEqual(M.allumerPack(index, cpSeul, "dramaturgie").filter(x => /dramaturgie/.test(x)), ["+dramaturgie"], "allumerPack note « +id » pour un pack écarté");
  // La règle tient au manifeste : n'importe quel domaine peut écarter n'importe quel pack de jeu.
  const fictif = { packs: index.packs.concat([{ id: "ce1", sorte: "domaine", reglages: { allume: false, sans: ["atomes"] }, requiert: ["socle"] }]) };
  const ce1Seul = domaines.concat(["+ce1"]);
  assert.ok(M.packsEteints(fictif, ce1Seul).atomes && !M.packsEteints(fictif, ce1Seul).dramaturgie);
  assert.ok(M.packsEteints(fictif, ce1Seul.filter(x => x !== "cp").concat(["+cp"])).atomes, "CE1 et CP d'accord sur les atomes : écartés");
  assert.ok(!M.packsEteints(fictif, ["+ce1"]).atomes, "un domaine qui garde les atomes suffit à les garder");

  // Dramaturgie éteinte : ses clés quittent ia.json, ses listes aussi ; le noyau garde un masque et un narrateur sobre.
  const C = S.contenu(brut, ["dramaturgie"]);
  assert.ok(complet.ia.faveur && complet.ia.alyca && complet.ia.masques_jour && complet.ia.credits.pots && M.dramaturgie(complet));
  for (const k of ["faveur", "alyca", "masques_jour"]) assert.ok(!(k in C.ia), `dramaturgie éteinte : ia.${k} encore là`);
  for (const k of ["humeurs", "pots", "agacement", "ultimatum", "emplettes", "verdicts"]) assert.ok(!(k in C.ia.credits), `ia.credits.${k} encore là`);
  assert.ok(C.ia.credits.bareme && C.ia.credits.boutique.articles.length, "les crédits et la boutique restent au noyau");
  assert.ok(!C.ia.credits.boutique.articles.some(a => a.id === "masque"), "plus de masque en boutique");
  assert.ok(!M.dramaturgie(C) && C.ia.masques.length >= 1 && C.ia.masques.every(m => !m.condition), "il ne reste que les masques de base");
  assert.ok(!C.apartes.length && !C.surnoms && !(C.avatar.tenues_farce || []).length);
  assert.ok(!C.commentairesPar.faveur_comblee && !C.commentairesPar.pot_radin && C.commentairesPar.accueil.length);
  const t0 = new Date(2026, 9, 1, 9).getTime(), P = M.nouvellePartie(t0);
  P.options = { tousArbres: true, packsOff: ["dramaturgie"] };
  assert.equal(M.tonDe(C, P), "sobre"); assert.equal(M.tonDe(complet, P), null);
  assert.ok(/^sobre-/.test(M.replique(C, P, ["quiz_reussi"], () => 0).id), "le narrateur parle sobrement");
  P.options.reglages = { ton: "enfant" }; assert.equal(M.tonDe(C, P), "enfant", "un ton choisi passe avant"); delete P.options.reglages;
  let t = S.jouer(C, P, 60, t0, S.graine(3));
  assert.ok(!P.faveur && !P.alyca && !P.punition && !P.ultimatum && !P.farce, "aucune trace de la dramaturgie dans la partie");
  assert.deepEqual(Object.keys(P.masques || {}).filter(id => id !== C.ia.masques[0].id), [], "aucun masque gagné");
  assert.equal(M.faveurIA(C, P, t), null); assert.equal(M.jeuFerme(C, P, t), false);
  assert.equal(M.potPossible(C, P, 5, t).ok, false); assert.equal(M.tenterUltimatum(C, P, t, () => 0), null);
  assert.deepEqual(M.masquesDuJour(C, P, t), []);
  // Un ultimatum ou une peine en suspens dorment pendant que la dramaturgie est éteinte, et reviennent avec elle.
  const P2 = M.nouvellePartie(t0); P2.ultimatum = { demande: 50, niveaux: 2, depuis: t0 }; P2.punition = { restant: 60000, total: 60000, palier: "boudeuse", rang: 2, depuis: t0, n: 1 };
  M.accorderPartie(C, P2); assert.ok(!P2.ultimatum && !P2.punition && P2.veille.ultimatum && P2.veille.punition);
  M.accorderPartie(complet, P2); assert.ok(P2.ultimatum && P2.punition);

  // Succès généraux éteints : chaque domaine garde les siens, les crédits tombent toujours.
  const CS = S.contenu(brut, ["succes"]), generaux = Object.keys(index.proprietaires["succes.json/succes"]).filter(k => index.proprietaires["succes.json/succes"][k] === "succes");
  assert.ok(generaux.length >= 80 && generaux.every(id => !CS.parSucces[id]) && CS.succes.length > 100);
  assert.ok(M.succesAbsent(CS, "premier-pas") && !M.succesAbsent(complet, "premier-pas"));
  const tn = complet.avatar.creation.tenues.filter(x => x.condition && x.condition.type === "succes" && generaux.indexOf(x.condition.id) >= 0)[0];
  if (tn) { const P3 = M.nouvellePartie(t0); assert.ok(M.tenueDebloquee(CS, P3, tn) && !M.tenueDebloquee(complet, P3, tn), "tenue gardée par un succès absent : libre"); }

  // CP seul : le jeu le plus simple. Ni faveur, ni succès généraux, ni ennemis, ni atomes ; les succès du CP restent, avec celui de la grotte de l'île (pack de jeu, toujours là).
  const CP = S.contenu(brut, cpSeul);
  assert.ok(!M.dramaturgie(CP) && !CP.ennemis.length && !CP.atomes && CP.succes.length && CP.succes.every(s => ["cp", "ile"].includes(index.proprietaires["succes.json/succes"][s.id])));
  const P4 = M.nouvellePartie(t0); P4.options = { packsOff: cpSeul, reglages: M.reglagesDesPacks(index, off) };
  assert.equal(M.tonDe(CP, P4), "enfant");
  S.jouer(CP, P4, 80, t0, S.graine(7));
  assert.ok(!P4.faveur && !P4.duel && Object.keys(P4.succes).every(id => CP.parSucces[id]));
  // Sans dramaturgie, un succès verse son tarif tel quel.
  const verses = Object.keys(P4.credits.parSucces).map(id => P4.credits.parSucces[id]);
  assert.ok(verses.length && verses.every(cr => cr.mot === null && cr.n === cr.base), "tarif versé sans humeur ni commentaire");
  console.log("OK : jeu modulable (dramaturgie, succès généraux, réglage « sans », narrateur sobre, CP seul)");
}

// Boutique : un pack éteint retire ses articles.
assert.ok(!M.articleDe(S.contenu(brut, ["atomes"]), "relance") && M.articleDe(complet, "relance"));
assert.ok(!M.articleDe(S.contenu(brut, ["ennemis"]), "chasser"));
// Cohérence : une longue partie avec des packs éteints ne montre rien d'eux (épreuves, butin, succès, plateau, Alyca).
function coherence(off, depuis, C, P) {
  const eteints = M.packsEteints(index, off), PR = index.proprietaires, pb = [];
  const de = (fam, id) => (PR[fam] || {})[id];
  const FAM = { competences: "skills.json/competences", succes: "succes.json/succes", objets: "objets.json/objets", savants: "avatar.json/savants",
    evenements: "frise.json/evenements", livres: "bibliotheque.json/livres", masques: "ia.json/masques", accessoires: "avatar.json/accessoires" };
  for (const [k, fam] of Object.entries(FAM)) for (const [id, v] of Object.entries(P[k] || {}))
    if (typeof v === "number" && v > depuis && eteints[de(fam, id)]) pb.push(`${k} ${id}`);
  for (const j of P.journal) if (j.t > depuis && j.comp && !C.parId[j.comp]) pb.push(`épreuve ${j.comp}`);
  // Victor (2026-11-01) : une date du socle rattachée à un arbre éteint ne se débloque pas.
  for (const e of C.evenements || []) if (P.evenements[e.id] > depuis && e.stat && !C.parStat[e.stat]) pb.push(`date ${e.id}`);
  for (const k of Object.keys(C.commentairesPar)) if (k.includes("@") && eteints[k.split("@")[1]]) pb.push(`répliques ${k}`);
  if (P.lot && P.lot.t > depuis && P.lot.theme && !C.parStat[P.lot.theme]) pb.push(`butin au thème ${P.lot.theme}`);
  const pc = P.plateau.parcours;
  if (pc && pc.dessine > depuis && ((eteints.ennemis && pc.ennemis) || (eteints.atomes && pc.atomes))) pb.push("parcours avec ennemis ou atomes");
  if (eteints.atomes && P.sauvages.length) pb.push("atomes sauvages");
  if (eteints.ennemis && (P.duel || Object.keys(P.plateau.ennemis || {}).length)) pb.push("ennemis ou duel");
  for (const { n } of complet.plateau.cases) { const sp = M.specialDe(C, P, n); if (eteints.atomes && sp && sp.type === "mendeleiev") pb.push(`case ${n} Mendeleïev`); }
  assert.deepEqual([...new Set(pb)].slice(0, 5), [], `incohérent avec ${off.join(", ")} éteints`);
}
for (const off of [["logique", "mecanique", "savoir"], ["atomes", "ennemis", "cosmos"]]) {
  const C = S.contenu(brut, off), P = M.nouvellePartie(new Date(2026, 9, 1, 9).getTime());
  P.options = { packsOff: off }; M.accorderPartie(C, P);
  S.jouer(C, P, 300, P.cree, S.graine(3));
  assert.ok(Object.values(P.competences).filter(c => c.maitrise).length >= 10, `${off.join(", ")} éteints : la partie avance`);
  coherence(off, -1, C, P);
}
{ // Éteint en cours de partie.
  const off = ["mecanique", "ennemis"], C = S.contenu(brut, off), P = M.nouvellePartie(new Date(2026, 9, 1, 9).getTime());
  let t = S.jouer(complet, P, 200, P.cree, S.graine(5));
  P.options = { packsOff: off }; M.accorderPartie(C, P);
  S.jouer(C, P, 200, t, S.graine(6));
  coherence(off, t, C, P);
}
// v36 : chaque arbre apporte ses cases ; une partie Philosophes + Biais seuls part de Thalès, ne passe que par leurs
// cases, dans l'ordre des dates, et le réglage « Voir toutes les cases » les dévoile sans allonger le tour.
{
  const off = packs.filter(p => !["sagesse", "lucidite"].includes(p)), C = S.contenu(brut, off);
  const P = M.nouvellePartie(new Date(2026, 9, 30, 9).getTime());
  P.options = { packsOff: off }; M.accorderPartie(C, P);
  const rt = M.routeTour(C, P), arr = rt[rt.length - 1], ks = rt.slice(0, -1).map(n => M.caseN(C, n));
  assert.equal(ks[0].id, "thales-eau", "premier tour : Thalès en premier");
  assert.ok(ks.every(k => ["sagesse", "lucidite"].includes(k.stat)), "seulement les cases des arbres allumés");
  assert.ok(ks.every((k, i) => !i || ks[i - 1].annee <= k.annee), "cases dans l'ordre des dates");
  assert.ok(M.caseN(C, arr).arrivee && new Set(rt).size === rt.length);
  // Victor (2026-11-08) : « Cases par tour » compte les cases de tous les arbres cochés ensemble, pas par arbre.
  assert.ok(C.plateau.cases.length > 30, "deux arbres : plus de cases qu'un tour");
  assert.equal(ks.length, M.casesParTour(C, P), "le tour fait « Cases par tour » cases, tous arbres confondus");
  M.voirToutesCases(C, P, true);
  const tout = M.routeTour(C, P);
  // Victor (2026-11-08) : le réglage dévoile les cases, la longueur du tour reste celle de « Cases par tour ».
  assert.equal(tout.length, M.casesParTour(C, P) + 1, "réglage coché : le tour garde sa longueur");
  assert.ok(C.plateau.cases.every(k => M.caseDecouverte(P, k.n)), "toutes dévoilées, même celles des tours à venir");
  M.voirToutesCases(C, P, false);
  assert.ok(!M.caseDecouverte(P, arr), "réglage coupé : l'arrivée redevient cachée");
  assert.equal(M.routeTour(C, P).length, M.casesParTour(C, P) + 1, "réglage coupé : le tour revient à « Cases par tour »");
  S.jouer(C, P, 60, P.cree, S.graine(7));
  console.log("OK : cases par arbre, Thalès en premier, réglage « Voir toutes les cases »");
}
// Tous les domaines éteints un moment : la route tombe à la seule arrivée, puis se redessine dès qu'un domaine revient
// (Victor, 2026-10-30 : bloqué sur un parcours d'une case après avoir changé de domaines).
{
  const sauf = l => packs.filter(p => !l.includes(p));
  const P = M.nouvellePartie(new Date(2026, 9, 30, 9).getTime());
  P.options = { packsOff: sauf(["mecanique"]) }; M.accorderPartie(S.contenu(brut, sauf(["mecanique"])), P);
  M.accorderPartie(S.contenu(brut, sauf([])), P);
  assert.equal(M.routeTour(S.contenu(brut, sauf([])), P).length, 1, "aucun domaine : l'arrivée seule");
  const C = S.contenu(brut, sauf(["logique"])); M.accorderPartie(C, P);
  // Une case par compétence (Victor, 2026-10-31) : un domaine seul peut avoir moins de 24 cases ; la route les prend toutes.
  const nLogique = C.plateau.cases.filter(k => k.stat === "logique").length;
  assert.ok(M.routeTour(C, P).length >= Math.min(24, nLogique), "un domaine rallumé : la route se redessine");
  console.log("OK : route d'une case redessinée quand un domaine revient");
}
// v53 : un pack de domaine chargé par le joueur (outils/packs.py paquet) se pose comme s'il avait été assemblé.
{
  const os = require("os"), { execFileSync } = require("child_process");
  // Victor (2026-11-04) : un portrait peut appartenir à plusieurs domaines (champ domaines). Sagesse éteinte, Aristote reste
  // en portrait pour Lucidité, Empathie et Mécanique ; tous éteints, il disparaît.
  {
    const ids = new Set(index.packs.map(m => m.id));
    for (const x of brut["avatar.json"].savants.concat(brut["avatar.json"].portraits)) for (const d of x.domaines || []) assert.ok(ids.has(d), `${x.id} : domaine inconnu ${d}`);
    const sansS = M.filtrerPacks(brut, index, ["sagesse"]);
    const a = sansS["avatar.json"].portraits.find(x => x.id === "aristote");
    assert.ok(a && !sansS["avatar.json"].savants.some(x => x.id === "aristote"), "Aristote reste en portrait sans Sagesse");
    assert.ok(a.theme !== "sagesse" && !a.condition, "rangé sous un domaine allumé, sans condition de déblocage");
    assert.ok(sansS["avatar.json"].portraits.some(x => x.id === "protagoras"), "Protagoras (Éloquence) reste là");
    const aucun = M.filtrerPacks(brut, index, ["sagesse", "lucidite", "empathie", "mecanique"]);
    assert.ok(!aucun["avatar.json"].portraits.some(x => x.id === "aristote"), "plus aucun de ses domaines : plus d'Aristote");
    const sansE = M.filtrerPacks(brut, index, ["eloquence"]);
    const pr = sansE["avatar.json"].portraits.find(x => x.id === "protagoras");
    assert.ok(pr && pr.theme === "lucidite", "Éloquence éteinte : Protagoras passe sous Lucidité");
    // Victor (2026-11-04) : Ibn al-Haytham (Mécanique) ouvre biais.optique/lumiere ; Mécanique éteinte, il reste pour Lucidité.
    const sansM = M.filtrerPacks(brut, index, ["mecanique"]);
    const ih = sansM["avatar.json"].portraits.find(x => x.id === "ibn-al-haytham");
    assert.ok(ih && ih.theme === "lucidite", "Mécanique éteinte : Ibn al-Haytham passe sous Lucidité");
  }
  const f = path.join(os.tmpdir(), "test-musique.pack.json");
  execFileSync("python3", [path.join(__dirname, "packs.py"), "paquet", "musique", f]);
  const paquet = JSON.parse(fs.readFileSync(f, "utf8")); fs.unlinkSync(f);
  assert.equal(paquet.sources.verifiees, paquet.sources.total, "paquet : sources toutes vérifiées");
  // Les données sans Musique, puis Musique chargée en paquet : on retrouve l'assemblage complet.
  const sans = JSON.parse(JSON.stringify(M.filtrerPacks(brut, index, ["musique", "+cp"])));
  const idx = JSON.parse(JSON.stringify(index));
  idx.packs = idx.packs.filter(m => m.id !== "musique");
  for (const ou of Object.keys(idx.proprietaires)) for (const k of Object.keys(idx.proprietaires[ou])) if (idx.proprietaires[ou][k] === "musique") delete idx.proprietaires[ou][k];
  const v = M.verifierPaquet(sans, idx, paquet);
  assert.deepEqual(v.erreurs, [], "paquet musique accepté");
  assert.ok(v.compte["questions.json/questions"] > 20);
  M.ajouterPaquet(sans, idx, paquet);
  const cles = (d, fi, ch) => ch.reduce((o, k) => o[k], d[fi]).map(x => x.id).sort().join("|");
  for (const [fi, ch] of [["skills.json", ["competences"]], ["questions.json", ["questions"]], ["succes.json", ["succes"]], ["avatar.json", ["savants"]], ["regles.json", ["stats"]], ["plateau.json", ["cases"]]])
    assert.equal(cles(sans, fi, ch), cles(brut, fi, ch), `paquet : ${fi} identique à l'assemblage`);
  assert.ok(idx.packs.find(m => m.id === "musique").ajoute);
  // Le jeu tourne avec, puis sans (pack éteint), sans rien perdre.
  sans["packs.json"] = idx;
  const C = S.contenu(sans, []), P = M.nouvellePartie(new Date(2026, 9, 1, 9).getTime());
  P.options = { tousArbres: true };
  S.jouer(C, P, 60, P.cree, S.graine(4));
  assert.ok(C.parStat.musique && C.parStat.musique.length);
  // Refus : un pack de jeu, un doublon d'un pack officiel, une dépendance absente, un emplacement interdit.
  const refus = (mod, attendu) => { const q = JSON.parse(JSON.stringify(paquet)); mod(q); assert.ok(M.verifierPaquet(brut, index, q).erreurs.some(e => e.startsWith(attendu)), attendu); };
  refus(q => { q.manifeste.sorte = "jeu"; }, "sorte");
  refus(q => {}, "officiel");
  refus(q => { q.manifeste.id = "musique2"; }, "doublon");
  refus(q => { q.manifeste.id = "musique2"; q.manifeste.requiert = ["socle", "inconnu"]; }, "requiert");
  refus(q => { q.manifeste.id = "musique2"; q.fragments.push({ fichier: "regles.json", chemin: ["xp"], elements: {} }); }, "emplacement");
  assert.deepEqual(M.verifierPaquet(brut, index, { format: "autre" }).erreurs, ["format"]);
}
// filtrerPacks ne copie que ce qu'il change : le reste est partagé avec les données chargées, qui ne doivent jamais
// bouger (on les refiltre à chaque changement de packs). Gelées ici, toute écriture du moteur lèverait une erreur.
{
  const gele = S.charger(); gele["ile.json"] = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/ile.json"), "utf8"));
  S.contenu(gele, []);
  const avant = JSON.stringify(gele);
  (function geler(o) { if (o && typeof o === "object" && !Object.isFrozen(o)) { Object.freeze(o); Object.values(o).forEach(geler); } })(gele);
  for (const off of [["ile"], ["ile", packs[0]], ["ile", "dramaturgie"], packs]) {
    const C = S.contenu(gele, off), P = M.nouvellePartie(new Date(2026, 9, 1, 9).getTime());
    P.options = { tousArbres: true };
    S.jouer(C, P, 40, P.cree, S.graine(6));
  }
  assert.strictEqual(JSON.stringify(gele), avant, "filtrerPacks a modifié les données chargées");
}
console.log(`OK : ${packs.length} packs éteints un à un, partie jouée puis reprise sans perte ; parties longues cohérentes avec les packs choisis ; pack additionnel chargé en paquet`);
