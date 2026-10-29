"""Les packs : chaque domaine de savoir, chaque jeu du plateau et le socle commun vivent dans packs/<id>/.

    python3 outils/packs.py assembler        fusionne les packs dans data/ (ce que lit le jeu)
    python3 outils/packs.py verifier [id…]   contrôle les packs (tous par défaut) sans rien écrire
    python3 outils/packs.py liste            liste les packs et ce qu'ils contiennent

Un pack, c'est un dossier :
    pack.json             le manifeste (id, sorte, nom, version, requiert…)
    arbres.json, competences.json, questions.json…   un fichier par type de contenu (EMPLACEMENTS)
    donnees/<fichier>.json  un fragment brut d'un fichier de data/ (socle et packs de jeu seulement)
    verifications.json    le registre des sources contrôlées en ligne (outils/verifier_sources.py)

Les packs JSON sont la seule source du contenu : data/ est un produit, régénéré par « assembler ».
Le guide pour écrire un pack : packs/LISEZMOI-IA.md.
"""
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PACKS = RACINE / "packs"
DATA = RACINE / "data"

# Les fichiers que lit le jeu, dans l'ordre où index.html les charge.
FICHIERS_DATA = ["regles.json", "skills.json", "questions.json", "succes.json", "commentaires.json", "objets.json",
                 "avatar.json", "ia.json", "plateau.json", "frise.json", "bibliotheque.json", "ennemis.json", "atomes.json"]

# Fichier d'un pack → (fichier de data, chemin dans ce fichier). Une liste s'ajoute à la liste, un dictionnaire au dictionnaire.
EMPLACEMENTS = {
    "arbres.json": ("regles.json", ("stats",)),
    "competences.json": ("skills.json", ("competences",)),
    "figures.json": ("skills.json", ("figures",)),
    "questions.json": ("questions.json", ("questions",)),
    "succes.json": ("succes.json", ("succes",)),
    "dessins.json": ("succes.json", ("dessins",)),
    "objets.json": ("objets.json", ("objets",)),
    "savants.json": ("avatar.json", ("savants",)),
    "accessoires.json": ("avatar.json", ("accessoires",)),
    "tenues.json": ("avatar.json", ("tenues_farce",)),
    "masques.json": ("ia.json", ("masques",)),
    "livres.json": ("bibliotheque.json", ("livres",)),
    "frise.json": ("frise.json", ("evenements",)),
    "repliques.json": ("commentaires.json", ("commentaires",)),
    "apartes.json": ("commentaires.json", ("apartes",)),
    "piques.json": ("ia.json", ("credits", "piques")),
    "cases.json": ("plateau.json", ("competences_cases",)),
    "ennemis.json": ("ennemis.json", ("ennemis",)),
    "mythes.json": ("ennemis.json", ("mythes",)),
    "atomes.json": ("atomes.json", ("elements",)),
    "boutique.json": ("ia.json", ("credits", "boutique", "articles")),
}
PAR_CHEMIN = {(f, c): nom for nom, (f, c) in EMPLACEMENTS.items()}
AUTRES = {"pack.json", "verifications.json", "ordre.json", "portraits.json", "LISEZMOI.md"}
SORTES = ("socle", "domaine", "jeu")

# v6 : le butin est réparti en 7 lots, un par tour du plateau ; le lot N ne tombe qu'à partir du tour N.
LOTS = 7
# Les listes que le jeu lit dans un ordre précis.
TRIS = {("bibliotheque.json", ("livres",)): lambda x: x["annee"]}


class ErreurPack(Exception):
    pass


def lire(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def ecrire(p, d):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def cle(x):
    """L'identifiant d'un élément de liste : son id, le numéro d'une case, le numéro atomique, ou le texte lui-même."""
    if isinstance(x, dict):
        for k in ("id", "n", "z"):
            if k in x:
                return str(x[k])
        return None
    return x if isinstance(x, str) else None


# --- Lecture des packs ---------------------------------------------------------------------------------------------

def manifeste(dossier):
    m = lire(dossier / "pack.json")
    m.setdefault("requiert", [])
    m.setdefault("ordre", 1000)
    return m


def tous(dossier=PACKS):
    """Les packs présents, socle d'abord puis par ordre (ordre, id)."""
    # Un dossier dont le nom commence par « _ » (packs/_modele) n'est pas un pack.
    packs = [manifeste(d) | {"_dossier": d} for d in sorted(dossier.iterdir())
             if (d / "pack.json").exists() and not d.name.startswith("_")]
    return sorted(packs, key=lambda m: (m.get("sorte") != "socle", m["ordre"], m["id"]))


def fragments(m):
    """Ce que le pack ajoute à data/ : liste de (fichier de data, fragment, nom du fichier du pack)."""
    d, out = m["_dossier"], []
    # Les fragments bruts d'abord : ils donnent l'ordre des clés de chaque fichier de data/.
    for f in sorted((d / "donnees").glob("*.json")) if (d / "donnees").exists() else []:
        if f.name not in FICHIERS_DATA:
            raise ErreurPack(f"{m['id']} : donnees/{f.name} ne correspond à aucun fichier de data/")
        out.append((f.name, lire(f), "donnees/" + f.name))
    for f in sorted(d.glob("*.json")):
        if f.name in AUTRES:
            continue
        if f.name not in EMPLACEMENTS:
            raise ErreurPack(f"{m['id']} : fichier inconnu {f.name} (voir EMPLACEMENTS dans outils/packs.py)")
        fichier, chemin = EMPLACEMENTS[f.name]
        frag = lire(f)
        for k in reversed(chemin):
            frag = {k: frag}
        out.append((fichier, frag, f.name))
    return out


# --- Fusion --------------------------------------------------------------------------------------------------------

def fusionner(cible, frag, pack, chemin, proprietaires, fichier):
    for k, v in frag.items():
        ch = chemin + (k,)
        if k not in cible:
            cible[k] = [] if isinstance(v, list) else {} if isinstance(v, dict) else v
            if not isinstance(v, (list, dict)):
                continue
        a = cible[k]
        if isinstance(a, dict) and isinstance(v, dict):
            fusionner(a, v, pack, ch, proprietaires, fichier)
        elif isinstance(a, list) and isinstance(v, list):
            if pack != "socle":
                p = proprietaires.setdefault(fichier + "/" + "/".join(ch), {})
                for x in v:
                    c = cle(x)
                    if c is not None and isinstance(x, dict):
                        p[c] = pack
            a.extend(v)
        elif a != v:
            raise ErreurPack(f"{pack} : {fichier} › {'/'.join(ch)} vaut déjà {json.dumps(a, ensure_ascii=False)[:60]}")


def doublons(donnees):
    """Deux éléments d'une même liste ne partagent jamais leur identifiant."""
    erreurs = []

    def voir(o, ou):
        if isinstance(o, dict):
            for k, v in o.items():
                voir(v, ou + "/" + k)
        elif isinstance(o, list) and o and isinstance(o[0], dict):
            vus = set()
            for x in o:
                c = cle(x)
                if c is None:
                    continue
                if c in vus:
                    erreurs.append(f"{ou} : identifiant « {c} » en double")
                vus.add(c)
    for f, d in donnees.items():
        voir(d, f)
    return erreurs


def poser_lots(donnees):
    """Range dans un lot chaque objet, livre, accessoire et masque qui n'en a pas encore, selon la difficulté de sa
    condition. Les éléments déjà rangés gardent le leur : ajouter un pack ne déplace pas le butin existant."""
    comps = {k["id"]: k["rang"] for k in donnees["skills.json"]["competences"]}
    succes = {x["id"]: x for x in donnees["succes.json"]["succes"]}

    def difficulte(cond, prof=0):
        if not cond or prof > 4:
            return 0
        t = cond["type"]
        if t == "competence_maitrisee":
            return comps.get(cond["id"], 4)
        if t in ("case_atteinte", "case_visitee", "epoque_atteinte"):
            return cond["n"] / 9
        if t == "succes":
            return difficulte(succes[cond["id"]]["condition"], prof + 1) if cond["id"] in succes else 3
        if t == "succes_obtenus":
            return cond["n"] / 11
        if t == "tours_plateau":
            return 1 + cond["n"]
        if t == "branche_complete":
            return 4.5
        return 3

    familles = [(donnees["objets.json"]["objets"], lambda x: x["condition"]["type"] != "tours_plateau"),
                (donnees["bibliotheque.json"]["livres"], lambda x: True),
                (donnees["avatar.json"]["accessoires"], lambda x: True),
                (donnees["ia.json"]["masques"], lambda x: "condition" in x)]
    for liste, eligible in familles:
        elus = [x for x in liste if eligible(x)]
        tries = sorted(enumerate(elus), key=lambda p: (difficulte(p[1].get("condition")), p[0]))
        for rang, (_, x) in enumerate(tries):
            x.setdefault("lot", 1 + rang * LOTS // len(tries))


def assembler(packs=None, ecrire_data=True):
    """Fusionne les packs ; renvoie (données par fichier de data, index des packs). Lève ErreurPack au moindre conflit."""
    packs = packs if packs is not None else tous()
    if not packs or packs[0].get("sorte") != "socle":
        raise ErreurPack("le pack socle est introuvable")
    donnees, proprietaires, fondamentaux = {f: {} for f in FICHIERS_DATA}, {}, []
    for m in packs:
        for fichier, frag, _ in fragments(m):
            if fichier == "regles.json" and "stats" in frag:
                # Un arbre ouvert dès le départ le dit lui-même ; regles.arbres_fondamentaux en est la liste.
                frag = {**frag, "stats": [{k: v for k, v in s.items() if k != "fondamental"} for s in frag["stats"]]}
                fondamentaux += [s["id"] for s in lire_liste(m, "arbres.json") if s.get("fondamental")]
            fusionner(donnees[fichier], frag, m["id"], (), proprietaires, fichier)
    donnees["regles.json"]["arbres_fondamentaux"] = fondamentaux
    # L'ordre historique des listes (socle/ordre.json) : le jeu prend parfois le premier élément qui convient, il ne doit
    # donc pas changer d'un assemblage à l'autre. Ce qui n'y figure pas suit, dans l'ordre des packs.
    ordre = packs[0]["_dossier"] / "ordre.json"
    for ou, cles in (lire(ordre).items() if ordre.exists() else []):
        fichier, *chemin = ou.split("/")
        o, rang = obtenir(donnees[fichier], chemin), {c: i for i, c in enumerate(cles)}
        if isinstance(o, list):
            o.sort(key=lambda x: rang.get(cle(x), len(rang)))
        elif isinstance(o, dict):
            tries = sorted(o.items(), key=lambda kv: rang.get(kv[0], len(rang)))
            o.clear()
            o.update(tries)
    for (fichier, chemin), cle_tri in TRIS.items():
        o = donnees[fichier]
        for k in chemin[:-1]:
            o = o[k]
        o[chemin[-1]].sort(key=cle_tri)
    poser_lots(donnees)
    erreurs = doublons(donnees)
    if erreurs:
        raise ErreurPack("\n".join(erreurs))
    # Un pack de jeu possède ses fichiers de data/ en entier (atomes.json…) : éteint en jeu, le fichier disparaît.
    index = {"format": 1,
             "packs": [{k: v for k, v in m.items() if not k.startswith("_")}
                       | ({"fichiers": [n.split("/")[1] for _, _, n in fragments(m) if n.startswith("donnees/")]} if m.get("sorte") == "jeu" else {})
                       for m in packs],
             "proprietaires": proprietaires}
    if ecrire_data:
        for f, d in donnees.items():
            ecrire(DATA / f, ordonner(f, d))
        ecrire(DATA / "packs.json", index)
    return donnees, index


def obtenir(o, chemin):
    for k in chemin:
        if not isinstance(o, dict) or k not in o:
            return None
        o = o[k]
    return o


def lire_liste(m, nom):
    f = m["_dossier"] / nom
    return lire(f) if f.exists() else []


# Les clés de premier niveau de chaque fichier de data/ dans un ordre stable (« format » d'abord), pour des diffs lisibles.
def ordonner(fichier, d):
    tete = {k: d[k] for k in ("format",) if k in d}
    return tete | {k: v for k, v in d.items() if k not in tete}


# --- Vérification --------------------------------------------------------------------------------------------------

CHAMPS_MANIFESTE = {"format": int, "id": str, "sorte": str, "version": str, "nom": dict, "description": dict,
                    "auteurs": list, "licence": str, "langue_source": str}


def verifier(packs=None, cibles=None):
    """Renvoie la liste des erreurs, chacune dite pour être corrigée sans autre aide."""
    packs = packs if packs is not None else tous()
    ids = {m["id"]: m for m in packs}
    erreurs = []

    def err(m, msg):
        erreurs.append(f"[{m['id']}] {msg}")

    for m in packs:
        if cibles and m["_dossier"].name not in cibles:
            continue
        for k, t in CHAMPS_MANIFESTE.items():
            if not isinstance(m.get(k), t):
                err(m, f"pack.json : champ « {k} » manquant ou du mauvais type (attendu : {t.__name__})")
        if m.get("id") != m["_dossier"].name:
            err(m, f"pack.json : l'id « {m.get('id')} » doit être le nom du dossier « {m['_dossier'].name} »")
        if not re.fullmatch(r"[a-z][a-z0-9-]*", str(m.get("id", ""))):
            err(m, "pack.json : l'id ne contient que des minuscules sans accent, des chiffres et des tirets")
        if m.get("sorte") not in SORTES:
            err(m, f"pack.json : « sorte » vaut {' ou '.join(SORTES)}")
        if not re.fullmatch(r"\d+\.\d+\.\d+", str(m.get("version", ""))):
            err(m, "pack.json : « version » s'écrit 1.0.0")
        if "fr" not in m.get("nom", {}):
            err(m, "pack.json : « nom » doit avoir au moins le français, {\"fr\": \"…\"}")
        for r in m["requiert"]:
            if r not in ids:
                err(m, f"pack.json : requiert le pack « {r} », absent de packs/")
        if m.get("sorte") != "socle" and "socle" not in m["requiert"]:
            err(m, "pack.json : tout pack requiert « socle »")
        try:
            frs = fragments(m)
        except ErreurPack as e:
            erreurs.append(str(e))
            continue
        if m.get("sorte") == "domaine" and any(n.startswith("donnees/") for _, _, n in frs):
            err(m, "un pack domaine n'a pas de dossier donnees/ : seulement les fichiers de EMPLACEMENTS")
        erreurs += verifier_contenu(m, ids)
        erreurs += completude(m)
    erreurs += cycles(packs)
    if not erreurs:
        try:
            assembler(packs, ecrire_data=False)
        except ErreurPack as e:
            erreurs.append(f"[assemblage] {e}")
    return erreurs


def accessibles(m, ids):
    """Le pack et tout ce qu'il requiert, directement ou non."""
    vus, pile = set(), [m["id"]]
    while pile:
        p = pile.pop()
        if p in vus or p not in ids:
            continue
        vus.add(p)
        pile += ids[p]["requiert"]
    return vus


def cycles(packs):
    ids = {m["id"]: m for m in packs}
    return [f"[{m['id']}] dépendance circulaire" for m in packs
            if any(m["id"] in accessibles(ids[r], ids) for r in m["requiert"] if r in ids)]


def verifier_contenu(m, ids):
    """Les liens d'un pack ne visent que lui-même et les packs qu'il requiert."""
    erreurs = []
    vus = accessibles(m, ids)
    arbres, comps, succes = set(), set(), set()
    for p in vus:
        d = ids[p]
        arbres |= {s["id"] for s in lire_liste(d, "arbres.json")}
        comps |= {c["id"] for c in lire_liste(d, "competences.json")}
        succes |= {s["id"] for s in lire_liste(d, "succes.json")}
    if m.get("sorte") == "socle":
        return []  # le socle fait référence aux arbres officiels par leur thème : liens souples, vérifiés après assemblage
    pre = m.get("prefixe")
    pre = tuple(p + "." for p in ([pre] if isinstance(pre, str) else pre or []))
    for c in lire_liste(m, "competences.json"):
        if c.get("stat") not in arbres:
            erreurs.append(f"[{m['id']}] competences.json › {c.get('id')} : arbre « {c.get('stat')} » inconnu (déclare-le dans arbres.json ou requiers son pack)")
        for r in c.get("prerequis", []):
            if r not in comps:
                erreurs.append(f"[{m['id']}] competences.json › {c['id']} : prérequis « {r} » introuvable dans ce pack ni ceux qu'il requiert")
        if pre and not (c["id"].startswith(pre) or c["id"] + "." in pre):
            erreurs.append(f"[{m['id']}] competences.json › {c['id']} : l'id commence par le préfixe du pack « {pre[0]} »")
    for q in lire_liste(m, "questions.json"):
        if q.get("competence") not in comps:
            erreurs.append(f"[{m['id']}] questions.json › {q.get('id')} : compétence « {q.get('competence')} » introuvable")
        if pre and not str(q.get("id", "")).startswith(pre):
            erreurs.append(f"[{m['id']}] questions.json › {q.get('id')} : l'id commence par le préfixe du pack « {pre[0]} »")
    # Le thème (et la couleur d'un livre ou d'une date) est un lien souple : il peut viser l'arbre de n'importe quel pack
    # présent ; si ce pack est désactivé, le jeu prend un ton général.
    tous_arbres = {s["id"] for d in ids.values() for s in lire_liste(d, "arbres.json")}
    for nom in ("succes.json", "objets.json", "savants.json", "accessoires.json", "masques.json", "tenues.json", "ennemis.json"):
        for x in lire_liste(m, nom):
            if "theme" in x and x["theme"] not in tous_arbres:
                erreurs.append(f"[{m['id']}] {nom} › {x.get('id')} : thème « {x['theme']} » inconnu (l'id d'un arbre déclaré dans un arbres.json)")
            erreurs += liens_condition(m, nom, x.get("id"), x.get("condition"), comps, arbres, succes)
    for nom in ("livres.json", "frise.json"):
        for x in lire_liste(m, nom):
            if x.get("stat") not in tous_arbres:
                erreurs.append(f"[{m['id']}] {nom} › {x.get('id')} : arbre « {x.get('stat')} » inconnu")
            if "competence" in x and x["competence"] not in comps:
                erreurs.append(f"[{m['id']}] {nom} › {x.get('id')} : compétence « {x['competence']} » introuvable")
            erreurs += liens_condition(m, nom, x.get("id"), x.get("condition"), comps, arbres, succes)
    for k, v in (lire(m["_dossier"] / "cases.json").items() if (m["_dossier"] / "cases.json").exists() else []):
        for c in v:
            if c not in comps:
                erreurs.append(f"[{m['id']}] cases.json › case {k} : compétence « {c} » introuvable")
    for r in lire_liste(m, "repliques.json"):
        ctx = r.get("contexte", "")
        if "@" in ctx and ctx.split("@")[1] not in arbres:
            erreurs.append(f"[{m['id']}] repliques.json › {r.get('id')} : arbre « {ctx.split('@')[1]} » inconnu")
    return erreurs


QUESTIONS_MIN = 10
REPLIQUES_MIN = {"theme_jouer": 3, "theme_reussi": 4, "theme_rate": 4}


def completude(m):
    """Ce qu'un arbre doit apporter pour tenir sa place dans le jeu (voir packs/LISEZMOI-IA.md, « Liste de contrôle »)."""
    erreurs = []
    if m.get("sorte") != "domaine":
        return erreurs
    comps = lire_liste(m, "competences.json")
    questions = lire_liste(m, "questions.json")
    livres = lire_liste(m, "livres.json")
    dates = lire_liste(m, "frise.json")
    succes = lire_liste(m, "succes.json")
    savants = lire_liste(m, "savants.json")
    repliques = lire_liste(m, "repliques.json")
    cases = lire(m["_dossier"] / "cases.json") if (m["_dossier"] / "cases.json").exists() else {}

    def err(msg):
        erreurs.append(f"[{m['id']}] complétude : {msg}")

    def maitrise(x, cid):
        c = x.get("condition") or {}
        return c.get("type") == "competence_maitrisee" and c.get("id") == cid
    for a in lire_liste(m, "arbres.json"):
        st = a["id"]
        siennes = [c for c in comps if c.get("stat") == st]
        rangs = sorted(c.get("rang") for c in siennes)
        if rangs != list(range(1, 9)):
            err(f"l'arbre « {st} » a 8 compétences, une par rang de 1 à 8 (il a les rangs {rangs})")
        for c in siennes:
            n = sum(q.get("competence") == c["id"] for q in questions)
            if n < QUESTIONS_MIN:
                err(f"{c['id']} : {n} questions, il en faut au moins {QUESTIONS_MIN} (questions.json)")
            if not any(l.get("competence") == c["id"] for l in livres):
                err(f"{c['id']} : aucun livre ne s'y rattache (livres.json, champ « competence »)")
            if not any(maitrise(d, c["id"]) for d in dates):
                err(f"{c['id']} : aucune date de la frise ne se débloque en la maîtrisant (frise.json)")
            if not any(maitrise(x, c["id"]) for x in succes):
                err(f"{c['id']} : aucun succès ne se gagne en la maîtrisant (succes.json)")
        if not a.get("fondamental") and not any(x.get("ouvre") == st for x in succes):
            err(f"l'arbre « {st} » s'ouvre par un succès de pionnier (succes.json, champ « ouvre »), sauf s'il est « fondamental »")
        if not any(x.get("theme") == st for x in savants):
            err(f"l'arbre « {st} » a au moins un savant jouable (savants.json, « theme »: « {st} »)")
        for ctx, n in REPLIQUES_MIN.items():
            k = sum(r.get("contexte") == f"{ctx}@{st}" for r in repliques)
            if k < n:
                err(f"l'arbre « {st} » a {k} répliques « {ctx}@{st} », il en faut {n} (repliques.json)")
        ids = {c["id"] for c in siennes}
        if not any(set(v) & ids for v in cases.values()):
            err(f"l'arbre « {st} » est évoqué par au moins une case du plateau (cases.json)")
    return erreurs


def liens_condition(m, nom, ident, cond, comps, arbres, succes):
    if not isinstance(cond, dict):
        return []
    t, out = cond.get("type"), []
    if t == "competence_maitrisee" and cond.get("id") not in comps:
        out.append(f"[{m['id']}] {nom} › {ident} : la condition vise la compétence « {cond.get('id')} », introuvable")
    if t == "succes" and cond.get("id") not in succes:
        out.append(f"[{m['id']}] {nom} › {ident} : la condition vise le succès « {cond.get('id')} », introuvable")
    if t in ("branche_complete", "quiz_parfaits_stat", "niveau_stat") and cond.get("stat", cond.get("id")) not in arbres:
        out.append(f"[{m['id']}] {nom} › {ident} : la condition vise l'arbre « {cond.get('stat', cond.get('id'))} », inconnu")
    return out


# --- Ligne de commande ---------------------------------------------------------------------------------------------

def main(args):
    action = args[0] if args else "assembler"
    if action == "verifier":
        erreurs = verifier(cibles=set(args[1:]) or None)
        for e in erreurs:
            print(e)
        print(f"{len(erreurs)} erreur(s)." if erreurs else "Packs valides.")
        return 1 if erreurs else 0
    if action == "assembler":
        erreurs = verifier()
        if erreurs:
            print("\n".join(erreurs))
            return 1
        donnees, index = assembler()
        print(f"data/ assemblé depuis {len(index['packs'])} packs : " + ", ".join(m["id"] for m in index["packs"]))
        return 0
    if action == "liste":
        for m in tous():
            frs = fragments(m)
            print(f"{m['id']:<12} {m['sorte']:<8} {m['version']:<7} {m['nom']['fr']}  ({len(frs)} fichiers)")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
