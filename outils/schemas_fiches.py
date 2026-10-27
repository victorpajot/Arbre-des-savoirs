"""v12 : petits gabarits de schémas pour les fiches de révision du mur de la honte.

Mêmes classes que illustrations.py (t, tm, l, lm, f, f2, a, al, ok, ko, jaune) : le schéma suit le thème de la page.
Les libellés passent à la ligne avec « | ».
"""
import math

from illustrations import svg, texte


def _lignes(x, y, s, cls="t", taille=12, poids=None, interligne=14):
    morceaux = s.split("|")
    y0 = y - (len(morceaux) - 1) * interligne / 2
    return "".join(texte(x, round(y0 + i * interligne + taille * 0.35, 1), m, cls, taille, "middle", poids) for i, m in enumerate(morceaux))


def fleche(x1, y1, x2, y2, cls="al"):
    a = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - 7 * math.cos(a - 0.5), y2 - 7 * math.sin(a - 0.5))
    p2 = (x2 - 7 * math.cos(a + 0.5), y2 - 7 * math.sin(a + 0.5))
    return (f'<line class="{cls}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke-width="2"/>'
            f'<path class="{cls}" d="M{p1[0]:.1f} {p1[1]:.1f} L{x2:.1f} {y2:.1f} L{p2[0]:.1f} {p2[1]:.1f}" stroke-width="2"/>')


def chaine(etapes, titre, accent=None, legende=None):
    """Boîtes reliées par des flèches, de gauche à droite (2 à 4 étapes)."""
    n = len(etapes)
    L = 340 + max(0, n - 3) * 90
    gap = 22
    w = (L - 20 - gap * (n - 1)) / n
    c = ""
    for i, e in enumerate(etapes):
        x = 10 + i * (w + gap)
        cls = "a" if accent == i else "f"
        c += f'<rect class="{cls}" x="{x:.1f}" y="20" width="{w:.1f}" height="64" rx="8"' + (' opacity="0.35"' if cls == "a" else "") + "/>"
        c += _lignes(x + w / 2, 52, e, "t", 12, 700)
        if i < n - 1:
            c += fleche(x + w + 3, 52, x + w + gap - 3, 52)
    h = 96
    if legende:
        c += texte(L / 2, 112, legende, "tm", 12)
        h = 122
    return svg(L, h, c, titre)


def cycle(etapes, titre, centre=""):
    n, cx, cy, rx, ry, bw = len(etapes), 170, 105, 112, 76, 96
    c = f'<ellipse class="lm" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke-dasharray="4 5"/>'
    if centre:
        c += _lignes(cx, cy, centre, "tm", 12)
    def pt(a):
        return cx + rx * math.cos(a), cy + ry * math.sin(a)
    pts = [pt(-math.pi / 2 + 2 * math.pi * i / n) for i in range(n)]
    for i in range(n):
        a1 = -math.pi / 2 + 2 * math.pi * (i + 0.5) / n
        (x0, y0), (x1, y1) = pt(a1 - 0.14), pt(a1 + 0.14)
        c += fleche(x0, y0, x1, y1)
    for (x, y), e in zip(pts, etapes):
        c += f'<rect class="f" x="{x - bw / 2:.1f}" y="{y - 17:.1f}" width="{bw}" height="34" rx="17"/>' + _lignes(x, y, e, "t", 11, 700, 12)
    return svg(340, 210, c, titre)


def echelle(points, titre, gauche="", droite=""):
    """Axe horizontal, repères étiquetés en alternance dessus et dessous. points : [(position 0-1, libellé, accent)]."""
    c = '<line class="l" x1="16" y1="60" x2="324" y2="60"/>' + fleche(300, 60, 326, 60, "l")
    # Repères rangés dans l'ordre et espacés régulièrement : un schéma de révision, pas une échelle exacte.
    points = sorted(points, key=lambda p: p[0])
    n = len(points)
    for i, p in enumerate(points):
        lab = p[1]
        acc = len(p) > 2 and p[2]
        x = 34 + i * (272 / max(1, n - 1))
        c += f'<circle class="{"a" if acc else "f"}" cx="{x:.1f}" cy="60" r="5"/>'
        c += _lignes(x, 34 if i % 2 == 0 else 88, lab, "t" if acc else "tm", 11, 700 if acc else None, 12)
    if gauche:
        c += texte(16, 118, gauche, "tm", 11, "start")
    if droite:
        c += texte(324, 118, droite, "tm", 11, "end")
    return svg(340, 124, c, titre)


def barres(valeurs, titre, unite="", maxi=None):
    """valeurs : [(libellé, nombre, accent)]."""
    n = len(valeurs)
    m = maxi or max(v[1] for v in valeurs)
    w = 260 / n
    c = '<line class="lm" x1="30" y1="130" x2="320" y2="130"/>'
    for i, v in enumerate(valeurs):
        lab, val = v[0], v[1]
        acc = len(v) > 2 and v[2]
        h = 100 * val / m
        x = 40 + i * w
        c += f'<rect class="{"a" if acc else "f2"}" x="{x + 6:.1f}" y="{130 - h:.1f}" width="{w - 12:.1f}" height="{h:.1f}" rx="3"/>'
        c += texte(x + w / 2, 124 - h, f"{val:g}".replace(".", ",") + unite, "t", 11, "middle", 700)
        c += _lignes(x + w / 2, 148, lab, "tm", 11, None, 12)
    return svg(340, 168, c, titre)


def triangle(sommets, titre, centre=""):
    (a, b, c3) = sommets
    pts = [(170, 22), (72, 160), (268, 160)]
    c = f'<polygon class="f2" points="{" ".join(f"{x},{y}" for x, y in pts)}"/>'
    if centre:
        c += _lignes(170, 112, centre, "tm", 12)
    for (x, y), s in zip(pts, (a, b, c3)):
        c += f'<rect class="f" x="{x - 60}" y="{y - 17}" width="120" height="34" rx="17"/>' + _lignes(x, y, s, "t", 12, 700)
    return svg(340, 184, c, titre)


def tableau(entetes, lignes, titre, accent=None):
    """Petit tableau ; accent : (ligne, colonne) mise en valeur, ou numéro de ligne."""
    nc = len(entetes)
    w = 320 / nc
    hl = 26
    c = ""
    for j, e in enumerate(entetes):
        c += texte(10 + j * w + w / 2, 22, e, "t", 12, "middle", 700)
    c += '<line class="l" x1="10" y1="32" x2="330" y2="32"/>'
    for i, l in enumerate(lignes):
        y = 36 + i * hl
        if accent == i:
            c += f'<rect class="a" x="10" y="{y}" width="320" height="{hl - 2}" rx="4" opacity="0.25"/>'
        for j, v in enumerate(l):
            c += texte(10 + j * w + w / 2, y + 17, v, "t" if j == 0 else "tm", 12, "middle", 700 if j == 0 else None)
    return svg(340, 44 + len(lignes) * hl, c, titre)


def courbe(d, titre, x_lab="", y_lab="", notes=()):
    """Repère et courbe (chemin SVG dans le cadre 40-320 × 20-150). notes : [(x, y, texte, accent)]."""
    c = '<polyline class="l" points="40,16 40,150 324,150"/>'
    c += f'<path class="al" d="{d}" fill="none" stroke-width="3"/>'
    for n in notes:
        x, y, s = n[0], n[1], n[2]
        acc = len(n) > 3 and n[3]
        if acc:
            c += f'<circle class="a" cx="{x}" cy="{y}" r="4"/>'
            c += _lignes(x, y - 16, s, "t", 11, 700, 12)
        else:
            c += _lignes(x, y, s, "tm", 11, None, 12)
    if y_lab:
        c += texte(46, 14, y_lab, "tm", 11, "start")
    if x_lab:
        c += texte(322, 166, x_lab, "tm", 11, "end")
    return svg(340, 172, c, titre)


def deux_colonnes(gauche, droite, titre, tg="", td=""):
    """Comparaison : deux colonnes de libellés."""
    n = max(len(gauche), len(droite))
    c = ""
    if tg:
        c += texte(90, 20, tg, "t", 13, "middle", 700)
    if td:
        c += texte(250, 20, td, "t", 13, "middle", 700)
    c += '<line class="lm" x1="170" y1="8" x2="170" y2="' + str(36 + n * 32) + '"/>'
    for i, s in enumerate(gauche):
        c += f'<rect class="f2" x="14" y="{32 + i * 32}" width="148" height="26" rx="6"/>' + _lignes(88, 45 + i * 32, s, "t", 11)
    for i, s in enumerate(droite):
        c += f'<rect class="f" x="178" y="{32 + i * 32}" width="148" height="26" rx="6"/>' + _lignes(252, 45 + i * 32, s, "t", 11)
    return svg(340, 44 + n * 32, c, titre)


def cercles(ensembles, titre):
    """Diagramme de Venn à deux ensembles : (gauche, intersection, droite)."""
    g, i, d = ensembles
    c = ('<circle class="f2" cx="125" cy="85" r="68"/><circle class="a" cx="215" cy="85" r="68" opacity="0.25"/>'
         '<circle class="lm" cx="125" cy="85" r="68" fill="none"/>')
    c += _lignes(95, 85, g, "t", 12, 700) + _lignes(170, 85, i, "t", 11) + _lignes(248, 85, d, "t", 12, 700)
    return svg(340, 170, c, titre)


def cartes_wason():
    """La tâche de Wason, résolue : E et 7 sont les deux cartes à retourner."""
    c = ""
    for i, (s, bon) in enumerate([("E", True), ("K", False), ("4", False), ("7", True)]):
        x = 16 + i * 80
        c += f'<rect class="{"a" if bon else "f"}" x="{x}" y="12" width="64" height="88" rx="8"' + (' opacity="0.35"' if bon else ' stroke-width="2"') + "/>"
        c += texte(x + 32, 68, s, "t", 34, "middle", 700)
        c += texte(x + 32, 120, "à retourner" if bon else "inutile", "t" if bon else "tm", 12, "middle", 700 if bon else None)
    return svg(336, 132, c, "Tâche de Wason résolue : retourner E et 7")
