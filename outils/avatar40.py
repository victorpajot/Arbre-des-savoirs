"""Avatar du joueur en 40 × 48 : corps, tenue du rang, cheveux, accessoires de tête et de visage.

Les calques se superposent dans cet ordre : corps, tenue, cheveux (ou accessoire de tête), visage, tête.
Dans les tenues, les caractères ! X * (vêtement), ~ Z (bas) et + Q (détails) prennent les couleurs du rang.
"""
from dessin import (FAMILLES_TENUE, Toile, anneau, arc, bande, courbe, disque, ellipse, miroir, poly,
                    rect, trait)

L, H = 40, 48


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


# --- Corps -------------------------------------------------------------------------

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


def tenue_etudiant():
    t = toile()
    silhouette(t)
    t.peindre(ellipse(20, 24.5, 6.5, 2.2), "tenue", "plat", 0)
    t.peindre(rect(14, 32, 25, 35), "tenue", "plat", 0)
    t.peindre(rect(15, 33, 24, 34), "tenue", "plat", 1)
    t.contour()
    t.poser(rect(17, 26, 17, 29) | rect(22, 26, 22, 29), "Q")
    t.poser({(17, 30), (22, 30)}, "+")
    t.poser(rect(23, 27, 25, 29), "Q")
    return t


def blouse(t, interieur):
    """Blouse ouverte sur un vêtement intérieur (une famille et sa teinte)."""
    t.peindre(poly([(17, 24), (23, 24), (22.5, 39), (17.5, 39)]), interieur[0], "plat", interieur[1])
    t.poser(trait(17, 24, 17.5, 39) | trait(22, 24, 22.5, 39), "!")
    t.poser(trait(16, 24, 18, 29) | trait(24, 24, 22, 29), "!")


def tenue_assistant():
    t = toile()
    silhouette(t)
    blouse(t, ("bleu", 2))
    t.poser(rect(12, 29, 15, 29) | rect(12, 29, 12, 31) | rect(15, 29, 15, 31), "!")
    t.contour()
    t.poser({(13, 27), (13, 28)}, "r")
    t.poser({(14, 26), (14, 27), (14, 28)}, "Q")
    return t


def tenue_chercheur():
    t = toile()
    silhouette(t)
    blouse(t, ("bleu", 3))
    t.poser(poly([(19, 24.5), (21, 24.5), (21.5, 33), (20, 35), (18.5, 33)]), "Q")
    t.poser({(19, 25), (20, 25), (20, 26)}, "+")
    t.contour()
    t.poser(rect(24, 29, 26, 31), "y")
    t.poser({(25, 30)}, "u")
    return t


def tenue_professeur():
    t = toile()
    silhouette(t)
    t.peindre(poly([(17, 24), (23, 24), (22.5, 38), (17.5, 38)]), "detail", "plat", 1)
    t.poser({(x, y) for x in range(9, 31) for y in range(24, 40) if (x * 3 + y * 5) % 7 == 0 and t.px.get((x, y)) == "X"}, "!")
    t.poser(trait(17, 24, 18, 37) | trait(23, 24, 22, 37), "!")
    t.peindre(ellipse(8.6, 32, 1.6, 2.2) | ellipse(31.4, 32, 1.6, 2.2), "detail", "plat", 0)
    t.contour()
    t.poser({(17, 25), (18, 26), (17, 27), (23, 25), (22, 26), (23, 27), (19, 26), (20, 26), (21, 26)}, "r")
    t.poser({(18, 25), (18, 27), (22, 25), (22, 27)}, "R")
    t.poser({(20, 30), (20, 33), (20, 36)}, "+")
    return t


def tenue_academicien():
    t = toile()
    silhouette(t)
    t.peindre(poly([(18, 24), (22, 24), (21.5, 30), (18.5, 30)]), "gris", "plat", 5)
    for x0, sens in ((13, 1), (27, -1)):
        tige = courbe([(x0, 26), (x0 + sens, 30), (x0 + sens * 2, 35)])
        t.poser(tige, "+")
        for y in (27, 30, 33):
            t.poser({(x0 + sens * (1 + (y - 26) // 4) - sens, y), (x0 + sens * (1 + (y - 26) // 4) + sens, y + 1)}, "Q")
    t.poser(rect(7, 34, 10, 34) | rect(30, 34, 33, 34), "Q")
    t.poser(rect(10, 38, 30, 38), "Q")
    t.contour()
    t.poser(trait(28, 36, 33, 44), "y")
    t.poser({(27, 36), (29, 35)}, "Y")
    return t


# --- Cheveux et accessoires ------------------------------------------------------------

def zone_cheveux():
    out = set()
    for (x, y) in ellipse(20, 12, 12, 10.6):
        frange = 8 + ((x // 3) % 2) * 2
        if y <= frange or ((x <= 10 or x >= 29) and y <= 16):
            out.add((x, y))
    return out


def cheveux():
    t = toile()
    t.peindre(zone_cheveux(), "cheveux", "sphere", 1)
    return t.contour()


def coiffure_einstein():
    t = toile()
    nuage = set()
    for cx, cy, r in [(12, 8, 5), (20, 6, 5.5), (28, 8, 5), (9, 14, 4), (31, 14, 4), (15, 5, 4), (25, 5, 4), (8, 19, 2.6), (32, 19, 2.6)]:
        nuage |= disque(cx, cy, r)
    nuage -= {(x, y) for (x, y) in ellipse(20, 16, 9.4, 8.2) if y >= 10}
    t.peindre(nuage, "gris", "sphere", 4, mini=2)
    return t.contour()


def perruque_poudree():
    t = toile()
    p = {(x, y) for (x, y) in ellipse(20, 11, 12, 10) if y <= 8}
    for y in range(9, 32, 3):
        p |= disque(9.5, y, 2.8) | disque(30.5, y, 2.8)
    t.peindre(p, "gris", "sphere", 4)
    for y in range(10, 31, 3):
        t.poser({(9, y), (30, y)}, "z")
    return t.contour()


def frange_sous(t, y_max):
    t.peindre({(x, y) for (x, y) in zone_cheveux() if y >= y_max - 1}, "cheveux", "plat", 1)


def chapeau_alu():
    t = toile()
    frange_sous(t, 9)
    import random
    r = random.Random(3)
    cone = poly([(20, -1), (31, 10), (9, 10)]) | rect(8, 9, 32, 11)
    for p in cone:
        t.poser({p}, r.choice("wllzzg"))
    t.poser(trait(20, 0, 16, 9) | trait(20, 0, 25, 9), "g")
    return t.contour()


def haut_de_forme():
    t = toile()
    frange_sous(t, 9)
    t.peindre(rect(13, 0, 27, 8), "gris", "cyl_v", 0, maxi=1)
    t.peindre(rect(13, 6, 27, 7), "rouge", "cyl_v", maxi=2)
    t.peindre(ellipse(20, 9, 13, 2.2), "gris", "plat", 0)
    return t.contour()


def laurier():
    t = cheveux()
    import math
    for i in range(13):
        a = math.radians(200 + i * 11.5)
        x, y = 20 + 11.5 * math.cos(a), 11 + 6 * math.sin(a)
        t.poser({(int(x), int(y)), (int(x) + 1, int(y))}, "e" if i % 2 else "E")
        t.poser({(int(x), int(y) - 1)}, "i")
    return t


def bonnet_de_nuit():
    t = toile()
    frange_sous(t, 9)
    bonnet = poly([(8.5, 10), (31.5, 10), (31, 6), (35, 12), (37, 17), (34, 13), (27, 1), (16, 0.5), (9, 5)])
    t.peindre(bonnet, "bleu", "biseau", 2)
    for p in bonnet:
        if p[1] % 3 == 0:
            t.px[p] = "x"
    t.peindre(rect(8, 9, 32, 11), "gris", "biseau", 4)
    t.peindre(disque(36.5, 18, 2.2), "or", "sphere")
    return t.contour()


def lunettes_rondes():
    t = toile()
    t.poser(anneau(14.5, 14, 3.4, 1) | anneau(24.5, 14, 3.4, 1) | rect(18, 13, 21, 13) | rect(8, 13, 11, 13) | rect(28, 13, 31, 13), "n")
    t.poser({(13, 12), (23, 12)}, "d")
    return t


def besicles_franklin():
    t = toile()
    cadre = (rect(12, 14, 17, 17) - rect(13, 15, 16, 16)) | (rect(22, 14, 27, 17) - rect(23, 15, 26, 16))
    t.poser(cadre | rect(18, 15, 21, 15) | rect(8, 14, 11, 14) | rect(28, 14, 31, 14), "Y")
    t.poser({(13, 15), (23, 15)}, "d")
    return t


def lunettes_protection():
    t = toile()
    t.poser(rect(8, 12, 32, 14), "n")
    t.peindre(rect(11, 10, 18, 17) | rect(21, 10, 28, 17), "cyan", "biseau", 1, contour=True)
    t.poser(rect(14, 13, 15, 15) | rect(24, 13, 25, 15), "C")
    t.poser({(12, 11), (22, 11)}, "d")
    return t


def monocle():
    t = toile()
    t.poser(anneau(24.5, 14, 3.6, 1.1), "y")
    t.poser({(26 + i // 2, 18 + i) for i in range(0, 10, 2)}, "Y")
    t.poser({(22, 12)}, "j")
    return t


def moustache():
    t = toile()
    m = poly([(20, 16.8), (23, 17.2), (26, 17.6), (27.6, 16.2), (27.4, 18.4), (24, 18.9), (20, 18.3)])
    m |= miroir(m, L)
    t.peindre(m, "cheveux", "biseau", 1)
    return t.contour()


TENUES = {
    "etudiant": tenue_etudiant, "assistant": tenue_assistant, "chercheur": tenue_chercheur,
    "professeur": tenue_professeur, "academicien": tenue_academicien,
}

RANGS = [
    {"id": "etudiant", "nom": "Étudiant", "niveau_min": 0, "couleurs": couleurs_rang("#3D63D9", "#2F3B59", "#F2C14E")},
    {"id": "assistant", "nom": "Assistant", "niveau_min": 5, "couleurs": couleurs_rang("#EEF0F4", "#2F3B59", "#3D63D9")},
    {"id": "chercheur", "nom": "Chercheur", "niveau_min": 15, "couleurs": couleurs_rang("#EEF0F4", "#5D6470", "#D94141")},
    {"id": "professeur", "nom": "Professeur", "niveau_min": 30, "couleurs": couleurs_rang("#7A5230", "#3B3B3B", "#E8DDC0")},
    {"id": "academicien", "nom": "Membre de l'Académie", "niveau_min": 50, "couleurs": couleurs_rang("#2E6B3F", "#1E1E24", "#F2C14E")},
]

ACCESSOIRES = {
    "coiffure-einstein": ("tete", coiffure_einstein), "perruque-poudree": ("tete", perruque_poudree),
    "chapeau-alu": ("tete", chapeau_alu), "haut-de-forme": ("tete", haut_de_forme), "laurier": ("tete", laurier),
    "bonnet-de-nuit": ("tete", bonnet_de_nuit), "lunettes-rondes": ("visage", lunettes_rondes),
    "besicles-franklin": ("visage", besicles_franklin), "lunettes-protection": ("visage", lunettes_protection),
    "monocle": ("visage", monocle), "moustache": ("visage", moustache),
}


def calques():
    return {
        "corps": corps().lignes(),
        "cheveux": cheveux().lignes(),
        "tenues": {r["id"]: TENUES[r["id"]]().lignes() for r in RANGS},
        "accessoires": {k: (v[0], v[1]().lignes()) for k, v in ACCESSOIRES.items()},
    }


def composer(c, rang, tete=None, visage=None):
    """Superpose les calques (pour l'aperçu)."""
    sortie = [list(l) for l in c["corps"]]
    couches = [c["tenues"][rang["id"]]]
    couches.append(c["accessoires"][tete][1] if tete else c["cheveux"])
    if visage:
        couches.append(c["accessoires"][visage][1])
    for couche in couches:
        for y, l in enumerate(couche):
            for x, ch in enumerate(l):
                if ch != ".":
                    sortie[y][x] = ch
    return ["".join(l) for l in sortie]


if __name__ == "__main__":
    import sys
    from dessin import apercu
    c = calques()
    images = {}
    for r in RANGS:
        images[r["id"]] = (composer(c, r), r["couleurs"])
    for k, (place, _) in ACCESSOIRES.items():
        images[k] = (composer(c, RANGS[2], k if place == "tete" else None, k if place == "visage" else None), RANGS[2]["couleurs"])
    # Les couleurs de rang diffèrent par image : on rend chaque image avec sa palette.
    from PIL import Image
    parts = []
    for nom, (img, coul) in images.items():
        apercu({nom: img}, "/tmp/_a.png", extra=coul, colonnes=1, echelle=5)
        parts.append(Image.open("/tmp/_a.png").copy())
    w, h = parts[0].size
    planche = Image.new("RGB", (w * 8, h * 2), (243, 233, 210))
    for i, p in enumerate(parts):
        planche.paste(p, ((i % 8) * w, (i // 8) * h))
    planche.save(sys.argv[1])
