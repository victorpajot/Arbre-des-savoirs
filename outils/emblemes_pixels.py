"""v29 : emblèmes dessinés pour les badges de compétence qui n'avaient pas d'objet parlant (demande de Victor).

Même atelier que les succès (dessin.py) ; ils rejoignent les dessins de data/succes.json, où le badge va les chercher.
"""
import math

from dessin import anneau, arc, bande, courbe, disque, ellipse, poly, rect, texte, trait
from succes_pixels import dessin, toile


@dessin
def camembert():
    t = toile()
    t.peindre(disque(15, 17, 12), "bleu", "sphere")
    part = {p for p in disque(17.5, 14.5, 12) if p[0] >= 18 and p[1] <= 13 and (p[0] - 17.5) ** 2 + (p[1] - 14.5) ** 2 <= 144}
    t.peindre(part, "or", "biseau", 2)
    t.poser(trait(15, 17, 15, 5) | trait(15, 17, 27, 17), "3")
    return t.contour()


@dessin
def courbe_cloche():
    t = toile()
    t.peindre(rect(2, 27, 29, 28), "gris", "plat", 2)
    pts = [(x, 26 - 19 * math.exp(-((x - 15.5) / 6.5) ** 2)) for x in range(2, 30)]
    aire = set()
    for x, y in pts:
        aire |= rect(x, int(y) + 1, x, 26)
    t.peindre(aire, "violet", "biseau", 2)
    t.poser(courbe(pts), "5")
    t.poser(trait(15, 6, 15, 26), "q")
    return t.contour()


@dessin
def bulles():
    t = toile()
    t.peindre(ellipse(11, 10, 9.5, 7) | poly([(6, 14), (4, 21), (12, 16)]), "bleu", "biseau", 2)
    t.peindre(ellipse(21, 20, 9.5, 7) | poly([(26, 24), (28, 30), (20, 26)]), "orange", "biseau", 1)
    t.poser(trait(6, 9, 16, 9) | trait(6, 12, 13, 12), "w")
    t.poser(trait(16, 19, 26, 19) | trait(16, 22, 23, 22), "w")
    return t.contour()


@dessin
def loupe():
    t = toile()
    t.peindre(bande((19, 19), (28, 28), 2.4), "bois", "cyl_v")
    t.peindre(anneau(13, 13, 10, 2.5), "or", "biseau", 2)
    t.peindre(disque(13, 13, 7.6), "cyan", "sphere")
    t.poser({(9, 9), (10, 8), (9, 10), (8, 11)}, "d")
    return t.contour()


@dessin
def pieces():
    t = toile()
    for i in range(4):
        t.peindre(ellipse(10, 25 - i * 3, 7.5, 2.8), "or", "cyl_h")
    for i in range(6):
        t.peindre(ellipse(21, 26 - i * 3, 7.5, 2.8), "or", "cyl_h")
    t.peindre(ellipse(21, 11, 7.5, 2.8), "or", "plat", 3)
    t.poser(texte("E", 20, 9), "Y")
    return t.contour()


@dessin
def barres():
    t = toile()
    t.peindre(rect(3, 27, 29, 28), "gris", "plat", 1)
    t.peindre(rect(3, 4, 4, 28), "gris", "plat", 1)
    for x, h, fam in [(7, 6, "vert"), (13, 9, "vert"), (19, 12, "vert"), (25, 21, "rouge")]:
        t.peindre(rect(x, 26 - h, x + 3, 26), fam, "biseau", 2)
    t.poser(courbe([(5, 23), (9, 20), (12, 19), (15, 16), (20, 12), (24, 4)], 2), "o")
    return t.contour()


@dessin
def visage():
    t = toile()
    t.peindre(disque(16, 16, 13), "or", "sphere")
    t.peindre(ellipse(11, 12, 1.8, 2.6) | ellipse(21, 12, 1.8, 2.6), "nuit", "plat", 0)
    t.poser(arc(16, 15, 8, 25, 155, 2), "D")
    t.peindre(ellipse(8, 19, 2.5, 1.5) | ellipse(24, 19, 2.5, 1.5), "rose", "plat", 1)
    return t.contour()


@dessin
def cubes():
    t = toile()
    for x0, y0, fam, l in [(3, 16, "rouge", "A"), (17, 16, "bleu", "B"), (10, 3, "vert", "C")]:
        t.peindre(rect(x0, y0, x0 + 11, y0 + 11), fam, "biseau", 2)
        t.peindre(rect(x0 + 2, y0 + 2, x0 + 9, y0 + 9), "ivoire", "plat", 0)
        lettre = texte(l, x0 + 4, y0 + 3)
        t.poser({(x0 + 4 + (x - x0 - 4) * 1, y) for x, y in lettre} | {(x, y + 1) for x, y in lettre if y == y0 + 7}, "k")
    return t.contour()


@dessin
def masque():
    t = toile()
    forme = ellipse(16, 14, 11, 12) | poly([(7, 18), (25, 18), (16, 29)])
    t.peindre(forme, "ivoire", "plat", 0)
    gauche = {p for p in forme if p[0] < 16}
    t.peindre(gauche, "violet", "biseau", 2)
    t.peindre(ellipse(11, 12, 2.5, 1.8) | ellipse(21, 12, 2.5, 1.8), "nuit", "plat", 0)
    t.poser(arc(11, 22, 4, 200, 340, 1), "q")
    t.poser(arc(21, 18, 4, 20, 160, 1), "5")
    return t.contour()


@dessin
def benzene():
    t = toile()
    pts = [(16 + 12 * math.cos(math.radians(a)), 16 + 12 * math.sin(math.radians(a))) for a in range(-90, 271, 60)]
    t.poser(courbe(pts, 2.2), "k")
    t.peindre(anneau(16, 16, 6.5, 1.6), "rouge", "plat", 2)
    for x, y in pts[:-1]:
        t.peindre(disque(x + 0.5, y + 0.5, 2.8), "gris", "sphere")
    return t.contour()


@dessin
def halo():
    t = toile()
    t.peindre(disque(16, 16, 14), "nuit", "plat", 1)
    t.peindre(anneau(16, 16, 14, 1.2), "violet", "plat", 1)
    t.peindre(anneau(16, 16, 10, 1), "nuit", "plat", 0)
    pts = [(16 + (1 + a * 1.1) * math.cos(a), 16 + (1 + a * 0.7) * math.sin(a)) for a in [i * 0.25 for i in range(30)]]
    t.poser(courbe(pts), "x")
    t.peindre(disque(16, 16, 2.2), "or", "sphere")
    for x, y in [(6, 9), (25, 8), (24, 24), (9, 23)]:
        t.poser({(x, y)}, "q")
    return t


@dessin
def antenne():
    t = toile()
    t.peindre(poly([(16, 10), (24, 30), (8, 30)]) - poly([(16, 15), (20, 28), (12, 28)]), "gris", "biseau", 3)
    t.poser(trait(12, 22, 20, 22) | trait(14, 17, 18, 17), "G")
    t.peindre(disque(16, 9, 2.5), "rouge", "sphere")
    for r in (6, 10):
        t.poser(arc(16, 9, r, 200, 250, 1) | arc(16, 9, r, 290, 340, 1), "u")
    return t.contour()


@dessin
def balance():
    t = toile()
    t.peindre(rect(15, 6, 16, 27), "or", "cyl_v")
    t.peindre(rect(9, 27, 22, 29), "or", "biseau", 2)
    t.peindre(rect(4, 7, 27, 8), "or", "biseau", 2)
    t.peindre(disque(16, 5, 2.2), "or", "sphere")
    for cx in (6, 25):
        t.poser(trait(cx, 9, cx - 4, 17) | trait(cx, 9, cx + 4, 17), "Y")
        t.peindre(poly([(cx - 6, 17), (cx + 6, 17), (cx + 3, 21), (cx - 3, 21)]), "or", "biseau", 2)
    return t.contour()
