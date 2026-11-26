"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack Savoir. Mode d'emploi : outils/dessins_lecons.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, courbe, disque, ellipse, poly, rect, trait  # noqa: E402
from dessins_lecons import executer  # noqa: E402


def pot_miel():
    """Le miel des médecins égyptiens (sci.egypte/ebers) : une jarre de miel, une cuillère qui coule."""
    t = Toile(48, 48)
    jarre = ellipse(22, 32, 14, 13) | rect(15, 14, 29, 22)
    t.peindre(jarre, "parchemin", "sphere", base=1)
    t.peindre(rect(13, 13, 31, 16), "parchemin", "biseau", base=0)
    t.peindre(poly([(15, 17), (29, 17), (29, 21), (26, 24), (22, 21), (18, 25), (15, 21)]), "or", "plat", base=2)
    t.peindre(trait(30, 4, 26, 15, 2), "bois", "plat", base=2)
    t.peindre(courbe([(25, 16), (24, 20), (24, 25)], 1), "or", "plat", base=1)
    t.contour()
    return t


def aiguilles():
    """Le Lingshu (sci.chine/neijing) : les aiguilles d'acupuncture, longues et fines, à manche enroulé."""
    t = Toile(48, 48)
    for i, x in enumerate((10, 18, 26, 34)):
        lg = 34 - i * 3
        t.peindre(trait(x + 4, 8, x - 2, 8 + lg, 1), "gris", "plat", base=4)
        t.peindre(trait(x + 4, 8, x + 6, 2, 2), "or", "plat", base=1)
        t.poser({(x + 5, 3), (x + 5, 5)}, "4")
    t.peindre(rect(2, 42, 45, 45), "rouge", "biseau", base=1)
    t.contour()
    return t


def vache():
    """Blossom (sci.vaccins/jenner) : la vache dont la vaccine a servi à Jenner en 1796."""
    t = Toile(48, 48)
    corps = rect(8, 18, 34, 32) | ellipse(10, 25, 4, 7) | ellipse(32, 25, 4, 7)
    tete = poly([(33, 14), (42, 15), (46, 24), (43, 27), (37, 26), (33, 22)])
    pattes = set()
    for x0 in (9, 14, 27, 32):
        pattes |= rect(x0, 32, x0 + 2, 43)
    t.peindre(pattes, "parchemin", "cyl_v", base=2)
    t.peindre(corps | tete, "parchemin", "sphere", base=2)
    for cx, cy, r in ((14, 22, 4), (24, 27, 3.5), (28, 20, 3), (38, 17, 2.4)):
        t.peindre(disque(cx, cy, r) & (corps | tete), "bois", "plat", base=1)
    t.peindre(ellipse(44, 25, 2.6, 2.2), "rose", "plat", base=1)
    t.peindre(trait(35, 14, 33, 10, 1) | trait(40, 14, 42, 10, 1), "ivoire", "plat")
    t.peindre(ellipse(22, 33.5, 3, 2), "rose", "sphere", base=1)
    t.peindre(courbe([(7, 20), (4, 26), (4, 33)], 1), "parchemin", "plat", base=1)
    for x0 in (9, 14, 27, 32):
        t.poser(rect(x0, 43, x0 + 2, 44), "n")
    t.contour()
    t.poser({(40, 18)}, "k")
    return t


DESSINS = {"mc-pot-miel": pot_miel, "mc-aiguilles": aiguilles, "mc-vache": vache}
ILLUS = {
    ("sci.egypte", "ebers"): ("mc-pot-miel", 1),
    ("sci.chine", "neijing"): ("mc-aiguilles", 1),
    ("sci.vaccins", "jenner"): ("mc-vache", 1),
}

if __name__ == "__main__":
    executer("savoir", DESSINS, ILLUS)
