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
    42: ({"type": "revision"}, "En 1764, Diderot découvre que son libraire a censuré en cachette les derniers volumes. Depuis, l'Encyclopédie se relit avec soin. Vous aussi."),
    50: ({"type": "revision"}, "Darwin a publié six éditions de L'Origine des espèces et n'a ajouté « la survie du plus apte » qu'à la cinquième. Réviser, c'est scientifique."),
    62: ({"type": "teleport", "vers": 53}, "Le premier site web, perdu, n'a été remis en ligne par le CERN qu'en 2013. Lien mort : retour au tableau de Mendeleïev."),
}

TEXTES = {
    "teleport": "Téléportation : retour à la case {vers}.",
    "revision": "Révision forcée : l'IA choisit une compétence que tu maîtrises. Ton pion ne bouge plus avant de l'avoir révisée.",
}

REPLIQUES = {
    "teleport": [
        "Téléportation. En 1993, Charles Bennett et ses collègues ont montré qu'on pouvait téléporter un état quantique. Votre pion, lui, n'a pas lu l'article et part dans le mauvais sens.",
        "Retour en arrière. Les idées justes aussi se perdent : Aristarque l'a appris pendant dix-huit siècles. Vous, c'est quelques cases.",
        sans("Pof. Votre pion a disparu. Ah non, il est là, plus loin derrière. Je n'ai pas encore réglé la machine."),
        sans("Je vous téléporte. Je n'ai jamais dit dans quel sens."),
    ],
    "revision": [
        "Révision forcée. Selon Roediger et Karpicke, en 2006, se tester fait mieux retenir que relire. Donc je vous teste.",
        "Ebbinghaus oubliait plus de la moitié de ses syllabes en une heure. Je préfère vérifier ce qu'il vous reste.",
        sans("Vous croyiez cette compétence rangée au chaud ? Je la ressors. Montrez-moi qu'elle est toujours là."),
        sans("Pas un pas de plus avant une petite révision. Considérez-moi comme votre conscience, mais avec un chronomètre."),
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

TONS = {"jouer_revision": "moqueuse", "teleport": "moqueuse", "revision": "moqueuse", "revision_reussie": "impressionnee", "revision_ratee": "decue"}
