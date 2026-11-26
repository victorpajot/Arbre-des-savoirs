"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack Musique. Mode d'emploi : outils/dessins_lecons.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, anneau, bande, disque, ellipse, poly, rect, trait  # noqa: E402
from dessins_lecons import executer  # noqa: E402


def flutes_bambou():
    """Ling Lun, selon la légende (mus.cloches/legende) : des flûtes taillées dans le bambou."""
    t = Toile(48, 48)
    for i, (x, h) in enumerate(((8, 36), (17, 30), (26, 24), (35, 18))):
        tube = rect(x, 44 - h, x + 5, 44)
        t.peindre(tube, "vert", "cyl_v", base=2)
        for y in range(44 - h + 6, 44, 9):
            t.peindre(rect(x, y, x + 5, y), "vert", "plat", base=0)
        for y in range(44 - h + 3, 40, 5):
            t.poser({(x + 2, y), (x + 3, y)}, "2")
        t.peindre(ellipse(x + 3, 44 - h, 3, 1), "vert", "plat", base=0)
    t.contour()
    return t


def oud():
    """Al-Farabi (mus.boece/farabi) : le luth oud, caisse bombée en poire, chevillier renversé."""
    t = Toile(48, 48)
    caisse = ellipse(20, 30, 14, 13) | poly([(26, 20), (34, 12), (37, 15), (30, 24)])
    t.peindre(caisse, "bois", "sphere", base=2)
    for k in range(-3, 4):
        t.poser(trait(9 + k * 3, 38 - k, 30 + k, 18 + k * 2, 1) & ellipse(20, 30, 13, 12), "B")
    t.peindre(ellipse(20, 30, 9, 8), "parchemin", "plat", base=1)
    t.peindre(disque(18, 28, 2.6), "bois", "plat", base=0)
    t.peindre(bande((33, 13), (41, 6), 2) | bande((41, 6), (44, 11), 1.6), "bois", "plat", base=1)
    t.peindre(trait(12, 38, 39, 10, 1), "parchemin", "plat", base=2)
    t.peindre(rect(10, 37, 15, 39), "bois", "plat", base=0)
    t.contour()
    return t


def caractere_note():
    """Attaingnant (mus.imprimerie/attaingnant) : chaque note fondue sur son petit morceau de portée, en un seul caractère."""
    t = Toile(48, 48)
    for i, (x, y, hauteur) in enumerate(((5, 14, 2), (19, 18, 0), (33, 12, 4))):
        bloc = rect(x, y, x + 10, y + 22)
        t.peindre(bloc, "gris", "cyl_h", base=2)
        for k in range(5):
            t.peindre(rect(x + 1, y + 4 + k * 3, x + 9, y + 4 + k * 3), "gris", "plat", base=0)
        ny = y + 4 + hauteur * 3
        t.peindre(ellipse(x + 4.5, ny + 0.5, 2.2, 1.6), "gris", "plat", base=0)
        t.peindre(rect(x + 6, ny - 8, x + 6, ny), "gris", "plat", base=0)
    t.contour()
    return t


def metronome():
    """Le métronome de Maelzel (mus.mesure/pendule) : un pendule inversé à masse mobile, dans une pyramide de bois."""
    t = Toile(48, 48)
    boite = poly([(10, 46), (18, 4), (30, 4), (38, 46)])
    t.peindre(boite, "bois", "biseau", base=2)
    t.peindre(poly([(16, 40), (21, 10), (27, 10), (32, 40)]), "parchemin", "plat", base=2)
    for y in range(13, 38, 4):
        t.poser({(25, y), (26, y)}, "A")
    t.peindre(trait(24, 40, 30, 9, 1), "gris", "plat", base=1)
    t.peindre(poly([(26, 19), (31, 20), (30, 24), (25, 23)]), "gris", "biseau", base=3)
    t.peindre(rect(8, 44, 40, 46), "bois", "biseau", base=1)
    t.contour()
    return t


def disque_78():
    """Pierre Schaeffer, 1948 (mus.electronique/concrete) : la musique concrète faite d'abord avec des disques."""
    t = Toile(48, 48)
    t.peindre(disque(24, 24, 21), "gris", "plat", base=0)
    for r in (18, 15, 12):
        t.peindre(anneau(24, 24, r, 1), "gris", "plat", base=1)
    t.peindre(trait(10, 14, 16, 9, 1), "gris", "plat", base=3)
    t.peindre(disque(24, 24, 7), "rouge", "plat", base=2)
    t.peindre(disque(24, 24, 1.2), "parchemin", "plat", base=2)
    t.contour()
    return t


def chauve_souris():
    """Les ultrasons (mus.perception/plage) : au-dessus de 20 000 Hz, ce que les chauves-souris entendent."""
    t = Toile(48, 48)
    corps = ellipse(24, 26, 4.5, 7)
    tete = disque(24, 17, 4) | poly([(20, 15), (21, 9), (23, 14)]) | poly([(28, 15), (27, 9), (25, 14)])
    aile_g = poly([(21, 22), (12, 16), (2, 20), (5, 24), (9, 23), (11, 28), (15, 26), (17, 31), (21, 29)])
    aile_d = {(47 - x, y) for (x, y) in aile_g}
    t.peindre(aile_g | aile_d, "violet", "biseau", base=1)
    t.peindre(corps | tete, "bois", "sphere", base=1)
    t.contour()
    t.poser({(22, 17), (26, 17)}, "r")
    return t


DESSINS = {"mc-flutes-bambou": flutes_bambou, "mc-oud": oud, "mc-caractere-note": caractere_note,
           "mc-metronome": metronome, "mc-disque-78": disque_78, "mc-chauve-souris": chauve_souris}
COPIES = {"mc-tablette-ougarit": ("alchimie", "chim-tablette")}
ILLUS = {
    ("mus.ecriture", "nikkal"): ("mc-tablette-ougarit", 0),
    ("mus.cloches", "legende"): ("mc-flutes-bambou", 0),
    ("mus.boece", "farabi"): ("mc-oud", 1),
    ("mus.imprimerie", "attaingnant"): ("mc-caractere-note", 0),
    ("mus.mesure", "pendule"): ("mc-metronome", 1),
    ("mus.electronique", "concrete"): ("mc-disque-78", 1),
    ("mus.perception", "plage"): ("mc-chauve-souris", 0),
}

if __name__ == "__main__":
    executer("musique", DESSINS, ILLUS, COPIES)
