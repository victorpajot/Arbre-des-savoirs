"""Valide les fichiers de data/ contre schema.json, puis vérifie les liens entre fichiers.

Usage : python3 outils/valider.py   (code de sortie 1 en cas d'erreur)
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

DATA = Path(__file__).resolve().parent.parent / "data"
FICHIERS = [("regles.json", "regles"), ("skills.json", "skills"), ("questions.json", "questions"),
            ("succes.json", "succes"), ("commentaires.json", "commentaires"), ("objets.json", "objets"),
            ("avatar.json", "avatar")]


def charger(nom):
    return json.loads((DATA / nom).read_text(encoding="utf-8"))


def verifier_pixels(nom, img, taille, palette, erreurs, extra=""):
    larg, haut = taille
    if len(img) != haut or any(len(l) != larg for l in img):
        erreurs.append(f"{nom} : image de {len(img)} lignes, {larg} × {haut} attendu")
    inconnus = set("".join(img)) - set(palette) - set("." + extra)
    if inconnus:
        erreurs.append(f"{nom} : couleurs absentes de la palette {sorted(inconnus)}")


def main():
    schema = charger("schema.json")
    erreurs = []
    contenu = {}
    for nom, definition in FICHIERS:
        doc = charger(nom)
        contenu[definition] = doc
        validateur = Draft202012Validator({**schema, "$ref": f"#/$defs/{definition}"})
        for e in validateur.iter_errors(doc):
            erreurs.append(f"{nom} {'/'.join(map(str, e.absolute_path))} : {e.message}")

    stats = {s["id"] for s in contenu["regles"]["stats"]}
    comps = {c["id"]: c for c in contenu["skills"]["competences"]}
    regles = contenu["regles"]
    for c in comps.values():
        if c["stat"] not in stats:
            erreurs.append(f"skills.json {c['id']} : stat inconnue {c['stat']}")
        for p in c["prerequis"]:
            if p not in comps:
                erreurs.append(f"skills.json {c['id']} : prérequis inconnu {p}")

    ids = set()
    par_comp = {}
    illustrees = 0
    for q in contenu["questions"]["questions"]:
        if q["id"] in ids:
            erreurs.append(f"questions.json : id en double {q['id']}")
        ids.add(q["id"])
        if q["competence"] not in comps:
            erreurs.append(f"questions.json {q['id']} : compétence inconnue")
        par_comp[q["competence"]] = par_comp.get(q["competence"], 0) + 1
        if q["type"] == "qcm" and not 0 <= q["reponse"] < len(q["choix"]):
            erreurs.append(f"questions.json {q['id']} : réponse hors des choix")
        illustrees += "illustration" in q or "illustration_explication" in q
    minimum = max(regles["quiz"]["questions_par_quiz"], regles["rappels"]["questions_par_rappel"])
    for c in comps:
        if par_comp.get(c, 0) < minimum:
            erreurs.append(f"questions.json : {c} n'a que {par_comp.get(c, 0)} questions")

    succes = {s["id"] for s in contenu["succes"]["succes"]}
    conditions = [(f"succes.json {s['id']}", s["condition"]) for s in contenu["succes"]["succes"]]
    conditions += [(f"objets.json {o['id']}", o["condition"]) for o in contenu["objets"]["objets"]]
    conditions += [(f"avatar.json {a['id']}", a["condition"]) for a in contenu["avatar"]["accessoires"]]
    for ou, cond in conditions:
        if cond.get("stat") and cond["stat"] not in stats:
            erreurs.append(f"{ou} : stat inconnue {cond['stat']}")
        if cond["type"] == "competence_maitrisee" and cond.get("id") not in comps:
            erreurs.append(f"{ou} : compétence inconnue {cond.get('id')}")
        if cond["type"] == "succes" and cond.get("id") not in succes:
            erreurs.append(f"{ou} : succès inconnu {cond.get('id')}")
        besoin = {"competence_maitrisee": "id", "succes": "id", "branche_complete": "stat", "quiz_parfaits_stat": "stat",
                  "duree_maitrise": "jours", "niveau_stat": "niveau", "toutes_branches": None}.get(cond["type"], "n")
        if besoin and besoin not in cond:
            erreurs.append(f"{ou} : la condition {cond['type']} demande « {besoin} »")

    contextes = {c["contexte"] for c in contenu["commentaires"]["commentaires"]}
    manquants = set(schema["$defs"]["commentaires"]["properties"]["commentaires"]["items"]["properties"]["contexte"]["enum"]) - contextes
    if manquants:
        erreurs.append(f"commentaires.json : aucune réplique pour {sorted(manquants)}")

    cab = contenu["objets"]
    for o in cab["objets"]:
        verifier_pixels(f"objets.json {o['id']}", o["pixels"], cab["taille"], cab["palette"], erreurs)
    av = contenu["avatar"]
    calques = [("corps", av["corps"], ""), ("cheveux", av["cheveux"], "")]
    calques += [(r["id"], r["tenue"], "".join(r["couleurs"])) for r in av["rangs"]]
    calques += [(a["id"], a["pixels"], "") for a in av["accessoires"]]
    for nom, img, extra in calques:
        verifier_pixels(f"avatar.json {nom}", img, av["taille"], av["palette"], erreurs, extra)
    if av["rangs"][0]["niveau_min"] != 0:
        erreurs.append("avatar.json : le premier rang doit commencer au niveau 0")

    if erreurs:
        print("\n".join(erreurs))
        sys.exit(1)
    print(f"OK : {len(stats)} stats, {len(comps)} compétences, {len(ids)} questions ({illustrees} illustrées), "
          f"{len(succes)} succès, {len(contenu['commentaires']['commentaires'])} répliques, "
          f"{len(cab['objets'])} objets, {len(av['rangs'])} rangs et {len(av['accessoires'])} accessoires d'avatar")


if __name__ == "__main__":
    main()
