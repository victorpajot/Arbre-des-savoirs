"""Dessins de leçon (pixel art 48 × 48) des masterclass du pack « L'île ».

Un dessin = une fonction qui rend une Toile. ILLUS dit sous quel paragraphe de quel chapitre il se place
(champs `dessin` et `dessin_apres` du chapitre, voir packs/LISEZMOI-IA.md). Le dessin montre l'objet ou
l'espèce dont parle le paragraphe, pas une autre.

    python3 outils/dessins_ile.py            # écrit packs/ile/dessins.json et les champs des chapitres
    python3 outils/dessins_ile.py --apercu   # planche PNG dans le dossier courant (dessins-ile.png)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dessin import Toile, apercu, arc, bande, courbe, disque, ellipse, poly, rect, trait  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(RACINE, "packs", "ile")


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


DESSINS = {"mc-orge-sauvage": epi_orge, "mc-chevre": chevre, "mc-thon": thon}

# (compétence, chapitre) → (dessin, indice du paragraphe qui en parle)
ILLUS = {
    ("res.cultiver", "semer"): ("mc-orge-sauvage", 1),
    ("res.cultiver", "elever"): ("mc-chevre", 1),
    ("res.cultiver", "pecher"): ("mc-thon", 0),
}


def main():
    images = {k: f().lignes() for k, f in DESSINS.items()}
    if "--apercu" in sys.argv:
        apercu(images, "dessins-ile.png", colonnes=len(images), echelle=8)
        return
    chemin = os.path.join(PACK, "dessins.json")
    dessins = json.load(open(chemin, encoding="utf-8"))
    dessins.update(images)
    json.dump(dessins, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(chemin, "a", encoding="utf-8").write("\n")
    chemin = os.path.join(PACK, "competences.json")
    comps = json.load(open(chemin, encoding="utf-8"))
    for c in comps:
        for ch in (c.get("masterclass") or {}).get("chapitres", []):
            v = ILLUS.get((c["id"], ch.get("id")))
            if v:
                ch["dessin"], ch["dessin_apres"] = v
    json.dump(comps, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(chemin, "a", encoding="utf-8").write("\n")
    print(len(images), "dessins,", len(ILLUS), "chapitres illustrés")


if __name__ == "__main__":
    main()
