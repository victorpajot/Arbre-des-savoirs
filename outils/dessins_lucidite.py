"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack Lucidité. Mode d'emploi : outils/dessins_lecons.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, anneau, ellipse, poly, rect  # noqa: E402
from dessins_lecons import executer  # noqa: E402


def foudre():
    """Wang Chong (biais.elephant/wang) : le tonnerre n'est pas la colère du Ciel, mais l'effet du feu ou de la chaleur."""
    t = Toile(48, 48)
    nuage = ellipse(15, 12, 10, 7) | ellipse(28, 9, 11, 8) | ellipse(38, 13, 8, 6) | rect(8, 12, 44, 17)
    t.peindre(nuage, "gris", "sphere", base=1, maxi=3)
    eclair = poly([(26, 17), (19, 31), (25, 31), (18, 46), (33, 26), (26, 26), (32, 17)])
    t.peindre(eclair, "or", "plat", base=3)
    t.peindre(poly([(27, 18), (22, 28), (25, 28)]), "or", "plat", base=2)
    t.contour()
    return t


def billet_law():
    """Le système de Law (biais.bulles/law) : un billet de la Banque royale, imprimé toujours plus pour suivre la fièvre."""
    t = Toile(48, 48)
    for dx, dy in ((6, 18), (3, 12)):
        feuille = rect(dx, dy, dx + 38, dy + 20)
        t.peindre(feuille, "parchemin", "plat", base=2)
        t.peindre(rect(dx + 2, dy + 2, dx + 36, dy + 18) - rect(dx + 3, dy + 3, dx + 35, dy + 17), "parchemin", "plat", base=0)
    t.peindre(anneau(11, 22, 4, 1), "bleu", "plat", base=1)
    for y in (17, 20, 23, 26):
        t.poser(rect(18, y, 36, y), "B")
    t.poser(rect(29, 28, 37, 28), "R")
    t.contour()
    return t


DESSINS = {"mc-foudre": foudre, "mc-billet-law": billet_law}
ILLUS = {
    ("biais.elephant", "wang"): ("mc-foudre", 1),
    ("biais.bulles", "law"): ("mc-billet-law", 1),
}

if __name__ == "__main__":
    executer("lucidite", DESSINS, ILLUS)
