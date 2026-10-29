"""Portraits des savants jouables, en 40 × 48 : le même corps que l'avatar (pour que lunettes et moustaches
tombent juste), une peau, une tenue, une barbe, un objet fétiche (calque « base ») et une coiffure (calque
« cheveux »). Les caractères ! X * (vêtement), ~ Z (bas) et + Q (détails) prennent les couleurs du savant.

Un pack décrit ses portraits dans packs/<id>/portraits.json, une recette par savant :

    {"id": "bach", "peau": "claire", "tenue": "manteau", "couleurs": ["#3B3B3B", "#1E1E24", "#EEF0F4"],
     "coiffure": ["perruque", "gris", 4], "barbe": null, "objet": "livre"}

  peau      claire, mate, foncee
  tenue     manteau, blouse, pull, cardigan, toge, robe
  couleurs  vêtement, bas, détails (#RRGGBB)
  coiffure  [style, famille de couleur, teinte] ; styles : court, raie, chignon, longs, boucles, couronne (chauve
            sur le dessus), ebouriffe, perruque, perruque_courte, turban, coiffe, frises ; familles : cheveux, gris,
            rouge, or… (voir FAMILLES dans dessin.py) ; teinte : de 0 (sombre) au plus clair de la famille
  barbe     null ou [style, famille, teinte] ; styles : pleine, longue, fleuve, favoris
  objet     tenu dans la main : astrolabe, compas, lentille, lunette, pomme, plume, balance, carnet, carte, fiole,
            craie, ardoise, photo51, ruban, trajectoire, tableau, col_cygne, bobine, lampe, des, loupe, livre,
            cerveau, menottes, thermometre, diapason, metronome, globe, rouleau, aucun

    python3 outils/portrait.py <pack>             remplit couleurs, base et cheveux des savants du pack
    python3 outils/portrait.py <pack> apercu.png  et dessine une planche pour vérifier à l'œil
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dessin import Toile, anneau, bande, courbe, disque, ellipse, miroir, poly, rect, texte, trait

L, H = 40, 48
RACINE = Path(__file__).resolve().parent.parent


def toile():
    return Toile(L, H)


def ombrer(hexa, f):
    """Assombrit (f < 1) ou éclaircit (f > 1) une couleur."""
    r, g, b = (int(hexa[i:i + 2], 16) for i in (1, 3, 5))
    if f < 1:
        r, g, b = (int(c * f) for c in (r, g, b))
    else:
        r, g, b = (int(c + (255 - c) * (f - 1)) for c in (r, g, b))
    return "#%02X%02X%02X" % (r, g, b)


def couleurs_rang(principal, bas, detail):
    return {"!": ombrer(principal, 0.68), "X": principal, "*": ombrer(principal, 1.32),
            "~": ombrer(bas, 0.7), "Z": bas, "+": ombrer(detail, 0.7), "Q": detail}


def corps():
    t = toile()
    t.peindre(disque(9.6, 15, 2.2) | disque(30.4, 15, 2.2), "peau", "plat", 1)
    t.peindre(rect(17, 21, 22, 25), "peau", "plat", 1)
    t.peindre(ellipse(20, 13.5, 10.6, 10), "peau", "sphere", 2, mini=1)
    t.peindre(disque(8.5, 37, 2.4) | disque(31.5, 37, 2.4), "peau", "sphere", 2, mini=1)
    t.contour()
    t.poser(rect(14, 13, 15, 15) | rect(24, 13, 25, 15), "n")
    t.poser({(14, 13), (24, 13)}, "w")
    t.poser({(12, 17), (13, 17), (26, 17), (27, 17)}, "I")
    t.poser({(20, 16)}, "S")
    t.poser({(17, 18), (18, 19), (19, 19), (20, 19), (21, 19), (22, 18)}, "m")
    return t


def silhouette(t):
    """Tenue de base : buste, manches, pantalon, chaussures."""
    buste = poly([(12, 24), (28, 24), (30.5, 39), (9.5, 39)])
    manches = bande((12.5, 25), (8.5, 35), 2.6, 2.3)
    manches |= miroir(manches, L)
    t.peindre(manches, "tenue", "biseau", 1)
    t.peindre(buste, "tenue", "biseau", 1)
    t.peindre(rect(12, 39, 19, 44) | rect(21, 39, 28, 44), "bas", "biseau", 1)
    t.peindre(rect(11, 44, 19, 46) | rect(21, 44, 29, 46), "gris", "biseau", 1)
    return buste


def zone_cheveux():
    out = set()
    for (x, y) in ellipse(20, 12, 12, 10.6):
        frange = 8 + ((x // 3) % 2) * 2
        if y <= frange or ((x <= 10 or x >= 29) and y <= 16):
            out.add((x, y))
    return out


# Teintes de peau : remplacement des quatre teintes de la famille « peau ».
PEAUX = {
    "claire": {},
    "mate": {"6": "J", "S": "L", "s": "W", "7": "s"},
    "foncee": {"6": "0", "S": "J", "s": "L", "7": "W"},
}


def peindre_corps(t, peau):
    c = corps()
    table = PEAUX[peau]
    for p, ch in c.px.items():
        t.px[p] = table.get(ch, ch)


def tenue(t, style):
    if style == "toge":
        drape = poly([(12, 24), (28, 24), (31, 46), (9, 46)])
        manches = bande((12.5, 25), (8.5, 35), 2.6, 2.3)
        t.peindre(manches | miroir(manches, L), "tenue", "biseau", 1)
        t.peindre(drape, "tenue", "biseau", 1)
        t.poser(trait(12, 25, 27, 40, 2), "!")
        t.poser(courbe([(14, 32), (17, 38), (16, 45)]) | courbe([(25, 40), (24, 45)]), "!")
    elif style == "robe":
        jupe = poly([(12, 24), (28, 24), (29, 33), (33, 46), (7, 46)])
        manches = bande((12.5, 25), (8.5, 35), 2.6, 2.3)
        t.peindre(manches | miroir(manches, L), "tenue", "biseau", 1)
        t.peindre(jupe, "tenue", "biseau", 1)
        t.poser(rect(12, 32, 28, 33), "Q")
        t.poser(courbe([(13, 36), (11, 45)]) | courbe([(27, 36), (29, 45)]), "!")
    else:
        silhouette(t)
        if style == "manteau":
            t.peindre(poly([(17, 24), (23, 24), (21, 33), (19, 33)]), "detail", "plat", 1)
            t.poser(trait(17, 24, 19, 33) | trait(23, 24, 21, 33), "!")
            t.poser({(20, 34), (20, 37)}, "+")
        elif style == "blouse":
            t.peindre(poly([(17, 24), (23, 24), (22.5, 39), (17.5, 39)]), "detail", "plat", 1)
            t.poser(trait(17, 24, 17.5, 39) | trait(22, 24, 22.5, 39), "!")
            t.poser(trait(16, 24, 18, 29) | trait(24, 24, 22, 29), "!")
        elif style == "pull":
            t.peindre(ellipse(20, 24.5, 5, 1.8), "detail", "plat", 1)
            for y in range(28, 39, 3):
                t.poser(rect(11, y, 28, y), "!")
        elif style == "cardigan":
            t.peindre(poly([(17, 24), (23, 24), (22.5, 39), (17.5, 39)]), "detail", "plat", 1)
            for y in (27, 31, 35):
                t.poser({(20, y)}, "+")
    t.contour()


def coiffure(style, fam="cheveux", base=1):
    t = toile()
    if style == "court":
        t.peindre(zone_cheveux(), fam, "sphere", base)
    elif style == "raie":
        z = {(x, y) for (x, y) in ellipse(20, 12, 12, 10.6) if y <= 8 or ((x <= 10 or x >= 29) and y <= 15)}
        z |= {(x, y) for (x, y) in ellipse(20, 12, 12, 10.6) if x >= 16 and y <= 10 - (x - 16) // 4}
        t.peindre(z, fam, "sphere", base)
        t.poser(trait(15, 2, 14, 7), "8" if fam == "cheveux" else "G")
    elif style == "chignon":
        t.peindre({(x, y) for (x, y) in ellipse(20, 12, 12, 10.6) if y <= 7 or ((x <= 10 or x >= 29) and y <= 14)}, fam, "sphere", base)
        t.peindre(disque(20, 2.5, 4), fam, "sphere", base)
    elif style == "longs":
        z = {(x, y) for (x, y) in ellipse(20, 12, 12, 10.6) if y <= 7}
        z |= rect(7, 7, 10, 27) | rect(29, 7, 32, 27)
        t.peindre(z, fam, "sphere", base)
    elif style == "boucles":
        z = {(x, y) for (x, y) in ellipse(20, 12, 12, 10.6) if y <= 6}
        for y in range(8, 24, 4):
            z |= disque(8.5, y, 2.4) | disque(31.5, y, 2.4)
        t.peindre(z, fam, "sphere", base)
    elif style == "couronne":
        # Chauve sur le dessus, une couronne de cheveux sur les côtés.
        t.peindre(rect(8, 9, 10, 17) | rect(29, 9, 31, 17), fam, "sphere", base)
    elif style == "ebouriffe":
        nuage = set()
        for cx, cy, r in [(12, 8, 5), (20, 6, 5.5), (28, 8, 5), (9, 14, 4), (31, 14, 4), (15, 5, 4), (25, 5, 4), (8, 19, 2.6), (32, 19, 2.6)]:
            nuage |= disque(cx, cy, r)
        nuage -= {(x, y) for (x, y) in ellipse(20, 16, 9.4, 8.2) if y >= 10}
        t.peindre(nuage, fam, "sphere", base)
    elif style == "perruque":
        p = {(x, y) for (x, y) in ellipse(20, 11, 12, 10) if y <= 8}
        for y in range(9, 32, 3):
            p |= disque(9.5, y, 2.8) | disque(30.5, y, 2.8)
        t.peindre(p, fam, "sphere", base)
    elif style == "perruque_courte":
        p = {(x, y) for (x, y) in ellipse(20, 11, 12, 10) if y <= 8}
        for y in (11, 15):
            p |= ellipse(8.5, y, 2.6, 1.8) | ellipse(31.5, y, 2.6, 1.8)
        t.peindre(p, fam, "sphere", base)
        t.peindre(bande((20, 4), (20, 4.5), 0.5), fam, "plat", base)
    elif style == "turban":
        tur = {(x, y) for (x, y) in ellipse(20, 8, 13, 7.5) if y <= 10}
        t.peindre(tur, "gris", "sphere", 4)
        for y in (4, 7):
            t.poser(courbe([(9, y + 2), (20, y - 1), (31, y + 2)]), "z")
        t.peindre(disque(20, 6, 1.6), "vert", "sphere", 2)
    elif style == "coiffe":
        t.peindre({(x, y) for (x, y) in ellipse(20, 12, 12, 10.6) if y <= 8 or ((x <= 10 or x >= 29) and y <= 13)}, fam, "sphere", base)
        t.peindre(poly([(9, 7), (20, 1), (31, 7), (29, 10), (11, 10)]), "gris", "biseau", 5)
        t.peindre(rect(9, 9, 31, 10), "gris", "plat", 4)
    elif style == "frises":
        z = {(x, y) for (x, y) in ellipse(20, 11, 12.5, 10.5) if y <= 9}
        z |= disque(9, 12, 3) | disque(31, 12, 3)
        t.peindre(z, fam, "sphere", base)
        for (x, y) in list(z):
            if (x + y) % 4 == 0:
                t.px[(x, y)] = "8" if fam == "cheveux" else "G"
    return t.contour()


def barbe(t, style, fam="cheveux", base=1):
    if style == "pleine":
        b = poly([(10, 15), (12, 21), (16, 25), (24, 25), (28, 21), (30, 15), (28, 19), (24, 21), (16, 21), (12, 19)])
    elif style == "longue":
        b = poly([(10, 15), (12, 22), (15, 28), (20, 32), (25, 28), (28, 22), (30, 15), (28, 19), (24, 21), (16, 21), (12, 19)])
    elif style == "fleuve":
        b = poly([(10, 15), (12, 23), (14, 31), (20, 37), (26, 31), (28, 23), (30, 15), (28, 19), (24, 21), (16, 21), (12, 19)])
    elif style == "favoris":
        b = rect(9, 14, 11, 21) | rect(29, 14, 31, 21)
    else:
        return
    t.peindre(b, fam, "sphere", base)
    t.poser({(18, 19), (19, 19), (20, 19), (21, 19)}, "1")


# Objets fétiches, tenus dans la main droite (vers x = 31, y = 37).
def objet(t, nom):
    if nom == "astrolabe":
        t.peindre(disque(32, 35, 5), "or", "sphere", 2)
        t.poser(anneau(32, 35, 3.4, 0.8), "Y")
        t.poser(trait(28, 32, 36, 38), "4")
        t.peindre(disque(32, 29, 1.2), "or", "plat", 1)
    elif nom == "compas":
        t.poser(trait(32, 27, 29, 42) | trait(32, 27, 36, 42), "g")
        t.peindre(disque(32, 27, 1.5), "or", "sphere", 2)
    elif nom == "lentille":
        t.peindre(ellipse(33, 33, 3, 5), "cyan", "sphere", 1)
        t.poser(anneau(33, 33, 3, 0.8, ry=5), "C")
        t.poser({(32, 31)}, "w")
    elif nom == "lunette":
        t.peindre(bande((27, 42), (38, 27), 1.3, 2.0), "bois", "cyl_v", 2)
        t.peindre(bande((36.5, 29), (38.5, 26.3), 2.3), "or", "plat", 2)
    elif nom == "pomme":
        t.peindre(disque(33, 34, 3.6), "rouge", "sphere", 2)
        t.poser({(33, 30), (33, 29)}, "B")
        t.poser({(34, 29), (35, 29)}, "e")
    elif nom == "plume":
        t.peindre(poly([(30, 40), (37, 25), (38, 27), (32, 39)]), "gris", "biseau", 5)
        t.poser(trait(30, 40, 37, 26), "g")
    elif nom == "balance":
        t.poser(trait(33, 26, 33, 41), "Y")
        t.poser(trait(28, 29, 38, 29), "Y")
        t.peindre(ellipse(28.5, 33, 2.4, 1) | ellipse(37.5, 33, 2.4, 1), "or", "plat", 2)
        t.poser(trait(28, 29, 27, 33) | trait(28, 29, 30, 33) | trait(38, 29, 36, 33) | trait(38, 29, 39, 33), "4")
    elif nom == "carnet":
        t.peindre(rect(29, 30, 37, 40), "vert", "biseau", 1)
        t.poser(rect(30, 31, 30, 39), "2")
    elif nom == "carte":
        t.peindre(rect(28, 28, 38, 40), "parchemin", "biseau", 2)
        for x, y in [(30, 30), (33, 30), (36, 31), (30, 33), (35, 34), (32, 36), (30, 38), (36, 38)]:
            t.poser({(x, y)}, "n")
    elif nom == "fiole":
        t.peindre(poly([(32, 27), (34, 27), (34, 31), (37, 38), (29, 38), (32, 31)]), "cyan", "plat", 2)
        t.peindre(poly([(30, 35), (36, 35), (37, 38), (29, 38)]), "vert", "plat", 3)
        t.poser({(28, 33), (38, 33), (33, 25)}, "i")
    elif nom == "craie":
        t.peindre(rect(27, 28, 39, 37), "vert", "plat", 0)
        t.poser(texte("E=", 28, 30) & rect(27, 28, 39, 37), "w")
        t.poser(rect(36, 32, 38, 32), "w")
        t.peindre(rect(26, 27, 39, 27) | rect(26, 38, 39, 38), "bois", "plat", 1)
    elif nom == "ardoise":
        t.peindre(rect(27, 28, 39, 39), "nuit", "plat", 1)
        t.poser(texte("1729", 27, 31, 0) & rect(27, 28, 39, 39), "z")
        t.peindre(rect(26, 27, 39, 27) | rect(26, 40, 39, 40), "bois", "plat", 1)
    elif nom == "photo51":
        t.peindre(rect(27, 27, 39, 39), "nuit", "plat", 0)
        t.poser(trait(29, 29, 37, 37) | trait(37, 29, 29, 37), "z")
        t.poser({(33, 30), (33, 36), (30, 33), (36, 33)}, "l")
    elif nom == "ruban":
        t.peindre(rect(26, 31, 39, 37), "parchemin", "cyl_h", 2)
        for x in range(26, 40, 4):
            t.poser(rect(x, 31, x, 37), "A")
        t.poser(texte("10", 28, 32, 1), "n")
    elif nom == "trajectoire":
        t.peindre(rect(27, 27, 39, 40), "gris", "plat", 5)
        t.poser(courbe([(28, 39), (31, 32), (35, 29), (38, 30)]), "u")
        t.poser(rect(28, 39, 38, 39) | rect(28, 28, 28, 39), "g")
    elif nom == "tableau":
        t.peindre(rect(27, 28, 39, 39), "parchemin", "plat", 2)
        for y in range(29, 39, 2):
            for x in range(28, 39, 2):
                if not (y < 33 and 30 <= x <= 36):
                    t.poser({(x, y)}, "rgbuo"[(x + y) % 5])
    elif nom == "col_cygne":
        t.peindre(disque(32, 36, 4), "cyan", "sphere", 1)
        t.poser(courbe([(32, 32), (32, 28), (35, 26), (38, 29), (38, 32)]), "C")
        t.peindre(ellipse(32, 38, 3.2, 1.5), "orange", "plat", 1)
    elif nom == "bobine":
        t.peindre(rect(28, 30, 37, 39), "cuivre", "cyl_h", 1)
        for y in range(30, 40, 2):
            t.poser(rect(28, y, 37, y), "D")
        t.peindre(rect(27, 29, 38, 29) | rect(27, 40, 38, 40), "bois", "plat", 1)
    elif nom == "lampe":
        t.peindre(ellipse(32, 36, 5, 2.6), "cuivre", "sphere", 2)
        t.poser(trait(37, 35, 39, 32), "m")
        t.peindre(poly([(26, 35), (28, 34), (28, 37)]), "cuivre", "plat", 1)
        t.peindre(poly([(25, 34), (26, 29), (27, 34)]), "orange", "plat", 1)
        t.poser({(26, 32)}, "j")
    # v18 : attributs des savants des arbres qui n'en avaient pas.
    elif nom == "des":
        t.peindre(rect(29, 30, 35, 36), "gris", "biseau", 5)
        t.poser({(30, 31), (32, 33), (34, 35)}, "k")
    elif nom == "loupe":
        t.poser(trait(34, 37, 37, 42, 1), "B")
        t.peindre(disque(32, 33, 4), "cyan", "sphere", 1)
        t.poser(disque(32, 33, 4.6) - disque(32, 33, 3.6), "g")
    elif nom == "livre":
        t.peindre(rect(28, 29, 37, 40), "rouge", "biseau", 1)
        t.poser(rect(29, 30, 29, 39), "1")
        t.poser(rect(31, 32, 35, 32) | rect(31, 34, 34, 34), "y")
    elif nom == "cerveau":
        t.peindre(ellipse(32, 33, 5.5, 4.2), "rose", "sphere", 1)
        t.poser(courbe([(28, 32), (30, 30), (32, 32), (34, 30), (36, 32)]) | courbe([(29, 35), (31, 34), (33, 36), (35, 34)]), "F")
        t.poser(trait(32, 29, 32, 37), "F")
    elif nom == "menottes":
        t.poser(anneau(29.5, 35, 2.6, 1) | anneau(35.5, 35, 2.6, 1), "g")
        t.poser(trait(32, 35, 33, 35), "G")
        t.poser({(28, 33), (34, 33)}, "w")
    elif nom == "thermometre":
        t.peindre(rect(31, 25, 33, 37), "gris", "plat", 5)
        t.peindre(disque(32, 39, 2.2), "rouge", "sphere", 2)
        t.poser(rect(32, 30, 32, 38), "r")
        for y in range(27, 36, 2):
            t.poser({(34, y)}, "G")
    elif nom == "diapason":
        t.poser(trait(32, 41, 32, 36, 2), "G")
        t.poser(trait(30, 36, 30, 27, 1) | trait(34, 36, 34, 27, 1) | trait(30, 36, 34, 36, 1), "g")
        t.poser({(30, 27), (34, 27)}, "z")
    elif nom == "metronome":
        t.peindre(poly([(29, 41), (35, 41), (33.5, 27), (30.5, 27)]), "bois", "biseau", 2)
        t.poser(trait(32, 39, 35, 28), "y")
        t.poser({(34, 31), (34, 32)}, "Y")
    elif nom == "globe":
        t.peindre(disque(32, 33, 5), "bleu", "sphere", 2)
        t.poser({(30, 31), (31, 31), (31, 32), (34, 34), (35, 34), (33, 35), (30, 35)}, "e")
        t.poser(trait(32, 38, 32, 41), "B")
        t.peindre(rect(29, 41, 35, 42), "bois", "plat", 1)
    elif nom == "rouleau":
        t.peindre(rect(29, 28, 36, 40), "parchemin", "plat", 2)
        t.peindre(rect(28, 27, 37, 28) | rect(28, 40, 37, 41), "bois", "cyl_h", 2)
        for y in range(30, 39, 2):
            t.poser(rect(30, y, 35, y), "A")


def portrait(r):
    """Une recette → (couleurs, base, cheveux)."""
    t = toile()
    peindre_corps(t, r["peau"])
    t2 = toile()
    tenue(t2, r["tenue"])
    t.px.update(t2.px)
    if r.get("barbe"):
        b = toile()
        barbe(b, *r["barbe"])
        b.contour()
        t.px.update(b.px)
    o = toile()
    objet(o, r.get("objet") or "aucun")
    o.contour()
    t.px.update(o.px)
    return couleurs_rang(*r["couleurs"]), t.lignes(), coiffure(*r["coiffure"]).lignes()


def main(args):
    if not args:
        print(__doc__)
        return 1
    dossier = RACINE / "packs" / args[0]
    recettes = json.loads((dossier / "portraits.json").read_text(encoding="utf-8"))
    chemin = dossier / "savants.json"
    savants = json.loads(chemin.read_text(encoding="utf-8"))
    par_id = {s["id"]: s for s in savants}
    for r in recettes:
        if r["id"] not in par_id:
            sys.exit(f"portraits.json : aucun savant « {r['id']} » dans savants.json")
        par_id[r["id"]]["couleurs"], par_id[r["id"]]["base"], par_id[r["id"]]["cheveux"] = portrait(r)
    chemin.write_text(json.dumps(savants, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(recettes)} portraits dessinés dans {chemin.relative_to(RACINE)}")
    if len(args) > 1:
        from PIL import Image
        from dessin import PALETTE
        planche = Image.new("RGB", (len(recettes) * 210, 270), (243, 233, 210))
        for i, r in enumerate(recettes):
            s = par_id[r["id"]]
            pal = dict(PALETTE, **s["couleurs"])
            for calque in (s["base"], s["cheveux"]):
                for y, l in enumerate(calque):
                    for x, ch in enumerate(l):
                        if ch != ".":
                            planche.paste(pal.get(ch, "#FF00FF"), (i * 210 + 5 + x * 5, 15 + y * 5, i * 210 + 10 + x * 5, 20 + y * 5))
        planche.save(args[1])
        print(f"aperçu : {args[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
