"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack Empathie. Mode d'emploi : outils/dessins_lecons.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, courbe, ellipse, poly, rect, trait  # noqa: E402
from dessins_ile import _flammes  # noqa: E402
from dessins_lecons import executer  # noqa: E402


def trois_feux():
    """Les trois feux à éteindre (psy.bouddha/feux) : le désir, la haine, l'ignorance."""
    t = Toile(48, 48)
    for cx, h in ((9, 22), (24, 30), (39, 22)):
        _flammes(t, cx, 40, h, 6.5)
    t.peindre(rect(1, 40, 46, 44), "gris", "biseau", base=2)
    t.contour()
    return t


def rat_blanc():
    """Le petit Albert (psy.pavlov/behaviorisme) : le rat blanc qu'on lui présentait, et qui finit par le faire pleurer."""
    t = Toile(48, 48)
    corps = ellipse(22, 30, 13, 8)
    tete = poly([(32, 25), (44, 30), (32, 35)])
    t.peindre(courbe([(9, 32), (5, 36), (3, 41), (8, 44), (14, 43)], 1), "rose", "plat", base=1)
    t.peindre(corps | tete | ellipse(33, 30, 4, 5), "gris", "sphere", base=4)
    t.peindre(ellipse(32, 23.5, 3, 3), "rose", "plat", base=1)
    for x in (14, 18, 27, 31):
        t.peindre(rect(x, 37, x + 1, 39), "rose", "plat", base=1)
    t.poser({(37, 28)}, "r")
    t.poser({(44, 30)}, "F")
    t.contour()
    return t


def deux_verres():
    """La conservation (psy.developpement/piaget) : la même eau versée d'un verre large dans un verre étroit et haut."""
    t = Toile(48, 48)
    large = rect(4, 26, 21, 42)
    etroit = rect(30, 8, 39, 42)
    t.peindre(large | etroit, "cyan", "cyl_v", base=2)
    t.peindre(rect(5, 33, 20, 41), "bleu", "cyl_v", base=3)
    t.peindre(rect(31, 14, 38, 41), "bleu", "cyl_v", base=3)
    t.peindre(trait(23, 30, 28, 30, 1) | trait(27, 28, 28, 30, 1) | trait(27, 32, 28, 30, 1), "gris", "plat", base=1)
    t.contour()
    return t


DESSINS = {"mc-trois-feux": trois_feux, "mc-rat-blanc": rat_blanc, "mc-deux-verres": deux_verres}
COPIES = {"mc-livres-freud": ("alchimie", "mc-livre-brule")}
ILLUS = {
    ("psy.bouddha", "feux"): ("mc-trois-feux", 1),
    ("psy.pavlov", "behaviorisme"): ("mc-rat-blanc", 1),
    ("psy.developpement", "piaget"): ("mc-deux-verres", 1),
    ("psy.freud", "ca"): ("mc-livres-freud", 1),
}

if __name__ == "__main__":
    executer("empathie", DESSINS, ILLUS, COPIES)
