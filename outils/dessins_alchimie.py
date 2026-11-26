"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack Alchimie. Mode d'emploi : outils/dessins_lecons.py."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, anneau, bande, courbe, disque, ellipse, poly, rect, trait  # noqa: E402
from dessins_ile import _flammes  # noqa: E402
from dessins_lecons import executer  # noqa: E402


def cuivre_natif():
    """Cuivre natif (chim.metaux/cuivre) : une pépite ramifiée martelée à froid, et des perles de cuivre."""
    t = Toile(48, 48)
    pepite = set()
    for a, b, r in (((8, 30), (22, 22), 3.4), ((22, 22), (30, 12), 2.8), ((22, 22), (36, 26), 3), ((14, 27), (12, 18), 2.2), ((30, 24), (34, 34), 2.2)):
        pepite |= bande(a, b, r) | disque(b[0], b[1], r)
    t.peindre(pepite, "cuivre", "sphere", base=1)
    t.peindre({p for p in pepite if (p[0] * 5 + p[1] * 3) % 11 == 0}, "vert", "plat", base=1)
    for i, x in enumerate(range(9, 42, 7)):
        y = 41 + (1 if i % 2 else 0)
        t.peindre(disque(x + 0.5, y + 0.5, 2.8), "cuivre", "sphere", base=2)
        t.poser({(x, y)}, "D")
    t.poser(courbe([(4, 41), (9, 42), (16, 43), (23, 42), (30, 43), (37, 42), (44, 41)], 1) - set(t.px), "A")
    t.contour()
    return t


def livre_brule():
    """Bâle, 1527 (chim.paracelse/bale) : Paracelse brûle le Canon d'Avicenne sur la place du marché."""
    t = Toile(48, 48)
    _flammes(t, 24, 30, 26, 12)
    livre = poly([(6, 32), (24, 36), (42, 32), (42, 40), (24, 44), (6, 40)])
    t.peindre(livre, "parchemin", "biseau", base=2)
    t.peindre(trait(24, 36, 24, 44, 1), "parchemin", "plat", base=0)
    for y in (37, 39):
        t.peindre(trait(9, y - 1, 21, y + 2, 1) | trait(27, y + 2, 39, y - 1, 1), "parchemin", "plat", base=1)
    t.peindre(poly([(4, 41), (24, 45), (44, 41), (44, 43), (24, 47), (4, 43)]), "rouge", "biseau", base=1)
    t.contour()
    return t


def ouroboros():
    """Cléopâtre l'alchimiste (chim.alexandrie/zosime) : l'ouroboros, le serpent qui se mord la queue."""
    t = Toile(48, 48)
    corps = anneau(24, 24, 18, 6)
    t.peindre(corps, "vert", "sphere", base=2)
    t.peindre({p for p in corps if (p[0] - 24) ** 2 + (p[1] - 24) ** 2 > 18 ** 2 * 0.9 and p[1] > 26}, "vert", "plat", base=1)
    # écailles
    for ang in range(0, 360, 20):
        x, y = 24 + 15 * math.cos(math.radians(ang)), 24 + 15 * math.sin(math.radians(ang))
        t.poser({(int(x), int(y))}, "2")
    # tête qui mord la queue, en haut
    tete = ellipse(30, 7, 6, 4.5)
    t.peindre(tete, "vert", "biseau", base=2)
    t.peindre(poly([(19, 6), (24, 3), (25, 10)]), "vert", "plat", base=1)
    t.contour()
    t.poser({(31, 5)}, "y")
    t.poser({(32, 5)}, "k")
    t.poser(trait(25, 8, 35, 9, 1), "k")
    return t


def khol():
    """Al-kuḥl (chim.jabir/mots) : le pot de khôl et son bâtonnet, la poudre noire tirée de la stibine."""
    t = Toile(48, 48)
    pot = ellipse(22, 33, 12, 11) | rect(17, 18, 27, 24)
    t.peindre(pot, "bleu", "sphere", base=2)
    t.peindre(rect(15, 18, 29, 20), "or", "biseau", base=1)
    t.peindre(ellipse(22, 33, 12, 1.4), "or", "plat", base=2)
    t.peindre(bande((24, 19), (36, 3), 1.2) | disque(36.5, 3, 1.8), "or", "plat", base=2)
    t.peindre(ellipse(40, 41, 6, 3), "gris", "sphere", base=0, maxi=1)
    t.contour()
    return t


def armoise():
    """Armoise annuelle (chim.chine/gehong) : feuilles finement découpées, épis de petites fleurs jaunes."""
    t = Toile(48, 48)
    t.peindre(trait(24, 47, 24, 6, 1) | trait(25, 47, 25, 8, 1), "vert", "plat", base=0)
    for i, y in enumerate(range(12, 44, 5)):
        cote = 1 if i % 2 else -1
        n = 9 - abs(i - 3)
        tige = trait(24, y, 24 + cote * n * 1.4, y - 4, 1)
        t.peindre(tige, "vert", "plat", base=1)
        for k in range(1, n):
            x = 24 + cote * k * 1.4
            t.peindre(trait(x, y - k * 4 / n, x + cote, y - k * 4 / n - 3, 1) | trait(x, y - k * 4 / n, x + cote * 2, y - k * 4 / n + 1, 1), "vert", "plat", base=2)
    for x, y in ((24, 5), (22, 7), (27, 8), (18, 9), (31, 11), (15, 14), (34, 16)):
        t.peindre(disque(x + 0.5, y + 0.5, 1.2), "or", "plat", base=2)
    t.contour()
    return t


def treuil_mine():
    """De re metallica (chim.paracelse/mines) : treuil au-dessus d'un puits de mine, seau de minerai."""
    t = Toile(48, 48)
    t.peindre(rect(0, 36, 47, 47), "bois", "plat", base=1)
    t.peindre(rect(18, 36, 29, 47), "gris", "plat", base=0)
    for x in (12, 35):
        t.peindre(rect(x - 1, 12, x + 1, 37), "bois", "cyl_v", base=2)
    t.peindre(rect(10, 14, 37, 17), "bois", "cyl_h", base=3)
    for ang in range(0, 360, 90):
        x, y = 6 + 5 * math.cos(math.radians(ang)), 15.5 + 5 * math.sin(math.radians(ang))
        t.peindre(trait(10, 15, x, y, 1), "bois", "plat", base=1)
    t.peindre(anneau(6, 15.5, 5, 1.2), "bois", "plat", base=2)
    t.peindre(trait(23, 18, 23, 34, 1), "parchemin", "plat", base=1)
    seau = poly([(19, 34), (28, 34), (27, 42), (20, 42)])
    t.peindre(seau, "bois", "biseau", base=2)
    t.peindre(ellipse(23.5, 33.5, 4, 1.5), "cuivre", "plat", base=0)
    t.contour()
    return t


def rouleau_papyrus():
    """Papyrus de Leyde (chim.alexandrie/papyrus) : un rouleau déroulé, des recettes en colonnes."""
    t = Toile(48, 48)
    feuille = rect(9, 10, 41, 38)
    t.peindre(feuille, "parchemin", "plat", base=2)
    t.peindre({p for p in feuille if p[0] % 4 == 0}, "parchemin", "plat", base=1)
    for col in (12, 27):
        for y in range(13, 36, 3):
            t.poser(rect(col, y, col + 10 - (y % 5), y), "B")
    t.peindre(rect(4, 8, 9, 40), "parchemin", "cyl_h", base=1)
    t.peindre(rect(41, 8, 45, 40), "parchemin", "cyl_h", base=1)
    t.contour()
    return t


DESSINS = {"mc-cuivre-natif": cuivre_natif, "mc-livre-brule": livre_brule, "mc-ouroboros": ouroboros,
           "mc-khol": khol, "mc-armoise": armoise, "mc-treuil-mine": treuil_mine, "mc-rouleau-papyrus": rouleau_papyrus}
COPIES = {"mc-balance-lavoisier": ("logique", "mc-balance"), "mc-citron-ph": ("savoir", "mc-citron")}
ILLUS = {
    ("chim.metaux", "cuivre"): ("mc-cuivre-natif", 0),
    ("chim.paracelse", "bale"): ("mc-livre-brule", 0),
    ("chim.alexandrie", "zosime"): ("mc-ouroboros", 1),
    ("chim.alexandrie", "papyrus"): ("mc-rouleau-papyrus", 0),
    ("chim.jabir", "mots"): ("mc-khol", 0),
    ("chim.chine", "gehong"): ("mc-armoise", 1),
    ("chim.paracelse", "mines"): ("mc-treuil-mine", 1),
    ("chim.lavoisier", "masse"): ("mc-balance-lavoisier", 0),
    ("chim.acides", "ph"): ("mc-citron-ph", 0),
}

if __name__ == "__main__":
    executer("alchimie", DESSINS, ILLUS, COPIES)
