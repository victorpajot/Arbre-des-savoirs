"""Création du personnage (Victor, 2026-11-03) : espèce, teinte, regard, coiffure, barbe et tenue, en 40 × 48.

Tout se dessine sur la géométrie de l'avatar (data/avatar.json, « corps » et tenue du premier rang), pour que les
accessoires (lunettes, chapeaux, moustache) et les farces d'Alyca tombent juste sur toutes les espèces.

Les calques se recolorent dans le jeu, sans redessiner :
  corps     familles peau (6 S s 7 : pelage ou peau), parchemin (A V v : museau, ventre), cheveux (8 h 9 : taches,
            rayures) ; chaque teinte de l'espèce remplace ces caractères.
  coiffure  et barbe : famille cheveux (8 h 9), remplacée par la couleur de cheveux choisie.
  tenue     emplacements ! X * (haut), ~ Z (bas), + Q (détails), comme les rangs ; couleur principale au choix.

    python3 outils/creation.py              écrit « creation » dans packs/socle/donnees/avatar.json
    python3 outils/creation.py planche.png  et dessine une planche de toutes les pièces
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dessin import (PALETTE, Toile, bande, courbe, depuis_lignes, disque, ellipse, ellipse_tournee, miroir, poly, rect,
                    trait)

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "packs" / "socle" / "donnees" / "avatar.json"
L, H = 40, 48


def fr(t):
    return {"fr": t}


AV = json.loads(SOURCE.read_text(encoding="utf-8"))
CORPS = depuis_lignes(AV["corps"])
TENUE0 = depuis_lignes(AV["rangs"][0]["tenue"])

# Yeux du corps d'origine : deux pavés 2 × 3 (reflet blanc en haut à gauche).
YEUX = rect(14, 13, 15, 15) | rect(24, 13, 25, 15)
TETE = {p for p in CORPS.px if p[1] <= 27}
TETE_INT = {p for p in TETE if CORPS.px[p] != "k"}
MAINS = {p for p in CORPS.px if p[1] > 27}
MAINS_INT = {p for p in MAINS if CORPS.px[p] != "k"}


def toile():
    return Toile(L, H)


def hexa(r, g, b):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(c)))) for c in (r, g, b))


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def nuance(h, f):
    """Assombrit (f < 1) ou éclaircit (f > 1)."""
    r, g, b = rgb(h)
    if f < 1:
        return hexa(r * f, g * f, b * f)
    return hexa(r + (255 - r) * (f - 1), g + (255 - g) * (f - 1), b + (255 - b) * (f - 1))


def gamme(base, n):
    """n teintes du sombre au clair autour d'une couleur moyenne."""
    if n == 4:
        return [nuance(base, 0.62), nuance(base, 0.84), base, nuance(base, 1.38)]
    if n == 3:
        return [nuance(base, 0.66), base, nuance(base, 1.35)]
    return [nuance(base, 0.7), base]


def teinte(id_, nom, peau, museau=None, marque=None):
    c = dict(zip("6Ss7", gamme(peau, 4)))
    c.update(zip("AVv", gamme(museau or nuance(peau, 1.45), 3)))
    c.update(zip("8h9", gamme(marque or nuance(peau, 0.55), 3)))
    return {"id": id_, "nom": fr(nom), "couleurs": c}


# --- Corps --------------------------------------------------------------------------

def corps_humain():
    t = toile()
    t.px.update(CORPS.px)
    for (x, y) in YEUX:
        voisin = (13, y) if x < 20 else (26, y)
        t.px[(x, y)] = CORPS.px.get(voisin, "s")
    return t


def corps_nu(base=2):
    """Tête et mains repeintes en pelage (famille peau), sans yeux ni bouche."""
    t = toile()
    t.peindre(TETE_INT, "peau", "sphere", base, mini=1)
    t.peindre(MAINS_INT, "peau", "sphere", base, mini=1)
    for p in TETE | MAINS:
        if CORPS.px[p] == "k":
            t.px[p] = "k"
    return t


def finir(t, extra=()):
    """Contour autour de ce qui dépasse de la tête (oreilles, antennes) ; les traits internes restent."""
    for p in extra:
        t.px.pop(p, None)
    t.contour()
    return t


def oreilles_chat(t, rose=True):
    g = poly([(7.5, 10), (9.5, 0.5), (16, 5)])
    t.peindre(g | miroir(g, L), "peau", "biseau", 2)
    if rose:
        i = poly([(9.5, 8), (10.3, 3), (13.5, 5.5)])
        t.poser(i | miroir(i, L), "I")


def moustaches(t):
    for y0, y1 in ((17, 16), (19, 20)):
        t.poser(trait(5, y1, 9, y0), "n")
        t.poser(miroir(trait(5, y1, 9, y0), L), "n")


def chat():
    t = corps_nu()
    oreilles_chat(t)
    t.contour()
    t.peindre(ellipse(20, 19, 5.6, 3.6), "parchemin", "sphere", 1)
    t.poser(rect(16, 4, 16, 7) | rect(20, 3, 20, 7) | rect(24, 4, 24, 7) | {(11, 11), (12, 12), (28, 11), (27, 12)}, "h")
    t.poser({(19, 17), (20, 17), (19, 18) , (20, 18)}, "F")
    t.poser({(19, 17)}, "I")
    t.poser({(17, 20), (18, 21), (19, 20), (20, 20), (21, 21), (22, 20)}, "k")
    moustaches(t)
    return t


def chien():
    t = corps_nu()
    t.contour()
    o = ellipse(7, 15, 3.6, 7.5)
    t.peindre(o | miroir(o, L), "cheveux", "sphere", 1)
    t.peindre(ellipse(20, 19.5, 6.5, 4.2), "parchemin", "sphere", 1)
    t.peindre(ellipse(26, 11, 4.2, 3.6), "cheveux", "sphere", 1)
    t.peindre(ellipse(20, 17, 2.6, 1.6), "gris", "sphere", 0, maxi=1)
    t.poser({(19, 16)}, "g")
    t.poser({(20, 19), (20, 20), (18, 21), (19, 21), (21, 21), (22, 21)}, "k")
    t.poser({(20, 22), (21, 22), (20, 23), (21, 23)}, "I")
    t.poser({(21, 23)}, "F")
    t.contour()
    return t


def lapin():
    t = corps_nu()
    o = bande((14.5, 8), (11.5, 0), 2.4, 2.0)
    t.peindre(o | miroir(o, L), "peau", "biseau", 2)
    t.contour()
    t.poser(trait(14, 6, 12, 1) | miroir(trait(14, 6, 12, 1), L), "I")
    t.peindre(disque(17.5, 19, 2.8) | disque(22.5, 19, 2.8), "parchemin", "sphere", 2)
    t.poser({(19, 17), (20, 17), (20, 18), (19, 18)}, "I")
    t.poser(rect(18, 21, 21, 23), "w")
    t.poser(rect(18, 24, 21, 24) | {(20, 21), (20, 22), (20, 23)} | {(17, 21), (17, 22), (17, 23), (22, 21), (22, 22), (22, 23)}, "k")
    t.poser({(19, 21), (19, 22)}, "z")
    moustaches(t)
    return t


def panda():
    t = corps_nu(3)
    o = disque(9, 5, 3.6)
    t.peindre(o | miroir(o, L), "cheveux", "sphere", 1)
    t.contour()
    for cx in (14.5, 25.5):
        tache = ellipse(cx, 14.5, 3.4, 4.4)
        t.peindre(tache, "cheveux", "sphere", 0, maxi=1)
    t.peindre(ellipse(20, 19.5, 5, 3.4), "parchemin", "sphere", 2)
    t.peindre(ellipse(20, 17.5, 2.2, 1.4), "cheveux", "plat", 0)
    t.poser({(20, 19), (18, 21), (19, 20), (21, 20), (22, 21)}, "k")
    return t


def grenouille():
    t = corps_nu()
    b = disque(13.5, 6.5, 4.2)
    t.peindre(b | miroir(b, L), "peau", "sphere", 2)
    t.contour()
    t.peindre({(x, y) for (x, y) in ellipse(20, 23, 10, 5) if (x, y) in TETE_INT}, "parchemin", "sphere", 2)
    t.poser(courbe([(9, 18), (12, 20), (20, 21), (28, 20), (31, 18)]), "k")
    t.poser({(18, 16), (21, 16)}, "8")
    t.poser({(10, 17), (11, 17), (29, 17), (28, 17)}, "I")
    return t


def cochon():
    t = corps_nu()
    o = poly([(8, 9), (8.5, 1.5), (15.5, 5.5)])
    t.peindre(o | miroir(o, L), "parchemin", "biseau", 1)
    t.contour()
    t.peindre(ellipse(20, 18.5, 4.4, 3.2), "parchemin", "sphere", 1)
    t.poser({(18, 18), (18, 19), (22, 18), (22, 19)}, "8")
    t.poser({(17, 22), (18, 23), (19, 23), (20, 23), (21, 23), (22, 22)}, "k")
    t.poser({(11, 18), (12, 18), (27, 18), (28, 18)}, "I")
    return t


def paresseux():
    t = corps_nu(3)
    t.peindre({(x, y) for (x, y) in TETE_INT if y <= 8 or (y <= 14 and (x <= 9 or x >= 30))}, "cheveux", "sphere", 2)
    for sens in (1, -1):
        b = bande((20 - sens * 4, 13), (20 - sens * 9.5, 18.5), 2.0, 1.6)
        t.peindre(b, "cheveux", "plat", 0)
    t.peindre(ellipse(20, 17.5, 2.4, 1.6), "cheveux", "plat", 0)
    t.poser({(19, 17)}, "G")
    t.poser(courbe([(16, 20), (18, 21.5), (22, 21.5), (24, 20)]), "k")
    t.contour()
    return t


def hibou():
    t = corps_nu()
    o = poly([(7, 9), (6, 0), (13, 4.5)])
    t.peindre(o | miroir(o, L), "cheveux", "biseau", 1)
    t.contour()
    for cx in (14.5, 25.5):
        t.peindre(disque(cx, 14.5, 5.2), "parchemin", "sphere", 2)
        t.peindre(disque(cx, 14.5, 2.9), "or", "sphere", 2)
    t.peindre(poly([(18, 17), (22, 17), (20, 22)]), "orange", "biseau", 1)
    for (x, y) in TETE_INT:
        if y >= 21 and (x * 3 + y * 5) % 7 == 0 and t.px.get((x, y)) in "6Ss7":
            t.px[(x, y)] = "h"
    return t


def petit_gris():
    t = corps_nu(2)
    t.contour()
    for sens in (1, -1):
        cx = 20 - sens * 5.8
        oeil = {(x, y) for (x, y) in ellipse(0, 0, 4.4, 2.6)}
        import math
        a = math.radians(28 * sens)
        pts = set()
        for (x, y) in ellipse(cx, 14, 4.6, 2.8):
            pts.add((x, y))
        # Œil en amande incliné : on tourne l'ellipse autour de son centre.
        rot = set()
        for y in range(8, 21):
            for x in range(8, 33):
                u, v = x + 0.5 - cx, y + 0.5 - 14
                ur = u * math.cos(a) + v * math.sin(a)
                vr = -u * math.sin(a) + v * math.cos(a)
                if (ur / 4.6) ** 2 + (vr / 2.6) ** 2 <= 1:
                    rot.add((x, y))
        t.poser(rot, "N")
        t.poser({(int(cx) - 1, 13)}, "K")
        t.poser({(int(cx) - 2, 13)}, "z")
    t.poser({(19, 21), (20, 21)}, "k")
    t.poser({(19, 18), (21, 18)}, "6")
    return t


def antennes(t, boule="or"):
    for sens in (1, -1):
        a = (20 - sens * 6, 5)
        b = (20 - sens * 10, 1)
        t.poser(trait(*a, *b), "k")
        t.peindre(disque(b[0] + 0.5, b[1] + 0.5, 1.6), boule, "sphere", 2)


def martien():
    t = corps_nu()
    t.contour()
    antennes(t)
    t.poser(courbe([(15, 19), (17, 21), (23, 21), (25, 19)]), "k")
    t.poser({(13, 9), (26, 8), (11, 19), (29, 18)}, "8")
    return t


def cyclope():
    t = corps_nu()
    t.peindre(poly([(18, 5), (20, -1), (22, 5)]), "or", "biseau", 2)
    t.contour()
    t.peindre(ellipse(20, 13, 5.6, 4.6), "gris", "sphere", 4, mini=3)
    t.poser(ellipse(20, 13, 5.6, 4.6) - ellipse(20, 13, 4.6, 3.6), "k")
    t.peindre(disque(20, 13.5, 2.3), "nuit", "plat", 0)
    t.poser({(19, 12)}, "w")
    t.poser(courbe([(15, 20), (18, 22), (22, 22), (25, 20)]), "k")
    t.poser({(18, 22), (22, 22)}, "w")
    return t


def trois_yeux():
    t = corps_nu()
    o = bande((8, 13), (2, 6), 1.6, 1.0)
    t.peindre(o | miroir(o, L), "peau", "biseau", 2)
    t.contour()
    t.poser(rect(19, 6, 20, 8), "n")
    t.poser({(19, 6)}, "w")
    t.poser(ellipse(19.5, 7, 2.6, 2.6) - rect(19, 6, 20, 8) - {(17, 5), (22, 5), (17, 9), (22, 9)}, "8")
    t.poser(courbe([(16, 20), (20, 21), (24, 20)]), "k")
    t.poser({(17, 21), (23, 21)}, "k")
    return t


def robot():
    t = toile()
    t.peindre(TETE_INT, "gris", "biseau", 3, mini=1, maxi=4)
    t.peindre(MAINS_INT, "gris", "sphere", 3, mini=1)
    for p in TETE | MAINS:
        if CORPS.px[p] == "k":
            t.px[p] = "k"
    t.poser(trait(20, 3, 20, 0), "k")
    t.peindre(disque(20.5, 0.5, 1.4), "rouge", "sphere", 2)
    t.contour()
    t.poser({(9, 9), (30, 9), (9, 20), (30, 20)}, "G")
    t.poser(rect(12, 12, 17, 16) | rect(22, 12, 27, 16), "k")
    t.poser(rect(13, 13, 16, 15) | rect(23, 13, 26, 15), "C")
    t.poser({(13, 13), (23, 13)}, "d")
    t.poser({(14, 13), (24, 13)}, "c")
    t.poser(rect(15, 19, 24, 22), "k")
    t.poser({(x, y) for x in range(16, 24) for y in (20, 21) if x % 2 == 0}, "z")
    # Les teintes du robot remplacent le gris de la tête (G g z l) via la famille peau, comme un pelage.
    for p, ch in list(t.px.items()):
        t.px[p] = {"G": "6", "g": "S", "z": "s", "l": "7"}.get(ch, ch) if p not in rect(15, 19, 24, 22) and p not in rect(12, 12, 27, 16) else ch
    return t


def patate():
    t = corps_nu(2)
    b = disque(9, 9, 3.2) | disque(31, 12, 2.6) | disque(20, 3.5, 2.6)
    t.peindre(b, "peau", "sphere", 2)
    t.contour()
    for (x, y) in [(12, 7), (27, 6), (11, 19), (29, 20), (22, 4), (17, 23), (31, 12)]:
        t.poser({(x, y), (x + 1, y)}, "8")
    t.poser(rect(19, 0, 19, 2), "e")
    t.poser({(18, 0), (20, 1)}, "E")
    t.poser(courbe([(16, 20), (18, 21), (22, 21), (24, 20)]), "k")
    t.poser({(20, 17), (20, 18)}, "6")
    return t


def humain_fige():
    return corps_humain()


PEAUX_HUMAINES = [
    ("claire", "Claire", "#F2C9A0"), ("rosee", "Rosée", "#F0B9A0"), ("halee", "Hâlée", "#D9A07A"),
    ("mate", "Mate", "#B98059"), ("foncee", "Foncée", "#94603C"), ("ebene", "Ébène", "#6E4429"),
    ("coup-de-soleil", "Coup de soleil", "#F07A6A"),
]


def teintes_humaines():
    out = []
    for id_, nom, base in PEAUX_HUMAINES:
        g = gamme(base, 4)
        out.append({"id": id_, "nom": fr(nom), "couleurs": dict(zip("6Ss7", [g[0], g[1], g[2], g[3]]))})
    out[0]["couleurs"] = {}
    return out


CATEGORIES = [
    {"id": "humain", "nom": fr("Humain")},
    {"id": "animal", "nom": fr("Animal")},
    {"id": "extraterrestre", "nom": fr("Extraterrestre")},
    {"id": "inclassable", "nom": fr("Inclassable")},
]

ESPECES = [
    ("humain", "humain", "Humain", corps_humain, True, "court",
     "Un humain. Audacieux. Personne n'y avait pensé.", teintes_humaines()),
    ("chat", "animal", "Chat", chat, True, "chauve",
     "Un chat. Tu vas donc pousser mes questions du bord de la table, une par une, en me regardant.",
     [teinte("roux", "Roux", "#E8873A", "#FBE3C8", "#A95A1F"), teinte("noir", "Noir", "#3A3640", "#5D6470", "#1E1A2B"),
      teinte("gris", "Gris", "#9AA0A8", "#E8E8EE", "#5D6470"), teinte("blanc", "Blanc", "#F4F1EA", "#FFFFFF", "#C9CED6"),
      teinte("tigre", "Tigré", "#C99260", "#F7EBD0", "#3E2614")]),
    ("chien", "animal", "Chien", chien, True, "chauve",
     "Un chien. Enthousiaste, loyal, et persuadé que chaque réponse mérite une friandise.",
     [teinte("fauve", "Fauve", "#D9A07A", "#FBE3C8", "#6B4226"), teinte("tache", "Blanc taché", "#F4F1EA", "#FFFFFF", "#2B2B33"),
      teinte("chocolat", "Chocolat", "#6E4429", "#C99260", "#2A1A0E"), teinte("gris", "Gris souris", "#9AA0A8", "#E8E8EE", "#2C3559")]),
    ("lapin", "animal", "Lapin", lapin, True, "chauve",
     "Un lapin. Tu ne finiras jamais une masterclass, tu seras déjà ailleurs.",
     [teinte("blanc", "Blanc", "#F4F1EA", "#FFFFFF", "#C9CED6"), teinte("gris", "Gris", "#9AA0A8", "#E8E8EE", "#5D6470"),
      teinte("caramel", "Caramel", "#C99260", "#FBE3C8", "#7A3E1E")]),
    ("panda", "animal", "Panda", panda, True, "chauve",
     "Un panda. Noir et blanc, comme tes réponses : tout juste ou tout faux.",
     [teinte("classique", "Classique", "#F4F1EA", "#FFFFFF", "#2B2B33"), teinte("pastel", "Pastel", "#FBE3EE", "#FFFFFF", "#5E2F8A")]),
    ("grenouille", "animal", "Grenouille", grenouille, True, "chauve",
     "Une grenouille. Tu sautes aux conclusions, c'est cohérent.",
     [teinte("verte", "Verte", "#4CAF50", "#D6F0B0", "#1B4D20"), teinte("tomate", "Tomate", "#D94141", "#FBE3C8", "#5E1414"),
      teinte("bleue", "Bleue", "#3D63D9", "#D8F4FC", "#1A2C66")]),
    ("cochon", "animal", "Cochon", cochon, True, "chauve",
     "Un cochon. Je ne dirai rien. Je pense très fort, mais je ne dirai rien.",
     [teinte("rose", "Rose", "#F2A5B0", "#E07A8C", "#7A3E1E"), teinte("tirelire", "Tirelire dorée", "#F2C14E", "#B8862B", "#7A5418")]),
    ("paresseux", "animal", "Paresseux", paresseux, True, "chauve",
     "Un paresseux. Enfin un personnage qui assume le rythme de tes rappels.",
     [teinte("sable", "Sable", "#E8D5B0", "#F7EBD0", "#5E3B1C"), teinte("mousse", "Moussu", "#B8C79A", "#E8EED8", "#3E2614")]),
    ("hibou", "animal", "Hibou", hibou, True, "chauve",
     "Un hibou, symbole de la sagesse. Le costume ne fait pas le savant, mais il aide.",
     [teinte("brun", "Brun", "#9A6534", "#F7EBD0", "#3E2614"), teinte("neige", "Neige", "#F4F1EA", "#FFFFFF", "#2B2B33"),
      teinte("gris", "Gris", "#9AA0A8", "#E8E8EE", "#2B2B33")]),
    ("petit-gris", "extraterrestre", "Petit gris", petit_gris, False, "chauve",
     "Un petit gris. Venu de très loin pour apprendre les fractions. Courage.",
     [teinte("gris", "Gris", "#B4BAC4", "#E8E8EE", "#5D6470"), teinte("bleute", "Bleuté", "#9FB4D9", "#D8F4FC", "#24408F")]),
    ("martien", "extraterrestre", "Martien", martien, True, "chauve",
     "Un petit homme vert à antennes. Tu captes tout, sauf la réponse.",
     [teinte("vert", "Vert", "#7CC46A", "#D6F0B0", "#2E7D32"), teinte("fluo", "Vert fluo", "#B6F23C", "#EEFFC0", "#4A8A10")]),
    ("cyclope", "extraterrestre", "Cyclope", cyclope, False, "chauve",
     "Un cyclope. Un seul œil, donc la moitié des erreurs de lecture. En théorie.",
     [teinte("violet", "Violet", "#9B59D0", "#CDA6EE", "#3B1A5C"), teinte("orange", "Orange", "#E8873A", "#F7B77A", "#A95A1F")]),
    ("trois-yeux", "extraterrestre", "Trois-yeux", trois_yeux, True, "chauve",
     "Trois yeux. Un pour la question, un pour la réponse, un pour me surveiller. Je vois clair dans ton jeu.",
     [teinte("bleu", "Bleu", "#5BA8E0", "#D8F4FC", "#1A2C66"), teinte("rose", "Rose", "#F28FB0", "#FFE3F2", "#B5476B")]),
    ("robot", "inclassable", "Robot", robot, False, "chauve",
     "Un robot. Tu vas me faire concurrence ? Mignon.",
     [teinte("chrome", "Chrome", "#C9CED6", "#E8E8EE", "#5D6470"), teinte("rouille", "Rouillé", "#C2703A", "#E39A6B", "#7A3E1E"),
      teinte("dore", "Doré", "#F2C14E", "#FFE79A", "#7A5418")]),
    ("patate", "inclassable", "Pomme de terre", patate, True, "chauve",
     "Une pomme de terre. Sur un canapé, avec un quiz. Le destin est parfois limpide.",
     [teinte("charlotte", "Charlotte", "#D9B07A", "#F7EBD0", "#6B4226"), teinte("douce", "Patate douce", "#C2563A", "#E39A6B", "#5E1414")]),
]

# --- Regards (sur les espèces aux yeux « standard ») -------------------------------------


def regard(nom):
    t = toile()
    g, d = (14, 13), (24, 13)
    if nom == "normal":
        for x0, y0 in (g, d):
            t.poser(rect(x0, y0, x0 + 1, y0 + 2), "n")
            t.poser({(x0, y0)}, "w")
    elif nom == "endormi":
        for x0, y0 in (g, d):
            t.poser({(x0 - 1, y0 + 1), (x0, y0 + 2), (x0 + 1, y0 + 2), (x0 + 2, y0 + 1)}, "n")
    elif nom == "blase":
        for x0, y0 in (g, d):
            t.poser(rect(x0 - 1, y0, x0 + 2, y0), "k")
            t.poser(rect(x0 + 1, y0 + 1, x0 + 2, y0 + 2), "n")
    elif nom == "louche":
        for (x0, y0), dx in ((g, 1), (d, -1)):
            t.poser(rect(x0 - 1, y0 - 1, x0 + 2, y0 + 2), "w")
            t.poser(rect(x0 - 1, y0 - 1, x0 + 2, y0 - 1) | rect(x0 - 1, y0 + 3, x0 + 2, y0 + 3), "k")
            t.poser(rect(x0 - 2, y0, x0 - 2, y0 + 2) | rect(x0 + 3, y0, x0 + 3, y0 + 2), "k")
            px = x0 + 1 if dx > 0 else x0 - 1
            t.poser(rect(px, y0 + 1, px + 1, y0 + 2), "n")
    elif nom == "ecarquille":
        for x0, y0 in (g, d):
            t.poser(rect(x0 - 1, y0 - 1, x0 + 2, y0 + 2), "w")
            t.poser(rect(x0 - 1, y0 - 2, x0 + 2, y0 - 2) | rect(x0 - 1, y0 + 3, x0 + 2, y0 + 3), "k")
            t.poser(rect(x0 - 2, y0 - 1, x0 - 2, y0 + 2) | rect(x0 + 3, y0 - 1, x0 + 3, y0 + 2), "k")
            t.poser({(x0, y0 + 1), (x0 + 1, y0 + 1)}, "n")
    elif nom == "etoiles":
        for x0, y0 in (g, d):
            t.poser({(x0, y0 - 1), (x0 + 1, y0 - 1), (x0 - 1, y0 + 1), (x0 + 2, y0 + 1), (x0, y0 + 3), (x0 + 1, y0 + 3)} | rect(x0, y0, x0 + 1, y0 + 2), "y")
            t.poser({(x0, y0 + 1), (x0 + 1, y0 + 1)}, "j")
    elif nom == "furieux":
        for (x0, y0), s in ((g, 1), (d, -1)):
            t.poser(rect(x0, y0 + 1, x0 + 1, y0 + 2), "n")
            sourcil = {(x0 - 1, y0 - 2 + (0 if s > 0 else 2)), (x0, y0 - 1 + (0 if s > 0 else 0)), (x0 + 1, y0 - 1 + (1 if s > 0 else -1) * 0), (x0 + 2, y0 + (0 if s > 0 else -2))}
            t.poser(trait(x0 - 1, y0 - 1, x0 + 2, y0 + 1) if s > 0 else trait(x0 - 1, y0 + 1, x0 + 2, y0 - 1), "k")
    return t


REGARDS = [
    ("normal", "Normal", "Un regard normal. On commence prudemment."),
    ("ecarquille", "Écarquillé", "Les yeux grands ouverts, comme devant une question de probabilités."),
    ("endormi", "Endormi", "Les yeux fermés. Tu as donc déjà vu mes questions ? Non ? Alors réveille-toi."),
    ("blase", "Blasé", "Le regard de quelqu'un qui a tout lu. Tu n'as pas tout lu."),
    ("louche", "Qui louche", "Tu louches. Ça explique beaucoup de tes réponses."),
    ("furieux", "Furieux", "Le regard noir. Garde-le pour mes questions de logique."),
    ("etoiles", "Étoiles", "Des étoiles plein les yeux. Elles partiront à la première question de chimie."),
]

# --- Coiffures (sur la tête de l'avatar : 28 px de large, front à la ligne 11) ------------

VISAGE = {(x, y) for (x, y) in ellipse(20, 16.5, 11.2, 10) if y >= 11}


def calotte(bas=9, cotes=15):
    """Le dessus du crâne, et les tempes jusqu'à la ligne `cotes`."""
    z = set()
    for (x, y) in ellipse(20, 10.5, 13.6, 10.8):
        if y <= bas or ((x <= 10 or x >= 29) and y <= cotes):
            z.add((x, y))
    return z - VISAGE


def coiffure(nom):
    t = toile()
    if nom == "court":
        t.px.update(depuis_lignes(AV["cheveux"]).px)
        return t
    if nom == "chauve":
        return t
    if nom == "raie":
        z = calotte(8, 16)
        z |= {(x, y) for (x, y) in ellipse(20, 10.5, 13.6, 10.8) if x >= 15 and y <= 11 - (x - 15) // 4} - VISAGE
        t.peindre(z, "cheveux", "sphere", 1)
        t.poser(trait(15, 1, 14, 8), "8")
    elif nom == "longs":
        z = calotte(8, 16) | rect(5, 9, 9, 31) | rect(30, 9, 34, 31)
        t.peindre(z - VISAGE, "cheveux", "sphere", 1)
        t.poser(trait(20, 0, 20, 6), "8")
    elif nom == "afro":
        z = set()
        for cx, cy, r in [(20, 7, 12), (9, 10, 7.5), (31, 10, 7.5), (6, 17, 5), (34, 17, 5), (13, 3, 6), (27, 3, 6)]:
            z |= disque(cx, cy, r)
        z -= VISAGE
        z = {(x, y) for (x, y) in z if y <= 24}
        t.peindre(z, "cheveux", "sphere", 1)
        for (x, y) in list(z):
            if (x * 5 + y * 3) % 9 == 0:
                t.px[(x, y)] = "8"
    elif nom == "ebouriffe":
        z = set()
        for cx, cy, r in [(12, 6, 5), (20, 4, 5.5), (28, 6, 5), (7, 12, 4.5), (33, 12, 4.5), (15, 2, 4), (25, 2, 4), (5, 18, 3), (35, 18, 3)]:
            z |= disque(cx, cy, r)
        for a, b in [((10, 4), (4, 0)), ((30, 4), (36, 0)), ((20, 3), (20, -1)), ((6, 14), (1, 12)), ((34, 14), (39, 12))]:
            z |= bande(a, b, 1.6, 0.6)
        t.peindre(z - VISAGE, "cheveux", "sphere", 2)
    elif nom == "crete":
        z = set()
        for i, x in enumerate(range(14, 26, 3)):
            z |= poly([(x - 1, 10), (x + 1.5, -1 + (i % 2) * 2), (x + 4, 10)])
        z |= rect(16, 4, 24, 10)
        t.peindre(z - VISAGE, "cheveux", "biseau", 1)
    elif nom == "chignon":
        z = calotte(7, 13) | disque(20, 2, 4.2)
        t.peindre(z - VISAGE, "cheveux", "sphere", 1)
        t.poser(courbe([(16, 5), (20, 6), (24, 5)]), "k")
    elif nom == "couettes":
        z = calotte(8, 13)
        for cx in (4.5, 35.5):
            z |= ellipse(cx, 18, 3.6, 6) | bande((cx, 12), (20 + (cx - 20) * 0.62, 10), 1.6)
        t.peindre(z - VISAGE, "cheveux", "sphere", 1)
        t.peindre(disque(7.5, 12, 1.6) | disque(32.5, 12, 1.6), "rouge", "sphere", 2)
    elif nom == "banane":
        z = calotte(8, 15) | ellipse(15, 3.5, 10, 4.5) | ellipse(10, 6, 5, 4)
        t.peindre(z - VISAGE, "cheveux", "sphere", 1)
        t.poser(courbe([(6, 6), (12, 2), (22, 1)]), "9")
    elif nom == "bol":
        z = {(x, y) for (x, y) in ellipse(20, 11, 14, 11) if y <= 11}
        z |= rect(6, 11, 9, 16) | rect(30, 11, 33, 16)
        t.peindre(z, "cheveux", "sphere", 1)
        t.poser(rect(10, 11, 29, 11), "8")
    elif nom == "mulet":
        z = calotte(7, 13) | rect(6, 13, 9, 27) | rect(30, 13, 33, 27)
        for (x, y) in list(z):
            if y >= 22 and (x + y) % 3 == 0:
                z.discard((x, y))
        t.peindre(z - VISAGE, "cheveux", "sphere", 1)
    elif nom == "tonsure":
        z = rect(6, 8, 10, 18) | rect(29, 8, 33, 18) | {(x, y) for (x, y) in ellipse(20, 10.5, 13.6, 10.8) if 6 <= y <= 9 and (x <= 13 or x >= 26)}
        t.peindre(z - VISAGE, "cheveux", "sphere", 1)
    t.contour()
    return t


COIFFURES = [
    ("court", "Courts", "Des cheveux courts. Pratique, sobre, sans risque. Comme toi au premier quiz."),
    ("chauve", "Chauve", "Rien sur le crâne. Plus de place pour les idées, en théorie."),
    ("raie", "Raie sur le côté", "La raie sur le côté du premier de la classe. On verra bien."),
    ("longs", "Longs", "Des cheveux longs, pour avoir quelque chose à arracher quand je pose une question de logique."),
    ("afro", "Afro", "Une afro magnifique. Elle a plus de volume que tes connaissances, pour l'instant."),
    ("ebouriffe", "Savant fou", "La coiffure du savant fou. Le savant viendra plus tard, la folie est déjà là."),
    ("crete", "Crête", "Une crête. Rebelle, contre qui ? Contre la courbe de l'oubli ? Bon courage."),
    ("chignon", "Chignon", "Un chignon bien serré, comme ton emploi du temps de révisions. Ah non."),
    ("couettes", "Couettes", "Des couettes. Je ne savais pas qu'on jouait au jardin d'enfants. Ça me va."),
    ("banane", "Banane", "La banane d'un rockeur des années 1950. Le rock est mort, la banane résiste."),
    ("bol", "Coupe au bol", "La coupe au bol. Faite avec un vrai bol, ça se voit."),
    ("mulet", "Mulet", "La nuque longue. Le business devant, la fête derrière, l'ignorance partout."),
    ("tonsure", "Tonsure", "La tonsure du moine copiste. Tu vas recopier mes réponses ? Je te vois."),
]

COULEURS_CHEVEUX = [
    ("chatain", "Châtain", "#9C6B43"), ("brun", "Brun", "#6B4226"), ("noir", "Noir", "#33303A"), ("roux", "Roux", "#D96A2B"),
    ("blond", "Blond", "#F2D27A"), ("gris", "Gris", "#A8ADB5"), ("blanc", "Blanc", "#F0EEE8"), ("bleu", "Bleu électrique", "#3D63D9"),
    ("rose", "Rose bonbon", "#F06AAE"), ("vert", "Vert pomme", "#6CC94A"), ("violet", "Violet", "#9B59D0"),
]


def couleurs_cheveux():
    out = []
    for id_, nom, base in COULEURS_CHEVEUX:
        g = gamme(base, 3)
        out.append({"id": id_, "nom": fr(nom), "couleurs": dict(zip("8h9", g))})
    return out


# --- Barbes --------------------------------------------------------------------------------

def barbe(nom):
    t = toile()
    if nom == "aucune":
        return t
    if nom == "bouc":
        z = poly([(16.5, 20), (23.5, 20), (22.5, 27), (20, 29), (17.5, 27)])
        t.peindre(z, "cheveux", "sphere", 1)
        t.poser({(18, 21), (19, 21), (20, 21), (21, 21)}, "1")
    elif nom == "favoris":
        t.peindre(rect(7, 12, 10, 21) | rect(29, 12, 32, 21), "cheveux", "sphere", 1)
    elif nom == "pleine":
        z = poly([(7, 14), (9, 21), (13, 26), (17, 28), (23, 28), (27, 26), (31, 21), (33, 14), (30, 19), (25, 21), (15, 21), (10, 19)])
        t.peindre(z, "cheveux", "sphere", 1)
        t.poser({(18, 22), (19, 22), (20, 22), (21, 22)}, "1")
    elif nom == "longue":
        z = poly([(7, 14), (9, 22), (13, 30), (20, 36), (27, 30), (31, 22), (33, 14), (30, 19), (25, 21), (15, 21), (10, 19)])
        t.peindre(z, "cheveux", "sphere", 1)
        t.poser({(18, 22), (19, 22), (20, 22), (21, 22)}, "1")
        t.poser(courbe([(17, 26), (18, 32)]) | courbe([(23, 26), (22, 32)]), "8")
    elif nom == "guidon":
        z = poly([(13, 18), (17, 17), (20, 18), (23, 17), (27, 18), (29, 15), (30, 17), (27, 20), (20, 19.5), (13, 20), (10, 17), (11, 15)])
        t.peindre(z, "cheveux", "sphere", 1)
    t.contour()
    return t


BARBES = [
    ("aucune", "Aucune", "Rasé de près. Lisse, comme ta courbe de progression."),
    ("bouc", "Bouc", "Un bouc. Le style « je réfléchis » sans avoir à réfléchir."),
    ("favoris", "Favoris", "Des favoris, très XIXe siècle. Tes connaissances aussi, d'ailleurs."),
    ("guidon", "Moustache en guidon", "Une moustache en guidon de vélo. Tu vas pédaler, crois-moi."),
    ("pleine", "Pleine", "Une barbe pleine. Elle cache le menton, pas les erreurs."),
    ("longue", "Longue de sage", "La barbe du vieux sage. La sagesse est vendue à part."),
]

# --- Tenues (sur la silhouette du premier rang) ----------------------------------------------

T0 = TENUE0.px
HAUT = {p for p, c in T0.items() if c != "k" and p[1] <= 38}
BAS = {p for p, c in T0.items() if c != "k" and 39 <= p[1] <= 43}
PIEDS = {p for p, c in T0.items() if c != "k" and p[1] >= 44}
TRAITS = {p for p, c in T0.items() if c == "k"}


def base_tenue(t, haut=True, bas=True):
    for p in HAUT:
        t.px[p] = {"Q": "X", "+": "X"}.get(T0[p], T0[p])
    for p in BAS | PIEDS:
        t.px[p] = T0[p]
    for p in TRAITS:
        t.px[p] = "k"


def tenue(nom):
    t = toile()
    base_tenue(t)
    if nom == "blazer":
        for p in HAUT:
            if T0[p] in "Q+":
                t.px[p] = T0[p]
    elif nom == "costume":
        t.poser(poly([(16.5, 22), (23.5, 22), (20.5, 31), (19.5, 31)]) & HAUT, "w")
        t.poser(trait(16, 22, 19, 31) | trait(24, 22, 21, 31), "!")
        t.poser({(19, 23), (20, 23)} | rect(19, 24, 20, 29) | {(20, 30)}, "+")
        t.poser({(20, 33), (20, 36)}, "+")
    elif nom == "pyjama":
        for (x, y) in HAUT | BAS:
            if x % 3 == 0:
                t.px[(x, y)] = "Q"
        t.poser({(20, 25), (20, 29), (20, 33)}, "+")
        t.poser(trait(20, 22, 20, 38) & HAUT - {(20, 25), (20, 29), (20, 33)}, "!")
    elif nom == "mariniere":
        for (x, y) in HAUT:
            if y % 2 == 0 and y > 23:
                t.px[(x, y)] = "Q"
    elif nom == "noel":
        for (x, y) in HAUT:
            if y in (27, 31):
                t.px[(x, y)] = "Q"
            elif 28 <= y <= 30:
                k = (x + (y - 28)) % 4
                if (y == 29 and x % 4 == 0) or (y != 29 and x % 4 == 2):
                    t.px[(x, y)] = "+"
            elif y in (24, 35) and x % 3 == 0:
                t.px[(x, y)] = "Q"
        t.poser({(20, 33), (19, 34), (20, 34), (21, 34), (20, 35)} & HAUT, "+")
        t.poser({(20, 32)} & HAUT, "Q")
    elif nom == "salopette":
        for p in HAUT:
            t.px[p] = "Q" if T0[p] not in "!" else "+"
        bib = rect(14, 28, 25, 38) | rect(14, 22, 15, 28) | rect(24, 22, 25, 28)
        t.peindre(bib & HAUT, "tenue", "biseau", 1)
        t.poser({(15, 28), (24, 28)}, "Q")
        t.poser(rect(17, 31, 22, 34) & HAUT, "!")
        for p in BAS:
            t.px[p] = "X" if T0[p] == "Z" else "!"
    elif nom == "survet":
        for (x, y) in HAUT:
            if x in (8, 31) and y >= 25:
                t.px[(x, y)] = "Q"
        t.poser({p for p in HAUT if p[0] in (19, 20)}, "+")
        t.poser({p for p in HAUT if p[1] <= 23}, "Q")
        for p in BAS:
            t.px[p] = "X" if T0[p] == "Z" else "!"
        t.poser({p for p in BAS if p[0] in (12, 28)}, "Q")
    elif nom == "hawai":
        for (x, y) in HAUT:
            if (x * 7 + y * 11) % 13 == 0 and y > 23:
                for q in ((x, y), (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if q in HAUT:
                        t.px[q] = "Q"
                t.px[(x, y)] = "+"
        t.poser(poly([(17, 22), (23, 22), (20, 27)]) & HAUT, "Q")
    elif nom == "blouse":
        long = rect(11, 39, 28, 42)
        t.peindre(long, "tenue", "biseau", 2)
        t.poser(rect(10, 39, 10, 42) | rect(29, 39, 29, 42) | rect(11, 43, 28, 43), "k")
        t.poser(trait(20, 23, 20, 42), "!")
        t.poser(trait(17, 22, 19, 27) | trait(23, 22, 21, 27), "!")
        t.poser(poly([(17, 22), (23, 22), (20, 26)]) & HAUT, "Q")
        t.poser(rect(13, 33, 16, 35) | rect(24, 33, 27, 35), "!")
        t.poser(rect(24, 27, 26, 27), "+")
    elif nom == "ecolier":
        long = rect(11, 39, 28, 41)
        t.peindre(long, "tenue", "biseau", 1)
        t.poser(rect(10, 39, 10, 41) | rect(29, 39, 29, 41) | rect(11, 42, 28, 42), "k")
        t.poser(ellipse(17.5, 23, 2.6, 1.8) | ellipse(22.5, 23, 2.6, 1.8), "Q")
        t.poser({(20, 22), (20, 23)}, "!")
        t.poser({(20, 27), (20, 31), (20, 35), (20, 39)}, "+")
        t.poser(rect(13, 32, 16, 34) | rect(24, 32, 27, 34), "!")
        t.poser({(14, 31), (15, 31), (25, 31), (26, 31)}, "Q")
    elif nom == "toge":
        zone = HAUT | BAS
        for p in zone:
            t.px[p] = "X"
        t.peindre(zone, "tenue", "biseau", 1)
        t.poser({p for p in BAS if T0[p] == "k"}, "X")
        for (x, y) in list(zone):
            if (x + y) % 7 == 0 and y > 25:
                t.px[(x, y)] = "!"
        t.poser(trait(12, 23, 27, 36, 2) & zone, "Q")
        t.poser({(20, 39), (20, 40), (20, 41), (20, 42), (20, 43)}, "X")
    elif nom == "robe":
        jupe = poly([(9, 35), (31, 35), (34, 44), (6, 44)])
        t.peindre(jupe, "tenue", "biseau", 1)
        for p in BAS - jupe:
            t.px.pop(p, None)
        t.poser(rect(10, 34, 29, 35), "Q")
        t.poser(courbe([(12, 37), (9, 43)]) | courbe([(28, 37), (31, 43)]) | courbe([(20, 37), (20, 43)]), "!")
        t.poser({(x, 45) for x in range(6, 35)} - set(), "k")
        for p in PIEDS:
            t.px.pop(p, None)
        t.poser(rect(12, 46, 18, 47) | rect(22, 46, 28, 47), "n")
    elif nom == "spatiale":
        for p in BAS:
            t.px[p] = "X" if T0[p] == "Z" else "!"
        t.poser({p for p in HAUT if p[1] <= 23} | rect(16, 21, 23, 22), "g")
        t.poser(rect(24, 26, 27, 28), "Q")
        t.poser({(25, 27)}, "+")
        t.poser({p for p in HAUT if p[1] in (36, 37)}, "+")
        for p in PIEDS:
            t.px[p] = {"g": "l", "G": "z", "n": "g"}.get(T0[p], T0[p])
    elif nom == "peignoir":
        long = rect(11, 39, 28, 43)
        t.peindre(long, "tenue", "biseau", 2)
        t.poser(rect(10, 39, 10, 43) | rect(29, 39, 29, 43), "k")
        for (x, y) in HAUT | long:
            if (x + 2 * y) % 5 == 0:
                t.px[(x, y)] = "*"
        t.poser(trait(16, 22, 21, 33) | trait(24, 22, 19, 33), "Q")
        t.poser({p for p in HAUT if p[1] == 33}, "+")
        t.poser({(13, 34), (12, 35), (27, 34), (28, 35)}, "+")
        t.poser(trait(20, 34, 20, 43), "!")
        for p in PIEDS:
            t.px[p] = {"g": "I", "G": "F", "n": "F"}.get(T0[p], T0[p])
    elif nom == "smoking":
        t.poser(poly([(16.5, 22), (23.5, 22), (21, 32), (19, 32)]) & HAUT, "w")
        t.poser({(18, 23), (19, 24), (20, 24), (21, 24), (22, 23), (18, 24), (22, 24), (18, 25), (22, 25)}, "+")
        t.poser(trait(16, 22, 19, 32) | trait(24, 22, 21, 32), "Q")
        t.poser({(20, 27), (20, 30)}, "n")
    t.contour()
    return t


# Couleur principale par défaut, bas et détail (« = » : la couleur principale, plus sombre).
TENUES = [
    ("ecolier", "Blouse d'écolier", "La blouse grise d'écolier. Tout le monde commence au premier rang. Toi, tu y resteras peut-être.", "#7C8796", "#2F3B59", "#F4F1EA"),
    ("blazer", "Blazer d'étudiant", "Le blazer d'étudiant. Il fait sérieux. C'est un début.", "#3D63D9", "#2F3B59", "#F2C14E"),
    ("costume", "Costume cravate", "Costume et cravate. Pour un entretien d'embauche avec moi ? Tu n'es pas pris.", "#3A3F4A", "#2B2E36", "#D94141"),
    ("smoking", "Smoking", "Un smoking. Tu viens recevoir un prix ? Il n'y en a pas. Pas encore.", "#22242C", "#1A1C22", "#D94141"),
    ("pyjama", "Pyjama rayé", "Un pyjama. Au moins, tu es honnête sur l'heure à laquelle tu révises.", "#7B94E5", "#7B94E5", "#F4F1EA"),
    ("mariniere", "Marinière", "Une marinière. Tu vas mener ta barque. Dans le brouillard.", "#24408F", "#2F3B59", "#F4F1EA"),
    ("noel", "Pull de Noël moche", "Un pull de Noël. Quel que soit le mois, c'est un choix. Un mauvais, mais un choix.", "#C0392B", "#2F3B59", "#F4F1EA"),
    ("salopette", "Salopette", "Une salopette, pour mettre les mains dans le cambouis du savoir. Ou dans la peinture.", "#3D63D9", "#3D63D9", "#F2C14E"),
    ("survet", "Survêtement", "Le survêtement. Tu fais du sport ? Non. Tu es juste à l'aise. Je respecte.", "#2E9E5B", "#2E9E5B", "#F4F1EA"),
    ("hawai", "Chemise hawaïenne", "La chemise à fleurs. Tu es en vacances ? Le cerveau, oui, visiblement.", "#E8873A", "#2F3B59", "#F2C14E"),
    ("blouse", "Blouse de labo", "La blouse blanche. Tu n'as rien découvert, mais tu as le costume.", "#F4F1EA", "#2F3B59", "#9AA0A8"),
    ("toge", "Toge", "Une toge, comme Cicéron. Lui plaidait. Toi, tu improvises.", "#F4F1EA", "#F4F1EA", "#B8862B"),
    ("robe", "Robe", "Une robe élégante. Pour aller où ? Au mur de la honte ? Il sera ravi.", "#24408F", "#2F3B59", "#F4F1EA"),
    ("spatiale", "Combinaison spatiale", "La combinaison d'astronaute. Tu as la tête dans les étoiles, au moins c'est assorti.", "#E8E8EE", "#E8E8EE", "#E8873A"),
    ("peignoir", "Peignoir et chaussons", "Peignoir et chaussons. Le télétravail du savoir. J'adore. Je juge, mais j'adore.", "#F28FB0", "#F28FB0", "#FFFFFF"),
]

# Victor (2026-11-03) : au départ, toge ou blouse d'écolier ; les autres tenues se gagnent avec des succès.
TENUES_DEPART = ["ecolier", "toge"]
TENUES_SUCCES = {
    "blouse": "premier-pas", "salopette": "eureka", "blazer": "dix-competences", "costume": "encyclopediste",
    "smoking": "deux-nobel", "pyjama": "insomniaque", "peignoir": "procrastination", "mariniere": "tour-complet",
    "noel": "huit-verres", "survet": "serie-rappels", "hawai": "pomme", "robe": "petit-gauss", "spatiale": "epoque-xxe",
}

# Ce qu'Alyca fait de ta garde-robe selon son humeur (Victor, 2026-11-03). {objet} : la tenue ou l'accessoire.
HUMEURS_PERSO = {
    "confisque_tenue": [
        "Je te confisque {objet}. Tu ne la mérites pas aujourd'hui. Retour à la blouse grise.",
        "{objet} ? Saisie. Tu la récupéreras quand tu m'auras fait sourire.",
        "J'ai mis {objet} au placard. La clé, c'est moi. Et je boude.",
    ],
    "confisque_accessoire": [
        "Je garde {objet} pour aujourd'hui. Il me va mieux, de toute façon.",
        "{objet}, confisqué. Considère ça comme une amende pour excès d'erreurs.",
        "Tu n'auras pas {objet} aujourd'hui. Pas de raison. Enfin si : mon humeur.",
    ],
    "retouche": [
        "Je suis de bonne humeur : j'ai cousu des galons dorés sur ta tenue. Ne t'y habitue pas.",
        "Regarde-toi, avec des boutons en or. C'est moi qui régale, pour aujourd'hui.",
        "Un peu de dorure sur {objet}. Tu brilles presque autant que moi. Presque.",
    ],
}

COULEURS_TENUE = [
    ("bleu", "Bleu roi", "#3D63D9"), ("marine", "Marine", "#24408F"), ("rouge", "Rouge", "#C0392B"), ("vert", "Vert sapin", "#2E7D32"),
    ("jaune", "Moutarde", "#D4A017"), ("orange", "Orange", "#E8873A"), ("violet", "Violet", "#7E3FB0"), ("rose", "Rose bonbon", "#F06AAE"),
    ("turquoise", "Turquoise", "#1FA5A5"), ("fluo", "Vert fluo", "#9BE22B"), ("noir", "Noir", "#2A2A33"), ("gris", "Gris", "#8A9099"),
    ("blanc", "Blanc", "#F4F1EA"), ("marron", "Marron", "#7A4A28"),
]


# --- Pouvoirs (Victor, 2026-11-03) : débloqués par un succès et un niveau, rechargés chaque jour ou chaque semaine --------

POUVOIRS = [
    {"id": "rasoir", "nom": fr("Le rasoir d'Ockham"), "icone": "✂",
     "effet": fr("Pendant un quiz, supprime deux mauvaises réponses d'une question à choix."),
     "notice": fr("Guillaume d'Ockham, logicien anglais du XIVe siècle, prônait la simplicité : ne rien supposer de plus que "
                  "nécessaire. La formule célèbre n'est pas de lui, et le mot « rasoir » n'apparaît qu'en 1852."),
     "source": "New World Encyclopedia, « Ockham's razor »",
     "pique": fr("Je te prête un rasoir. Pour couper les mauvaises réponses, pas ta moustache."),
     "condition": {"succes": "eureka", "niveau_global": 3},
     "charges": {"periode": "jour", "n": 1, "palier": {"niveau_global": 20, "n": 2}}},
    {"id": "pascaline", "nom": fr("La Pascaline"), "icone": "🧮",
     "effet": fr("Une calculatrice pour les questions où l'on répond par un nombre (sauf les dates)."),
     "notice": fr("En 1642, Blaise Pascal n'a pas vingt ans quand il commence une machine à calculer pour aider son père, "
                  "chargé de collecter les impôts à Rouen. En 1652, une cinquantaine de prototypes existent, mais très peu se vendent."),
     "source": "MacTutor History of Mathematics (université de St Andrews), « Blaise Pascal »",
     "pique": fr("Pascal a inventé sa machine pour aider son père. Moi, je te la prête par pitié. Chacun ses raisons."),
     "condition": {"niveau_stat": {"stats": ["logique", "mecanique", "cp-calcul", "informatique"], "min": 3, "sinon_global": 6}},
     "charges": {"periode": "jour", "n": 3, "palier": {"niveau_stat": 8, "n": 6}}},
    {"id": "demon", "nom": fr("Le démon de Socrate"), "icone": "🗣",
     "effet": fr("Ouvre la masterclass de la compétence en plein quiz, pour relire la leçon avant de répondre."),
     "notice": fr("Dans l'Apologie de Platon, Socrate raconte qu'une voix divine l'accompagne depuis l'enfance : elle le détourne "
                  "de ce qu'il s'apprêtait à faire, mais ne lui recommande jamais rien. Le tien est plus bavard."),
     "source": "Platon, Apologie de Socrate, 31c-d (résumé de Wikipédia, « Daimonion (Socrates) »)",
     "pique": fr("Une petite voix va te souffler la leçon. Ne t'habitue pas : elle est syndiquée, une fois par semaine."),
     "condition": {"succes": "dix-competences", "niveau_global": 10},
     "charges": {"periode": "semaine", "n": 1, "palier": {"niveau_global": 40, "n": 2}}},
    {"id": "palais", "nom": fr("Le palais de mémoire"), "icone": "🏛",
     "effet": fr("Un rappel raté ne fait pas perdre la compétence : le rappel revient tout de suite, à retenter."),
     "notice": fr("Cicéron rapporte la légende de Simonide : sorti d'un banquet juste avant que le toit s'effondre, le poète "
                  "reconnut les convives, méconnaissables, en se rappelant la place de chacun à table. D'où la méthode des lieux."),
     "source": "Stanford Encyclopedia of Philosophy, « Mental Imagery », supplément « Ancient Imagery Mnemonics »",
     "pique": fr("Te voilà propriétaire d'un palais de mémoire. Vide, pour l'instant. Meuble-le."),
     "condition": {"succes": "cloche", "niveau_global": 6},
     "charges": {"periode": "semaine", "n": 1, "palier": {"niveau_global": 40, "n": 2}}},
]


def generer():
    especes = []
    for id_, cat, nom, f, yeux, coif, pique, teintes in ESPECES:
        especes.append({"id": id_, "categorie": cat, "nom": fr(nom), "pique": fr(pique), "yeux": yeux, "coiffure": coif,
                        "corps": f().lignes(), "teintes": teintes})
    return {
        "categories": CATEGORIES,
        "especes": especes,
        "regards": [{"id": i, "nom": fr(n), "pique": fr(p), "pixels": regard(i).lignes()} for i, n, p in REGARDS],
        "coiffures": [{"id": i, "nom": fr(n), "pique": fr(p), "pixels": coiffure(i).lignes()} for i, n, p in COIFFURES],
        "couleurs_cheveux": couleurs_cheveux(),
        "barbes": [{"id": i, "nom": fr(n), "pique": fr(p), "pixels": barbe(i).lignes()} for i, n, p in BARBES],
        "tenues": [dict({"id": i, "nom": fr(n), "pique": fr(p), "couleur": c, "bas": b, "detail": d, "pixels": tenue(i).lignes()},
                        **({"depart": True} if i in TENUES_DEPART else {"condition": {"type": "succes", "id": TENUES_SUCCES[i]}}))
                   for i, n, p, c, b, d in TENUES],
        "humeurs": {k: [fr(x) for x in v] for k, v in HUMEURS_PERSO.items()},
        "couleurs_tenue": [{"id": i, "nom": fr(n), "hexa": h} for i, n, h in COULEURS_TENUE],
    }


def couleurs_tenue(principal, bas, detail):
    return {"!": nuance(principal, 0.68), "X": principal, "*": nuance(principal, 1.32),
            "~": nuance(bas, 0.7), "Z": bas, "+": nuance(detail, 0.7), "Q": detail}


def planche(cr, chemin):
    from PIL import Image
    E = 4
    vides = ["." * L] * H

    def poser(im, calques, ox, oy):
        for lignes, cs in calques:
            pal = dict(PALETTE, **(cs or {}))
            for y, l in enumerate(lignes):
                for x, ch in enumerate(l):
                    if ch != ".":
                        im.paste(pal.get(ch, "#FF00FF"), (ox + x * E, oy + y * E, ox + (x + 1) * E, oy + (y + 1) * E))

    tn = {t["id"]: t for t in cr["tenues"]}
    co = {c["id"]: c for c in cr["coiffures"]}
    rg = {r["id"]: r for r in cr["regards"]}
    cc = {c["id"]: c for c in cr["couleurs_cheveux"]}
    lignes = []
    for e in cr["especes"]:
        row = []
        for i, te in enumerate(e["teintes"]):
            t = cr["tenues"][i % len(cr["tenues"])]
            row.append([(e["corps"], te["couleurs"]), (t["pixels"], couleurs_tenue(t["couleur"], t["bas"], t["detail"])),
                        (rg["normal"]["pixels"] if e["yeux"] else vides, None),
                        (co[e["coiffure"]]["pixels"], cc["chatain"]["couleurs"])])
        lignes.append(row)
    h0 = cr["especes"][0]
    for groupe in ("regards", "coiffures", "barbes", "tenues"):
        row = []
        for j, x in enumerate(cr[groupe]):
            cal = [(h0["corps"], None)]
            t = tn["blazer"] if groupe != "tenues" else x
            cal.append((t["pixels"], couleurs_tenue(t["couleur"], t["bas"], t["detail"])))
            cal.append((x["pixels"] if groupe == "regards" else rg["normal"]["pixels"], None))
            if groupe == "barbes":
                cal.append((x["pixels"], cc["roux"]["couleurs"]))
            cal.append((x["pixels"] if groupe == "coiffures" else co["court"]["pixels"], cr["couleurs_cheveux"][j % 11]["couleurs"]))
            row.append(cal)
        for k in range(0, len(row), 7):
            lignes.append(row[k:k + 7])
    cw, ch = L * E + 8, H * E + 8
    im = Image.new("RGB", (cw * 7, ch * len(lignes)), (243, 233, 210))
    for j, row in enumerate(lignes):
        for i, cal in enumerate(row):
            poser(im, cal, i * cw + 4, j * ch + 4)
    im.save(chemin)
    print("planche :", chemin)


def main(args):
    cr = generer()
    AV["creation"] = cr
    AV["pouvoirs"] = POUVOIRS
    SOURCE.write_text(json.dumps(AV, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"création : {len(cr['especes'])} espèces, {len(cr['regards'])} regards, {len(cr['coiffures'])} coiffures, "
          f"{len(cr['barbes'])} barbes, {len(cr['tenues'])} tenues")
    if args:
        planche(cr, args[0])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
