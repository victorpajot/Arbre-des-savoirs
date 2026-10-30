"""Valide les fichiers de data/ (assemblés depuis packs/) contre outils/schema.json, puis vérifie les liens entre fichiers.

Usage : python3 outils/valider.py   (code de sortie 1 en cas d'erreur)
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

DATA = Path(__file__).resolve().parent.parent / "data"
SCHEMA = Path(__file__).resolve().parent / "schema.json"
FICHIERS = [("regles.json", "regles"), ("skills.json", "skills"), ("questions.json", "questions"),
            ("succes.json", "succes"), ("commentaires.json", "commentaires"), ("objets.json", "objets"),
            ("avatar.json", "avatar"), ("ia.json", "ia"), ("plateau.json", "plateau"), ("frise.json", "frise"),
            ("bibliotheque.json", "bibliotheque"), ("ennemis.json", "ennemis"), ("atomes.json", "atomes"),
            ("packs.json", "packs")]


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
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
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

    figs = contenu["skills"].get("figures", {})
    for c in comps.values():
        for f in c["fiche"].get("figures", []):
            if f not in figs:
                erreurs.append(f"skills.json {c['id']} : figure inconnue {f}")
        for ch in c.get("masterclass", {}).get("chapitres", []):
            if ch.get("figure") and ch["figure"] not in figs:
                erreurs.append(f"skills.json {c['id']} : figure de masterclass inconnue {ch['figure']}")
            # Les repères d'histoire des quiz recopient mot pour mot une phrase vérifiée du chapitre.
            corps = " ".join(t["fr"] for t in ch["texte"])
            for h in ch.get("reperes", []):
                if h["fr"] not in corps:
                    erreurs.append(f"skills.json {c['id']}/{ch['id']} : repère d'histoire absent du texte du chapitre")
    for q in contenu["questions"]["questions"]:
        if q.get("figure") and q["figure"] not in figs:
            erreurs.append(f"questions.json {q['id']} : figure inconnue {q['figure']}")

    for st in stats:
        rangs = sorted(c["rang"] for c in comps.values() if c["stat"] == st)
        if rangs != list(range(1, 9)):
            erreurs.append(f"skills.json : la branche {st} doit avoir les rangs 1 à 8, elle a {rangs}")

    ids = set()
    enonces = {}
    par_comp = {}
    illustrees = 0
    for q in contenu["questions"]["questions"]:
        if q["id"] in ids:
            erreurs.append(f"questions.json : id en double {q['id']}")
        ids.add(q["id"])
        if q["competence"] not in comps:
            erreurs.append(f"questions.json {q['id']} : compétence inconnue")
        par_comp[q["competence"]] = par_comp.get(q["competence"], 0) + 1
        e = q["enonce"]["fr"] if isinstance(q["enonce"], dict) else q["enonce"]
        if e in enonces:
            erreurs.append(f"questions.json {q['id']} : même énoncé que {enonces[e]}")
        enonces[e] = q["id"]
        if q["type"] == "qcm" and not 0 <= q["reponse"] < len(q["choix"]):
            erreurs.append(f"questions.json {q['id']} : réponse hors des choix")
        illustrees += "illustration" in q or "illustration_explication" in q
    minimum = max(regles["quiz"]["questions_par_quiz"], regles["rappels"]["questions_par_rappel"])
    for c in comps:
        if par_comp.get(c, 0) < minimum:
            erreurs.append(f"questions.json : {c} n'a que {par_comp.get(c, 0)} questions")

    succes = {s["id"] for s in contenu["succes"]["succes"]}
    # v17 : l'illustration de chaque succès renvoie à un dessin qui existe.
    sources = {"objet": {o["id"] for o in contenu["objets"]["objets"]}, "icone": set(contenu["plateau"]["icones"]),
               "dessin": set(contenu["succes"].get("dessins", {})), "ennemi": {e["id"] for e in contenu["ennemis"]["ennemis"]},
               "savant": {x["id"] for x in contenu["avatar"]["savants"]}}
    for s in contenu["succes"]["succes"]:
        il = s["illustration"]
        if il["id"] not in sources[il["type"]]:
            erreurs.append(f"succes.json {s['id']} : illustration inconnue {il['type']} {il['id']}")
    conditions = [(f"succes.json {s['id']}", s["condition"]) for s in contenu["succes"]["succes"]]
    conditions += [(f"objets.json {o['id']}", o["condition"]) for o in contenu["objets"]["objets"]]
    conditions += [(f"avatar.json {a['id']}", a["condition"]) for a in contenu["avatar"]["accessoires"]]
    conditions += [(f"avatar.json {sv['id']}", sv["condition"]) for sv in contenu["avatar"].get("savants", [])]
    conditions += [(f"frise.json {e['id']}", e["condition"]) for e in contenu["frise"]["evenements"]]
    conditions += [(f"bibliotheque.json {l['id']}", l["condition"]) for l in contenu["bibliotheque"]["livres"]]
    conditions += [(f"ia.json {m['id']}", m["condition"]) for m in contenu["ia"]["masques"] if m.get("condition")]
    nb_cases = len(contenu["plateau"]["cases"])
    for ou, cond in conditions:
        if cond.get("stat") and cond["stat"] not in stats:
            erreurs.append(f"{ou} : stat inconnue {cond['stat']}")
        if cond["type"] == "competence_maitrisee" and cond.get("id") not in comps:
            erreurs.append(f"{ou} : compétence inconnue {cond.get('id')}")
        if cond["type"] == "succes" and cond.get("id") not in succes:
            erreurs.append(f"{ou} : succès inconnu {cond.get('id')}")
        if cond["type"] in ("case_atteinte", "case_visitee", "epoque_atteinte") and not 1 <= cond.get("n", 0) <= nb_cases:
            erreurs.append(f"{ou} : case hors du plateau {cond.get('n')}")
        besoin = {"competence_maitrisee": "id", "succes": "id", "ennemi_vaincu": "id", "famille_capturee": "famille", "branche_complete": "stat", "quiz_parfaits_stat": "stat",
                  "duree_maitrise": "jours", "niveau_stat": "niveau", "rang_maitrise": "rang", "toutes_branches": None}.get(cond["type"], "n")
        if besoin and besoin not in cond:
            erreurs.append(f"{ou} : la condition {cond['type']} demande « {besoin} »")

    repliques = contenu["commentaires"]["commentaires"]
    contextes = {c["contexte"] for c in repliques}
    attendus = set(schema["$defs"]["contexte"]["anyOf"][0]["enum"])
    # Packs : chaque arbre a ses propres répliques d'annonce, de réussite et d'échec.
    for st in stats:
        for moment, mini in (("jouer", 3), ("reussi", 4), ("rate", 4)):
            nb = sum(1 for r in repliques if r["contexte"] == f"theme_{moment}@{st}")
            if nb < mini:
                erreurs.append(f"commentaires.json : {nb} répliques theme_{moment}@{st}, {mini} attendues")
    for r in repliques:
        if "@" in r["contexte"] and r["contexte"].split("@")[1] not in stats:
            erreurs.append(f"commentaires.json {r['id']} : arbre inconnu {r['contexte']}")
    if attendus - contextes:
        erreurs.append(f"commentaires.json : aucune réplique pour {sorted(attendus - contextes)}")
    if len(repliques) < 200:
        erreurs.append(f"commentaires.json : {len(repliques)} répliques, 200 attendues")
    # v27 : furieuse, l'IA ne fait plus de culture ; ces répliques sèches ne comptent pas dans la part sourcée.
    # Fil « Basile » : les répliques du mode enfant non plus (des mots simples pour un enfant de six ans).
    cultivees = [r for r in repliques if not r["contexte"].startswith(("furieuse_", "enfant_")) and r["contexte"] not in ("faveur_nulle", "faveur_remontee", "mur_force", "mur_libere")]
    part = sum(r.get("reference", False) for r in cultivees) / len(cultivees)
    if part < 0.7:
        erreurs.append(f"commentaires.json : {part:.0%} des répliques citent l'histoire des sciences, 70 % attendus")
    narr = contenu["ia"]
    if attendus - set(narr["expressions"]):
        erreurs.append(f"ia.json : pas d'expression pour {sorted(attendus - set(narr['expressions']))}")
    if narr["masques"][0].get("condition"):
        erreurs.append("ia.json : le premier masque doit être porté dès le début, sans condition")
    seuils = [m["condition"]["n"] for m in narr["masques"] if m.get("condition", {}).get("type") == "succes_obtenus"]
    precis = [m for m in narr["masques"] if m.get("condition", {}).get("type") in ("succes", "tours_plateau")]
    if len(seuils) + 1 < 12 or len(precis) < 12:
        erreurs.append(f"ia.json : {len(seuils) + 1} masques par paliers et {len(precis)} par succès précis, 12 de chaque attendus")
    if seuils != sorted(seuils):
        erreurs.append("ia.json : les paliers des masques doivent croître")
    for m in narr["masques"]:
        verifier_pixels(f"ia.json {m['id']}", m["base"], narr["taille"], narr["palette"], erreurs)
        for e, img in m["expressions"].items():
            verifier_pixels(f"ia.json {m['id']} {e}", img, narr["taille"], narr["palette"], erreurs)
    if seuils and max(seuils) > len(succes):
        erreurs.append(f"ia.json : seuil de masque {max(seuils)} au-delà des {len(succes)} succès")

    pl = contenu["plateau"]
    sprites = set(pl["icones"]) | {o["id"] for o in contenu["objets"]["objets"]} | set(contenu["succes"].get("dessins", {}))
    for nom, img in pl["icones"].items():
        verifier_pixels(f"plateau.json icône {nom}", img, pl["taille"], pl["palette"], erreurs)
    en = contenu["ennemis"]
    ids_en = {e["id"] for e in en["ennemis"]}
    for e in en["ennemis"]:
        verifier_pixels(f"ennemis.json {e['id']}", e["base"], [40, 48], contenu["avatar"]["palette"], erreurs, "!X*~Z+Q")
        verifier_pixels(f"ennemis.json {e['id']} cheveux", e["cheveux"], [40, 48], contenu["avatar"]["palette"], erreurs)
    for n, e in en["placement"].items():
        if e not in ids_en:
            erreurs.append(f"ennemis.json : ennemi inconnu {e} case {n}")
        k = next((c for c in pl["cases"] if c["n"] == int(n)), None)
        if not k or int(n) == 1 or k.get("arrivee") or k.get("special"):
            erreurs.append(f"ennemis.json : case {n} interdite (départ, arrivée ou case spéciale)")
    if en["reserve"] not in ids_en or en["reserve"] in en["placement"].values():
        erreurs.append("ennemis.json : réserve invalide")
    for e in ids_en:
        nb = sum(1 for m in en["mythes"] if m["ennemi"] == e)
        if nb < en["questions_par_duel"]:
            erreurs.append(f"ennemis.json : {e} n'a que {nb} affirmations")
    for m in en["mythes"]:
        if m["ennemi"] not in ids_en:
            erreurs.append(f"ennemis.json {m['id']} : ennemi inconnu")
    for s in contenu["succes"]["succes"]:
        if s["condition"]["type"] == "ennemi_vaincu" and s["condition"]["id"] not in ids_en:
            erreurs.append(f"succes.json {s['id']} : ennemi inconnu")
    # v9 : atomes du jeu de Mendeleïev.
    at = contenu["atomes"]
    for i, e in enumerate(at["elements"], 1):
        if e["z"] != i:
            erreurs.append(f"atomes.json : {e['symbole']} numéroté {e['z']}, {i} attendu")
        if e["famille"] not in at["familles"]:
            erreurs.append(f"atomes.json {e['symbole']} : famille inconnue {e['famille']}")
        if e["stable"] != (not float(e["masse"]).is_integer()):
            erreurs.append(f"atomes.json {e['symbole']} : masse entière réservée aux éléments sans isotope stable")
    if len({e["symbole"] for e in at["elements"]}) != len(at["elements"]):
        erreurs.append("atomes.json : deux éléments avec le même symbole")
    lieux = [o["fr"] for e in at["elements"] for o in e["ou"]]
    if len(set(lieux)) != len(lieux):
        erreurs.append("atomes.json : un même lieu sert à deux éléments, la question « où » serait ambiguë")
    for s in contenu["succes"]["succes"]:
        cond = s["condition"]
        if cond["type"] == "famille_capturee" and cond["famille"] not in at["familles"]:
            erreurs.append(f"succes.json {s['id']} : famille inconnue")
    if not any(c.get("special", {}).get("type") == "mendeleiev" for c in pl["cases"]):
        erreurs.append("plateau.json : aucune case Mendeleïev")
    # v36 : chaque arbre apporte ses cases ; le numéro est l'identité d'une case, unique, pas sa place dans le tour.
    numeros = [c["n"] for c in pl["cases"]]
    if len(set(numeros)) != len(numeros):
        erreurs.append("plateau.json : deux cases portent le même numéro")
    annee_de = {c["n"]: c["annee"] for c in pl["cases"]}
    for c in pl["cases"]:
        i = c["n"]
        if c["stat"] not in stats:
            erreurs.append(f"plateau.json {c['id']} : stat inconnue {c['stat']}")
        if c["icone"] not in sprites:
            erreurs.append(f"plateau.json {c['id']} : icône inconnue {c['icone']}")
        sp = c.get("special")
        if sp and sp["type"] in ("avance", "recul", "quarantaine") and "n" not in sp:
            erreurs.append(f"plateau.json {c['id']} : la règle {sp['type']} demande « n »")
        if sp and sp["type"] in ("retour_epoque", "teleport") and not annee_de.get(sp.get("vers"), c["annee"] + 1) <= c["annee"]:
            erreurs.append(f"plateau.json {c['id']} : retour d'époque vers une case invalide")
    arrivees = [c for c in pl["cases"] if c.get("arrivee")]
    if len(arrivees) != 1 or arrivees[0]["annee"] != max(annee_de.values()):
        erreurs.append("plateau.json : une seule case d'arrivée (« arrivee »: true), la plus récente")
    for e in pl["epoques"]:
        if e["icone"] not in sprites:
            erreurs.append(f"plateau.json époque {e['id']} : icône inconnue")

    objets_ids = {o["id"] for o in contenu["objets"]["objets"]}
    for o in contenu["plateau"].get("objectifs", []):
        if o["relique"] not in objets_ids:
            erreurs.append(f"plateau.json objectif {o['tour']} : relique inconnue {o['relique']}")
    ev = contenu["frise"]["evenements"]
    if len({e["id"] for e in ev}) != len(ev):
        erreurs.append("frise.json : id en double")
    datees = {e["condition"].get("id") for e in ev if e["condition"]["type"] == "competence_maitrisee"}
    if set(comps) - datees:
        erreurs.append(f"frise.json : compétences sans date {sorted(set(comps) - datees)}")
    for e in ev:
        if "case" not in e and "detail" not in e:
            erreurs.append(f"frise.json {e['id']} : ni case ni détail")

    rattachees = [l["competence"] for l in contenu["bibliotheque"]["livres"]]
    if set(rattachees) != set(comps):
        erreurs.append(f"bibliotheque.json : il faut au moins un livre par compétence ({len(set(rattachees))} sur {len(comps)})")
    for l in contenu["bibliotheque"]["livres"]:
        if l["embleme"] not in sprites and l["embleme"] not in contenu["succes"].get("dessins", {}):
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
    for sv in av.get("savants", []):
        calques += [(sv["id"], sv["base"], "".join(sv["couleurs"])), (sv["id"] + " cheveux", sv["cheveux"], "")]
    if len(av.get("savants", [])) < 20:
        erreurs.append(f"avatar.json : {len(av.get('savants', []))} savants, 20 attendus")
    for nom, img, extra in calques:
        verifier_pixels(f"avatar.json {nom}", img, av["taille"], av["palette"], erreurs, extra)
    if av["rangs"][0]["niveau_min"] != 0:
        erreurs.append("avatar.json : le premier rang doit commencer au niveau 0")

    # v18 : le thème de chaque chose est un arbre qui existe.
    a_theme = [("succes.json", contenu["succes"]["succes"]), ("objets.json", contenu["objets"]["objets"]),
               ("avatar.json", av["savants"] + av["accessoires"] + av.get("tenues_farce", [])), ("ia.json", narr["masques"]),
               ("ennemis.json", en["ennemis"])]
    for nom, liste in a_theme:
        for x in liste:
            if "theme" in x and x["theme"] not in stats:
                erreurs.append(f"{nom} {x['id']} : thème inconnu {x['theme']}")
    if at["theme"] not in stats:
        erreurs.append(f"atomes.json : thème inconnu {at['theme']}")

    # v7 : chaque arbre hors fondamentaux s'ouvre par un succès de pionnier.
    fond = set(contenu["regles"].get("arbres_fondamentaux", []))
    ouverts = {x["ouvre"] for x in contenu["succes"]["succes"] if "ouvre" in x}
    ids_stats = {s["id"] for s in contenu["regles"]["stats"]}
    if fond and (ids_stats - fond - ouverts):
        erreurs.append(f"succes.json : aucun pionnier n'ouvre {sorted(ids_stats - fond - ouverts)}")
    if (fond | ouverts) - ids_stats:
        erreurs.append(f"arbres inconnus : {sorted((fond | ouverts) - ids_stats)}")
    if erreurs:
        print("\n".join(erreurs))
        sys.exit(1)
    print(f"OK : {len(stats)} stats, {len(comps)} compétences, {len(ids)} questions ({illustrees} illustrées), "
          f"{len(succes)} succès, {len(contenu['commentaires']['commentaires'])} répliques, "
          f"{len(cab['objets'])} objets, {len(av['rangs'])} rangs et {len(av['accessoires'])} accessoires d'avatar, {len(av.get('savants', []))} savants, "
          f"{len(narr['masques'])} masques, {len(pl['cases'])} cases, {len(ev)} dates, {len(contenu['bibliotheque']['livres'])} livres, {len(contenu['ennemis']['ennemis'])} ennemis, {len(contenu['ennemis']['mythes'])} affirmations de duel")


if __name__ == "__main__":
    main()
