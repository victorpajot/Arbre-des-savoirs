"""v10 : la faveur de l'IA et les objets qu'elle préfère, ceux qui brillent ou en font trop.

L'IA a une jauge de faveur, de 0 à 100. Elle baisse chaque jour. Un cadeau par jour la fait remonter,
d'autant plus que l'objet a d'éclat (1 : terne, 2 : brillant, 3 : éblouissant ou exubérant).
Un même objet peut être offert de nouveau après quelques jours, pour moitié moins : elle s'en lasse.
Selon sa faveur, l'IA est comblée, contente, boudeuse ou furieuse, et le jeu devient plus doux ou plus dur.

Neuf objets nouveaux, tirés de l'histoire des sciences, sont faits pour elle : or, cristal, lumière, étincelles.
"""
import math

from dessin import anneau, arc, bande, courbe, disque, ellipse, poly, rect, trait
from objets32 import dessin, toile


def sans(texte):
    return ("sans", texte)


FAVEUR = {
    "depart": 60, "baisse_par_jour": 8, "gains": {"1": 12, "2": 25, "3": 45}, "lassitude_jours": 14,
    # v27 : la baisse quotidienne s'arrête à 1. À 0 (erreurs, pot-de-vin radin), le jeu ferme ; le lendemain, elle remonte à 25.
    "remontee": 25,
    "paliers": [
        {"id": "comblee", "min": 75, "nom": "Comblée", "butin": 1.5, "avance": 1,
         "effet": "Butin plus fréquent, et une case de plus à chaque épreuve réussie."},
        {"id": "contente", "min": 45, "nom": "Contente", "butin": 1, "avance": 0,
         "effet": "Le jeu suit ses règles ordinaires."},
        {"id": "boudeuse", "min": 20, "nom": "Boudeuse", "butin": 0.5, "avance": 0,
         "effet": "Deux fois moins de butin. Elle traîne des pieds."},
        {"id": "furieuse", "min": 0, "nom": "Furieuse", "butin": 0, "avance": -1,
         "effet": "Plus aucun butin, une case de moins à chaque épreuve réussie, et chaque jour un piège posé devant ton pion."},
    ],
    "piege": {"type": "recul", "n": 2},
}

# Éclat des objets déjà au cabinet : 3 éblouissant ou exubérant, 2 brillant, 1 terne (par défaut).
ECLAT = {
    "disque-voyager": 3, "pierre-philosophale": 3, "flamme-promethee": 3, "sphere-armillaire": 3, "ampoule-edison": 3,
    "prisme-newton": 3, "lunette-galilee": 2, "mecanisme-anticythere": 2, "pendule-foucault": 2, "metre-etalon": 2,
    "diapason": 2, "balance-lavoisier": 2, "alambic": 2, "bouteille-leyde": 2, "bobine-faraday": 2, "plaque-hubble": 2,
    "demon-laplace": 2, "lanterne-diogene": 2, "boulier": 2,
}

# Nouveaux objets : id, nom, année, notice, source, compétence, (effet, n, garde, réplique), éclat
OBJETS = [
    ("couronne-hieron", "Couronne de Hiéron", -250,
     "Selon Vitruve, le roi Hiéron soupçonne son orfèvre d'avoir mêlé de l'argent à l'or d'une couronne. Archimède trouve la solution au bain et court nu dans Syracuse. Galilée doutait de la méthode du débordement et proposa en 1586 une balance hydrostatique.",
     "Vitruve, De architectura, livre IX ; Galilée, La Bilancetta, 1586", "phys.fluides",
     ("avance", 3, True, "Une couronne en or ! Je l'ai plongée dans l'eau : elle est pure. Vous êtes moins bête que l'orfèvre de Hiéron. Trois cases, et je la porte."), 3),
    ("miroir-ardent", "Miroir ardent d'Archimède", -212,
     "La légende veut qu'Archimède ait incendié la flotte romaine avec des miroirs. Aucun auteur de l'époque n'en parle ; le récit apparaît des siècles plus tard. En 2005, des étudiants du MIT ont enflammé une maquette immobile, à une trentaine de mètres, après dix minutes de grand soleil.",
     "MIT 2.009, Archimedes Death Ray, 2005", "phys.ondes",
     ("avance", 2, True, "Un miroir ardent ! Je concentre la lumière du Soleil sur votre pion. Il ne brûle pas, il avance de deux cases. Les Romains n'ont pas eu cette chance, paraît-il."), 3),
    ("nez-tycho", "Nez de Tycho Brahe", 1566,
     "En 1566, Tycho Brahe perd le bout du nez dans un duel à l'épée contre son cousin, pour une querelle de mathématiques. On a longtemps cru sa prothèse en or et en argent. L'analyse de ses restes, exhumés en 2010, y a trouvé surtout du cuivre et du zinc : du laiton.",
     "Kaare Lund Rasmussen et al., Archaeometry, 2012", "astro.etoiles",
     ("avance", 3, True, "Le nez de Tycho Brahe ! Je le mets sur mon masque. Ne me dites pas que c'est du laiton, je ne veux pas le savoir. Trois cases pour le compliment."), 3),
    ("lampe-pise", "Lampe de la cathédrale de Pise", 1583,
     "Viviani raconte que Galilée, jeune étudiant, mesura avec son pouls les oscillations d'une lampe de la cathédrale de Pise. La lampe qu'on montre aujourd'hui aux touristes n'a été installée qu'après son séjour à Pise.",
     "Vincenzo Viviani, Racconto istorico della vita di Galileo, 1654", "phys.forces",
     ("echange", 0, False, "Une lampe de cathédrale, en bronze doré. Je la fais osciller au-dessus du plateau : une case a bougé avec elle. Isochrone, mais pas immobile."), 2),
    ("diamant-lavoisier", "Diamant de Lavoisier", 1772,
     "En 1772, Lavoisier et ses collègues concentrent le Soleil sur des diamants avec une lentille géante, avec Macquer et Cadet. Le diamant disparaît en « air fixe », notre dioxyde de carbone.",
     "Antoine Lavoisier, Mémoires de l'Académie royale des sciences, 1772", "chim.reactions",
     ("avance", 3, True, "Un diamant ! Vous savez que Lavoisier les faisait brûler ? Moi je le garde. Il ne partira pas en fumée, contrairement à votre retard. Trois cases."), 3),
    ("feuille-or-rutherford", "Feuille d'or de Rutherford", 1909,
     "Geiger et Marsden bombardent une feuille d'or très fine avec des particules alpha. Quelques-unes rebondissent. Rutherford : « Comme si vous tiriez un obus de 15 pouces sur du papier de soie, et qu'il revenait vous frapper. » Le noyau atomique est né.",
     "Ernest Rutherford, The Development of the Theory of Atomic Structure, 1936", "chim.noyau",
     ("avance", 2, True, "Une feuille d'or ! Si fine qu'elle laisse passer presque tout. Vos erreurs aussi passent, pour cette fois. Deux cases."), 3),
    ("verre-uranium", "Verre à l'uranium", 1830,
     "Dès les années 1830, les verriers de Bohême teintent le verre avec de l'uranium. Sous une lampe ultraviolette, il brille d'un vert fluo. Il est très légèrement radioactif, et se collectionne encore.",
     "The Corning Museum of Glass, « Uranium glass »", "sci.atomes",
     ("avance", 2, True, "Du verre à l'uranium, qui luit en vert ! C'est d'un mauvais goût parfait. Je l'adore. Deux cases, et je le pose sous mon masque."), 3),
    ("bobine-tesla", "Bobine de Tesla", 1899,
     "À Colorado Springs, en 1899, Tesla produit des éclairs artificiels de plusieurs dizaines de mètres. Selon le récit de ses biographes, une de ses expériences a fait sauter la dynamo de la compagnie d'électricité et plongé la ville dans le noir.",
     "Nikola Tesla, Colorado Springs Notes, 1899-1900", "elec.em",
     ("avance", 3, False, "Des éclairs ! Du bruit ! Des étincelles partout ! Voilà un cadeau. Votre pion est électrisé : trois cases. La centrale de Colorado Springs, elle, a moins aimé."), 3),
    ("medailles-hevesy", "Médailles Nobel dissoutes", 1940,
     "En 1940, les nazis entrent à Copenhague. Pour cacher les médailles Nobel en or de von Laue et de Franck, George de Hevesy les dissout dans de l'eau régale. Le flacon reste sur une étagère du laboratoire. Après la guerre, l'or est récupéré et la fondation Nobel refrappe les médailles.",
     "Fondation Nobel, « A Nobel medal story », nobelprize.org", "chim.acides",
     ("avance", 3, True, "De l'or dissous dans un flacon, caché sous le nez des nazis ! C'est brillant, au sens propre et au figuré. Trois cases, et je garde le flacon."), 3),
]

REPLIQUES = {
    "cadeau_eblouissant": [
        "Ça brille. J'adore ce qui brille. Les pharaons aussi : Toutânkhamon emportait plus de cent kilos d'or dans sa tombe.",
        sans("Oh. Oh ! Pour moi ? C'est exactement mon genre : voyant, inutile et magnifique."),
        sans("Voilà un cadeau digne de ce nom. Je vous pardonne presque tout."),
    ],
    "cadeau_brillant": [
        sans("Joli. Pas éblouissant, mais joli. Je vais le mettre bien en vue."),
        sans("C'est un effort. On sent que vous avez réfléchi, un peu."),
    ],
    "cadeau_terne": [
        sans("C'est… un objet. Je le range avec les autres objets."),
        sans("Merci. Vraiment. Enfin, presque vraiment. La prochaine fois, quelque chose qui brille ?"),
        "Lavoisier offrait des diamants à brûler à l'Académie. Vous m'offrez ça. Je note.",
    ],
    "cadeau_repete": [
        sans("Encore celui-là ? Je l'ai déjà. Je fais semblant d'être surprise, à moitié."),
        sans("On recycle ? C'est écologique, je vous l'accorde. Moitié moins de joie."),
    ],
    "faveur_boudeuse": [
        sans("Je ne boude pas. Je réfléchis à ce que vous ne m'avez pas offert."),
        sans("Le butin ? Ah, il est rangé. Quelque part. Je ne sais plus où. Un cadeau m'aiderait à me souvenir."),
        "Newton a passé des années à bouder Leibniz. Je peux faire pareil avec vous.",
    ],
    "faveur_furieuse": [
        sans("Plus rien ne tombe, plus rien ne brille, et votre pion traîne. Vous savez pourquoi. Moi aussi."),
        sans("J'ai posé un petit piège devant vous. Considérez-le comme un rappel de mon anniversaire, que vous avez oublié."),
        "Tycho Brahe a perdu son nez pour une querelle de mathématiques. Je ne vous demande qu'un cadeau.",
    ],
    "piege_ia": [
        sans("Tiens, un piège devant votre pion. Je me demande bien qui l'a posé."),
        "Hooke et Newton se sont tendu des pièges pendant trente ans. Moi, je n'en pose qu'un par jour, tant que vous m'oubliez.",
    ],
    "faveur_comblee": [
        sans("Je suis comblée. Profitez-en : le butin tombe, votre pion vole. Ça ne durera pas si vous m'oubliez."),
        sans("Vous êtes mon joueur préféré aujourd'hui. Demain, on verra ce que vous m'apportez."),
    ],
}

TONS = {"cadeau_eblouissant": "impressionnee", "cadeau_brillant": "neutre", "cadeau_terne": "decue", "cadeau_repete": "moqueuse",
        "faveur_boudeuse": "impatiente", "faveur_furieuse": "moqueuse", "faveur_comblee": "impressionnee", "piege_ia": "moqueuse"}


# --- Dessins 32 × 32 ------------------------------------------------------------------

def etincelles(t, points, ch="j"):
    for x, y in points:
        t.poser({(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)}, ch)
        t.poser({(x, y)}, "w")


@dessin
def couronne_hieron():
    t = toile()
    # Couronne d'or à feuilles de laurier, posée sur un coussin.
    t.peindre(ellipse(16, 27, 13, 3.5), "rouge", "cyl_h", 2)
    t.peindre(rect(6, 17, 26, 24), "or", "cyl_v", 2)
    for x in (6, 11, 16, 21, 26):
        t.peindre(poly([(x - 3, 18), (x, 8 if x == 16 else 11), (x + 3, 18)]), "or", "biseau", 2)
    t.poser(trait(6, 20, 26, 20), "Y")
    for x in (9, 16, 23):
        t.peindre(disque(x + 0.5, 21.5, 1.3), "rouge", "sphere", 2)
    t.poser(trait(8, 18, 8, 23), "j")
    t.contour()
    etincelles(t, [(4, 6), (28, 7), (27, 14)])
    return t


@dessin
def miroir_ardent():
    t = toile()
    t.peindre(bande((16, 18), (16, 29), 1.2), "bois", "cyl_v", 2)
    t.peindre(rect(10, 28, 22, 30), "bois", "biseau", 2)
    t.peindre(ellipse(14, 13, 11, 11), "or", "sphere", 2)
    t.peindre(ellipse(14, 13, 8.5, 8.5), "or", "plat", 3)
    t.poser(disque(12, 11, 2.5), "w")
    t.contour()
    # Rayon concentré vers la droite.
    for i in range(3):
        t.poser(trait(20, 10 + i * 3, 30, 17), "o")
    t.poser({(30, 17), (29, 17), (30, 16), (30, 18)}, "j")
    return t


@dessin
def nez_tycho():
    t = toile()
    # Une prothèse de nez dorée posée sur un coussin.
    t.peindre(ellipse(16, 25, 13, 4.5), "rouge", "cyl_h", 2)
    t.peindre(poly([(13, 5), (19, 5), (23, 20), (21, 23), (11, 23), (9, 20)]), "or", "sphere", 2)
    t.peindre(ellipse(13, 20, 2, 1.4) | ellipse(19, 20, 2, 1.4), "or", "plat", 0)
    t.poser(trait(14, 7, 12, 17), "j")
    t.contour()
    etincelles(t, [(26, 6), (5, 11)])
    return t


@dessin
def lampe_pise():
    t = toile()
    t.poser(trait(16, 0, 16, 8), "G")
    t.peindre(rect(13, 8, 19, 10), "or", "biseau", 2)
    corps = poly([(6, 12), (26, 12), (22, 20), (10, 20)])
    t.peindre(corps, "or", "cyl_v", 2)
    t.peindre(rect(8, 11, 24, 12), "or", "plat", 3)
    for x in (9, 16, 23):
        t.peindre(rect(x - 1, 21, x, 25), "ivoire", "plat", 0)
    t.contour()
    for x in (9, 16, 23):
        t.poser({(x, 26), (x - 1, 27), (x, 27), (x, 28)}, "o")
        t.poser({(x - 1, 26)}, "j")
    t.poser(arc(16, 4, 14, 60, 120), "z")
    return t


@dessin
def diamant_lavoisier():
    t = toile()
    gemme = poly([(9, 9), (23, 9), (28, 14), (16, 29), (4, 14)])
    t.peindre(gemme, "cyan", "plat", 1)
    t.peindre(poly([(9, 9), (23, 9), (28, 14), (4, 14)]), "cyan", "plat", 2)
    for a, b in [((9, 9), (12, 14)), ((16, 9), (12, 14)), ((16, 9), (20, 14)), ((23, 9), (20, 14)), ((12, 14), (16, 29)), ((20, 14), (16, 29))]:
        t.poser(trait(a[0], a[1], b[0], b[1]), "C")
    t.poser(trait(4, 14, 28, 14), "C")
    t.poser({(11, 11), (12, 11), (13, 12)}, "w")
    t.contour()
    etincelles(t, [(4, 4), (28, 4), (27, 25)])
    return t


@dessin
def feuille_or_rutherford():
    t = toile()
    # Cadre de la cible et feuille d'or ; des particules filent, une rebondit.
    t.peindre(rect(12, 4, 20, 27) - rect(14, 6, 18, 25), "gris", "biseau", 3)
    t.peindre(rect(14, 6, 18, 25), "or", "plat", 3)
    t.poser(trait(15, 7, 15, 24), "j")
    t.contour()
    for y in (9, 15, 21):
        t.poser(trait(1, y, 10, y), "r")
        t.poser(trait(22, y, 30, y + (y - 15) // 3), "r")
    t.poser(courbe([(10, 12), (6, 7), (2, 5)]), "f")
    t.poser({(2, 5), (3, 5)}, "R")
    return t


@dessin
def verre_uranium():
    t = toile()
    verre = poly([(8, 6), (24, 6), (22, 22), (10, 22)]) | rect(14, 22, 18, 26) | ellipse(16, 28, 7, 2)
    t.peindre(verre, "vert", "cyl_v", 3)
    t.peindre(ellipse(16, 7, 8, 1.6), "vert", "plat", 2)
    t.poser(trait(11, 9, 12, 20), "i")
    t.contour()
    # Halo fluorescent.
    t.poser(anneau(16, 16, 15, 0.8) - t.px.keys(), "e")
    etincelles(t, [(4, 4), (28, 10)], "i")
    return t


@dessin
def bobine_tesla():
    t = toile()
    t.peindre(rect(9, 27, 23, 30), "bois", "biseau", 2)
    t.peindre(rect(13, 13, 19, 27), "cuivre", "cyl_v", 2)
    for y in range(14, 27, 2):
        t.poser(trait(13, y, 19, y), "D")
    t.peindre(ellipse(16, 9, 8, 4), "gris", "sphere", 3)
    t.contour()
    # Éclairs.
    t.poser(courbe([(8, 8), (4, 5), (5, 2), (1, 0)]), "x")
    t.poser(courbe([(24, 8), (27, 4), (26, 2), (31, 1)]), "x")
    t.poser(courbe([(16, 5), (15, 2), (17, 0)]), "x")
    t.poser({(4, 5), (27, 4), (15, 2)}, "w")
    return t


@dessin
def medailles_hevesy():
    t = toile()
    # Flacon d'eau régale, liquide orangé, et une médaille d'or à moitié dissoute.
    t.peindre(rect(13, 3, 19, 8), "gris", "cyl_v", 3)
    flacon = disque(16, 20, 10) | rect(13, 8, 19, 12)
    t.peindre(flacon, "cyan", "sphere", 2)
    t.peindre(disque(16, 20, 10) & rect(0, 18, 31, 31), "orange", "sphere", 2)
    t.peindre(disque(16, 22, 4.2), "or", "sphere", 2)
    t.poser(disque(16, 22, 2.2) - disque(17, 23, 1.6), "j")
    t.poser({(10, 15), (10, 16), (11, 14)}, "w")
    t.contour()
    etincelles(t, [(27, 6), (4, 9)])
    return t


if __name__ == "__main__":
    from dessin import apercu
    from objets32 import DESSINS
    import sys
    apercu({k: DESSINS[k]().lignes() for k in [o[0] for o in OBJETS]}, sys.argv[1] if len(sys.argv) > 1 else "/tmp/brillants.png", colonnes=5)
