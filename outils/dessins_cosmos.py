"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack Cosmos. Mode d'emploi : outils/dessins_lecons.py."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, anneau, bande, disque, ellipse, poly, rect, trait  # noqa: E402
from dessins_lecons import executer  # noqa: E402


def globe():
    """Une Terre ronde (astro.mesurer/ronde) : la sphère, océans et terres, l'ombre du côté de la nuit."""
    t = Toile(48, 48)
    sphere = disque(24, 24, 20)
    t.peindre(sphere, "bleu", "sphere", base=2)
    terres = (ellipse(17, 15, 7, 5) | ellipse(14, 24, 4, 7) | ellipse(31, 26, 6, 9) | ellipse(29, 12, 5, 3)) & sphere
    t.peindre(terres, "vert", "sphere", base=2)
    t.peindre(ellipse(24, 6, 8, 2) & sphere, "gris", "plat", base=4)
    t.contour()
    return t


def astrolabe():
    """Astrolabe d'argent (astro.ptolemee/transmission) : la mère, l'araignée ajourée, l'alidade, l'anneau de suspension."""
    t = Toile(48, 48)
    t.peindre(anneau(24, 6, 3, 1.4), "gris", "plat", base=3)
    t.peindre(rect(22, 8, 26, 10), "gris", "biseau", base=3)
    mere = disque(24, 27, 19)
    t.peindre(mere, "gris", "sphere", base=3)
    t.peindre(anneau(24, 27, 16, 1), "gris", "plat", base=1)
    for ang in range(0, 360, 15):
        x, y = 24 + 17.5 * math.cos(math.radians(ang)), 27 + 17.5 * math.sin(math.radians(ang))
        t.poser({(int(x), int(y))}, "G")
    # araignée : cercle de l'écliptique décentré et pointes d'étoiles
    t.peindre(anneau(26, 24, 9, 1.2), "or", "plat", base=2)
    for ang in (30, 110, 200, 290):
        x, y = 24 + 13 * math.cos(math.radians(ang)), 27 + 13 * math.sin(math.radians(ang))
        t.peindre(trait(24, 27, x, y, 1), "or", "plat", base=1)
    t.peindre(bande((9, 35), (39, 19), 1.2), "gris", "plat", base=1)
    t.peindre(disque(24, 27, 1.6), "or", "plat", base=3)
    t.contour()
    return t


def roues_maya():
    """Calendriers mayas (astro.maya/calendriers) : deux roues dentées, 13 dents et 20 dents, qui s'engrènent."""
    t = Toile(48, 48)

    def roue(cx, cy, r, n, fam):
        corps = disque(cx, cy, r)
        for i in range(n):
            a = 2 * math.pi * i / n
            corps |= disque(cx + (r + 1.4) * math.cos(a), cy + (r + 1.4) * math.sin(a), 1.4)
        t.peindre(corps, fam, "sphere", base=2)
        t.peindre(anneau(cx, cy, r - 3, 1), fam, "plat", base=0)
        t.peindre(disque(cx, cy, 2), fam, "plat", base=0)

    roue(14, 18, 8.5, 13, "vert")
    roue(31.5, 30, 12.5, 20, "orange")
    t.contour()
    return t


def livre_annote():
    """De revolutionibus (astro.copernic/posterite) : un exemplaire ouvert, les marges pleines de notes à la main."""
    t = Toile(48, 48)
    t.peindre(poly([(3, 12), (23, 15), (23, 41), (3, 38)]) | poly([(25, 15), (45, 12), (45, 38), (25, 41)]), "parchemin", "plat", base=2)
    t.peindre(rect(23, 14, 24, 42), "parchemin", "plat", base=0)
    # schéma des orbites, imprimé
    for r in (3, 5, 7):
        t.poser(anneau(34, 24, r, 1) - {(34, 24)}, "B")
    t.poser({(34, 24), (33, 24), (34, 23)}, "Y")
    for y in range(18, 36, 3):
        t.poser(rect(7, y, 19, y), "B")
    # notes manuscrites, en rouge, dans les marges
    for y in range(17, 37, 2):
        t.poser(trait(4, y, 6, y + 1, 1), "R")
        t.poser(trait(42, y, 44, y - 1, 1), "R")
    t.poser(trait(27, 34, 41, 34, 1) | trait(27, 36, 37, 36, 1), "R")
    t.peindre(poly([(2, 38), (23, 41), (23, 43), (2, 40)]) | poly([(25, 41), (46, 38), (46, 40), (25, 43)]), "bois", "plat", base=1)
    t.contour()
    return t


def nez_laiton():
    """Tycho Brahe (astro.tycho/prague) : sa prothèse de nez, en laiton d'après l'analyse de 2010."""
    t = Toile(48, 48)
    # vu de profil : l'arête qui descend, le bout arrondi, l'aile de la narine
    nez = poly([(12, 4), (19, 4), (31, 28), (36, 34), (34, 39), (26, 40), (19, 38), (14, 33), (17, 27)])
    t.peindre(nez, "or", "sphere", base=1)
    t.peindre(ellipse(22, 34, 4, 3), "or", "plat", base=1)
    t.peindre(ellipse(29, 38, 4, 1.4), "or", "plat", base=0)
    t.peindre(trait(15, 6, 28, 30, 1), "or", "plat", base=3)
    t.contour()
    return t


def trois_etoiles():
    """Couleur et température (astro.etoiles/fusion) : étoile bleue, plus de 10 000 °C ; le Soleil, jaune-blanc ; une rouge, vers 3 000 °C."""
    t = Toile(48, 48)
    t.peindre(rect(0, 0, 47, 47), "nuit", "plat", base=0)
    for (cx, cy, r, fam, base) in ((10, 14, 6, "bleu", 3), (25, 31, 9, "or", 3), (39, 13, 5, "rouge", 2)):
        t.peindre(disque(cx, cy, r + 1.5), fam, "plat", base=max(0, base - 2))
        t.peindre(disque(cx, cy, r), fam, "sphere", base=base)
    for x, y in ((4, 40), (42, 38), (20, 6), (33, 44), (45, 26)):
        t.poser({(x, y)}, "l")
    return t


def ceres():
    """Cérès (astro.pluton/ceres) : petit astre rond et cratérisé, premier objet connu de la ceinture d'astéroïdes."""
    t = Toile(48, 48)
    t.peindre(rect(0, 0, 47, 47), "nuit", "plat", base=0)
    t.peindre(disque(24, 24, 15), "gris", "sphere", base=2)
    for cx, cy, r in ((19, 18, 3), (28, 27, 4), (21, 30, 2), (30, 17, 2)):
        t.peindre(anneau(cx, cy, r, 1), "gris", "plat", base=1)
    t.poser({(26, 21), (27, 21)}, "w")
    for x, y in ((4, 6), (41, 40), (8, 42), (43, 8), (6, 26)):
        t.poser({(x, y)}, "g")
    return t


def pluton_charon():
    """Pluton et Charon (astro.pluton/pluton) : la planète naine, son cœur clair, et sa grande lune."""
    t = Toile(48, 48)
    t.peindre(rect(0, 0, 47, 47), "nuit", "plat", base=0)
    t.peindre(disque(19, 27, 14), "orange", "sphere", base=1)
    t.peindre(ellipse(22, 31, 6, 5) & disque(19, 27, 14), "parchemin", "sphere", base=2)
    t.peindre(disque(38, 11, 6), "gris", "sphere", base=2)
    t.peindre(ellipse(38, 7, 3, 1.4), "rouge", "plat", base=0)
    for x, y in ((5, 5), (44, 42), (30, 44), (26, 6)):
        t.poser({(x, y)}, "l")
    return t


DESSINS = {"mc-globe": globe, "mc-astrolabe": astrolabe, "mc-roues-maya": roues_maya, "mc-livre-annote": livre_annote,
           "mc-nez-laiton": nez_laiton, "mc-trois-etoiles": trois_etoiles, "mc-ceres": ceres, "mc-pluton-charon": pluton_charon}
COPIES = {"mc-tablette-mulapin": ("alchimie", "chim-tablette")}
ILLUS = {
    ("astro.babylone", "mulapin"): ("mc-tablette-mulapin", 0),
    ("astro.mesurer", "ronde"): ("mc-globe", 0),
    ("astro.ptolemee", "transmission"): ("mc-astrolabe", 0),
    ("astro.maya", "calendriers"): ("mc-roues-maya", 0),
    ("astro.copernic", "posterite"): ("mc-livre-annote", 0),
    ("astro.tycho", "prague"): ("mc-nez-laiton", 1),
    ("astro.etoiles", "fusion"): ("mc-trois-etoiles", 1),
    ("astro.pluton", "ceres"): ("mc-ceres", 0),
    ("astro.pluton", "pluton"): ("mc-pluton-charon", 1),
}

if __name__ == "__main__":
    executer("cosmos", DESSINS, ILLUS, COPIES)
