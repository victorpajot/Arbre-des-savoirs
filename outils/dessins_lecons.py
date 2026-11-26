"""Pose des dessins de leçon (pixel art 48 × 48) dans les masterclass d'un pack.

Chaque pack a son module outils/dessins_<pack>.py avec :
- DESSINS : {id: fonction qui rend une Toile} ;
- ILLUS : {(compétence, chapitre): (id du dessin, indice du paragraphe qui en parle)} ;
- COPIES (facultatif) : {id: (pack, id d'origine)}, dessins d'autres packs repris tels quels.

    python3 outils/dessins_<pack>.py            # écrit packs/<pack>/dessins.json et les champs des chapitres
    python3 outils/dessins_<pack>.py --apercu   # planche PNG dans le dossier courant (dessins-<pack>.png)

Le champ `dessin` n'entre pas dans l'empreinte de verifier_sources.py : pas de réinscription à faire.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import apercu  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ecrire(chemin, donnees):
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=1)
        f.write("\n")


def executer(pack, dessins, illus, copies=None, argv=None):
    argv = sys.argv if argv is None else argv
    images = {k: f().lignes() for k, f in dessins.items()}
    for k, (autre, id_) in (copies or {}).items():
        images[k] = json.load(open(os.path.join(RACINE, "packs", autre, "dessins.json"), encoding="utf-8"))[id_]
    if "--apercu" in argv:
        apercu(images, "dessins-%s.png" % pack, colonnes=6, echelle=6)
        return
    dossier = os.path.join(RACINE, "packs", pack)
    chemin = os.path.join(dossier, "dessins.json")
    tous = json.load(open(chemin, encoding="utf-8")) if os.path.exists(chemin) else {}
    tous.update(images)
    _ecrire(chemin, tous)
    chemin = os.path.join(dossier, "competences.json")
    comps = json.load(open(chemin, encoding="utf-8"))
    poses = 0
    for c in comps:
        for ch in (c.get("masterclass") or {}).get("chapitres", []):
            v = illus.get((c["id"], ch.get("id")))
            if v:
                assert v[0] in images, v[0]
                assert 0 <= v[1] < len(ch["texte"]), (c["id"], ch["id"], v[1])
                ch["dessin"], ch["dessin_apres"] = v
                poses += 1
    assert poses == len(illus), "chapitre introuvable dans ILLUS"
    _ecrire(chemin, comps)
    print(pack, ":", len(images), "dessins,", poses, "chapitres illustrés")
