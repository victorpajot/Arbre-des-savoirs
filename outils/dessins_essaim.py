"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack Essaim. Mode d'emploi : outils/dessins_lecons.py."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, anneau, arc, courbe, disque, ellipse, poly, rect, trait  # noqa: E402
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


def recolte_miel():
    """La peinture rupestre de la Cueva de la Araña (coll.ruche/miel), d'après le relevé publié sur Wikipédia : sous une
    branche, le nid ; des lianes pendent ; un humain y grimpe, plonge le bras dans le nid et tient un panier ; de grosses
    abeilles tournent autour. Tout est peint à l'ocre sur la paroi."""
    t = Toile(48, 48)
    paroi = poly([(1, 4), (8, 1), (24, 2), (36, 1), (46, 4), (47, 22), (45, 36), (47, 46), (30, 47), (12, 46), (1, 47), (2, 30), (0, 16)])
    t.peindre(paroi, "parchemin", "biseau", base=1)
    for (x, y) in [(40, 8), (6, 26), (37, 40), (5, 38), (43, 18), (27, 44)]:  # grain de la roche
        t.poser({(x, y), (x + 1, y)}, "A")
    o = "R"
    # la branche, en haut, et ses rameaux qui pendent vers le nid
    t.poser(courbe([(4, 2), (15, 6), (28, 10)], 1), o)
    t.poser(trait(5, 3, 15, 7, 1), o)
    for x0, y0, y1 in ((14, 7, 14), (18, 8, 15), (20, 9, 14)):
        t.poser(trait(x0, y0, x0, y1, 1), o)
    # le nid sous son abri, et la corniche à gauche
    t.poser(courbe([(10, 18), (12, 15), (16, 14), (20, 15), (22, 18)], 1), o)
    t.poser(ellipse(16, 19, 4, 2.2), o)
    t.poser(trait(7, 20, 15, 23, 1), o)
    # les lianes, du nid jusqu'en bas
    t.poser(courbe([(16, 22), (15, 34), (12, 46)], 1), o)
    t.poser(courbe([(18, 22), (17, 34), (15, 46)], 1), o)
    # le grimpeur : tête, corps penché sur les lianes, un bras dans le nid, l'autre tenant le panier, jambes repliées
    t.poser(disque(25, 16, 2), o)
    t.poser(courbe([(25, 19), (24, 25), (22, 32)], 3), o)
    t.poser(trait(24, 20, 20, 20, 1), o)
    t.poser(courbe([(26, 20), (27, 24), (28, 27)], 1), o)
    t.poser(rect(28, 28, 32, 32), o)                          # le panier
    t.poser({(28, 26), (28, 27), (29, 25), (30, 25), (31, 26), (31, 27)}, o)  # son anse
    t.poser(courbe([(22, 32), (23, 35), (24, 38)], 1), o)
    t.poser(courbe([(22, 32), (20, 35), (22, 37)], 1), o)
    # les abeilles : un corps et deux ailes ouvertes
    for (x, y) in [(33, 22), (40, 22), (40, 29), (27, 35), (35, 41)]:
        t.poser({(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1), (x + 2, y + 1)}, o)
        t.poser({(x - 1, y - 1), (x - 2, y - 2), (x + 2, y - 1), (x + 3, y - 2)}, o)
    t.contour()
    return t


DESSINS = {"mc-spirale-tombe": spirale_tombe, "mc-recolte-miel": recolte_miel}
ILLUS = {("coll.grandsnombres", "theoreme"): ("mc-spirale-tombe", 1), ("coll.ruche", "miel"): ("mc-recolte-miel", 0)}

if __name__ == "__main__":
    executer("essaim", DESSINS, ILLUS)
