"""Valide les fichiers de data/ contre schema.json, puis vérifie les liens entre fichiers.

Usage : python3 outils/valider.py   (code de sortie 1 en cas d'erreur)
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

DATA = Path(__file__).resolve().parent.parent / "data"


def charger(nom):
    return json.loads((DATA / nom).read_text(encoding="utf-8"))


def main():
    schema = charger("schema.json")
    erreurs = []
    contenu = {}
    for nom, definition in [("regles.json", "regles"), ("skills.json", "skills"),
                            ("questions.json", "questions"), ("succes.json", "succes")]:
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
    for q in contenu["questions"]["questions"]:
        if q["id"] in ids:
            erreurs.append(f"questions.json : id en double {q['id']}")
        ids.add(q["id"])
        if q["competence"] not in comps:
            erreurs.append(f"questions.json {q['id']} : compétence inconnue")
        par_comp[q["competence"]] = par_comp.get(q["competence"], 0) + 1
        if q["type"] == "qcm" and not 0 <= q["reponse"] < len(q["choix"]):
            erreurs.append(f"questions.json {q['id']} : réponse hors des choix")
    minimum = max(regles["quiz"]["questions_par_quiz"], regles["rappels"]["questions_par_rappel"])
    for c in comps:
        if par_comp.get(c, 0) < minimum:
            erreurs.append(f"questions.json : {c} n'a que {par_comp.get(c, 0)} questions")

    for s in contenu["succes"]["succes"]:
        st = s["condition"].get("stat")
        if st and st not in stats:
            erreurs.append(f"succes.json {s['id']} : stat inconnue {st}")

    if erreurs:
        print("\n".join(erreurs))
        sys.exit(1)
    print(f"OK : {len(stats)} stats, {len(comps)} compétences, {len(ids)} questions, {len(contenu['succes']['succes'])} succès")


if __name__ == "__main__":
    main()
