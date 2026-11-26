"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack Étincelle. Mode d'emploi : outils/dessins_lecons.py."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, anneau, bande, disque, ellipse, poly, rect, trait  # noqa: E402
from dessins_lecons import executer  # noqa: E402


def poisson_fer():
    """Le poisson de fer flottant (elec.boussole/mer) : une lame aimantée en forme de poisson, sur l'eau d'un bol."""
    t = Toile(48, 48)
    bol = ellipse(24, 30, 21, 13) & rect(0, 26, 47, 47)
    t.peindre(bol, "bois", "sphere", base=2)
    t.peindre(ellipse(24, 27, 21, 5), "bois", "plat", base=0)
    t.peindre(ellipse(24, 27, 19, 4), "cyan", "plat", base=1)
    poisson = poly([(10, 25), (14, 22), (30, 22), (35, 25), (30, 28), (14, 28)]) | poly([(35, 25), (40, 21), (39, 25), (40, 29)])
    t.peindre(poisson, "gris", "biseau", base=1)
    t.poser({(13, 24)}, "k")
    t.poser({(x, 25) for x in range(16, 30, 3)}, "G")
    t.contour()
    return t


def inclinaison():
    """L'instrument d'inclinaison de Gilbert (elec.gilbert/experience) : une aiguille aimantée qui pivote à la verticale et plonge."""
    t = Toile(48, 48)
    t.peindre(rect(10, 42, 38, 45), "bois", "biseau", base=2)
    t.peindre(rect(22, 34, 26, 42), "bois", "cyl_v", base=2)
    t.peindre(anneau(24, 20, 15, 2.2), "or", "sphere", base=2)
    for ang in range(0, 360, 30):
        x, y = 24 + 12 * math.cos(math.radians(ang)), 20 + 12 * math.sin(math.radians(ang))
        t.poser({(int(round(x)), int(round(y)))}, "4")
    a = math.radians(35)
    t.peindre(bande((24 - 11 * math.cos(a), 20 - 11 * math.sin(a)), (24, 20), 0.6) | bande((24, 20), (24 + 11 * math.cos(a), 20 + 11 * math.sin(a)), 1.2), "gris", "plat", base=1)
    t.peindre(bande((24, 20), (24 + 11 * math.cos(a), 20 + 11 * math.sin(a)), 1.2), "rouge", "plat", base=1)
    t.peindre(disque(24, 20, 1.4), "or", "plat", base=3)
    t.contour()
    return t


def globe_soufre():
    """Le globe de soufre d'Otto von Guericke (elec.leyde/gray) : une boule jaune sur une tige de fer, frottée à la main."""
    t = Toile(48, 48)
    t.peindre(rect(4, 40, 44, 44), "bois", "biseau", base=2)
    for x in (6, 40):
        t.peindre(rect(x, 14, x + 2, 40), "bois", "cyl_v", base=2)
    t.peindre(rect(3, 21, 45, 22), "gris", "cyl_h", base=1)
    t.peindre(trait(45, 22, 45, 29, 1) | trait(45, 29, 47, 29, 1), "gris", "plat", base=1)
    t.peindre(disque(24, 21.5, 13), "or", "sphere", base=2)
    # la main qui frotte, posée sur le globe
    main = ellipse(25, 38, 7, 4) | rect(21, 34, 29, 38)
    t.peindre(main & rect(0, 31, 47, 47), "peau", "biseau", base=2)
    t.contour()
    return t


def bouteille_leyde():
    """La bouteille de Leyde (elec.leyde/spectacle) : un bocal de verre garni de métal dedans et dehors, une tige à boule."""
    t = Toile(48, 48)
    verre = rect(13, 14, 34, 44)
    t.peindre(verre, "cyan", "cyl_v", base=1)
    t.peindre(rect(13, 26, 34, 44), "gris", "cyl_v", base=3)
    t.peindre(rect(11, 11, 36, 14), "bois", "biseau", base=1)
    t.peindre(rect(23, 4, 24, 36), "or", "plat", base=1)
    t.peindre(disque(23.5, 4, 3.2), "or", "sphere", base=2)
    t.peindre(trait(23, 36, 19, 41, 1) | trait(24, 36, 28, 41, 1), "or", "plat", base=1)
    t.contour()
    return t


def balance_torsion():
    """La balance de torsion de Coulomb (elec.coulomb/ingenieur) : un fil d'argent fin, une aiguille et deux petites boules chargées, dans une cage de verre."""
    t = Toile(48, 48)
    t.peindre(rect(20, 2, 27, 6), "or", "biseau", base=2)
    t.peindre(rect(22, 6, 25, 18), "cyan", "cyl_v", base=0)
    cage = rect(6, 18, 41, 44)
    t.peindre(cage, "cyan", "cyl_v", base=0)
    t.peindre(rect(4, 16, 43, 18) | rect(4, 44, 43, 46), "bois", "biseau", base=2)
    t.peindre(trait(23, 2, 23, 31, 1), "gris", "plat", base=1)
    t.peindre(trait(10, 31, 36, 31, 1), "gris", "plat", base=0)
    t.peindre(disque(36.5, 31.5, 2.2), "or", "sphere", base=2)
    t.peindre(rect(9, 29, 11, 33), "parchemin", "plat", base=1)
    t.peindre(trait(31, 18, 31, 33, 1), "gris", "plat", base=1)
    t.peindre(disque(31.5, 35.5, 2.2), "or", "sphere", base=2)
    for x in range(8, 40, 3):
        t.poser({(x, 40)}, "C")
    t.contour()
    return t


def cable_sous_marin():
    """Le câble transatlantique (elec.telegraphe/cable) : l'âme de cuivre, la gutta-percha isolante, l'armure de fils de fer."""
    t = Toile(48, 48)
    # tronçon en biais, coupé net pour montrer les couches
    t.peindre(bande((4, 40), (30, 14), 9), "gris", "cyl_h", base=1)
    for i in range(-8, 9, 3):
        t.poser(trait(4 + i * 0.7, 40 + i * 0.7, 30 + i * 0.7, 14 + i * 0.7, 1), "G")
    cx, cy = 33, 15
    t.peindre(disque(cx, cy, 11), "gris", "plat", base=2)
    for ang in range(0, 360, 30):
        x, y = cx + 9.5 * math.cos(math.radians(ang)), cy + 9.5 * math.sin(math.radians(ang))
        t.peindre(disque(x, y, 1.8), "gris", "sphere", base=3)
    t.peindre(disque(cx, cy, 7), "bois", "plat", base=1)
    t.peindre(disque(cx, cy, 3), "cuivre", "sphere", base=2)
    t.contour()
    return t


def cloche():
    """Calcutta, 1895 (elec.radio/bose) : la cloche que Bose fait sonner à distance avec des micro-ondes."""
    t = Toile(48, 48)
    corps = poly([(17, 12), (31, 12), (34, 20), (35, 30), (40, 36), (8, 36), (13, 30), (14, 20)])
    t.peindre(corps, "or", "sphere", base=2)
    t.peindre(rect(21, 7, 27, 12), "or", "biseau", base=1)
    t.peindre(rect(6, 36, 42, 38), "or", "biseau", base=1)
    t.peindre(disque(24, 41, 3), "or", "sphere", base=1)
    t.contour()
    for r in (5, 8):
        for sens in (-1, 1):
            cx = 24 + sens * 19
            for ang in range(-40, 41, 10):
                x = cx - sens * r * math.cos(math.radians(ang)) + sens * 6
                y = 22 + r * math.sin(math.radians(ang))
                if 0 <= x < 48:
                    t.poser({(int(x), int(y))}, "U")
    return t


def valve_fleming():
    """La valve de Fleming (elec.radio/marconi) : une ampoule de verre vide d'air, un filament et une plaque ; le courant n'y passe que dans un sens."""
    t = Toile(48, 48)
    t.peindre(ellipse(24, 20, 14, 17), "cyan", "sphere", base=0)
    t.peindre(rect(18, 34, 30, 44), "gris", "cyl_v", base=1)
    for x in (20, 24, 28):
        t.peindre(rect(x, 44, x, 47), "gris", "plat", base=2)
    t.peindre(trait(21, 34, 21, 18, 1) | trait(27, 34, 27, 18, 1) | trait(21, 18, 24, 13, 1) | trait(27, 18, 24, 13, 1), "orange", "plat", base=2)
    t.peindre(anneau(24, 19, 9, 1.4) & rect(0, 8, 47, 30), "gris", "plat", base=3)
    t.peindre(trait(33, 20, 33, 34, 1), "gris", "plat", base=1)
    t.contour()
    return t


def laser_rubis():
    """Le laser de Maiman (elec.supra/laser) : un barreau de rubis dans une lampe flash en spirale, le rayon rouge de 694 nm."""
    t = Toile(48, 48)
    t.peindre(rect(4, 19, 27, 28), "rouge", "cyl_h", base=2)
    for x in range(5, 28, 5):
        t.peindre(bande((x, 16), (x + 3, 31), 0.9), "gris", "plat", base=3)
    t.peindre(rect(27, 22, 47, 24), "rouge", "plat", base=2)
    t.peindre(rect(27, 23, 47, 23), "rouge", "plat", base=3)
    t.contour()
    return t


DESSINS = {"mc-poisson-fer": poisson_fer, "mc-inclinaison": inclinaison, "mc-globe-soufre": globe_soufre,
           "mc-bouteille-leyde": bouteille_leyde, "mc-balance-torsion": balance_torsion, "mc-cable-sous-marin": cable_sous_marin,
           "mc-cloche": cloche, "mc-valve-fleming": valve_fleming, "mc-laser-rubis": laser_rubis}
ILLUS = {
    ("elec.boussole", "mer"): ("mc-poisson-fer", 1),
    ("elec.gilbert", "experience"): ("mc-inclinaison", 0),
    ("elec.leyde", "gray"): ("mc-globe-soufre", 0),
    ("elec.leyde", "spectacle"): ("mc-bouteille-leyde", 1),
    ("elec.coulomb", "ingenieur"): ("mc-balance-torsion", 1),
    ("elec.telegraphe", "cable"): ("mc-cable-sous-marin", 0),
    ("elec.radio", "bose"): ("mc-cloche", 1),
    ("elec.radio", "marconi"): ("mc-valve-fleming", 1),
    ("elec.supra", "laser"): ("mc-laser-rubis", 1),
}

if __name__ == "__main__":
    executer("etincelle", DESSINS, ILLUS)
