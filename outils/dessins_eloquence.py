"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack Éloquence. Mode d'emploi : outils/dessins_lecons.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import POLICE, Toile, bande, disque, rect, trait  # noqa: E402
from dessins_lecons import executer  # noqa: E402

# lettres qui manquent à la police 3 × 5 de dessin.py
LETTRES = dict(POLICE, **{
    "J": ["001", "001", "001", "101", "010"], "S": ["011", "100", "010", "001", "110"], "L": ["100", "100", "100", "100", "111"],
    "T": ["111", "010", "010", "010", "010"], "'": ["010", "010", "000", "000", "000"], "N": ["101", "111", "111", "111", "101"],
    "H": ["101", "101", "111", "101", "101"], "G": ["011", "100", "101", "101", "011"], "P": ["110", "101", "110", "100", "100"],
    "W": ["101", "101", "111", "111", "101"],
})


def ecrire(chaine, x, y, espace=1):
    out = set()
    for i, c in enumerate(chaine):
        for dy, ligne in enumerate(LETTRES[c]):
            for dx, b in enumerate(ligne):
                if b == "1":
                    out.add((x + i * (3 + espace) + dx, y + dy))
    return out


def jaccuse():
    """L'Aurore du 13 janvier 1898 (rhet.tribuns/lincoln-zola) : « J'accuse…! » en une, la lettre de Zola sur six colonnes."""
    t = Toile(48, 48)
    feuille = rect(4, 3, 43, 46)
    t.peindre(feuille, "parchemin", "plat", base=2)
    t.peindre(rect(4, 3, 43, 3) | rect(4, 46, 43, 46), "parchemin", "plat", base=1)
    t.poser(ecrire("L'AURORE", 8, 5), "k")
    t.poser(rect(6, 11, 41, 11), "k")
    t.poser(ecrire("J'ACCUSE", 8, 14), "R")
    t.poser({(39, 18), (41, 18)}, "R")
    t.poser(rect(6, 21, 41, 21), "k")
    for col in range(6):
        x = 6 + col * 6
        for y in range(23, 45, 2):
            t.poser(rect(x, y, x + 4, y), "A")
    t.contour()
    return t


def presse():
    """L'imprimerie (rhet.imprimerie/luther) : une presse à bras, la vis, la platine, la feuille imprimée sur le marbre."""
    t = Toile(48, 48)
    for x in (8, 37):
        t.peindre(rect(x, 4, x + 3, 44), "bois", "cyl_v", base=2)
    t.peindre(rect(6, 3, 42, 7), "bois", "biseau", base=2)
    t.peindre(rect(6, 15, 42, 18), "bois", "biseau", base=1)
    t.peindre(rect(22, 7, 26, 23), "gris", "cyl_v", base=2)
    for y in range(9, 22, 3):
        t.peindre(trait(22, y, 26, y + 1, 1), "gris", "plat", base=0)
    t.peindre(bande((10, 21), (38, 21), 1), "bois", "plat", base=3)
    t.peindre(rect(15, 23, 33, 26), "gris", "biseau", base=2)
    t.peindre(rect(4, 31, 44, 34), "bois", "biseau", base=2)
    t.peindre(rect(13, 28, 35, 30), "parchemin", "plat", base=2)
    for x in range(15, 34, 3):
        t.poser({(x, 29)}, "B")
    t.peindre(rect(6, 44, 42, 46), "bois", "biseau", base=1)
    t.peindre(disque(40, 21, 1.6), "bois", "plat", base=0)
    t.contour()
    return t


DESSINS = {"mc-jaccuse": jaccuse, "mc-presse": presse}
COPIES = {"mc-papyrus-prisse": ("alchimie", "mc-rouleau-papyrus")}
ILLUS = {
    ("rhet.tribuns", "lincoln-zola"): ("mc-jaccuse", 1),
    ("rhet.imprimerie", "luther"): ("mc-presse", 1),
    ("rhet.origines", "ptahhotep"): ("mc-papyrus-prisse", 2),
}

if __name__ == "__main__":
    executer("eloquence", DESSINS, ILLUS, COPIES)
