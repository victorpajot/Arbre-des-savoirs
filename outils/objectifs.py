"""v4 : la case centrale du plateau, objectif de chaque tour.

Chaque tour terminé rapporte la relique du tour (cabinet), un succès et un masque de l'IA.
Les reliques sont dessinées ici en 32 × 32 et rejoignent les objets du cabinet.
"""
import math

from aides import anecdote, citation, fr, succes
from dessin import anneau, bande, disque, ellipse, poly, rect, texte, trait
from icones32 import flammes
from objets32 import dessin, toile

# Relique, dans l'ordre des tours : id, nom, année, notice, source.
RELIQUES = [
    ("flamme-promethee", "La flamme de Prométhée", None,
     "Prométhée vole le feu aux dieux et le rapporte aux hommes caché dans une tige de férule, une plante dont la moelle sèche brûle lentement. Zeus l'enchaîne au Caucase, où un aigle lui dévore chaque jour le foie, qui repousse chaque nuit. Le foie est bien l'un des rares organes capables de se régénérer.",
     "Hésiode, Théogonie, v. 521-616 ; Eschyle, Prométhée enchaîné"),
    ("pierre-philosophale", "La pierre philosophale", 1669,
     "Elle devait changer le plomb en or. En 1669, à Hambourg, Hennig Brand la cherche en faisant bouillir des dizaines de seaux d'urine. Il obtient une substance qui brille dans le noir : le phosphore, premier élément découvert par une personne connue. Pas d'or, mais un élément.",
     "John Emsley, The 13th Element, 2000"),
    ("mecanisme-anticythere", "Le mécanisme d'Anticythère", -100,
     "Une boîte de bronze à une trentaine d'engrenages, repêchée en 1901 par des pêcheurs d'éponges grecs dans une épave du Ier siècle avant notre ère. Elle calculait la position du Soleil et de la Lune et prédisait les éclipses. Il faudra plus de mille ans pour revoir une mécanique aussi fine.",
     "Tony Freeth et al., Nature, 2006"),
    ("principia", "Les Principia", 1687,
     "Les Principes mathématiques de la philosophie naturelle de Newton. La Royal Society, ruinée par un luxueux livre sur les poissons, ne peut payer l'impression : c'est Edmond Halley qui la finance de sa poche. On le rémunère ensuite en exemplaires invendus de l'Histoire des poissons.",
     "Royal Society, procès-verbaux de 1686 ; Willughby, De Historia Piscium, 1686"),
    ("ruban-turing", "Le ruban de Turing", 1936,
     "Une machine imaginaire : un ruban infini, une tête qui lit, écrit et se déplace d'une case. Turing montre qu'elle peut calculer tout ce qui est calculable, et qu'aucune machine ne peut décider, pour toutes les autres, si elles finiront par s'arrêter.",
     "Alan Turing, « On Computable Numbers », Proceedings of the London Mathematical Society, 1936"),
    ("disque-voyager", "Le disque d'or de Voyager", 1977,
     "Un disque de cuivre plaqué or, envoyé avec les sondes Voyager : 115 images, des saluts en 55 langues, des baleines, Bach et Chuck Berry. Le mode d'emploi est gravé sur la pochette. Les sondes ont quitté le système solaire ; le disque devrait durer un milliard d'années.",
     "Carl Sagan et al., Murmurs of Earth, 1978"),
    ("demon-laplace", "Le démon de Laplace", 1814,
     "Une intelligence qui connaîtrait à un instant donné toutes les forces et toutes les positions pourrait calculer l'avenir entier. Laplace l'imagine pour défendre le déterminisme. Le chaos et la mécanique quantique l'ont depuis mis au chômage. L'IA, elle, postule.",
     "Pierre-Simon de Laplace, Essai philosophique sur les probabilités, 1814"),
]


def objectifs():
    """Objectif affiché au centre du plateau, tour par tour."""
    return [{"tour": i + 1, "relique": r[0], "nom": fr(r[1])} for i, r in enumerate(RELIQUES)]


def objets():
    """Reliques du cabinet : une par tour terminé."""
    return [(id, nom, annee, notice, source, {"type": "tours_plateau", "n": i + 1})
            for i, (id, nom, annee, notice, source) in enumerate(RELIQUES)]


# Succès des tours 3 à 7 (les tours 1 et 2 ont déjà les leurs, dans plateau.py).
SUCCES = [
    succes("cycle-meton", "Dix-neuf ans, deux cent trente-cinq lunes", "Terminer trois tours du plateau. Le mécanisme d'Anticythère vous attendait.",
           {"type": "tours_plateau", "n": 3},
           anecdote("Le mécanisme d'Anticythère suit le cycle de Méton : 19 années solaires valent presque exactement 235 mois lunaires. Les Grecs en tiraient un calendrier, le mécanisme le mettait en engrenages.",
                    "Tony Freeth et al., Nature, 2006")),
    succes("hypotheses-non-fingo", "Je ne feins pas d'hypothèses", "Terminer quatre tours du plateau. Les Principia sont à vous, Halley a payé.",
           {"type": "tours_plateau", "n": 4},
           citation("Je n'ai pu encore parvenir à déduire des phénomènes la raison de ces propriétés de la gravité, et je ne feins pas d'hypothèses.",
                    "Isaac Newton", "Principia, scholie général, 2e édition, 1713 (traduction d'Émilie du Châtelet)")),
    succes("infaillible", "Ni infaillible ni bête", "Terminer cinq tours du plateau. Vous ne vous êtes toujours pas arrêté.",
           {"type": "tours_plateau", "n": 5},
           citation("Si l'on attend d'une machine qu'elle soit infaillible, elle ne peut pas être aussi intelligente.",
                    "Alan Turing", "Conférence à la London Mathematical Society, 20 février 1947 (traduction)")),
    succes("point-bleu", "Un point bleu pâle", "Terminer six tours du plateau. Le disque d'or file vers les étoiles, avec votre nom dessus, en esprit.",
           {"type": "tours_plateau", "n": 6},
           citation("Regardez encore ce point. C'est ici. C'est notre foyer. C'est nous.",
                    "Carl Sagan", "Pale Blue Dot, 1994 (traduction)")),
    succes("demon-laplace", "Rien ne serait incertain", "Terminer sept tours du plateau. Le démon de Laplace vous regarde avec envie.",
           {"type": "tours_plateau", "n": 7},
           citation("Rien ne serait incertain pour elle, et l'avenir, comme le passé, serait présent à ses yeux.",
                    "Pierre-Simon de Laplace", "Essai philosophique sur les probabilités, 1814")),
]


# --- Reliques en pixel art ------------------------------------------------------

@dessin
def flamme_promethee():
    t = toile()
    # La tige de férule, en biais, et le feu qui couve à son sommet.
    t.peindre(bande((9, 30), (19, 14), 1.4, 2.2), "vert", "cyl_v", 2)
    for y in (26, 21):
        x = 9 + (30 - y) * 10 / 16
        t.peindre(trait(round(x) - 2, y, round(x) + 2, y - 1), "vert", "plat", 0)
    flammes(t, 20, 15, 14, 7)
    t.poser({(14, 4), (25, 7), (27, 2)}, "j")
    return t.contour()


@dessin
def pierre_philosophale():
    t = toile()
    t.peindre(ellipse(16, 26, 11, 3.2), "or", "cyl_h", 2)
    gemme = poly([(16, 4), (25, 11), (22, 23), (10, 23), (7, 11)])
    t.peindre(gemme, "rouge", "sphere", 2)
    t.peindre(poly([(16, 4), (20, 11), (12, 11)]), "rouge", "plat", 3)
    t.peindre(trait(7, 11, 25, 11), "rouge", "plat", 1)
    t.poser({(13, 7), (12, 8), (14, 14), (13, 15)}, "w")
    t.poser({(4, 5), (28, 17), (27, 4)}, "j")
    return t.contour()


@dessin
def mecanisme_anticythere():
    t = toile()
    dents = set()
    for i in range(14):
        a = 2 * math.pi * i / 14
        cx, cy = 16 + 12.5 * math.cos(a), 15 + 12.5 * math.sin(a)
        dents |= disque(cx, cy, 1.6)
    t.peindre(dents | disque(16, 15, 11.5), "cuivre", "sphere", 1)
    t.effacer(disque(16, 15, 8.2) - disque(16, 15, 2.6))
    for a in (0, 60, 120):
        r = math.radians(a)
        t.peindre(bande((16 - 8 * math.cos(r), 15 - 8 * math.sin(r)), (16 + 8 * math.cos(r), 15 + 8 * math.sin(r)), 1), "cuivre", "plat", 1)
    t.peindre(disque(16, 15, 2.4), "cuivre", "sphere", 2)
    # Vert-de-gris : deux mille ans sous la mer.
    t.poser({(7, 9), (8, 9), (24, 21), (25, 20), (11, 24), (21, 6), (6, 18)}, "E")
    t.poser({(8, 10), (23, 21), (12, 24)}, "i")
    t.peindre(rect(9, 28, 22, 30), "bois", "biseau", 2)
    return t.contour()


@dessin
def principia():
    t = toile()
    t.peindre(rect(6, 3, 25, 28), "bois", "biseau", 1)
    t.peindre(rect(24, 4, 27, 29), "parchemin", "plat", 1)
    t.peindre(rect(8, 5, 23, 26) - rect(9, 6, 22, 25), "or", "plat", 1)
    t.peindre(ellipse(15.5, 15.5, 5.5, 3) - ellipse(15.5, 15.5, 4.5, 2), "or", "plat", 2)
    t.peindre(disque(15.5, 15.5, 1.6), "or", "sphere", 3)
    t.peindre(disque(20, 13.5, 0.9), "bleu", "plat", 2)
    t.peindre(texte("I", 14, 20) | texte("I", 17, 20) | texte("I", 11, 20), "or", "plat", 1)
    return t.contour()


@dessin
def ruban_turing():
    t = toile()
    t.peindre(rect(0, 15, 31, 25), "parchemin", "cyl_h", 2)
    for x in range(0, 32, 6):
        t.poser(rect(x, 15, x, 25), "A")
    for i, c in enumerate("10110"):
        t.poser(texte(c, 2 + i * 6, 18), "N")
    # La tête de lecture, au-dessus de la troisième case.
    t.peindre(poly([(10, 4), (22, 4), (22, 9), (16, 14), (10, 9)]), "gris", "biseau", 3)
    t.poser({(15, 6), (16, 6), (15, 7), (16, 7)}, "r")
    return t.contour()


@dessin
def disque_voyager():
    t = toile()
    t.peindre(disque(16, 16, 14), "or", "plat", 2)
    for r in (13, 11, 9, 7):
        t.poser(anneau(16, 16, r, 0.9), "Y")
    t.peindre(disque(16, 16, 4.6), "or", "plat", 3)
    t.poser(disque(16, 16, 1.2), "4")
    # Reflet de la lumière sur le sillon.
    t.poser({(8, 9), (9, 8), (10, 7), (9, 9), (10, 8), (11, 7), (22, 24), (23, 23)}, "j")
    return t.contour()


@dessin
def demon_laplace():
    t = toile()
    tete = ellipse(16, 18, 10, 10)
    cornes = poly([(7, 13), (4, 2), (11, 9)]) | poly([(25, 13), (28, 2), (21, 9)])
    t.peindre(cornes, "gris", "biseau", 4)
    t.peindre(tete, "violet", "sphere", 2)
    for cx in (12, 20):
        t.peindre(disque(cx, 17, 2.6), "cyan", "sphere", 1)
        t.poser({(cx, 17)}, "N")
    t.peindre(bande((11, 24), (21, 24), 0.8), "violet", "plat", 0)
    t.poser({(13, 25), (19, 25)}, "w")
    return t.contour()
