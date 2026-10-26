"""Petit atelier de pixel art : on dessine par formes (rectangle, disque, polygone, trait),
chaque forme reçoit une famille de couleurs et un modelé (biseau, sphère, cylindre), puis on
ajoute un contour sombre autour de la silhouette.

Le résultat reste le format texte du jeu : une liste de lignes, un caractère par pixel,
« . » pour le transparent. La lumière vient du haut à gauche, comme partout dans le jeu.
"""
import math

# Familles de couleurs, de la plus sombre à la plus claire. Chaque teinte a son caractère.
# X, Z, Q et ! * ~ + sont réservés aux couleurs des tenues (une par rang), voir pixels.py.
FAMILLES = {
    "contour": [("k", "#1E1A2B")],
    "gris": [("n", "#2B2B33"), ("G", "#5D6470"), ("g", "#9AA0A8"), ("z", "#C9CED6"), ("l", "#E8E8EE"), ("w", "#FFFFFF")],
    "or": [("4", "#7A5418"), ("Y", "#B8862B"), ("y", "#F2C14E"), ("j", "#FFE79A")],
    "bois": [("H", "#3E2614"), ("B", "#5E3B1C"), ("b", "#9A6534"), ("t", "#C99260")],
    "rouge": [("1", "#5E1414"), ("R", "#8E2424"), ("r", "#D94141"), ("f", "#F28B82")],
    "orange": [("O", "#A95A1F"), ("o", "#E8873A"), ("a", "#F7B77A")],
    "vert": [("2", "#1B4D20"), ("E", "#2E7D32"), ("e", "#4CAF50"), ("i", "#A5DC8F")],
    "cyan": [("C", "#2A6F99"), ("c", "#8FD8F2"), ("d", "#D8F4FC")],
    "bleu": [("3", "#1A2C66"), ("U", "#24408F"), ("u", "#3D63D9"), ("x", "#93AAF2")],
    "violet": [("5", "#3B1A5C"), ("P", "#5E2F8A"), ("p", "#9B59D0"), ("q", "#CDA6EE")],
    "peau": [("6", "#9C5E3E"), ("S", "#D9A07A"), ("s", "#F2C9A0"), ("7", "#FBE3C8")],
    "cheveux": [("8", "#2A1A0E"), ("h", "#6B4226"), ("9", "#9C6B43")],
    "parchemin": [("A", "#A8905E"), ("V", "#D8C49A"), ("v", "#F7EBD0")],
    "cuivre": [("D", "#7A3E1E"), ("m", "#B5623B"), ("M", "#E39A6B")],
    "rose": [("F", "#B5476B"), ("I", "#F28FB0")],
    "nuit": [("N", "#141A33"), ("K", "#2C3559")],
    "ivoire": [("T", "#E8DFC8")],
}
PALETTE = {ch: hexa for fam in FAMILLES.values() for ch, hexa in fam}

# Emplacements de couleur des tenues de l'avatar : la teinte réelle dépend du rang (voir avatar40.py).
FAMILLES_TENUE = {
    "tenue": [("!", ""), ("X", ""), ("*", "")],
    "bas": [("~", ""), ("Z", "")],
    "detail": [("+", ""), ("Q", "")],
}
EMPLACEMENTS = "".join(ch for fam in FAMILLES_TENUE.values() for ch, _ in fam)
assert len(PALETTE) == sum(len(f) for f in FAMILLES.values()), "caractère de palette en double"

LUMIERE = (-0.48, -0.58, 0.66)
_n = math.sqrt(sum(c * c for c in LUMIERE))
LUMIERE = tuple(c / _n for c in LUMIERE)
BAYER = [[0.0, 0.5], [0.75, 0.25]]


def teintes(fam):
    return [ch for ch, _ in (FAMILLES.get(fam) or FAMILLES_TENUE[fam])]


# --- Ensembles de pixels -------------------------------------------------------

def rect(x0, y0, x1, y1):
    return {(x, y) for x in range(min(x0, x1), max(x0, x1) + 1) for y in range(min(y0, y1), max(y0, y1) + 1)}


def ellipse(cx, cy, rx, ry):
    """Pixels dont le centre tombe dans l'ellipse. cx, cy en coordonnées de pixels (x + 0,5 = centre)."""
    out = set()
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                out.add((x, y))
    return out


def disque(cx, cy, r):
    return ellipse(cx, cy, r, r)


def anneau(cx, cy, r, ep=1.0, ry=None):
    ry = ry or r
    return ellipse(cx, cy, r, ry) - ellipse(cx, cy, r - ep, ry - ep)


def poly(points):
    """Polygone plein (règle pair-impair, au centre des pixels)."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    out = set()
    for y in range(int(min(ys)) - 1, int(max(ys)) + 2):
        for x in range(int(min(xs)) - 1, int(max(xs)) + 2):
            px, py, dedans = x + 0.5, y + 0.5, False
            for i in range(len(points)):
                (x1, y1), (x2, y2) = points[i], points[i - 1]
                if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1:
                    dedans = not dedans
            if dedans:
                out.add((x, y))
    return out


def trait(x0, y0, x1, y1, ep=1):
    """Segment épais (Bresenham élargi)."""
    out = set()
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(int(n * 2) + 1):
        f = i / (n * 2)
        x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        if ep <= 1:
            out.add((int(round(x)), int(round(y))))
        else:
            out |= disque(x + 0.5, y + 0.5, ep / 2)
    return out


def courbe(points, ep=1):
    out = set()
    for a, b in zip(points, points[1:]):
        out |= trait(a[0], a[1], b[0], b[1], ep)
    return out


def arc(cx, cy, r, a0, a1, ep=1):
    """Arc de cercle entre deux angles en degrés (0 = droite, 90 = bas)."""
    pts = []
    n = max(8, int(abs(a1 - a0) / 6))
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return courbe(pts, ep)


def decaler(pixels, dx, dy):
    return {(x + dx, y + dy) for x, y in pixels}


def miroir(pixels, largeur):
    return {(largeur - 1 - x, y) for x, y in pixels}


# --- Toile ----------------------------------------------------------------------

class Toile:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = {}

    def dans(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def poser(self, pixels, ch):
        for x, y in pixels:
            if self.dans(x, y):
                self.px[(x, y)] = ch
        return self

    def effacer(self, pixels):
        for p in pixels:
            self.px.pop(p, None)
        return self

    def peindre(self, pixels, fam, modele="biseau", base=None, contour=False, mini=0, maxi=99):
        """Peint un ensemble de pixels avec une famille de couleurs.

        modele : « plat » (une teinte), « biseau » (bord haut-gauche clair, bas-droit sombre),
        « sphere », « cyl_v » ou « cyl_h » (modelé selon la lumière, avec un léger tramage).
        base : indice de la teinte moyenne dans la famille. contour : trait sombre sur le bord de la forme.
        """
        t = teintes(fam)
        if base is None:
            base = min(len(t) - 1, max(0, (len(t) - 1) // 2 + (1 if len(t) >= 4 else 0)))
        pixels = {p for p in pixels if self.dans(*p)}
        if not pixels:
            return self
        xs = [p[0] for p in pixels]
        ys = [p[1] for p in pixels]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        cx, cy = (x0 + x1 + 1) / 2, (y0 + y1 + 1) / 2
        rx, ry = max(0.5, (x1 - x0 + 1) / 2), max(0.5, (y1 - y0 + 1) / 2)
        for (x, y) in pixels:
            if modele == "plat":
                i = base
            elif modele == "biseau":
                haut = (x, y - 1) not in pixels or (x - 1, y) not in pixels
                bas = (x, y + 1) not in pixels or (x + 1, y) not in pixels
                i = base + 1 if haut and not bas else base - 1 if bas and not haut else base
            else:
                u = (x + 0.5 - cx) / rx
                v = (y + 0.5 - cy) / ry
                if modele == "cyl_v":
                    v = 0.0
                elif modele == "cyl_h":
                    u = 0.0
                d = min(1.0, u * u + v * v)
                n = (u, v, math.sqrt(1 - d))
                intensite = sum(a * b for a, b in zip(n, LUMIERE))
                niveau = (intensite + 0.35) / 1.35 * (len(t) - 0.01) + BAYER[y % 2][x % 2] * 0.6 - 0.3
                i = int(niveau)
            self.px[(x, y)] = t[max(mini, min(len(t) - 1, maxi, i))]
        if contour:
            for (x, y) in pixels:
                if any((x + dx, y + dy) not in pixels for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    self.px[(x, y)] = "k"
        return self

    def contour(self, ch="k", diagonales=False):
        """Trace un contour autour de tout ce qui est dessiné."""
        voisins = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if diagonales:
            voisins += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        ajout = set()
        for (x, y) in self.px:
            for dx, dy in voisins:
                q = (x + dx, y + dy)
                if q not in self.px and self.dans(*q):
                    ajout.add(q)
        for q in ajout:
            self.px[q] = ch
        return self

    def lignes(self):
        return ["".join(self.px.get((x, y), ".") for x in range(self.w)) for y in range(self.h)]


def depuis_lignes(lignes):
    t = Toile(len(lignes[0]), len(lignes))
    for y, l in enumerate(lignes):
        for x, ch in enumerate(l):
            if ch != ".":
                t.px[(x, y)] = ch
    return t


def apercu(images, chemin, palette=None, echelle=6, colonnes=8, fond=(243, 233, 210), extra=None):
    """Planche PNG pour vérifier les dessins à l'œil."""
    from PIL import Image, ImageDraw
    palette = dict(palette or PALETTE)
    palette.update(extra or {})
    noms = list(images)
    w = max(len(images[n][0]) for n in noms)
    h = max(len(images[n]) for n in noms)
    cw, ch = w * echelle + 12, h * echelle + 22
    lig = (len(noms) + colonnes - 1) // colonnes
    im = Image.new("RGB", (cw * colonnes, ch * lig), fond)
    d = ImageDraw.Draw(im)
    for i, n in enumerate(noms):
        ox, oy = (i % colonnes) * cw + 6, (i // colonnes) * ch + 4
        for y, l in enumerate(images[n]):
            for x, c in enumerate(l):
                if c != ".":
                    hexa = palette.get(c, "#FF00FF")
                    d.rectangle([ox + x * echelle, oy + y * echelle, ox + (x + 1) * echelle - 1, oy + (y + 1) * echelle - 1], fill=hexa)
        d.text((ox, oy + h * echelle + 4), n[:20], fill=(40, 40, 40))
    im.save(chemin)


# --- Compléments : tubes obliques, ellipses tournées, petite police -----------------

def peindre_tube(toile, pixels, fam, a, b, rayon, base=None):
    """Modelé de cylindre le long d'un axe quelconque a → b (pour une lunette posée en biais)."""
    t = teintes(fam)
    if base is None:
        base = len(t) // 2
    ax, ay = b[0] - a[0], b[1] - a[1]
    L = math.hypot(ax, ay) or 1
    nx, ny = -ay / L, ax / L
    for (x, y) in pixels:
        if not toile.dans(x, y):
            continue
        u = ((x + 0.5 - a[0]) * nx + (y + 0.5 - a[1]) * ny) / rayon
        u = max(-1.0, min(1.0, u))
        n = (u * nx, u * ny, math.sqrt(1 - u * u))
        intensite = sum(p * q for p, q in zip(n, LUMIERE))
        niveau = (intensite + 0.35) / 1.35 * (len(t) - 0.01) + BAYER[y % 2][x % 2] * 0.6 - 0.3
        toile.px[(x, y)] = t[max(0, min(len(t) - 1, int(niveau)))]
    return toile


def bande(a, b, demi_largeur_a, demi_largeur_b=None):
    """Quadrilatère autour du segment a → b (un tube, une lame, un manche)."""
    demi_largeur_b = demi_largeur_a if demi_largeur_b is None else demi_largeur_b
    ax, ay = b[0] - a[0], b[1] - a[1]
    L = math.hypot(ax, ay) or 1
    nx, ny = -ay / L, ax / L
    return poly([(a[0] + nx * demi_largeur_a, a[1] + ny * demi_largeur_a), (b[0] + nx * demi_largeur_b, b[1] + ny * demi_largeur_b),
                 (b[0] - nx * demi_largeur_b, b[1] - ny * demi_largeur_b), (a[0] - nx * demi_largeur_a, a[1] - ny * demi_largeur_a)])


def ellipse_tournee(cx, cy, rx, ry, angle, ep=1.0):
    """Contour d'une ellipse tournée de `angle` degrés."""
    th = math.radians(angle)
    pts = []
    for i in range(73):
        s = 2 * math.pi * i / 72
        x, y = rx * math.cos(s), ry * math.sin(s)
        pts.append((cx + x * math.cos(th) - y * math.sin(th), cy + x * math.sin(th) + y * math.cos(th)))
    return courbe(pts, ep)


POLICE = {
    "0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"], "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "011", "001", "111"], "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "010", "010", "010"], "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "111"], "+": ["000", "010", "111", "010", "000"], "=": ["000", "111", "000", "111", "000"],
    "A": ["010", "101", "111", "101", "101"], "B": ["110", "101", "110", "101", "110"], "C": ["011", "100", "100", "100", "011"],
    "D": ["110", "101", "101", "101", "110"], "E": ["111", "100", "110", "100", "111"], "F": ["111", "100", "110", "100", "100"],
    "I": ["111", "010", "010", "010", "111"], "K": ["101", "101", "110", "101", "101"], "M": ["101", "111", "111", "101", "101"],
    "O": ["010", "101", "101", "101", "010"], "R": ["110", "101", "110", "101", "101"], "U": ["101", "101", "101", "101", "111"],
    "V": ["101", "101", "101", "101", "010"], "X": ["101", "101", "010", "101", "101"], "Z": ["111", "001", "010", "100", "111"],
    "!": ["010", "010", "010", "000", "010"], "?": ["111", "001", "010", "000", "010"], "@": ["111", "101", "111", "100", "111"],
    " ": ["000", "000", "000", "000", "000"], "-": ["000", "000", "111", "000", "000"], ".": ["000", "000", "000", "000", "010"],
    "^": ["010", "101", "000", "000", "000"], "v": ["000", "000", "000", "101", "010"], "x": ["000", "101", "010", "101", "000"],
}


def texte(chaine, x, y, espace=1):
    """Pixels d'un texte en police 3 × 5."""
    out = set()
    for i, c in enumerate(chaine):
        g = POLICE[c]
        for dy, l in enumerate(g):
            for dx, b in enumerate(l):
                if b == "1":
                    out.add((x + i * (3 + espace) + dx, y + dy))
    return out
