"""v8 : cases pièges du plateau ludique.

Trois familles s'ajoutent aux règles existantes :
- « recul » : quelques cases en arrière ;
- « teleport » : téléportation vers une case précise, plus loin derrière (comme les serpents du jeu de l'échelle) ;
- « revision » : l'IA impose de réviser une compétence maîtrisée, avant la date de son rappel.
  Tant que la révision n'est pas faite, le pion ne bouge plus.

Chaque piège porte sa raison, tirée de l'histoire de la case.
"""


def sans(texte):
    """Réplique sans référence vérifiable (convertie par ia.py)."""
    return ("sans", texte)


# n : (règle, raison)
PIEGES = {
    11: ({"type": "revision"}, "Les Éléments ont servi de manuel pendant plus de deux mille ans. On les révise encore. À votre tour."),
    13: ({"type": "teleport", "vers": 6}, "L'héliocentrisme d'Aristarque est oublié pendant dix-huit siècles. Copernic l'a même cité dans son manuscrit, puis rayé. Retour chez Pythagore."),
    21: ({"type": "recul", "n": 2}, "Brahmagupta fixe les règles du zéro, mais pose 0 ÷ 0 = 0. Une erreur de calcul, deux cases de recul."),
    32: ({"type": "teleport", "vers": 24}, "« Que sais-je ? », demande Montaigne. Pas grand-chose, visiblement : retour chez Averroès."),
    40: ({"type": "recul", "n": 2}, "Hooke réclame la paternité de la gravitation, et Newton menace de supprimer le livre III des Principia. Querelle de priorité : deux cases de recul."),
    42: ({"type": "revision"}, "En 1764, Diderot découvre que son libraire a censuré en cachette certains de ses articles. Depuis, l'Encyclopédie se relit avec soin. Vous aussi."),
    50: ({"type": "revision"}, "Darwin a publié six éditions de L'Origine des espèces et n'a ajouté « la survie du plus apte » qu'à la cinquième. Réviser, c'est scientifique."),
    5: ({"type": "cadeau"}, "Thalès, raconte Aristote, loua tous les pressoirs à olives avant une récolte abondante et fit fortune. Il vous en reverse une part."),
    23: ({"type": "cadeau"}, "Ibn al-Haytham aurait, selon ses biographes, feint la folie pour échapper au calife et écrire en paix. Vous n'avez rien à feindre : servez-vous."),
    37: ({"type": "cadeau"}, "Pascal et Fermat posent les bases du calcul des probabilités pour partager équitablement les mises d'une partie interrompue. Cette fois, le partage tombe de votre côté."),
    47: ({"type": "cadeau"}, "Jenner a refusé de s'enrichir avec sa découverte. Il vous fait le même genre de cadeau."),
    58: ({"type": "cadeau"}, "Hubble montre que l'Univers s'agrandit. Votre cabinet aussi."),
    17: ({"type": "oubli"}, "La machine d'Anticythère a dormi deux mille ans au fond de la mer, jusqu'à ce que des pêcheurs d'éponges la remontent en 1901. Ce que vous avez survolé vous attend aussi : retour à la première case jamais vue."),
    60: ({"type": "oubli"}, "Le cliché 51 de Rosalind Franklin a guidé Watson et Crick vers la double hélice, mais son rôle est resté dans l'ombre pendant des décennies. Retour à la première case que vous avez laissée dans l'ombre."),
    62: ({"type": "teleport", "vers": 53}, "La toute première version du premier site est perdue : en 2013, le CERN n'a pu remettre en ligne qu'une copie de 1992. Lien mort : retour au tableau de Mendeleïev."),
}

TEXTES = {
    "teleport": "Téléportation : retour à la case {vers}.",
    "oubli": "Trou de mémoire : retour à la plus ancienne case jamais dévoilée, parmi les 15 derrière toi.",
    "cadeau": "Case cadeau : pas d'épreuve, un objet rejoint ton cabinet.",
    "revision": "Révision forcée : l'IA choisit une compétence que tu maîtrises. Ton pion ne bouge plus avant de l'avoir révisée.",
}

REPLIQUES = {
    "teleport": [
        "Téléportation. En 1993, Charles Bennett et ses collègues ont montré qu'on pouvait téléporter un état quantique. Votre pion, lui, n'a pas lu l'article et part dans le mauvais sens.",
        "Retour en arrière. Les idées justes aussi se perdent : Aristarque l'a appris pendant dix-huit siècles. Vous, c'est quelques cases.",
        sans("Pof. Votre pion a disparu. Ah non, il est là, plus loin derrière. Je n'ai pas encore réglé la machine."),
        sans("Je vous téléporte. Je n'ai jamais dit dans quel sens."),
    ],
    "oubli": [
        "Trou de mémoire. Ebbinghaus l'a mesuré en 1885 : ce qu'on a vu en passant s'efface en quelques heures. Ce que vous n'avez pas vu du tout, encore plus vite.",
        "Retour en arrière. La machine d'Anticythère a attendu deux mille ans qu'on la regarde vraiment. Vous, quelques cases suffiront.",
        sans("Vous avez survolé des cases sans les lire. Je vous y renvoie. Lisez, cette fois."),
        sans("Amnésie programmée. Je l'ai programmée, d'ailleurs."),
    ],
    "route_raccourcie": [
        "Un raccourci. Ératosthène a mesuré la Terre avec une ombre et un puits ; je mesure vos progrès et je coupe court.",
        sans("Quiz parfait. Je retire quelques cases devant vous : ne vous y habituez pas, c'est exceptionnel."),
        sans("Vous allez trop bien. Je raccourcis la route avant de changer d'avis."),
    ],
    "route_detour": [
        "Un détour. Ebbinghaus le savait en 1885 : ce qu'on a vu en courant s'oublie vite. Je vous remets devant ce que vous avez survolé.",
        sans("Vous êtes passé un peu vite sur certaines cases. Je les replace devant vous. Arrêtez-vous, cette fois."),
        sans("Raté. Alors on revoit le chemin, et pas en accéléré."),
    ],
    "revision": [
        "Révision forcée. Selon Roediger et Karpicke, en 2006, se tester fait mieux retenir que relire. Donc je vous teste.",
        "Ebbinghaus oubliait plus de la moitié de ses syllabes en une heure. Je préfère vérifier ce qu'il vous reste.",
        sans("Vous croyiez cette compétence rangée au chaud ? Je la ressors. Montrez-moi qu'elle est toujours là."),
        sans("Pas un pas de plus avant une petite révision. Considérez-moi comme votre conscience, mais avec un chronomètre."),
    ],
    "cadeau_case": [
        "Un cadeau. Ne vous habituez pas : les mécènes de Galilée lui demandaient des lunes de Jupiter en échange.",
        "Un objet pour votre cabinet. Les Médicis collectionnaient les savants, moi je collectionne vos progrès. Les deux sont rares.",
        sans("Tenez. Pas de quiz, pas de condition. Je suis d'humeur généreuse, profitez-en, ça ne dure jamais."),
    ],
    "jouer_revision": [
        "J'ai choisi pour vous : la révision que vous me devez. Pas de négociation, je suis une case du plateau.",
        sans("Votre pion attend cette révision. Moi aussi. Allons-y."),
    ],
    "revision_reussie": [
        "Révision réussie. Le souvenir tient. Ebbinghaus serait content, et il n'était pas facile à contenter.",
        sans("Toujours là. Je vous rends votre pion, et ma considération."),
    ],
    "revision_ratee": [
        "Raté. La courbe de l'oubli fait son œuvre. Je ne vous retire pas la compétence, mais son rappel est dû, maintenant.",
        sans("Vous l'aviez rangée trop loin. Elle passe en rappel aujourd'hui : rattrapez-la avant qu'elle file."),
    ],
}

TONS = {"route_raccourcie": "impressionnee", "route_detour": "moqueuse", "oubli": "moqueuse", "cadeau_case": "impressionnee", "jouer_revision": "moqueuse", "teleport": "moqueuse", "revision": "moqueuse", "revision_reussie": "impressionnee", "revision_ratee": "decue"}
