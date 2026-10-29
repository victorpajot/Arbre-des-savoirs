"""v34 : Chrono, le jeu des siècles (demande de Victor, 2026-10-29).

Alyca présente un événement déjà débloqué ailleurs dans le jeu (une date de la frise, un livre, un savant, un objet)
et le joueur dit quand il s'est produit : le siècle d'abord, puis le demi-siècle, la décennie, l'année exacte. Chaque
événement a son propre niveau : deux réponses justes de suite le font monter d'un cran, une erreur le fait redescendre.
Juste : des crédits ; proche (un cran à côté) : un tout petit peu. Pas de compte à rebours, mais une réponse juste en
moins de huit secondes rapporte un crédit de plus.

Deux portes d'entrée : une case Chrono sur le plateau (la partie sert d'épreuve de la case), ou Alyca qui lance une
partie d'elle-même, environ une fois par jour (bonus : crédits seulement, le pion ne bouge pas).

Rien de nouveau à dater : les dates viennent de la frise, des livres, des savants et des objets, déjà vérifiées.
Pour un savant, tout siècle de sa vie compte juste (choix de Victor) ; en mode année exacte, on demande sa naissance.
"""

from aides import fr

# Cases du premier tour (les parcours suivants en ajoutent ou en retirent selon l'humeur, outils/parcours.py).
CASES = [14, 30, 49]

REGLES = {
    "cases": CASES,
    "evenements": 5,        # événements par partie
    "reussite": 3,          # justes sur une case Chrono pour réussir l'épreuve
    "avance": 3,            # cases gagnées sur une case Chrono réussie (plus le bonus du bouton Jouer)
    "min_reservoir": 5,     # éléments datés débloqués nécessaires pour jouer
    "points": {"juste": 2, "proche": 1, "rapide": 1, "parfait": 5},
    "rapide_ms": 8000,
    "monter": 2,            # justes de suite pour passer au niveau suivant
    "prehistoire": -4000,   # avant : une seule case « Préhistoire », au niveau 1 seulement
    "spontane": 0.34,       # chance, après une épreuve, qu'Alyca lance une partie (au plus une fois par jour)
    # pas : taille d'un créneau en années ; proche : créneaux d'écart encore « proches ».
    "niveaux": [
        {"n": 1, "pas": 100, "proche": 1, "nom": fr("Le siècle")},
        {"n": 2, "pas": 50, "proche": 1, "nom": fr("Le demi-siècle")},
        {"n": 3, "pas": 10, "proche": 1, "nom": fr("La décennie")},
        {"n": 4, "pas": 1, "proche": 5, "nom": fr("L'année exacte")},
    ],
}

TEXTES = {"chrono": "Case Chrono : l'IA te présente cinq événements déjà débloqués, tu dis quand ils se sont produits. "
                    "Trois justes, et ton pion avance."}

# Tuple (référence, texte) : la réplique cite l'histoire de la datation ; sinon, une chaîne sans référence.
REPLIQUES = {
    "chrono_annonce": [
        "Petite vérification d'archives. En 1583, Joseph Scaliger a comparé toutes les chronologies anciennes. Je vous demande seulement cinq dates.",
        "Un contrôle de chronologie. En 1650, l'archevêque Ussher datait la Création de 4004 av. J.-C. Vous pouvez faire mieux. Moins sûr de vous, déjà.",
        "Je range mes archives et j'ai besoin d'un assistant. Bède le Vénérable a popularisé l'ère chrétienne au VIIIe siècle. Vous, vous allez juste la réciter.",
        "Cinq dates, tirées de ce que vous avez déjà vu. Hérodote mélangeait légende et chronologie ; vous n'avez pas cette excuse.",
        ("", "Une partie de Chrono. Je vous montre un événement, vous me dites quand. Ce n'est pas un interrogatoire. Si, un peu."),
        ("", "J'ai retrouvé de vieilles fiches. Voyons si vous savez les classer, ou si je dois tout refaire moi-même."),
    ],
    "chrono_case": [
        "Case Chrono. Le calendrier grégorien a supprimé dix jours d'un coup en 1582. Ici, on ne supprime rien : on date.",
        "Case Chrono. En 1949, Libby a daté au carbone 14 des échantillons de tombes égyptiennes. Vous, vous avez votre mémoire. Bon courage.",
        "Case Chrono. Les cernes d'un arbre donnent son âge à l'année près. J'attends la même précision, plus tard.",
        "Case Chrono. En 1752, les Anglais sont passés du 2 au 14 septembre. Vous ne sauterez aucune question.",
        "Case Chrono. Les astronomes comptent les jours depuis l'an 4713 av. J.-C. Vous, comptez juste jusqu'à cinq.",
        ("", "Case Chrono. Cinq événements, trois justes, et votre pion repart."),
        ("", "Case Chrono. Rangez ces événements dans le temps. Le temps, lui, ne vous attendra pas."),
    ],
    "chrono_juste": [
        "Juste. Scaliger aurait approuvé, et il approuvait peu de monde.",
        "Juste. Même Ussher ne datait pas aussi bien. Bon, Ussher ne datait pas bien.",
        "Juste. Vous avez l'œil d'un dendrochronologue.",
        "Juste. Ératosthène dressait déjà des listes de dates au IIIe siècle av. J.-C. Vous voilà dans sa lignée.",
        "Juste. Bède le Vénérable a écrit tout un traité sur le calcul du temps. Il vous aurait pris comme copiste.",
        "Exact. Comme la montre de Harrison, qui ne perdait que quelques secondes en traversant l'Atlantique.",
        ("", "Juste. Votre frise mentale tient debout."),
    ],
    "chrono_proche": [
        "Presque. Le carbone 14 aussi a une marge d'erreur. Elle est plus petite que la vôtre.",
        "À un cran près. La révolution russe d'Octobre a eu lieu en novembre, selon notre calendrier. Vous êtes en bonne compagnie.",
        "Proche. César a ajouté quatre-vingt-dix jours à l'an 46 av. J.-C. pour rattraper son retard. Vous avez moins de retard.",
        ("", "Pas loin. Un tout petit crédit, pour l'effort."),
        ("", "Presque. Le temps vous a glissé entre les doigts, d'un rien."),
    ],
    "chrono_faux": [
        "Raté. Lorenzo Valla a démasqué la Donation de Constantin par ses anachronismes, vers 1440. Vous venez d'en commettre un.",
        "Faux. Il n'y a pas d'an zéro dans notre calendrier. Il n'y a pas de zéro faute dans votre partie non plus.",
        "Raté. Le calendrier républicain avait rebaptisé les mois. Il n'avait pas déplacé les siècles.",
        "À côté. Ussher se trompait de quatre milliards d'années, mais avec aplomb. Vous, vous n'avez même pas l'aplomb.",
        "Raté. Denys le Petit s'est trompé de quelques années sur la naissance du Christ. Vous, de quelques siècles.",
        ("", "Faux. Je range l'événement sur votre mur, rubrique anachronismes."),
        ("", "Raté. Vous avez confondu les siècles. Ils ne vous en veulent pas. Moi, si."),
    ],
    "chrono_bilan_bon": [
        "Bonne partie. Priestley a dessiné une frise de deux mille vies en 1765. Vous en tenez cinq, c'est un début.",
        "Vos dates tiennent. Les cernes des arbres aussi, depuis des millénaires. Continuez à pousser.",
        "Belle partie. Scaliger a proposé la période julienne pour ranger tous les calendriers. Vous rangez déjà les vôtres.",
        ("", "Joli. Votre frise se remplit. La mienne est complète, mais je ne m'en vante pas."),
        ("", "Partie réussie. J'en connais qui confondent encore Moyen Âge et Antiquité. Pas vous, aujourd'hui."),
    ],
    "chrono_bilan_rate": [
        "Partie ratée. Même Newton s'est perdu dans la chronologie des anciens royaumes. Lui, au moins, il a écrit un livre dessus.",
        "Le temps vous a eu. Les Anglais avaient cent soixante-dix ans de retard sur le calendrier grégorien. Vous rattraperez.",
        ("", "Raté. Vos siècles se marchent sur les pieds. On les remettra en rang."),
        ("", "Partie perdue. Les événements reviendront, au même endroit du temps. C'est leur avantage sur vous."),
    ],
    "chrono_parfait": [
        "Cinq sur cinq. L'horloge atomique dérive d'une seconde en des millions d'années. Vous, aujourd'hui, de rien du tout.",
        "Sans faute. John Harrison a résolu le problème des longitudes avec une montre précise. Vous gagnez un bonus avec une mémoire précise.",
        ("", "Parfait. Je vérifie mes archives : non, elles ne disent rien de mieux."),
    ],
    # Furieuse, elle date sans plaisanter (contexte « furieuse_chrono », moteur.js FURIEUSE).
    "furieuse_chrono": [
        ("", "Cinq dates. Ne me faites pas perdre mon temps."),
        ("", "Datez. Vite, et juste, pour une fois."),
        ("", "Chrono. Je ne vous aiderai pas."),
        ("", "Des événements. Des siècles. Vous. Le mélange habituel."),
    ],
}

TONS = {"chrono_annonce": "neutre", "chrono_case": "neutre", "chrono_juste": "impressionnee", "chrono_proche": "moqueuse",
        "chrono_faux": "moqueuse", "chrono_bilan_bon": "impressionnee", "chrono_bilan_rate": "moqueuse",
        "chrono_parfait": "impressionnee", "furieuse_chrono": "impatiente"}


def succes():
    def s(id, nom, desc, cond, texte, source, cache=False):
        return {"id": id, "nom": fr(nom), "description": fr(desc), "condition": cond, "cache": cache,
                "recompense": {"type": "anecdote", "texte": fr(texte), "source": source}}
    return [
        s("chrono-1", "Pas d'an zéro", "Jouer une première partie de Chrono.", {"type": "chronos_joues", "n": 1},
          "Au VIe siècle, Denys le Petit compte les années à partir de la naissance du Christ. Il ne prévoit pas d'an zéro : "
          "on passe directement de l'an 1 av. J.-C. à l'an 1.", "Encyclopædia Britannica, « Dionysius Exiguus »"),
        s("chrono-10", "Dix jours effacés", "Jouer 10 parties de Chrono.", {"type": "chronos_joues", "n": 10},
          "En 1582, le pape Grégoire XIII réforme le calendrier : le jeudi 4 octobre est suivi du vendredi 15 octobre. "
          "Dix jours n'ont jamais existé.", "Bulle Inter gravissimas, 1582 ; Encyclopædia Britannica, « Gregorian calendar »"),
        s("chrono-50", "La longue durée", "Jouer 50 parties de Chrono.", {"type": "chronos_joues", "n": 50},
          "En 1949, Fernand Braudel découpe l'histoire en trois temps : l'événement, la conjoncture, et la « longue durée », "
          "celle des montagnes et des mers.", "Fernand Braudel, La Méditerranée et le monde méditerranéen à l'époque de Philippe II, 1949"),
        s("chrono-parfait-1", "Carbone 14", "Réussir une partie de Chrono sans faute.", {"type": "chronos_parfaits", "n": 1},
          "En 1949, Willard Libby et James Arnold vérifient la datation au carbone 14 sur des échantillons d'âge connu, tirés de tombes de pharaons. "
          "Prix Nobel de chimie pour Libby en 1960.", "Nobel Prize, « The Nobel Prize in Chemistry 1960 » ; Libby et Arnold, Science, décembre 1949"),
        s("chrono-parfait-10", "Lire les cernes", "Réussir 10 parties de Chrono sans faute.", {"type": "chronos_parfaits", "n": 10},
          "L'astronome Andrew Ellicott Douglass relie les cernes des arbres au cycle des taches solaires. Il fonde la dendrochronologie, "
          "la datation par les cernes, et le laboratoire de Tucson en 1937.", "University of Arizona, Laboratory of Tree-Ring Research, « Lab History »"),
        s("chrono-exactes-3", "À l'année près", "Donner 3 années exactes dans la même partie.", {"type": "dates_exactes_partie", "n": 3},
          "En 1650, l'archevêque James Ussher date la Création de 4004 av. J.-C., la veille du 23 octobre. "
          "D'une précision admirable, et faux de quelques milliards d'années.", "James Ussher, Annales Veteris Testamenti, 1650", cache=True),
        s("chrono-niveau-2", "La frise de Priestley", "Faire passer 10 événements au demi-siècle.", {"type": "dates_niveau", "niveau": 2, "n": 10},
          "En 1765, Joseph Priestley publie une frise de deux mille vies célèbres, de 1200 av. J.-C. à 1800. "
          "Trois mille ans d'histoire sur une seule feuille.", "Joseph Priestley, A Chart of Biography, 1765"),
        s("chrono-niveau-4", "Scaliger", "Connaître 10 événements à l'année exacte.", {"type": "dates_niveau", "niveau": 4, "n": 10},
          "En 1583, Joseph Scaliger compare les chronologies des Perses, des Babyloniens, des Égyptiens et des Juifs, "
          "pas seulement des Grecs et des Romains. Il bouleverse l'idée qu'on se faisait de l'histoire ancienne.", "Joseph Scaliger, De emendatione temporum, 1583"),
        s("chrono-rapides", "Horloge atomique", "Donner 20 réponses justes en moins de 8 secondes.", {"type": "dates_rapides", "n": 20},
          "Depuis 1967, la seconde est la durée de 9 192 631 770 périodes d'une radiation de l'atome de césium 133.",
          "BIPM, Brochure sur le SI, 9e édition, 2019"),
        s("chrono-anachronismes", "Donation de Constantin", "Se tromper de date 25 fois.", {"type": "dates_fausses", "n": 25},
          "Vers 1440, Lorenzo Valla démasque la Donation de Constantin : sa langue ne peut pas dater du IVe siècle. Un faux, trahi par ses anachronismes.",
          "Lorenzo Valla, De falso credita et ementita Constantini donatione, 1440", cache=True),
    ]


# Thème de chaque succès, selon son anecdote (outils/themes.py).
THEMES = {"chrono-1": "cosmos", "chrono-10": "cosmos", "chrono-50": "sagesse", "chrono-parfait-1": "alchimie",
          "chrono-parfait-10": "savoir", "chrono-exactes-3": "lucidite", "chrono-niveau-2": "sagesse",
          "chrono-niveau-4": "sagesse", "chrono-rapides": "mecanique", "chrono-anachronismes": "eloquence"}

# Genre des conditions pour les crédits (outils/credits.py).
GENRES = {"chronos_joues": "petit", "chronos_parfaits": "jalon", "dates_exactes_partie": "exploit", "dates_niveau": "jalon",
          "dates_rapides": "jalon", "dates_fausses": "honte"}

# Illustration de chaque succès (outils/succes_pixels.py).
ILLUSTRATIONS = {"chrono-1": ("icone", "zero"), "chrono-10": ("icone", "astrolabe"), "chrono-50": ("dessin", "sablier"),
                 "chrono-parfait-1": ("dessin", "sablier"), "chrono-parfait-10": ("dessin", "plante"),
                 "chrono-exactes-3": ("dessin", "loupe"), "chrono-niveau-2": ("icone", "plume"),
                 "chrono-niveau-4": ("icone", "enluminure"), "chrono-rapides": ("icone", "atome"),
                 "chrono-anachronismes": ("icone", "couronne")}


def repliques():
    """Au format de outils/ia.py : (contexte → lignes), les sans-référence en tuples ("", texte)."""
    return REPLIQUES
