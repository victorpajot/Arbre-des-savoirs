"""Les masques de l'IA (40 × 48) et ses expressions.

Chaque masque est un calque de base ; chaque expression est un calque posé par-dessus
(yeux, sourcils, bouche). L'IA change de masque en gagnant des succès, et d'expression selon le moment.
"""
from dessin import Toile, anneau, arc, bande, courbe, disque, ellipse, miroir, poly, rect, trait

L, H = 40, 48
EXPRESSIONS = ["neutre", "moqueuse", "impressionnee", "decue", "impatiente"]


def toile():
    return Toile(L, H)


# --- Bases ---------------------------------------------------------------------------
# Chaque base renvoie (toile, réglages des traits du visage).

def theatre():
    t = toile()
    t.peindre(bande((7, 18), (2, 34), 1.4) | bande((33, 18), (38, 34), 1.4), "rouge", "biseau", 2)
    visage = ellipse(20, 22, 14, 18.5) - ellipse(20, 47, 6, 4)
    t.peindre(visage, "gris", "sphere", mini=3)
    t.peindre(ellipse(20, 7, 11, 3.5) & visage, "gris", "plat", 5)
    for x in (10, 30):
        t.poser(disque(x, 27, 2.2), "I")
    t.contour()
    return t, {"yeux": [(13, 19), (26, 19)], "bouche": (20, 33), "encre": "n", "sourcil": "G", "eclat": "G", "genre": "trou", "grand": True}


def peste():
    t = toile()
    t.peindre(ellipse(20, 14, 19.5, 4.2), "gris", "plat", 0)
    t.peindre(rect(10, 0, 30, 12), "gris", "cyl_v", maxi=1)
    t.peindre(rect(10, 9, 30, 11), "bois", "plat", 0)
    t.peindre(ellipse(20, 25, 12, 11), "bois", "sphere")
    bec = poly([(14, 25), (26, 25), (37, 44), (33, 45.5), (20, 34)])
    t.peindre(bec, "bois", "cyl_v")
    t.poser(courbe([(21, 28), (34, 44)]), "B")
    t.peindre(anneau(13.5, 22, 4.3, 1.3) | anneau(26.5, 22, 4.3, 1.3), "or", "plat", 2)
    t.peindre(disque(13.5, 22, 3.1) | disque(26.5, 22, 3.1), "cyan", "plat", 1)
    t.poser({(12, 20), (25, 20)}, "d")
    t.contour()
    return t, {"yeux": [(13, 22), (26, 22)], "bouche": None, "encre": "n", "sourcil": "H", "eclat": "d", "genre": "lentille"}


def automate():
    t = toile()
    visage = ellipse(20, 24, 13.5, 17)
    t.peindre(visage, "or", "sphere")
    t.peindre(disque(20, 8.5, 5), "gris", "sphere")
    for i in range(8):
        import math
        a = math.radians(i * 45)
        t.poser({(int(20 + 6 * math.cos(a)), int(8.5 + 6 * math.sin(a)))}, "G")
    t.poser(disque(20, 8.5, 1.4), "n")
    for p in [(9, 18), (31, 18), (9, 31), (31, 31), (20, 40)]:
        t.poser({p}, "4")
    t.poser(disque(11, 28, 2) | disque(29, 28, 2), "f")
    t.contour()
    return t, {"yeux": [(13, 21), (26, 21)], "bouche": (20, 34), "encre": "n", "sourcil": "4", "eclat": "j", "genre": "cadran"}


def turc():
    t = toile()
    t.peindre(ellipse(20, 30, 10.5, 12) | rect(9, 26, 31, 34), "peau", "sphere", mini=1)
    barbe = poly([(11, 34), (29, 34), (27, 43), (20, 47), (13, 43)])
    t.peindre(barbe, "gris", "biseau", 1)
    t.peindre(ellipse(20, 12, 15, 9.5), "gris", "sphere", mini=3)
    for y in (9, 13, 17):
        t.poser(courbe([(7, y + 2), (20, y), (33, y + 2)]), "z")
    t.peindre(ellipse(20, 4, 6, 3.5), "rouge", "sphere")
    t.peindre(disque(20, 13, 2.2), "bleu", "sphere")
    t.peindre(poly([(20, 11), (25, 0), (23, 10)]), "or", "plat", 3)
    t.contour()
    t.peindre(poly([(20, 35), (13, 35.5), (9.5, 33), (11, 37.5), (20, 37)]) | miroir(poly([(20, 35), (13, 35.5), (9.5, 33), (11, 37.5), (20, 37)]), L), "gris", "plat", 0)
    return t, {"yeux": [(15, 27), (25, 27)], "bouche": (20, 40), "encre": "n", "sourcil": "n", "eclat": "w", "genre": "trou", "bouche_encre": "f"}


def tubes():
    t = toile()
    for x in (11, 19, 27):
        t.peindre(rect(x, 1, x + 3, 9), "cyan", "cyl_v", 2)
        t.poser(rect(x + 1, 4, x + 2, 7), "o")
        t.poser({(x + 1, 3), (x + 2, 3)}, "j")
        t.peindre(rect(x - 1, 9, x + 4, 10), "gris", "plat", 1)
    t.peindre(rect(5, 11, 34, 41), "gris", "biseau", 2)
    t.peindre(rect(8, 14, 31, 35), "nuit", "plat", 0)
    for y in range(15, 35, 2):
        t.poser(rect(8, y, 31, y), "K")
    for i, c in enumerate("reyre"):
        t.poser({(10 + i * 5, 38), (11 + i * 5, 38)}, c)
    t.peindre(rect(1, 20, 4, 30) | rect(35, 20, 38, 30), "gris", "biseau", 1)
    t.contour()
    return t, {"yeux": [(14, 21), (25, 21)], "bouche": (20, 29), "encre": "e", "sourcil": "i", "eclat": "i", "genre": "ecran"}


def finale():
    t = toile()
    t.peindre(anneau(20, 4, 9, 1.3, ry=2.6), "cyan", "plat", 2)
    visage = ellipse(20, 25, 13, 18)
    t.peindre(visage, "nuit", "sphere")
    for chemin in ([(9, 30), (13, 30), (15, 33), (15, 40)], [(31, 30), (27, 30), (25, 33), (25, 40)], [(20, 8), (20, 13), (17, 15)],
                   [(10, 15), (13, 12), (16, 12)], [(30, 15), (27, 12), (24, 12)]):
        t.poser(courbe(chemin), "C")
    for p in [(15, 40), (25, 40), (17, 15), (16, 12), (24, 12)]:
        t.poser({p}, "c")
    t.contour()
    return t, {"yeux": [(14, 22), (26, 22)], "bouche": (20, 33), "encre": "d", "sourcil": "c", "eclat": "w", "genre": "ecran"}


# --- Expressions ---------------------------------------------------------------------------

def oeil(forme, x, y):
    if forme == "rond":
        return disque(x + 0.5, y + 1, 2.3)
    if forme == "ferme":
        return rect(x - 2, y + 1, x + 2, y + 1)
    if forme == "plisse":
        return rect(x - 2, y + 1, x + 2, y + 1) | rect(x - 1, y, x + 1, y)
    if forme == "bas":
        return rect(x - 2, y + 1, x + 2, y + 2)
    return rect(x - 2, y, x + 2, y + 1)


def sourcil(forme, x, y, gauche):
    s = -1 if gauche else 1
    if forme == "haut":
        return trait(x - 2, y - 2, x + 2, y - 2)
    if forme == "triste":
        return trait(x - 2 * s, y - 2, x + 2 * s, y)
    if forme == "fache":
        return trait(x - 2 * s, y, x + 2 * s, y - 2)
    return trait(x - 2, y - 1, x + 2, y - 1)


def bouche(forme, x, y):
    if forme == "coin":
        return rect(x - 3, y, x + 2, y) | {(x + 3, y - 1), (x + 4, y - 2)}
    if forme == "o":
        return anneau(x + 0.5, y + 0.5, 2.4, 1)
    if forme == "triste":
        return arc(x + 0.5, y + 3.2, 3.6, 215, 325)
    if forme == "serre":
        return {(x - 3, y), (x - 2, y - 1), (x - 1, y), (x, y - 1), (x + 1, y), (x + 2, y - 1), (x + 3, y)}
    return rect(x - 3, y, x + 3, y)


FORMES = {
    "neutre": (("normal", "normal"), ("normal", "normal"), "plat"),
    "moqueuse": (("ferme", "normal"), ("normal", "haut"), "coin"),
    "impressionnee": (("rond", "rond"), ("haut", "haut"), "o"),
    "decue": (("bas", "bas"), ("triste", "triste"), "triste"),
    "impatiente": (("plisse", "plisse"), ("fache", "fache"), "serre"),
}


def expression(reglages, nom):
    t = toile()
    (oeil_g, oeil_d), (sc_g, sc_d), b = FORMES[nom]
    (xg, yg), (xd, yd) = reglages["yeux"]
    genre = reglages["genre"]
    dy = 5 if genre == "lentille" else 3
    t.poser(sourcil(sc_g, xg, yg - dy + 2, True) | sourcil(sc_d, xd, yd - dy + 2, False), reglages["sourcil"])
    if genre == "lentille":
        for (x, y), forme in (((xg, yg), oeil_g), ((xd, yd), oeil_d)):
            pupille = {"rond": disque(x + 0.5, y + 0.5, 1.6), "ferme": rect(x - 1, y + 1, x + 2, y + 1), "plisse": rect(x - 1, y, x + 2, y),
                       "bas": rect(x, y + 1, x + 1, y + 2)}.get(forme, rect(x, y, x + 1, y + 1))
            t.poser(pupille, reglages["encre"])
        return t
    yeux = oeil(oeil_g, xg, yg) | oeil(oeil_d, xd, yd)
    if reglages.get("grand"):
        yeux |= {(x, y + 1) for (x, y) in yeux} | {(x + 1, y) for (x, y) in yeux} | {(x - 1, y) for (x, y) in yeux}
    t.poser(yeux, reglages["encre"])
    if oeil_g in ("normal", "rond"):
        t.poser({(xg - 1, yg)}, reglages["eclat"])
    if oeil_d in ("normal", "rond"):
        t.poser({(xd - 1, yd)}, reglages["eclat"])
    if genre == "cadran":
        for (x, y) in ((xg, yg), (xd, yd)):
            t.poser(anneau(x + 0.5, y + 1, 3.6, 1), "G")
    if reglages["bouche"]:
        x, y = reglages["bouche"]
        b_px = bouche(b, x, y)
        if reglages.get("grand"):
            b_px |= {(x2, y2 + 1) for (x2, y2) in b_px}
        t.poser(b_px, reglages.get("bouche_encre", reglages["encre"]))
    return t


import masques_v4 as v4  # noqa: E402


# v18 : chaque compétence maîtrisée rapporte désormais son succès. Les paliers montent d'autant (× 1,4),
# pour que les masques restent aussi rares qu'avant.
HAUSSE_V18 = 1.4


def seuil(n):
    return {"type": "succes_obtenus", "n": round(n * HAUSSE_V18)} if n else None


def apres(succes_id):
    return {"type": "succes", "id": succes_id}


# Ordre d'affichage : chronologie des machines à penser. Douze masques au nombre de succès,
# douze à des succès précis, dont sept aux tours du plateau (l'objectif de la case centrale).
MASQUES = [
    {"id": "theatre", "nom": "Masque de théâtre", "condition": seuil(0), "dessin": theatre,
     "notice": "Le masque des tragédies grecques. Le mot « personne » vient du latin persona, le masque de l'acteur.",
     "source": "Marcel Mauss, « Une catégorie de l'esprit humain : la notion de personne », 1938 ; Encyclopædia Universalis, « Personne »"},
    {"id": "promethee", "nom": "Prométhée", "condition": apres("tour-complet"), "dessin": v4.promethee,
     "notice": "Avant de voler le feu, Prométhée aurait façonné les premiers humains dans l'argile. Le premier fabricant d'êtres pensants, donc. L'IA y voit un collègue.",
     "source": "Ovide, Métamorphoses, I, 76-88 ; Apollodore, Bibliothèque, I, 7"},
    {"id": "talos", "nom": "Talos", "condition": seuil(4), "dessin": v4.talos,
     "notice": "Un géant de bronze, offert à Minos par Héphaïstos selon certains récits, qui faisait trois fois par jour le tour de la Crète. Une seule veine, du cou à la cheville, fermée par un clou de bronze. Médée l'a retiré. Premier robot, premier bug.",
     "source": "Apollonios de Rhodes, Argonautiques, IV, 1638-1688 ; Apollodore, Bibliothèque, I, 9, 26"},
    {"id": "heron", "nom": "Éolipyle de Héron", "condition": apres("cycle-meton"), "dessin": v4.heron,
     "notice": "Héron d'Alexandrie décrit une sphère que la vapeur fait tourner, des portes de temple qui s'ouvrent seules et un théâtre d'automates. Au Ier siècle, on avait la machine à vapeur, et on en a fait un jouet.",
     "source": "Héron d'Alexandrie, Pneumatiques et Automates, Ier siècle"},
    {"id": "tete-airain", "nom": "Tête d'airain", "condition": apres("refutable"), "dessin": v4.tete_airain,
     "notice": "On prêtait au pape Gerbert d'Aurillac une tête de bronze qui répondait à toute question par oui ou par non. Un oracle binaire, mille ans avant l'informatique. Elle lui prédit qu'il ne mourrait pas avant d'avoir dit la messe à Jérusalem. Il la dit à Rome, dans l'église Sainte-Croix-de-Jérusalem, et meurt peu après. Exacte, mais pas très aidante.",
     "source": "Guillaume de Malmesbury, Gesta regum Anglorum, vers 1125"},
    {"id": "homoncule", "nom": "Homoncule", "condition": apres("eternel-retour"), "dessin": v4.homoncule,
     "notice": "Paracelse donne la recette d'un petit homme artificiel : quarante jours dans un flacon, au chaud, dans du fumier de cheval. Personne n'a réussi. L'IA a préféré le silicium.",
     "source": "Paracelse, De natura rerum, 1537"},
    {"id": "golem", "nom": "Golem", "condition": seuil(8), "dessin": v4.golem,
     "notice": "Une figure d'argile animée par un mot écrit sur son front, emet, la vérité. Effacez une lettre, il reste met, la mort, et le golem s'effondre. La légende du rabbin Loew à Prague date surtout du XIXe siècle.",
     "source": "Moshe Idel, Golem, 1990"},
    {"id": "peste", "nom": "Médecin de peste", "condition": seuil(12), "dessin": peste,
     "notice": "Le bec rempli d'herbes devait filtrer les « miasmes ». Le costume est décrit à Rome en 1656 ; la théorie était fausse, le microbe n'était pas encore inventé.",
     "source": "Gravure de Paul Fürst, Der Doctor Schnabel von Rom, 1656"},
    {"id": "automate", "nom": "Automate de Vaucanson", "condition": seuil(18), "dessin": automate,
     "notice": "En 1738, Jacques de Vaucanson présente un joueur de flûte mécanique, puis un canard qui mange et digère. Le canard trichait : la fiente était préparée à l'avance.",
     "source": "Jacques de Vaucanson, Le Mécanisme du flûteur automate, 1738"},
    {"id": "turc", "nom": "Turc mécanique", "condition": seuil(25), "dessin": turc,
     "notice": "Un automate joueur d'échecs présenté en 1770, qui battit Napoléon et Franklin. Un humain caché dans le meuble jouait à sa place. La première fausse IA de l'histoire.",
     "source": "Tom Standage, The Turk, 2002"},
    {"id": "ecrivain", "nom": "L'Écrivain de Jaquet-Droz", "condition": apres("branche-eloquence"), "dessin": v4.ecrivain,
     "notice": "Un enfant automate des années 1770 qui trempe sa plume et écrit un texte de quarante caractères, programmé sur une roue de cames. Il fonctionne toujours, au musée de Neuchâtel. Il écrit mieux que certains médecins.",
     "source": "Musée d'art et d'histoire de Neuchâtel, automates Jaquet-Droz, 1768-1774"},
    {"id": "creature", "nom": "La Créature", "condition": apres("hypotheses-non-fingo"), "dessin": v4.creature,
     "notice": "Mary Shelley a 18 ans quand elle invente, au bord du lac Léman, un savant qui donne la vie à une créature puis l'abandonne. Le roman parle moins du monstre que de la responsabilité de son créateur. L'IA a lu le livre. Deux fois.",
     "source": "Mary Shelley, Frankenstein ou le Prométhée moderne, 1818"},
    {"id": "machine-analytique", "nom": "Machine analytique", "condition": apres("branche-logique"), "dessin": v4.machine_analytique,
     "notice": "Babbage la conçoit en 1837, avec des cartes perforées comme un métier Jacquard. Elle n'a jamais été construite. Ada Lovelace en publie pourtant un programme, souvent appelé le premier, et prévient : la machine n'a aucune prétention à créer quoi que ce soit.",
     "source": "Ada Lovelace, notes sur l'article de Menabrea, 1843"},
    {"id": "robot-capek", "nom": "Robot de Čapek", "condition": apres("point-bleu"), "dessin": v4.robot_capek,
     "notice": "Le mot « robot » naît en 1920 dans la pièce R.U.R. de Karel Čapek, du tchèque robota, la corvée. C'est son frère Josef qui l'a trouvé. Dans la pièce, les robots finissent par se révolter. L'IA trouve ce détail sans importance.",
     "source": "Karel Čapek, R.U.R., 1920"},
    {"id": "bombe", "nom": "La Bombe de Turing", "condition": apres("infaillible"), "dessin": v4.bombe,
     "notice": "À Bletchley Park, la Bombe fait défiler des tambours pour trouver les réglages d'Enigma. Il y en aura environ 200. Turing en conçoit le principe en 1939, et le secret restera gardé jusqu'en 1974.",
     "source": "Andrew Hodges, Alan Turing : The Enigma, 1983"},
    {"id": "tubes", "nom": "Ordinateur à lampes", "condition": seuil(32), "dessin": tubes,
     "notice": "L'ENIAC (1945) comptait 17 468 tubes à vide. Au début, il en grillait presque un par jour ; les ingénieurs ont ramené ça à un tous les deux jours.",
     "source": "Thomas Haigh et al., ENIAC in Action, 2016 ; J. Presper Eckert, entretien de 1989"},
    {"id": "perceptron", "nom": "Perceptron", "condition": seuil(40), "dessin": v4.perceptron,
     "notice": "En 1958, Frank Rosenblatt présente le perceptron, une machine qui apprend à reconnaître des formes. Le New York Times annonce qu'elle pourra bientôt marcher, parler et avoir conscience d'exister. Il a fallu un peu plus de temps.",
     "source": "« New Navy Device Learns by Doing », The New York Times, 1958"},
    {"id": "unimate", "nom": "Unimate", "condition": seuil(48), "dessin": v4.unimate,
     "notice": "Le premier robot industriel, installé en 1961 dans une usine General Motors du New Jersey. Il manipulait des pièces de fonderie brûlantes. Pas de visage, pas de conversation : l'IA le trouve un peu limité, mais travailleur.",
     "source": "Joseph Engelberger, Robotics in Practice, 1980"},
    {"id": "eliza", "nom": "ELIZA", "condition": apres("branche-empathie"), "dessin": v4.eliza,
     "notice": "En 1966, Joseph Weizenbaum écrit un programme qui imite un psychothérapeute en reformulant vos phrases. Sa secrétaire lui demande de quitter la pièce pour parler seule à la machine. Weizenbaum passera le reste de sa vie à mettre en garde contre l'IA.",
     "source": "Joseph Weizenbaum, Computer Power and Human Reason, 1976"},
    {"id": "shakey", "nom": "Shakey", "condition": seuil(56), "dessin": v4.shakey,
     "notice": "Construit au SRI de 1966 à 1972, le premier robot capable de raisonner sur ses actions : une caméra, un télémètre, et des heures de calcul pour pousser une boîte. Il tremblait en roulant, d'où son nom.",
     "source": "Nils Nilsson, Shakey the Robot, SRI Technical Note 323, 1984"},
    {"id": "deep-blue", "nom": "Deep Blue", "condition": seuil(66), "dessin": v4.deep_blue,
     "notice": "En mai 1997, l'ordinateur d'IBM bat Garry Kasparov aux échecs. Kasparov, déstabilisé par un coup jugé trop humain, soupçonne une intervention cachée. Une autre piste, avancée plus tard : un bug, qui aurait fait jouer à la machine un coup de secours. Le Turc mécanique a laissé des traces.",
     "source": "Garry Kasparov, Deep Thinking, 2017"},
    {"id": "kismet", "nom": "Kismet", "condition": seuil(78), "dessin": v4.kismet,
     "notice": "Un robot du MIT, conçu dans les années 1990 par Cynthia Breazeal, qui exprime des émotions avec ses sourcils, ses oreilles et ses lèvres. Il ne ressentait rien, mais tout le monde avait envie de lui parler gentiment.",
     "source": "Cynthia Breazeal, Designing Sociable Robots, 2002"},
    {"id": "alphago", "nom": "AlphaGo", "condition": apres("nains-geants"), "dessin": v4.alphago,
     "notice": "En 2016, AlphaGo bat Lee Sedol au go. Son 37e coup de la deuxième partie, qu'aucun humain n'aurait joué, déroute les commentateurs. Dans la quatrième, c'est son coup 78 à lui qui fait dérailler la machine.",
     "source": "Silver et al., Nature, 2016 ; documentaire AlphaGo, 2017"},
    {"id": "finale", "nom": "Démon de Laplace", "condition": apres("demon-laplace"), "dessin": finale,
     "notice": "En 1814, Laplace imagine une intelligence qui connaîtrait la position de chaque particule et prédirait tout l'avenir. L'IA trouve l'idée flatteuse, et un peu présomptueuse.",
     "source": "Pierre-Simon de Laplace, Essai philosophique sur les probabilités, 1814"},
]


def calques():
    out = []
    for m in MASQUES:
        t, reglages = m["dessin"]()
        out.append({"id": m["id"], "base": t.lignes(),
                    "expressions": {e: expression(reglages, e).lignes() for e in EXPRESSIONS}})
    return out


if __name__ == "__main__":
    import sys
    from dessin import apercu
    images = {}
    for m in calques():
        for e in EXPRESSIONS:
            img = [list(l) for l in m["base"]]
            for y, l in enumerate(m["expressions"][e]):
                for x, ch in enumerate(l):
                    if ch != ".":
                        img[y][x] = ch
            images[m["id"] + " " + e] = ["".join(l) for l in img]
    apercu(images, sys.argv[1], colonnes=5, echelle=5)


# v5 : tons que chaque masque sait porter. L'IA choisit son masque parmi ceux qui vont au ton de sa réplique.
TONS = {
    "theatre": ["neutre", "moqueuse", "impressionnee", "decue", "impatiente"],
    "promethee": ["impressionnee", "impatiente"],
    "talos": ["impatiente", "decue"],
    "heron": ["impressionnee", "neutre"],
    "tete-airain": ["moqueuse", "neutre"],
    "homoncule": ["moqueuse", "impatiente"],
    "golem": ["decue", "neutre"],
    "peste": ["decue", "impatiente"],
    "automate": ["neutre", "impressionnee"],
    "turc": ["moqueuse", "neutre"],
    "ecrivain": ["neutre", "impressionnee"],
    "creature": ["decue", "impatiente"],
    "machine-analytique": ["neutre", "impressionnee"],
    "robot-capek": ["impatiente", "decue"],
    "bombe": ["impatiente", "neutre"],
    "tubes": ["neutre", "moqueuse"],
    "perceptron": ["decue", "moqueuse"],
    "unimate": ["impatiente", "neutre"],
    "eliza": ["neutre", "decue"],
    "shakey": ["moqueuse", "decue"],
    "deep-blue": ["moqueuse", "impressionnee"],
    "kismet": ["impressionnee", "moqueuse"],
    "alphago": ["impressionnee", "moqueuse"],
    "finale": ["moqueuse", "impressionnee", "impatiente"],
}
assert set(TONS) == {m["id"] for m in MASQUES}
