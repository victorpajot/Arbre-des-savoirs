"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack Essaim. Mode d'emploi : outils/dessins_lecons.py."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, courbe, disque, ellipse, poly, trait  # noqa: E402
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
    """La peinture rupestre de la Cueva de la Araña (coll.ruche/miel) : sur la paroi, un humain peint à l'ocre grimpe
    à des lianes pendues, un sac à la main, et plonge le bras dans le nid ; les abeilles tournent autour."""
    t = Toile(48, 48)
    paroi = poly([(2, 6), (8, 2), (22, 3), (34, 1), (45, 5), (46, 20), (44, 34), (46, 45), (30, 46), (14, 45), (2, 46), (3, 30), (1, 18)])
    t.peindre(paroi, "parchemin", "biseau", base=1)
    for (x, y) in [(9, 9), (15, 38), (38, 40), (41, 26), (6, 33), (27, 42), (12, 21)]:  # grain de la roche
        t.poser({(x, y), (x + 1, y)}, "A")
    nid = ellipse(33, 9, 4, 3)
    t.peindre(nid, "bois", "plat", base=0)
    # les lianes : trois cordes pendues sous le nid, peintes elles aussi
    for x0, x1 in ((22, 20), (25, 24), (28, 29)):
        t.poser(trait(x0, 4, x1, 45), "D")
    ocre = "R"
    t.poser(disque(25, 16, 2.8), ocre)                      # tête
    t.poser(trait(25, 18, 24, 29, 3), ocre)                 # corps
    t.poser(trait(26, 21, 31, 12, 2), ocre)                 # bras tendu vers le nid
    t.poser(trait(23, 22, 18, 26, 2), ocre)                 # bras qui tient le sac
    t.poser(trait(24, 29, 20, 37, 2), ocre)                 # jambes accrochées aux lianes
    t.poser(trait(25, 29, 29, 36, 2), ocre)
    sac = ellipse(16, 30, 3, 3.5)
    t.peindre(sac, "rouge", "plat", base=1)
    for (x, y) in [(39, 4), (40, 11), (36, 15), (28, 4), (42, 17), (32, 18)]:  # les abeilles : rayées, une aile
        t.poser({(x, y), (x + 2, y)}, "k")
        t.poser({(x + 1, y)}, "y")
        t.poser({(x + 1, y - 1)}, "l")
    t.contour()
    return t


DESSINS = {"mc-spirale-tombe": spirale_tombe, "mc-recolte-miel": recolte_miel}
ILLUS = {("coll.grandsnombres", "theoreme"): ("mc-spirale-tombe", 1), ("coll.ruche", "miel"): ("mc-recolte-miel", 0)}

if __name__ == "__main__":
    executer("essaim", DESSINS, ILLUS)
