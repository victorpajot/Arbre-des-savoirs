"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack Essaim. Mode d'emploi : outils/dessins_lecons.py."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, courbe, poly  # noqa: E402
from dessins_lecons import executer  # noqa: E402


def spirale_tombe():
    """La tombe de Jacques Bernoulli (coll.grandsnombres/theoreme) : il y voulait une spirale logarithmique, « Eadem mutata resurgo »."""
    t = Toile(48, 48)
    pierre = poly([(6, 46), (6, 12), (12, 4), (36, 4), (42, 12), (42, 46)])
    t.peindre(pierre, "gris", "biseau", base=2)
    pts = []
    for i in range(160):
        a = i * 0.09
        r = 0.9 * math.exp(0.19 * a)
        if r > 15:
            break
        pts.append((24 + r * math.cos(a), 24 + r * math.sin(a)))
    t.peindre(courbe(pts, 1), "gris", "plat", base=0)
    t.contour()
    return t


DESSINS = {"mc-spirale-tombe": spirale_tombe}
ILLUS = {("coll.grandsnombres", "theoreme"): ("mc-spirale-tombe", 1)}

if __name__ == "__main__":
    executer("essaim", DESSINS, ILLUS)
