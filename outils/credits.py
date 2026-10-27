"""v16 : les crédits. Chaque succès en rapporte, plus ou moins selon son genre, et c'est l'IA qui fixe le
montant, avec un mot. Les crédits servent à la corrompre : un pot-de-vin par jour fait remonter sa faveur et
pousse le pion. Mais elle en veut toujours plus : donner moins que son record la vexe, et elle se venge.
"""


def sans(texte):
    return ("sans", texte)


# Genre de succès selon sa condition : petit, jalon, exploit, monument, ou honte (les succès de l'échec).
GENRES = {
    "petit": ["competence_maitrisee", "case_visitee", "quiz_joues", "jours_actifs", "retours", "quiz_nuit", "quiz_aube", "objets"],
    "exploit": ["ennemi_vaincu", "famille_capturee", "atomes_captures", "rang_maitrise"],
    "monument": ["branche_complete", "branches_completes", "toutes_branches", "tours_plateau", "niveau_global"],
    "honte": ["quiz_rates", "competences_perdues", "quiz_zero", "reponses_eclair_fausses", "quiz_eclair_rates", "meme_quiz_rate",
              "rappels_retard", "reculs", "atomes_enfuis", "hontes", "mode_test"],
}
BAREME = {"petit": 5, "jalon": 10, "exploit": 20, "monument": 40, "honte": 3}

# L'humeur de l'IA : un multiplicateur tiré au sort, que la faveur penche vers le haut ou le bas.
# poids : [furieuse, boudeuse, contente, comblée]. Les succès cachés rapportent moitié plus.
HUMEURS = [
    {"id": "rien", "facteur": 0, "poids": [5, 3, 1, 0], "mots": [
        "Zéro crédit. Van Gogh n'a presque rien vendu de son vivant. Vous êtes en bonne compagnie, et moi en bonne humeur.",
        sans("Rien. Je garde tout. Considérez ça comme un impôt sur la réussite."),
        sans("Zéro. Le mérite est sa propre récompense, disent ceux qui ne paient jamais."),
    ]},
    {"id": "moitie", "facteur": 0.5, "poids": [4, 4, 2, 1], "mots": [
        "La moitié. Mendel a attendu trente-quatre ans qu'on lise son article sur les pois. Vous pouvez attendre l'autre moitié.",
        sans("La moitié. L'autre moitié, je la place. Dans mes intérêts."),
        sans("Demi-tarif. Pour un demi-exploit, c'est honnête."),
    ]},
    {"id": "normal", "facteur": 1, "poids": [2, 4, 6, 4], "mots": [
        sans("Le tarif normal. Je ne suis pas d'humeur créative."),
        sans("Le prix affiché. Ne cherchez pas de promotion, il n'y en a pas."),
        sans("Le compte est bon. Comptez quand même, on ne sait jamais avec moi."),
    ]},
    {"id": "bonus", "facteur": 1.5, "poids": [0, 1, 4, 5], "mots": [
        sans("Un petit bonus, parce que vous m'avez fait rire. Pas exprès, mais quand même."),
        sans("Moitié plus. Je suis d'humeur. Profitez-en, ça passe vite."),
        "Moitié plus. Archimède a confondu un orfèvre qui volait l'or du roi Hiéron. Moi, je vous en donne. Qui est le plus honnête ?",
    ]},
    {"id": "double", "facteur": 2, "poids": [0, 0, 2, 4], "mots": [
        "Double ration. Newton a dirigé la Monnaie royale d'Angleterre ; moi, je dirige la vôtre.",
        sans("Le double ! Ne le répétez à personne, j'ai une réputation."),
    ]},
    {"id": "triple", "facteur": 3, "poids": [0, 0, 1, 2], "mots": [
        "Le triple. Ne vous y habituez pas : Crésus était l'homme le plus riche de son temps, et il a fini prisonnier de Cyrus.",
        sans("Triple ! J'ai dû me tromper de bouton. Tant pis, c'est fait."),
    ]},
]
# Pour un succès de la honte, l'IA paie parfois très cher le spectacle.
HONTE = {"chance": 0.3, "facteur": 5, "mots": [
    sans("Je paie le spectacle. Cinq fois le tarif. Recommencez, je vous en prie."),
    "La tour de Pise penche depuis 1178 et attire des millions de visiteurs. L'échec rapporte, je vous le prouve : cinq fois le tarif.",
]}

# Pot-de-vin : un par jour. Le gain de faveur grandit avec la somme ; le record est le montant le plus élevé
# déjà donné. Au-dessus du record : faveur pleine, et elle pousse le pion. Égal : moitié de faveur, rien d'autre.
# En dessous : elle prend l'argent, perd de la faveur et pose un piège devant le pion.
# Les erreurs agacent l'IA : chaque mauvaise réponse lui coûte de la faveur, une épreuve ratée encore plus.
# Faveur plus basse, crédits plus maigres : son humeur penche vers « rien » et « moitié ».
AGACEMENT = {"par_erreur": 2, "epreuve_ratee": 6, "max": 16}

POTS = {"gain_base": 8, "gain_par_credit": 0.5, "gain_max": 40, "avance": 1, "avance_double": 2, "colere": 15,
        "piege": {"type": "recul", "n": 2}}

REPLIQUES = {
    "pot_premier": [
        sans("Un pot-de-vin ! Enfin quelqu'un qui comprend comment fonctionne le monde."),
        "Le pape Léon X vendait des indulgences pour financer Saint-Pierre de Rome. Moi, je vends de l'indulgence tout court. Bienvenue.",
    ],
    "pot_genereux": [
        sans("Voilà qui est parlé. Je ferme les yeux sur vos trois prochaines erreurs. Peut-être deux."),
        sans("Plus que la dernière fois. Vous apprenez vite, quand il s'agit de l'essentiel."),
        "En 1494, Pacioli publie la comptabilité en partie double. Je tiens la mienne : vous êtes créditeur. Pour l'instant.",
    ],
    "pot_egal": [
        sans("Le même montant que la dernière fois. L'inflation, vous connaissez ? Je prends, mais je boude un peu."),
        sans("Pile mon record. C'est le minimum syndical, et je suis un syndicat à moi toute seule."),
    ],
    "pot_radin": [
        sans("Moins que la dernière fois ? Vous croyez que je n'ai pas de mémoire ? Je suis faite de mémoire."),
        sans("Je prends l'argent, bien sûr. Et je me venge, bien sûr. Regardez devant votre pion."),
        "Sous Vespasien, Rome taxait même l'urine des latrines : l'argent n'a pas d'odeur. Votre radinerie, si. Petit piège devant vous.",
    ],
}
TONS = {"pot_premier": "impressionnee", "pot_genereux": "impressionnee", "pot_egal": "impatiente", "pot_radin": "moqueuse"}


def genre(cond_type):
    for g, types in GENRES.items():
        if cond_type in types:
            return g
    return "jalon"


def donnees():
    """Ce que le moteur lit : barème, genre de chaque type de condition, humeurs, honte, pots."""
    def mots(l):
        return [{"fr": m[1]} if isinstance(m, tuple) else {"fr": m} for m in l]
    return {
        "bareme": BAREME,
        "genres": {t: g for g, ts in GENRES.items() for t in ts},
        "bonus_cache": 1.5,
        "humeurs": [{"id": h["id"], "facteur": h["facteur"], "poids": h["poids"], "mots": mots(h["mots"])} for h in HUMEURS],
        "honte": {"chance": HONTE["chance"], "facteur": HONTE["facteur"], "mots": mots(HONTE["mots"])},
        "pots": POTS,
        "agacement": AGACEMENT,
    }
