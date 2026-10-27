"""v17 : chaque succès a son illustration en pixel art (32 × 32).

La plupart réutilisent un dessin du jeu : objet du cabinet, case du plateau, portrait d'ennemi ou de savant.
Les autres sont dessinés ici, avec le même atelier (dessin.py) : lumière en haut à gauche, contour sombre.
"""
import math

from dessin import Toile, anneau, arc, bande, courbe, disque, ellipse, poly, rect, texte, trait

N = 32
DESSINS = {}


def dessin(fn):
    DESSINS[fn.__name__.replace("_", "-")] = fn
    return fn


def toile():
    return Toile(N, N)


@dessin
def empreinte():
    t = toile()
    t.peindre(ellipse(16, 15, 6.5, 6) | ellipse(15, 22, 5, 6.5), "peau", "sphere")
    for x, y, r in [(10.5, 7.5, 2.3), (14, 5.2, 2.1), (17.6, 5, 1.9), (20.6, 6.4, 1.7), (22.6, 8.8, 1.4)]:
        t.peindre(disque(x, y, r), "peau", "sphere")
    return t.contour()

@dessin
def baignoire():
    t = toile()
    for x, y, r in [(9, 9, 2.5), (14, 6, 3), (20, 8, 2.4), (24, 12, 1.8), (6, 13, 1.6)]:
        t.peindre(disque(x, y, r), "cyan", "sphere")
    t.peindre(rect(3, 14, 28, 15), "cyan", "plat", 1)
    t.peindre(poly([(2, 15), (29, 15), (27, 25), (5, 25)]), "gris", "biseau", 4)
    t.peindre(rect(6, 26, 8, 28), "or", "biseau")
    t.peindre(rect(23, 26, 25, 28), "or", "biseau")
    return t.contour()


@dessin
def citron():
    t = toile()
    t.peindre(ellipse(16, 17, 12, 8.5), "or", "sphere")
    t.peindre(ellipse(4.5, 17, 2, 1.6), "or", "plat", 1)
    t.peindre(ellipse(27.5, 17, 2, 1.6), "or", "plat", 1)
    t.peindre(poly([(17, 9), (22, 4), (25, 6), (20, 10)]), "vert", "biseau", 2)
    return t.contour()


@dessin
def coeur():
    t = toile()
    forme = disque(10.5, 11.5, 6.5) | disque(21.5, 11.5, 6.5) | poly([(4.2, 13.5), (27.8, 13.5), (16, 28)])
    t.peindre(forme, "rouge", "sphere")
    t.poser({(8, 9), (9, 8), (8, 10)}, "f")
    return t.contour()


@dessin
def cobaye():
    t = toile()
    t.peindre(ellipse(15, 19, 12, 8), "orange", "sphere")
    t.peindre(ellipse(10, 17, 5, 5), "ivoire", "plat")
    t.peindre(ellipse(24, 17, 5.5, 5), "orange", "sphere")
    t.peindre(disque(21, 12, 2), "rose", "plat", 1)
    t.poser({(25, 16), (26, 16)}, "k")
    t.poser({(29, 19)}, "F")
    t.peindre(rect(8, 26, 10, 27), "rose", "plat", 1)
    t.peindre(rect(20, 26, 22, 27), "rose", "plat", 1)
    return t.contour()


@dessin
def ouroboros():
    t = toile()
    t.peindre(anneau(16, 16, 12, 4.2), "vert", "biseau", 2)
    for a in range(0, 360, 30):
        r = math.radians(a)
        t.poser({(int(16 + 10 * math.cos(r)), int(16 + 10 * math.sin(r)))}, "2")
    t.peindre(ellipse(9, 6.5, 4.6, 3.6), "vert", "sphere")
    t.poser({(8, 5)}, "y")
    t.poser({(12, 8), (13, 9)}, "r")
    return t.contour()


@dessin
def tour_pise():
    t = toile()
    def penche(pts):
        return [(x + (28 - y) * 0.22, y) for x, y in pts]
    for i in range(6):
        y0 = 25 - i * 4
        t.peindre(poly(penche([(9, y0 - 3.6), (21, y0 - 3.6), (21, y0), (9, y0)])), "ivoire" if i % 2 else "gris", "biseau", 0 if i % 2 else 4)
        for x in (11, 14, 17, 20):
            px = int(x + (28 - (y0 - 1.5)) * 0.22) - 1
            t.poser({(px, y0 - 2), (px, y0 - 1)}, "G")
    t.peindre(poly(penche([(11, 1.5), (19, 1.5), (19, 4.4), (11, 4.4)])), "gris", "biseau", 4)
    t.peindre(rect(4, 28, 28, 29), "vert", "biseau", 2)
    return t.contour()


@dessin
def cerveau():
    t = toile()
    t.peindre(ellipse(16, 15, 13, 10.5), "rose", "sphere")
    for pts in ([(16, 5), (16, 25)], [(8, 9), (11, 13), (7, 17)], [(24, 9), (21, 13), (25, 17)], [(10, 20), (14, 22)], [(22, 20), (18, 22)], [(12, 7), (13, 10)], [(20, 7), (19, 10)]):
        t.poser(courbe(pts), "F")
    t.peindre(rect(14, 25, 18, 29), "rose", "cyl_v")
    return t.contour()


@dessin
def muraille():
    t = toile()
    t.peindre(poly([(0, 31), (0, 22), (12, 19), (31, 23), (31, 31)]), "vert", "biseau", 2)
    t.peindre(rect(0, 15, 31, 21), "parchemin", "biseau", 1)
    for x in range(0, 32, 4):
        t.peindre(rect(x, 13, x + 1, 14), "parchemin", "biseau", 1)
    for x0 in (4, 21):
        t.peindre(rect(x0, 8, x0 + 6, 21), "parchemin", "biseau", 1)
        for x in (x0, x0 + 3, x0 + 6):
            t.peindre(rect(x, 6, x, 7), "parchemin", "plat", 1)
        t.peindre(rect(x0 + 2, 11, x0 + 4, 14), "nuit", "plat")
    for x in range(1, 31, 5):
        t.poser({(x, 18), (x + 1, 18)}, "A")
    return t.contour()

@dessin
def eclair():
    t = toile()
    t.peindre(ellipse(16, 6, 13, 5), "gris", "sphere", base=3)
    t.peindre(poly([(17, 9), (10, 19), (15, 19), (11, 30), (22, 15), (16, 15), (21, 9)]), "or", "biseau", 2)
    return t.contour()


@dessin
def tourbillon():
    t = toile()
    t.peindre(ellipse(16, 18, 14, 10), "gris", "biseau", 4)
    t.peindre(ellipse(16, 17, 11.5, 7.5), "cyan", "plat", 1)
    pts = [(16 + (0.6 + a / 10) * math.cos(a), 17 + (0.4 + a / 15) * math.sin(a)) for a in [i * 0.3 for i in range(32)]]
    t.poser(courbe(pts), "C")
    t.peindre(disque(16, 17, 1.4), "nuit", "plat")
    return t.contour()


@dessin
def vitrail():
    t = toile()
    forme = rect(6, 12, 25, 29) | disque(16, 12.5, 10)
    t.peindre(forme, "gris", "plat", 1)
    couleurs = ["rouge", "bleu", "or", "vert", "violet", "cyan"]
    for i, (x0, y0, x1, y1) in enumerate([(8, 13, 15, 20), (17, 13, 23, 20), (8, 22, 15, 27), (17, 22, 23, 27)]):
        t.peindre(rect(x0, y0, x1, y1), couleurs[i], "biseau", 2)
    for i, a in enumerate(range(195, 345, 30)):
        r = math.radians(a + 15)
        t.peindre(disque(16 + 5.5 * math.cos(r), 12 + 5.5 * math.sin(r), 2.2), couleurs[(i + 1) % 6], "sphere")
    t.peindre(disque(16, 11, 2.2), "or", "sphere")
    return t.contour()


@dessin
def verre_eau():
    t = toile()
    t.peindre(poly([(8, 4), (24, 4), (22, 28), (10, 28)]), "cyan", "plat", 2)
    t.peindre(poly([(9, 11), (23, 11), (22, 28), (10, 28)]), "cyan", "biseau", 1)
    t.poser(trait(11, 7, 11, 25), "d")
    t.peindre(texte("8", 14, 16), "bleu", "plat", 1)
    return t.contour()


@dessin
def lune():
    t = toile()
    t.peindre(disque(15, 16, 12) - disque(21, 12, 10.5), "or", "sphere")
    for x, y in [(25, 6), (28, 18), (22, 26), (6, 4)]:
        t.poser({(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)}, "j")
    return t.contour()


@dessin
def soleil():
    t = toile()
    for a in range(0, 360, 45):
        r = math.radians(a)
        t.peindre(bande((16 + 9 * math.cos(r), 14 + 9 * math.sin(r)), (16 + 14 * math.cos(r), 14 + 14 * math.sin(r)), 1.6, 0.4), "orange", "plat", 1)
    t.peindre(disque(16, 14, 8), "or", "sphere")
    t.peindre(rect(1, 23, 30, 30), "bleu", "biseau", 2)
    t.poser(trait(4, 26, 12, 26) | trait(18, 28, 27, 28), "x")
    return t.contour()


@dessin
def sablier():
    t = toile()
    t.peindre(rect(6, 2, 25, 4), "bois", "biseau", 2)
    t.peindre(rect(6, 27, 25, 29), "bois", "biseau", 2)
    verre = poly([(8, 5), (23, 5), (17, 16), (23, 27), (8, 27), (14, 16)])
    t.peindre(verre, "cyan", "plat", 2)
    t.peindre(poly([(11, 9), (20, 9), (16.5, 15), (15.5, 15)]), "or", "plat", 2)
    t.peindre(poly([(10, 26), (21, 26), (17, 21), (14, 21)]), "or", "biseau", 2)
    t.poser(trait(15, 16, 15, 21), "y")
    return t.contour()


@dessin
def pluton():
    t = toile()
    t.peindre(disque(16, 16, 11), "parchemin", "sphere")
    t.peindre(poly([(13, 17), (17, 13), (22, 15), (23, 21), (18, 25), (14, 22)]), "ivoire", "plat")
    t.peindre(ellipse(10, 11, 2.5, 1.6), "cuivre", "plat", 1)
    t.poser(texte("9", 26, 2), "r")
    t.poser(trait(24, 1, 31, 8, 1), "r")
    return t.contour()


@dessin
def chat():
    t = toile()
    t.peindre(poly([(4, 16), (28, 16), (28, 29), (4, 29)]), "bois", "biseau", 2)
    t.peindre(poly([(4, 16), (12, 11), (14, 16)]), "bois", "plat", 3)
    t.peindre(ellipse(19, 13, 6, 5), "gris", "sphere")
    t.peindre(poly([(14, 10), (15, 4), (18, 9)]), "gris", "plat", 2)
    t.peindre(poly([(20, 9), (23, 4), (24, 10)]), "gris", "plat", 2)
    t.poser({(17, 12), (21, 12)}, "y")
    t.poser({(19, 14)}, "F")
    t.peindre(texte("?", 8, 20), "or", "plat", 2)
    return t.contour()


@dessin
def elephant():
    t = toile()
    t.peindre(ellipse(17, 13, 8, 8.5), "gris", "sphere", maxi=3)
    t.peindre(ellipse(9, 14, 6.5, 8), "gris", "biseau", 1)
    t.peindre(bande((19, 18), (22, 28), 2.6, 1.6), "gris", "plat", 2)
    t.peindre(rect(22, 27, 25, 28), "gris", "plat", 2)
    t.peindre(bande((24, 18), (29, 23), 1.3, 0.7), "ivoire", "plat")
    t.poser({(20, 10), (20, 11)}, "k")
    return t.contour()


@dessin
def grenouille():
    t = toile()
    t.peindre(ellipse(16, 20, 12, 8), "vert", "sphere")
    t.peindre(disque(10, 11, 4), "vert", "sphere")
    t.peindre(disque(22, 11, 4), "vert", "sphere")
    t.peindre(disque(10, 11, 2), "ivoire", "plat")
    t.peindre(disque(22, 11, 2), "ivoire", "plat")
    t.poser({(10, 11), (22, 11)}, "k")
    t.poser(arc(16, 18, 6, 20, 160), "2")
    t.peindre(ellipse(6, 27, 4, 1.6), "vert", "plat", 1)
    t.peindre(ellipse(26, 27, 4, 1.6), "vert", "plat", 1)
    return t.contour()


@dessin
def boussole():
    t = toile()
    t.peindre(disque(16, 16, 13), "cuivre", "sphere")
    t.peindre(disque(16, 16, 10.5), "parchemin", "plat", 2)
    t.peindre(poly([(16, 6), (19, 16), (13, 16)]), "rouge", "plat", 2)
    t.peindre(poly([(16, 26), (19, 16), (13, 16)]), "gris", "plat", 3)
    t.poser(texte("N", 15, 0) if False else set(), "k")
    t.peindre(disque(16, 16, 1.4), "or", "plat", 2)
    return t.contour()


@dessin
def etoile():
    t = toile()
    pts = []
    for i in range(10):
        r = 14 if i % 2 == 0 else 6
        a = math.radians(-90 + i * 36)
        pts.append((16 + r * math.cos(a), 17 + r * math.sin(a)))
    t.peindre(poly(pts), "or", "sphere")
    for x, y in [(4, 4), (27, 26), (5, 25)]:
        t.poser({(x, y)}, "j")
    return t.contour()


@dessin
def plante():
    t = toile()
    t.peindre(poly([(9, 20), (23, 20), (21, 30), (11, 30)]), "cuivre", "biseau", 1)
    t.peindre(rect(8, 19, 24, 21), "cuivre", "biseau", 2)
    t.poser(trait(16, 19, 16, 9), "E")
    t.peindre(ellipse(10.5, 11, 5, 2.6), "vert", "sphere")
    t.peindre(ellipse(21.5, 8, 5, 2.6), "vert", "sphere")
    t.peindre(ellipse(16, 4.5, 2.6, 3.6), "vert", "sphere")
    return t.contour()


@dessin
def tonneau():
    t = toile()
    t.peindre(ellipse(16, 18, 11, 12) & rect(0, 7, 31, 29), "bois", "cyl_v")
    for y in (10, 18, 26):
        t.peindre(rect(5 if y == 18 else 6, y, 26 if y == 18 else 25, y), "gris", "plat", 1)
    t.peindre(ellipse(16, 7.5, 9, 2), "bois", "plat", 0)
    t.peindre(disque(16, 17, 3), "nuit", "plat")
    return t.contour()


@dessin
def cygne():
    t = toile()
    t.peindre(rect(1, 25, 30, 29), "bleu", "biseau", 2)
    t.peindre(ellipse(17, 21, 10, 5), "nuit", "sphere")
    t.peindre(poly([(19, 19), (25, 12), (24, 8)]) | bande((9, 19), (9, 9), 1.8), "nuit", "plat")
    t.peindre(courbe([(9, 20), (8, 12), (9, 7), (12, 5)], 3), "nuit", "plat")
    t.peindre(poly([(12, 4), (16, 5.5), (12, 7)]), "rouge", "plat", 2)
    t.poser({(11, 5)}, "w")
    return t.contour()


@dessin
def caverne():
    t = toile()
    t.peindre(rect(0, 4, 31, 31), "parchemin", "biseau", 0)
    t.peindre(ellipse(16, 24, 10, 14) & rect(0, 0, 31, 31), "nuit", "plat")
    t.peindre(ellipse(16, 27, 5, 6) & rect(0, 0, 31, 31), "or", "sphere")
    t.peindre(disque(16, 22, 1.6), "or", "plat", 3)
    t.peindre(rect(0, 29, 31, 31), "parchemin", "plat", 0)
    return t.contour()


@dessin
def colonnes():
    t = toile()
    for x in (5, 21):
        t.peindre(rect(x, 7, x + 5, 26), "ivoire", "cyl_v")
        t.peindre(rect(x - 1, 4, x + 6, 6), "parchemin", "biseau", 1)
        t.peindre(rect(x - 1, 27, x + 6, 29), "parchemin", "biseau", 1)
    t.peindre(bande((6, 12), (26, 18), 1.4), "rouge", "plat", 2)
    t.peindre(bande((6, 18), (26, 12), 1.4), "rouge", "plat", 1)
    return t.contour()


@dessin
def rocher():
    t = toile()
    t.peindre(poly([(1, 30), (31, 14), (31, 30)]), "vert", "biseau", 2)
    t.peindre(disque(19, 11, 7), "gris", "sphere")
    t.peindre(poly([(6, 25), (10, 17), (13, 16), (15, 19), (10, 24)]), "peau", "sphere")
    t.peindre(disque(10, 14, 2.5), "peau", "sphere")
    return t.contour()


@dessin
def sel():
    t = toile()
    face = rect(6, 12, 19, 25)
    t.peindre(poly([(6, 12), (12, 6), (25, 6), (19, 12)]), "gris", "plat", 5)
    t.peindre(poly([(19, 12), (25, 6), (25, 19), (19, 25)]), "gris", "plat", 3)
    t.peindre(face, "gris", "plat", 4)
    t.poser(trait(8, 14, 11, 14) | trait(8, 15, 8, 18), "w")
    return t.contour()


@dessin
def eau_boum():
    t = toile()
    t.peindre(poly([(5, 20), (27, 20), (25, 30), (7, 30)]), "cyan", "biseau", 1)
    for a in range(0, 360, 40):
        r = math.radians(a)
        t.peindre(bande((16, 14), (16 + 13 * math.cos(r), 14 + 11 * math.sin(r)), 2, 0.3), "orange", "plat", 1)
    t.peindre(disque(16, 14, 5.5), "or", "sphere")
    t.peindre(disque(16, 14, 2.4), "gris", "plat", 5)
    return t.contour()


@dessin
def clou():
    t = toile()
    t.peindre(rect(0, 18, 31, 31), "bois", "biseau", 2)
    t.peindre(bande((10, 6), (18, 22), 1.5), "gris", "cyl_v")
    t.peindre(bande((6, 7), (14, 4), 2), "gris", "biseau", 4)
    t.peindre(rect(19, 4, 28, 11), "parchemin", "biseau", 1)
    t.poser(trait(21, 7, 26, 7) | trait(21, 9, 25, 9), "A")
    return t.contour()


@dessin
def mur():
    t = toile()
    for rang in range(7):
        y = 3 + rang * 4
        dec = 0 if rang % 2 else -4
        for x in range(dec, 32, 8):
            t.peindre(rect(max(1, x + 1), y, min(30, x + 7), y + 2), "cuivre", "biseau", 1 + (rang + x) % 2)
    t.peindre(rect(11, 10, 20, 17), "parchemin", "biseau", 1)
    t.poser({(15, 9), (16, 9)}, "G")
    return t.contour()


@dessin
def pinceau():
    t = toile()
    t.peindre(rect(1, 20, 30, 30), "cuivre", "biseau", 1)
    t.peindre(rect(1, 20, 16, 30), "ivoire", "plat")
    t.peindre(bande((24, 3), (17, 14), 1.6), "bois", "cyl_v")
    t.peindre(bande((17, 14), (15, 17), 2.2), "gris", "biseau", 3)
    t.peindre(poly([(12, 17), (18, 17), (15, 23), (12, 22)]), "ivoire", "biseau")
    return t.contour()


def dessins():
    return {nom: fn().lignes() for nom, fn in DESSINS.items()}


# Illustration de chaque succès : (« objet » | « icone » | « dessin » | « ennemi » | « savant », identifiant).
ILLUSTRATIONS = {
    "premier-pas": ("dessin", "empreinte"), "eureka": ("objet", "couronne-hieron"), "petit-gauss": ("objet", "boulier"),
    "branche-logique": ("objet", "compas-euclide"), "branche-mecanique": ("objet", "metre-etalon"), "branche-savoir": ("objet", "boite-petri"),
    "branche-eloquence": ("objet", "cailloux-demosthene"), "branche-lucidite": ("dessin", "citron"), "branche-empathie": ("dessin", "coeur"),
    "polymathe": ("savant", "ibn-sina"), "dix-competences": ("icone", "lunettes"), "arbre-complet": ("savant", "newton"),
    "premier-rappel": ("dessin", "cobaye"), "serie-rappels": ("objet", "rasoir-ockham"), "cinquante-rappels": ("icone", "pyramide"),
    "constance": ("icone", "bougie"), "niveau-5": ("dessin", "ouroboros"), "resilience": ("icone", "zero"),
    "tour-de-pise": ("dessin", "tour-pise"), "pomme": ("objet", "pomme-newton"), "lucide": ("dessin", "citron"),
    "dix-pour-cent": ("dessin", "cerveau"), "einstein-notes": ("savant", "einstein"), "grande-muraille": ("dessin", "muraille"),
    "foudre-deux-fois": ("dessin", "eclair"), "coriolis": ("dessin", "tourbillon"), "carte-langue": ("objet", "papier-tournesol"),
    "ampoule-partagee": ("objet", "ampoule-edison"), "saisons": ("icone", "heliocentre"), "sang-bleu": ("objet", "microscope-hooke"),
    "vitraux": ("dessin", "vitrail"), "effet-mozart": ("objet", "diapason"), "styles-apprentissage": ("objet", "fiche-ebbinghaus"),
    "eppur": ("objet", "lunette-galilee"), "perseverance": ("objet", "roue-loterie"), "plus-apte": ("savant", "darwin"),
    "pois-de-senteur": ("objet", "pois-mendel"), "cloche": ("objet", "cloche-pavlov"), "trente-huit-temoins": ("objet", "lignes-asch"),
    "miroirs-ardents": ("objet", "miroir-ardent"), "deux-hemispheres": ("dessin", "cerveau"), "huit-verres": ("dessin", "verre-eau"),
    "insomniaque": ("dessin", "lune"), "leve-tot": ("dessin", "soleil"), "voyageur-temporel": ("dessin", "sablier"),
    "table-rase": ("objet", "ardoise-boole"), "neutrinos": ("icone", "fusee"), "serendipite": ("icone", "fiole"),
    "procrastination": ("objet", "carnet-darwin"), "pluton": ("dessin", "pluton"), "schrodinger": ("dessin", "chat"),
    "elephant": ("dessin", "elephant"), "preuves-extraordinaires": ("objet", "lanterne-diogene"), "encyclopediste": ("icone", "alexandrie"),
    "un-an": ("objet", "sphere-armillaire"), "deux-nobel": ("savant", "marie-curie"), "nous-saurons": ("objet", "ruban-turing"),
    "wunderkammer": ("objet", "diamant-lavoisier"), "conservateur": ("objet", "medailles-hevesy"), "reve-mendeleiev": ("savant", "mendeleiev"),
    "rien-ne-se-perd": ("objet", "balance-lavoisier"), "grenouilles": ("dessin", "grenouille"), "ohm": ("objet", "bouteille-leyde"),
    "oersted": ("dessin", "boussole"), "poussieres": ("dessin", "etoile"), "big-bang": ("objet", "plaque-hubble"),
    "branche-alchimie": ("objet", "pierre-philosophale"), "branche-cosmos": ("icone", "astrolabe"), "branche-etincelle": ("objet", "cerf-volant-franklin"),
    "plus-ultra": ("dessin", "colonnes"), "nains-geants": ("icone", "pont"), "cultiver-jardin": ("dessin", "plante"),
    "dernier-homme": ("savant", "aristote"), "tonneau-diogene": ("dessin", "tonneau"), "terre-ronde": ("objet", "sphere-armillaire"),
    "pas-voltaire": ("icone", "plume"), "refutable": ("dessin", "cygne"), "branche-sagesse": ("objet", "coupe-cigue"),
    "caverne": ("dessin", "caverne"), "promenade-kant": ("objet", "pendule-foucault"), "nietzsche-soeur": ("objet", "marteau-nietzsche"),
    "promethee": ("objet", "flamme-promethee"), "epoque-moyen-age": ("icone", "enluminure"), "epoque-renaissance": ("icone", "presse"),
    "epoque-classique": ("objet", "lunette-galilee"), "epoque-xixe": ("objet", "prisme-newton"), "epoque-xxe": ("icone", "relativite"),
    "tete-lavoisier": ("icone", "guillotine"), "arcetri": ("icone", "prison"), "eppur-si-muove": ("icone", "heliocentre"),
    "woolsthorpe": ("icone", "puits"), "alexandrie-brule": ("icone", "incendie"), "baignoire": ("dessin", "baignoire"),
    "des-de-dieu": ("objet", "des-pascal"), "sisyphe": ("dessin", "rocher"), "tour-complet": ("icone", "ordinateur"),
    "eternel-retour": ("icone", "roue"), "cycle-meton": ("objet", "mecanisme-anticythere"), "hypotheses-non-fingo": ("objet", "principia"),
    "infaillible": ("icone", "couronne"), "point-bleu": ("objet", "disque-voyager"), "demon-laplace": ("objet", "demon-laplace"),
    "pionnier-ciceron": ("objet", "rouleau-aristote"), "pionnier-lavoisier": ("savant", "lavoisier"), "pionnier-galilee": ("savant", "galilee"),
    "pionnier-bacon": ("objet", "microscope-hooke"), "pionnier-faraday": ("savant", "faraday"), "pionnier-william-james": ("icone", "labyrinthe"),
    "pionnier-socrate": ("objet", "coupe-cigue"),
    "atome-1": ("icone", "atome"), "atome-10": ("objet", "alambic"), "atome-30": ("icone", "fiole"), "atome-63": ("objet", "tableau-mendeleiev"),
    "atome-92": ("objet", "verre-uranium"), "atome-118": ("objet", "modele-moleculaire"), "gaz-nobles": ("icone", "flacon"),
    "halogenes": ("dessin", "sel"), "alcalins": ("dessin", "eau-boum"), "atome-fuite": ("objet", "feuille-or-rutherford"),
    "honte-1": ("dessin", "clou"), "honte-10": ("dessin", "pinceau"), "honte-50": ("dessin", "mur"), "honte-effacee-50": ("dessin", "pinceau"),
}


def illustration(succes):
    """Le champ « illustration » d'un succès ; un succès « Victoire sur X » prend le portrait de l'ennemi."""
    c = succes["condition"]
    if c["type"] == "ennemi_vaincu":
        return {"type": "ennemi", "id": c["id"]}
    from succes_themes import ILLUSTRATIONS as V18
    t, i = ILLUSTRATIONS.get(succes["id"]) or V18[succes["id"]]
    return {"type": t, "id": i}


if __name__ == "__main__":
    from dessin import apercu
    apercu(dessins(), "/tmp/succes_pixels.png", echelle=6, colonnes=8)
