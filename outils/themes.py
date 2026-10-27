"""v18 : le thème de chaque chose. Un ancrage de plus sur le même thème, c'est un souvenir de plus.

Chaque objet, savant, masque, ennemi, accessoire et succès porte le thème (l'arbre) auquel il se rattache.
Le jeu s'en sert pour que la case où se tient le pion donne le ton : sur une case Cosmos, le butin, les cadeaux,
les apartés de l'IA, son masque, ses farces et ses répliques parlent d'astronomie autant que possible.

Le thème se déduit de la condition quand elle vise une compétence ou un arbre ; sinon il est donné ici.
"""

# Les masques de l'IA : des automates, des créatures et des machines, chacun rattaché à ce qu'il évoque.
MASQUES = {
    "theatre": "eloquence",          # persona, le masque de l'acteur
    "promethee": "savoir",           # le feu, première case du plateau
    "talos": "mecanique",            # géant de bronze, premier automate
    "heron": "mecanique",            # l'éolipyle, la vapeur
    "tete-airain": "sagesse",        # la tête qui répond, légende de Roger Bacon
    "homoncule": "alchimie",         # l'homunculus de Paracelse
    "golem": "eloquence",            # animé par un mot, emet
    "peste": "lucidite",             # miasmes, boucs émissaires
    "automate": "mecanique",         # Vaucanson
    "turc": "lucidite",              # l'illusion du joueur d'échecs
    "ecrivain": "eloquence",         # l'automate qui écrit
    "creature": "etincelle",         # Frankenstein et le galvanisme
    "machine-analytique": "logique",
    "robot-capek": "eloquence",      # le mot « robot » vient d'une pièce de théâtre
    "bombe": "logique",
    "tubes": "etincelle",
    "perceptron": "empathie",        # un neurone artificiel
    "unimate": "mecanique",
    "eliza": "empathie",             # l'effet ELIZA
    "shakey": "logique",
    "deep-blue": "logique",
    "kismet": "empathie",            # le robot aux émotions
    "alphago": "logique",
    "finale": "cosmos",              # Laplace, Mécanique céleste
}

ENNEMIS = {
    "sophiste": "eloquence", "platiste": "cosmos", "influenceur": "savoir", "astrologue": "cosmos",
    "mesmer": "etincelle", "lyssenko": "savoir", "complotiste": "lucidite", "charlatan": "alchimie",
    "pline": "savoir", "gall": "empathie", "ussher": "savoir", "diafoirus": "savoir",
    "bessler": "mecanique", "raconteur": "lucidite", "lombroso": "empathie", "tribun": "eloquence",
}

# Premier tour : chaque ennemi attend sur une case de son thème, ou sur celle qui lui répond le mieux.
PLACEMENT = {
    "4": "sophiste",      # l'écriture : les mots, déjà
    "15": "platiste",     # Ératosthène mesure la Terre
    "39": "influenceur",  # Leeuwenhoek voit les microbes : les vraies « toxines »
    "34": "astrologue",   # Kepler faisait des horoscopes
    "43": "mesmer",       # Franklin présidait la commission qui l'a démasqué en 1784
    "52": "lyssenko",     # Mendel, qu'il niait
    "61": "complotiste",  # Apollo 11, sa cible préférée
}

# Reliques des tours (sans compétence) : le thème de leur histoire.
RELIQUES = {
    "flamme-promethee": "savoir", "pierre-philosophale": "alchimie", "mecanisme-anticythere": "mecanique",
    "principia": "mecanique", "ruban-turing": "logique", "disque-voyager": "cosmos", "demon-laplace": "mecanique",
}

# Succès dont la condition ne dit rien du thème : celui de leur anecdote ou de leur citation.
SUCCES = {
    "premier-pas": "savoir", "eureka": "mecanique", "petit-gauss": "logique", "dix-competences": "empathie",
    "arbre-complet": "mecanique", "premier-rappel": "empathie", "serie-rappels": "lucidite", "cinquante-rappels": "sagesse",
    "constance": "eloquence", "niveau-5": "alchimie", "resilience": "logique", "tour-de-pise": "mecanique",
    "pomme": "mecanique", "lucide": "lucidite", "dix-pour-cent": "empathie", "foudre-deux-fois": "etincelle",
    "effet-mozart": "empathie", "styles-apprentissage": "empathie", "eppur": "cosmos", "perseverance": "lucidite",
    "cloche": "empathie", "deux-hemispheres": "empathie", "huit-verres": "savoir", "insomniaque": "empathie",
    "leve-tot": "sagesse", "voyageur-temporel": "mecanique", "table-rase": "logique", "neutrinos": "mecanique",
    "serendipite": "eloquence", "procrastination": "savoir", "pluton": "cosmos", "schrodinger": "mecanique",
    "elephant": "savoir", "preuves-extraordinaires": "lucidite", "encyclopediste": "eloquence", "un-an": "cosmos",
    "deux-nobel": "alchimie", "nous-saurons": "logique", "wunderkammer": "savoir", "plus-ultra": "sagesse",
    "nains-geants": "sagesse", "cultiver-jardin": "sagesse", "promenade-kant": "sagesse", "nietzsche-soeur": "sagesse",
    "sisyphe": "sagesse", "tour-complet": "logique", "eternel-retour": "sagesse", "cycle-meton": "cosmos",
    "hypotheses-non-fingo": "mecanique", "infaillible": "logique", "point-bleu": "cosmos", "demon-laplace": "mecanique",
    "baignoire": "mecanique", "eppur-si-muove": "cosmos", "woolsthorpe": "mecanique", "honte-1": "alchimie",
    "honte-10": "cosmos", "honte-effacee-50": "cosmos",
}
# Ceux-là restent sans thème : ils parlent de tout à la fois.
SANS_THEME = {"polymathe", "conservateur", "dernier-homme", "honte-50"}


def theme_condition(cond, stat_de, succes_par_id, cases, prof=0):
    """Thème déduit d'une condition : compétence, arbre, case du plateau, ennemi, atomes, ou succès requis."""
    if not cond or prof > 4:
        return None
    t = cond.get("type")
    if t == "competence_maitrisee":
        return stat_de.get(cond["id"])
    if t in ("branche_complete", "quiz_parfaits_stat"):
        return cond["stat"]
    if t in ("case_visitee", "case_atteinte", "epoque_atteinte"):
        return cases[cond["n"] - 1]
    if t == "ennemi_vaincu":
        return ENNEMIS.get(cond["id"])
    if t in ("atomes_captures", "famille_capturee", "atomes_enfuis"):
        return "alchimie"
    if t == "succes":
        s = succes_par_id.get(cond["id"])
        return s and theme_succes(s, stat_de, succes_par_id, cases, prof + 1)
    return None


def theme_succes(s, stat_de, succes_par_id, cases, prof=0):
    if s["id"] in SANS_THEME:
        return None
    if s["id"] in SUCCES:
        return SUCCES[s["id"]]
    if s.get("ouvre"):
        return s["ouvre"]
    return theme_condition(s["condition"], stat_de, succes_par_id, cases, prof)


def poser(fichiers):
    """Ajoute le champ « theme » à chaque objet, savant, accessoire, masque, ennemi et succès."""
    stat_de = {k["id"]: k["stat"] for k in fichiers["skills.json"]["competences"]}
    cases = [c["stat"] for c in fichiers["plateau.json"]["cases"]]
    succes = fichiers["succes.json"]["succes"]
    par_id = {s["id"]: s for s in succes}
    stats = set(stat_de.values())

    def fixer(x, th, quoi):
        assert th is None or th in stats, (quoi, x["id"], th)
        if th:
            x["theme"] = th

    for s in succes:
        fixer(s, theme_succes(s, stat_de, par_id, cases), "succès")
    for o in fichiers["objets.json"]["objets"]:
        fixer(o, RELIQUES.get(o["id"]) or theme_condition(o.get("condition"), stat_de, par_id, cases), "objet")
    for sv in fichiers["avatar.json"]["savants"]:
        fixer(sv, theme_condition(sv["condition"], stat_de, par_id, cases), "savant")
    for a in fichiers["avatar.json"]["accessoires"]:
        fixer(a, theme_condition(a.get("condition"), stat_de, par_id, cases), "accessoire")
    for m in fichiers["ia.json"]["masques"]:
        fixer(m, MASQUES[m["id"]], "masque")
    for e in fichiers["ennemis.json"]["ennemis"]:
        fixer(e, ENNEMIS[e["id"]], "ennemi")
    assert set(MASQUES) == {m["id"] for m in fichiers["ia.json"]["masques"]}
    assert set(ENNEMIS) == {e["id"] for e in fichiers["ennemis.json"]["ennemis"]}
    inconnus = (set(SUCCES) | SANS_THEME) - set(par_id)
    assert not inconnus, inconnus
    sans = [s["id"] for s in succes if "theme" not in s and s["id"] not in SANS_THEME]
    assert not sans, f"succès sans thème : {sans}"
    sans = [o["id"] for o in fichiers["objets.json"]["objets"] if "theme" not in o]
    assert not sans, f"objets sans thème : {sans}"
    sans = [s["id"] for s in fichiers["avatar.json"]["savants"] if "theme" not in s]
    assert not sans, f"savants sans thème : {sans}"
