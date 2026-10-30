"""v26 : la routine de vérification des sources, lancée avant chaque commit (hook .githooks/pre-commit)
et par la compilation GitHub. Demande de Victor (2026-10-28) : rien d'inventé dans le jeu.

Une « information sourcée » est tout élément des data/*.json qui porte un champ `source` (succès, cases, livres,
objets, ennemis, mythes, savants, atomes…). Son empreinte couvre tout son texte.

  - vérifiée : inscrite dans le registre de son pack, packs/<id>/verifications.json, avec la même empreinte, l'URL
    consultée, la date et ce qui a été contrôlé ;
  - sinon (nouvelle, ou modifiée sans nouvelle vérification) : le commit est refusé.

Les extraits de livres doivent en plus porter leur propre `verification` (texte trouvé mot pour mot).

Usage :
  python3 outils/verifier_sources.py                    contrôle (code 1 si un élément n'est pas vérifié)
  python3 outils/verifier_sources.py --liste            liste ce qui reste à vérifier, avec le pack de chaque élément
  python3 outils/verifier_sources.py --inscrire CLE URL "ce qui a été contrôlé"
"""
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DATA = RACINE / "data"
PACKS = RACINE / "packs"


def textes(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for k in sorted(o):
            # Un extrait porte sa propre vérification : il ne remet pas en cause la fiche qui le contient.
            # `reperes` (masterclass) ne fait que recopier des phrases du texte vérifié (contrôlé par valider.py).
            # `repere` (question) est vérifié pour lui-même : il ne remet pas en cause la source de la question.
            if k in ("lot", "verification", "extrait", "reperes", "repere"):
                continue
            yield from textes(o[k])
    elif isinstance(o, list):
        for v in o:
            yield from textes(v)


def empreinte(item):
    return hashlib.sha1("\x1f".join(textes(item)).encode("utf-8")).hexdigest()[:16]


def elements(lire_fichier=None):
    """Toutes les informations sourcées : clé « fichier:chemin:id » → élément. `lire_fichier(nom)` : lire une autre version."""
    out = {}

    def parcourir(o, fichier, chemin, parent):
        # La clé suit le dernier `id` rencontré, pour rester stable quand l'ordre des éléments change.
        if isinstance(o, dict):
            ident = o.get("id", o.get("n", o.get("z")))
            if ident is not None:
                parent, chemin = f"{parent}/{ident}" if parent else str(ident), ""
            if isinstance(o.get("source"), str) and o["source"].strip():
                cle = f"{fichier}:{parent}" + (f":{chemin}" if chemin else "")
                n = 2
                while cle in out:
                    cle = f"{fichier}:{parent}" + (f":{chemin}" if chemin else "") + f"#{n}"
                    n += 1
                out[cle] = o
            for k, v in o.items():
                parcourir(v, fichier, f"{chemin}.{k}" if chemin else k, parent)
        elif isinstance(o, list):
            for v in o:
                parcourir(v, fichier, chemin, parent)

    for f in sorted(DATA.glob("*.json")):
        if f.name == "schema.json":
            continue
        texte = lire_fichier(f.name) if lire_fichier else f.read_text(encoding="utf-8")
        if texte:
            parcourir(json.loads(texte), f.stem, "", "")
    return out


def lire(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def ecrire(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def extraits_sans_verif():
    b = json.loads((DATA / "bibliotheque.json").read_text(encoding="utf-8"))
    mauvais = []
    for l in b["livres"]:
        x = l.get("extrait")
        if x:
            v = x.get("verification") or {}
            if not (str(v.get("url", "")).startswith("https://") and v.get("date") and len(v.get("controle", "")) >= 10):
                mauvais.append(l["id"])
    return mauvais


def proprietaire(cle, index=None):
    """Le pack d'une information sourcée, d'après data/packs.json (clé « fichier:id/… »)."""
    index = index or lire(DATA / "packs.json")
    fichier, ident = cle.split(":")[0] + ".json", cle.split(":")[1].split("/")[0].split("#")[0]
    for ou, proprios in index.get("proprietaires", {}).items():
        if ou.split("/")[0] == fichier and ident in proprios:
            return proprios[ident]
    return "socle"


def registres():
    """Tous les registres des packs, fusionnés : clé → vérification."""
    out = {}
    for f in sorted(PACKS.glob("*/verifications.json")):
        out.update(lire(f))
    return out


def main(args):
    el, verifs = elements(), registres()
    if args[:1] == ["--inscrire"]:
        cle, url, controle = args[1], args[2], " ".join(args[3:])
        if cle not in el:
            sys.exit(f"Clé inconnue : {cle}")
        if not url.startswith("https://") or len(controle) < 10:
            sys.exit("Il faut l'URL consultée (https://) et ce qui a été contrôlé.")
        pack = proprietaire(cle)
        f = PACKS / pack / "verifications.json"
        reg = lire(f)
        reg[cle] = {"empreinte": empreinte(el[cle]), "url": url, "date": date.today().isoformat(), "controle": controle}
        ecrire(f, reg)
        print(f"Vérifié : {cle} (registre du pack {pack})")
        return 0
    ok, refus = 0, []
    for k, v in el.items():
        if k in verifs and verifs[k]["empreinte"] == empreinte(v):
            ok += 1
        else:
            refus.append(k)
    sans = extraits_sans_verif()
    if args[:1] == ["--liste"]:
        index = lire(DATA / "packs.json")
        print("\n".join(f"{k}  [{proprietaire(k, index)}]" for k in refus))
    print(f"Sources : {ok} vérifiées, {len(refus)} nouvelles ou modifiées sans vérification.")
    if refus or sans:
        for k in refus[:40]:
            print("  NON VÉRIFIÉ :", k)
        if len(refus) > 40:
            print(f"  … et {len(refus) - 40} autres")
        for i in sans:
            print("  EXTRAIT SANS VÉRIFICATION :", i)
        print("Vérifie chaque élément sur une source en ligne, puis : python3 outils/verifier_sources.py --inscrire CLE URL \"contrôle\"")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
