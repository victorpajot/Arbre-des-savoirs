"""v4 : dix-huit nouveaux masques de l'IA (40 × 48), de Talos à AlphaGo.

Même principe que masques.py : une base, puis les expressions posées par-dessus.
"""
import math

from dessin import Toile, anneau, bande, courbe, disque, ellipse, miroir, poly, rect, trait

L, H = 40, 48


def toile():
    return Toile(L, H)


def sym(pixels):
    return pixels | miroir(pixels, L)


# --- Mythes et légendes ----------------------------------------------------------------

def promethee():
    t = toile()
    for i, (x, h) in enumerate([(9, 14), (14, 19), (20, 22), (26, 19), (31, 14)]):
        t.peindre(poly([(x - 5, 16), (x, 16 - h), (x + 5, 16)]), "rouge" if i % 2 else "orange", "plat", 1 if i % 2 else 1)
    t.peindre(sym(poly([(15, 6), (20, 2), (20, 14)])), "or", "plat", 2)
    t.peindre(ellipse(20, 28, 12, 15), "peau", "sphere", mini=1)
    t.peindre(poly([(9, 30), (31, 30), (28, 42), (20, 46), (12, 42)]), "cheveux", "biseau", 1)
    t.peindre(rect(15, 34, 25, 36), "peau", "plat", 1)
    t.contour()
    return t, {"yeux": [(14, 24), (25, 24)], "bouche": (20, 35), "encre": "n", "sourcil": "8", "eclat": "w", "genre": "trou", "bouche_encre": "1"}


def talos():
    t = toile()
    t.peindre(poly([(18, 0), (22, 0), (24, 12), (16, 12)]) | rect(17, 0, 23, 3), "rouge", "biseau", 2)
    t.peindre(ellipse(20, 26, 14, 18) | rect(6, 14, 34, 26), "cuivre", "sphere")
    t.peindre(rect(6, 12, 34, 16), "cuivre", "biseau", 1)
    t.peindre(sym(rect(6, 26, 10, 40)), "cuivre", "biseau", 0)
    t.poser(trait(20, 26, 20, 33), "D")
    # La veine unique de Talos, fermée par un clou à la cheville : ici, sur la tempe.
    t.poser(courbe([(30, 18), (32, 24), (31, 30)]), "D")
    t.poser({(31, 30), (31, 31)}, "y")
    t.contour()
    return t, {"yeux": [(14, 22), (26, 22)], "bouche": (20, 37), "encre": "n", "sourcil": "D", "eclat": "y", "genre": "trou"}


def golem():
    t = toile()
    tete = poly([(8, 8), (16, 4), (26, 4), (33, 9), (35, 26), (32, 40), (24, 46), (14, 45), (7, 38), (5, 22)])
    t.peindre(tete, "bois", "sphere", 2, mini=1)
    for p in [(12, 14), (29, 33), (10, 31), (27, 8)]:
        t.poser({p, (p[0] + 1, p[1])}, "B")
    # Les lettres sur le front, qui animent l'argile.
    t.peindre(rect(13, 9, 27, 13), "parchemin", "plat", 2)
    for x in (15, 19, 23):
        t.poser({(x, 10), (x + 1, 10), (x + 1, 11), (x + 1, 12), (x, 12)}, "n")
    t.contour()
    return t, {"yeux": [(14, 22), (26, 22)], "bouche": (20, 35), "encre": "n", "sourcil": "n", "eclat": "t", "genre": "trou", "grand": True}


def tete_airain():
    t = toile()
    t.peindre(rect(10, 42, 30, 47), "gris", "biseau", 2)
    t.peindre(ellipse(20, 20, 12, 15), "cuivre", "sphere", 1)
    barbe = poly([(8, 24), (32, 24), (30, 36), (24, 42), (16, 42), (10, 36)])
    t.peindre(barbe, "cuivre", "biseau", 0)
    for x in range(12, 30, 3):
        t.poser(trait(x, 30, x + 1, 39), "D")
    t.peindre(rect(13, 30, 27, 33), "cuivre", "plat", 1)
    t.poser({(9, 6), (31, 6), (20, 2)}, "j")
    t.contour()
    return t, {"yeux": [(15, 19), (25, 19)], "bouche": (20, 31), "encre": "n", "sourcil": "D", "eclat": "j", "genre": "trou"}


def homoncule():
    t = toile()
    t.peindre(rect(16, 0, 24, 9), "cyan", "cyl_v", 1)
    t.peindre(rect(14, 0, 26, 2), "bois", "plat", 1)
    t.peindre(ellipse(20, 30, 17, 17), "cyan", "plat", 2)
    t.peindre(ellipse(20, 30, 15, 15), "cyan", "sphere", 1)
    t.peindre(ellipse(20, 41, 14, 4) & ellipse(20, 30, 15, 15), "vert", "plat", 2)
    t.peindre(ellipse(20, 28, 7, 8), "peau", "sphere", 2)
    t.peindre(ellipse(20, 21.5, 6, 2.5), "cheveux", "plat", 1)
    t.poser({(9, 22), (10, 21), (11, 20)}, "w")
    t.contour()
    return t, {"yeux": [(17, 27), (23, 27)], "bouche": (20, 32), "encre": "n", "sourcil": "h", "eclat": "w", "genre": "trou"}


def heron():
    t = toile()
    for x in (6, 34):
        t.peindre(disque(x, 6, 3.5) | disque(x + (4 if x < 20 else -4), 3, 2.5), "gris", "sphere", 4)
    t.peindre(sym(bande((4, 12), (10, 22), 1.6)), "cuivre", "cyl_v", 1)
    t.peindre(disque(20, 24, 15), "cuivre", "sphere", 1)
    t.peindre(anneau(20, 24, 15, 1.4), "cuivre", "plat", 0)
    t.peindre(rect(16, 39, 24, 47), "cuivre", "biseau", 1)
    t.poser({(13, 33), (27, 33)}, "M")
    t.contour()
    return t, {"yeux": [(14, 21), (26, 21)], "bouche": (20, 31), "encre": "n", "sourcil": "D", "eclat": "M", "genre": "cadran"}


# --- Automates et machines ----------------------------------------------------------

def ecrivain():
    t = toile()
    t.peindre(ellipse(20, 16, 14, 13) | rect(6, 14, 34, 32), "cheveux", "sphere", 1)
    t.peindre(ellipse(20, 26, 11, 13), "peau", "sphere", 2)
    t.peindre(poly([(9, 13), (31, 13), (30, 20), (10, 20)]), "cheveux", "biseau", 1)
    t.peindre(poly([(8, 40), (32, 40), (36, 47), (4, 47)]), "bleu", "biseau", 1)
    t.peindre(sym(poly([(12, 38), (20, 42), (20, 47), (14, 44)])), "gris", "plat", 5)
    t.poser(disque(12, 31, 1.6) | disque(28, 31, 1.6), "I")
    t.contour()
    t.peindre(bande((33, 26), (39, 42), 0.7), "parchemin", "plat", 2)
    return t, {"yeux": [(15, 25), (25, 25)], "bouche": (20, 34), "encre": "n", "sourcil": "h", "eclat": "w", "genre": "trou"}


def machine_analytique():
    t = toile()
    t.peindre(rect(4, 2, 35, 45), "bois", "biseau", 1)
    t.peindre(rect(6, 4, 33, 43), "nuit", "plat", 1)
    for x in (9, 20, 31):
        for y in range(6, 42, 5):
            t.peindre(ellipse(x, y + 1.5, 3.2, 1.6), "or", "cyl_h", 2)
            t.poser({(x - 1, y + 1), (x + 1, y + 2)}, "4")
    t.peindre(rect(4, 0, 35, 2), "or", "plat", 1)
    # Une plaque de laiton au centre, où l'IA a gravé son visage.
    t.peindre(rect(9, 14, 30, 37), "or", "biseau", 3)
    t.contour()
    return t, {"yeux": [(14, 19), (26, 19)], "bouche": (20, 33), "encre": "n", "sourcil": "4", "eclat": "j", "genre": "cadran"}


def creature():
    t = toile()
    t.peindre(rect(7, 4, 33, 11), "cheveux", "plat", 0)
    t.peindre(rect(8, 9, 32, 42) | ellipse(20, 40, 12, 6), "vert", "biseau", 3, mini=2)
    t.peindre(rect(7, 4, 33, 9), "cheveux", "biseau", 0)
    for x in range(10, 31, 2):
        t.poser({(x, 10)}, "8")
    t.poser(trait(11, 15, 18, 13), "2")
    for x in (12, 14, 16):
        t.poser({(x, 13), (x, 15)}, "2")
    t.peindre(rect(3, 30, 7, 34) | rect(33, 30, 37, 34), "gris", "cyl_h", 3)
    t.contour()
    return t, {"yeux": [(14, 24), (26, 24)], "bouche": (20, 37), "encre": "n", "sourcil": "8", "eclat": "i", "genre": "trou"}


def robot_capek():
    t = toile()
    t.peindre(trait(20, 0, 20, 5), "gris", "plat", 1)
    t.peindre(disque(20, 1.5, 1.8), "rouge", "sphere")
    t.peindre(rect(6, 6, 33, 40), "gris", "biseau", 3)
    t.peindre(rect(1, 16, 5, 28) | rect(34, 16, 38, 28), "gris", "biseau", 2)
    for x, y in [(8, 8), (31, 8), (8, 38), (31, 38)]:
        t.poser({(x, y)}, "G")
    t.peindre(rect(12, 32, 27, 37), "nuit", "plat", 0)
    for x in range(13, 27, 2):
        t.poser(rect(x, 33, x, 36), "g")
    t.peindre(rect(13, 42, 26, 47), "gris", "biseau", 2)
    t.contour()
    return t, {"yeux": [(14, 20), (26, 20)], "bouche": None, "encre": "o", "sourcil": "G", "eclat": "a", "genre": "trou", "grand": True}


def bombe():
    t = toile()
    t.peindre(rect(2, 3, 37, 46), "gris", "biseau", 1)
    couleurs = ["rouge", "nuit", "or"]
    for j, y in enumerate((9, 31, 40)):
        for i, x in enumerate(range(7, 36, 7)):
            t.peindre(disque(x, y, 3), couleurs[(i + j) % 3], "sphere")
            t.poser({(x, y)}, "w")
    t.peindre(rect(5, 15, 34, 27), "parchemin", "plat", 1)
    t.contour()
    return t, {"yeux": [(14, 20), (26, 20)], "bouche": (20, 25), "encre": "n", "sourcil": "A", "eclat": "A", "genre": "trou"}


def unimate():
    t = toile()
    t.peindre(bande((20, 47), (20, 34), 4), "gris", "cyl_v", 3)
    t.peindre(rect(4, 10, 35, 34), "orange", "biseau", 1)
    t.peindre(rect(4, 6, 35, 10), "gris", "biseau", 2)
    t.peindre(rect(8, 14, 31, 27), "nuit", "plat", 1)
    t.poser(rect(4, 30, 35, 31), "n")
    t.peindre(rect(36, 18, 39, 24) | rect(0, 18, 3, 24), "gris", "biseau", 3)
    t.contour()
    return t, {"yeux": [(14, 20), (26, 20)], "bouche": None, "encre": "o", "sourcil": "O", "eclat": "a", "genre": "trou", "grand": True}


def perceptron():
    t = toile()
    t.peindre(rect(3, 5, 36, 44), "gris", "biseau", 1)
    t.peindre(rect(6, 8, 33, 41), "nuit", "plat", 0)
    for x in range(8, 33, 3):
        for y in range(10, 40, 3):
            t.poser({(x, y)}, "K")
    for chemin in ([(3, 12), (0, 16), (0, 30)], [(36, 12), (39, 16), (39, 30)]):
        t.poser(courbe(chemin), "r")
    t.contour()
    return t, {"yeux": [(14, 20), (26, 20)], "bouche": (20, 32), "encre": "c", "sourcil": "C", "eclat": "d", "genre": "ecran"}


def eliza():
    t = toile()
    t.peindre(rect(2, 4, 37, 38), "ivoire", "biseau", 0)
    t.peindre(rect(2, 4, 37, 38), "parchemin", "biseau", 2)
    t.peindre(rect(6, 8, 33, 33), "nuit", "plat", 0)
    for y in (10, 12):
        t.poser(rect(8, y, 8 + (y - 4) * 2, y), "2")
    t.peindre(rect(10, 40, 29, 46), "parchemin", "biseau", 1)
    for x in range(12, 28, 3):
        t.poser({(x, 42), (x, 44)}, "A")
    t.contour()
    return t, {"yeux": [(14, 19), (26, 19)], "bouche": (20, 27), "encre": "e", "sourcil": "E", "eclat": "i", "genre": "ecran"}


def shakey():
    t = toile()
    t.peindre(trait(26, 0, 26, 8), "gris", "plat", 1)
    t.peindre(rect(23, 0, 29, 2), "gris", "plat", 3)
    t.peindre(rect(6, 8, 33, 30), "gris", "biseau", 2)
    t.peindre(rect(9, 11, 30, 27), "gris", "plat", 4)
    t.peindre(bande((20, 30), (20, 47), 3), "gris", "cyl_v", 1)
    for y in (36, 41):
        t.peindre(rect(10, y, 29, y + 2), "nuit", "plat", 1)
    t.contour()
    return t, {"yeux": [(14, 19), (26, 19)], "bouche": None, "encre": "n", "sourcil": "G", "eclat": "c", "genre": "lentille"}


def deep_blue():
    t = toile()
    t.peindre(rect(4, 2, 35, 46), "bleu", "biseau", 0)
    for y in range(5, 44, 4):
        t.poser(rect(6, y, 33, y), "U")
    t.peindre(rect(8, 12, 31, 34), "nuit", "plat", 0)
    # Un pion d'échecs en guise de couronne.
    t.peindre(disque(20, 5, 2.4) | poly([(17, 9), (23, 9), (24, 11), (16, 11)]), "ivoire", "sphere", 0)
    t.contour()
    return t, {"yeux": [(14, 20), (26, 20)], "bouche": (20, 29), "encre": "x", "sourcil": "u", "eclat": "w", "genre": "ecran"}


def kismet():
    t = toile()
    t.peindre(sym(poly([(3, 10), (9, 6), (11, 20), (6, 22)])), "rose", "biseau", 1)
    t.peindre(ellipse(20, 26, 13, 16), "gris", "sphere", 3)
    for x in (14, 26):
        t.peindre(disque(x, 21, 5), "ivoire", "sphere", 0)
    t.peindre(rect(13, 33, 27, 36), "rouge", "biseau", 2)
    t.contour()
    return t, {"yeux": [(14, 20), (26, 20)], "bouche": None, "encre": "n", "sourcil": "p", "eclat": "w", "genre": "trou", "grand": True}


def alphago():
    t = toile()
    t.peindre(rect(3, 4, 36, 43), "bois", "biseau", 2)
    for i in range(5, 36, 5):
        t.poser(rect(i, 6, i, 41), "B")
        t.poser(rect(5, i + 2, 34, i + 2), "B")
    for (x, y), c in [((10, 12), "nuit"), ((30, 12), "ivoire"), ((10, 37), "ivoire"), ((25, 37), "nuit"), ((35, 22), "nuit")]:
        t.peindre(disque(x, y, 2.2), c, "sphere", 1)
    t.contour()
    return t, {"yeux": [(14, 21), (26, 21)], "bouche": (20, 30), "encre": "n", "sourcil": "H", "eclat": "w", "genre": "trou", "grand": True}
