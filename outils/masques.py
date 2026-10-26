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


MASQUES = [
    {"id": "theatre", "nom": "Masque de théâtre", "seuil": 0, "dessin": theatre,
     "notice": "Le masque des tragédies grecques. Le mot « personne » vient du latin persona, le masque de l'acteur."},
    {"id": "peste", "nom": "Médecin de peste", "seuil": 8, "dessin": peste,
     "notice": "Le bec rempli d'herbes devait filtrer les « miasmes ». Le costume est décrit à Rome en 1656 ; la théorie était fausse, le microbe n'était pas encore inventé."},
    {"id": "automate", "nom": "Automate de Vaucanson", "seuil": 20, "dessin": automate,
     "notice": "En 1739, Jacques de Vaucanson expose un joueur de flûte mécanique et un canard qui mange et digère. Le canard trichait : la fiente était préparée à l'avance."},
    {"id": "turc", "nom": "Turc mécanique", "seuil": 35, "dessin": turc,
     "notice": "Un automate joueur d'échecs présenté en 1770, qui battit Napoléon et Franklin. Un humain caché dans le meuble jouait à sa place. La première fausse IA de l'histoire."},
    {"id": "tubes", "nom": "Ordinateur à lampes", "seuil": 55, "dessin": tubes,
     "notice": "L'ENIAC (1945) comptait 17 468 tubes à vide. Selon la légende, une lampe grillait tous les deux jours ; en vrai, on en remplaçait plusieurs par semaine."},
    {"id": "finale", "nom": "Démon de Laplace", "seuil": 80, "dessin": finale, "tour": 1,
     "notice": "En 1814, Laplace imagine une intelligence qui connaîtrait la position de chaque particule et prédirait tout l'avenir. L'IA trouve l'idée flatteuse, et un peu présomptueuse."},
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
