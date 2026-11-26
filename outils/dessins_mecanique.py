"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack Mécanique. Mode d'emploi : outils/dessins_lecons.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, courbe, disque, ellipse, poly, rect, trait  # noqa: E402
from dessins_ile import _flammes  # noqa: E402
from dessins_lecons import executer  # noqa: E402


def quatre_elements():
    """Aristote (phys.aristote/elements) : la terre, l'eau, l'air et le feu, chacun vers son lieu naturel."""
    t = Toile(48, 48)
    t.peindre(rect(4, 34, 21, 44), "bois", "biseau", base=2)
    t.peindre(rect(4, 34, 21, 36), "vert", "plat", base=2)
    goutte = poly([(36, 25), (31, 35), (31, 39), (34, 43), (38, 43), (41, 39), (41, 35)])
    t.peindre(goutte, "bleu", "sphere", base=2)
    for cx, cy in ((9, 11), (15, 9), (20, 12)):
        t.peindre(ellipse(cx, cy, 5, 3.4), "cyan", "plat", base=2)
    t.peindre(courbe([(3, 18), (9, 16), (15, 18), (21, 16)], 1), "cyan", "plat", base=0)
    _flammes(t, 36, 21, 18, 8)
    t.contour()
    return t


def eolipyle():
    """L'éolipyle de Héron (phys.alexandrie/heron) : une boule qui tourne, poussée par la vapeur de deux tuyères."""
    t = Toile(48, 48)
    t.peindre(ellipse(24, 40, 14, 5), "cuivre", "sphere", base=1)
    t.peindre(rect(10, 40, 38, 44), "cuivre", "cyl_h", base=1)
    for x in (14, 33):
        t.peindre(rect(x, 15, x + 1, 37), "cuivre", "plat", base=0)
    t.peindre(disque(24, 18, 8), "cuivre", "sphere", base=2)
    t.peindre(rect(13, 17, 15, 19) | rect(33, 17, 35, 19), "cuivre", "plat", base=1)
    t.peindre(courbe([(30, 12), (34, 10), (35, 6)], 2) | courbe([(18, 24), (14, 26), (13, 30)], 2), "cuivre", "plat", base=1)
    t.contour()
    for x, y in ((37, 4), (39, 2), (41, 5), (11, 31), (9, 33), (12, 34)):
        t.poser({(x, y)}, "l")
    return t


def deux_poids():
    """Philopon (phys.impetus/philopon) : deux poids lâchés de la même hauteur, l'un bien plus lourd ; la différence de temps est très petite."""
    t = Toile(48, 48)
    t.peindre(rect(2, 43, 45, 46), "bois", "biseau", base=2)
    t.peindre(rect(4, 2, 44, 4), "bois", "biseau", base=1)
    t.peindre(disque(14, 30, 7), "gris", "sphere", base=1)
    t.peindre(disque(34, 32, 3.5), "gris", "sphere", base=3)
    t.contour()
    return t


DESSINS = {"mc-quatre-elements": quatre_elements, "mc-eolipyle": eolipyle, "mc-deux-poids": deux_poids}
COPIES = {"mc-sphere-cylindre-tombe": ("logique", "mc-sphere-cylindre"), "mc-balance-mohiste": ("logique", "mc-balance")}
ILLUS = {
    ("phys.aristote", "elements"): ("mc-quatre-elements", 0),
    ("phys.alexandrie", "heron"): ("mc-eolipyle", 1),
    ("phys.impetus", "philopon"): ("mc-deux-poids", 2),
    ("phys.archimede", "syracuse"): ("mc-sphere-cylindre-tombe", 2),
    ("phys.mohistes", "balance"): ("mc-balance-mohiste", 1),
}

if __name__ == "__main__":
    executer("mecanique", DESSINS, ILLUS, COPIES)
