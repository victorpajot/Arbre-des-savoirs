"""v31 (Victor) : schémas d'explication ajoutés après celui du test de dépistage.

Même vocabulaire de classes que illustrations.py (t, tm, l, lm, f, f2, a, al, ok, ko, jaune) : clair et sombre.
Chacun s'affiche après la réponse, sous l'explication.
"""
import math

from illustrations import fil, svg, texte


def barre(x, base, h, l, cls, haut, bas):
    """Barre verticale posée sur la ligne `base`, valeur au-dessus, étiquette dessous."""
    return (f'<rect class="{cls}" x="{x - l / 2}" y="{base - h}" width="{l}" height="{h}" rx="3"/>'
            + texte(x, base - h - 6, haut, "t", 14, "middle", 700) + texte(x, base + 16, bas, "tm", 12))


def fleche(x1, y1, x2, y2, cls="l"):
    a = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - 8 * math.cos(a - 0.45), y2 - 8 * math.sin(a - 0.45))
    p2 = (x2 - 8 * math.cos(a + 0.45), y2 - 8 * math.sin(a + 0.45))
    return (f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'
            + f'<polyline class="{cls}" points="{p1[0]:.1f},{p1[1]:.1f} {x2},{y2} {p2[0]:.1f},{p2[1]:.1f}"/>')


# --- Pourcentages -------------------------------------------------------------

def hausse_baisse():
    b = 150
    c = barre(60, b, 60, 50, "f", "100 €", "départ") + barre(170, b, 90, 50, "ok", "150 €", "+50 %") + barre(280, b, 45, 50, "ko", "75 €", "−50 %")
    c += texte(115, 40, "+50 de 100", "tm", 12) + texte(225, 40, "−75 de 150", "tm", 12)
    c += f'<line class="lm" x1="20" y1="{b - 60}" x2="320" y2="{b - 60}" stroke-dasharray="4 4"/>'
    return svg(340, 176, c, "100 € plus 50 % donnent 150 €, puis moins 50 % donnent 75 € : la baisse s'applique à un montant plus grand")


def ttc_ht():
    c = f'<rect class="f" x="20" y="30" width="250" height="34" rx="4"/><rect class="a" x="270" y="30" width="50" height="34" rx="4" opacity="0.6"/>'
    c += texte(145, 52, "HT : 100 €", "t", 14, "middle", 700) + texte(295, 52, "+20", "t", 13, "middle", 700)
    c += texte(170, 20, "TTC = 120 € = HT × 1,2", "tm", 12)
    c += f'<rect class="f" x="20" y="100" width="240" height="34" rx="4"/><rect class="ko" x="260" y="100" width="60" height="34" rx="4"/>'
    c += texte(140, 122, "96 €", "t", 14, "middle", 700) + texte(290, 122, "−24", "t", 13, "middle", 700)
    c += texte(170, 90, "Piège : 20 % de 120 € = 24 €", "tm", 12)
    c += texte(170, 156, "La TVA se calcule sur le prix HT, pas sur le TTC.", "t", 13, "middle", 700)
    return svg(340, 166, c, "Prix hors taxe 100 euros, plus 20 euros de TVA, donne 120 euros ; retirer 20 % de 120 donnerait 96 euros")


def points_pourcent():
    b = 150
    c = barre(90, b, 50, 60, "f", "10 %", "avant") + barre(250, b, 75, 60, "a", "15 %", "après")
    c += f'<rect class="ok" x="220" y="{b - 75}" width="60" height="25" rx="3"/>'
    c += texte(170, 36, "+5 points", "t", 14, "middle", 700) + texte(170, 54, "5 / 10 = +50 % de hausse relative", "tm", 12)
    return svg(340, 176, c, "De 10 % à 15 % : cinq points de plus, soit une hausse relative de 50 %")


# --- Statistiques ---------------------------------------------------------------

def mediane_moyenne():
    def x(v):
        return 20 + v * 3
    c = fil((20, 80), (320, 80))
    for v in (0, 25, 50, 75, 100):
        c += f'<line class="lm" x1="{x(v)}" y1="76" x2="{x(v)}" y2="84"/>' + texte(x(v), 100, str(v), "tm", 11)
    for v, dy in ((2, 0), (3, 0), (3, -12), (8, 0), (100, 0)):
        c += f'<circle class="f" cx="{x(v)}" cy="{68 + dy}" r="5"/>'
    c += f'<line class="ok" x1="{x(3)}" y1="30" x2="{x(3)}" y2="80" stroke-width="2.5"/>' + texte(x(3) + 4, 26, "médiane 3", "t", 13, "start", 700)
    c += f'<line class="ko" x1="{x(23.2)}" y1="44" x2="{x(23.2)}" y2="80" stroke-width="2.5"/>' + texte(x(23.2) + 4, 44, "moyenne 23,2", "t", 13, "start", 700)
    c += texte(x(100), 40, "le 100 tire", "tm", 11, "end") + texte(x(100), 54, "la moyenne", "tm", 11, "end")
    return svg(340, 112, c, "Les valeurs 2, 3, 3, 8 et 100 : la médiane reste à 3, la moyenne monte à 23,2 à cause du 100")


def loi_normale():
    def y(x):
        return 140 - 110 * math.exp(-((x - 170) / 45) ** 2 / 2)
    bandes = ""
    for (a, b, cls) in ((80, 125, "f2"), (125, 215, "ok"), (215, 260, "f2")):
        pts = [(a, 140)] + [(xx, y(xx)) for xx in range(a, b + 1, 3)] + [(b, 140)]
        bandes += '<polygon class="' + cls + '" points="' + " ".join(f"{p[0]},{p[1]:.1f}" for p in pts) + '"/>'
    courbe = '<polyline class="l" points="' + " ".join(f"{xx},{y(xx):.1f}" for xx in range(20, 321, 4)) + '"/>'
    c = bandes + courbe + fil((20, 140), (320, 140))
    for k, lab in ((-2, "−2σ"), (-1, "−1σ"), (0, "moyenne"), (1, "+1σ"), (2, "+2σ")):
        xx = 170 + 45 * k
        c += f'<line class="lm" x1="{xx}" y1="140" x2="{xx}" y2="146"/>' + texte(xx, 160, lab, "tm", 11)
    c += texte(170, 112, "≈ 68 %", "t", 15, "middle", 700) + texte(170, 22, "≈ 95 % entre −2σ et +2σ", "tm", 12)
    return svg(340, 168, c, "Courbe en cloche : environ 68 % des valeurs à moins d'un écart type de la moyenne, 95 % à moins de deux")


def cause_commune():
    def boite(x, y, s, cls="f"):
        return f'<rect class="{cls}" x="{x - 58}" y="{y - 18}" width="116" height="36" rx="8"/>' + texte(x, y + 5, s, "t", 14, "middle", 700)
    c = boite(170, 30, "l'été, la chaleur", "a") + boite(70, 130, "glaces vendues") + boite(270, 130, "noyades")
    c = c.replace('class="a"', 'class="ok"', 1)
    c += fleche(140, 48, 90, 110) + fleche(200, 48, 250, 110)
    c += f'<line class="ko" x1="130" y1="130" x2="210" y2="130" stroke-dasharray="5 5" stroke-width="2"/>'
    c += texte(170, 122, "corrélées", "tm", 11) + texte(170, 166, "mais l'une ne cause pas l'autre", "tm", 12)
    return svg(340, 176, c, "L'été fait monter à la fois les ventes de glaces et les noyades : corrélation sans causalité")


def ordinaire_noire():
    parts = (("matière ordinaire", 5, "a"), ("matière noire", 27, "a"), ("énergie noire", 68, "f"))
    c, x = "", 20
    for nom, p, cls in parts:
        l = 300 * p / 100
        c += f'<rect class="{cls}" x="{x}" y="40" width="{l}" height="40" rx="2"' + (' fill-opacity="0.4"' if nom == "matière noire" else "") + '/>'
        x += l
    c += texte(28, 100, "5 %", "t", 14, "start", 700) + texte(28, 116, "ordinaire", "tm", 11, "start")
    c += texte(75, 65, "27 %", "t", 13, "middle", 700) + texte(75, 32, "matière noire", "tm", 12, "middle")
    c += texte(320, 100, "68 % énergie noire", "tm", 12, "end")
    c += texte(170, 140, "Tout ce qu'on voit tient dans la petite tranche.", "t", 13, "middle", 700)
    return svg(340, 150, c, "Contenu de l'Univers : 5 % de matière ordinaire, 27 % de matière noire, 68 % d'énergie noire")


# --- Géométrie, infini, logique ---------------------------------------------------

def pythagore():
    u = 16
    A, B, C = (100, 150), (100 + 4 * u, 150), (100, 150 - 3 * u)
    c = f'<polygon class="f" points="{A[0]},{A[1]} {B[0]},{B[1]} {C[0]},{C[1]}" stroke-width="2"/>'
    c += f'<rect class="f2" x="{A[0]}" y="{A[1]}" width="{4 * u}" height="{4 * u}" transform="translate(0,0)"/>'
    c += f'<rect class="f2" x="{A[0] - 3 * u}" y="{C[1]}" width="{3 * u}" height="{3 * u}"/>'
    dx, dy = B[0] - C[0], B[1] - C[1]
    pts = [C, B, (B[0] + dy, B[1] - dx), (C[0] + dy, C[1] - dx)]
    c += '<polygon class="ok" points="' + " ".join(f"{p[0]},{p[1]}" for p in pts) + '"/>'
    c += texte(A[0] + 2 * u, A[1] + 2 * u + 5, "16", "t", 14, "middle", 700) + texte(A[0] - 1.5 * u, C[1] + 1.5 * u + 5, "9", "t", 14, "middle", 700)
    cx, cy = sum(p[0] for p in pts) / 4, sum(p[1] for p in pts) / 4
    c += texte(cx, cy + 5, "25", "t", 15, "middle", 700)
    c += texte(A[0] + 2 * u, A[1] - 6, "4", "tm", 12) + texte(A[0] - 6, A[1] - 1.5 * u, "3", "tm", 12, "end") + texte(150, 128, "5", "tm", 12)
    c += texte(300, 210, "9 + 16 = 25 = 5²", "t", 14, "end", 700)
    return svg(340, 222, c, "Triangle 3-4-5 : les carrés des côtés de l'angle droit, 9 et 16, font ensemble le carré de l'hypoténuse, 25")


def serie_moitie():
    x, y, l, h = 60, 20, 220, 140
    c = f'<rect class="f" x="{x}" y="{y}" width="{l}" height="{h}"/>'
    labels = ["1/2", "1/4", "1/8", "1/16", "1/32"]
    cx, cy, w, hh = x, y, l, h
    for i, lab in enumerate(labels):
        cls = "a" if i % 2 == 0 else "ok"
        if i % 2 == 0:
            c += f'<rect class="{cls}" x="{cx}" y="{cy}" width="{w / 2}" height="{hh}" opacity="{0.55 - i * 0.07:.2f}"/>'
            c += texte(cx + w / 4, cy + hh / 2 + 5, lab, "t", max(9, 15 - 2 * i), "middle", 700)
            cx += w / 2; w /= 2
        else:
            c += f'<rect class="{cls}" x="{cx}" y="{cy}" width="{w}" height="{hh / 2}"/>'
            c += texte(cx + w / 2, cy + hh / 4 + 4, lab, "t", max(9, 15 - 2 * i), "middle", 700)
            cy += hh / 2; hh /= 2
    c += texte(170, 180, "Chaque part comble la moitié de ce qui reste : le tout vaut 1.", "tm", 12)
    return svg(340, 190, c, "Un carré rempli par moitiés successives : 1/2, 1/4, 1/8… finissent par le remplir entièrement")


def consequent():
    c = '<ellipse class="f2" cx="170" cy="80" rx="150" ry="66"/><ellipse class="ok" cx="110" cy="84" rx="62" ry="38"/>'
    c += texte(250, 46, "sol mouillé", "t", 13, "middle", 700) + texte(110, 88, "il a plu", "t", 13, "middle", 700)
    c += '<circle class="a" cx="250" cy="96" r="6"/>' + texte(250, 118, "arrosage", "tm", 12)
    c += texte(170, 168, "Mouillé ne veut pas dire « il a plu » : d'autres causes existent.", "tm", 12)
    return svg(340, 178, c, "Le cas « il a plu » est inclus dans « sol mouillé », mais le sol peut être mouillé par l'arrosage")


# --- Biais ------------------------------------------------------------------------

def avion_wald():
    c = ('<path class="f" d="M170 20 L182 60 L182 88 L310 120 L310 136 L182 122 L180 168 L210 186 L210 196 L170 188 '
         'L130 196 L130 186 L160 168 L158 122 L30 136 L30 120 L158 88 L158 60 Z" stroke-width="2"/>')
    trous = [(70, 124), (95, 118), (250, 120), (275, 126), (225, 116), (120, 116), (170, 110), (165, 140), (175, 152), (190, 190), (150, 190)]
    for x, y in trous:
        c += f'<circle class="ko" cx="{x}" cy="{y}" r="3.5"/>'
    for x, y, lab in ((170, 42, "moteur"), (170, 76, "cockpit")):
        c += f'<circle class="ok" cx="{x}" cy="{y}" r="11" fill-opacity="0.6"/>'
    c += f'<circle class="ko" cx="236" cy="26" r="4"/><circle class="ok" cx="236" cy="46" r="5" fill-opacity="0.6"/>'
    c += texte(246, 30, "impacts relevés", "tm", 11, "start") + texte(246, 50, "à blinder", "t", 12, "start", 700)
    return svg(340, 206, c, "Silhouette d'avion : les impacts relevés sont sur les ailes et la queue ; moteur et cockpit, intacts, sont là où les avions touchés ne revenaient pas")


# --- Physique ---------------------------------------------------------------------

def inverse_carre():
    b = 150
    c = barre(70, b, 100, 50, "a", "F", "distance 1") + barre(170, b, 25, 50, "a", "F/4", "distance 2") + barre(270, b, 11, 50, "a", "F/9", "distance 3")
    c += texte(170, 26, "Deux fois plus loin : quatre fois moins", "t", 13, "middle", 700)
    return svg(340, 176, c, "La force de gravitation divisée par 4 à distance double, par 9 à distance triple")


def doppler():
    c = ""
    for i, r in enumerate((18, 36, 54, 72)):
        cx = 170 - i * 14
        c += f'<circle class="lm" cx="{cx}" cy="90" r="{r}" fill="none"/>'
    c += '<circle class="a" cx="170" cy="90" r="7"/>' + fleche(180, 90, 214, 90, "al")
    c += texte(280, 70, "ondes serrées", "t", 12, "middle", 700) + texte(280, 86, "son plus aigu", "tm", 12)
    c += texte(46, 70, "ondes étirées", "t", 12, "middle", 700) + texte(46, 86, "son plus grave", "tm", 12)
    c += texte(170, 176, "La source avance : devant elle, les crêtes se rapprochent.", "tm", 12)
    return svg(340, 186, c, "Une source qui avance vers la droite : ses ondes sont serrées devant elle et étirées derrière")


def boyle():
    def piston(x, h, lab, p):
        c = f'<rect class="f" x="{x}" y="{150 - h}" width="80" height="{h}" rx="2"/>'
        c += f'<rect class="lm" x="{x - 4}" y="{150 - h - 8}" width="88" height="8" fill="none"/><line class="l" x1="{x + 40}" y1="{150 - h - 8}" x2="{x + 40}" y2="20"/>'
        n = 10
        for i in range(n):
            px = x + 10 + (i * 37) % 60
            py = 150 - 8 - (i * 23) % max(10, h - 16)
            c += f'<circle class="a" cx="{px}" cy="{py}" r="3"/>'
        c += texte(x + 40, 170, lab, "t", 13, "middle", 700) + texte(x + 40, 186, p, "tm", 12)
        return c
    c = piston(50, 100, "volume V", "pression P") + piston(210, 50, "volume V/2", "pression 2P")
    c += fleche(140, 100, 196, 100, "al")
    return svg(340, 194, c, "Même gaz, même température : divisé par deux, le volume double la pression ; P × V reste constant")


# --- Chimie, vivant -----------------------------------------------------------------

def demi_vie():
    b = 150
    c = ""
    for i, (h, lab) in enumerate(((112, "1"), (56, "1/2"), (28, "1/4"), (14, "1/8"), (7, "1/16"))):
        x = 50 + i * 60
        c += barre(x, b, h, 36, "a", lab, str(i))
    c += texte(170, 190, "demi-vies écoulées", "tm", 12)
    return svg(340, 200, c, "À chaque demi-vie, il reste la moitié des noyaux : 1, 1/2, 1/4, 1/8, 1/16")


def pyramide_energie():
    c = ""
    niveaux = (("producteurs", "10 000", 200, "ok"), ("herbivores", "1 000", 150, "f"), ("carnivores", "100", 100, "f"), ("super-prédateurs", "10", 50, "a"))
    for i, (nom, e, l, cls) in enumerate(niveaux):
        y = 150 - i * 34
        c += f'<rect class="{cls}" x="{120 - l / 2}" y="{y - 30}" width="{l}" height="30" rx="3"/>'
        c += texte(120, y - 10, e, "t", 13, "middle", 700) + texte(232, y - 10, nom, "tm", 12, "start")
    c += texte(170, 172, "À chaque étage, environ 10 % de l'énergie passe.", "tm", 12)
    return svg(340, 180, c, "Pyramide de l'énergie : 10 000, puis 1 000, 100 et 10 unités en montant d'un niveau à l'autre")


# --- Astronomie -----------------------------------------------------------------------

def canon_newton():
    c = '<circle class="f2" cx="170" cy="150" r="70"/>' + texte(170, 156, "Terre", "tm", 12)
    c += '<rect class="l" x="164" y="72" width="12" height="8"/>'
    c += '<path class="ko" style="fill:none" stroke-width="2" d="M176 76 Q 200 78 206 92"/>'
    c += '<path class="ko" style="fill:none" stroke-width="2" d="M176 76 Q 225 80 230 118"/>'
    c += '<circle class="ok" cx="170" cy="150" r="86" style="fill:none" stroke-width="2.5" stroke-dasharray="6 5"/>'
    c += texte(334, 196, "assez vite :", "t", 12, "end", 700) + texte(334, 212, "elle tombe sans", "tm", 12, "end") + texte(334, 228, "jamais toucher le sol", "tm", 12, "end")
    c += texte(334, 30, "trop lent :", "t", 12, "end", 700) + texte(334, 46, "elle retombe", "tm", 12, "end")
    return svg(340, 244, c, "Le canon de Newton : tirée assez vite depuis une montagne, la balle tombe en contournant la Terre, c'est une orbite")


def marees():
    c = '<ellipse class="ok" cx="110" cy="90" rx="64" ry="46" fill-opacity="0.6"/>' + '<circle class="f" cx="110" cy="90" r="38"/>'
    c += texte(110, 95, "Terre", "t", 13, "middle", 700) + '<circle class="f2" cx="300" cy="90" r="14"/>' + texte(300, 124, "Lune", "tm", 12)
    c += fleche(180, 90, 280, 90, "lm")
    c += texte(110, 30, "deux renflements d'eau :", "tm", 12) + texte(110, 160, "côté Lune et côté opposé", "tm", 12)
    return svg(340, 172, c, "L'attraction de la Lune étire les océans en deux renflements, l'un face à la Lune, l'autre à l'opposé")


def phases_lune():
    noms = ("nouvelle", "croissant", "1er quartier", "gibbeuse", "pleine", "gibbeuse", "dernier q.", "croissant")
    c = ""
    for i, nom in enumerate(noms):
        x, y, r = 30 + i * 40, 50, 15
        c += f'<circle class="f2" cx="{x}" cy="{y}" r="{r}"/>'
        f = i / 8
        if 0 < i < 8 and i != 0:
            # partie éclairée : demi-disque + ellipse (terminateur)
            croissant = i < 4
            k = abs(math.cos(2 * math.pi * f)) * r
            cote = 1 if i < 4 or i == 4 else 0
            if i == 4:
                c += f'<circle class="jaune" cx="{x}" cy="{y}" r="{r}"/>'
            else:
                droite = i < 4
                s = 1 if droite else 0
                bombe = (i in (3, 5))
                c += (f'<path class="jaune" d="M{x} {y - r} A {r} {r} 0 0 {s} {x} {y + r} '
                      f'A {k:.1f} {r} 0 0 {1 - s if not bombe else s} {x} {y - r} Z"/>')
        c += f'<circle class="lm" cx="{x}" cy="{y}" r="{r}" fill="none"/>'
        c += texte(x, y + 32 + (12 if i % 2 else 0), nom, "tm", 10)
    c += texte(170, 112, "Un tour complet ≈ 29,5 jours", "t", 13, "middle", 700)
    return svg(340, 122, c, "Les phases de la Lune, de la nouvelle lune à la pleine lune puis retour, en environ 29,5 jours")


EXPLICATION = {
    "math.proportions.q02": hausse_baisse(),
    "math.proportions.q10": ttc_ht(),
    "math.proportions.q07": points_pourcent(),
    "math.statistiques.q01": mediane_moyenne(),
    "math.statistiques.q07": loi_normale(),
    "math.statistiques.q06": cause_commune(),
    "sci.methode.q02": cause_commune(),
    "astro.sombre.q04": ordinaire_noire(),
    "astro.galaxies.q10": ordinaire_noire(),
    "math.geometrie.q01": pythagore(),
    "math.infini.q01": serie_moitie(),
    "math.logique.q01": consequent(),
    "biais.disponibilite.q07": avion_wald(),
    "phys.forces.q09": inverse_carre(),
    "phys.ondes.q08": doppler(),
    "chim.etats.q04": boyle(),
    "chim.noyau.q02": demi_vie(),
    "sci.ecologie.q04": pyramide_energie(),
    "astro.orbites.q04": canon_newton(),
    "astro.orbites.q05": marees(),
    "astro.observer.q10": phases_lune(),
}
