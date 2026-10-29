// Tests des packs en jeu (node outils/test_packs.js) : chaque pack s'éteint sans casser le moteur et sans rien perdre.
const assert = require("assert");
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
console.log(`OK : ${packs.length} packs éteints un à un, partie jouée puis reprise sans perte`);
