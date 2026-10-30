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
// cases, dans l'ordre des dates, et le réglage « Voir toutes les cases » met toutes leurs cases sur la route.
{
  const off = packs.filter(p => !["sagesse", "lucidite"].includes(p)), C = S.contenu(brut, off);
  const P = M.nouvellePartie(new Date(2026, 9, 30, 9).getTime());
  P.options = { packsOff: off }; M.accorderPartie(C, P);
  const rt = M.routeTour(C, P), arr = rt[rt.length - 1], ks = rt.slice(0, -1).map(n => M.caseN(C, n));
  assert.equal(ks[0].id, "thales-eau", "premier tour : Thalès en premier");
  assert.ok(ks.every(k => ["sagesse", "lucidite"].includes(k.stat)), "seulement les cases des arbres allumés");
  assert.ok(ks.every((k, i) => !i || ks[i - 1].annee <= k.annee), "cases dans l'ordre des dates");
  assert.ok(M.caseN(C, arr).arrivee && ks.length >= 24 && new Set(rt).size === rt.length);
  M.voirToutesCases(C, P, true);
  const tout = M.routeTour(C, P);
  assert.equal(tout.length, C.plateau.cases.length, "toutes les cases sur la route");
  assert.ok(tout.every(n => M.caseDecouverte(P, n)), "toutes dévoilées");
  M.voirToutesCases(C, P, false);
  assert.ok(!M.caseDecouverte(P, arr), "réglage coupé : l'arrivée redevient cachée");
  S.jouer(C, P, 60, P.cree, S.graine(7));
  console.log("OK : cases par arbre, Thalès en premier, réglage « Voir toutes les cases »");
}
// v53 : un pack de domaine chargé par le joueur (outils/packs.py paquet) se pose comme s'il avait été assemblé.
{
  const os = require("os"), { execFileSync } = require("child_process");
  const f = path.join(os.tmpdir(), "test-musique.pack.json");
  execFileSync("python3", [path.join(__dirname, "packs.py"), "paquet", "musique", f]);
  const paquet = JSON.parse(fs.readFileSync(f, "utf8")); fs.unlinkSync(f);
  assert.equal(paquet.sources.verifiees, paquet.sources.total, "paquet : sources toutes vérifiées");
  // Les données sans Musique, puis Musique chargée en paquet : on retrouve l'assemblage complet.
  const sans = JSON.parse(JSON.stringify(M.filtrerPacks(brut, index, ["musique"])));
  const idx = JSON.parse(JSON.stringify(index));
  idx.packs = idx.packs.filter(m => m.id !== "musique");
  for (const ou of Object.keys(idx.proprietaires)) for (const k of Object.keys(idx.proprietaires[ou])) if (idx.proprietaires[ou][k] === "musique") delete idx.proprietaires[ou][k];
  const v = M.verifierPaquet(sans, idx, paquet);
  assert.deepEqual(v.erreurs, [], "paquet musique accepté");
  assert.ok(v.compte["questions.json/questions"] > 20);
  M.ajouterPaquet(sans, idx, paquet);
  const cles = (d, fi, ch) => ch.reduce((o, k) => o[k], d[fi]).map(x => x.id).sort().join("|");
  for (const [fi, ch] of [["skills.json", ["competences"]], ["questions.json", ["questions"]], ["succes.json", ["succes"]], ["avatar.json", ["savants"]], ["regles.json", ["stats"]]])
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
console.log(`OK : ${packs.length} packs éteints un à un, partie jouée puis reprise sans perte ; parties longues cohérentes avec les packs choisis ; pack additionnel chargé en paquet`);
