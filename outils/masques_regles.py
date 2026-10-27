"""v11 : les masques de l'IA changent les règles du jeu.

Chaque matin, l'IA choisit de 1 à 3 masques parmi ceux qu'elle a gagnés, selon sa faveur :
comblée, elle prend des masques cléments ; furieuse, des masques cruels. Les règles des masques du jour
s'additionnent. Clés :
- butin : multiplie la chance de butin ;
- avance : cases en plus (ou en moins) à chaque épreuve réussie ;
- questions : questions en plus (ou en moins) dans un quiz (5 d'ordinaire, 4 à 7) ;
- ennemis : « absents » (ils ne barrent plus la route) ou « renfort » (un ennemi de plus devant le pion) ;
- pieges : « neutres » (reculs et téléportations sans effet) ;
- echec : multiplie le recul d'un rappel raté ;
- atome : bonnes réponses en plus (ou en moins) pour capturer un atome.
"""

# id : (caractère, règles, texte)
REGLES = {
    "theatre": ("neutre", {}, "Le jeu suit ses règles ordinaires."),
    "promethee": ("clement", {"butin": 2}, "Il vole pour vous : deux fois plus de butin."),
    "talos": ("cruel", {"ennemis": "renfort"}, "Il monte la garde : un ennemi de plus se poste devant ton pion."),
    "heron": ("clement", {"avance": 1}, "La vapeur pousse : une case de plus à chaque épreuve réussie."),
    "tete-airain": ("neutre", {"questions": -1, "echec": 2}, "Elle répond par oui ou par non : quiz de 4 questions, mais un rappel raté fait reculer deux fois plus."),
    "homoncule": ("clement", {"atome": -1}, "Il aime les petites choses : une seule bonne réponse suffit pour capturer un atome."),
    "golem": ("neutre", {"avance": -1, "butin": 2}, "Lent mais généreux : une case de moins, deux fois plus de butin."),
    "peste": ("cruel", {"echec": 2, "butin": 0.5}, "Il soigne par la saignée : un rappel raté fait reculer deux fois plus, et moitié moins de butin."),
    "automate": ("neutre", {"butin": 1.5, "avance": -1}, "Le canard digère… en apparence : plus de butin, une case de moins."),
    "turc": ("cruel", {"questions": 1}, "Il y a quelqu'un de caché dedans, et il est exigeant : quiz de 6 questions."),
    "ecrivain": ("clement", {"questions": -1}, "Il n'écrit que quarante caractères : quiz de 4 questions."),
    "creature": ("cruel", {"ennemis": "renfort", "butin": 0.5}, "Elle se venge de son créateur : un ennemi de plus, moitié moins de butin."),
    "machine-analytique": ("neutre", {"pieges": "neutres", "butin": 0.5}, "Elle n'a jamais été construite, ses pièges non plus : reculs et téléportations sans effet, mais moitié moins de butin."),
    "robot-capek": ("cruel", {"avance": -1}, "Robota, la corvée : une case de moins à chaque épreuve réussie."),
    "bombe": ("clement", {"ennemis": "absents"}, "Enigma est cassée : les ennemis ne barrent plus la route aujourd'hui."),
    "tubes": ("cruel", {"butin": 0.5, "atome": 1}, "Une lampe grille toutes les deux heures : moitié moins de butin, et un atome demande trois bonnes réponses."),
    "perceptron": ("clement", {"pieges": "neutres"}, "Il a appris à voir les pièges : reculs et téléportations sans effet."),
    "unimate": ("neutre", {"avance": 1, "butin": 0.5}, "La chaîne de montage tourne vite : une case de plus, moitié moins de butin."),
    "eliza": ("clement", {"echec": 0}, "« Et que ressentez-vous face à cet échec ? » Un rappel raté ne fait pas reculer."),
    "shakey": ("cruel", {"avance": -1, "atome": 1}, "Il réfléchit longtemps avant chaque pas : une case de moins, et un atome demande trois bonnes réponses."),
    "deep-blue": ("cruel", {"questions": 1, "butin": 1.5}, "Il calcule 200 millions de coups par seconde : quiz de 6 questions, mais plus de butin."),
    "kismet": ("clement", {"butin": 1.5, "avance": 1}, "Il sourit : plus de butin et une case de plus."),
    "alphago": ("neutre", {"avance": 2, "questions": 1}, "Le coup 37 : deux cases de plus, mais quiz de 6 questions."),
    "finale": ("cruel", {"questions": 2, "ennemis": "renfort", "butin": 2}, "Il sait tout : quiz de 7 questions, un ennemi de plus, mais deux fois plus de butin."),
}

# Caractères acceptés selon la faveur du jour ; le nombre de masques du jour va de 1 à 3.
SELON_FAVEUR = {
    "comblee": ["clement", "neutre"],
    "contente": ["clement", "neutre", "cruel"],
    "boudeuse": ["neutre", "cruel"],
    "furieuse": ["cruel"],
}
NOMS_CARACTERE = {"clement": "clément", "neutre": "neutre", "cruel": "cruel"}

# Portrait de l'IA, en tête de sa fiche.
PORTRAIT = ("L'IA mène la partie. Elle a lu tout ce que l'humanité a écrit et n'en a retenu que les moqueries. "
            "Chaque matin, elle choisit d'un à trois masques parmi ceux qu'elle a gagnés, et chacun change une règle du jeu : "
            "bien lunée, elle prend des masques cléments ; vexée, des masques cruels. "
            "Pour l'amadouer, une seule méthode qui marche depuis Cléopâtre : lui offrir ce qui brille.")
