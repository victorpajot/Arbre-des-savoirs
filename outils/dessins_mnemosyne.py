"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack Mnémosyne. Mode d'emploi : outils/dessins_lecons.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, poly, rect  # noqa: E402
from dessins_eloquence import ecrire  # noqa: E402
from dessins_lecons import executer  # noqa: E402


def marbre_paros():
    """Le marbre de Paros (mnemo.simonide/poete) : une chronologie gravée, qui compte les années à rebours."""
    t = Toile(48, 48)
    bloc = poly([(5, 8), (18, 4), (34, 6), (43, 3), (44, 40), (30, 44), (14, 42), (4, 45)])
    t.peindre(bloc, "gris", "biseau", base=4)
    for y in range(10, 41, 3):
        for x in range(8, 41, 2):
            if (x, y) in bloc and (x * 3 + y) % 7:
                t.poser({(x, y)}, "g")
    t.contour()
    return t


def syllabes():
    """Ebbinghaus (mnemo.oubli/ebbinghaus) : des syllabes sans sens, comme WID ou ZOF, sur des cartes."""
    t = Toile(48, 48)
    for (x, y, mot) in ((5, 10, "WID"), (22, 26, "ZOF")):
        t.peindre(rect(x, y, x + 19, y + 11), "parchemin", "biseau", base=2)
        t.poser(ecrire(mot, x + 4, y + 3), "k")
    t.contour()
    return t


DESSINS = {"mc-marbre-paros": marbre_paros, "mc-syllabes": syllabes}
ILLUS = {
    ("mnemo.simonide", "poete"): ("mc-marbre-paros", 1),
    ("mnemo.oubli", "ebbinghaus"): ("mc-syllabes", 0),
}

if __name__ == "__main__":
    executer("mnemosyne", DESSINS, ILLUS)
