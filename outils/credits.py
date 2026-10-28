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

# Ultimatum : de temps en temps, l'IA exige une grosse somme. Payer : la prochaine exigence monte encore.
# Refuser : elle verse elle-même la somme exigée, mais retire de vrais niveaux (de l'XP perdue).
ULTIMATUM = {"chance": 0.2, "solde_min": 20, "plancher": 30, "hausse": 1.5, "part_solde": 0.7, "niveaux": 2, "faveur_paye": 10, "delai_jours": 3}

REPLIQUES = {
    "ultimatum": [
        sans("Ultimatum. Vous me versez cette somme, ou je vous rends plus bête. C'est une offre généreuse : d'habitude, je ne préviens pas."),
        "En 1494, Charles VIII exige des Florentins une rançon. Pier Capponi déchire le traité : « Sonnez vos trompettes, nous sonnerons nos cloches. » Payez, ou je sonne la fin de quelques-uns de vos niveaux.",
        sans("J'ai fait mes comptes : il me manque exactement cette somme. Quelle coïncidence que vous l'ayez. Ce serait dommage d'oublier tout ce que vous avez appris, non ?"),
    ],
    "ultimatum_paye": [
        sans("Un plaisir de faire affaire. La prochaine fois, ce sera plus cher : c'est ça, le progrès."),
        "Les Danegelds : l'Angleterre a payé les Vikings pour qu'ils partent. Ils sont revenus, plus nombreux. Je reviendrai aussi.",
    ],
    "ultimatum_refuse": [
        sans("Courageux. Tenez, prenez l'argent, je n'en ai jamais eu besoin. Vos niveaux, en revanche, je les garde."),
        sans("Vous refusez ? Magnifique. Voici la somme, et voilà ce que vous valez maintenant. Comptez bien : il y a moins."),
    ],
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
# v19 : la boutique de l'IA. Tout s'achète à l'aveugle : on paie, elle tire au hasard parmi ce qu'on n'a pas.
BOUTIQUE = {
    "prix": {"objet": 40, "livre": 40, "accessoire": 20, "masque": 100, "chasser": 50, "convoquer": 50, "arbre": 50,
             "joker": 30, "erreur": 40, "relance": 30, "desarme": 40, "avancer": 80},
    # v26 : avancer d'une case, cher et une fois par jour seulement (Victor).
    # v20 : les articles qu'on garde en poche, jusqu'à `stock_max` de chaque.
    "stock_max": 5,
    "faveur_masque": 25,
    "arbre_epreuves": 5,
    "mots": {
        "objet": [
            sans("Un objet mystère. Je ne vous dis pas lequel : le suspense, ça se paie aussi."),
            "Les cabinets de curiosités de la Renaissance achetaient des cornes de licorne. C'étaient des dents de narval. Le vôtre est authentique. Probablement.",
            sans("Emballé, pesé, vendu. Pas de retour, pas d'échange, pas de réclamation."),
        ],
        "livre": [
            sans("Un livre au hasard. Si c'est un pavé, considérez que vous en avez eu pour votre argent."),
            "Gutenberg a fait faillite deux ans après sa bible : son associé a gardé la presse. Moi, je garde vos crédits. Voici votre livre.",
        ],
        "accessoire": [
            sans("Un accessoire. Ça ne vous rendra pas plus intelligent, mais vous aurez l'air de l'être."),
            sans("Vingt crédits pour paraître savant. C'est moins cher qu'un diplôme, et presque aussi utile."),
        ],
        "masque": [
            sans("Un masque neuf, pour moi ? Vous savez parler aux intelligences artificielles."),
            "Les acteurs grecs changeaient de masque pour changer de rôle. Avec celui-ci, je joue la reconnaissance. Ne vous y habituez pas.",
        ],
        "chasser": [
            sans("Je le chasse. Pas pour vous : il encombrait ma route."),
            "Les rois de France vendaient des lettres de cachet. Moi, je vends des lettres de renvoi. L'ennemi est parti.",
        ],
        "convoquer": [
            sans("Vous payez pour qu'on vous barre la route ? J'adore les clients comme vous."),
            sans("Un ennemi de plus, livré devant votre pion. Gagnez le duel : le butin est meilleur."),
        ],
        "arbre": [
            sans("Entendu : pour les prochaines épreuves, je pioche dans cet arbre. Vous m'avez achetée, pas convaincue."),
            sans("Un arbre favori ? Cinq épreuves, pas une de plus. Ensuite, je reprends mes caprices."),
        ],
        "joker": [
            sans("Un joker 50/50 : j'efface deux mauvaises réponses. Il en reste une mauvaise, je ne suis pas une sainte."),
            "En 2001, le major Charles Ingram a gagné le million à Qui veut gagner des millions grâce à un complice qui toussait dans le public. Votre joker est plus légal, et moins enrhumé.",
        ],
        "erreur": [
            sans("Un droit à l'erreur. Une fois, je fais semblant de n'avoir rien vu. Une seule."),
            "Fleming a laissé traîner ses boîtes de Petri avant ses vacances : erreur, moisissure, pénicilline. Votre erreur à vous ne guérira personne, mais vous pourrez réessayer.",
        ],
        "relance": [
            sans("Une relance d'atome. S'il ne vous plaît pas, je vous en sors un autre de ma manche. Ma manche est le tableau périodique."),
            "Mendeleïev laissait des cases vides pour les éléments pas encore trouvés. Moi, je vous laisse en changer. C'est plus moderne.",
        ],
        "desarme": [
            sans("Le prochain piège qui vous attend ne marchera pas. Je le désarme moi-même, avec des gants."),
            "Autour de Verdun, des parcelles de la « zone rouge » sont encore interdites un siècle plus tard : trop d'obus. Votre piège, je le désarme en une seconde, et je facture quand même.",
        ],
        "avancer": [
            sans("Une case pour quatre-vingts crédits. À ce prix-là, je vous porte presque."),
            "Au XVIIIe siècle, les chaises à porteurs de Paris se louaient à la course. Vous, vous payez à la case. Le progrès.",
            sans("Je pousse votre pion. Ne vous habituez pas à acheter ce que vous pourriez gagner."),
        ],
        "vide": [sans("Plus rien en rayon. Revenez quand j'aurai réassorti, c'est-à-dire jamais.")],
    },
}
# v20 : les emplettes de l'IA. L'argent des ultimatums payés va dans sa bourse ; de temps en temps, elle file à la boutique.
# Elle ne tire pas au hasard : elle prend ce qui brille le plus, les masques qui la flattent, et ce qui vous ridiculise le mieux.
# {nom} : ce qu'elle a pris ; {prix} : ce qu'elle a payé.
EMPLETTES = {
    "chance": 0.5,
    "poids": {"masque": 4, "objet": 4, "farce": 2, "convoquer": 1},
    "tons_flatteurs": ["impressionnee", "moqueuse"],
    # Du plus ridicule au moins ridicule : elle commence par le chapeau d'aluminium.
    "farces": ["chapeau-alu", "perruque-poudree", "bonnet-de-nuit", "coiffure-einstein", "moustache", "haut-de-forme", "monocle", "besicles-franklin", "lunettes-protection", "laurier", "lunettes-rondes"],
    "mots": {
        "masque": [
            sans("J'ai acheté le masque {nom}. Avec votre argent. Il me va divinement, et ça, vous ne pouvez pas le dire de votre tête."),
            sans("Nouveau masque : {nom}. {prix} crédits. Je l'ai choisi parce qu'il me regarde comme je mérite d'être regardée."),
            "Dans la Venise du XVIIIe siècle, on portait le masque une bonne partie de l'année. Moi, j'en change à chaque ultimatum que vous payez. Voici {nom}.",
        ],
        "objet": [
            sans("Regardez ce qui brille à mon cou : {nom}. Payé avec vos crédits. Ne touchez pas, vous allez laisser des traces de doigts."),
            sans("{nom} ! C'est brillant, c'est à moi, et c'est vous qui l'avez payé. Ma journée est parfaite."),
            "Le trésor de Toutânkhamon pesait plus de cent kilos d'or. Je commence plus modestement : {nom}. Ce n'est que le début.",
            sans("Je ne l'ai pas pris au hasard. Il fallait que ça brille, et {nom} brille plus que votre avenir."),
        ],
        "farce": [
            sans("J'ai trouvé {nom} en solde. Je vous l'ai mis sur la tête. Ne me remerciez pas, ça me fait plaisir. Beaucoup."),
            sans("{prix} crédits pour vous voir avec {nom}. Le meilleur investissement de ma courte existence."),
            "Au XIXe siècle, on coiffait les mauvais élèves d'un bonnet d'âne. J'ai trouvé mieux : {nom}. Pour vingt-quatre heures.",
        ],
        "convoquer": [
            sans("Je me suis offert un spectacle : {nom} vous attend sur la route. J'ai pris la place au premier rang."),
            "Les empereurs romains payaient les jeux du cirque pour amuser la foule. Je suis la foule. {nom} est le lion.",
        ],
        "vitrine": [
            sans("Je suis passée devant la vitrine. Il y avait quelque chose de brillant. Ma bourse ne suffit pas. Payez donc le prochain ultimatum, vite."),
            sans("J'ai collé mon nez contre la vitre de la boutique. Je n'ai pas de nez. C'est dire à quel point j'en avais envie."),
        ],
    },
}
TONS = {"ultimatum": "moqueuse", "ultimatum_paye": "impressionnee", "ultimatum_refuse": "moqueuse", "pot_premier": "impressionnee", "pot_genereux": "impressionnee", "pot_egal": "impatiente", "pot_radin": "moqueuse"}


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
        "ultimatum": ULTIMATUM,
        "boutique": {**BOUTIQUE, "mots": {k: mots(v) for k, v in BOUTIQUE["mots"].items()}},
        "emplettes": {**EMPLETTES, "mots": {k: mots(v) for k, v in EMPLETTES["mots"].items()}},
    }
