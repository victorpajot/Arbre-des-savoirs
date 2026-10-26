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
            ("avatar.json", "avatar"), ("ia.json", "ia"), ("plateau.json", "plateau"), ("frise.json", "frise"),
            ("bibliotheque.json", "bibliotheque")]


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
    conditions += [(f"frise.json {e['id']}", e["condition"]) for e in contenu["frise"]["evenements"]]
    conditions += [(f"bibliotheque.json {l['id']}", l["condition"]) for l in contenu["bibliotheque"]["livres"]]
    nb_cases = len(contenu["plateau"]["cases"])
    for ou, cond in conditions:
        if cond.get("stat") and cond["stat"] not in stats:
            erreurs.append(f"{ou} : stat inconnue {cond['stat']}")
        if cond["type"] == "competence_maitrisee" and cond.get("id") not in comps:
            erreurs.append(f"{ou} : compétence inconnue {cond.get('id')}")
        if cond["type"] == "succes" and cond.get("id") not in succes:
            erreurs.append(f"{ou} : succès inconnu {cond.get('id')}")
        if cond["type"] in ("case_atteinte", "case_visitee") and not 1 <= cond.get("n", 0) <= nb_cases:
            erreurs.append(f"{ou} : case hors du plateau {cond.get('n')}")
        besoin = {"competence_maitrisee": "id", "succes": "id", "branche_complete": "stat", "quiz_parfaits_stat": "stat",
                  "duree_maitrise": "jours", "niveau_stat": "niveau", "toutes_branches": None}.get(cond["type"], "n")
        if besoin and besoin not in cond:
            erreurs.append(f"{ou} : la condition {cond['type']} demande « {besoin} »")

    repliques = contenu["commentaires"]["commentaires"]
    contextes = {c["contexte"] for c in repliques}
    attendus = set(schema["$defs"]["commentaires"]["properties"]["commentaires"]["items"]["properties"]["contexte"]["enum"])
    if attendus - contextes:
        erreurs.append(f"commentaires.json : aucune réplique pour {sorted(attendus - contextes)}")
    if len(repliques) < 200:
        erreurs.append(f"commentaires.json : {len(repliques)} répliques, 200 attendues")
    part = sum(r.get("reference", False) for r in repliques) / len(repliques)
    if part < 0.7:
        erreurs.append(f"commentaires.json : {part:.0%} des répliques citent l'histoire des sciences, 70 % attendus")
    narr = contenu["ia"]
    if attendus - set(narr["expressions"]):
        erreurs.append(f"ia.json : pas d'expression pour {sorted(attendus - set(narr['expressions']))}")
    seuils = [m["seuil"] for m in narr["masques"]]
    if seuils[0] != 0 or seuils != sorted(seuils):
        erreurs.append("ia.json : les seuils des masques doivent partir de 0 et croître")
    for m in narr["masques"]:
        verifier_pixels(f"ia.json {m['id']}", m["base"], narr["taille"], narr["palette"], erreurs)
        for e, img in m["expressions"].items():
            verifier_pixels(f"ia.json {m['id']} {e}", img, narr["taille"], narr["palette"], erreurs)
    if max(seuils) > len(succes):
        erreurs.append(f"ia.json : seuil de masque {max(seuils)} au-delà des {len(succes)} succès")

    pl = contenu["plateau"]
    sprites = set(pl["icones"]) | {o["id"] for o in contenu["objets"]["objets"]}
    for nom, img in pl["icones"].items():
        verifier_pixels(f"plateau.json icône {nom}", img, pl["taille"], pl["palette"], erreurs)
    for i, c in enumerate(pl["cases"], 1):
        if c["n"] != i:
            erreurs.append(f"plateau.json : case {c['id']} numérotée {c['n']}, {i} attendu")
        if c["stat"] not in stats:
            erreurs.append(f"plateau.json {c['id']} : stat inconnue {c['stat']}")
        if c["icone"] not in sprites:
            erreurs.append(f"plateau.json {c['id']} : icône inconnue {c['icone']}")
        sp = c.get("special")
        if sp and sp["type"] in ("avance", "recul", "quarantaine") and "n" not in sp:
            erreurs.append(f"plateau.json {c['id']} : la règle {sp['type']} demande « n »")
        if sp and sp["type"] == "retour_epoque" and not 1 <= sp.get("vers", 0) < i:
            erreurs.append(f"plateau.json {c['id']} : retour d'époque vers une case invalide")
    if pl["regles"]["arrivee"] != len(pl["cases"]):
        erreurs.append("plateau.json : l'arrivée doit être la dernière case")
    for e in pl["epoques"]:
        if e["icone"] not in sprites:
            erreurs.append(f"plateau.json époque {e['id']} : icône inconnue")
    annees = [c["annee"] for c in pl["cases"]]
    if annees != sorted(annees):
        erreurs.append("plateau.json : les cases doivent suivre l'ordre chronologique")

    ev = contenu["frise"]["evenements"]
    if len({e["id"] for e in ev}) != len(ev):
        erreurs.append("frise.json : id en double")
    datees = {e["condition"].get("id") for e in ev if e["condition"]["type"] == "competence_maitrisee"}
    if set(comps) - datees:
        erreurs.append(f"frise.json : compétences sans date {sorted(set(comps) - datees)}")
    for e in ev:
        if "case" not in e and "detail" not in e:
            erreurs.append(f"frise.json {e['id']} : ni case ni détail")

    for l in contenu["bibliotheque"]["livres"]:
        if l["embleme"] not in sprites:
            erreurs.append(f"bibliotheque.json {l['id']} : emblème inconnu {l['embleme']}")
        if l["stat"] not in stats:
            erreurs.append(f"bibliotheque.json {l['id']} : stat inconnue {l['stat']}")
        mots = len(l["resume"]["fr"].split())
        if not 80 <= mots <= 170:
            erreurs.append(f"bibliotheque.json {l['id']} : résumé de {mots} mots")

    cab = contenu["objets"]
    for o in cab["objets"]:
        verifier_pixels(f"objets.json {o['id']}", o["pixels"], cab["taille"], cab["palette"], erreurs)
    av = contenu["avatar"]
    calques = [("corps", av["corps"], ""), ("cheveux", av["cheveux"], "")]
    calques += [(r["id"], r["tenue"], "".join(r["couleurs"])) for r in av["rangs"]]
    for r in av["rangs"]:
        if set(av.get("emplacements", "")) - set(r["couleurs"]):
            erreurs.append(f"avatar.json {r['id']} : couleurs de rang manquantes")
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
          f"{len(cab['objets'])} objets, {len(av['rangs'])} rangs et {len(av['accessoires'])} accessoires d'avatar, "
          f"{len(narr['masques'])} masques, {len(pl['cases'])} cases, {len(ev)} dates, {len(contenu['bibliotheque']['livres'])} livres")


if __name__ == "__main__":
    main()
