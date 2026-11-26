"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack « L'île ».

Un dessin = une fonction qui rend une Toile. ILLUS dit sous quel paragraphe de quel chapitre il se place
(champs `dessin` et `dessin_apres` du chapitre, voir packs/LISEZMOI-IA.md). Le dessin montre l'objet ou
l'espèce dont parle le paragraphe, pas une autre.

Mode d'emploi : outils/dessins_lecons.py.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, anneau, bande, courbe, disque, ellipse, poly, rect, trait  # noqa: E402

from dessins_lecons import executer  # noqa: E402


def epi_orge():
    """Orge sauvage : épi à deux rangs de grains, chacun prolongé d'une longue barbe.
    Ohalo II (res.cultiver/semer) : céréales sauvages cultivées il y a 23 000 ans."""
    t = Toile(48, 48)
    barbes, grains, tiges = [], [], set()
    # (x de l'axe, y du bas de l'épi, nombre de paires de grains, écart des barbes en haut)
    for ax, bas, n, pas in ((33, 31, 6, 2.1), (13, 36, 5, 1.8)):
        tiges |= rect(ax - 1, bas, ax, 47)
        sommet = bas - n * 3.4
        for j in range(n):
            gy = bas - 2 - j * 3.4
            for cote in (-1, 1):
                gx = ax + (cote - 1) * 0.5 + cote * 1.6
                grains.append(ellipse(gx + 0.5, gy - (1.1 if cote > 0 else 0), 1.8, 2.5))
                # les barbes des grains du bas partent le plus loin : l'éventail ne se croise pas
                bx = ax - 0.5 + cote * (1.0 + (n - 1 - j) * pas)
                barbes.append(((gx + 0.5 + cote * 1.0, gy - 2.5), (bx, sommet - 11 + (n - 1 - j) * 1.6)))
    t.peindre(tiges, "or", "biseau", base=0)
    feuille = poly([(32, 47), (34, 47), (40, 42), (46, 40), (41, 44)]) | poly([(13, 47), (11, 47), (17, 42), (23, 40), (18, 44)])
    t.peindre(feuille, "vert", "biseau", base=2)
    for g in grains:
        t.peindre(g, "or", "sphere", base=2)
    t.contour()
    # barbes fines, d'un pixel, couleur paille, derrière les grains
    for (x0, y0), (x1, y1) in barbes:
        t.poser({p for p in trait(x0, y0, x1, y1, 1) if p not in t.px}, "Y")
    return t


def chevre():
    """Chèvre (Capra hircus), monts Zagros (res.cultiver/elever) : une femelle, celle que l'éleveur garde.
    Cornes courtes en arc vers l'arrière, barbiche, pis sous le ventre."""
    t = Toile(48, 48)
    corps = ellipse(21, 26, 13, 7.5)
    cou = poly([(29, 24), (33, 14), (38, 14), (37, 24), (32, 29)])
    tete = poly([(33, 13), (40, 11), (46, 17), (45, 20), (41, 20), (35, 18)])
    pattes = set()
    for x0, x1 in ((10, 12), (14, 16), (27, 29), (31, 33)):
        pattes |= rect(x0, 30, x1, 43)
    queue = poly([(8, 21), (5, 16), (7, 15), (10, 20)])
    t.peindre(pattes, "bois", "cyl_v", base=1)
    t.peindre(corps | cou | queue, "bois", "sphere", base=2)
    t.peindre(tete, "bois", "biseau", base=2)
    # raie sombre le long du dos et devant des pattes, comme chez les chèvres sauvages des Zagros
    t.poser(courbe([(10, 19), (18, 18), (26, 19), (31, 17)], 1), "B")
    t.poser(rect(31, 37, 33, 43) | rect(14, 37, 16, 43), "H")
    # sabots
    for x0, x1 in ((10, 12), (14, 16), (27, 29), (31, 33)):
        t.poser(rect(x0, 43, x1, 44), "n")
    # pis
    t.peindre(ellipse(22.5, 33, 2.2, 2), "rose", "sphere", base=1)
    t.poser({(21, 35), (24, 35)}, "F")
    # oreille, cornes, œil, barbiche, museau
    t.peindre(poly([(36, 13), (32, 16), (31, 15), (34, 12)]), "bois", "plat", base=1)
    t.peindre(courbe([(37, 12), (35, 8), (31, 5), (27, 6), (26, 8)], 2), "parchemin", "biseau", base=1)
    t.peindre(trait(43, 20, 42, 25, 1) | trait(42, 20, 41, 24, 1), "bois", "plat", base=0)
    t.poser({(40, 14)}, "k")
    t.poser({(46, 17), (45, 18)}, "H")
    t.contour()
    return t


def thon():
    """Thon : corps en fuseau, dos bleu sombre, ventre argenté, pinnules jaunes, queue en croissant.
    Jerimalai (res.cultiver/pecher) : du thon parmi les arêtes de 42 000 ans."""
    t = Toile(48, 48)
    # fuseau : profil haut et bas
    haut = [(3, 24), (6, 20), (11, 17), (18, 15), (26, 15), (33, 17), (38, 20), (40, 22)]
    bas = [(40, 25), (38, 27), (33, 30), (26, 32), (18, 32), (11, 30), (6, 28), (3, 25)]
    corps = poly(haut + bas)
    pedoncule = poly([(38, 21), (42, 22.5), (42, 24.5), (38, 26)])
    queue = poly([(41, 22), (45, 14), (47, 8), (47, 15), (44, 23.5), (47, 32), (47, 39), (45, 33), (41, 25)])
    dorsale = poly([(17, 15), (20, 9), (22, 9), (24, 15)])
    pectorale = poly([(13, 23), (24, 21), (14, 25)])
    anale = poly([(27, 31), (30, 36), (31, 31)])
    deuxieme = poly([(27, 15), (31, 10), (32, 16)])
    t.peindre(queue | dorsale | deuxieme, "bleu", "biseau", base=1)
    t.peindre(corps | pedoncule, "gris", "cyl_h", base=3)
    # dos bleu nuit au-dessus de la ligne latérale
    dos = {p for p in corps | pedoncule if p[1] < 21 + (p[0] - 20) * 0.03}
    t.peindre(dos, "bleu", "cyl_h", base=1, maxi=2)
    t.peindre(anale, "or", "plat", base=2)
    t.peindre(pectorale, "bleu", "plat", base=2)
    # pinnules jaunes entre la seconde dorsale/l'anale et la queue
    for x in (33, 35, 37):
        t.poser({(x, 17 + (x - 33) // 2), (x, 16 + (x - 33) // 2)}, "y")
        t.poser({(x, 30 - (x - 33) // 2), (x, 31 - (x - 33) // 2)}, "y")
    # œil, bouche, opercule
    t.poser({(8, 21), (9, 21), (8, 22), (9, 22)}, "k")
    t.poser({(8, 21)}, "w")
    t.poser({(3, 25), (4, 25), (5, 25)}, "n")
    t.poser(courbe([(13, 21), (14, 24), (13, 28)], 1), "G")
    t.contour()
    return t



# --- Le feu (ile.feu) ------------------------------------------------------------

def _flammes(t, cx, bas, h, l):
    """Flamme en trois couches (rouge, orange, jaune), pointe en haut."""
    for fam_px, k in ((("rouge", 1), 1.0), (("orange", 1), 0.72), (("or", 2), 0.42)):
        fam, base = fam_px
        pts = [(cx - l * k, bas), (cx - l * k * 0.8, bas - h * k * 0.45), (cx - l * k * 0.25, bas - h * k * 0.7),
               (cx, bas - h * k), (cx + l * k * 0.35, bas - h * k * 0.62), (cx + l * k * 0.85, bas - h * k * 0.38), (cx + l * k, bas)]
        t.peindre(poly(pts), fam, "plat", base=base)


def os_brule():
    """Wonderwerk (ile.feu/garder) : un os à demi carbonisé posé dans la cendre, quelques braises."""
    t = Toile(48, 48)
    cendre = ellipse(24, 37, 22, 8)
    t.peindre(cendre, "gris", "sphere", base=1, maxi=3)
    os_ = bande((12, 30), (36, 22), 2.4) | disque(11, 32, 3.6) | disque(9, 27.5, 3) | disque(37, 21, 3.6) | disque(39, 16.5, 3)
    t.peindre(os_, "ivoire", "plat")
    t.peindre({p for p in os_ if p[1] > (34 - (p[0] - 8) * 0.33)}, "parchemin", "plat", base=1)
    # partie carbonisée : brun puis noir vers le bout posé dans le feu
    t.peindre({p for p in os_ if p[0] > 27}, "gris", "plat", base=0)
    t.peindre({p for p in os_ if 22 < p[0] <= 27 and (p[0] + p[1]) % 2 == 0}, "gris", "plat", base=0)
    t.peindre({p for p in os_ if 18 < p[0] <= 22 and (p[0] + p[1]) % 2 == 0}, "bois", "plat", base=1)
    for x, y in ((14, 40), (21, 42), (30, 41), (37, 38), (27, 37), (8, 37)):
        t.peindre(ellipse(x + 0.5, y + 0.5, 1.7, 1.2), "rouge", "plat", base=2)
        t.poser({(x, y)}, "a")
    t.contour()
    return t


def pyrite_silex():
    """Barnham (ile.feu/allumer) : pyrite frappée contre un silex, des étincelles sur de l'herbe sèche."""
    t = Toile(48, 48)
    silex = poly([(4, 30), (9, 22), (18, 19), (24, 24), (22, 33), (12, 36)])
    t.peindre(silex, "gris", "biseau", base=2)
    t.peindre(poly([(9, 23), (17, 20), (21, 24), (12, 27)]), "parchemin", "plat", base=1)
    pyrite = poly([(28, 14), (36, 9), (43, 13), (42, 22), (33, 24), (27, 20)])
    t.peindre(pyrite, "or", "biseau", base=1)
    t.peindre(rect(31, 13, 33, 15) | rect(37, 16, 39, 18), "or", "plat", base=3)
    herbe = set()
    for x0 in range(14, 38, 3):
        herbe |= trait(x0, 46, x0 + (x0 % 5) - 2, 39, 1)
    t.peindre(herbe, "parchemin", "plat", base=1)
    t.contour()
    for x, y in ((25, 21), (27, 26), (24, 29), (29, 30), (26, 34), (31, 35), (22, 31)):
        t.poser({(x, y)}, "j")
        t.poser({(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)} - set(t.px), "y")
    return t


def foyer():
    """Le soir au coin du feu (ile.feu/changer) : un foyer de bûches et de pierres, la nuit autour."""
    t = Toile(48, 48)
    t.peindre(ellipse(24, 24, 23, 23), "nuit", "plat", base=1)
    for x, y in ((8, 10), (38, 7), (30, 13), (12, 20), (41, 18)):
        t.poser({(x, y)}, "j")
    t.peindre(ellipse(24, 26, 15, 15), "violet", "plat", base=0)
    _flammes(t, 24, 37, 22, 9)
    t.peindre(bande((12, 40), (36, 34), 2) | bande((12, 34), (36, 40), 2), "bois", "cyl_h", base=2)
    for x in (9, 16, 24, 32, 39):
        t.peindre(ellipse(x + 0.5, 42.5, 3.2, 2.2), "gris", "sphere", base=2)
    t.contour()
    return t


# --- Cueillir sans épuiser (res.cueillir) -----------------------------------------

def moa():
    """Moa (res.cueillir/moas) : grand oiseau de Nouvelle-Zélande sans ailes visibles, long cou, pattes épaisses."""
    t = Toile(48, 48)
    corps = ellipse(19, 24, 13, 9)
    cou = bande((26, 20), (34, 6), 2.6)
    tete = ellipse(36, 5.5, 3.6, 2.6)
    bec = poly([(38, 4), (44, 6), (38, 7)])
    pattes = bande((16, 31), (14, 44), 1.6) | bande((23, 31), (25, 44), 1.6)
    pieds = trait(10, 45, 17, 45, 1) | trait(22, 45, 29, 45, 1) | trait(11, 46, 16, 46, 1) | trait(23, 46, 28, 46, 1)
    t.peindre(pattes | pieds, "gris", "cyl_v", base=1, maxi=2)
    t.peindre(corps | cou | tete, "bois", "sphere", base=2)
    # plumage pendant en mèches
    for x in range(8, 30, 3):
        t.poser(trait(x, 27, x - 1, 32, 1), "B")
    t.peindre(bec, "parchemin", "biseau", base=1)
    t.poser({(36, 5)}, "k")
    t.contour()
    return t


def anguille():
    """Budj Bim (res.cueillir/reserve) : une anguille dans un bassin creusé dans la lave."""
    t = Toile(48, 48)
    t.peindre(ellipse(24, 30, 23, 14), "gris", "biseau", base=1)
    t.peindre(ellipse(24, 30, 20, 11), "cyan", "plat", base=0)
    corps = set()
    pts = [(6, 31), (12, 26), (18, 30), (24, 35), (31, 31), (36, 26), (41, 27)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        corps |= bande((x0, y0), (x1, y1), 2.2)
    corps |= ellipse(41.5, 27.5, 3.4, 2.6)
    t.peindre(corps, "bois", "plat", base=1)
    t.peindre({p for p in corps if (p[0] + 1, p[1] + 1) not in corps}, "parchemin", "plat", base=1)
    t.poser({(42, 26)}, "k")
    t.contour()
    return t


def rahui():
    """Rāhui (res.cueillir/rahui) : un vieux vêtement pendu à un poteau au bord de la rivière."""
    t = Toile(48, 48)
    t.peindre(rect(0, 38, 47, 47), "cyan", "plat", base=0)
    for x in range(2, 46, 7):
        t.poser(trait(x, 41, x + 3, 41, 1), "c")
    t.peindre(rect(21, 4, 24, 44), "bois", "cyl_v", base=2)
    t.peindre(rect(12, 8, 34, 10), "bois", "biseau", base=1)
    habit = poly([(13, 11), (33, 11), (31, 30), (27, 28), (24, 31), (19, 28), (15, 30)])
    t.peindre(habit, "bois", "biseau", base=2)
    t.peindre({p for p in habit if p[1] in (15, 20, 25)}, "bois", "plat", base=1)
    t.peindre(trait(18, 12, 23, 18, 1) | trait(28, 12, 23, 18, 1), "bois", "plat", base=3)
    t.contour()
    return t


# --- Lire le ciel (meteo.ciel) ----------------------------------------------------

def ciel_rouge():
    """Ciel rouge le soir (meteo.ciel/rouge) : soleil couchant, nuages rougis, mer à l'ouest."""
    t = Toile(48, 48)
    for y in range(4, 34):
        fam, b = (("violet", 1) if y < 10 else ("rouge", 1) if y < 18 else ("rouge", 2) if y < 26 else ("orange", 1))
        t.peindre(rect(2, y, 45, y), fam, "plat", base=b)
    t.peindre(ellipse(24, 33, 7, 7) & rect(0, 0, 47, 33), "or", "plat", base=2)
    for cx, cy, rx in ((12, 12, 9), (35, 17, 8), (20, 22, 6)):
        t.peindre(ellipse(cx, cy, rx, 2), "rose", "plat", base=1)
    t.peindre(rect(2, 34, 45, 44), "bleu", "plat", base=0)
    for y, x0, x1 in ((36, 18, 30), (39, 20, 28), (42, 22, 26)):
        t.poser(rect(x0, y, x1, y), "y")
    t.contour()
    return t


def halo_solaire():
    """Halo (meteo.ciel/halo) : l'anneau à 22 degrés autour du Soleil, dans un ciel voilé."""
    t = Toile(48, 48)
    t.peindre(rect(1, 1, 46, 46), "bleu", "plat", base=3)
    t.peindre(anneau(24, 22, 17, 2.4), "gris", "plat", base=5)
    t.peindre(anneau(24, 22, 15, 1), "orange", "plat", base=2)
    t.peindre(disque(24, 22, 4), "or", "plat", base=3)
    t.peindre(rect(1, 38, 46, 46), "vert", "biseau", base=1)
    t.contour()
    return t


def pomme_de_pin():
    """Pomme de pin (meteo.ciel/sol) : écailles ouvertes par temps sec."""
    t = Toile(48, 48)
    t.peindre(rect(23, 3, 25, 9), "bois", "plat", base=1)
    for j, (y, n, r) in enumerate(((11, 2, 6), (16, 3, 9), (21, 4, 11), (26, 4, 12), (31, 4, 11), (36, 3, 9), (41, 2, 6))):
        for i in range(n):
            x = 24 - r + (2 * r) * (i + 0.5) / n
            ec = poly([(x - 3, y - 1), (x + 3, y - 1), (x + 2.2, y + 3), (x - 2.2, y + 3)])
            t.peindre(ec, "bois", "biseau", base=2)
            t.peindre(rect(int(x) - 1, y - 1, int(x), y - 1), "bois", "plat", base=0)
    t.contour()
    return t



# --- La cité : écrire, juger, payer (cite.*) ---------------------------------------

def stele():
    """Stèle du code d'Hammurabi (cite.loi/stele) : basalte noir, le roi devant Shamash en haut, le texte dessous."""
    t = Toile(48, 48)
    pierre = poly([(13, 46), (11, 12), (14, 5), (24, 2), (34, 5), (37, 12), (35, 46)])
    t.peindre(pierre, "gris", "sphere", base=0, maxi=1)
    # relief : Shamash assis à droite, Hammurabi debout à gauche
    t.peindre(rect(17, 8, 19, 17) | disque(18.5, 6.5, 1.8) | rect(19, 10, 21, 10), "gris", "plat", base=3)
    t.peindre(rect(26, 11, 31, 16) | rect(27, 6, 30, 10) | disque(28.5, 5, 1.8) | trait(26, 9, 23, 10, 1), "gris", "plat", base=3)
    t.peindre(rect(25, 17, 32, 18), "gris", "plat", base=2)
    # lignes de signes cunéiformes
    for y in range(21, 45, 3):
        for x in range(14, 34, 2):
            if (x * 7 + y * 3) % 5:
                t.poser({(x, y)}, "g")
    t.contour()
    return t


def piece_lydie():
    """Pièce de Lydie (cite.monnaie/lydie) : électrum, or pâle mêlé d'argent, tête de lion, frappe irrégulière."""
    t = Toile(48, 48)
    flan = poly([(9, 22), (12, 12), (21, 7), (33, 8), (40, 16), (41, 28), (35, 38), (23, 41), (13, 36)])
    t.peindre(flan, "or", "sphere", base=2)
    # tête de lion, gueule ouverte, crinière en mèches
    criniere = disque(23, 23, 9)
    t.peindre(criniere, "or", "plat", base=1)
    tete = ellipse(26, 24, 7, 5.5)
    t.peindre(tete, "or", "plat", base=2)
    t.poser(trait(28, 27, 33, 26, 1) | trait(28, 29, 33, 29, 1), "4")
    t.poser({(27, 21), (28, 21)}, "4")
    t.poser({(31, 22), (31, 23)}, "k")
    t.contour()
    return t


def piece_tortue():
    """Statère d'Égine (cite.monnaie/frappe) : pièce d'argent à la tortue de mer."""
    t = Toile(48, 48)
    flan = ellipse(24, 24, 18, 17)
    t.peindre(flan, "gris", "sphere", base=3)
    carapace = ellipse(24, 23, 8, 9)
    t.peindre(carapace, "gris", "sphere", base=2)
    t.peindre(trait(24, 15, 24, 31, 1) | trait(17, 21, 31, 21, 1) | trait(18, 26, 30, 26, 1), "gris", "plat", base=1)
    t.peindre(ellipse(24, 12.5, 2.4, 2.4), "gris", "plat", base=2)
    for (x0, y0, x1, y1) in ((17, 17, 12, 13), (31, 17, 36, 13), (18, 30, 14, 34), (30, 30, 34, 34)):
        t.peindre(bande((x0, y0), (x1, y1), 1.6), "gris", "plat", base=2)
    t.poser({(23, 12), (25, 12)}, "n")
    t.contour()
    return t


def barres_metal():
    """Avant les pièces (cite.monnaie/troc) : de grosses barres de cuivre en lingots, et des broches (obeloi)."""
    t = Toile(48, 48)
    for (y, dx) in ((34, 0), (25, 4)):
        lingot = poly([(6 + dx, y), (10 + dx, y - 6), (38 + dx, y - 6), (42 + dx, y), (38 + dx, y + 3), (10 + dx, y + 3)])
        t.peindre(lingot, "cuivre", "biseau", base=1)
    for i in range(4):
        t.peindre(bande((8 + i * 3, 14 - i), (40 + i * 2, 6 - i), 0.8), "gris", "plat", base=2)
    t.contour()
    return t


def tablette_eleve():
    """Maison des tablettes (cite.ecrire/ecole) : la petite tablette ronde de l'élève, et son stylet de roseau."""
    t = Toile(48, 48)
    tab = ellipse(22, 27, 17, 15)
    t.peindre(tab, "parchemin", "sphere", base=1)
    for y in (20, 26, 32):
        for x in range(12, 32, 4):
            t.poser({(x, y), (x + 1, y), (x, y + 1)}, "A")
    t.poser(trait(9, 23, 35, 23, 1) | trait(9, 29, 35, 29, 1), "A")
    t.peindre(bande((30, 40), (45, 6), 1.3), "or", "cyl_h", base=1)
    t.peindre(poly([(29, 43), (30, 39), (32, 40)]), "bois", "plat", base=1)
    t.contour()
    return t


def os_oracle():
    """Chine (cite.ecrire/ailleurs) : omoplate de bœuf gravée pour la divination, fendue par le feu."""
    t = Toile(48, 48)
    os_ = poly([(18, 3), (28, 3), (27, 12), (38, 34), (35, 45), (14, 45), (10, 34), (19, 12)])
    t.peindre(os_, "ivoire", "plat")
    t.peindre({p for p in os_ if p[0] > 29 or p[1] > 42}, "parchemin", "plat", base=1)
    for y in range(18, 42, 5):
        for x in range(15, 34, 5):
            if (x + y) % 3 and (x, y) in os_:
                t.poser(trait(x, y, x + 2, y, 1) | trait(x + 1, y - 1, x + 1, y + 2, 1), "B")
    t.poser(courbe([(23, 14), (24, 22), (22, 26)], 1) | trait(24, 20, 28, 22, 1), "H")
    t.contour()
    return t


# --- Fils et bateaux (res.tisser, res.naviguer) -----------------------------------

def lin():
    """Lin (res.tisser/fils) : tiges fines, petites feuilles, fleurs bleues à cinq pétales."""
    t = Toile(48, 48)
    for x0, x1, top in ((14, 12, 10), (24, 25, 5), (33, 36, 12)):
        t.peindre(trait(x0, 47, x1, top + 4, 1), "vert", "plat", base=1)
        for y in range(top + 10, 44, 6):
            xx = x0 + (x1 - x0) * (47 - y) / (47 - top - 4)
            t.peindre(trait(xx, y, xx + 3, y - 3, 1), "vert", "plat", base=2)
        for ang in range(-90, 270, 72):
            px, py = x1 + 2.6 * math.cos(math.radians(ang)), top + 2.6 * math.sin(math.radians(ang))
            t.peindre(disque(px + 0.5, py + 0.5, 2.1), "bleu", "plat", base=3)
        t.peindre(disque(x1, top, 1.2), "or", "plat", base=2)
    t.contour()
    return t


def fils_teints():
    """Dzudzuana (res.tisser/usages) : fibres tordues en fils, l'un noué, teintes en noir, gris, turquoise et rose."""
    t = Toile(48, 48)
    for i, (fam, base) in enumerate((("gris", 0), ("gris", 2), ("cyan", 0), ("rose", 1))):
        y0 = 10 + i * 9
        fil = set()
        for x in range(3, 45):
            fil |= {(x, y0 + (1 if (x // 2 + i) % 2 else 0))}
        fil |= {(x, y0 + 1) for x in range(3, 45, 2)}
        t.peindre(fil, fam, "plat", base=base)
        # torsion visible : pixels clairs en biais
        t.poser({(x, y0 + ((x // 2) % 2)) for x in range(4, 44, 4)}, "z" if fam != "gris" or base else "G")
    t.peindre(ellipse(30, 29, 3, 2.5), "cyan", "plat", base=1)
    t.contour()
    return t


def chene():
    """Çatalhöyük (res.tisser/chene) : feuille et gland de chêne, et une lanière de liber, la couche souple sous l'écorce."""
    t = Toile(48, 48)
    feuille = set()
    for i, y in enumerate(range(8, 34, 5)):
        r = 4 + (3 if i in (2, 3, 4) else 1)
        feuille |= ellipse(18 + (1 if i % 2 else -1), y + 2, r, 3.2)
    feuille |= rect(17, 6, 19, 38)
    t.peindre(feuille, "vert", "biseau", base=2)
    t.peindre(trait(18, 6, 18, 40, 1), "vert", "plat", base=0)
    t.peindre(ellipse(33, 15, 4, 5), "bois", "sphere", base=2)
    t.peindre(ellipse(33, 10.5, 4.8, 2.4), "bois", "plat", base=1)
    liber = bande((26, 44), (45, 30), 2.4)
    t.peindre(liber, "parchemin", "biseau", base=2)
    t.peindre(bande((26, 46), (45, 32), 1), "bois", "plat", base=1)
    t.contour()
    return t


def pirogue_pesse():
    """Pirogue de Pesse (res.naviguer/pesse) : un seul tronc de pin creusé, environ 3 mètres."""
    t = Toile(48, 48)
    coque = poly([(2, 24), (8, 21), (40, 21), (46, 23), (40, 31), (8, 31)])
    t.peindre(coque, "bois", "cyl_h", base=2)
    creux = poly([(8, 22), (40, 22), (38, 25), (10, 25)])
    t.peindre(creux, "bois", "plat", base=0)
    t.peindre(trait(10, 28, 38, 28, 1), "bois", "plat", base=1)
    t.peindre(rect(0, 34, 47, 40), "bois", "plat", base=0)
    for x in range(1, 47, 5):
        t.poser({(x, 35), (x + 2, 37)}, "B")
    t.contour()
    return t


def pirogue_balancier():
    """Pacifique (res.naviguer/etoiles) : pirogue à balancier, voile en pince de crabe, sous les étoiles."""
    t = Toile(48, 48)
    t.peindre(rect(0, 0, 47, 34), "nuit", "plat", base=0)
    for x, y in ((5, 5), (40, 4), (33, 10), (12, 14), (44, 18), (20, 3)):
        t.poser({(x, y)}, "j")
    t.peindre(rect(0, 35, 47, 47), "bleu", "plat", base=1)
    coque = poly([(6, 33), (40, 33), (37, 38), (10, 38)])
    t.peindre(coque, "bois", "biseau", base=2)
    t.peindre(rect(12, 39, 34, 40), "bois", "plat", base=3)
    t.peindre(trait(16, 33, 14, 39, 1) | trait(30, 33, 32, 39, 1), "bois", "plat", base=1)
    voile = poly([(22, 32), (12, 8), (17, 9), (23, 22), (31, 6), (35, 8)])
    t.peindre(voile, "parchemin", "biseau", base=2)
    t.peindre(trait(22, 32, 12, 8, 1) | trait(22, 32, 35, 8, 1), "bois", "plat", base=1)
    t.poser({(x, 43) for x in range(3, 45, 6)} | {(x + 3, 45) for x in range(3, 45, 6)}, "x")
    t.contour()
    return t


DESSINS = {"mc-orge-sauvage": epi_orge, "mc-chevre": chevre, "mc-thon": thon,
           "mc-os-brule": os_brule, "mc-pyrite-silex": pyrite_silex, "mc-foyer": foyer,
           "mc-moa": moa, "mc-anguille": anguille, "mc-rahui": rahui,
           "mc-ciel-rouge": ciel_rouge, "mc-halo-solaire": halo_solaire, "mc-pomme-de-pin": pomme_de_pin,
           "mc-stele-hammurabi": stele, "mc-piece-lydie": piece_lydie, "mc-piece-tortue": piece_tortue,
           "mc-barres-metal": barres_metal, "mc-tablette-eleve": tablette_eleve, "mc-os-oracle": os_oracle,
           "mc-lin": lin, "mc-fils-teints": fils_teints, "mc-chene": chene,
           "mc-pirogue-pesse": pirogue_pesse, "mc-pirogue-balancier": pirogue_balancier}

# (compétence, chapitre) → (dessin, indice du paragraphe qui en parle)
ILLUS = {
    ("res.cultiver", "semer"): ("mc-orge-sauvage", 1),
    ("res.cultiver", "elever"): ("mc-chevre", 1),
    ("res.cultiver", "pecher"): ("mc-thon", 0),
    ("ile.feu", "garder"): ("mc-os-brule", 1),
    ("ile.feu", "allumer"): ("mc-pyrite-silex", 0),
    ("ile.feu", "changer"): ("mc-foyer", 1),
    ("res.cueillir", "moas"): ("mc-moa", 0),
    ("res.cueillir", "reserve"): ("mc-anguille", 0),
    ("res.cueillir", "rahui"): ("mc-rahui", 1),
    ("meteo.ciel", "rouge"): ("mc-ciel-rouge", 0),
    ("meteo.ciel", "halo"): ("mc-halo-solaire", 0),
    ("meteo.ciel", "sol"): ("mc-pomme-de-pin", 1),
    ("cite.ecrire", "comptes"): ("mc-tablette-cuneiforme", 1),
    ("cite.ecrire", "ecole"): ("mc-tablette-eleve", 0),
    ("cite.ecrire", "ailleurs"): ("mc-os-oracle", 0),
    ("cite.loi", "urnammu"): ("mc-balance-argent", 1),
    ("cite.loi", "stele"): ("mc-stele-hammurabi", 0),
    ("cite.monnaie", "troc"): ("mc-barres-metal", 0),
    ("cite.monnaie", "lydie"): ("mc-piece-lydie", 0),
    ("cite.monnaie", "frappe"): ("mc-piece-tortue", 0),
    ("res.tisser", "fils"): ("mc-lin", 1),
    ("res.tisser", "usages"): ("mc-fils-teints", 0),
    ("res.tisser", "chene"): ("mc-chene", 1),
    ("res.naviguer", "pesse"): ("mc-pirogue-pesse", 0),
    ("res.naviguer", "etoiles"): ("mc-pirogue-balancier", 1),
}

# Dessins d'autres packs repris tels quels (copiés : un pack éteint ne doit pas laisser l'île sans image).
COPIES = {"mc-tablette-cuneiforme": ("alchimie", "chim-tablette"), "mc-balance-argent": ("logique", "mc-balance")}


if __name__ == "__main__":
    executer("ile", DESSINS, ILLUS, COPIES)
