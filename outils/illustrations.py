"""Schémas SVG des questions.

Chaque schéma est un SVG autonome qui n'utilise que des classes, pour suivre le thème clair ou sombre de la page :
  t  texte principal      tm  texte secondaire    l  trait principal    lm  trait secondaire
  f  forme claire bordée  f2  aplat discret       a  aplat d'accent     al  trait d'accent
  ok aplat « vrai »       ko  aplat « faux »      jaune  Soleil, lumière (couleur fixe)
Une autre application (mobile natif, Unreal) peut les afficher en remplaçant ces classes par ses couleurs.

ENONCE : schéma affiché avec la question. EXPLICATION : schéma affiché après la réponse, quand il la donnerait.
"""


def svg(largeur, hauteur, corps, titre):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largeur} {hauteur}" role="img" aria-label="{titre}">'
            + corps + "</svg>")


def texte(x, y, s, cls="t", taille=14, ancre="middle", poids=None):
    p = f' font-weight="{poids}"' if poids else ""
    return f'<text class="{cls}" x="{x}" y="{y}" font-size="{taille}" text-anchor="{ancre}"{p}>{s}</text>'


# --- Électricité --------------------------------------------------------------

def pile(x, y, etiquette=""):
    """Pile verticale centrée en (x, y) sur un fil vertical : grand trait = borne +."""
    c = (f'<line class="l" x1="{x - 14}" y1="{y - 5}" x2="{x + 14}" y2="{y - 5}"/>'
         f'<line class="l" x1="{x - 7}" y1="{y + 5}" x2="{x + 7}" y2="{y + 5}" stroke-width="4"/>'
         f'<rect class="fond" x="{x - 16}" y="{y - 3}" width="32" height="6"/>')
    c += texte(x - 22, y - 2, "+", "tm", 13, "end") + texte(x - 22, y + 12, "−", "tm", 13, "end")
    if etiquette:
        c += texte(x + 20, y + 5, etiquette, "t", 14, "start", 700)
    return c


def lampe(x, y, etiquette="", cls="f"):
    c = (f'<circle class="{cls}" cx="{x}" cy="{y}" r="12"/>'
         f'<line class="l" x1="{x - 8}" y1="{y - 8}" x2="{x + 8}" y2="{y + 8}"/>'
         f'<line class="l" x1="{x + 8}" y1="{y - 8}" x2="{x - 8}" y2="{y + 8}"/>')
    if etiquette:
        c += texte(x, y - 18, etiquette, "tm", 12)
    return c


def resistance(x, y, etiquette="", vertical=False):
    if vertical:
        c = f'<rect class="f" x="{x - 8}" y="{y - 20}" width="16" height="40" rx="2"/>'
        return c + (texte(x + 14, y + 5, etiquette, "t", 14, "start", 700) if etiquette else "")
    c = f'<rect class="f" x="{x - 20}" y="{y - 8}" width="40" height="16" rx="2"/>'
    return c + (texte(x, y - 14, etiquette, "t", 14, "middle", 700) if etiquette else "")


def fil(*points):
    pts = " ".join(f"{x},{y}" for x, y in points)
    return f'<polyline class="l" points="{pts}"/>'


def circuit_ouvert():
    c = fil((60, 100), (60, 30), (130, 30)) + fil((172, 30), (260, 30), (260, 130), (60, 130), (60, 100))
    c += f'<line class="l" x1="130" y1="30" x2="166" y2="12"/><circle class="f" cx="130" cy="30" r="3"/><circle class="f" cx="172" cy="30" r="3"/>'
    c += texte(151, 52, "interrupteur", "tm", 12)
    c += pile(60, 80) + lampe(260, 80, "")
    c += texte(285, 85, "lampe", "tm", 12, "start")
    return svg(340, 150, c, "Circuit : une pile, un interrupteur ouvert et une lampe")


def circuit_serie():
    c = fil((50, 30), (290, 30), (290, 130), (50, 130), (50, 30))
    c += pile(50, 80) + lampe(130, 30, "lampe 1") + lampe(210, 30, "lampe 2")
    return svg(340, 150, c, "Deux lampes en série sur une même boucle")


def circuit_derivation():
    c = fil((50, 30), (290, 30), (290, 150), (50, 150), (50, 30))
    c += fil((170, 30), (170, 150))
    c += pile(50, 90) + lampe(170, 90, "") + lampe(290, 90, "")
    c += texte(190, 95, "lampe 1", "tm", 12, "start") + texte(308, 95, "lampe 2", "tm", 12, "start")
    return svg(380, 170, c, "Deux lampes en dérivation, chacune sur sa propre branche")


def circuit_ohm():
    c = fil((60, 30), (260, 30), (260, 130), (60, 130), (60, 30))
    c += pile(60, 80, "9 V") + resistance(260, 80, "3 Ω", vertical=True)
    c += '<path class="al" d="M150 18 l12 12 l-12 12" fill="none"/>' + texte(150, 60, "I = ?", "t", 15, "middle", 700)
    return svg(340, 150, c, "Pile de 9 volts reliée à une résistance de 3 ohms")


def resistances_derivation():
    c = fil((40, 80), (90, 80)) + fil((90, 40), (90, 120)) + fil((90, 40), (130, 40)) + fil((170, 40), (210, 40))
    c += fil((90, 120), (130, 120)) + fil((170, 120), (210, 120)) + fil((210, 40), (210, 120)) + fil((210, 80), (260, 80))
    c += resistance(150, 40, "100 Ω") + resistance(150, 120, "100 Ω")
    c += f'<circle class="f" cx="40" cy="80" r="4"/><circle class="f" cx="260" cy="80" r="4"/>'
    return svg(300, 150, c, "Deux résistances de 100 ohms montées en dérivation")


# --- Biais, probabilités, logique ---------------------------------------------

def wason():
    cartes = ["E", "K", "4", "7"]
    c = ""
    for i, s in enumerate(cartes):
        x = 16 + i * 80
        c += f'<rect class="f" x="{x}" y="12" width="64" height="92" rx="8" stroke-width="2"/>'
        c += texte(x + 32, 70, s, "t", 36, "middle", 700)
    c += texte(168, 130, "Règle : si une carte porte une voyelle d'un côté,", "tm", 13)
    c += texte(168, 148, "alors elle porte un nombre pair de l'autre.", "tm", 13)
    return svg(336, 160, c, "Quatre cartes posées sur la table : E, K, 4 et 7")


def monty_hall():
    c = ""
    for i in range(3):
        x = 22 + i * 100
        if i == 2:
            c += f'<rect class="f2" x="{x}" y="14" width="76" height="112" rx="4"/>'
            c += f'<rect class="f" x="{x}" y="14" width="22" height="112" rx="2"/>'
            c += texte(x + 49, 76, "chèvre", "tm", 13)
        else:
            c += f'<rect class="f" x="{x}" y="14" width="76" height="112" rx="4" stroke-width="2"/>'
            c += f'<circle class="l" cx="{x + 62}" cy="74" r="3"/>' + texte(x + 38, 60, str(i + 1), "t", 26, "middle", 700)
    c += texte(60, 146, "votre choix", "t", 13, "middle", 700) + texte(160, 146, "fermée", "tm", 13) + texte(260, 146, "ouverte", "tm", 13)
    return svg(320, 156, c, "Trois portes : vous avez choisi la 1, l'animateur a ouvert la 3 sur une chèvre")


def deux_des():
    c = ""
    for i in range(6):
        c += texte(52 + i * 30, 22, str(i + 1), "tm", 13) + texte(24, 47 + i * 30, str(i + 1), "tm", 13)
        for j in range(6):
            c += f'<rect class="f2" x="{38 + i * 30}" y="{30 + j * 30}" width="28" height="28" rx="3"/>'
    c += texte(130, 222, "36 issues équiprobables (dé 1 × dé 2)", "tm", 12)
    return svg(240, 232, c, "Tableau des 36 résultats possibles avec deux dés")


def arbre_pieces():
    c = fil((30, 90), (110, 45)) + fil((30, 90), (110, 135))
    for y in (45, 135):
        c += fil((130, y), (210, y - 25)) + fil((130, y), (210, y + 25))
    c += texte(120, 50, "P", "t", 15, "middle", 700) + texte(120, 140, "F", "t", 15, "middle", 700)
    issues = [("P", "P", 25, True), ("P", "F", 75, True), ("F", "P", 115, True), ("F", "F", 165, False)]
    for a, b, y, ok in issues:
        c += texte(222, y, b, "t", 15, "middle", 700)
        c += texte(250, y, a + b, "t" if ok else "tm", 13, "start")
        c += texte(290, y, "✓" if ok else "✗", "t" if ok else "tm", 14, "start")
    c += texte(16, 95, "●", "tm", 10)
    return svg(320, 180, c, "Arbre des quatre issues de deux lancers : PP, PF, FP et FF")


def euler():
    c = ('<ellipse class="f2" cx="160" cy="90" rx="150" ry="80"/><ellipse class="f" cx="140" cy="100" rx="95" ry="55"/>'
         '<ellipse class="a" cx="120" cy="108" rx="45" ry="28" opacity="0.35"/>')
    c += texte(270, 40, "C", "t", 18, "middle", 700) + texte(210, 70, "B", "t", 18, "middle", 700) + texte(120, 114, "A", "t", 18, "middle", 700)
    return svg(320, 180, c, "Trois ensembles emboîtés : A dans B, B dans C")


def roue_loterie():
    c = '<circle class="f" cx="90" cy="90" r="72" stroke-width="2"/>'
    for i in range(12):
        import math
        a = i * math.pi / 6
        c += f'<line class="lm" x1="90" y1="90" x2="{90 + 72 * math.cos(a):.1f}" y2="{90 + 72 * math.sin(a):.1f}"/>'
    c += '<circle class="a" cx="90" cy="90" r="6"/><path class="a" d="M90 6 l-8 -2 l8 22 l8 -22 z"/>'
    c += texte(90, 52, "10", "t", 18, "middle", 700) + texte(90, 142, "65", "t", 18, "middle", 700)
    c += texte(250, 70, "Part des pays africains", "tm", 13) + texte(250, 88, "à l'ONU :", "tm", 13) + texte(250, 116, "plus ou moins", "t", 14, "middle", 700) + texte(250, 134, "que le nombre tiré ?", "t", 14, "middle", 700)
    return svg(340, 180, c, "Une roue de loterie qui ne peut tomber que sur 10 ou 65")


def asch():
    c = '<line class="l" x1="70" y1="20" x2="70" y2="140" stroke-width="5"/>' + texte(70, 162, "référence", "tm", 13)
    for i, (h, lettre) in enumerate([(70, "A"), (120, "B"), (95, "C")]):
        x = 190 + i * 50
        c += f'<line class="l" x1="{x}" y1="{140 - h}" x2="{x}" y2="140" stroke-width="5"/>' + texte(x, 162, lettre, "t", 15, "middle", 700)
    return svg(340, 172, c, "Une ligne de référence et trois lignes A, B et C ; B a la même longueur")


def courbe_oubli():
    c = fil((40, 20), (40, 150), (320, 150))
    c += '<path class="al" fill="none" stroke-width="3" d="M40 25 C 60 95, 90 115, 140 124 S 260 132, 320 134"/>'
    for x, y in [(70, 92), (110, 117), (180, 127), (260, 132)]:
        c += f'<circle class="a" cx="{x}" cy="{y}" r="3"/>'
    c += texte(46, 16, "souvenir retenu", "tm", 12, "start") + texte(318, 168, "temps", "tm", 12, "end")
    return svg(340, 176, c, "Courbe de l'oubli : chute rapide au début, puis plus lente")


# --- Physique, chimie, astronomie ---------------------------------------------

def spectre():
    stops = [("0", "#7A2BD9"), ("0.18", "#2B4BE0"), ("0.36", "#18A9C9"), ("0.52", "#2EB04A"), ("0.68", "#F2D22E"), ("0.84", "#F2852E"), ("1", "#D92B2B")]
    g = "".join(f'<stop offset="{o}" stop-color="{col}"/>' for o, col in stops)
    c = f'<defs><linearGradient id="spectre" x1="0" x2="1">{g}</linearGradient></defs><rect x="20" y="30" width="300" height="40" rx="6" fill="url(#spectre)"/>'
    c += texte(20, 92, "400 nm", "tm", 12, "start") + texte(320, 92, "700 nm", "tm", 12, "end") + texte(170, 20, "longueur d'onde croissante →", "tm", 12)
    return svg(340, 100, c, "Spectre visible du violet (400 nm) au rouge (700 nm)")


def echelle_ph():
    import colorsys
    c = ""
    for i in range(15):
        r, g, b = colorsys.hsv_to_rgb((i / 14) * 0.75, 0.75, 0.9)
        c += f'<rect x="{10 + i * 21}" y="24" width="20" height="34" fill="#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"/>'
        c += texte(20 + i * 21, 76, str(i), "t" if i in (3, 7) else "tm", 12, "middle", 700 if i in (3, 7) else None)
    c += texte(60, 16, "acide", "t", 13, "middle", 700) + texte(167, 16, "neutre", "t", 13, "middle", 700) + texte(275, 16, "basique", "t", 13, "middle", 700)
    c += texte(20, 100, "citron ≈ 2", "tm", 12, "start") + texte(167, 100, "eau pure 7", "tm", 12) + texte(325, 100, "Javel ≈ 12", "tm", 12, "end")
    return svg(335, 110, c, "Échelle de pH de 0 à 14 : acide, neutre, basique")


def molecules_eau():
    def h2(x, y):
        return f'<circle class="f" cx="{x}" cy="{y}" r="9"/><circle class="f" cx="{x + 16}" cy="{y}" r="9"/>'
    c = h2(30, 50) + h2(30, 90) + texte(92, 76, "+", "t", 22, "middle", 700)
    c += '<circle class="a" cx="122" cy="70" r="13" opacity="0.6"/><circle class="a" cx="146" cy="70" r="13" opacity="0.6"/>'
    c += texte(196, 78, "→", "t", 26, "middle", 700) + texte(270, 78, "? H₂O", "t", 20, "middle", 700)
    c += texte(38, 128, "2 H₂", "tm", 13) + texte(134, 128, "O₂", "tm", 13)
    return svg(330, 140, c, "Deux molécules de dihydrogène et une de dioxygène")


def punnett():
    c = ""
    entetes = ["A", "a"]
    for i, e in enumerate(entetes):
        c += texte(110 + i * 70, 26, e, "t", 18, "middle", 700) + texte(52, 80 + i * 60, e, "t", 18, "middle", 700)
    cases = [["AA", "Aa"], ["aA", "aa"]]
    for i in range(2):
        for j in range(2):
            cls = "a" if cases[j][i] == "aa" else "f2"
            c += f'<rect class="{cls}" x="{78 + i * 70}" y="{42 + j * 60}" width="64" height="54" rx="6"' + (' opacity="0.45"' if cls == "a" else "") + "/>"
            c += texte(110 + i * 70, 76 + j * 60, cases[j][i], "t", 16, "middle", 700)
    c += texte(260, 76, "parent 2 →", "tm", 12) + texte(260, 136, "aa : 1 case / 4", "t", 13, "middle", 700)
    return svg(320, 170, c, "Tableau de croisement de deux parents Aa")


def lune_entre():
    c = '<circle class="jaune" cx="40" cy="80" r="30"/>' + texte(40, 132, "Soleil", "tm", 12)
    for y in (62, 80, 98):
        c += f'<line class="lm" x1="80" y1="{y}" x2="140" y2="{y}" stroke-dasharray="4 4"/>'
    c += '<circle class="f" cx="170" cy="80" r="12"/><path class="jaune" d="M170 68 a12 12 0 0 0 0 24 z"/>' + texte(170, 112, "Lune", "tm", 12)
    c += '<circle class="a" cx="290" cy="80" r="24" opacity="0.55"/>' + texte(290, 124, "Terre", "tm", 12)
    return svg(340, 140, c, "Le Soleil, la Lune puis la Terre, alignés dans cet ordre")


def kepler():
    c = '<ellipse class="lm" cx="170" cy="80" rx="140" ry="62" fill="none" stroke-width="2"/>'
    c += '<circle class="jaune" cx="80" cy="80" r="16"/>' + texte(80, 116, "Soleil", "tm", 12)
    c += '<circle class="a" cx="30" cy="80" r="8"/>' + texte(18, 62, "A", "t", 16, "middle", 700)
    c += '<circle class="a" cx="310" cy="80" r="8"/>' + texte(322, 62, "B", "t", 16, "middle", 700)
    return svg(340, 150, c, "Orbite elliptique : A est le point le plus proche du Soleil, B le plus éloigné")


def saisons():
    c = '<ellipse class="lm" cx="170" cy="80" rx="130" ry="44" fill="none" stroke-dasharray="5 5"/>'
    c += '<circle class="jaune" cx="170" cy="80" r="18"/>'
    for x, lab in ((40, "juin"), (300, "décembre")):
        c += f'<circle class="f" cx="{x}" cy="80" r="16"/><line class="al" x1="{x - 9}" y1="{58}" x2="{x + 9}" y2="{102}" stroke-width="2.5"/>'
        c += texte(x, 128, lab, "tm", 12)
    c += texte(170, 22, "axe incliné de 23,4°, toujours dans la même direction", "tm", 12)
    return svg(340, 140, c, "La Terre en juin et en décembre, axe toujours incliné du même côté")


def couleurs_etoiles():
    c = ""
    for i, (col, temp) in enumerate([("#9BB0FF", "30 000 °C"), ("#CAD7FF", "10 000 °C"), ("#FFF4E8", "5 500 °C"), ("#FFD2A1", "4 000 °C"), ("#FF9A5C", "3 000 °C")]):
        x = 40 + i * 64
        c += f'<circle cx="{x}" cy="50" r="{22 - i * 2}" fill="{col}" stroke="var(--line)"/>' + texte(x, 100, temp, "tm", 11)
    c += texte(184, 126, "← plus chaude          plus froide →", "tm", 12)
    return svg(340, 136, c, "Couleur des étoiles selon leur température")


def chiasme():
    c = texte(70, 40, "manger", "t", 15, "middle", 700) + texte(250, 40, "vivre", "t", 15, "middle", 700)
    c += texte(70, 120, "vivre", "t", 15, "middle", 700) + texte(250, 120, "manger", "t", 15, "middle", 700)
    c += '<line class="al" x1="105" y1="48" x2="215" y2="106" stroke-width="2"/><line class="al" x1="215" y1="48" x2="105" y2="106" stroke-width="2"/>'
    c += texte(160, 150, "A — B / B — A : les termes se croisent", "tm", 12)
    return svg(320, 160, c, "Schéma du chiasme : manger, vivre, puis vivre, manger")


def fractions():
    c = texte(20, 30, "3/4", "t", 15, "start", 700) + texte(20, 80, "1/8", "t", 15, "start", 700)
    for i in range(4):
        c += f'<rect class="{"a" if i < 3 else "f2"}" x="{70 + i * 60}" y="12" width="58" height="28" rx="3"' + (' opacity="0.5"' if i < 3 else "") + "/>"
    for i in range(8):
        c += f'<rect class="{"a" if i < 1 else "f2"}" x="{70 + i * 30}" y="62" width="28" height="28" rx="3"' + (' opacity="0.5"' if i < 1 else "") + "/>"
    return svg(320, 100, c, "Une barre coupée en 4 dont 3 parts colorées, une barre coupée en 8 dont 1 part colorée")


ENONCE = {
    "biais.confirmation.q02": wason(),
    "math.probabilites.q05": monty_hall(),
    "math.probabilites.q04": deux_des(),
    "math.arithmetique.q01": fractions(),
    "biais.ancrage.q06": roue_loterie(),
    "psy.influence.q01": asch(),
    "chim.reactions.q02": molecules_eau(),
    "astro.systeme.q07": lune_entre(),
    "astro.orbites.q02": kepler(),
    "elec.circuits.q03": circuit_ouvert(),
    "elec.circuits.q06": circuit_serie(),
    "elec.circuits.q07": circuit_derivation(),
    "elec.ohm.q05": circuit_ohm(),
    "elec.ohm.q07": resistances_derivation(),
}

EXPLICATION = {
    "math.probabilites.q03": arbre_pieces(),
    "math.logique.q05": euler(),
    "phys.ondes.q04": spectre(),
    "psy.memoire.q01": courbe_oubli(),
    "sci.genetique.q04": punnett(),
    "chim.acides.q01": echelle_ph(),
    "astro.systeme.q04": saisons(),
    "astro.etoiles.q03": couleurs_etoiles(),
    "rhet.figures.q05": chiasme(),
}
