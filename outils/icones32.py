"""Illustrations des cases du plateau et pictogrammes d'époque (32 × 32)."""
import math
import random

from dessin import (Toile, anneau, arc, bande, courbe, disque, ellipse, ellipse_tournee, peindre_tube,
                    poly, rect, texte, trait)

N = 32
DESSINS = {}


def dessin(fn):
    DESSINS[fn.__name__.replace("_", "-")] = fn
    return fn


def toile():
    return Toile(N, N)


def flammes(t, cx, base, haut, larg):
    t.peindre(poly([(cx - larg, base), (cx - larg * 0.6, base - haut * 0.55), (cx - larg * 0.2, base - haut * 0.4), (cx, base - haut),
                    (cx + larg * 0.3, base - haut * 0.5), (cx + larg * 0.7, base - haut * 0.7), (cx + larg, base)]), "rouge", "plat", 2)
    t.peindre(poly([(cx - larg * 0.7, base), (cx - larg * 0.3, base - haut * 0.45), (cx + larg * 0.1, base - haut * 0.75),
                    (cx + larg * 0.5, base - haut * 0.35), (cx + larg * 0.7, base)]), "orange", "plat", 1)
    t.peindre(poly([(cx - larg * 0.35, base), (cx, base - haut * 0.45), (cx + larg * 0.35, base)]), "or", "plat", 2)


@dessin
def feu():
    t = toile()
    flammes(t, 16, 25, 22, 9)
    t.peindre(bande((4, 28), (27, 23), 1.8), "bois", "cyl_h")
    t.peindre(bande((5, 23), (28, 28), 1.8), "bois", "cyl_h")
    return t.contour()


@dessin
def roue():
    t = toile()
    for a in range(0, 180, 30):
        r = math.radians(a)
        t.peindre(bande((16 - 11 * math.cos(r), 16 - 11 * math.sin(r)), (16 + 11 * math.cos(r), 16 + 11 * math.sin(r)), 1), "bois", "plat", 2)
    t.peindre(anneau(16, 16, 14, 3.2), "bois", "biseau", 2)
    t.peindre(disque(16, 16, 3.6), "bois", "sphere")
    t.poser(disque(16, 16, 1.2), "H")
    return t.contour()


@dessin
def tablette():
    t = toile()
    t.peindre(poly([(4, 4), (28, 3), (29, 28), (3, 29)]), "cuivre", "biseau", 2)
    r = random.Random(4)
    for y in range(7, 27, 4):
        x = 6
        while x < 25:
            t.poser({(x, y), (x + 1, y), (x, y + 1)}, "D")
            x += r.choice((3, 4, 5))
    return t.contour()


@dessin
def pyramide():
    t = toile()
    t.peindre(disque(25, 6, 3.6), "or", "sphere")
    t.peindre(poly([(15, 6), (29, 26), (1, 26)]), "parchemin", "plat", 2)
    t.peindre(poly([(15, 6), (29, 26), (18, 26)]), "parchemin", "plat", 0)
    for y in range(9, 26, 3):
        t.poser({(x, y) for x in range(0, 32) if (x, y) in t.px and t.px[(x, y)] in "VA"}, "A")
    t.contour()
    t.poser(rect(0, 27, 31, 28), "y")
    return t


@dessin
def eclipse():
    t = toile()
    for a in range(0, 360, 30):
        r = math.radians(a)
        t.poser(trait(16 + 11 * math.cos(r), 16 + 11 * math.sin(r), 16 + 14.5 * math.cos(r), 16 + 14.5 * math.sin(r)), "j")
    t.peindre(disque(16, 16, 10), "or", "sphere")
    t.peindre(disque(18.5, 15, 9.4), "nuit", "plat", 0)
    t.poser(arc(18.5, 15, 9, 200, 250), "K")
    return t.contour()


@dessin
def atome():
    t = toile()
    for a in (0, 60, 120):
        t.poser(ellipse_tournee(16, 16, 14, 5, a, 1.3), "u")
    t.peindre(disque(16, 16, 3.6), "rouge", "sphere")
    for a in (0, 120, 240):
        r = math.radians(a + 20)
        x, y = 16 + 14 * math.cos(math.radians(a)) * math.cos(r * 0), 16
    for (x, y) in [(29, 16), (9, 4), (9, 28)]:
        t.peindre(disque(x + 0.5, y + 0.5, 1.8), "cyan", "sphere")
    return t.contour()


def colonnes(t):
    t.peindre(poly([(2, 8), (16, 2), (30, 8)]), "ivoire", "plat", 0)
    t.peindre(rect(2, 8, 29, 10), "gris", "biseau", 4)
    for x in (4, 10, 17, 23):
        t.peindre(rect(x, 11, x + 4, 25), "gris", "cyl_v", mini=2)
        for xx in (x + 1, x + 3):
            t.poser(rect(xx, 12, xx, 24), "g")
    t.peindre(rect(1, 26, 30, 28), "gris", "biseau", 3)


@dessin
def alexandrie():
    t = toile()
    colonnes(t)
    return t.contour()


@dessin
def incendie():
    t = toile()
    colonnes(t)
    flammes(t, 9, 14, 13, 6)
    flammes(t, 22, 16, 15, 7)
    t.contour()
    t.poser({(5, 2), (27, 1), (14, 0)}, "g")
    return t


@dessin
def couronne():
    t = toile()
    t.peindre(ellipse(16, 25, 14, 4.5), "cyan", "plat", 1)
    t.poser(courbe([(3, 24), (8, 23), (12, 25), (17, 23), (22, 25), (28, 24)]), "d")
    t.peindre(poly([(6, 22), (6, 10), (10, 15), (13, 7), (16, 14), (19, 7), (22, 15), (26, 10), (26, 22)]), "or", "biseau", 2)
    for x in (10, 16, 22):
        t.peindre(disque(x, 18.5, 1.5), "rouge", "sphere")
    t.poser(rect(6, 21, 26, 21), "Y")
    return t.contour()


@dessin
def engrenage():
    t = toile()
    def roue_dentee(cx, cy, r, dents, fam):
        forme = disque(cx, cy, r)
        for i in range(dents):
            a = 2 * math.pi * i / dents
            forme |= disque(cx + (r + 1.2) * math.cos(a), cy + (r + 1.2) * math.sin(a), 1.7)
        t.peindre(forme, fam, "biseau", 2)
        t.peindre(disque(cx, cy, r * 0.4), fam, "plat", 1)
        t.poser(disque(cx, cy, 1.2), "n")
    roue_dentee(11, 12, 7.5, 10, "or")
    roue_dentee(23, 22, 5.5, 8, "cuivre")
    return t.contour()


@dessin
def zero():
    t = toile()
    t.peindre(rect(3, 4, 28, 27), "parchemin", "biseau", 2)
    t.peindre(anneau(16, 15.5, 7.5, 2.6, ry=9), "rouge", "plat", 1)
    t.poser(trait(6, 24, 26, 24), "A")
    return t.contour()


@dessin
def astrolabe():
    t = toile()
    t.peindre(anneau(16, 4, 2.6, 1.2), "or", "plat", 2)
    t.peindre(disque(16, 18, 13), "or", "biseau", 2)
    t.peindre(disque(16, 18, 10.5), "or", "plat", 1)
    t.poser(anneau(16, 18, 7, 1) | anneau(18, 16, 4.5, 1) | trait(6, 18, 26, 18) | trait(16, 8, 16, 28), "y")
    t.poser(bande((8, 26), (24, 10), 0.8), "4")
    for a in range(0, 360, 30):
        r = math.radians(a)
        t.poser({(int(16 + 12 * math.cos(r)), int(18 + 12 * math.sin(r)))}, "4")
    return t.contour()


@dessin
def lunettes():
    t = toile()
    t.poser(courbe([(1, 12), (4, 14), (5, 16)]) | courbe([(30, 12), (27, 14), (26, 16)]), "b")
    for cx in (9, 23):
        t.peindre(disque(cx, 17, 6), "cyan", "plat", 2)
        t.peindre(anneau(cx, 17, 6.6, 1.5), "bois", "plat", 2)
        t.poser({(cx - 2, 14), (cx - 3, 15)}, "w")
    t.peindre(arc(16, 17, 3, 200, 340, 1.5), "bois", "plat", 2)
    return t.contour()


@dessin
def presse():
    t = toile()
    t.peindre(rect(3, 2, 6, 29) | rect(25, 2, 28, 29), "bois", "cyl_v")
    t.peindre(rect(3, 2, 28, 5), "bois", "biseau", 2)
    t.peindre(rect(15, 6, 16, 13), "gris", "cyl_v")
    t.poser({(15, y) for y in range(6, 14, 2)}, "G")
    t.peindre(rect(10, 9, 21, 10), "bois", "biseau", 1)
    t.peindre(rect(8, 14, 23, 17), "bois", "biseau", 2)
    t.peindre(rect(8, 21, 23, 23), "parchemin", "biseau", 2)
    t.poser({(x, 22) for x in range(9, 23, 2)}, "n")
    t.peindre(rect(6, 24, 25, 26), "bois", "biseau", 1)
    return t.contour()


@dessin
def heliocentre():
    t = toile()
    for r, ry in ((7, 5), (11, 8), (15, 11)):
        t.poser(ellipse_tournee(16, 16, r, ry, 0, 1), "g")
    t.peindre(disque(16, 16, 4), "or", "sphere")
    t.peindre(disque(23.5, 13, 1.6), "rouge", "sphere")
    t.peindre(disque(6, 21, 2.2), "bleu", "sphere")
    t.peindre(disque(28, 22, 2), "orange", "sphere")
    t.peindre(disque(4, 10, 1.4), "gris", "sphere")
    return t.contour()


@dessin
def prison():
    t = toile()
    t.peindre(rect(2, 2, 29, 29), "rouge", "plat", 1)
    for y in range(2, 30, 3):
        dec = 0 if (y // 3) % 2 else 3
        t.poser({(x, y) for x in range(2, 30) if (x + dec) % 6 == 0} | rect(2, y, 29, y), "1")
    t.peindre(rect(8, 7, 23, 24), "nuit", "plat", 0)
    t.peindre(disque(19, 11, 2.5), "gris", "plat", 4)
    for x in (10, 14, 18, 22):
        t.peindre(rect(x, 6, x, 25), "gris", "cyl_v", 2)
    t.peindre(rect(7, 6, 24, 6) | rect(7, 25, 24, 25), "gris", "biseau", 2)
    return t.contour()


@dessin
def guillotine():
    t = toile()
    t.peindre(rect(6, 3, 8, 28) | rect(23, 3, 25, 28), "bois", "cyl_v")
    t.peindre(rect(5, 2, 26, 4), "bois", "biseau", 2)
    t.peindre(poly([(9, 7), (22, 7), (22, 12), (9, 15)]), "gris", "cyl_h", 4)
    t.peindre(rect(9, 5, 22, 7), "bois", "plat", 1)
    t.peindre(rect(9, 21, 22, 24), "bois", "biseau", 2)
    t.poser(disque(15.5, 21, 2), "n")
    t.peindre(rect(3, 27, 28, 29), "bois", "biseau", 1)
    return t.contour()


@dessin
def puits():
    t = toile()
    t.peindre(rect(7, 5, 8, 18) | rect(23, 5, 24, 18), "bois", "cyl_v")
    t.peindre(poly([(3, 7), (16, 1), (28, 7)]), "rouge", "biseau", 1)
    t.peindre(rect(9, 8, 22, 8), "bois", "plat", 1)
    t.poser(trait(15, 9, 15, 13), "g")
    t.peindre(rect(13, 13, 17, 16), "bois", "biseau", 2)
    t.peindre(ellipse(16, 19, 11, 3), "nuit", "plat", 0)
    murs = rect(5, 19, 26, 29)
    t.peindre(murs, "gris", "cyl_v", mini=1)
    for y in range(19, 30, 3):
        dec = 0 if (y // 3) % 2 else 3
        t.poser({(x, y) for x in range(5, 27) if (x + dec) % 6 == 0} | rect(5, y, 26, y), "G")
    return t.contour()


@dessin
def flacon():
    t = toile()
    t.peindre(courbe([(16, 14), (17, 8), (21, 4), (26, 5), (28, 9), (29, 14)], 2.4), "cyan", "plat", 1)
    t.peindre(disque(14, 21, 9), "cyan", "sphere", mini=1)
    t.peindre({(x, y) for (x, y) in disque(14, 21, 8) if y >= 21}, "parchemin", "plat", 2)
    t.poser({(10, 17), (11, 16)}, "d")
    return t.contour()


@dessin
def fiole():
    t = toile()
    for a in range(0, 360, 45):
        r = math.radians(a)
        t.poser(trait(16 + 12 * math.cos(r), 18 + 12 * math.sin(r), 16 + 15 * math.cos(r), 18 + 15 * math.sin(r)), "i")
    t.peindre(rect(13, 2, 18, 5), "bois", "biseau", 2)
    t.peindre(rect(13, 6, 18, 12) | poly([(13, 12), (18, 12), (25, 27), (6, 27)]), "cyan", "plat", 1)
    t.peindre(poly([(10.2, 19), (21.8, 19), (25, 27), (6, 27)]), "vert", "plat", 3)
    t.poser({(13, 23), (16, 21), (19, 24)}, "w")
    return t.contour()


@dessin
def relativite():
    t = toile()
    t.peindre(rect(1, 6, 30, 26), "bois", "biseau", 2)
    t.peindre(rect(3, 8, 28, 24), "vert", "plat", 0)
    t.poser(texte("E=MC", 4, 12), "l")
    t.poser(texte("2", 21, 9), "l")
    t.poser(trait(4, 20, 26, 20), "z")
    return t.contour()


@dessin
def labyrinthe():
    t = toile()
    t.peindre(rect(2, 2, 29, 29), "vert", "plat", 2)
    murs = set()
    for r in range(1, 6):
        x0, y0, x1, y1 = 2 + r * 2, 2 + r * 2, 29 - r * 2, 29 - r * 2
        cadre = rect(x0, y0, x1, y1) - rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1)
        ouverture = {(x0 + (r * 5) % (x1 - x0 - 2) + 1, y0)} if r % 2 else {(x1, y0 + (r * 3) % (y1 - y0 - 2) + 1)}
        murs |= cadre - ouverture - {(p[0], p[1] + 1) for p in ouverture if r % 2 == 0} - {(p[0] + 1, p[1]) for p in ouverture if r % 2}
    t.poser(murs, "E")
    t.peindre(disque(16, 16, 1.6), "rouge", "sphere")
    return t.contour()


@dessin
def adn():
    t = toile()
    for y in range(1, 31):
        a = y / 30 * 2 * math.pi * 1.5
        x1, x2 = 16 + 9 * math.sin(a), 16 - 9 * math.sin(a)
        if y % 3 == 0:
            t.poser(trait(x1, y, x2, y), "g")
        devant = math.cos(a) > 0
        t.peindre(disque(x1, y + 0.5, 1.6), "bleu" if devant else "violet", "plat", 2 if devant else 1)
        t.peindre(disque(x2, y + 0.5, 1.6), "rouge" if not devant else "orange", "plat", 2 if not devant else 1)
    return t.contour()


@dessin
def ordinateur():
    t = toile()
    t.peindre(rect(2, 3, 29, 24), "gris", "biseau", 3)
    for y in (6, 10, 14):
        for x in range(5, 27, 3):
            t.poser({(x, y)}, random.Random(x * y).choice("reyw"))
    t.peindre(disque(9, 19.5, 2.5) | disque(22, 19.5, 2.5), "gris", "sphere", maxi=2)
    t.poser({(9, 19), (22, 19)}, "w")
    t.peindre(rect(0, 26, 31, 29), "parchemin", "plat", 2)
    t.poser({(x, y) for x in range(1, 31, 2) for y in (27, 28) if (x * 7 + y) % 3 == 0}, "n")
    return t.contour()


@dessin
def fusee():
    t = toile()
    flammes(t, 16, 31, 8, 4)
    t.peindre(poly([(16, 0), (19.5, 6), (19.5, 23), (12.5, 23), (12.5, 6)]), "gris", "cyl_v", mini=3)
    t.poser(rect(13, 9, 19, 9) | rect(13, 16, 19, 16), "n")
    t.peindre(poly([(12.5, 17), (8, 24), (12.5, 22)]) | poly([(19.5, 17), (24, 24), (19.5, 22)]), "rouge", "plat", 2)
    t.peindre(disque(16, 12.5, 1.8), "bleu", "sphere")
    return t.contour()


@dessin
def internet():
    t = toile()
    t.peindre(rect(3, 2, 28, 22), "ivoire", "biseau", 0)
    t.peindre(rect(6, 5, 25, 18), "bleu", "plat", 0)
    t.poser(anneau(15.5, 11.5, 5.5, 1) | ellipse_tournee(15.5, 11.5, 2.4, 5.5, 0, 1) | trait(10, 11.5, 21, 11.5), "c")
    t.peindre(rect(11, 23, 20, 25), "ivoire", "biseau", 0)
    t.peindre(rect(5, 26, 26, 29), "ivoire", "biseau", 0)
    t.poser({(x, 27) for x in range(7, 25, 2)}, "g")
    return t.contour()


@dessin
def puce():
    t = toile()
    for i in range(6, 27, 4):
        t.peindre(rect(i, 1, i + 1, 4) | rect(i, 27, i + 1, 30) | rect(1, i, 4, i + 1) | rect(27, i, 30, i + 1), "or", "plat", 2)
    t.peindre(rect(5, 5, 26, 26), "gris", "biseau", 1)
    t.peindre(rect(9, 9, 22, 22), "nuit", "plat", 0)
    for chemin in ([(11, 20), (14, 16), (17, 18), (20, 12)], [(11, 12), (14, 16)], [(17, 18), (20, 20)], [(14, 16), (17, 11)]):
        t.poser(courbe(chemin), "C")
    for p in [(11, 20), (14, 16), (17, 18), (20, 12), (11, 12), (20, 20), (17, 11)]:
        t.poser({p}, "d")
    return t.contour()


@dessin
def oie():
    t = toile()
    t.peindre(rect(12, 26, 13, 29) | rect(17, 26, 18, 29), "orange", "plat", 1)
    t.peindre(ellipse(15, 21, 11, 6.5), "gris", "sphere", mini=3)
    t.peindre(bande((21, 18), (23, 7), 2.2, 1.8), "gris", "plat", 4)
    t.peindre(disque(23.5, 6, 3.6), "gris", "sphere", mini=3)
    t.peindre(poly([(26, 5), (31, 7), (26, 8)]), "orange", "plat", 1)
    t.poser(courbe([(8, 20), (13, 18), (19, 21)]), "z")
    t.contour()
    t.poser({(24, 5)}, "n")
    t.poser(anneau(23.5, 5.5, 2, 0.8) - rect(0, 7, 31, 31), "y")
    return t


@dessin
def pont():
    t = toile()
    t.peindre(ellipse(16, 30, 15, 3), "bleu", "plat", 2)
    pierre = rect(1, 12, 30, 16) | (rect(1, 16, 30, 27) - ellipse(16, 27, 10, 9))
    t.peindre(pierre, "gris", "biseau", 3)
    for y in (14, 18, 22):
        t.poser({(x, y) for x in range(1, 31) if (x, y) in pierre and (x + y) % 5 == 0}, "G")
    t.peindre(rect(1, 10, 30, 11), "gris", "biseau", 2)
    return t.contour()


# --- Pictogrammes d'époque ---------------------------------------------------------

@dessin
def amphore():
    t = toile()
    t.peindre(anneau(8, 10, 3.5, 1.4) | anneau(24, 10, 3.5, 1.4), "orange", "plat", 1)
    corps = poly([(12, 4), (20, 4), (20, 8), (26, 15), (20, 27), (16, 30), (12, 27), (6, 15), (12, 8)])
    t.peindre(corps, "orange", "cyl_v")
    t.poser({(x, y) for (x, y) in corps if 14 <= y <= 17}, "n")
    t.poser({(x, 15) for x in range(8, 25, 3)}, "O")
    return t.contour()


@dessin
def enluminure():
    t = toile()
    t.peindre(rect(4, 3, 27, 28), "parchemin", "biseau", 2)
    t.peindre(rect(7, 6, 16, 15), "bleu", "plat", 2)
    t.poser(texte("A", 10, 8), "y")
    t.poser(courbe([(7, 15), (5, 19), (8, 23)]), "e")
    for y in range(8, 26, 3):
        t.poser(trait(18 if y < 16 else 8, y, 25, y), "A")
    return t.contour()


@dessin
def plume():
    t = toile()
    t.peindre(rect(4, 22, 15, 29), "nuit", "cyl_v")
    t.peindre(ellipse(9.5, 22, 5.5, 1.5), "nuit", "plat", 0)
    t.peindre(poly([(11, 21), (28, 2), (30, 4), (24, 13), (15, 20)]), "gris", "biseau", 4)
    t.poser(trait(11, 21, 28, 3), "g")
    return t.contour()


@dessin
def bougie():
    t = toile()
    t.peindre(ellipse(16, 27, 11, 3), "or", "sphere")
    t.peindre(rect(12, 11, 19, 26), "ivoire", "cyl_v")
    t.poser({(12, 13), (12, 14), (12, 15)}, "T")
    t.peindre(poly([(16, 2), (18.5, 7), (16, 10), (13.5, 7)]), "orange", "sphere")
    t.poser({(16, 6), (16, 7)}, "j")
    return t.contour()


def icones():
    return {nom: fn().lignes() for nom, fn in DESSINS.items()}


if __name__ == "__main__":
    import sys
    from dessin import apercu
    apercu(icones(), sys.argv[1])
