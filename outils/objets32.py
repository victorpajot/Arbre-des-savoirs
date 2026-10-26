"""Objets du cabinet de curiosités en 32 × 32, dessinés par formes (voir dessin.py)."""
from dessin import (Toile, anneau, arc, bande, courbe, decaler, disque, ellipse, ellipse_tournee,
                    peindre_tube, poly, rect, texte, trait)

N = 32
DESSINS = {}


def dessin(fn):
    DESSINS[fn.__name__.replace("_", "-")] = fn
    return fn


def toile():
    return Toile(N, N)


def cube(t, x, y, s, d, fam="gris", base=4):
    """Dé vu de trois quarts : face avant, dessus et côté droit."""
    face = rect(x, y + d, x + s - 1, y + d + s - 1)
    dessus = poly([(x, y + d), (x + d, y), (x + d + s, y), (x + s, y + d)])
    cote = poly([(x + s, y + d), (x + s + d, y), (x + s + d, y + s), (x + s, y + d + s)])
    t.peindre(dessus, fam, "plat", base + 1)
    t.peindre(cote, fam, "plat", base - 2)
    t.peindre(face, fam, "plat", base)
    return face


@dessin
def boulier():
    t = toile()
    cadre = rect(2, 5, 29, 26) - rect(4, 7, 27, 24)
    for y in (9, 13, 17, 21):
        t.peindre(rect(4, y, 27, y), "gris", "plat", 2)
    t.peindre(rect(4, 11, 27, 11), "bois", "plat", 1)
    t.peindre(cadre, "bois", "biseau", 2)
    rangs = [("rouge", [6, 9, 18, 21, 24]), ("bleu", [6, 15, 18, 21, 24]), ("or", [6, 9, 12, 21, 24]), ("vert", [6, 9, 12, 15, 24])]
    for (fam, xs), y in zip(rangs, (9, 13, 17, 21)):
        for x in xs:
            t.peindre(ellipse(x + 0.5, y + 0.5, 1.6, 1.7), fam, "sphere")
    return t.contour()


@dessin
def compas_euclide():
    t = toile()
    t.poser(arc(16, 27, 10, 195, 345), "u")
    peindre_tube(t, bande((15, 6), (7, 27), 1.3, 1.0), "gris", (15, 6), (7, 27), 1.3)
    peindre_tube(t, bande((17, 6), (25, 27), 1.3, 1.0), "gris", (17, 6), (25, 27), 1.3)
    t.peindre(rect(24, 26, 26, 28), "orange", "biseau", 1)
    t.peindre(rect(15, 1, 16, 3), "or", "biseau")
    t.peindre(disque(16, 6, 3), "or", "sphere")
    return t.contour()


@dessin
def des_pascal():
    t = toile()
    f1 = cube(t, 2, 6, 12, 4)
    f2 = cube(t, 15, 13, 11, 4)
    t.contour()
    for x, y in [(4, 12), (11, 19), (7, 15)]:
        t.poser(rect(x, y, x + 1, y + 1), "n")
    for x, y in [(17, 19), (23, 19), (17, 25), (23, 25), (20, 22)]:
        t.poser(rect(x, y, x + 1, y + 1), "n")
    return t


@dessin
def ardoise_boole():
    t = toile()
    t.peindre(rect(3, 5, 28, 26), "bois", "biseau", 2)
    t.peindre(rect(5, 7, 26, 24), "gris", "plat", 1)
    t.poser({(x, y) for x in range(5, 27) for y in range(7, 25) if (x * 7 + y * 3) % 11 == 0}, "G")
    t.poser(texte("1+1=1", 6, 9), "l")
    t.poser(texte("1x0=0", 6, 17), "z")
    return t.contour()


@dessin
def metre_etalon():
    t = toile()
    t.peindre(rect(2, 15, 29, 24), "bois", "biseau", 2)
    t.peindre(rect(4, 17, 27, 22), "rouge", "plat", 1)
    t.peindre(rect(1, 11, 30, 16), "gris", "cyl_h", 4)
    for x in range(3, 30, 3):
        t.poser({(x, 11), (x, 12)}, "G")
    t.poser({(1, 12), (1, 13), (1, 14), (30, 12), (30, 13), (30, 14)}, "G")
    return t.contour()


@dessin
def pomme_newton():
    t = toile()
    pomme = disque(11.5, 18, 8.5) | disque(20.5, 18, 8.5) | ellipse(16, 21, 11, 7.5)
    pomme -= {(15, 9), (16, 9), (15, 10), (16, 10), (14, 9), (17, 9)}
    t.peindre(pomme, "rouge", "sphere")
    t.poser(rect(9, 13, 10, 14), "f")
    t.peindre(bande((16, 11), (17, 4), 0.9), "bois", "plat", 1)
    t.peindre(poly([(18, 7), (22, 3.5), (28, 4.5), (23, 8.5)]), "vert", "biseau", 2)
    t.poser(trait(19, 7, 26, 4.8), "E")
    return t.contour()


@dessin
def machine_joule():
    t = toile()
    t.poser(trait(7, 5, 21, 8), "n")
    t.poser(trait(4, 9, 4, 20), "n")
    t.peindre(disque(6, 8, 3.2), "gris", "sphere")
    t.peindre(rect(1, 20, 7, 27), "gris", "biseau", 2)
    t.peindre(rect(12, 15, 29, 29), "cuivre", "cyl_v")
    t.peindre(ellipse(20.5, 15, 8.5, 2), "cuivre", "plat", 2)
    t.peindre(rect(20, 4, 21, 14), "gris", "cyl_v")
    t.peindre(rect(16, 3, 25, 4), "bois", "biseau", 2)
    t.peindre(rect(26, 8, 27, 14), "gris", "plat", 5)
    t.peindre(disque(26.5, 15, 1.6), "rouge", "sphere")
    t.poser({(13, 21), (13, 22), (28, 21), (28, 22)}, "D")
    return t.contour()


@dessin
def diapason():
    t = toile()
    fourche = rect(10, 3, 12, 18) | rect(19, 3, 21, 18) | (ellipse(16, 18, 6, 4) - ellipse(16, 17, 3.2, 2.6) - rect(13, 10, 18, 17))
    fourche |= rect(15, 21, 16, 28)
    t.peindre(fourche, "gris", "biseau", 4)
    t.peindre(ellipse(16, 29, 3, 1.8), "gris", "sphere")
    t.contour()
    for r in (4, 6):
        t.poser(arc(11, 9, r, 150, 210), "c")
        t.poser(arc(20, 9, r, -30, 30), "c")
    return t


@dessin
def carnet_darwin():
    t = toile()
    t.peindre(rect(2, 24, 29, 27), "bois", "biseau", 2)
    t.peindre(poly([(3, 7), (15.5, 9), (15.5, 26), (3, 25)]), "parchemin", "plat", 2)
    t.peindre(poly([(16.5, 9), (29, 7), (29, 25), (16.5, 26)]), "parchemin", "plat", 2)
    t.poser(rect(14, 9, 15, 25), "V")
    t.poser(rect(16, 9, 17, 25), "V")
    for y in (11, 14, 17, 20, 23):
        t.poser(trait(5, y - 1, 13, y - 0.5), "A")
    t.contour()
    tronc = [(21, 23), (21, 18)]
    t.poser(courbe(tronc), "n")
    t.poser(courbe([(21, 18), (19, 15), (19, 12)]), "n")
    t.poser(courbe([(21, 18), (24, 15), (26, 13)]), "n")
    t.poser(courbe([(24, 15), (24, 11)]), "n")
    t.poser(courbe([(19, 15), (18, 13)]), "n")
    for p in [(19, 11), (26, 12), (24, 10), (18, 12)]:
        t.poser({p}, "r")
    return t


@dessin
def microscope_hooke():
    t = toile()
    t.peindre(ellipse(16, 28.5, 11, 2.6), "bois", "sphere")
    t.peindre(rect(23, 11, 25, 27), "or", "cyl_v")
    t.peindre(rect(19, 12, 23, 13), "or", "biseau", 2)
    t.peindre(rect(9, 23, 22, 24), "gris", "biseau", 3)
    t.peindre(rect(11, 6, 19, 20), "cuivre", "cyl_v")
    for y in (8, 13, 18):
        t.peindre(rect(11, y, 19, y), "or", "cyl_v")
    t.peindre(rect(13, 1, 17, 5), "gris", "cyl_v", 1)
    t.peindre(poly([(12, 20.5), (18.5, 20.5), (16.5, 23), (14, 23)]), "gris", "plat", 1)
    return t.contour()


@dessin
def pois_mendel():
    t = toile()
    t.poser(courbe([(28, 14), (30, 11), (29, 8), (27, 7)], 1), "E")
    t.peindre(ellipse(16, 17, 14, 6), "vert", "biseau", 2)
    t.peindre(ellipse(16, 15.5, 12, 3.4), "vert", "plat", 0)
    for i, x in enumerate((7, 11.5, 16, 20.5)):
        t.peindre(disque(x, 15.5, 2.4), "vert", "sphere")
    t.peindre(disque(25, 15.5, 2.4), "or", "sphere")
    t.poser({(24, 15), (25, 16)}, "Y")
    return t.contour()


@dessin
def boite_petri():
    t = toile()
    t.peindre(ellipse(16, 17, 14.5, 10), "cyan", "plat", 2)
    t.peindre(ellipse(16, 17.5, 12.8, 8.6), "parchemin", "plat", 2)
    t.poser({(x, y) for (x, y) in ellipse(16, 17.5, 12.8, 8.6) if (x + y * 2) % 7 == 0}, "V")
    t.peindre(ellipse(13, 15, 4.5, 3.2), "parchemin", "plat", 2)
    t.peindre(ellipse(13, 15, 3, 2), "vert", "sphere")
    t.poser({(12, 14)}, "i")
    for (x, y, fam) in [(22, 12, "or"), (25, 17, "or"), (21, 22, "or"), (8, 21, "or"), (17, 23, "orange"), (24, 21, "orange"), (6, 15, "or")]:
        t.peindre(disque(x + 0.5, y + 0.5, 1.3), fam, "sphere")
    t.poser(arc(16, 17, 13.8, 200, 300) , "w")
    return t.contour()


@dessin
def rouleau_aristote():
    t = toile()
    t.peindre(rect(7, 6, 24, 25), "parchemin", "biseau", 2)
    for y in range(9, 24, 3):
        for x in range(9, 23):
            if (x * 3 + y) % 5 != 0:
                t.poser({(x, y)}, "A")
    t.peindre(rect(4, 3, 27, 6), "bois", "cyl_h")
    t.peindre(rect(4, 25, 27, 28), "bois", "cyl_h")
    for x in (2, 28):
        t.peindre(rect(x, 3, x + 1, 6), "or", "biseau")
        t.peindre(rect(x, 25, x + 1, 28), "or", "biseau")
    return t.contour()


@dessin
def cailloux_demosthene():
    t = toile()
    for r, y in ((11, 8), (8, 9)):
        t.poser(arc(16, y + 12, r, 200, 340, 1), "x" if r == 11 else "u")
    t.peindre(ellipse(9, 23, 6, 4.5), "gris", "sphere")
    t.peindre(ellipse(21, 24, 7, 4.5), "gris", "sphere")
    t.peindre(ellipse(15, 17.5, 4.5, 3.3), "parchemin", "sphere")
    t.peindre(ellipse(26, 18, 3, 2.4), "gris", "sphere")
    return t.contour()


@dessin
def cartes_wason():
    t = toile()
    lettres = [("E", "u"), ("K", "u"), ("4", "r"), ("7", "r")]
    for i, (c, coul) in enumerate(lettres):
        x0 = 1 + i * 8
        t.peindre(rect(x0, 8, x0 + 5, 22), "gris", "biseau", 4)
    t.contour()
    for i, (c, coul) in enumerate(lettres):
        x0 = 1 + i * 8
        t.poser(texte(c, x0 + 1, 13), coul)
    return t


@dessin
def roue_loterie():
    t = toile()
    t.peindre(bande((15, 18), (8, 30), 1), "bois", "biseau", 2)
    t.peindre(bande((17, 18), (24, 30), 1), "bois", "biseau", 2)
    import math
    roue = disque(16, 15, 12)
    for (x, y) in roue:
        a = math.degrees(math.atan2(y + 0.5 - 15, x + 0.5 - 16)) % 360
        t.poser({(x, y)}, "r" if int(a // 30) % 2 == 0 else "w")
    t.peindre(anneau(16, 15, 12, 1.6), "or", "plat", 2)
    t.peindre(disque(16, 15, 2.6), "or", "sphere")
    t.poser({(x, y) for (x, y) in disque(16, 15, 9) if (x, y) in t.px and t.px[(x, y)] == "r" and (x + y) % 2 and ((x - 16) ** 2 + (y - 15) ** 2) > 60}, "R")
    t.contour()
    t.peindre(poly([(13, 0), (19, 0), (16, 5)]), "gris", "plat", 1)
    return t


@dessin
def fiche_ebbinghaus():
    t = toile()
    t.peindre(poly([(6, 4), (29, 6), (27, 27), (4, 25)]), "parchemin", "plat", 1)
    t.peindre(rect(3, 6, 26, 26), "parchemin", "biseau", 2)
    t.poser(rect(4, 9, 25, 9), "r")
    for y, mot in ((11, "DAX"), (16, "BOK"), (21, "ZUF")):
        t.poser(texte(mot, 6, y), "n")
    return t.contour()


@dessin
def cloche_pavlov():
    t = toile()
    t.peindre(anneau(16, 4, 2.8, 1.3), "or", "plat", 2)
    t.peindre(disque(16, 26, 2.4), "or", "sphere")
    cloche = poly([(11.5, 6), (20.5, 6), (22.5, 10), (23, 18), (28, 24), (4, 24), (9, 18), (9.5, 10)])
    t.peindre(cloche, "or", "cyl_v")
    t.peindre(rect(4, 22, 27, 24), "or", "biseau", 1)
    t.contour()
    for r in (2, 4):
        t.poser(arc(4, 12, r + 1, 160, 250), "g")
        t.poser(arc(28, 12, r + 1, -70, 20), "g")
    return t


@dessin
def lignes_asch():
    t = toile()
    t.peindre(rect(2, 4, 29, 27), "gris", "biseau", 4)
    t.contour()
    t.poser(rect(6, 8, 7, 19), "n")
    for x, y0 in ((14, 12), (20, 8), (26, 15)):
        t.poser(rect(x, y0, x + 1, 19), "n")
    t.poser(texte("A", 13, 21) | texte("B", 19, 21) | texte("C", 25, 21), "G")
    return t


@dessin
def tableau_mendeleiev():
    t = toile()
    t.peindre(rect(1, 3, 30, 28), "parchemin", "biseau", 2)
    couleurs = ["r", "o", "u", "u", "u", "e", "y", "p"]
    vides = {(2, 4), (5, 3), (4, 5)}
    for col in range(7):
        for lig in range(6):
            x0, y0 = 3 + col * 4, 5 + lig * 4
            if (col, lig) in vides:
                t.poser(rect(x0, y0, x0 + 2, y0 + 2), "v")
                t.poser({(x0 + 1, y0 + 1)}, "r")
            else:
                c = couleurs[col]
                t.poser(rect(x0, y0, x0 + 2, y0 + 2), c)
                t.poser({(x0, y0)}, {"r": "f", "o": "a", "u": "x", "e": "i", "y": "j", "p": "q"}[c])
    return t.contour()


@dessin
def modele_moleculaire():
    t = toile()
    t.peindre(bande((16, 14), (5, 22), 1.1), "gris", "plat", 2)
    t.peindre(bande((16, 14), (27, 22), 1.1), "gris", "plat", 2)
    t.peindre(disque(5, 23, 4), "gris", "sphere")
    t.peindre(disque(27, 23, 4), "gris", "sphere")
    t.peindre(disque(16, 13, 8.5), "rouge", "sphere")
    return t.contour()


@dessin
def papier_tournesol():
    t = toile()
    verre = rect(6, 11, 25, 29)
    t.peindre(verre, "cyan", "cyl_v", 2)
    t.peindre(rect(8, 18, 23, 27), "rouge", "cyl_v", 3)
    t.peindre(rect(14, 2, 17, 26), "parchemin", "biseau", 2)
    t.peindre(rect(14, 18, 17, 26), "rouge", "biseau", 2)
    t.poser(rect(7, 11, 7, 28), "d")
    t.peindre(rect(4, 10, 27, 11), "cyan", "plat", 2)
    return t.contour()


@dessin
def balance_lavoisier():
    t = toile()
    t.peindre(rect(7, 26, 24, 29), "bois", "biseau", 2)
    t.peindre(rect(15, 7, 16, 26), "or", "cyl_v")
    t.peindre(rect(3, 7, 28, 8), "or", "biseau", 2)
    t.peindre(rect(15, 2, 16, 6), "gris", "plat", 1)
    t.peindre(disque(16, 2, 1.6), "or", "sphere")
    for cx in (5, 26):
        t.poser(trait(cx, 9, cx - 3, 18) | trait(cx, 9, cx + 3, 18), "Y")
        t.peindre(ellipse(cx + 0.5, 19, 5, 1.8), "or", "sphere")
    t.peindre(disque(5.5, 15.5, 2.6), "cyan", "sphere")
    t.peindre(rect(24, 15, 28, 17), "gris", "biseau", 2)
    t.peindre(rect(25, 13, 27, 14), "gris", "biseau", 2)
    return t.contour()


@dessin
def alambic():
    t = toile()
    t.peindre(rect(2, 25, 19, 30), "rouge", "biseau", 1)
    t.poser({(x, y) for x in range(2, 20) for y in range(25, 31) if y % 2 == 0 and x % 4 == 1}, "1")
    t.peindre(poly([(6, 25), (8, 21), (10, 24), (12, 20), (14, 24), (16, 22), (16, 25)]), "orange", "plat", 1)
    t.peindre(bande((13, 6), (27, 14), 1.2), "cuivre", "biseau", 1)
    t.peindre(rect(23, 14, 28, 26), "cyan", "cyl_v", 2)
    for y in range(15, 26, 3):
        t.poser(trait(23, y, 28, y + 1), "m")
    t.peindre(disque(25.5, 28.5, 2.4), "vert", "sphere")
    t.peindre(disque(11, 19, 7.5), "cuivre", "sphere")
    t.peindre(rect(9, 7, 13, 12), "cuivre", "cyl_v")
    t.peindre(ellipse(11, 7, 4.5, 3), "cuivre", "sphere")
    return t.contour()


@dessin
def lunette_galilee():
    t = toile()
    a, b = (6, 26), (26, 6)
    tube = bande(a, b, 2.0, 3.0)
    peindre_tube(t, tube, "cuivre", a, b, 2.6)
    import math
    for f in (0.12, 0.42, 0.72, 0.93):
        cx, cy = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        anneau_or = {p for p in tube if abs((p[0] + 0.5 - cx) * 0.707 - (p[1] + 0.5 - cy) * 0.707) < 0.8}
        peindre_tube(t, anneau_or, "or", a, b, 2.6)
    t.peindre(ellipse(26.5, 5.5, 2.2, 2.2) & bande((24, 8), (29, 3), 3.4), "cyan", "plat", 2)
    t.peindre(bande((3, 29), (6, 26), 1.3), "gris", "plat", 1)
    return t.contour()


@dessin
def prisme_newton():
    t = toile()
    t.peindre(poly([(15, 5), (26, 26), (4, 26)]), "cyan", "biseau", 1)
    t.peindre(poly([(15, 9), (22, 23), (8, 23)]), "cyan", "plat", 2)
    t.contour()
    t.poser(trait(0, 18, 10, 16, 1) | trait(0, 19, 10, 17, 1), "w")
    for i, c in enumerate("royeup"):
        t.poser(trait(20, 17 + i * 0.3, 31, 15 + i * 2.4), c)
    return t


@dessin
def pendule_foucault():
    t = toile()
    t.peindre(ellipse(16, 29, 14, 2.3), "parchemin", "plat", 1)
    t.poser({(x, 29) for x in range(4, 29, 2)}, "Y")
    t.peindre(rect(4, 2, 27, 4), "bois", "biseau", 2)
    t.poser(trait(16, 5, 19, 20), "G")
    t.peindre(disque(19.5, 24, 4.2), "or", "sphere")
    t.poser({(19, 28), (19, 29)}, "n")
    return t.contour()


@dessin
def plaque_hubble():
    t = toile()
    t.peindre(rect(2, 4, 29, 27), "gris", "biseau", 2)
    t.peindre(rect(4, 6, 27, 25), "nuit", "plat", 0)
    import random
    r = random.Random(7)
    for _ in range(26):
        t.poser({(r.randint(4, 27), r.randint(6, 25))}, r.choice("lzg"))
    t.peindre(ellipse(15, 14, 8, 3), "nuit", "plat", 1)
    t.peindre(ellipse(15, 14, 4, 1.4), "gris", "sphere")
    t.poser(anneau(23, 10, 2.2, 0.9), "r")
    t.poser({(23, 10)}, "w")
    t.poser(texte("VAR!", 11, 19), "r")
    return t.contour()


@dessin
def sphere_armillaire():
    t = toile()
    t.peindre(ellipse(16, 29.5, 7, 1.8), "bois", "sphere")
    t.peindre(rect(15, 24, 16, 28), "or", "cyl_v")
    t.peindre(disque(16, 13, 3.6), "bleu", "sphere")
    t.poser(anneau(16, 13, 11.5, 1.4), "y")
    t.poser(ellipse_tournee(16, 13, 11, 3.6, 0, 1.3), "Y")
    t.poser(ellipse_tournee(16, 13, 11, 3.6, -24, 1.3), "j")
    t.poser(ellipse_tournee(16, 13, 3.8, 11, 0, 1.2), "y")
    return t.contour()


@dessin
def pile_volta():
    t = toile()
    t.peindre(rect(3, 27, 28, 29), "bois", "biseau", 2)
    t.peindre(rect(5, 3, 26, 4), "bois", "biseau", 2)
    for x in (5, 25):
        t.peindre(rect(x, 5, x + 1, 26), "cyan", "cyl_v", 2)
    couches = ["cuivre", "gris", "parchemin"]
    y = 25
    i = 0
    while y >= 6:
        t.peindre(rect(9, y, 22, y + 1), couches[i % 3], "cyl_v")
        y -= 2
        i += 1
    t.contour()
    t.poser(courbe([(22, 6), (28, 2), (31, 6)]), "r")
    t.poser(courbe([(22, 25), (30, 24), (31, 20)]), "n")
    return t


@dessin
def bouteille_leyde():
    t = toile()
    t.peindre(rect(9, 10, 22, 28), "cyan", "cyl_v", 2)
    t.peindre(rect(9, 18, 22, 28), "gris", "cyl_v")
    t.peindre(rect(11, 7, 20, 10), "bois", "biseau", 2)
    t.peindre(rect(15, 3, 16, 7), "or", "cyl_v")
    t.peindre(disque(16, 3, 2.7), "or", "sphere")
    t.poser({(16, y) for y in range(11, 25, 2)}, "Y")
    t.contour()
    t.poser(courbe([(20, 1), (22, 3), (21, 4), (24, 6)]), "j")
    return t


@dessin
def ampoule_edison():
    t = toile()
    t.peindre(rect(12, 23, 19, 29), "gris", "cyl_v")
    t.poser({(x, y) for x in range(12, 20) for y in range(24, 29) if y % 2 == 0}, "G")
    t.peindre(rect(14, 30, 17, 30), "gris", "plat", 0)
    verre = disque(16, 12, 10) | poly([(10, 18), (22, 18), (19.5, 23.5), (12.5, 23.5)])
    t.peindre(verre, "cyan", "sphere", 2)
    t.poser(disque(16, 11, 5.5) & {p for p in verre}, "d")
    t.poser(trait(14, 23, 13, 13) | trait(18, 23, 19, 13), "g")
    t.poser(arc(16, 12, 3.2, 180, 360), "o")
    t.poser(arc(16, 12, 4.4, 190, 350), "j")
    t.poser(arc(16, 12, 9, 200, 250), "w")
    return t.contour()


@dessin
def bobine_faraday():
    t = toile()
    t.poser(courbe([(7, 22), (6, 30)]), "r")
    t.poser(courbe([(25, 22), (26, 30)]), "u")
    t.peindre(anneau(16, 15, 11.5, 4), "gris", "biseau", 2)
    for y in range(7, 24, 2):
        t.peindre(rect(3, y, 9, y), "cuivre", "cyl_h", 2)
        t.peindre(rect(23, y, 29, y), "orange", "cyl_h", 1)
    return t.contour()


@dessin
def cerf_volant_franklin():
    t = toile()
    t.poser(courbe([(16, 22), (14, 25), (18, 27), (21, 28)]), "g")
    for p in [(14, 24), (18, 27)]:
        t.peindre(poly([(p[0] - 2, p[1] - 1), (p[0] + 2, p[1] + 1), (p[0] + 2, p[1] - 1), (p[0] - 2, p[1] + 1)]), "or", "plat", 2)
    t.peindre(poly([(16, 3), (26, 11), (16, 22), (6, 11)]), "rouge", "biseau", 2)
    t.poser(trait(16, 4, 16, 21) | trait(7, 11, 25, 11), "t")
    t.peindre(disque(22.5, 28.5, 1.6) | rect(23, 28, 28, 28) | {(27, 29), (25, 29)}, "or", "biseau", 2)
    t.contour()
    t.poser(poly([(4, 0), (8, 0), (5, 3), (7, 3), (2, 8), (4, 4), (2, 4)]), "j")
    return t


# --- Philosophes ---------------------------------------------------------------

@dessin
def coupe_cigue():
    t = toile()
    t.peindre(anneau(4, 12, 2.6, 1.2) | anneau(28, 12, 2.6, 1.2), "orange", "plat", 1)
    t.peindre(poly([(4, 10), (28, 10), (23, 18), (9, 18)]), "orange", "cyl_v")
    t.poser(rect(6, 13, 25, 14) & poly([(4, 10), (28, 10), (23, 18), (9, 18)]), "n")
    t.poser({(x, 13) for x in range(7, 25, 3)} | {(x, 14) for x in range(8, 25, 3)}, "O")
    t.peindre(ellipse(16, 10, 12, 2.2), "vert", "plat", 1)
    t.poser(ellipse(14, 9.6, 5, 0.9), "e")
    t.peindre(rect(15, 18, 16, 25), "orange", "cyl_v")
    t.peindre(ellipse(16, 26, 6.5, 1.8), "orange", "sphere")
    return t.contour()


@dessin
def rasoir_ockham():
    t = toile()
    t.peindre(poly([(3, 11), (21, 11), (23, 16.5), (3, 18)]), "gris", "cyl_h", 4)
    t.poser(trait(3, 17, 22, 16), "w")
    t.peindre(bande((20, 14), (28, 22), 2.2), "bois", "biseau", 2)
    t.peindre(disque(20.5, 14.5, 1.4), "or", "sphere")
    t.contour()
    for p in [(6, 22), (9, 25), (12, 22), (8, 28), (14, 27)]:
        t.poser({p, (p[0] + 1, p[1] - 1)}, "h")
    return t


@dessin
def poele_descartes():
    t = toile()
    t.peindre(rect(14, 0, 17, 5), "gris", "cyl_v")
    t.peindre(rect(6, 5, 25, 7), "ivoire", "biseau", 0)
    t.peindre(rect(8, 7, 23, 27), "ivoire", "plat", 0)
    for y in range(8, 27, 4):
        for x in range(8, 23, 4):
            t.poser(rect(x, y, x + 3, y + 3) - rect(x + 1, y + 1, x + 2, y + 2), "x")
            t.poser({(x + 1, y + 1), (x + 2, y + 2)}, "u")
    t.peindre(rect(12, 18, 19, 25), "gris", "biseau", 1)
    t.peindre(rect(13, 21, 18, 24), "orange", "plat", 1)
    t.poser({(14, 22), (16, 21), (17, 23)}, "j")
    t.peindre(rect(6, 27, 25, 29), "bois", "biseau", 2)
    return t.contour()


@dessin
def marteau_nietzsche():
    t = toile()
    peindre_tube(t, bande((13, 12), (26, 29), 1.8), "bois", (13, 12), (26, 29), 1.8)
    t.peindre(poly([(3, 6), (21, 3), (23, 11), (5, 14)]), "gris", "biseau", 3)
    t.peindre(poly([(3, 6), (6, 5.5), (8, 13.5), (5, 14)]), "gris", "plat", 1)
    t.contour()
    t.poser(courbe([(1, 18), (3, 16)]) | courbe([(5, 20), (6, 17)]) | courbe([(26, 4), (29, 2)]), "y")
    return t


@dessin
def lanterne_diogene():
    t = toile()
    t.peindre(anneau(16, 4, 3, 1.2), "gris", "plat", 1)
    t.peindre(poly([(16, 5), (23, 10), (9, 10)]), "gris", "biseau", 1)
    t.peindre(rect(10, 10, 21, 24), "or", "plat", 3)
    t.peindre(disque(16, 18, 4.5), "or", "sphere", 3)
    t.peindre(poly([(16, 13), (18.5, 19), (16, 21.5), (13.5, 19)]), "orange", "sphere")
    t.poser({(16, 17), (16, 18)}, "j")
    t.poser(rect(10, 10, 10, 24) | rect(21, 10, 21, 24) | rect(15, 10, 16, 11), "n")
    t.peindre(rect(9, 24, 22, 27), "gris", "biseau", 1)
    return t.contour()


def objets():
    return {nom: fn().lignes() for nom, fn in DESSINS.items()}


if __name__ == "__main__":
    from dessin import apercu
    import sys
    apercu(objets(), sys.argv[1] if len(sys.argv) > 1 else "/tmp/objets.png")
