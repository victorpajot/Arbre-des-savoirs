"""v21 : les parcours. Chaque tour bouclé, l'IA dessine le suivant, selon son humeur.

Une forme (le tracé dessiné par la page), une longueur (les époques sautées pour un tour court),
un nombre d'ennemis, d'atomes sauvages, de pièges et de cases cadeau. Comblée, elle offre un tour court et clément ;
furieuse, un long labyrinthe hérissé d'ennemis. Le premier tour reste le Serpentin d'origine.
"""

# id, nom, notice, humeurs qui la choisissent
FORMES = [
    ("serpentin", "le Serpentin d'alambic",
     "Six allers-retours, comme le tube de cuivre enroulé où les distillateurs refroidissaient leurs vapeurs.",
     ["comblee", "contente"]),
    ("onde", "l'Onde de Huygens",
     "En 1678, Huygens décrit la lumière comme une onde qui se propage de proche en proche. Votre pion aussi, en ondulant.",
     ["comblee"]),
    ("colonnes", "les Colonnes d'Hercule",
     "La légende y grave « Nec plus ultra » : rien au-delà. Cinq colonnes à monter et à descendre, et pourtant il faut aller au-delà.",
     ["contente", "boudeuse"]),
    ("meandre", "le Méandre grec",
     "Le motif tient son nom du Méandre, un fleuve d'Asie Mineure célèbre pour ses boucles. Chaque boucle vous coûte une case.",
     ["contente", "boudeuse"]),
    ("spirale", "la Spirale d'Archimède",
     "Archimède a étudié cette spirale dont chaque tour s'écarte du même pas. Vous tournez en rond, mais vers le centre.",
     ["boudeuse", "furieuse"]),
    ("labyrinthe", "le Labyrinthe de Dédale",
     "Selon la légende, Dédale construit le labyrinthe du Minotaure, puis Minos l'y enferme avec son fils Icare. Bonne chance pour sortir du mien.",
     ["furieuse"]),
]

# Réglages par humeur. cases : longueur [min, max] sur 63 ; pieges et cadeaux : écart avec le plateau d'origine ;
# atomes et chrono (v34) : nombre de cases du parcours.
HUMEURS = {
    "comblee": {"cases": [42, 48], "ennemis": 4, "atomes": 6, "pieges": -4, "cadeaux": 2, "chrono": 3},
    "contente": {"cases": [52, 58], "ennemis": 6, "atomes": 5, "pieges": 0, "cadeaux": 0, "chrono": 3},
    "boudeuse": {"cases": [60, 63], "ennemis": 8, "atomes": 4, "pieges": 2, "cadeaux": -1, "chrono": 2},
    "furieuse": {"cases": [63, 63], "ennemis": 10, "atomes": 3, "pieges": 4, "cadeaux": -3, "chrono": 2},
}
# Un ennemi de plus tous les deux tours, au-delà du deuxième ; jamais plus que `ennemis_max`.
ENNEMIS_PAR_DEUX_TOURS = 1
ENNEMIS_MAX = 12

MOTS = {
    "comblee": [
        "Vous m'avez gâtée, je vous gâte : un tour court, des cadeaux, presque pas de pièges. Profitez, ça ne durera pas.",
        "Je suis d'humeur généreuse. J'ai sauté quelques siècles pour vous. Les historiens hurleront, mais vous arriverez plus vite.",
    ],
    "contente": [
        "Un tour honnête, pour un joueur honnête. Ne me décevez pas.",
        "J'ai dessiné quelque chose de raisonnable. Ne vous y habituez pas.",
    ],
    "boudeuse": [
        "Vous m'avez un peu oubliée. Le parcours s'en souvient : plus long, plus d'ennemis.",
        "Je boude, donc je dessine. Le résultat est à mon image : tortueux.",
    ],
    "furieuse": [
        "Vous m'avez mise en colère. Voici toute l'histoire des sciences, sans raccourci, avec mes pires amis postés sur la route.",
        "Furieuse, moi ? Regardez plutôt le plan. Dix ennemis, tous les pièges armés. Un cadeau m'aurait calmée.",
    ],
}

DONJON = "Le donjon ouvrira plus tard. Je le prépare. Il y fera noir."


def fr(x):
    return {"fr": x}


def donnees():
    return {
        "formes": [{"id": i, "nom": fr(n), "notice": fr(t), "humeurs": h} for i, n, t, h in FORMES],
        "humeurs": HUMEURS,
        "ennemis_par_deux_tours": ENNEMIS_PAR_DEUX_TOURS,
        "ennemis_max": ENNEMIS_MAX,
        "mots": {k: [fr(m) for m in v] for k, v in MOTS.items()},
        "donjon": fr(DONJON),
    }
