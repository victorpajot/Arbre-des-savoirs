"""v15 : schémas figuratifs, façon manuel de SVT, pour les notions concrètes.

Victor a demandé « des schémas dès que possible », comme un schéma de cellule légendé.
Les organes, organites et molécules gardent des couleurs fixes, comme une planche de manuel ;
les légendes et les traits de rappel suivent le thème (classes t, tm, lm de illustrations.py).

FIGURES[id] = (titre, svg). QUESTIONS[id_question] = id_figure : le schéma s'affiche après la réponse.
Chaque compétence qui a des figures les montre aussi dans sa fiche de révision (COMPETENCES).
"""
import math
import re

from illustrations import texte

# Contours et aplats des planches.
BRUN = "#7A5418"


def forme(tag, fill, stroke, largeur=2, **attrs):
    a = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<{tag} fill="{fill}" stroke="{stroke}" stroke-width="{largeur}"{a}/>'


def chemin(d, stroke, largeur=2, fill="none", **attrs):
    return forme("path", fill, stroke, largeur, d=d, stroke_linecap="round", stroke_linejoin="round", **attrs)


def legende(x, y, s, vers, ancre="end", taille=13):
    """Légende (une ou deux lignes séparées par « | ») et trait de rappel vers le point `vers`.

    Le trait part du bord de la légende tourné vers la cible et passe sous le texte,
    qui garde un liseré couleur de fond (classe h) : un trait qui croise une autre légende ne la barre pas."""
    lignes = s.split("|")
    w = max(len(l) for l in lignes) * taille * 0.58
    gauche = x - w if ancre == "end" else x
    droite = gauche + w
    haut, bas = y - taille + 2, y + (len(lignes) - 1) * (taille + 2) + 3
    if vers[1] < haut - 6 or vers[1] > bas + 6:
        lx = round(min(max(vers[0], gauche + 4), droite - 4), 1)
        ly = haut - 2 if vers[1] < haut else bas + 2
    else:
        lx = round(gauche - 4 if vers[0] < gauche else droite + 4, 1)
        ly = (haut + bas) / 2
    c = f'<line class="lm" x1="{lx}" y1="{ly}" x2="{vers[0]}" y2="{vers[1]}"/>'
    c += f'<circle class="lm" cx="{vers[0]}" cy="{vers[1]}" r="1.8" fill="currentColor"/>'
    c += "".join(texte(x, y + i * (taille + 2), l, "t h", taille, ancre, 600) for i, l in enumerate(lignes))
    return c


def planche(largeur, hauteur, corps, titre, marge=8):
    """svg() dont la viewBox s'élargit jusqu'aux légendes, pour qu'aucune ne soit rognée au bord."""
    x0, x1 = 0, largeur
    for m in re.finditer(r'<text[^>]* x="([\d.-]+)"[^>]* font-size="([\d.]+)" text-anchor="(\w+)"[^>]*>([^<]*)</text>', corps):
        x, t, ancre, s = float(m[1]), float(m[2]), m[3], m[4]
        w = len(s) * t * 0.58
        g = x - w if ancre == "end" else x - w / 2 if ancre == "middle" else x
        x0, x1 = min(x0, g - marge), max(x1, g + w + marge)
    x0, x1 = math.floor(x0), math.ceil(x1)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} 0 {x1 - x0} {hauteur}" role="img" aria-label="{titre}">'
            + corps + "</svg>")


def arc(cx, cy, r, a0, a1):
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    grand = 1 if abs(a1 - a0) > 180 else 0
    return f"M{x0:.1f} {y0:.1f} A{r} {r} 0 {grand} 1 {x1:.1f} {y1:.1f}"


def pt(cx, cy, r, a):
    return (round(cx + r * math.cos(math.radians(a)), 1), round(cy + r * math.sin(math.radians(a)), 1))


def mitochondrie(x, y, rot, s=1.0):
    rx, ry = 22 * s, 11 * s
    crete = " ".join(f"L{x - rx + 6 + i * (2 * rx - 12) / 7:.1f} {y + (5 if i % 2 else -5) * s:.1f}" for i in range(8))
    return (f'<g transform="rotate({rot} {x} {y})">' + forme("ellipse", "#F4B26B", "#B35A1A", 2, cx=x, cy=y, rx=rx, ry=ry)
            + chemin(f"M{x - rx + 6:.1f} {y:.1f} " + crete, "#B35A1A", 1.5) + "</g>")


# --- La cellule animale ---------------------------------------------------------------

def cellule_animale():
    cx, cy = 190, 132
    c = forme("ellipse", "#F7EBC8", "#B98A3E", 3.5, cx=cx, cy=cy, rx=110, ry=100)
    # Cytosquelette : quelques fibres.
    for d in ["M118 74 Q160 58 205 52", "M268 112 Q288 150 276 196", "M112 168 Q118 200 150 222", "M232 60 Q262 72 286 98"]:
        c += chemin(d, "#8DA05A", 1.6)
    # Appareil de Golgi : des saccules empilés.
    for i, r in enumerate((24, 31, 38, 45)):
        c += chemin(arc(64, 136, r, -42, 42), "#E07A93", 5 - i * 0.4)
    # Réticulum endoplasmique et ses ribosomes.
    for r in (50, 58, 66):
        c += chemin(arc(178, 138, r, -95, 10), "#4F86C6", 4)
    for a in range(-90, 12, 12):
        x, y = pt(178, 138, 62, a)
        c += forme("circle", "#D63B3B", "none", 0, cx=x, cy=y, r=2.4)
    # Noyau, enveloppe double, chromatine, nucléole.
    c += forme("circle", "#E2D6F0", "#5B4A8C", 3, cx=178, cy=138, r=40)
    c += forme("circle", "none", "#8E7CC0", 1.5, cx=178, cy=138, r=35)
    for d in ["M158 128 q6 -10 14 -2 t14 0", "M160 152 q8 6 14 -2 t12 4", "M186 118 q8 4 6 12 t6 10", "M164 140 q4 8 12 6"]:
        c += chemin(d, "#8E7CC0", 1.8)
    c += forme("circle", "#3E275F", "none", 0, cx=172, cy=132, r=9)
    # Mitochondries.
    c += mitochondrie(258, 92, 30) + mitochondrie(262, 172, -25) + mitochondrie(140, 206, 12)
    # Vacuole et ribosomes libres.
    c += forme("ellipse", "#DDEBF6", "#6C8DB0", 2, cx=214, cy=212, rx=18, ry=10)
    for x, y in [(236, 130), (122, 98), (128, 178), (244, 214), (208, 72), (290, 140), (110, 130)]:
        c += forme("circle", "#D63B3B", "none", 0, cx=x, cy=y, r=2.4)
    # Légendes.
    c += legende(74, 40, "Membrane", (112, 62))
    c += legende(74, 80, "Cytosquelette", (126, 72))
    c += legende(74, 126, "Appareil|de Golgi", (100, 132))
    c += legende(74, 176, "Noyau", (142, 150))
    c += legende(74, 218, "Cytoplasme", (118, 194))
    c += legende(306, 36, "Mitochondrie", (262, 88), "start")
    c += legende(306, 76, "Réticulum|endoplasmique", (236, 110), "start")
    c += legende(306, 124, "Ribosome", (238, 130), "start")
    c += legende(306, 156, "Nucléole", (176, 128), "start")
    c += legende(306, 190, "ADN|(chromatine)", (196, 150), "start")
    c += legende(306, 232, "Vacuole", (228, 212), "start")
    return planche(380, 250, c, "Schéma d'une cellule animale et de ses organites")


# --- La cellule végétale -----------------------------------------------------------------

def chloroplaste(x, y, rot):
    c = f'<g transform="rotate({rot} {x} {y})">' + forme("ellipse", "#7CC36A", "#2F7A2A", 2, cx=x, cy=y, rx=17, ry=9)
    for dx in (-8, 0, 8):
        c += forme("rect", "#2F7A2A", "none", 0, x=x + dx - 2.5, y=y - 4, width=5, height=8, rx=1)
    return c + "</g>"


def cellule_vegetale():
    c = forme("rect", "#C7E3A8", "#4E7D2E", 6, x=60, y=24, width=260, height=200, rx=14)
    c += forme("rect", "#F4F1D8", "#A7B56A", 2, x=68, y=32, width=244, height=184, rx=10)
    c += forme("rect", "#DCEBF6", "#6C8DB0", 2, x=150, y=60, width=140, height=130, rx=30)
    c += forme("circle", "#E2D6F0", "#5B4A8C", 3, cx=106, cy=84, r=24)
    c += forme("circle", "#3E275F", "none", 0, cx=101, cy=80, r=6)
    c += chloroplaste(100, 150, 20) + chloroplaste(120, 196, -10) + chloroplaste(260, 206, 0) + chloroplaste(190, 44, 0) + chloroplaste(300, 120, 80)
    c += mitochondrie(96, 118, 0, 0.7)
    c += legende(52, 34, "Paroi", (62, 50))
    c += legende(52, 72, "Noyau", (84, 82))
    c += legende(52, 150, "Chloroplaste", (88, 148))
    c += legende(52, 112, "Mitochondrie", (82, 118))
    c += legende(52, 210, "Membrane", (70, 206))
    c += legende(330, 60, "Grande|vacuole", (270, 92), "start")
    c += legende(330, 216, "Cytoplasme", (296, 196), "start")
    return planche(400, 240, c, "Cellule végétale : paroi, chloroplastes et grande vacuole")


# --- Bactérie et virus ------------------------------------------------------------------

def bacterie_virus():
    c = texte(105, 18, "Bactérie (≈ 2 µm)", "t", 13, "middle", 700) + texte(290, 18, "Virus (≈ 0,1 µm)", "t", 13, "middle", 700)
    c += f'<line class="lm" x1="214" y1="10" x2="214" y2="196"/>'
    c += forme("rect", "#CFE8C4", "#3E7D3A", 5, x=30, y=60, width=150, height=72, rx=36)
    c += forme("rect", "#E6F3DE", "#7FB070", 2, x=38, y=68, width=134, height=56, rx=28)
    c += chemin("M60 96 q10 -16 24 -4 t26 2 t24 -6", "#5B4A8C", 2.2)
    c += forme("circle", "none", "#5B4A8C", 1.8, cx=140, cy=104, r=6)
    for x, y in [(72, 82), (120, 84), (96, 112), (150, 90), (60, 110)]:
        c += forme("circle", "#D63B3B", "none", 0, cx=x, cy=y, r=2.2)
    c += chemin("M180 96 q14 -10 22 6 t16 -4", "#3E7D3A", 2)
    c += legende(30, 160, "Paroi et|membrane", (52, 128), "start")
    c += legende(104, 160, "ADN libre,|sans noyau", (100, 102), "start")
    c += legende(40, 48, "Ribosomes", (72, 82), "start")
    c += legende(196, 52, "Flagelle", (206, 100))
    # Virus : capside icosaédrique, ADN ou ARN, spicules.
    pts = [pt(290, 100, 34, a) for a in range(-90, 270, 60)]
    c += forme("polygon", "#F2C7D2", "#A8325B", 3, points=" ".join(f"{x},{y}" for x, y in pts))
    for x, y in pts:
        x2, y2 = pt(290, 100, 46, math.degrees(math.atan2(y - 100, x - 290)))
        c += f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="#A8325B" stroke-width="2"/>' + forme("circle", "#A8325B", "none", 0, cx=x2, cy=y2, r=3)
    c += chemin("M276 92 q8 -10 14 2 t14 -2 q4 10 -8 14 t-16 4", "#5B4A8C", 2.2)
    c += legende(222, 166, "Capside|(protéines)", (268, 122), "start")
    c += legende(304, 166, "Génome|(ADN ou ARN)", (298, 104), "start")
    c += texte(300, 214, "Pas de ribosomes : il se fait", "tm", 11) + texte(300, 228, "copier par la cellule infectée.", "tm", 11)
    return planche(390, 236, c, "Bactérie et virus comparés")


# --- L'atome ----------------------------------------------------------------------------

def atome():
    c = ""
    for r in (40, 78):
        c += f'<circle class="lm" cx="150" cy="120" r="{r}" stroke-dasharray="4 4"/>'
    noyau = [(-6, -5, "p"), (5, -6, "n"), (-5, 6, "n"), (6, 5, "p"), (0, 0, "p"), (-9, 2, "n"), (9, -1, "p"), (1, -10, "n"), (0, 10, "n"), (-2, -1, "n"), (3, 2, "p"), (-1, 5, "p")]
    for dx, dy, k in noyau:
        c += forme("circle", "#D94141" if k == "p" else "#9AA0A8", "#5E1414" if k == "p" else "#5D6470", 1, cx=150 + dx, cy=120 + dy, r=5)
    for r, angles in ((40, (30, 210)), (78, (45, 135, 225, 315))):
        for a in angles:
            x, y = pt(150, 120, r, a)
            c += forme("circle", "#3D63D9", "#1A2C66", 1.2, cx=x, cy=y, r=5) + texte(x, y + 3.5, "−", "t", 10, "middle", 700).replace('class="t"', 'fill="#fff"')
    c += legende(330, 40, "Électron (charge −)", (205, 65), "end")
    c += legende(222, 148, "Proton (charge +)", (157, 125), "start")
    c += legende(222, 200, "Neutron (sans charge)", (141, 118), "start")
    c += texte(24, 20, "Carbone : 6 protons,", "t", 12, "start", 700) + texte(24, 35, "6 neutrons, 6 électrons", "t", 12, "start", 700)
    c += texte(24, 250, "Pas à l'échelle : le noyau est", "tm", 11, "start") + texte(24, 264, "100 000 fois plus petit que l'atome.", "tm", 11, "start")
    return planche(340, 272, c, "Atome de carbone : noyau de protons et de neutrons, électrons autour")


# --- L'ADN ------------------------------------------------------------------------------

def adn():
    c = ""
    paires = [("A", "T"), ("C", "G"), ("T", "A"), ("G", "C"), ("A", "T"), ("G", "C"), ("T", "A"), ("C", "G"), ("A", "T")]
    couleur = {"A": "#E8873A", "T": "#4F86C6", "C": "#5FAE5A", "G": "#C94B6D"}
    haut, pas = 30, 22
    brin1 = []
    brin2 = []
    for i in range(len(paires) * 4 + 1):
        y = haut + i * pas / 4
        ph = i / 4 * 0.75
        brin1.append((190 + 70 * math.sin(ph), y))
        brin2.append((190 - 70 * math.sin(ph), y))
    for i, (b1, b2) in enumerate(paires):
        y = haut + (i + 0.5) * pas
        ph = (i + 0.5) * 0.75
        x1, x2 = 190 + 70 * math.sin(ph), 190 - 70 * math.sin(ph)
        xm = (x1 + x2) / 2
        c += f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{xm:.1f}" y2="{y:.1f}" stroke="{couleur[b1]}" stroke-width="7" stroke-linecap="round"/>'
        c += f'<line x1="{xm:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{couleur[b2]}" stroke-width="7" stroke-linecap="round"/>'
        if abs(x1 - x2) > 40:
            c += texte(x1 + (8 if x1 > x2 else -8), y + 4, b1, "t", 11, "start" if x1 > x2 else "end", 700)
            c += texte(x2 + (8 if x2 > x1 else -8), y + 4, b2, "t", 11, "start" if x2 > x1 else "end", 700)
    c += chemin("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in brin1), "#5D6470", 4)
    c += chemin("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in brin2), "#9AA0A8", 4)
    c += texte(20, 40, "Toujours :", "t", 13, "start", 700)
    c += f'<rect x="20" y="52" width="14" height="10" rx="2" fill="{couleur["A"]}"/><rect x="34" y="52" width="14" height="10" rx="2" fill="{couleur["T"]}"/>' + texte(56, 61, "A avec T", "t", 12, "start")
    c += f'<rect x="20" y="72" width="14" height="10" rx="2" fill="{couleur["C"]}"/><rect x="34" y="72" width="14" height="10" rx="2" fill="{couleur["G"]}"/>' + texte(56, 81, "C avec G", "t", 12, "start")
    c += legende(360, 60, "Brin|(sucre et|phosphate)", (258, 62), "end")
    c += legende(360, 190, "Paire de|bases", (226, 195), "end")
    c += texte(20, 252, "Deux brins enroulés en double hélice", "tm", 11, "start") + texte(20, 266, "(Watson, Crick, Franklin, Wilkins, 1953)", "tm", 11, "start")
    return planche(380, 274, c, "La double hélice de l'ADN et ses paires de bases")


# --- Le neurone et le cerveau -----------------------------------------------------------

def neurone():
    c = ""
    for d in ["M60 100 l-28 -26 m14 13 l-6 -18", "M60 100 l-34 4 m14 -1 l-8 -12", "M60 100 l-24 30 m10 -13 l-14 2", "M66 92 l-6 -34 m2 14 l12 -10", "M66 110 l2 32 m-1 -14 l-12 6"]:
        c += chemin(d, "#B35A1A", 2.5)
    c += forme("circle", "#F4B26B", "#B35A1A", 2.5, cx=66, cy=100, r=20)
    c += forme("circle", "#7A3E1E", "none", 0, cx=64, cy=98, r=6)
    c += chemin("M86 100 H300", "#B35A1A", 3)
    for x in range(100, 290, 34):
        c += forme("rect", "#F7EBD0", "#C99260", 2, x=x, y=92, width=26, height=16, rx=8)
    for d in ["M300 100 l22 -20", "M300 100 l26 0", "M300 100 l22 20"]:
        c += chemin(d, "#B35A1A", 2.5)
    for x, y in [(322, 80), (326, 100), (322, 120)]:
        c += forme("circle", "#F4B26B", "#B35A1A", 2, cx=x, cy=y, r=5)
    c += chemin("M120 150 H290", "#5B4A8C", 2, marker_end="url(#fl)")
    c += '<defs><marker id="fl" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="#5B4A8C"/></marker></defs>'
    c += texte(205, 168, "sens du message électrique", "tm", 11)
    c += legende(20, 30, "Dendrites (reçoivent)", (40, 78), "start")
    c += legende(120, 52, "Corps cellulaire et noyau", (70, 88), "start")
    c += legende(170, 76, "Axone gainé de myéline", (180, 92), "start")
    c += legende(340, 56, "Synapses|(vers le neurone|suivant)", (324, 78), "start")
    c += texte(20, 200, "Environ 86 milliards de neurones dans un cerveau humain.", "tm", 11, "start")
    return planche(350, 210, c, "Un neurone : dendrites, corps cellulaire, axone, synapses")


def cerveau():
    c = chemin("M70 150 C40 120 50 60 110 46 C150 20 230 22 270 52 C310 70 320 120 300 150 C290 170 260 176 240 168 "
               "C220 178 180 180 160 170 C130 178 90 176 70 150 Z", "#9C6B43", 3, fill="#F2C9A0")
    # Lobes.
    c += chemin("M110 46 C120 80 116 120 126 160", "#9C6B43", 2)
    c += chemin("M200 26 C196 60 206 90 200 116", "#9C6B43", 2)
    c += chemin("M126 118 C160 108 210 114 250 120", "#9C6B43", 2)
    c += chemin("M262 46 C250 80 258 110 270 140", "#9C6B43", 2)
    # Cervelet et tronc cérébral.
    c += chemin("M232 168 C236 196 290 200 300 170 C296 156 258 156 232 168 Z", "#9C6B43", 2.5, fill="#E39A6B")
    for y in (172, 180, 188):
        c += chemin(f"M244 {y} C262 {y + 4} 282 {y + 2} 294 {y - 4}", "#9C6B43", 1.2)
    c += chemin("M200 170 C202 196 206 214 212 232 L230 232 C224 212 224 194 226 172", "#9C6B43", 2.5, fill="#E39A6B")
    # Aire de Broca.
    c += forme("ellipse", "#D94141", "none", 0, cx=112, cy=128, rx=12, ry=8, opacity="0.75")
    c += legende(30, 22, "Lobe frontal|(décider, planifier)", (90, 80), "start")
    c += legende(206, 14, "Lobe pariétal (toucher, espace)", (220, 60), "start")
    c += legende(392, 96, "Lobe|occipital|(vision)", (288, 96), "end")
    c += legende(30, 196, "Aire de Broca|(parole)", (108, 132), "start")
    c += legende(30, 238, "Lobe temporal|(audition, mémoire)", (176, 146), "start")
    c += legende(380, 214, "Cervelet|(équilibre)", (282, 184), "end")
    return planche(390, 262, c, "Le cerveau vu de profil : lobes, aire de Broca, cervelet")


# --- Le corps : les organes du tronc ----------------------------------------------------

def organes():
    c = chemin("M120 20 C90 22 70 40 70 70 L64 220 C64 236 80 244 100 244 L240 244 C260 244 276 236 276 220 L270 70 C270 40 250 22 220 20 Z",
               "#C99260", 2.5, fill="#FBE3C8")
    # Poumons.
    c += chemin("M150 40 C120 44 100 80 100 124 C100 140 120 144 146 136 C150 100 152 66 150 40 Z", "#B5476B", 2, fill="#F28FB0")
    c += chemin("M190 40 C220 44 240 80 240 124 C240 140 220 144 194 136 C190 100 188 66 190 40 Z", "#B5476B", 2, fill="#F28FB0")
    c += chemin("M170 22 V60 M170 60 L150 78 M170 60 L190 78", "#9C6B43", 4)
    # Cœur.
    c += chemin("M168 98 C150 84 140 108 158 122 L176 136 L192 116 C206 100 190 84 176 96 Z", "#8E2424", 2, fill="#D94141")
    # Foie, estomac, pancréas, reins, intestins.
    c += chemin("M100 150 C120 140 180 140 186 156 C176 176 130 182 104 172 Z", "#6E4429", 2, fill="#A0522D")
    c += chemin("M196 148 C230 140 250 160 236 182 C222 196 200 186 198 170 Z", "#B5623B", 2, fill="#E39A6B")
    c += chemin("M160 186 C186 182 212 186 226 192", "#B98059", 6)
    c += forme("ellipse", "#B5476B", "#6E2A3E", 2, cx=116, cy=196, rx=10, ry=16)
    c += forme("ellipse", "#B5476B", "#6E2A3E", 2, cx=228, cy=212, rx=10, ry=16)
    c += chemin("M130 206 C150 196 190 196 210 206 C214 222 196 230 170 230 C150 230 128 224 130 206 Z", "#C99260", 2, fill="#F2C9A0")
    c += chemin("M140 214 q10 -6 20 0 t20 0 t20 0", "#C99260", 1.5)
    c += legende(56, 60, "Poumons|(alvéoles)", (110, 96))
    c += legende(56, 112, "Cœur", (160, 112))
    c += legende(56, 160, "Foie (bile)", (120, 160))
    c += legende(56, 204, "Rein", (106, 196))
    c += legende(290, 62, "Trachée", (172, 40), "start")
    c += legende(290, 160, "Estomac", (226, 162), "start")
    c += legende(290, 190, "Pancréas|(insuline)", (214, 188), "start")
    c += legende(290, 236, "Intestins", (200, 220), "start")
    return planche(350, 252, c, "Les principaux organes du tronc")


# --- La molécule d'eau ------------------------------------------------------------------

def eau():
    c = forme("circle", "#D94141", "#8E2424", 2.5, cx=170, cy=100, r=34)
    c += forme("circle", "#E8E8EE", "#5D6470", 2.5, cx=110, cy=150, r=22)
    c += forme("circle", "#E8E8EE", "#5D6470", 2.5, cx=230, cy=150, r=22)
    c += texte(170, 106, "O", "t", 20, "middle", 800).replace('class="t"', 'fill="#fff"')
    c += texte(110, 156, "H", "t", 16, "middle", 800).replace('class="t"', 'fill="#1E1A2B"')
    c += texte(230, 156, "H", "t", 16, "middle", 800).replace('class="t"', 'fill="#1E1A2B"')
    for x, y in [(136, 126), (142, 132), (204, 126), (198, 132)]:
        c += forme("circle", "#3D63D9", "none", 0, cx=x, cy=y, r=3.5)
    for x, y in [(160, 62), (180, 62), (204, 84), (204, 94)]:
        c += forme("circle", "#3D63D9", "none", 0, cx=x, cy=y, r=3.5)
    c += texte(170, 46, "δ−", "t", 16, "middle", 700) + texte(84, 182, "δ+", "t", 16, "middle", 700) + texte(256, 182, "δ+", "t", 16, "middle", 700)
    c += legende(262, 96, "Paire d'électrons|partagée : liaison|covalente", (206, 126), "start")
    c += texte(20, 30, "Angle 104,5° : l'eau est", "t", 12, "start", 700) + texte(20, 45, "une molécule polaire.", "t", 12, "start", 700)
    c += texte(20, 214, "L'oxygène, plus électronégatif, attire les électrons :", "tm", 11, "start")
    c += texte(20, 228, "c'est pour ça que l'eau dissout le sel et repousse l'huile.", "tm", 11, "start")
    return planche(340, 236, c, "La molécule d'eau : liaisons covalentes et charges partielles")


# --- Le cycle du carbone ----------------------------------------------------------------

def cycle_carbone():
    c = forme("rect", "#DDEBF6", "none", 0, x=0, y=0, width=380, height=150)
    c += forme("rect", "#C9A57A", "none", 0, x=0, y=150, width=380, height=90)
    c += forme("circle", "#F2C14E", "#C99A1E", 2, cx=356, cy=26, r=14)
    c += texte(190, 26, "CO₂ dans l'air", "t", 14, "middle", 800).replace('class="t"', 'fill="#1E1A2B"')
    # Arbre, vache, champignon, usine.
    c += forme("rect", "#6E4429", "none", 0, x=76, y=96, width=10, height=56) + forme("circle", "#4CAF50", "#2E7D32", 2, cx=81, cy=86, r=26)
    c += forme("ellipse", "#F7EBD0", "#5E3B1C", 2, cx=190, cy=134, rx=28, ry=14) + forme("rect", "#5E3B1C", "none", 0, x=168, y=144, width=4, height=10) + forme("rect", "#5E3B1C", "none", 0, x=206, y=144, width=4, height=10) + forme("circle", "#F7EBD0", "#5E3B1C", 2, cx=222, cy=124, r=9)
    c += forme("rect", "#9AA0A8", "#5D6470", 2, x=296, y=110, width=46, height=40) + forme("rect", "#9AA0A8", "#5D6470", 2, x=318, y=76, width=10, height=36)
    c += forme("ellipse", "#E39A6B", "#9C4A2A", 2, cx=130, cy=176, rx=14, ry=7) + forme("rect", "#F7EBD0", "#9C4A2A", 1.5, x=126, y=176, width=8, height=12)
    c += forme("rect", "#3B3B3B", "none", 0, x=230, y=200, width=110, height=22, rx=6) + texte(285, 215, "charbon, pétrole", "t", 11, "middle", 700).replace('class="t"', 'fill="#E8E8EE"')

    def fleche(x1, y1, x2, y2, couleur, label, mx, my):
        # L'étiquette se pose en pastille à côté de sa flèche.
        w = len(label) * 6.6 + 12
        return (f'<defs><marker id="fc{couleur[1:]}" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="{couleur}"/></marker></defs>'
                + f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{couleur}" stroke-width="3" marker-end="url(#fc{couleur[1:]})"/>'
                + forme("rect", "#FFFFFF", couleur, 1.5, x=round(mx - w / 2, 1), y=my - 9, width=round(w, 1), height=18, rx=9, opacity="0.92")
                + texte(mx, my + 4, label, "t", 11, "middle", 700).replace('class="t"', f'fill="{couleur}"'))
    c += fleche(146, 34, 106, 60, "#2E7D32", "photosynthèse", 62, 36)
    c += fleche(196, 112, 196, 40, "#8E2424", "respiration", 240, 86)
    c += fleche(128, 168, 150, 42, "#9C4A2A", "décomposition", 192, 172)
    c += fleche(318, 72, 252, 34, "#3B3B3B", "combustion", 240, 60)
    return planche(380, 232, c, "Le cycle du carbone : photosynthèse, respiration, décomposition, combustion")


FIGURES = {
    "cellule": cellule_animale(),
    "cellule_vegetale": cellule_vegetale(),
    "bacterie_virus": bacterie_virus(),
    "atome": atome(),
    "adn": adn(),
    "neurone": neurone(),
    "cerveau": cerveau(),
    "organes": organes(),
    "eau": eau(),
    "carbone": cycle_carbone(),
}

# Figures d'une compétence, montrées dans sa fiche de révision.
COMPETENCES = {
    "sci.cellule": ["cellule", "cellule_vegetale", "adn"],
    "sci.immunite": ["bacterie_virus"],
    "sci.atomes": ["atome"],
    "chim.liaisons": ["eau", "atome"],
    "sci.genetique": ["adn"],
    "psy.cerveau": ["cerveau", "neurone"],
    "sci.corps": ["organes"],
    "sci.ecologie": ["carbone"],
}

# Le schéma qui éclaire la réponse de chaque question.
QUESTIONS = {
    "sci.cellule.q01": "cellule", "sci.cellule.q02": "bacterie_virus", "sci.cellule.q03": "cellule_vegetale", "sci.cellule.q04": "cellule",
    "sci.cellule.q05": "cellule", "sci.cellule.q06": "cellule", "sci.cellule.q07": "cellule", "sci.cellule.q10": "bacterie_virus",
    "sci.cellule.q11": "adn", "sci.cellule.q12": "cellule_vegetale",
    "sci.immunite.q02": "bacterie_virus", "sci.immunite.q03": "bacterie_virus", "sci.immunite.q12": "bacterie_virus",
    "sci.atomes.q01": "atome", "sci.atomes.q03": "atome", "sci.atomes.q04": "atome", "sci.atomes.q12": "atome", "sci.atomes.q02": "eau",
    "chim.liaisons.q01": "eau", "chim.liaisons.q05": "atome", "chim.liaisons.q07": "eau", "chim.liaisons.q09": "eau", "chim.liaisons.q12": "eau",
    "sci.genetique.q02": "adn", "sci.genetique.q05": "adn", "sci.genetique.q06": "adn", "sci.genetique.q10": "adn",
    "psy.cerveau.q01": "neurone", "psy.cerveau.q04": "cerveau", "psy.cerveau.q06": "neurone", "psy.cerveau.q08": "neurone", "psy.cerveau.q12": "cerveau",
    "sci.corps.q03": "organes", "sci.corps.q05": "organes", "sci.corps.q07": "organes", "sci.corps.q09": "organes", "sci.corps.q12": "organes",
    "sci.ecologie.q01": "carbone", "sci.ecologie.q06": "carbone", "sci.ecologie.q10": "carbone",
}

TITRES = {k: v[v.find('aria-label="') + 12:v.find('">', v.find('aria-label="'))] for k, v in FIGURES.items()}


if __name__ == "__main__":
    import sys
    page = ['<!doctype html><meta charset="utf-8"><style>body{font-family:sans-serif;background:#ECEEF3;color:#161A26}'
            '.d{background:#1E1A2B;color:#eee}.t{fill:currentColor}.tm{fill:#5B6273}.lm{stroke:#5B6273;stroke-width:1.5;fill:none}.h{stroke:#fff;stroke-width:3.5px;paint-order:stroke;stroke-linejoin:round}.d .h{stroke:#2B2B33}'
            '.d .tm{fill:#aab}.d .lm{stroke:#aab}div{display:inline-block;width:420px;margin:8px;padding:10px;border-radius:12px;background:#fff}'
            '.d div{background:#2B2B33}svg{width:100%}</style>']
    for cls in ("", "d"):
        page.append(f'<section class="{cls}">' + "".join(f"<div>{v}</div>" for v in FIGURES.values()) + "</section>")
    open(sys.argv[1], "w").write("".join(page))
