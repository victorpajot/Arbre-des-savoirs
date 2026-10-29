"""v4 : vingt savants jouables (40 × 48), débloqués par des succès liés à leur histoire.

Chaque savant reprend le corps de l'avatar (même visage, pour que lunettes et moustaches tombent juste),
avec sa peau, sa tenue, sa barbe et son objet fétiche (calque « base »), et sa coiffure (calque « cheveux »),
que remplace un accessoire de tête porté en déguisement.
Les caractères ! X * ~ Z + Q de la tenue prennent les couleurs propres au savant.
"""
import math

from avatar40 import L, couleurs_rang, corps, silhouette, toile, zone_cheveux
from dessin import anneau, bande, courbe, disque, ellipse, miroir, poly, rect, texte, trait

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


# --- Tenues ---------------------------------------------------------------------

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


# --- Coiffures (calque « cheveux ») ----------------------------------------------------

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


# --- Objets fétiches, tenus dans la main droite (vers x = 31, y = 37) ------------------------

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


# --- Les vingt -------------------------------------------------------------------------------

def c(principal, bas, detail):
    return couleurs_rang(principal, bas, detail)


def maitriser(comp):
    return {"type": "competence_maitrisee", "id": comp}


def apres(succes_id):
    return {"type": "succes", "id": succes_id}


# id, nom, années, peau, tenue, couleurs, coiffure (style, famille, teinte), barbe (style, famille, teinte), objet, condition, notice, source
SAVANTS = [
    ("aristote", "Aristote", "-384 / -322", "claire", "toge", c("#E8DDC0", "#A8905E", "#5E2F8A"), ("frises", "cheveux", 1), ("pleine", "cheveux", 1), "rouleau",
     apres("branche-sagesse"),
     "Précepteur d'Alexandre, il a écrit sur la logique, la physique, la biologie, la politique et la rhétorique. Il pensait que les femmes avaient moins de dents que les hommes. Bertrand Russell s'amusait qu'il n'ait jamais pensé à vérifier dans la bouche de ses deux épouses.",
     "Aristote, Histoire des animaux, II, 3"),
    ("archimede", "Archimède", "-287 / -212", "claire", "toge", c("#F2EAD8", "#A8905E", "#2E7D32"), ("couronne", "gris", 3), ("pleine", "gris", 4), "compas",
     apres("baignoire"),
     "Il calcule le volume de la sphère, approche π et donne son nom à une vis qui existait sans doute avant lui. Selon Plutarque, il est tué par un soldat romain parce qu'il refuse de le suivre avant d'avoir fini son problème. « Ne dérange pas mes cercles » n'apparaît dans aucun texte antique.",
     "Plutarque, Vie de Marcellus, 19"),
    ("hypatie", "Hypatie", "vers 370 / 415", "claire", "robe", c("#F2EAD8", "#D8C49A", "#3D63D9"), ("chignon", "cheveux", 0), None, "astrolabe",
     maitriser("astro.observer"),
     "Mathématicienne et astronome d'Alexandrie, elle enseigne la philosophie à des élèves venus de loin. Son élève Synésios lui doit l'art de construire un astrolabe, et lui écrit pour qu'elle lui fasse fabriquer un hydroscope. Elle est assassinée par une foule chrétienne en 415.",
     "Socrate le Scolastique, Histoire ecclésiastique, VII, 15"),
    ("ibn-al-haytham", "Ibn al-Haytham", "965 / 1040", "mate", "manteau", c("#2E7D32", "#3B3B3B", "#F2C14E"), ("turban", "gris", 4), ("pleine", "cheveux", 0), "lentille",
     maitriser("phys.ondes"),
     "Au Caire, il montre que la vision vient de la lumière qui entre dans l'œil, pas de rayons qui en sortent, et le prouve par l'expérience. Selon la légende, il aurait simulé la folie pour échapper à une mission impossible du calife.",
     "Ibn al-Haytham, Kitab al-Manazir (Traité d'optique), vers 1021"),
    ("galilee", "Galilée", "1564 / 1642", "claire", "manteau", c("#1E1E24", "#1E1E24", "#EEF0F4"), ("couronne", "cheveux", 2), ("pleine", "orange", 0), "lunette",
     apres("eppur-si-muove"),
     "Il pointe une lunette vers le ciel en 1609 et voit les lunes de Jupiter, les phases de Vénus et les montagnes de la Lune. Condamné en 1633, il finit ses jours assigné à résidence. Le « Eppur si muove » est sans doute une légende.",
     "Galilée, Sidereus Nuncius, 1610"),
    ("newton", "Isaac Newton", "1643 / 1727", "claire", "manteau", c("#7A5230", "#3B3B3B", "#E8DDC0"), ("perruque", "gris", 4), None, "pomme",
     apres("woolsthorpe"),
     "Gravitation, optique, calcul infinitésimal. Il a aussi dirigé la Monnaie royale, fait pendre des faussaires et perdu une fortune dans la bulle de la Compagnie des mers du Sud. Selon un témoin cité par Joseph Spence, il disait ne pas pouvoir « calculer la folie des gens ».",
     "Richard Westfall, Never at Rest, 1980"),
    ("du-chatelet", "Émilie du Châtelet", "1706 / 1749", "claire", "robe", c("#3D63D9", "#24408F", "#F2C14E"), ("perruque_courte", "gris", 4), None, "plume",
     maitriser("phys.energie"),
     "Elle traduit et commente les Principia de Newton, traduction qui reste la référence en français. Elle montre, avec les expériences de 's Gravesande, que l'énergie d'un corps dépend du carré de sa vitesse. Voltaire la disait « un grand homme qui n'avait de défaut que d'être femme ».",
     "Judith Zinsser, La Dame d'esprit, 2006"),
    ("lavoisier", "Antoine Lavoisier", "1743 / 1794", "claire", "manteau", c("#24408F", "#3B3B3B", "#EEF0F4"), ("perruque_courte", "gris", 4), None, "balance",
     apres("tete-lavoisier"),
     "Il nomme l'oxygène, prouve que l'eau est un composé et établit la conservation de la masse, avec l'aide de Marie-Anne Paulze, sa femme et collaboratrice. Fermier général, il est guillotiné en 1794. « La République n'a pas besoin de savants » est une phrase apocryphe.",
     "Jean-Pierre Poirier, Lavoisier, 1993"),
    ("faraday", "Michael Faraday", "1791 / 1867", "claire", "manteau", c("#3B3B3B", "#2F3B59", "#EEF0F4"), ("court", "cheveux", 2), ("favoris", "cheveux", 2), "bobine",
     maitriser("elec.magnetisme"),
     "Fils de forgeron, apprenti relieur, il apprend la science en lisant les livres qu'il relie. Il découvre l'induction électromagnétique en 1831. À un ministre qui demandait à quoi servait l'électricité : « Un jour, vous pourrez la taxer. » La réplique est sans doute inventée.",
     "Frank James, Michael Faraday : A Very Short Introduction, 2010"),
    ("ada-lovelace", "Ada Lovelace", "1815 / 1852", "claire", "robe", c("#5E2F8A", "#3B1A5C", "#EEF0F4"), ("boucles", "cheveux", 0), None, "carte",
     maitriser("elec.numerique"),
     "Fille de Byron, elle écrit en 1843 le premier programme publié, pour la machine analytique de Babbage, et entrevoit qu'une machine pourrait composer de la musique. Sa mère l'avait nourrie de mathématiques pour la protéger de la « folie » qu'elle prêtait à son père.",
     "Ada Lovelace, notes sur l'article de Menabrea, 1843"),
    ("darwin", "Charles Darwin", "1809 / 1882", "claire", "manteau", c("#3B3B3B", "#3B3B3B", "#E8DDC0"), ("couronne", "gris", 4), ("fleuve", "gris", 4), "carnet",
     apres("plus-apte"),
     "Cinq ans autour du monde sur le Beagle, vingt ans de réflexion avant de publier L'Origine des espèces en 1859. Il a dressé une liste des pour et des contre du mariage. Conclusion : « Marry, marry, marry. »",
     "Charles Darwin, notes sur le mariage, 1838"),
    ("nightingale", "Florence Nightingale", "1820 / 1910", "claire", "robe", c("#2F3B59", "#1E1E24", "#EEF0F4"), ("coiffe", "cheveux", 1), None, "lampe",
     maitriser("math.statistiques"),
     "La « dame à la lampe » de la guerre de Crimée était d'abord une statisticienne. Ses diagrammes montrent que les soldats meurent plus de maladies que de blessures, et font réformer les hôpitaux militaires.",
     "Florence Nightingale, Notes on Matters Affecting the Health… of the British Army, 1858"),
    ("pasteur", "Louis Pasteur", "1822 / 1895", "claire", "manteau", c("#1E1E24", "#1E1E24", "#EEF0F4"), ("court", "cheveux", 1), ("pleine", "cheveux", 1), "col_cygne",
     maitriser("sci.immunite"),
     "Avec ses flacons à col de cygne, il montre que les microbes ne naissent pas spontanément. En 1885, il vaccine contre la rage le petit Joseph Meister. Ses carnets, accessibles aux chercheurs après 1971, montrent qu'il arrangeait parfois ses résultats.",
     "Gerald Geison, The Private Science of Louis Pasteur, 1995"),
    ("mendeleiev", "Dmitri Mendeleïev", "1834 / 1907", "claire", "manteau", c("#5E3B1C", "#3B3B3B", "#E8DDC0"), ("longs", "gris", 3), ("fleuve", "gris", 3), "tableau",
     apres("reve-mendeleiev"),
     "En 1869, il range les éléments dans un tableau et y laisse des cases vides pour des éléments encore inconnus, dont il prédit les propriétés. Le gallium et le germanium arrivent quelques années plus tard. Il ne se coupait les cheveux qu'une fois par an.",
     "Michael Gordin, A Well-Ordered Thing, 2004"),
    ("marie-curie", "Marie Curie", "1867 / 1934", "claire", "robe", c("#1E1E24", "#1E1E24", "#5D6470"), ("chignon", "gris", 2), None, "fiole",
     apres("deux-nobel"),
     "Seule personne à avoir reçu deux prix Nobel dans deux sciences différentes, physique en 1903 et chimie en 1911. Ses carnets sont encore radioactifs : la Bibliothèque nationale ne les communique que sous un protocole très strict.",
     "Bibliothèque nationale de France, fonds Pierre et Marie Curie"),
    ("einstein", "Albert Einstein", "1879 / 1955", "claire", "pull", c("#9AA0A8", "#3B3B3B", "#EEF0F4"), ("ebouriffe", "gris", 4), None, "craie",
     maitriser("phys.relativite"),
     "En 1905, employé à l'Office des brevets de Berne, il publie quatre articles qui changent la physique. Il ne portait pas de chaussettes ; à un voisin, il expliquait avoir atteint l'âge où, si on lui dit d'en mettre, il n'est pas obligé.",
     "Walter Isaacson, Einstein, 2007 ; Peter Pesic, Physics in Perspective, 2025"),
    ("ramanujan", "Srinivasa Ramanujan", "1887 / 1920", "foncee", "manteau", c("#EEF0F4", "#2F3B59", "#9C5E3E"), ("raie", "cheveux", 0), None, "ardoise",
     maitriser("math.infini"),
     "Autodidacte de Madras, il écrit en 1913 à Hardy, à Cambridge, une lettre pleine de formules étonnantes. Hardy lui rend visite à l'hôpital en taxi numéro 1729, « un nombre sans intérêt ». « Au contraire, c'est le plus petit nombre somme de deux cubes de deux façons. »",
     "G. H. Hardy, Ramanujan, 1940"),
    ("turing", "Alan Turing", "1912 / 1954", "claire", "manteau", c("#7A5230", "#5D6470", "#D94141"), ("raie", "cheveux", 1), None, "ruban",
     maitriser("math.logique"),
     "Il invente la machine qui porte son nom en 1936, casse Enigma pendant la guerre et pose la question des machines pensantes en 1950. Coureur de fond, il manque de peu la sélection olympique pour le marathon de 1948.",
     "Andrew Hodges, Alan Turing : The Enigma, 1983"),
    ("katherine-johnson", "Katherine Johnson", "1918 / 2020", "foncee", "cardigan", c("#F28FB0", "#2F3B59", "#EEF0F4"), ("frises", "cheveux", 0), None, "trajectoire",
     maitriser("astro.espace"),
     "Calculatrice à la NASA, elle vérifie à la main les trajectoires de la mission de John Glenn en 1962. Glenn avait demandé : « Faites vérifier les chiffres par la fille. Si elle dit qu'ils sont bons, je suis prêt. »",
     "Margot Lee Shetterly, Hidden Figures, 2016"),
    ("rosalind-franklin", "Rosalind Franklin", "1920 / 1958", "claire", "blouse", c("#EEF0F4", "#2F3B59", "#3D63D9"), ("court", "cheveux", 0), None, "photo51",
     maitriser("sci.genetique"),
     "Sa « photo 51 », une image de diffraction de l'ADN, est montrée à Watson sans qu'elle le sache, et l'aide à trouver la double hélice. Elle meurt à 37 ans, quatre ans avant le Nobel attribué à Watson, Crick et Wilkins.",
     "Brenda Maddox, Rosalind Franklin : The Dark Lady of DNA, 2002"),
]

# v7 : vingt de plus, pour quarante en tout, avec davantage de savantes et de savants hors d'Europe.
SAVANTS += [
    ("imhotep", "Imhotep", "vers -2650", "mate", "toge", c("#F2EAD8", "#D8C49A", "#C99A1E"), ("court", "cheveux", 0), None, "rouleau",
     maitriser("phys.unites"),
     "Vers 2650 avant notre ère, il conçoit pour le pharaon Djéser la pyramide à degrés de Saqqarah, la première grande construction en pierre taillée. Plus tard, les Égyptiens en font un dieu de la médecine, et les Grecs l'identifient à Asclépios. De l'homme réel, on ne sait presque rien.",
     "Dietrich Wildung, Imhotep und Amenhotep, 1977"),
    ("confucius", "Confucius", "-551 / -479", "mate", "robe", c("#8E2424", "#3B3B3B", "#F2C14E"), ("chignon", "gris", 3), ("longue", "gris", 3), "rouleau",
     maitriser("philo.ethique"),
     "Il enseigne la morale, les rites et l'art de gouverner par l'exemple. Ses disciples recueillent ses paroles dans les Entretiens. « Ce que tu ne voudrais pas qu'on te fasse, ne le fais pas aux autres » y figure, cinq siècles avant les Évangiles.",
     "Confucius, Entretiens, XV, 24"),
    ("zhang-heng", "Zhang Heng", "78 / 139", "mate", "manteau", c("#2E7D32", "#3B3B3B", "#F2C14E"), ("chignon", "cheveux", 0), ("longue", "cheveux", 0), "astrolabe",
     maitriser("astro.systeme"),
     "Astronome de la cour des Han, il construit en 132 un sismoscope de bronze : huit dragons tiennent chacun une bille, qui tombe dans la gueule d'un crapaud du côté du séisme. En 138, une bille tombe sans que personne ne sente rien à la capitale. Un messager confirme le séisme quelques jours plus tard.",
     "Fan Ye, Livre des Han postérieurs, biographie de Zhang Heng"),
    ("aryabhata", "Aryabhata", "476 / 550", "mate", "toge", c("#F7B77A", "#A95A1F", "#8E2424"), ("court", "cheveux", 0), ("pleine", "cheveux", 0), "carnet",
     maitriser("astro.orbites"),
     "À 23 ans, il écrit un traité en vers où il affirme que la Terre tourne sur elle-même, ce qui explique le mouvement apparent des étoiles. Il donne π à 3,1416 et explique les éclipses par les ombres de la Terre et de la Lune, pas par un démon qui avale le Soleil.",
     "Aryabhata, Aryabhatiya, 499, trad. Walter Eugene Clark, 1930"),
    ("brahmagupta", "Brahmagupta", "598 / 668", "mate", "toge", c("#F2EAD8", "#D8C49A", "#E8873A"), ("turban", "orange", 1), ("pleine", "cheveux", 0), "rouleau",
     maitriser("math.arithmetique"),
     "En 628, il écrit les premières règles de calcul avec zéro comme un nombre à part entière : un nombre moins lui-même donne zéro, et le produit de deux dettes est une fortune. Il ne se trompe que sur un point : pour lui, zéro divisé par zéro vaut zéro.",
     "Brahmagupta, Brahmasphutasiddhanta, 628 ; Kim Plofker, Mathematics in India, 2009"),
    ("al-khwarizmi", "Al-Khwarizmi", "vers 780 / vers 850", "mate", "manteau", c("#24408F", "#3B3B3B", "#F2C14E"), ("turban", "gris", 4), ("pleine", "cheveux", 0), "carnet",
     maitriser("math.algebre"),
     "À la Maison de la sagesse de Bagdad, il écrit vers 820 un traité pour résoudre les équations par al-jabr, « remettre en place ». Le mot a donné « algèbre », et son nom latinisé, Algoritmi, « algorithme ». Il résout tout en phrases et en figures, sans un seul symbole.",
     "Roshdi Rashed, Al-Khwarizmi : le commencement de l'algèbre, 2007"),
    ("ibn-sina", "Ibn Sina (Avicenne)", "980 / 1037", "mate", "manteau", c("#5E2F8A", "#3B3B3B", "#F2C14E"), ("turban", "gris", 4), ("pleine", "cheveux", 0), "fiole",
     maitriser("sci.corps"),
     "Médecin du prince samanide à 17 ans, il écrit le Canon de la médecine, enseigné en Europe jusqu'au XVIIe siècle. Il y demande de tester un remède sur des cas simples et de répéter l'essai. Il raconte avoir lu quarante fois la Métaphysique d'Aristote sans la comprendre, jusqu'à ce qu'un petit commentaire d'al-Farabi l'éclaire.",
     "William Gohlman, The Life of Ibn Sina, 1974"),
    ("shen-kuo", "Shen Kuo", "1031 / 1095", "mate", "manteau", c("#1E1E24", "#3B3B3B", "#D94141"), ("chignon", "cheveux", 0), ("longue", "gris", 3), "lentille",
     maitriser("elec.circuits"),
     "Haut fonctionnaire de la dynastie Song, il note en 1088 qu'une aiguille aimantée ne pointe pas exactement vers le nord : c'est la première description connue de la déclinaison magnétique. Il décrit aussi l'imprimerie à caractères mobiles de Bi Sheng et la formation des fossiles.",
     "Shen Kuo, Essais au fil du pinceau dans le Jardin des rêves, 1088 ; Joseph Needham, Science and Civilisation in China"),
    ("averroes", "Ibn Rushd (Averroès)", "1126 / 1198", "mate", "manteau", c("#3E6B48", "#3B3B3B", "#E8DDC0"), ("turban", "gris", 4), ("pleine", "cheveux", 1), "rouleau",
     maitriser("philo.medievale"),
     "Juge et médecin à Cordoue, il commente Aristote si complètement que les Latins l'appellent simplement « le Commentateur ». Pour lui, la philosophie et la religion, bien interprétées, ne peuvent pas se contredire. Exilé et ses livres brûlés, il est réhabilité peu avant sa mort.",
     "Dominique Urvoy, Averroès : les ambitions d'un intellectuel musulman, 1998"),
    ("ibn-khaldun", "Ibn Khaldun", "1332 / 1406", "mate", "manteau", c("#7A5230", "#3B3B3B", "#E8DDC0"), ("turban", "gris", 4), ("pleine", "gris", 2), "carnet",
     maitriser("philo.politique"),
     "Diplomate, juge et historien né à Tunis, il écrit en 1377 la Muqaddima, une introduction à l'histoire. Il y cherche les lois de l'essor et du déclin des dynasties : la solidarité d'un groupe le porte au pouvoir, puis le luxe l'use en trois ou quatre générations.",
     "Ibn Khaldun, Le Livre des exemples, trad. Abdesselam Cheddadi, Pléiade, 2002"),
    ("merian", "Maria Sibylla Merian", "1647 / 1717", "claire", "robe", c("#2E7D32", "#1B4D20", "#F2C14E"), ("chignon", "cheveux", 1), None, "plume",
     maitriser("sci.ecologie"),
     "Peintre et naturaliste, elle élève des chenilles et dessine chaque étape de leur métamorphose avec la plante qui les nourrit. À 52 ans, elle part au Suriname avec sa fille. Sa planche d'une mygale dévorant un oiseau passe pour une invention. Les naturalistes lui donnent raison au XIXe siècle.",
     "Maria Sibylla Merian, Metamorphosis insectorum Surinamensium, 1705"),
    ("mary-anning", "Mary Anning", "1799 / 1847", "claire", "robe", c("#7A5230", "#3E2614", "#E8DDC0"), ("coiffe", "cheveux", 1), None, "carnet",
     maitriser("sci.evolution"),
     "Fille d'un menuisier de Lyme Regis, elle fouille les falaises après les tempêtes. Elle trouve le premier squelette complet de plésiosaure et des ichtyosaures qui prouvent que des espèces ont disparu. Femme et pauvre, elle n'est pas admise à la Geological Society, et d'autres publient ses trouvailles.",
     "Shelley Emling, The Fossil Hunter, 2009"),
    ("carver", "George Washington Carver", "vers 1864 / 1943", "foncee", "manteau", c("#5D6470", "#3B3B3B", "#EEF0F4"), ("court", "gris", 2), None, "fiole",
     maitriser("chim.organique"),
     "Né esclave dans le Missouri, il devient botaniste et chimiste à l'institut Tuskegee. Il apprend aux fermiers à alterner le coton, qui épuise la terre, avec l'arachide, qui l'enrichit en azote, et cherche des centaines d'usages à ces plantes. Contrairement à la légende, il n'a pas inventé le beurre de cacahuète.",
     "Linda McMurry, George Washington Carver, Scientist and Symbol, 1981"),
    ("leavitt", "Henrietta Leavitt", "1868 / 1921", "claire", "robe", c("#3B3B3B", "#1E1E24", "#EEF0F4"), ("chignon", "cheveux", 1), None, "carte",
     maitriser("astro.galaxies"),
     "« Calculatrice » à l'observatoire de Harvard, payée 30 cents de l'heure, elle étudie des milliers d'étoiles variables sur des plaques photographiques. En 1912, elle découvre que les céphéides les plus brillantes clignotent plus lentement. C'est l'étalon qui permettra à Hubble de mesurer la distance d'Andromède.",
     "Henrietta Leavitt et Edward Pickering, Harvard College Observatory Circular 173, 1912"),
    ("raman", "C. V. Raman", "1888 / 1970", "foncee", "manteau", c("#3B3B3B", "#2F3B59", "#EEF0F4"), ("turban", "gris", 4), None, "lentille",
     maitriser("elec.em"),
     "En 1921, sur le bateau du retour, il se demande pourquoi la mer est bleue. À Calcutta, il découvre qu'une petite partie de la lumière diffusée par les molécules change de couleur : l'effet Raman. Prix Nobel 1930, il avait réservé son voyage à Stockholm des mois avant l'annonce.",
     "G. Venkataraman, Journey into Light : Life and Science of C. V. Raman, 1988"),
    ("meitner", "Lise Meitner", "1878 / 1968", "claire", "blouse", c("#EEF0F4", "#3B3B3B", "#5E2F8A"), ("chignon", "gris", 2), None, "fiole",
     maitriser("chim.noyau"),
     "Physicienne autrichienne, elle fuit l'Allemagne nazie en 1938. Quelques mois plus tard, avec son neveu Otto Frisch, elle explique les résultats de son ancien collègue Otto Hahn : le noyau d'uranium s'est cassé en deux, c'est la fission. Le Nobel va à Hahn seul. L'élément 109 porte son nom.",
     "Ruth Lewin Sime, Lise Meitner : A Life in Physics, 1996"),
    ("noether", "Emmy Noether", "1882 / 1935", "claire", "robe", c("#2F3B59", "#1E1E24", "#93AAF2"), ("court", "cheveux", 1), None, "craie",
     maitriser("phys.forces"),
     "En 1918, elle démontre que chaque symétrie de la nature correspond à une grandeur conservée : l'invariance dans le temps donne la conservation de l'énergie. Interdite d'enseigner en son nom parce que femme, elle donne d'abord ses cours de Göttingen sous le nom de Hilbert. Einstein la tenait pour un génie.",
     "Albert Einstein, lettre au New York Times, mai 1935"),
    ("chien-shiung-wu", "Chien-Shiung Wu", "1912 / 1997", "mate", "robe", c("#3D63D9", "#24408F", "#F2C14E"), ("court", "cheveux", 0), None, "fiole",
     maitriser("phys.quantique"),
     "En 1956, les théoriciens Lee et Yang se demandent si la nature distingue la gauche de la droite. Chien-Shiung Wu monte l'expérience avec du cobalt 60 refroidi près du zéro absolu : les électrons partent de préférence d'un côté. La symétrie du miroir est violée. Lee et Yang ont le Nobel l'année suivante, pas elle.",
     "Wu et al., Physical Review, 1957"),
    ("mamie-clark", "Mamie Phipps Clark", "1917 / 1983", "foncee", "cardigan", c("#8E2424", "#2F3B59", "#EEF0F4"), ("frises", "cheveux", 0), None, "carnet",
     maitriser("psy.developpement"),
     "Avec son mari Kenneth, elle présente à des enfants noirs deux poupées identiques, l'une blanche, l'autre noire, et leur demande laquelle est gentille, laquelle est jolie. La plupart choisissent la blanche. Ces travaux sont cités en 1954 par la Cour suprême dans l'arrêt qui met fin à la ségrégation scolaire.",
     "Brown v. Board of Education, 1954, note 11 ; Clark et Clark, 1947"),
    ("rachel-carson", "Rachel Carson", "1907 / 1964", "claire", "cardigan", c("#3E6B48", "#2F3B59", "#E8DDC0"), ("court", "cheveux", 1), None, "carnet",
     maitriser("chim.quotidien"),
     "Biologiste marine, elle publie en 1962 Printemps silencieux, sur les dégâts des pesticides comme le DDT. L'industrie chimique la traite de « fanatique ». Un comité scientifique présidentiel lui donne en grande partie raison en 1963, et le DDT agricole est interdit aux États-Unis en 1972. Elle meurt d'un cancer deux ans après le livre.",
     "Linda Lear, Rachel Carson : Witness for Nature, 1997"),
]


# v18 : un ou plusieurs savants pour chaque arbre et chaque compétence qui n'en avaient pas (savants_v18.py).
from savants_v18 import SAVANTS_V18
SAVANTS += SAVANTS_V18


def savant(s):
    id, nom, annees, peau, style, couleurs, (coif, fam_c, base_c), barbe_, objet_, cond, notice, source = s
    t = toile()
    peindre_corps(t, peau)
    t2 = toile()
    tenue(t2, style)
    t.px.update(t2.px)
    if barbe_:
        b = toile()
        barbe(b, *barbe_)
        b.contour()
        t.px.update(b.px)
    o = toile()
    objet(o, objet_)
    o.contour()
    t.px.update(o.px)
    return t, coiffure(coif, fam_c, base_c)


def calques():
    out = []
    for s in SAVANTS:
        base, cheveux = savant(s)
        out.append({"id": s[0], "base": base.lignes(), "cheveux": cheveux.lignes()})
    return out


if __name__ == "__main__":
    import sys
    from PIL import Image
    from dessin import apercu
    parts = []
    for s, cq in zip(SAVANTS, calques()):
        img = [list(l) for l in cq["base"]]
        for y, l in enumerate(cq["cheveux"]):
            for x, ch in enumerate(l):
                if ch != ".":
                    img[y][x] = ch
        apercu({s[0]: ["".join(l) for l in img]}, "/tmp/_s.png", extra=s[5], colonnes=1, echelle=4)
        parts.append(Image.open("/tmp/_s.png").copy())
    w, h = parts[0].size
    planche = Image.new("RGB", (w * 10, h * ((len(parts) + 9) // 10)), (243, 233, 210))
    for i, p in enumerate(parts):
        planche.paste(p, ((i % 10) * w, (i // 10) * h))
    planche.save(sys.argv[1])
