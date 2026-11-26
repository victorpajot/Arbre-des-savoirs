"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack Logique. Mode d'emploi : outils/dessins_lecons.py."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, bande, courbe, disque, ellipse, poly, rect, trait  # noqa: E402
from dessins_lecons import executer  # noqa: E402


def os_lebombo():
    """L'os de Lebombo (math.origines/lebombo) : un péroné de babouin couvert d'entailles, 42 000 ans."""
    t = Toile(48, 48)
    os_ = bande((5, 34), (43, 14), 3) | ellipse(5, 34.5, 3.6, 4) | ellipse(43, 13.5, 3.6, 4)
    t.peindre(os_, "parchemin", "cyl_h", base=2)
    for i in range(29):
        x = 9 + i * 1.15
        y = 32 - i * 0.6
        t.poser(trait(x, y - 2, x + 1, y + 2, 1) & os_, "B")
    t.contour()
    return t


def pyramide_tronquee():
    """Papyrus de Moscou, problème 14 (math.egypte/volumes) : pyramide tronquée, 4 de côté en bas, 2 en haut, 6 de haut."""
    t = Toile(48, 48)
    avant = poly([(8, 40), (32, 40), (28, 14), (16, 14)])
    cote = poly([(32, 40), (42, 33), (35, 10), (28, 14)])
    haut = poly([(16, 14), (28, 14), (35, 10), (23, 10)])
    t.peindre(avant, "parchemin", "plat", base=1)
    t.peindre(cote, "parchemin", "plat", base=0)
    t.peindre(haut, "parchemin", "plat", base=2)
    for y in range(18, 40, 4):
        t.poser({(x, y) for x in range(6, 44)} & (avant | cote), "A" if y % 8 else "V")
    t.contour()
    return t


def polygone_cercle():
    """Liu Hui (math.chine/liu-hui) : un polygone inscrit dans le cercle, dont on double les côtés pour approcher π."""
    t = Toile(48, 48)
    t.peindre(disque(24, 24, 21), "parchemin", "plat", base=2)
    pts = [(24 + 20 * math.cos(2 * math.pi * k / 12), 24 + 20 * math.sin(2 * math.pi * k / 12)) for k in range(12)]
    pts6 = [(24 + 20 * math.cos(2 * math.pi * k / 6), 24 + 20 * math.sin(2 * math.pi * k / 6)) for k in range(6)]
    t.peindre(poly(pts6), "cyan", "plat", base=1)
    t.peindre(courbe(pts6 + [pts6[0]], 1), "bleu", "plat", base=1)
    t.peindre(courbe(pts + [pts[0]], 1), "rouge", "plat", base=1)
    t.contour()
    return t


def coq_noir():
    """Le coq noir de Napier (math.logarithmes/napier) : couvert de suie, il démasque le voleur aux mains propres."""
    t = Toile(48, 48)
    queue = poly([(6, 12), (14, 18), (18, 26), (10, 30), (4, 22)])
    corps = ellipse(22, 28, 11, 9)
    cou = poly([(26, 22), (30, 10), (36, 10), (35, 22), (30, 28)])
    tete = ellipse(34, 10, 5, 4.5)
    t.peindre(queue | corps | cou | tete, "gris", "sphere", base=0, maxi=1)
    t.peindre(courbe([(6, 12), (10, 8), (16, 10)], 2) | courbe([(4, 22), (2, 16), (5, 12)], 2), "gris", "plat", base=1)
    t.peindre(poly([(30, 6), (32, 2), (34, 5), (36, 1), (38, 5), (39, 7)]), "rouge", "plat", base=2)
    t.peindre(ellipse(36, 17, 1.6, 2.6), "rouge", "plat", base=2)
    t.peindre(poly([(38, 10), (44, 12), (38, 13)]), "or", "plat", base=2)
    for x in (20, 26):
        t.peindre(rect(x, 36, x + 1, 44) | rect(x - 2, 44, x + 3, 45), "or", "plat", base=1)
    t.contour()
    t.poser({(35, 9)}, "y")
    return t


def pluie_sol():
    """« S'il pleut, le sol est mouillé » (math.logique/implication) : un nuage, la pluie, une flaque."""
    t = Toile(48, 48)
    nuage = ellipse(16, 14, 9, 6) | ellipse(27, 10, 10, 8) | ellipse(36, 15, 8, 5) | rect(10, 14, 40, 19)
    t.peindre(nuage, "gris", "sphere", base=2)
    for i, x in enumerate(range(10, 40, 5)):
        y = 23 + (i % 2) * 4
        t.peindre(trait(x, y, x - 1, y + 4, 1), "bleu", "plat", base=3)
    t.peindre(rect(2, 38, 45, 45), "bois", "biseau", base=2)
    t.peindre(ellipse(24, 39, 13, 2.2), "cyan", "plat", base=1)
    t.contour()
    return t


DESSINS = {"mc-os-lebombo": os_lebombo, "mc-pyramide-tronquee": pyramide_tronquee, "mc-polygone-cercle": polygone_cercle,
           "mc-coq-noir": coq_noir, "mc-pluie-sol": pluie_sol}
COPIES = {"mc-deux-des": ("essaim", "mc-des")}
ILLUS = {
    ("math.origines", "lebombo"): ("mc-os-lebombo", 0),
    ("math.egypte", "volumes"): ("mc-pyramide-tronquee", 1),
    ("math.chine", "liu-hui"): ("mc-polygone-cercle", 0),
    ("math.logarithmes", "napier"): ("mc-coq-noir", 1),
    ("math.logique", "implication"): ("mc-pluie-sol", 0),
    ("math.probabilites", "compter"): ("mc-deux-des", 0),
}

if __name__ == "__main__":
    executer("logique", DESSINS, ILLUS, COPIES)
