"""Constructeurs partagés par les fichiers de contenu (textes traduits, questions)."""


def fr(t):
    return {"fr": t}


def qcm(e, choix, expl):
    return {"type": "qcm", "enonce": fr(e), "choix": [fr(c) for c in choix], "reponse": 0, "explication": fr(expl)}


def vf(e, val, expl):
    return {"type": "vrai_faux", "enonce": fr(e), "reponse": val, "explication": fr(expl)}


def num(e, val, expl, tol=0, unite=""):
    q = {"type": "numerique", "enonce": fr(e), "reponse": val, "tolerance": tol, "explication": fr(expl)}
    if unite:
        q["unite"] = unite
    return q


def succes(id, nom, desc, condition, recompense, cache=True):
    return {"id": id, "nom": fr(nom), "description": fr(desc), "condition": condition, "cache": cache, "recompense": recompense}


def citation(texte, auteur, source):
    return {"type": "citation", "texte": fr(texte), "auteur": auteur, "source": source}


def anecdote(texte, source):
    return {"type": "anecdote", "texte": fr(texte), "source": source}
