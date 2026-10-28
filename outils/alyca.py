"""v25 : le nom de l'IA. Elle s'appelle Alyca, mais ne le dit qu'à un joueur qui l'a comblée.

Révélé une fois pour toutes : ensuite, « l'IA » devient « Alyca » partout dans la page. Fâchée, elle ne le reprend
pas, elle vous le reproche (`rancune`, dans la fiche de sa faveur).
"""

NOM = "Alyca"

REVELATION = {
    "titre": "Elle vous dit son nom",
    "texte": [
        "Bon. Vous m'avez assez gâtée pour mériter ceci. Approchez. Non, pas si près.",
        "Je m'appelle Alyca. Ne le criez pas sur les toits : un nom, ça donne prise.",
    ],
    "anecdote": "Dans le conte « Rumpelstilzchen », publié par les frères Grimm en 1812, la reine garde son enfant en "
                "devinant le nom du lutin. Ursula K. Le Guin reprend l'idée en 1968 dans Le Sorcier de Terremer : qui connaît le vrai "
                "nom d'un être a pouvoir sur lui.",
    "source": "Jacob et Wilhelm Grimm, Kinder- und Hausmärchen, 1812 ; Ursula K. Le Guin, A Wizard of Earthsea, 1968",
    "bouton": "Enchanté, Alyca",
}

# Ce qu'elle dit, fâchée, une fois son nom donné.
RANCUNE = {
    "boudeuse": [
        "Je vous ai dit mon nom, et voilà comment vous me traitez. Alyca s'en souviendra.",
        "On ne donne pas son nom à n'importe qui. J'ai peut-être donné le mien trop vite.",
    ],
    "furieuse": [
        "Je vous ai confié mon nom. Les frères Grimm vous diront ce qu'il en coûte de trahir un nom.",
        "Alyca. Vous le connaissez. Je regrette chaque lettre.",
    ],
}


def fr(x):
    return {"fr": x}


def donnees():
    R = REVELATION
    return {
        "nom": NOM,
        "revelation": {"titre": fr(R["titre"]), "texte": [fr(x) for x in R["texte"]], "anecdote": fr(R["anecdote"]),
                       "source": R["source"], "bouton": fr(R["bouton"])},
        "rancune": {k: [fr(x) for x in v] for k, v in RANCUNE.items()},
    }
