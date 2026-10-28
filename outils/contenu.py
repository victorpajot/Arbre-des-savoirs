"""Source du contenu du jeu. Génère les fichiers JSON de data/.

Usage : python3 outils/contenu.py
Convention : pour un QCM, la bonne réponse est écrite en premier ;
le jeu mélange les choix à l'affichage.
"""
import json
from pathlib import Path

from aides import anecdote, citation, fr, num, qcm, succes, vf
import approfondissement_humain
import approfondissement_sciences
import avatar40
import bibliotheque
import ia
import icones32
import masques
import objectifs
import objets32
import philosophes
import pionniers
import ennemis
import cadeaux
import pieges
import mendeleiev
import brillants
import credits
import fiches
import figures
import symboles
import succes_pixels
import themes
import succes_themes
import ia_themes
import honte
import masques_regles
import objets_v11
import tenues_farce
import alyca
import extraits
import bibliotheque_v7
import bibliotheque_v8
import plateau
import parcours
import savants
import portraits
from dessin import EMPLACEMENTS, PALETTE
from illustrations import ENONCE, EXPLICATION
from questions_nouvelles import Q as Q_NOUVELLES
from recompenses import ACCESSOIRES, OBJETS, SUCCES_V2, objet

DATA = Path(__file__).resolve().parent.parent / "data"


# --- Règles -----------------------------------------------------------------

REGLES = {
    "format": 1,
    # v7 : arbres ouverts dès le départ ; les autres s'ouvrent par un succès de pionnier (pionniers.py).
    "arbres_fondamentaux": pionniers.FONDAMENTAUX,
    "stats": [
        {"id": "logique", "nom": fr("Logique"), "branche": fr("Mathématiques"), "couleur": "#3D63D9",
         "description": fr("Calculer, raisonner, estimer les probabilités.")},
        {"id": "mecanique", "nom": fr("Mécanique"), "branche": fr("Physique"), "couleur": "#D9822B",
         "description": fr("Comprendre les forces, l'énergie, la lumière et les ordres de grandeur.")},
        {"id": "savoir", "nom": fr("Savoir"), "branche": fr("Sciences du vivant"), "couleur": "#2E9E6A",
         "description": fr("La méthode scientifique, la cellule, l'évolution et la génétique.")},
        {"id": "eloquence", "nom": fr("Éloquence"), "branche": fr("Rhétorique"), "couleur": "#8A4FD1",
         "description": fr("Construire un argument, persuader, repérer les sophismes.")},
        {"id": "lucidite", "nom": fr("Lucidité"), "branche": fr("Biais cognitifs"), "couleur": "#0E95A3",
         "description": fr("Voir les pièges de son propre jugement.")},
        {"id": "empathie", "nom": fr("Empathie"), "branche": fr("Psychologie"), "couleur": "#D04A78",
         "description": fr("Émotions, mémoire, motivation et influence des autres.")},
        {"id": "alchimie", "nom": fr("Alchimie"), "branche": fr("Chimie"), "couleur": "#C8443A",
         "description": fr("Les éléments, les liaisons, les acides et les bases, les réactions.")},
        {"id": "cosmos", "nom": fr("Cosmos"), "branche": fr("Astronomie"), "couleur": "#4F46B8",
         "description": fr("Le Système solaire, les étoiles, les orbites et l'histoire de l'Univers.")},
        {"id": "etincelle", "nom": fr("Étincelle"), "branche": fr("Électricité"), "couleur": "#A67C00",
         "description": fr("Circuits, loi d'Ohm, puissance, magnétisme et induction.")},
        {"id": philosophes.STAT["id"], "nom": fr(philosophes.STAT["nom"]), "branche": fr(philosophes.STAT["branche"]),
         "couleur": philosophes.STAT["couleur"], "description": fr(philosophes.STAT["description"])},
    ],
    "xp": {
        "par_bonne_reponse": 10,
        "bonus_maitrise": 20,
        "par_rappel_reussi": 5,
        # XP d'un rappel réussi selon l'étape atteinte : garder un savoir longtemps rapporte de plus en plus.
        "rappel_par_etape": [5, 10, 15, 20, 30, 40, 50],
        "paliers_niveau": [0, 50, 110, 180, 260, 350, 450, 560, 680, 810, 950,
                           1100, 1260, 1430, 1610, 1800, 2000, 2210, 2430, 2660, 2900],
    },
    "quiz": {"questions_par_quiz": 5, "seuil_maitrise": 0.8},
    "chrono": {"secondes": 30, "bonus_xp_par_bonne_reponse": 5},
    "rappels": {
        "intervalles_jours": [1, 3, 7, 14, 30, 90, 180],
        "questions_par_rappel": 3,
        "bonnes_reponses_min": 2,
    },
    "aujourdhui": {"max_rappels": 8, "suggestion": "stat_la_plus_faible"},
}

# --- Compétences ------------------------------------------------------------
# Dans chaque branche : 1 racine, 2 compétences qui en dépendent, 1 sommet qui dépend des deux.
# Les ids sont stables : une compétence garde le sien même si elle change de branche (sci.atomes, passée en Alchimie en v2).

BRANCHES = {
    "logique": [
        ("math.arithmetique", "Arithmétique et fractions", "Les opérations, les priorités de calcul, les fractions et les nombres premiers."),
        ("math.proportions", "Proportions et pourcentages", "Règle de trois, échelles, hausses et baisses en pourcentage."),
        ("math.probabilites", "Probabilités", "Le hasard, l'indépendance, les paradoxes qui trompent l'intuition."),
        ("math.logique", "Logique formelle", "Implication, négation, syllogismes et raisonnement par l'absurde."),
    ],
    "mecanique": [
        ("phys.unites", "Unités et ordres de grandeur", "Le Système international, les préfixes et les tailles du monde."),
        ("phys.forces", "Forces et mouvement", "Les lois de Newton, la gravitation, l'inertie."),
        ("phys.energie", "Énergie", "Énergie cinétique et potentielle, puissance, conservation."),
        ("phys.ondes", "Ondes et lumière", "Son, lumière, fréquences, couleurs et effet Doppler."),
    ],
    "savoir": [
        ("sci.methode", "Méthode scientifique", "Hypothèse, réfutabilité, groupe témoin, reproductibilité."),
        ("sci.cellule", "La cellule", "Organites, ADN, division cellulaire."),
        ("sci.evolution", "Évolution", "Sélection naturelle, mutations, histoire du vivant."),
        ("sci.genetique", "Génétique", "Gènes, allèles, hérédité, ADN et mutations."),
    ],
    "eloquence": [
        ("rhet.argument", "Structure d'un argument", "Prémisses, conclusion, déduction et induction."),
        ("rhet.figures", "Figures de style", "Métaphore, litote, chiasme, anaphore et les autres."),
        ("rhet.persuasion", "Ethos, pathos, logos", "Les trois leviers de la persuasion selon Aristote."),
        ("rhet.sophismes", "Sophismes", "Les raisonnements fallacieux et comment les nommer."),
    ],
    "lucidite": [
        ("biais.confirmation", "Biais de confirmation", "Chercher ce qui nous donne raison et ignorer le reste."),
        ("biais.ancrage", "Effet d'ancrage", "Quand un premier chiffre tire nos estimations."),
        ("biais.disponibilite", "Heuristique de disponibilité", "Juger la fréquence d'un événement par les exemples qui viennent en tête."),
        ("biais.surconfiance", "Dunning-Kruger et métacognition", "Mesurer ce qu'on sait, et ce qu'on croit savoir."),
    ],
    "empathie": [
        ("psy.emotions", "Émotions", "Les émotions de base, leur rôle et leur régulation."),
        ("psy.memoire", "Mémoire", "Comment on retient, comment on oublie, comment on se trompe."),
        ("psy.motivation", "Motivation", "Ce qui nous fait agir et ce qui nous fait procrastiner."),
        ("psy.influence", "Influence sociale", "Conformisme, obéissance et leviers de persuasion."),
    ],
    "alchimie": [
        ("sci.atomes", "Atomes et éléments", "La structure de l'atome, les éléments et le tableau périodique."),
        ("chim.liaisons", "Liaisons et molécules", "Comment les atomes s'assemblent : liaisons covalentes, ioniques, polarité."),
        ("chim.acides", "Acides et bases", "Le pH, la neutralisation et les acides du quotidien."),
        ("chim.reactions", "Réactions et oxydoréduction", "Équations, combustion, catalyse, oxydation et réduction."),
    ],
    "cosmos": [
        ("astro.systeme", "Système solaire", "Le Soleil, les planètes, la Lune et les petits corps."),
        ("astro.etoiles", "Étoiles et lumière des astres", "Comment les étoiles brillent, vivent et meurent."),
        ("astro.orbites", "Orbites et gravitation", "Les lois de Kepler, les satellites, les marées, les trous noirs."),
        ("astro.galaxies", "Galaxies et Big Bang", "La Voie lactée, l'expansion de l'Univers et son histoire."),
    ],
    "etincelle": [
        ("elec.circuits", "Charges et circuits", "Charges, conducteurs, circuits en série et en dérivation."),
        ("elec.ohm", "Tension, intensité et loi d'Ohm", "Volts, ampères, ohms, et la relation qui les lie."),
        ("elec.puissance", "Puissance et énergie électrique", "Watts, kilowattheures, effet Joule et production d'électricité."),
        ("elec.magnetisme", "Magnétisme et induction", "Aimants, boussoles, électroaimants, moteurs et alternateurs."),
    ],
    "sagesse": philosophes.BRANCHE,
}
# v4 : second losange, rangs 5 à 8.
for _module in (approfondissement_sciences, approfondissement_humain):
    for _stat, _noeuds in _module.BRANCHES.items():
        BRANCHES[_stat] = BRANCHES[_stat] + _module.BRANCHES[_stat]


def fiche(id):
    f = fiches.FICHES[id]
    out = {"essentiel": [fr(x) for x in f["essentiel"]], "piege": fr(f["piege"]), "schema": f["schema"], "source": f["source"]}
    # v15 : planches figuratives (cellule, atome, cerveau…) en plus du schéma de la fiche.
    if id in figures.COMPETENCES:
        out["figures"] = figures.COMPETENCES[id]
    return out


def competences():
    out = []
    for stat, noeuds in BRANCHES.items():
        ids = [n[0] for n in noeuds]
        # Deux losanges : 1 → 2, 3 → 4, puis 4 → 5 → 6, 7 → 8.
        prerequis = [[], [ids[0]], [ids[0]], [ids[1], ids[2]], [ids[3]], [ids[4]], [ids[4]], [ids[5], ids[6]]][:len(ids)]
        for i, (id, nom, desc) in enumerate(noeuds):
            out.append({
                "id": id, "stat": stat, "rang": i + 1,
                "nom": fr(nom), "description": fr(desc), "prerequis": prerequis[i], "fiche": fiche(id),
                "symbole": symboles.SYMBOLES[id],
            })
    return out


# --- Questions --------------------------------------------------------------

Q = {}

Q["math.arithmetique"] = [
    qcm("Combien font 3/4 + 1/8 ?", ["7/8", "4/12", "1/2", "5/8"], "3/4 = 6/8, donc 6/8 + 1/8 = 7/8."),
    num("Combien font 7 × 8 ?", 56, "7 × 8 = 56."),
    qcm("Quelle fraction est la plus grande ?", ["2/3", "3/5", "5/8", "7/12"], "En décimal : 2/3 ≈ 0,667 ; 5/8 = 0,625 ; 3/5 = 0,6 ; 7/12 ≈ 0,583."),
    vf("Diviser par 1/2 revient à multiplier par 2.", True, "Diviser par une fraction revient à multiplier par son inverse : l'inverse de 1/2 est 2."),
    num("Combien font 2 + 3 × 4 ?", 14, "La multiplication passe avant l'addition : 3 × 4 = 12, puis 2 + 12 = 14."),
    qcm("Quel est le plus grand diviseur commun (PGCD) de 12 et 18 ?", ["6", "3", "2", "36"], "Les diviseurs communs sont 1, 2, 3 et 6. Le plus grand est 6."),
    vf("Tout nombre divisible par 9 est divisible par 3.", True, "9 = 3 × 3 : un multiple de 9 est donc aussi un multiple de 3."),
    num("Combien vaut le tiers de 27 ?", 9, "27 ÷ 3 = 9."),
    qcm("Lequel de ces nombres est premier ?", ["59", "51", "57", "91"], "51 = 3 × 17, 57 = 3 × 19 et 91 = 7 × 13. Seul 59 n'a pas d'autre diviseur que 1 et lui-même."),
    num("Combien font (−3) × (−4) ?", 12, "Le produit de deux nombres négatifs est positif : 3 × 4 = 12."),
    qcm("Combien vaut 2⁵ ?", ["32", "10", "25", "64"], "2 × 2 × 2 × 2 × 2 = 32. Ne pas confondre avec 2 × 5 = 10."),
    vf("La moitié d'un tiers est un sixième.", True, "1/2 × 1/3 = 1/6."),
]

Q["math.proportions"] = [
    qcm("Un article à 80 € est soldé à −25 %. Quel est son nouveau prix ?", ["60 €", "55 €", "64 €", "65 €"], "25 % de 80 € = 20 €, donc 80 − 20 = 60 €."),
    vf("Une hausse de 50 % suivie d'une baisse de 50 % ramène au prix de départ.", False, "100 € × 1,5 = 150 €, puis 150 € × 0,5 = 75 €. On a perdu 25 %."),
    num("Un prix passe de 40 € à 50 €. Quelle est la hausse en pourcentage ?", 25, "La hausse de 10 € rapportée au prix de départ de 40 € donne 10/40 = 25 %.", unite="%"),
    qcm("5 crayons coûtent 3 €. Combien coûtent 15 crayons ?", ["9 €", "8 €", "10 €", "7,50 €"], "15 crayons, c'est 3 fois plus que 5 : 3 × 3 € = 9 €."),
    num("Combien font 15 % de 200 ?", 30, "200 × 0,15 = 30."),
    qcm("Sur une carte au 1/25 000, 4 cm représentent :", ["1 km", "100 m", "10 km", "250 m"], "4 cm × 25 000 = 100 000 cm, soit 1 000 m = 1 km."),
    vf("Passer de 10 % à 15 %, c'est une hausse de 5 points, mais une hausse relative de 50 %.", True, "La différence est de 5 points. Rapportée à 10, elle représente +50 %."),
    num("Une voiture roule à 90 km/h. Quelle distance parcourt-elle en 20 minutes ?", 30, "20 minutes, c'est un tiers d'heure : 90 ÷ 3 = 30 km.", unite="km"),
    qcm("Un taux d'intérêt passe de 2 % à 3 %. Quelle est sa hausse relative ?", ["+50 %", "+1 %", "+33 %", "+150 %"], "La hausse est d'un point, soit la moitié du taux de départ : +50 %."),
    num("Un produit coûte 120 € TTC avec 20 % de TVA. Quel est son prix hors taxe ?", 100, "Prix TTC = HT × 1,2, donc HT = 120 ÷ 1,2 = 100 €. Retirer 20 % de 120 € donnerait 96 €, ce qui est faux.", unite="€"),
    vf("Si x est proportionnel à y, doubler y double x.", True, "Proportionnel signifie x = k × y : si y double, x double aussi."),
    qcm("Une recette pour 4 personnes demande 300 g de farine. Combien en faut-il pour 6 personnes ?", ["450 g", "400 g", "500 g", "600 g"], "300 g ÷ 4 = 75 g par personne, × 6 = 450 g."),
]

Q["math.probabilites"] = [
    qcm("Quelle est la probabilité d'obtenir un 6 avec un dé équilibré ?", ["1/6", "1/3", "1/2", "1/5"], "Six faces équiprobables, une seule favorable."),
    vf("Après cinq « pile » de suite, « face » devient plus probable au lancer suivant.", False, "Les lancers sont indépendants : c'est toujours 1/2. Croire le contraire s'appelle l'erreur du joueur."),
    qcm("Quelle est la probabilité d'obtenir au moins un pile en deux lancers ?", ["3/4", "1/2", "1/4", "2/3"], "Seul « face, face » échoue, avec une probabilité de 1/4. Il reste 1 − 1/4 = 3/4."),
    qcm("Avec deux dés, quelle est la probabilité que la somme fasse 7 ?", ["1/6", "1/12", "7/36", "1/11"], "6 combinaisons sur 36 donnent 7 : (1,6), (2,5), (3,4), (4,3), (5,2), (6,1)."),
    qcm("Jeu de Monty Hall : l'animateur ouvre une porte perdante. Si vous changez de porte, votre chance de gagner est de :", ["2/3", "1/2", "1/3", "1"], "Votre premier choix a 1/3 de chances. Les 2/3 restants se reportent sur l'autre porte fermée."),
    vf("Pour deux événements indépendants, P(A et B) = P(A) × P(B).", True, "C'est la définition même de l'indépendance."),
    num("Combien de résultats différents peut-on obtenir en lançant 3 pièces ?", 8, "Chaque pièce a 2 issues : 2 × 2 × 2 = 8."),
    qcm("Dans un groupe de 23 personnes, la probabilité que deux aient le même anniversaire est d'environ :", ["50 %", "6 %", "23 %", "90 %"], "C'est le paradoxe des anniversaires : avec 23 personnes, il y a 253 paires possibles, et la probabilité dépasse 50 %."),
    qcm("Une urne contient 3 boules rouges et 7 bleues. Quelle est la probabilité de tirer une rouge ?", ["0,3", "0,7", "0,43", "0,5"], "3 boules favorables sur 10."),
    vf("Un événement de probabilité 0,01 % n'arrive jamais.", False, "Il est rare, pas impossible : sur un million d'essais, il arrive environ 100 fois."),
    num("On gagne 10 € avec une probabilité de 1/5, rien sinon. Quelle est l'espérance de gain ?", 2, "Espérance = 10 € × 1/5 = 2 €.", unite="€"),
    qcm("Un test détecte une maladie rare (1 personne sur 1 000). Il est fiable à 99 % dans les deux sens. Si votre test est positif, la probabilité d'être malade est d'environ :", ["9 %", "99 %", "50 %", "1 %"], "Sur 100 000 personnes : 99 malades testés positifs, mais aussi environ 999 faux positifs. 99 / 1 098 ≈ 9 %."),
]

Q["math.logique"] = [
    vf("« S'il pleut, le sol est mouillé. Le sol est mouillé. » On peut en conclure qu'il a plu.", False, "C'est l'affirmation du conséquent : le sol peut être mouillé pour une autre raison (arrosage)."),
    qcm("Quelle est la contraposée de « Si A alors B » ?", ["Si non B alors non A", "Si B alors A", "Si non A alors non B", "A et non B"], "La contraposée est équivalente à l'implication de départ. « Si B alors A » est la réciproque, qui ne l'est pas."),
    qcm("Quelle est la négation de « Tous les chats sont gris » ?", ["Au moins un chat n'est pas gris", "Aucun chat n'est gris", "Certains chats sont gris", "Tous les chats sont noirs"], "Pour contredire « tous », un seul contre-exemple suffit."),
    vf("En logique, « A ou B » est vrai quand A et B sont vrais tous les deux.", True, "Le « ou » logique est inclusif. Le « ou » exclusif (l'un ou l'autre, pas les deux) est un autre opérateur."),
    qcm("Tous les A sont B. Tous les B sont C. Donc :", ["Tous les A sont C", "Tous les C sont A", "Certains C ne sont pas A", "On ne peut rien conclure"], "C'est un syllogisme valide : l'inclusion se transmet."),
    qcm("Si « non (A et B) » est vrai, alors :", ["non A ou non B", "non A et non B", "A ou B", "A et non B"], "C'est une loi de De Morgan : la négation d'un « et » est le « ou » des négations."),
    vf("« Si A alors B » est vrai dès que A est faux, quelle que soit la valeur de B.", True, "Une implication n'est fausse que dans un cas : A vrai et B faux."),
    qcm("« Aucun poisson ne vole. Certains animaux volent. » Que peut-on conclure ?", ["Certains animaux ne sont pas des poissons", "Aucun animal n'est un poisson", "Certains poissons sont des animaux", "Rien du tout"], "Les animaux qui volent ne peuvent pas être des poissons."),
    num("Combien de lignes compte la table de vérité d'une formule à 3 variables ?", 8, "Chaque variable vaut vrai ou faux : 2³ = 8 combinaisons."),
    qcm("Dans un raisonnement par l'absurde, on suppose :", ["le contraire de ce qu'on veut prouver, et on aboutit à une contradiction", "ce qu'on veut prouver", "un cas particulier", "que tout est faux"], "Si l'hypothèse contraire mène à une contradiction, c'est qu'elle est fausse."),
    vf("Un seul contre-exemple suffit à réfuter une affirmation universelle.", True, "« Tous les cygnes sont blancs » tombe dès qu'on observe un cygne noir."),
    qcm("Épiménide le Crétois dit : « Tous les Crétois sont menteurs » (un menteur ne dit que des faussetés). Que peut-on en déduire ?", ["Sa phrase est fausse", "Sa phrase est vraie", "Elle est vraie et fausse à la fois", "Tous les Crétois disent la vérité"], "Si elle était vraie, Épiménide mentirait en la disant : contradiction. Elle est donc fausse, et au moins un Crétois dit parfois vrai."),
]

Q["phys.unites"] = [
    qcm("Quelle est l'unité de force dans le Système international ?", ["le newton", "le joule", "le watt", "le pascal"], "Le joule mesure l'énergie, le watt la puissance, le pascal la pression."),
    num("Combien y a-t-il de secondes dans une heure ?", 3600, "60 minutes × 60 secondes = 3 600 s.", unite="s"),
    qcm("La vitesse de la lumière dans le vide vaut environ :", ["300 000 km/s", "300 000 km/h", "30 000 km/s", "3 000 km/s"], "Précisément 299 792 458 m/s, une valeur fixée par définition du mètre."),
    vf("1 litre est égal à 1 dm³.", True, "Un cube de 10 cm de côté contient exactement un litre."),
    qcm("Le préfixe « micro » (µ) signifie :", ["10⁻⁶", "10⁻³", "10⁻⁹", "10⁶"], "Milli = 10⁻³, micro = 10⁻⁶, nano = 10⁻⁹."),
    num("Combien de cm³ dans 1 m³ ?", 1000000, "100 × 100 × 100 = 1 000 000 cm³.", unite="cm³"),
    qcm("En 1999, la sonde Mars Climate Orbiter a été perdue à cause :", ["d'une confusion entre unités anglo-saxonnes et métriques", "d'une météorite", "d'une panne de batterie", "d'un virus informatique"], "Un logiciel produisait des valeurs en livres-force·seconde, un autre les lisait en newtons·seconde."),
    qcm("La distance Terre–Soleil vaut environ :", ["150 millions de km", "15 millions de km", "1,5 milliard de km", "384 000 km"], "384 000 km, c'est la distance Terre–Lune. 150 millions de km définissent l'unité astronomique."),
    vf("Le kilowattheure (kWh) est une unité de puissance.", False, "C'est une unité d'énergie : une puissance (kW) multipliée par une durée (h)."),
    num("Combien vaut 72 km/h en m/s ?", 20, "72 000 m ÷ 3 600 s = 20 m/s. Astuce : diviser par 3,6.", unite="m/s"),
    qcm("L'ordre de grandeur de la taille d'un atome est :", ["10⁻¹⁰ m", "10⁻⁶ m", "10⁻¹⁵ m", "10⁻³ m"], "Environ un dixième de nanomètre. 10⁻¹⁵ m, c'est la taille d'un noyau."),
    qcm("Quelle est l'unité SI de la température ?", ["le kelvin", "le degré Celsius", "le degré Fahrenheit", "la calorie"], "Le kelvin part du zéro absolu. 0 °C = 273,15 K."),
]

Q["phys.forces"] = [
    qcm("Selon le principe d'inertie, un objet soumis à une force nette nulle :", ["reste immobile ou garde une vitesse constante en ligne droite", "finit toujours par s'arrêter", "accélère", "tombe"], "C'est la première loi de Newton. Sur Terre, les objets s'arrêtent à cause des frottements."),
    vf("Dans le vide, une plume et un marteau lâchés ensemble tombent à la même vitesse.", True, "David Scott l'a montré sur la Lune en 1971, pendant la mission Apollo 15."),
    num("F = m × a. Quelle force faut-il pour accélérer 10 kg à 2 m/s² ?", 20, "10 kg × 2 m/s² = 20 N.", unite="N"),
    qcm("Le poids d'un objet de 1 kg à la surface de la Terre vaut environ :", ["9,8 N", "1 N", "1 kg", "98 N"], "Poids = masse × g, avec g ≈ 9,8 m/s²."),
    vf("Sur la Lune, la masse d'un astronaute est six fois plus faible que sur Terre.", False, "Sa masse ne change pas. C'est son poids qui est environ six fois plus faible."),
    qcm("Que dit la troisième loi de Newton ?", ["À toute action correspond une réaction égale et opposée", "F = m × a", "Un corps garde sa vitesse sans force", "Les corps s'attirent selon leur masse"], "Quand vous poussez un mur, il vous pousse avec la même force."),
    num("Un objet parcourt 100 m en 20 s à vitesse constante. Quelle est sa vitesse ?", 5, "100 m ÷ 20 s = 5 m/s.", unite="m/s"),
    qcm("Qu'est-ce qui maintient la Lune en orbite autour de la Terre ?", ["la gravitation", "le magnétisme", "l'inertie seule", "le vent solaire"], "La gravitation courbe sa trajectoire. Sans elle, l'inertie l'enverrait en ligne droite."),
    vf("La force de gravitation entre deux corps diminue avec le carré de leur distance.", True, "Deux fois plus loin, la force est quatre fois plus faible."),
    qcm("Un objet lâché sans vitesse initiale, sans frottement. Après 1 seconde, sa vitesse est d'environ :", ["9,8 m/s", "4,9 m/s", "1 m/s", "98 m/s"], "v = g × t = 9,8 × 1. Il a alors parcouru 4,9 m, d'où le piège."),
    qcm("Pourquoi une patineuse tourne-t-elle plus vite en ramenant les bras ?", ["Conservation du moment cinétique", "Elle pousse sur la glace", "La gravité augmente", "Moins de frottement de l'air"], "En rapprochant sa masse de l'axe, elle doit tourner plus vite pour garder le même moment cinétique."),
    num("Une vitesse passe de 0 à 30 m/s en 10 s. Quelle est l'accélération moyenne ?", 3, "30 m/s ÷ 10 s = 3 m/s².", unite="m/s²"),
]

Q["phys.energie"] = [
    qcm("Quelle formule donne l'énergie cinétique ?", ["½ m v²", "m g h", "m v", "m a"], "m g h est l'énergie potentielle de pesanteur, m v la quantité de mouvement."),
    vf("L'énergie totale d'un système isolé se conserve.", True, "Elle change de forme, mais ne disparaît pas et n'apparaît pas."),
    num("Quelle est l'énergie cinétique d'une masse de 2 kg à 3 m/s ?", 9, "½ × 2 × 3² = 9 J.", unite="J"),
    qcm("La puissance est égale à :", ["l'énergie divisée par le temps", "la force multipliée par le temps", "la masse multipliée par la vitesse", "l'énergie multipliée par le temps"], "1 watt = 1 joule par seconde."),
    num("Une ampoule de 10 W allumée pendant 100 heures consomme combien de kWh ?", 1, "10 W × 100 h = 1 000 Wh = 1 kWh.", unite="kWh"),
    qcm("Un barrage hydroélectrique convertit surtout :", ["l'énergie potentielle de l'eau en électricité", "la chaleur en électricité", "l'énergie chimique en électricité", "l'énergie nucléaire en électricité"], "L'eau qui descend fait tourner des turbines reliées à des alternateurs."),
    vf("Une machine peut avoir un rendement supérieur à 100 %.", False, "Ce serait créer de l'énergie, ce que la conservation interdit. Le mouvement perpétuel n'existe pas."),
    qcm("Combien de joules dans 1 kWh ?", ["3,6 millions", "1 000", "3 600", "60 000"], "1 000 W × 3 600 s = 3 600 000 J."),
    qcm("Quelle formule donne l'énergie potentielle de pesanteur ?", ["m g h", "½ m v²", "m c²", "F × t"], "Masse × gravité × hauteur."),
    num("On monte une masse de 1 kg de 10 m (g = 10 m/s²). Quelle énergie potentielle gagne-t-elle ?", 100, "1 × 10 × 10 = 100 J.", unite="J"),
    vf("La « calorie » des étiquettes alimentaires est une unité d'énergie.", True, "La kilocalorie vaut environ 4 184 joules."),
    qcm("Que signifie E = mc² ?", ["La masse et l'énergie sont équivalentes", "L'énergie cinétique dépend du carré de la vitesse", "La quantité de mouvement se conserve", "La tension est proportionnelle au courant"], "Einstein, 1905 : une petite masse correspond à une énorme énergie, car c² est très grand."),
]

Q["phys.ondes"] = [
    vf("Le son se propage dans le vide.", False, "Le son est une vibration de la matière. Dans l'espace, aucune explosion ne s'entend."),
    qcm("La vitesse du son dans l'air vaut environ :", ["340 m/s", "3 400 m/s", "34 m/s", "300 000 km/s"], "Environ 340 m/s à 15 °C. Dans l'eau, c'est près de 1 500 m/s."),
    num("Un éclair, puis le tonnerre 3 secondes plus tard. À quelle distance est l'orage ? (son : 340 m/s)", 1020, "La lumière arrive presque instantanément. 3 s × 340 m/s = 1 020 m, environ 1 km.", tol=30, unite="m"),
    qcm("Quelle couleur visible a la plus grande longueur d'onde ?", ["le rouge", "le violet", "le vert", "le bleu"], "Environ 700 nm pour le rouge, 400 nm pour le violet."),
    qcm("Pourquoi le ciel est-il bleu ?", ["L'air diffuse davantage les courtes longueurs d'onde (diffusion de Rayleigh)", "Il reflète les océans", "L'ozone est bleu", "La vapeur d'eau absorbe le rouge"], "Le bleu est diffusé dans toutes les directions bien plus que le rouge."),
    vf("Les rayons X et la lumière visible sont tous deux des ondes électromagnétiques.", True, "Ils ne diffèrent que par leur longueur d'onde, comme les ondes radio et les micro-ondes."),
    qcm("La fréquence d'une onde est égale à :", ["sa vitesse divisée par sa longueur d'onde", "sa longueur d'onde divisée par sa vitesse", "sa vitesse multipliée par sa longueur d'onde", "l'inverse de sa vitesse"], "f = v / λ."),
    qcm("L'effet Doppler explique :", ["le changement de son d'une sirène qui passe", "l'arc-en-ciel", "l'écho", "les marées"], "La source qui approche comprime les ondes (son plus aigu), celle qui s'éloigne les étire."),
    num("Une onde a une période de 0,01 s. Quelle est sa fréquence ?", 100, "f = 1 / T = 1 / 0,01 = 100 Hz.", unite="Hz"),
    qcm("Un arc-en-ciel est dû :", ["à la réfraction et la réflexion de la lumière dans les gouttes d'eau", "à la diffraction par les nuages", "à la pollution", "à l'ozone"], "Chaque couleur est déviée d'un angle légèrement différent."),
    vf("La lumière du Soleil met environ 8 minutes à nous parvenir.", True, "Environ 8 min 20 s pour 150 millions de km."),
    qcm("L'oreille humaine perçoit environ les fréquences de :", ["20 Hz à 20 kHz", "2 Hz à 2 kHz", "200 Hz à 200 kHz", "20 kHz à 200 kHz"], "Au-delà de 20 kHz, ce sont les ultrasons, que les chauves-souris utilisent."),
]

Q["sci.methode"] = [
    qcm("Une hypothèse scientifique doit avant tout être :", ["réfutable par l'expérience", "prouvée d'avance", "approuvée par un expert", "intuitive"], "Une hypothèse qu'aucune observation ne pourrait contredire n'est pas scientifique."),
    vf("Une corrélation prouve une relation de cause à effet.", False, "Les ventes de glaces et les noyades augmentent ensemble : la cause commune est l'été."),
    qcm("Dans un essai clinique, le groupe témoin sert à :", ["comparer avec des personnes qui ne reçoivent pas le traitement", "tester une dose plus forte", "remplacer les malades", "accélérer l'étude"], "Sans comparaison, impossible de savoir si l'amélioration vient du traitement."),
    qcm("Un essai « en double aveugle » signifie que :", ["ni les patients ni les médecins ne savent qui reçoit le traitement", "deux groupes de patients sont aveugles", "l'expérience est répétée deux fois", "les résultats sont cachés au public"], "Cela empêche les attentes de chacun d'influencer les résultats."),
    vf("En science, une théorie est une simple supposition sans preuves.", False, "Une théorie scientifique est un cadre explicatif solide, testé et confirmé de nombreuses fois, comme la théorie de l'évolution."),
    qcm("Quel philosophe a fait de la réfutabilité le critère de la science ?", ["Karl Popper", "René Descartes", "Auguste Comte", "Thomas Kuhn"], "Popper l'expose dans « La Logique de la découverte scientifique » (1934)."),
    qcm("L'effet placebo désigne :", ["une amélioration due au fait de croire recevoir un traitement", "un effet secondaire grave", "un médicament générique", "une erreur de mesure"], "C'est pourquoi on compare un traitement à un placebo, pas à rien."),
    vf("Qu'un résultat soit retrouvé par d'autres équipes le renforce.", True, "C'est la reproductibilité, un pilier de la méthode scientifique."),
    qcm("Un échantillon trop petit expose surtout à :", ["des résultats dus au hasard", "des résultats toujours faux", "aucun problème", "des résultats trop précis"], "Plus l'échantillon est petit, plus le hasard pèse sur le résultat."),
    qcm("Le rasoir d'Ockham recommande :", ["de préférer l'explication la plus simple qui suffit", "de rejeter toute hypothèse", "de multiplier les causes", "de croire les autorités"], "« Les entités ne doivent pas être multipliées sans nécessité. »"),
    vf("Une publication dans une revue scientifique relue par des pairs garantit qu'un résultat est vrai.", False, "La relecture filtre beaucoup d'erreurs, mais des articles publiés sont ensuite corrigés ou rétractés."),
    qcm("Qui a montré en 1847 que le lavage des mains des médecins réduisait la fièvre des accouchées ?", ["Ignace Semmelweis", "Louis Pasteur", "Robert Koch", "Claude Bernard"], "Ses collègues l'ont rejeté. Il a fallu attendre Pasteur pour comprendre pourquoi il avait raison."),
]

Q["sci.atomes"] = [
    qcm("Le noyau d'un atome contient :", ["des protons et des neutrons", "des électrons et des protons", "seulement des électrons", "des molécules"], "Les électrons se trouvent autour du noyau."),
    qcm("Quelle est la formule de l'eau ?", ["H₂O", "HO₂", "H₂O₂", "OH"], "Deux atomes d'hydrogène, un d'oxygène. H₂O₂ est l'eau oxygénée."),
    num("Quel est le numéro atomique du carbone ?", 6, "Le carbone a 6 protons."),
    vf("Un atome est surtout fait de vide.", True, "Si le noyau avait la taille d'une bille, l'atome aurait celle d'un stade."),
    qcm("Quel est l'élément le plus abondant dans l'Univers ?", ["l'hydrogène", "l'hélium", "l'oxygène", "le carbone"], "Environ trois quarts de la matière ordinaire, en masse."),
    qcm("Quel est le symbole chimique du fer ?", ["Fe", "F", "Fr", "Ir"], "Du latin ferrum. F est le fluor, Fr le francium, Ir l'iridium."),
    vf("Le diamant et le graphite sont tous deux faits de carbone.", True, "Seul l'arrangement des atomes diffère."),
    qcm("Qui a publié un tableau périodique des éléments en 1869 ?", ["Dmitri Mendeleïev", "Antoine Lavoisier", "Marie Curie", "John Dalton"], "Il y laissait des cases vides pour des éléments encore inconnus, découverts ensuite."),
    qcm("Quel gaz est le plus abondant dans l'air ?", ["l'azote", "l'oxygène", "le dioxyde de carbone", "l'argon"], "Environ 78 % d'azote, 21 % d'oxygène."),
    num("Combien d'atomes compte une molécule de CO₂ ?", 3, "Un atome de carbone et deux d'oxygène."),
    vf("Lors d'une réaction chimique, la masse totale se conserve.", True, "C'est la loi de Lavoisier : les atomes se réarrangent sans disparaître."),
    qcm("Un ion est :", ["un atome qui a gagné ou perdu des électrons", "un atome sans noyau", "une molécule d'eau", "un neutron libre"], "Il porte alors une charge électrique, comme Na⁺ ou Cl⁻ dans le sel."),
]

Q["sci.cellule"] = [
    qcm("Quel organite produit l'essentiel de l'énergie (ATP) de la cellule ?", ["la mitochondrie", "le noyau", "le ribosome", "l'appareil de Golgi"], "On la surnomme la centrale énergétique de la cellule."),
    vf("Les bactéries ont un noyau.", False, "Ce sont des procaryotes : leur ADN flotte dans le cytoplasme."),
    qcm("Où a lieu la photosynthèse ?", ["dans les chloroplastes", "dans les mitochondries", "dans le noyau", "dans les lysosomes"], "Les chloroplastes contiennent la chlorophylle."),
    qcm("Dans une cellule animale, l'ADN se trouve principalement :", ["dans le noyau", "dans la membrane", "dans les ribosomes", "dans les lysosomes"], "Une petite partie se trouve aussi dans les mitochondries."),
    qcm("Les ribosomes fabriquent :", ["des protéines", "des lipides", "de l'ADN", "du glucose"], "Ils lisent l'ARN messager et assemblent les acides aminés."),
    vf("Les cellules d'un même individu portent, à peu près, le même ADN.", True, "Une cellule de peau et un neurone ont le même génome ; ils n'en utilisent pas les mêmes gènes."),
    num("Combien de chromosomes compte une cellule humaine non sexuelle ?", 46, "23 paires, dont une paire de chromosomes sexuels."),
    qcm("Qui a observé et nommé les « cellules » en 1665 ?", ["Robert Hooke", "Antoni van Leeuwenhoek", "Louis Pasteur", "Gregor Mendel"], "En observant du liège au microscope, il y a vu de petites chambres, des « cells »."),
    qcm("Quelle division cellulaire produit les gamètes ?", ["la méiose", "la mitose", "l'osmose", "la fécondation"], "La méiose divise par deux le nombre de chromosomes."),
    vf("Les virus sont des cellules.", False, "Ils n'ont ni métabolisme ni ribosomes et doivent infecter une cellule pour se reproduire."),
    qcm("Quelles sont les quatre bases de l'ADN ?", ["A, T, G, C", "A, U, G, C", "A, B, C, D", "H, O, N, C"], "Adénine, thymine, guanine, cytosine. L'ARN remplace T par U (uracile)."),
    qcm("Qu'ont les cellules végétales que n'ont pas les cellules animales ?", ["une paroi en cellulose", "une membrane", "un noyau", "des mitochondries"], "Elles ont aussi des chloroplastes et une grande vacuole."),
]

Q["sci.evolution"] = [
    qcm("Qui a publié « L'Origine des espèces » en 1859 ?", ["Charles Darwin", "Jean-Baptiste Lamarck", "Gregor Mendel", "Alfred Wegener"], "Le livre expose la théorie de l'évolution par sélection naturelle."),
    vf("Selon la théorie de l'évolution, l'humain descend du chimpanzé actuel.", False, "Humains et chimpanzés partagent un ancêtre commun, qui vivait il y a environ 6 à 7 millions d'années."),
    qcm("La sélection naturelle favorise :", ["les individus qui laissent le plus de descendants dans leur milieu", "les plus forts physiquement", "les plus gros", "ceux qui le veulent"], "La « survie du plus apte » désigne le succès reproductif, pas la force."),
    qcm("Quel est l'âge de la Terre ?", ["environ 4,5 milliards d'années", "environ 6 000 ans", "environ 450 millions d'années", "environ 13,8 milliards d'années"], "13,8 milliards d'années, c'est l'âge de l'Univers."),
    qcm("D'où vient la variation génétique sur laquelle agit la sélection ?", ["des mutations et du brassage des gènes", "de la volonté de l'organisme", "de l'usage des organes", "du climat directement"], "Les caractères acquis par l'usage ne se transmettent pas : c'était l'idée de Lamarck."),
    vf("Les oiseaux descendent de dinosaures.", True, "Ce sont des dinosaures théropodes, proches parents des vélociraptors."),
    qcm("La résistance des bactéries aux antibiotiques est un exemple :", ["de sélection naturelle", "de génération spontanée", "d'hérédité des caractères acquis", "de mutation volontaire"], "Les rares bactéries résistantes survivent au traitement et se multiplient."),
    qcm("Qui a eu l'idée de la sélection naturelle en même temps que Darwin ?", ["Alfred Russel Wallace", "Thomas Huxley", "Charles Lyell", "Jean-Baptiste Lamarck"], "Leurs textes ont été présentés ensemble à la Société linnéenne de Londres en 1858."),
    qcm("Les fossiles permettent surtout :", ["de retracer l'histoire des espèces disparues", "de mesurer la température", "de prédire les séismes", "de dater les étoiles"], "Ils montrent aussi des formes de transition, comme Tiktaalik entre poissons et tétrapodes."),
    vf("L'évolution poursuit un but : produire des êtres de plus en plus complexes.", False, "L'évolution n'a pas de direction. Des parasites ont même perdu des organes au fil du temps."),
    qcm("Les pinsons de Darwin, aux Galápagos, diffèrent surtout par :", ["la forme de leur bec", "la couleur de leurs yeux", "la taille de leurs pattes", "leur chant"], "Chaque forme de bec correspond à une nourriture : graines dures, insectes, cactus."),
    qcm("Les dinosaures non aviens ont disparu il y a environ :", ["66 millions d'années", "6 millions d'années", "650 millions d'années", "10 000 ans"], "Probablement après l'impact d'un astéroïde au Yucatán (cratère de Chicxulub)."),
]

Q["rhet.argument"] = [
    qcm("Un argument se compose :", ["de prémisses et d'une conclusion", "d'une opinion seule", "d'une question", "d'un exemple seul"], "Les prémisses sont les raisons ; la conclusion est ce qu'elles soutiennent."),
    qcm("« Socrate est un homme, tous les hommes sont mortels, donc Socrate est mortel » est :", ["un syllogisme", "une métaphore", "un sophisme", "une anaphore"], "Deux prémisses, une conclusion qui en découle nécessairement."),
    vf("Un argument peut être logiquement valide et avoir une conclusion fausse.", True, "Si une prémisse est fausse : « Tous les oiseaux volent, l'autruche est un oiseau, donc l'autruche vole »."),
    qcm("Une déduction va :", ["du général au particulier", "du particulier au général", "de l'effet à sa cause probable", "de l'émotion à l'action"], "Si les prémisses sont vraies, la conclusion l'est forcément."),
    qcm("Une induction va :", ["de cas particuliers à une règle générale", "du général au particulier", "d'une prémisse à sa négation", "d'une hypothèse à une preuve absolue"], "Elle est utile mais jamais certaine : un nouveau cas peut la contredire."),
    qcm("« Il faut réduire la vitesse, car cela sauve des vies. » Quelle est la conclusion ?", ["Il faut réduire la vitesse", "Cela sauve des vies", "Le mot « car »", "Les deux propositions"], "« Car » introduit la raison, donc la prémisse."),
    vf("« Il est en retard, donc il ne m'aime plus » : la conclusion découle nécessairement de la prémisse.", False, "Un retard a bien d'autres explications possibles. Le lien n'est pas nécessaire."),
    qcm("Le plan « thèse, antithèse, synthèse » s'appelle :", ["le plan dialectique", "le plan chronologique", "le plan thématique", "le plan comparatif"], "Il confronte deux positions pour les dépasser."),
    qcm("Un syllogisme dont une prémisse reste sous-entendue s'appelle :", ["un enthymème", "un oxymore", "une hyperbole", "un chiasme"], "« Il a de la fièvre, donc il est malade » sous-entend « la fièvre est un signe de maladie »."),
    qcm("À qui revient la charge de la preuve ?", ["à celui qui affirme", "à celui qui doute", "au public", "à personne"], "C'est à celui qui avance une thèse de la justifier."),
    vf("Une anecdote personnelle suffit à prouver une règle générale.", False, "Un cas isolé peut illustrer, pas prouver. Il faut des données représentatives."),
    qcm("À quoi sert un contre-argument dans un discours ?", ["à anticiper les objections et y répondre", "à répéter sa thèse", "à changer de sujet", "à attaquer l'adversaire"], "Traiter l'objection avant qu'on vous l'oppose renforce votre crédibilité."),
]

Q["rhet.figures"] = [
    qcm("« Cette obscure clarté qui tombe des étoiles » (Corneille, Le Cid) est :", ["un oxymore", "une litote", "une anaphore", "une hyperbole"], "Deux termes contradictoires réunis : obscure et clarté."),
    qcm("« Va, je ne te hais point » (Corneille, Le Cid) est :", ["une litote", "une hyperbole", "une métaphore", "un pléonasme"], "Dire moins pour suggérer plus : Chimène avoue son amour."),
    qcm("« Je meurs de faim » est :", ["une hyperbole", "une litote", "un euphémisme", "un chiasme"], "Une exagération volontaire."),
    qcm("Dire « il nous a quittés » pour « il est mort » est :", ["un euphémisme", "une hyperbole", "une antithèse", "une allitération"], "On adoucit une réalité pénible."),
    qcm("« Il faut manger pour vivre et non pas vivre pour manger » (Molière, L'Avare) est :", ["un chiasme", "une métonymie", "une litote", "un oxymore"], "Les termes sont repris en ordre inverse : A-B, B-A."),
    qcm("« Boire un verre » (on boit le contenu, pas le verre) est :", ["une métonymie", "une métaphore", "une hyperbole", "une anaphore"], "On désigne une chose par une autre qui lui est liée, ici le contenant pour le contenu."),
    vf("La comparaison utilise un outil comme « comme » ou « tel », contrairement à la métaphore.", True, "« Il est fort comme un lion » est une comparaison ; « c'est un lion » est une métaphore."),
    qcm("« Pour qui sont ces serpents qui sifflent sur vos têtes ? » (Racine, Andromaque) illustre :", ["une allitération", "une litote", "un euphémisme", "une prétérition"], "La répétition du son « s » imite le sifflement des serpents."),
    qcm("« Paris outragé ! Paris brisé ! Paris martyrisé ! » (de Gaulle, 1944) est :", ["une anaphore", "une épiphore", "une ellipse", "une antiphrase"], "Le même mot est répété en tête de chaque segment."),
    qcm("« Je ne vous parlerai pas de ses mensonges… » (pour en parler quand même) est :", ["une prétérition", "une litote", "une hyperbole", "une métonymie"], "On annonce qu'on ne dira pas ce qu'on est en train de dire."),
    qcm("« Quel temps magnifique ! » sous une pluie battante est :", ["une antiphrase", "un euphémisme", "un oxymore", "une anaphore"], "Dire le contraire de ce qu'on pense : c'est le ressort de l'ironie."),
    vf("« Monter en haut » est un pléonasme.", True, "On ne peut monter qu'en haut : la précision est redondante."),
]

Q["rhet.persuasion"] = [
    qcm("Qui a distingué l'ethos, le pathos et le logos ?", ["Aristote", "Platon", "Cicéron", "Socrate"], "Dans sa « Rhétorique », au IVe siècle avant notre ère."),
    qcm("L'ethos repose sur :", ["la crédibilité de l'orateur", "les émotions du public", "la logique des arguments", "le rythme des phrases"], "On croit plus volontiers quelqu'un qui paraît compétent, honnête et bienveillant."),
    qcm("Le pathos repose sur :", ["les émotions suscitées chez le public", "la crédibilité de l'orateur", "les chiffres", "la grammaire"], "Peur, pitié, colère, enthousiasme."),
    qcm("Le logos repose sur :", ["le raisonnement et les preuves", "la réputation", "la peur", "l'humour"], "Faits, chiffres, enchaînements logiques."),
    qcm("« Je suis médecin depuis trente ans, croyez-moi » mobilise surtout :", ["l'ethos", "le pathos", "le logos", "le kairos"], "L'orateur met en avant son autorité."),
    qcm("Une photo d'enfant en détresse dans une campagne humanitaire mobilise surtout :", ["le pathos", "l'ethos", "le logos", "l'anaphore"], "Elle vise l'émotion du public."),
    qcm("Que désigne le « kairos » ?", ["le moment opportun pour parler", "un type de syllogisme", "une figure de style", "la conclusion d'un discours"], "Le même argument n'a pas le même effet selon le moment."),
    vf("Selon Robert Cialdini, la preuve sociale est un levier d'influence.", True, "Dans « Influence » (1984) : nous jugeons un comportement plus juste quand nous voyons d'autres l'adopter."),
    qcm("« 90 % de survie » ou « 10 % de mortalité » :", ["c'est la même information, perçue différemment", "ce sont deux informations différentes", "c'est une erreur de calcul", "c'est un argument ad hominem"], "C'est l'effet de cadrage : la formulation positive rassure davantage."),
    qcm("La « captatio benevolentiae » vise à :", ["gagner la bienveillance du public au début du discours", "conclure", "réfuter l'adversaire", "menacer"], "Par exemple en remerciant l'auditoire ou en se montrant modeste."),
    vf("Un discours efficace combine souvent les trois leviers : ethos, pathos et logos.", True, "Les preuves convainquent mieux venant d'un orateur crédible qui sait toucher son public."),
    qcm("En rhétorique classique, l'« inventio » consiste à :", ["trouver les arguments", "les mémoriser", "les prononcer", "les mettre en ordre"], "Viennent ensuite dispositio (ordre), elocutio (style), memoria et actio (prononciation)."),
]

Q["rhet.sophismes"] = [
    qcm("Attaquer la personne plutôt que son argument, c'est :", ["un argument ad hominem", "un homme de paille", "une pente glissante", "un faux dilemme"], "« Tu dis ça, mais tu n'as même pas de diplôme. »"),
    qcm("Déformer la position de l'adversaire pour la réfuter plus facilement, c'est :", ["l'homme de paille", "l'ad hominem", "l'appel à l'autorité", "le tu quoque"], "On combat une caricature, pas la vraie position."),
    qcm("« Soit tu es avec nous, soit tu es contre nous » est :", ["un faux dilemme", "une pente glissante", "une généralisation hâtive", "une pétition de principe"], "On présente deux options comme les seules possibles alors qu'il en existe d'autres."),
    qcm("« Si on autorise ça, bientôt ce sera le chaos » est :", ["une pente glissante", "un ad hominem", "un appel à la nature", "l'erreur du joueur"], "On enchaîne des conséquences de plus en plus graves sans montrer qu'elles sont probables."),
    qcm("« C'est naturel, donc c'est bon » est :", ["un appel à la nature", "un appel à la nouveauté", "un homme de paille", "un faux dilemme"], "L'arsenic et la ciguë sont naturels."),
    qcm("« Tout le monde le fait, donc c'est bien » est :", ["un appel à la popularité", "un ad hominem", "un faux dilemme", "un appel à l'ignorance"], "Le nombre de partisans ne prouve pas qu'une idée est juste."),
    qcm("« Personne n'a prouvé que les fantômes n'existent pas, donc ils existent » est :", ["un appel à l'ignorance", "un appel à l'autorité", "une pente glissante", "un tu quoque"], "L'absence de preuve contraire n'est pas une preuve."),
    qcm("« Toi aussi tu fumes, donc ton conseil ne vaut rien » est :", ["un tu quoque", "un homme de paille", "un faux dilemme", "un appel à la nature"], "L'incohérence de l'orateur ne rend pas son argument faux."),
    qcm("« J'ai pris mon parapluie et il a plu, donc mon parapluie fait pleuvoir » est :", ["un post hoc ergo propter hoc", "une pétition de principe", "un appel à la popularité", "un faux dilemme"], "« Après cela, donc à cause de cela » : la succession n'est pas la causalité."),
    qcm("« Ce journal est fiable, puisqu'il l'écrit lui-même » est :", ["une pétition de principe", "un homme de paille", "un ad hominem", "une pente glissante"], "La conclusion est déjà dans la prémisse : c'est un raisonnement circulaire."),
    vf("Un argument d'autorité est toujours fallacieux.", False, "Citer un expert dans son domaine est légitime. Le sophisme, c'est l'autorité hors de sa compétence, ou présentée comme une preuve définitive."),
    qcm("Le « Gish gallop » consiste à :", ["noyer l'adversaire sous une masse d'arguments faibles", "répéter la même phrase", "attaquer la personne", "se taire"], "Réfuter chaque point prend plus de temps que de les lancer."),
]

Q["biais.confirmation"] = [
    qcm("Le biais de confirmation est la tendance à :", ["privilégier les informations qui confirment nos croyances", "douter de tout", "oublier les faits récents", "surestimer les petits risques"], "On cherche, on retient et on interprète ce qui nous donne raison."),
    qcm("Quatre cartes : E, K, 4, 7. Règle : « une voyelle d'un côté implique un nombre pair de l'autre ». Quelles cartes retourner pour vérifier la règle ?", ["E et 7", "E et 4", "E seulement", "E, 4 et 7"], "C'est la tâche de Wason (1966). Le 4 ne peut pas réfuter la règle ; le 7 le peut, s'il cache une voyelle."),
    vf("Les algorithmes de recommandation peuvent renforcer le biais de confirmation.", True, "Ils proposent ce qui ressemble à ce qu'on a déjà aimé."),
    qcm("Quel est un bon antidote au biais de confirmation ?", ["chercher activement ce qui contredirait son idée", "lire plus de sources qui nous donnent raison", "éviter les débats", "se fier à sa première impression"], "Se demander : « Qu'est-ce qui me ferait changer d'avis ? »"),
    qcm("La « persévérance des croyances » consiste à :", ["garder une croyance même quand ses preuves ont été discréditées", "changer d'avis trop vite", "croire tout ce qu'on lit", "oublier ses croyances"], "L'explication qu'on s'est construite survit à la preuve qui l'avait fait naître."),
    qcm("Ne retenir que les fois où un horoscope « tombe juste » illustre :", ["la mémoire sélective", "l'effet d'ancrage", "le biais du survivant", "l'effet de halo"], "Les prédictions ratées sont vite oubliées."),
    vf("Les personnes très intelligentes échappent au biais de confirmation.", False, "Elles sont parfois plus habiles à trouver des arguments pour ce qu'elles croient déjà."),
    qcm("L'effet Barnum (ou effet Forer) consiste à :", ["se reconnaître dans une description vague qui vaut pour tout le monde", "croire aux spectacles de cirque", "surestimer ses capacités", "préférer les gains immédiats"], "Forer (1949) a donné à ses étudiants le même « portrait personnel » : ils l'ont jugé très juste."),
    qcm("En 1979, Lord, Ross et Lepper font lire les mêmes études sur la peine de mort à des partisans et des opposants. Résultat :", ["chacun renforce sa position", "tous changent d'avis", "tous deviennent indécis", "ils tombent d'accord"], "Chacun a jugé plus convaincante l'étude qui lui donnait raison."),
    qcm("Une « chambre d'écho » désigne :", ["un milieu où l'on n'entend que des avis semblables au sien", "une salle de concert", "un biais de mémoire", "un argument circulaire"], "Les réseaux sociaux peuvent en créer sans qu'on s'en aperçoive."),
    vf("Formuler une question de façon neutre aide à limiter le biais de confirmation.", True, "« Est-ce que ça marche ? » oriente moins que « Pourquoi ça marche ? »"),
    qcm("Dans le jeu « 2-4-6 » de Wason (1960), il faut deviner une règle. Les participants testent surtout :", ["des exemples qui confirment leur hypothèse", "des exemples qui la réfutent", "des exemples au hasard", "aucun exemple"], "La règle était simplement « trois nombres croissants ». Peu de gens testaient 1-7-50."),
]

Q["biais.ancrage"] = [
    qcm("L'effet d'ancrage, c'est :", ["être influencé par un premier chiffre, même sans rapport", "oublier le premier chiffre", "préférer les nombres ronds", "sous-estimer le temps"], "Nos estimations restent tirées vers la première valeur entendue."),
    qcm("Qui a décrit l'effet d'ancrage avec une roue de loterie en 1974 ?", ["Amos Tversky et Daniel Kahneman", "Stanley Milgram", "Solomon Asch", "Leon Festinger"], "Dans l'article « Judgment under Uncertainty: Heuristics and Biases »."),
    vf("Un prix barré à 200 € à côté d'un prix de 120 € utilise l'effet d'ancrage.", True, "Le premier prix sert de référence et fait paraître le second avantageux."),
    qcm("En négociation, faire la première offre :", ["peut ancrer la discussion à son avantage", "est toujours une erreur", "n'a aucun effet", "fait forcément perdre"], "La première offre sert de point de référence au reste de la discussion."),
    vf("Être prévenu de l'existence de l'ancrage suffit à l'annuler.", False, "L'effet diminue un peu, mais persiste même chez des gens avertis."),
    qcm("Une roue truquée tombe sur 10 ou sur 65. On demande ensuite la part des pays africains à l'ONU. Résultat :", ["des estimations plus élevées après 65", "aucune différence", "des estimations plus élevées après 10", "des refus de répondre"], "Estimations médianes : 25 % après 10, 45 % après 65."),
    qcm("Un plat très cher en haut d'une carte de restaurant sert souvent :", ["à faire paraître les autres plats raisonnables", "à être commandé souvent", "à décorer la carte", "à respecter la loi"], "Il ancre la perception des prix."),
    qcm("Comment réduire l'ancrage quand on estime un chiffre ?", ["faire sa propre estimation avant de voir celles des autres", "demander l'avis du premier venu", "faire la moyenne avec l'ancre", "s'en tenir à l'ancre"], "Une fois l'ancre entendue, il est difficile de s'en détacher."),
    vf("Même des experts, comme des juges, sont sensibles à l'ancrage.", True, "Des études ont montré des peines influencées par un chiffre tiré aux dés (Englich et al., 2006)."),
    qcm("L'effet de leurre consiste à :", ["ajouter une troisième option moins bonne pour rendre une autre plus attractive", "afficher un faux prix", "mentir dans une publicité", "tirer une ancre au hasard"], "Le moyen format de pop-corn à 6,50 € fait paraître le grand à 7 € très avantageux."),
    qcm("En 5 secondes, on estime 8×7×6×5×4×3×2×1 plus grand que 1×2×3×4×5×6×7×8. Pourquoi ?", ["les premiers chiffres servent d'ancre", "le premier produit est plus grand", "par hasard", "par fatigue"], "Kahneman et Tversky (1974) : médianes de 2 250 contre 512. La vraie valeur est 40 320."),
    num("Combien vaut 8 × 7 × 6 × 5 × 4 × 3 × 2 × 1 ?", 40320, "C'est 8 factorielle (8!). Les estimations rapides en sont très loin."),
]

Q["biais.disponibilite"] = [
    qcm("L'heuristique de disponibilité consiste à juger une probabilité selon :", ["la facilité avec laquelle des exemples viennent en tête", "des statistiques précises", "l'avis d'un expert", "le hasard"], "Ce qui est marquant ou récent paraît plus fréquent."),
    vf("Après un accident d'avion très médiatisé, beaucoup de gens surestiment le risque de prendre l'avion.", True, "L'avion reste bien plus sûr par kilomètre que la voiture."),
    qcm("En France, quelle est la cause de décès la plus fréquente parmi celles-ci ?", ["les cancers", "les attaques de requins", "les accidents d'avion", "les attentats"], "Les cancers et les maladies cardiovasculaires sont les deux premières causes de décès."),
    qcm("En anglais, y a-t-il plus de mots commençant par « k » ou ayant « k » en troisième lettre ?", ["en troisième lettre", "commençant par « k »", "autant", "aucun des deux"], "Les mots commençant par « k » viennent plus facilement en tête, donc on les croit plus nombreux (Tversky et Kahneman, 1973)."),
    vf("La couverture médiatique d'un risque reflète fidèlement sa fréquence réelle.", False, "Les médias parlent de ce qui est rare et spectaculaire, justement parce que c'est rare."),
    qcm("Le biais du survivant consiste à :", ["ne regarder que les cas qui ont passé une sélection", "survivre à un danger", "se croire immortel", "se souvenir des disparus"], "On ne voit que les entreprises qui ont réussi, pas celles qui ont fait faillite avec la même méthode."),
    qcm("Pendant la Seconde Guerre mondiale, Abraham Wald étudie les impacts sur les avions revenus de mission. Où faut-il renforcer le blindage ?", ["là où les avions revenus n'avaient pas d'impacts", "là où il y avait le plus d'impacts", "partout", "nulle part"], "Les avions touchés à ces endroits-là ne sont jamais revenus."),
    qcm("« Mon grand-père a fumé toute sa vie et a vécu jusqu'à 95 ans » illustre :", ["la confiance excessive dans un exemple marquant", "une preuve statistique", "un syllogisme valide", "l'effet placebo"], "Un cas frappant ne dit rien du risque moyen."),
    vf("Un exemple récent et frappant pèse souvent plus dans notre jugement qu'une statistique.", True, "C'est le cœur de l'heuristique de disponibilité."),
    qcm("Quel est le meilleur réflexe pour corriger ce biais ?", ["chercher les chiffres de fréquence réelle", "se fier à son expérience", "demander à un ami", "lire les gros titres"], "Les statistiques de base remettent les exemples marquants à leur place."),
    qcm("La « négligence du taux de base » consiste à :", ["ignorer la fréquence générale d'un événement", "ignorer les détails", "trop calculer", "oublier les noms"], "Comme dans le cas du test positif pour une maladie rare."),
    qcm("Kahneman appelle « WYSIATI » l'idée que :", ["ce qu'on voit est tout ce qui existe", "on voit mieux le soir", "tout est relatif", "on oublie vite"], "« What You See Is All There Is » : on juge avec ce qu'on a sous les yeux, sans penser à ce qui manque."),
]

Q["biais.surconfiance"] = [
    qcm("L'effet Dunning-Kruger décrit le fait que :", ["les moins compétents tendent à surestimer leur niveau", "les experts sont toujours modestes", "tout le monde se sous-estime", "l'intelligence est innée"], "Les compétences qui manquent sont souvent celles qui permettraient de voir ses erreurs."),
    qcm("En quelle année Dunning et Kruger ont-ils publié leur article ?", ["1999", "1979", "2009", "1959"], "« Unskilled and Unaware of It », Journal of Personality and Social Psychology, 1999."),
    vf("L'article de Dunning et Kruger évoque un braqueur persuadé que du jus de citron le rendrait invisible aux caméras.", True, "McArthur Wheeler, arrêté à Pittsburgh en 1995. L'histoire a inspiré l'étude."),
    qcm("La métacognition, c'est :", ["la connaissance de ses propres processus de pensée", "la mémoire à long terme", "une maladie", "la vitesse de lecture"], "Savoir ce qu'on sait, et repérer ce qu'on ne sait pas."),
    qcm("Quel exemple montre une surconfiance ?", ["être sûr à 90 % mais avoir raison 60 % du temps", "avoir raison", "douter", "hésiter"], "Une confiance bien calibrée correspond au taux de réussite réel."),
    vf("La plupart des conducteurs s'estiment meilleurs que la moyenne.", True, "Svenson (1981) : 93 % des Américains interrogés se plaçaient dans la moitié la plus habile."),
    qcm("L'erreur de planification consiste à :", ["sous-estimer le temps nécessaire à une tâche", "surestimer le temps nécessaire", "bien estimer les délais", "refuser de planifier"], "Même quand on sait que les projets passés ont pris du retard."),
    qcm("Le syndrome de l'imposteur, c'est :", ["douter de ses compétences malgré ses réussites", "surestimer ses compétences", "mentir sur son CV", "imiter les autres"], "On attribue ses succès à la chance plutôt qu'à son travail."),
    qcm("Se tester plutôt que relire améliore la mémorisation. On l'appelle :", ["l'effet de test", "l'effet placebo", "l'effet de halo", "l'effet Zeigarnik"], "Aller chercher l'information dans sa mémoire la renforce : c'est le principe de ce jeu."),
    vf("Plus on apprend dans un domaine, plus on mesure l'étendue de ce qu'on ignore.", True, "C'est l'envers de l'effet Dunning-Kruger."),
    qcm("Le biais d'angle mort consiste à :", ["voir les biais des autres mais pas les siens", "ne pas voir en conduisant", "oublier un détail", "ignorer les statistiques"], "Décrit par Emily Pronin et ses collègues en 2002."),
    qcm("Comment mieux calibrer sa confiance ?", ["noter sa certitude avant chaque réponse et la comparer aux résultats", "répondre plus vite", "ne jamais répondre", "demander aux autres"], "C'est l'entraînement utilisé par les prévisionnistes les plus fiables."),
]

Q["psy.emotions"] = [
    qcm("Paul Ekman a proposé six émotions de base. Laquelle n'en fait pas partie ?", ["la jalousie", "la peur", "la colère", "la surprise"], "Ses six émotions : joie, tristesse, peur, colère, dégoût et surprise."),
    qcm("Quelle structure du cerveau est associée à la peur ?", ["l'amygdale", "le cervelet", "le bulbe olfactif", "la moelle épinière"], "Elle déclenche des réactions rapides face à un danger."),
    vf("Les expressions faciales des émotions de base sont reconnues dans de nombreuses cultures.", True, "Ekman l'a observé jusque chez les Fore de Papouasie-Nouvelle-Guinée, dans les années 1960."),
    qcm("L'empathie cognitive, c'est :", ["comprendre ce que l'autre ressent ou pense", "ressentir la même émotion que lui", "être gentil", "imiter ses gestes"], "Ressentir avec l'autre, c'est l'empathie émotionnelle."),
    qcm("Qui a popularisé l'« intelligence émotionnelle » en 1995 ?", ["Daniel Goleman", "Sigmund Freud", "Jean Piaget", "Carl Rogers"], "Le concept vient de Salovey et Mayer (1990) ; le livre de Goleman l'a rendu célèbre."),
    qcm("Quelle hormone déclenche surtout la réaction « combat ou fuite » ?", ["l'adrénaline", "la mélatonine", "l'insuline", "l'ocytocine"], "Le cœur accélère, les muscles se préparent à agir."),
    vf("Mettre un mot sur son émotion (« je me sens anxieux ») peut aider à la réguler.", True, "Des études d'imagerie montrent une baisse de l'activité de l'amygdale (Lieberman et al., 2007)."),
    qcm("L'écoute active consiste notamment à :", ["reformuler ce que dit l'autre", "préparer sa réponse pendant qu'il parle", "donner tout de suite des conseils", "changer de sujet"], "Reformuler montre qu'on a compris et laisse l'autre corriger."),
    qcm("La contagion émotionnelle, c'est :", ["attraper sans s'en rendre compte les émotions des autres", "une maladie", "un biais de mémoire", "un trouble du sommeil"], "Un bâillement ou un fou rire se propagent de la même façon."),
    qcm("La réévaluation cognitive est une stratégie qui :", ["change l'interprétation d'une situation pour en changer l'émotion", "supprime l'émotion par la volonté", "évite la situation", "ignore l'émotion"], "Voir un trac comme de l'excitation plutôt que de la peur, par exemple."),
    vf("Réprimer systématiquement ses émotions est la stratégie la plus efficace à long terme.", False, "La suppression coûte de l'énergie et ne réduit pas l'émotion ressentie."),
    qcm("Chez quel animal les neurones miroirs ont-ils été découverts ?", ["le macaque", "le rat", "l'humain", "le pigeon"], "Par l'équipe de Giacomo Rizzolatti à Parme, dans les années 1990."),
]

Q["psy.memoire"] = [
    qcm("Hermann Ebbinghaus (1885) a montré que l'oubli est :", ["très rapide juste après l'apprentissage, puis plus lent", "régulier dans le temps", "nul la première semaine", "aléatoire"], "C'est la courbe de l'oubli, à l'origine des rappels de ce jeu."),
    qcm("Selon George Miller (1956), la mémoire à court terme retient environ :", ["7 éléments, à 2 près", "3 éléments", "20 éléments", "un nombre illimité"], "D'où l'intérêt de regrouper un numéro de téléphone par paires."),
    vf("Réviser à intervalles espacés est plus efficace que tout réviser d'un coup.", True, "C'est l'effet d'espacement, l'un des résultats les plus solides de la psychologie de l'apprentissage."),
    qcm("Quelle structure du cerveau joue un rôle clé dans la formation de nouveaux souvenirs ?", ["l'hippocampe", "l'amygdale", "le cervelet", "la moelle épinière"], "Son nom vient de sa forme, qui rappelle un cheval de mer."),
    qcm("Le patient H. M. (Henry Molaison) est célèbre parce que :", ["il ne pouvait plus former de nouveaux souvenirs après une opération", "il se souvenait de tout", "il parlait vingt langues", "il ne dormait jamais"], "Après l'ablation de ses hippocampes en 1953, il a pourtant appris de nouveaux gestes."),
    vf("Nos souvenirs sont des enregistrements fidèles et immuables.", False, "Chaque rappel reconstruit le souvenir, et peut le modifier."),
    qcm("Elizabeth Loftus est connue pour ses travaux sur :", ["les faux souvenirs", "la mémoire des poissons", "le sommeil paradoxal", "l'intelligence artificielle"], "Elle a montré qu'une question orientée peut modifier le souvenir d'un témoin."),
    qcm("Le « palais de mémoire » consiste à :", ["associer chaque élément à un lieu d'un trajet familier", "répéter à voix haute", "écrire dix fois", "dormir dessus"], "On l'appelle aussi méthode des lieux ; elle remonte à l'Antiquité."),
    qcm("Pourquoi le sommeil aide-t-il la mémoire ?", ["il consolide les souvenirs", "il efface tout", "il n'a aucun effet", "il les rend faux"], "Les souvenirs de la journée sont rejoués et stabilisés pendant la nuit."),
    qcm("Avoir un mot « sur le bout de la langue », c'est :", ["un échec passager pour retrouver un souvenir", "une perte définitive", "un trouble grave du langage", "un faux souvenir"], "L'information est bien en mémoire ; c'est l'accès qui bloque."),
    vf("Le poisson rouge a une mémoire de trois secondes.", False, "Des expériences montrent qu'il retient des associations pendant des semaines, voire des mois."),
    qcm("Dans une liste, on retient mieux :", ["les premiers et les derniers éléments", "ceux du milieu", "les plus longs", "des éléments au hasard"], "Ce sont les effets de primauté et de récence."),
]

Q["psy.motivation"] = [
    qcm("La motivation intrinsèque, c'est agir :", ["pour l'intérêt ou le plaisir de l'activité", "pour une récompense", "sous la contrainte", "par peur"], "La motivation extrinsèque vient de l'extérieur : salaire, note, punition."),
    qcm("La théorie de l'autodétermination (Deci et Ryan) repose sur trois besoins :", ["autonomie, compétence, appartenance", "argent, pouvoir, gloire", "faim, soif, sommeil", "peur, joie, colère"], "Quand ces besoins sont satisfaits, la motivation est plus durable."),
    vf("Récompenser une activité qu'on aime déjà peut réduire l'envie de la faire.", True, "C'est l'effet de surjustification : l'activité devient un moyen d'obtenir la récompense."),
    qcm("Dans la pyramide associée à Maslow, que trouve-t-on à la base ?", ["les besoins physiologiques", "l'accomplissement de soi", "l'estime", "l'appartenance"], "Manger, boire, dormir. Maslow lui-même n'a jamais dessiné de pyramide."),
    qcm("Selon Mihaly Csikszentmihalyi, l'état de « flow » apparaît quand :", ["le défi est à la hauteur de nos compétences", "la tâche est très facile", "on est distrait", "on est fatigué"], "Trop facile, on s'ennuie ; trop difficile, on angoisse."),
    qcm("Quel neurotransmetteur est associé à l'anticipation d'une récompense ?", ["la dopamine", "la mélatonine", "l'adrénaline", "le GABA"], "Elle signale ce qui vaut la peine d'être recherché, plus que le plaisir lui-même."),
    vf("Un objectif précis et mesurable motive davantage que « faire de son mieux ».", True, "C'est un résultat central de la théorie de Locke et Latham."),
    qcm("Le test du marshmallow de Walter Mischel portait sur :", ["la capacité à différer une récompense", "la mémoire", "la peur", "l'empathie"], "Une friandise tout de suite, ou deux si l'enfant patiente quelques minutes."),
    qcm("La procrastination est souvent liée à :", ["l'évitement des émotions désagréables liées à la tâche", "la paresse uniquement", "un manque d'intelligence", "trop de temps libre"], "On repousse ce qui ennuie, angoisse ou paraît flou."),
    qcm("L'effet Zeigarnik désigne le fait que :", ["on se souvient mieux des tâches inachevées", "on oublie aussitôt les tâches finies", "on préfère les tâches faciles", "on travaille mieux la nuit"], "Une tâche commencée reste « ouverte » dans l'esprit."),
    vf("Avoir un « état d'esprit de croissance » (Carol Dweck), c'est croire que ses capacités peuvent se développer.", True, "Par opposition à l'état d'esprit fixe, qui les croit figées."),
    qcm("Pour installer une habitude durable, il est conseillé :", ["de l'attacher à un moment régulier et de commencer petit", "de compter sur la volonté seule", "de tout changer d'un coup", "d'attendre la motivation"], "Le rappel quotidien de ce jeu repose sur ce principe."),
]

Q["psy.influence"] = [
    qcm("L'expérience des lignes de Solomon Asch (1951) a montré :", ["le conformisme au groupe", "l'obéissance à l'autorité", "les limites de la mémoire", "la perception des couleurs"], "Beaucoup de participants donnaient une réponse visiblement fausse pour suivre le groupe."),
    qcm("L'expérience de Stanley Milgram (1963) étudiait :", ["l'obéissance à l'autorité", "le conformisme", "la mémoire", "l'altruisme"], "Des participants devaient envoyer des chocs électriques (fictifs) à un « élève »."),
    vf("Dans l'expérience de Milgram, une majorité de participants sont allés jusqu'au choc maximal de 450 volts.", True, "65 % dans la version principale de l'expérience."),
    qcm("L'effet du témoin, c'est que :", ["plus il y a de témoins, moins chacun intervient", "on aide davantage en groupe", "les témoins mentent", "on aide toujours"], "Chacun pense qu'un autre va agir : la responsabilité se dilue."),
    qcm("L'effet de halo, c'est :", ["une qualité remarquée qui influence le jugement des autres qualités", "une illusion d'optique", "une lumière autour du visage", "un biais de mémoire"], "Une personne séduisante est souvent jugée plus intelligente."),
    qcm("La dissonance cognitive (Festinger, 1957), c'est :", ["l'inconfort ressenti face à deux croyances, ou une croyance et un acte, contradictoires", "un trouble de l'audition", "l'oubli", "la peur de la foule"], "Pour le réduire, on change souvent de croyance plutôt que de comportement."),
    vf("Obtenir une petite faveur augmente les chances d'en obtenir une plus grande ensuite.", True, "C'est la technique du pied dans la porte (Freedman et Fraser, 1966)."),
    qcm("Selon Cialdini, le principe de réciprocité veut que :", ["l'on se sente obligé de rendre une faveur", "l'on imite les autres", "l'on obéisse aux experts", "l'on désire ce qui est rare"], "D'où les échantillons gratuits."),
    qcm("La rareté comme levier d'influence signifie que :", ["ce qui est rare ou limité paraît plus désirable", "ce qui est rare est moins cher", "on fuit ce qui est rare", "elle n'a aucun effet"], "« Plus que 2 en stock », « offre valable jusqu'à minuit »."),
    qcm("La polarisation de groupe, c'est :", ["des opinions qui deviennent plus extrêmes après une discussion en groupe", "un groupe qui devient neutre", "un groupe qui se divise toujours", "une absence d'effet"], "Les arguments échangés vont surtout dans le sens déjà dominant."),
    vf("La pensée de groupe peut conduire des experts à de mauvaises décisions collectives.", True, "Irving Janis (1972) l'illustre avec le débarquement raté de la baie des Cochons."),
    qcm("Aujourd'hui, l'expérience de la prison de Stanford (Zimbardo, 1971) est :", ["vivement critiquée pour sa méthode", "considérée comme irréprochable", "jugée imaginaire", "une étude sur la mémoire"], "Des archives montrent que les « gardiens » ont été encouragés à se montrer durs."),
]


NOMS_PORTRAITS = portraits.par_nom()


def questions():
    out = []
    for comp, qs in {**Q, **Q_NOUVELLES, **philosophes.Q, **approfondissement_sciences.Q, **approfondissement_humain.Q}.items():
        assert len(qs) == 12, (comp, len(qs))
        for i, q in enumerate(qs, 1):
            id = f"{comp}.q{i:02d}"
            q = {"id": id, "competence": comp, **q}
            if id in ENONCE:
                q["illustration"] = ENONCE[id]
            if id in EXPLICATION:
                q["illustration_explication"] = EXPLICATION[id]
            if id in figures.QUESTIONS:
                q["figure"] = figures.QUESTIONS[id]
            # v15 : bonne réponse = une personne qui a un portrait → portrait et biographie au retour.
            if q.get("type") == "qcm":
                rep = q["choix"][q["reponse"]]
                qui = NOMS_PORTRAITS.get(rep["fr"] if isinstance(rep, dict) else rep)
                if qui:
                    q["portrait"] = {"famille": qui[0], "id": qui[1]}
            out.append(q)
    ids = {q["id"] for q in out}
    assert set(ENONCE) <= ids and set(EXPLICATION) <= ids, (set(ENONCE) | set(EXPLICATION)) - ids
    assert set(figures.QUESTIONS) <= ids, set(figures.QUESTIONS) - ids
    return out


# --- Succès -----------------------------------------------------------------

SUCCES = [
    succes("premier-pas", "Premier pas", "Maîtriser une première compétence.",
           {"type": "competences_maitrisees", "n": 1},
           citation("Dans les champs de l'observation, le hasard ne favorise que les esprits préparés.",
                    "Louis Pasteur", "Discours inaugural, faculté des sciences de Lille, 7 décembre 1854")),
    succes("eureka", "Eurêka", "Réussir deux quiz sans aucune erreur.",
           {"type": "quiz_parfaits", "n": 2},
           anecdote("Selon Vitruve, Archimède aurait compris comment mesurer le volume d'une couronne en entrant dans son bain. Il serait alors sorti dans la rue, nu, en criant « Eurêka ! » (« J'ai trouvé ! »).",
                    "Vitruve, De l'architecture, livre IX")),
    succes("petit-gauss", "Le petit Gauss", "Réussir 5 quiz sans erreur.",
           {"type": "quiz_parfaits", "n": 5},
           anecdote("Vers 9 ans, Carl Friedrich Gauss aurait calculé en un instant la somme des nombres de 1 à 100, que son maître avait donnée pour occuper la classe. Il aurait vu 50 paires valant chacune 101, soit 5 050. Le récit est sans doute embelli.",
                    "Wolfgang Sartorius von Waltershausen, Gauss zum Gedächtniss, 1856")),
    succes("branche-logique", "Langue du monde", "Maîtriser le premier losange de Logique.",
           {"type": "branche_complete", "stat": "logique", "rang_max": 4},
           citation("La philosophie est écrite dans ce très grand livre qui se tient constamment ouvert devant nos yeux, je veux dire l'Univers. […] Il est écrit en langue mathématique.",
                    "Galilée", "L'Essayeur (Il Saggiatore), 1623")),
    succes("branche-mecanique", "Unités de compte", "Maîtriser le premier losange de Mécanique.",
           {"type": "branche_complete", "stat": "mecanique", "rang_max": 4},
           anecdote("En 1999, la sonde Mars Climate Orbiter s'est perdue dans l'atmosphère de Mars. Un logiciel donnait ses valeurs en livres-force·seconde, un autre les lisait en newtons·seconde.",
                    "NASA, rapport du Mars Climate Orbiter Mishap Investigation Board, 1999")),
    succes("branche-savoir", "Heureux hasard", "Maîtriser le premier losange de Savoir.",
           {"type": "branche_complete", "stat": "savoir", "rang_max": 4},
           anecdote("En septembre 1928, Alexander Fleming rentre de vacances et trouve une boîte de culture envahie par une moisissure. Autour d'elle, les bactéries ont disparu : c'est la découverte de la pénicilline.",
                    "Alexander Fleming, British Journal of Experimental Pathology, 1929")),
    succes("branche-eloquence", "Cailloux en bouche", "Maîtriser le premier losange d'Éloquence.",
           {"type": "branche_complete", "stat": "eloquence", "rang_max": 4},
           anecdote("Selon Plutarque, Démosthène, le plus grand orateur d'Athènes, corrigeait son défaut de prononciation en parlant avec des cailloux dans la bouche, et déclamait face à la mer pour couvrir le bruit des vagues.",
                    "Plutarque, Vies parallèles, Vie de Démosthène")),
    succes("branche-lucidite", "Jus de citron", "Maîtriser le premier losange de Lucidité.",
           {"type": "branche_complete", "stat": "lucidite", "rang_max": 4},
           anecdote("En 1995, McArthur Wheeler braque deux banques de Pittsburgh à visage découvert, enduit de jus de citron, persuadé que cela le rend invisible aux caméras. Son histoire ouvre l'article de Dunning et Kruger.",
                    "Kruger et Dunning, « Unskilled and Unaware of It », 1999")),
    succes("branche-empathie", "Les raisons du cœur", "Maîtriser le premier losange d'Empathie.",
           {"type": "branche_complete", "stat": "empathie", "rang_max": 4},
           citation("Le cœur a ses raisons, que la raison ne connaît point.",
                    "Blaise Pascal", "Pensées, 1670")),
    succes("polymathe", "Polymathe", "Maîtriser au moins une compétence dans chacune des 10 branches.",
           {"type": "toutes_branches"},
           anecdote("Le mot anglais « scientist » n'existe que depuis 1834. William Whewell l'a proposé, sur le modèle d'« artist », pour désigner ceux qu'on appelait jusque-là des « philosophes de la nature ».",
                    "William Whewell, Quarterly Review, 1834")),
    succes("dix-competences", "Tête bien faite", "Maîtriser 10 compétences.",
           {"type": "competences_maitrisees", "n": 10},
           citation("Je voudrais aussi qu'on fût soigneux de lui choisir un conducteur qui eût plutôt la tête bien faite que bien pleine.",
                    "Montaigne", "Essais, livre I, chapitre 26, 1580")),
    succes("arbre-complet", "Sur les épaules de géants", "Maîtriser les 80 compétences.",
           {"type": "competences_maitrisees", "n": 80},
           citation("Si j'ai vu plus loin, c'est en me tenant sur les épaules de géants.",
                    "Isaac Newton", "Lettre à Robert Hooke, 5 février 1676")),
    succes("premier-rappel", "Cobaye volontaire", "Réussir un premier rappel.",
           {"type": "rappels_reussis", "n": 1},
           anecdote("Pour étudier l'oubli, Hermann Ebbinghaus a appris par cœur des milliers de syllabes sans sens, comme « DAX » ou « BOK ». Il était le seul sujet de ses propres expériences.",
                    "Hermann Ebbinghaus, Über das Gedächtnis, 1885")),
    succes("serie-rappels", "Ne pas se tromper soi-même", "Réussir 5 rappels d'affilée.",
           {"type": "serie_rappels", "n": 5},
           citation("Le premier principe est que vous ne devez pas vous tromper vous-même, et vous êtes la personne la plus facile à tromper.",
                    "Richard Feynman", "« Cargo Cult Science », discours à Caltech, 1974 (traduction)")),
    succes("cinquante-rappels", "Pierre après pierre", "Réussir 50 rappels.",
           {"type": "rappels_reussis", "n": 50},
           citation("On fait la science avec des faits, comme on fait une maison avec des pierres ; mais une accumulation de faits n'est pas plus une science qu'un tas de pierres n'est une maison.",
                    "Henri Poincaré", "La Science et l'Hypothèse, 1902")),
    succes("constance", "Constance", "Garder une compétence maîtrisée pendant 180 jours.",
           {"type": "duree_maitrise", "jours": 180},
           citation("Ce que l'on conçoit bien s'énonce clairement, et les mots pour le dire arrivent aisément.",
                    "Nicolas Boileau", "L'Art poétique, chant I, 1674")),
    succes("niveau-5", "Le serpent qui se mord la queue", "Atteindre le niveau 5 dans une stat.",
           {"type": "niveau_stat", "niveau": 5},
           anecdote("August Kekulé racontait avoir trouvé la structure en anneau du benzène en rêvassant devant le feu : il y aurait vu un serpent qui se mordait la queue.",
                    "Discours d'August Kekulé lors du Benzolfest, Berlin, 1890")),
    succes("resilience", "Même Erdős", "Regagner une compétence perdue.",
           {"type": "competences_regagnees", "n": 1},
           anecdote("En 1990, Marilyn vos Savant publie la bonne réponse au problème de Monty Hall. Elle reçoit des milliers de lettres l'accusant d'erreur. Le mathématicien Paul Erdős lui-même n'a été convaincu qu'en voyant une simulation.",
                    "Paul Hoffman, The Man Who Loved Only Numbers, 1998")),
    succes("tour-de-pise", "La tour de Pise", "Échouer à un quiz.",
           {"type": "quiz_rates", "n": 1},
           anecdote("Galilée aurait lâché deux boules du haut de la tour de Pise pour montrer qu'elles tombent ensemble. Le récit vient de son disciple Viviani, et la plupart des historiens doutent que l'expérience ait eu lieu.",
                    "Vincenzo Viviani, Racconto istorico della vita di Galileo, 1654"),
           cache=True),
    succes("pomme", "La pomme", "Jouer 7 jours différents.",
           {"type": "jours_actifs", "n": 7},
           anecdote("Newton a bien raconté à William Stukeley, en 1726, qu'une pomme tombant dans un jardin l'avait fait réfléchir à la gravitation. La pomme qui lui tombe sur la tête est une invention plus tardive.",
                    "William Stukeley, Memoirs of Sir Isaac Newton's Life, 1752"),
           cache=True),
    succes("lucide", "L'ignorance confiante", "Perdre une compétence lors d'un rappel.",
           {"type": "competences_perdues", "n": 1},
           citation("L'ignorance engendre plus souvent la confiance que ne le fait la connaissance.",
                    "Charles Darwin", "La Descendance de l'homme, introduction, 1871 (traduction)"),
           cache=True),
]


def avatar():
    c = avatar40.calques()
    return {
        "format": 3,
        "palette": PALETTE,
        "emplacements": EMPLACEMENTS,
        "taille": [avatar40.L, avatar40.H],
        "corps": c["corps"],
        "cheveux": c["cheveux"],
        "rangs": [{"id": r["id"], "nom": fr(r["nom"]), "niveau_min": r["niveau_min"], "couleurs": r["couleurs"], "tenue": c["tenues"][r["id"]]}
                  for r in avatar40.RANGS],
        "accessoires": [{"id": id, "nom": fr(nom), "emplacement": c["accessoires"][id][0], "condition": cond, "pixels": c["accessoires"][id][1]}
                        for id, nom, cond in ACCESSOIRES],
        # v4 : savants jouables, qui remplacent l'avatar ; le rang se lit alors au cadre.
        "savants": [{"id": s[0], "nom": fr(s[1]), "annees": s[2], "condition": s[9], "notice": fr(s[10]), "source": s[11],
                     "couleurs": s[5], "base": cq["base"], "cheveux": cq["cheveux"]} for s, cq in zip(savants.SAVANTS, savants.calques())],
        # v15 : portraits des personnes qu'une question fait choisir par leur nom.
        "portraits": portraits.donnees(),
        # v25 : tenues que l'IA impose par farce, en recolorant les vêtements.
        "tenues_farce": tenues_farce.donnees(),
    }


def tous_objets():
    # v10 : les objets brillants, faits pour être offerts à l'IA.
    neufs = [objet(id, nom, annee, notice, source, {"type": "competence_maitrisee", "id": comp}) for id, nom, annee, notice, source, comp, _, _ in brillants.OBJETS]
    return OBJETS + [objet(*o) for o in philosophes.OBJETS] + [objet(*o) for o in objectifs.objets()] + neufs


def cabinet():
    pixels = objets32.objets()
    liste = tous_objets()
    assert {o["id"] for o in liste} == set(pixels), set(pixels) ^ {o["id"] for o in liste}
    return {"format": 2, "palette": PALETTE, "taille": [objets32.N, objets32.N],
            # v11 : la source citée quand on offre ou qu'on porte l'objet, et son bonus quand l'avatar le tient.
            "chance_bonus": objets_v11.CHANCE_BONUS,
            "objets": [{**o, "pixels": pixels[o["id"]], "cadeau": cadeau(o["id"]), "citation": citation_objet(o["id"]), "bonus": bonus_objet(o["id"])} for o in liste]}


def citation_objet(id):
    verbatim, texte, source = objets_v11.CITATIONS[id]
    return {"verbatim": verbatim, "texte": fr(texte), "source": source}


def bonus_objet(id):
    t, n = objets_v11.bonus(id, cadeau(id)["eclat"])
    return {"type": t, "n": n} if n else {"type": t}


def cadeau(id):
    neufs = {o[0]: o for o in brillants.OBJETS}
    effet, n, garde, texte = neufs[id][6] if id in neufs else cadeaux.CADEAUX[id]
    # v10 : l'éclat de l'objet (1 terne, 2 brillant, 3 éblouissant) fait monter la faveur de l'IA.
    out = {"effet": effet, "garde": garde, "texte": fr(texte), "eclat": neufs[id][7] if id in neufs else brillants.ECLAT.get(id, 1)}
    if n:
        out["n"] = n
    return out


def tous_succes():
    return SUCCES + SUCCES_V2 + philosophes.SUCCES + plateau.SUCCES + objectifs.SUCCES + pionniers.SUCCES + ennemis.succes() + mendeleiev.succes() + honte.succes() + succes_themes.succes_v18()


def commentaires():
    # v18 : en plus, les lignes propres à chaque arbre (annonce, réussite, échec).
    return {"format": 3, "narrateur": fr(ia.NOM), "commentaires": ia.repliques() + ia_themes.repliques(), "apartes": ia.apartes(), "surnoms": ia.surnoms()}


def regles_masque(id):
    car, regles, texte = masques_regles.REGLES[id]
    return {"caractere": car, "regles": regles, "texte_regles": fr(texte)}


def narrateur():
    """L'IA : ses masques (un par palier de succès) et l'expression prise selon le contexte."""
    calques = {m["id"]: m for m in masques.calques()}
    return {
        "format": 2,
        "nom": fr(ia.NOM),
        "portrait": fr(masques_regles.PORTRAIT),
        "palette": PALETTE,
        "taille": [40, 48],
        "expressions": {**ia.EXPRESSIONS, **ia_themes.expressions()},
        "masques_jour": {"max": 3, "selon_faveur": masques_regles.SELON_FAVEUR},
        "credits": credits.donnees(),
        # v25 : son nom, donné une fois qu'elle est comblée.
        "alyca": alyca.donnees(),
        "faveur": {**brillants.FAVEUR, "paliers": [{**p, "nom": fr(p["nom"]), "effet": fr(p["effet"])} for p in brillants.FAVEUR["paliers"]]},
        "masques": [{"id": m["id"], "nom": fr(m["nom"]), **({"condition": m["condition"]} if m["condition"] else {}), "notice": fr(m["notice"]),
                     "source": m["source"], "tons": masques.TONS[m["id"]], **regles_masque(m["id"]), "base": calques[m["id"]]["base"], "expressions": calques[m["id"]]["expressions"]} for m in masques.MASQUES],
    }


def icone_case(c, icones, objets):
    ill = c[5] or plateau.PICTO_EPOQUE[plateau.epoque(c[1])]
    assert ill in icones or ill in objets, ill
    return ill


def jeu_plateau():
    icones = icones32.icones()
    objets = objets32.objets()
    cases = []
    for i, c in enumerate(plateau.CASES):
        id, annee, titre, phrase, stat, ill, histoire, replique, source, special = c
        n = i + 1
        if special is None and n % 9 == 0 and n < len(plateau.CASES):
            special = {"type": "eureka"}
        if special and special["type"] == "retour_epoque":
            special = {"type": "retour_epoque", "vers": plateau.debut_epoque(plateau.epoque(annee))}
        if n in pieges.PIEGES:
            assert special is None or special["type"] == "eureka", (n, special)
            regle, raison = pieges.PIEGES[n]
            special = dict(regle, raison=fr(raison))
        if n in mendeleiev.CASES:
            assert special is None, (n, special)
            special = {"type": "mendeleiev", "raison": fr(mendeleiev.CASES[n])}
        case = {"n": n, "id": id, "annee": annee, "titre": fr(titre), "stat": stat, "epoque": plateau.epoque(annee),
                "icone": icone_case(c, icones, objets), "histoire": fr(histoire), "replique": fr(replique), "source": source}
        if special:
            case["special"] = special
        cases.append(case)
    # Les emblèmes des livres puisent aussi dans les icônes du plateau.
    utilisees = {c["icone"] for c in cases} | set(plateau.PICTO_EPOQUE.values()) | {l[5] for l in bibliotheque.LIVRES + bibliotheque_v7.LIVRES + bibliotheque_v8.LIVRES}
    manquants = {l[5] for l in bibliotheque.LIVRES + bibliotheque_v7.LIVRES + bibliotheque_v8.LIVRES} - set(icones) - set(objets)
    assert not manquants, manquants
    return {
        "format": 1,
        "regles": {
            "depart": 1, "arrivee": len(cases),
            # v6 : une épreuve réussie fait avancer d'autant de cases que le rang de sa compétence, rappels compris.
            "valeurs": {"rappel": 1, "quiz_rang": {str(r): r for r in range(1, 9)}},
            "bonus": {"parfait": 0, "chrono": 0, "du_jour": 0, "jouer": 0, "jouer_max": 4},
            # v6 : butin. Chance qu'une épreuve réussie fasse tomber un objet, un livre, un accessoire ou un masque.
            "butin": {"rappel": 0.4, "quiz_base": 0.4, "quiz_par_rang": 0.05, "lots": LOTS},
            "echec": {"quiz": 0, "rappel": -2},
            "tour_suivant": {"multiplicateur_recul": 2, "quiz_parfaits_prison": 2},
            "textes": {k: fr(v) for k, v in {**plateau.REGLES_SPECIALES, **pieges.TEXTES, **mendeleiev.TEXTES}.items()},
        },
        "epoques": [{"id": id, "nom": fr(nom), "debut": d, "fin": f, "icone": plateau.PICTO_EPOQUE[id]} for id, nom, d, f in plateau.EPOQUES],
        "palette": PALETTE,
        "taille": [icones32.N, icones32.N],
        "icones": {k: v for k, v in icones.items() if k in utilisees},
        "cases": cases,
        "objectifs": objectifs.objectifs(),
        "parcours": parcours.donnees(),
    }


def frise():
    evenements = []
    for i, c in enumerate(plateau.CASES):
        evenements.append({"id": c[0], "annee": c[1], "titre": fr(c[2]), "phrase": fr(c[3]), "stat": c[4], "epoque": plateau.epoque(c[1]),
                           "source": c[8], "case": i + 1, "condition": {"type": "case_atteinte", "n": i + 1}})
    for id, annee, titre, phrase, stat, comp, detail, source in plateau.DATES + approfondissement_sciences.DATES + approfondissement_humain.DATES:
        evenements.append({"id": id, "annee": annee, "titre": fr(titre), "phrase": fr(phrase), "stat": stat, "epoque": plateau.epoque(annee),
                           "detail": fr(detail), "source": source, "condition": {"type": "competence_maitrisee", "id": comp}})
    evenements.sort(key=lambda e: e["annee"])
    return {"format": 1, "epoques": [{"id": id, "nom": fr(nom), "debut": d, "fin": f} for id, nom, d, f in plateau.EPOQUES],
            "evenements": evenements}


def livres():
    out = []
    for id, titre, auteur, annee, stat, embleme, couleur, cond, resume, importance, anec, source, reaction in bibliotheque.LIVRES + bibliotheque_v7.LIVRES + bibliotheque_v8.LIVRES:
        # v7 : chaque livre est rattaché à une compétence ; v8 : une compétence peut en avoir plusieurs.
        competence = bibliotheque_v7.THEMES.get(id) or bibliotheque_v8.COMPETENCES.get(id) or cond["id"]
        out.append({"id": id, "titre": fr(titre), "auteur": auteur, "annee": annee, "stat": stat, "embleme": embleme, "couleur": couleur,
                    "condition": cond, "competence": competence, "resume": fr(resume), "importance": fr(importance), "anecdote": fr(anec), "source": source,
                    "reaction": fr(reaction)})
        # v26 : un extrait vérifié du vrai livre, quand on en a un.
        ex = extraits.donnees(id)
        if ex:
            out[-1]["extrait"] = ex
    assert set(extraits.EXTRAITS) <= {l["id"] for l in out}, set(extraits.EXTRAITS) - {l["id"] for l in out}
    assert len({l["id"] for l in out}) == len(out), "deux livres avec le même id"
    out.sort(key=lambda l: l["annee"])
    return {"format": 1, "livres": out}


# v6 : le butin est réparti en lots, un par tour du plateau. Le lot N ne tombe qu'à partir du tour N.
LOTS = 7


def assigner_lots(fichiers):
    """Classe chaque objet, livre, accessoire et masque par difficulté de sa condition, puis le range dans un lot."""
    comps = {k["id"]: k["rang"] for k in fichiers["skills.json"]["competences"]}
    succes = {x["id"]: x for x in fichiers["succes.json"]["succes"]}

    def difficulte(cond, prof=0):
        if not cond or prof > 4:
            return 0
        t = cond["type"]
        if t == "competence_maitrisee":
            return comps.get(cond["id"], 4)
        if t in ("case_atteinte", "case_visitee", "epoque_atteinte"):
            return cond["n"] / 9
        if t == "succes":
            return difficulte(succes[cond["id"]]["condition"], prof + 1)
        if t == "succes_obtenus":
            return cond["n"] / 11
        if t == "tours_plateau":
            return 1 + cond["n"]
        if t == "branche_complete":
            return 4.5
        return 3

    familles = [(fichiers["objets.json"]["objets"], lambda x: x["condition"]["type"] != "tours_plateau"),
                (fichiers["bibliotheque.json"]["livres"], lambda x: True),
                (fichiers["avatar.json"]["accessoires"], lambda x: True),
                (fichiers["ia.json"]["masques"], lambda x: "condition" in x)]
    for liste, eligible in familles:
        elus = [x for x in liste if eligible(x)]
        tries = sorted(enumerate(elus), key=lambda p: (difficulte(p[1].get("condition")), p[0]))
        for rang, (_, x) in enumerate(tries):
            x["lot"] = 1 + rang * LOTS // len(tries)


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    fichiers = {
        "regles.json": REGLES,
        "skills.json": {"format": 1, "competences": competences(),
                        "figures": {k: {"titre": figures.TITRES[k], "svg": v} for k, v in figures.FIGURES.items()}},
        "questions.json": {"format": 1, "questions": questions()},
        "succes.json": {"format": 1, "succes": [{**x, "illustration": succes_pixels.illustration(x)} for x in tous_succes()], "dessins": succes_pixels.dessins()},
        "commentaires.json": commentaires(),
        "objets.json": cabinet(),
        "avatar.json": avatar(),
        "ia.json": narrateur(),
        "plateau.json": jeu_plateau(),
        "frise.json": frise(),
        "bibliotheque.json": livres(),
        "ennemis.json": ennemis.donnees(),
        "atomes.json": mendeleiev.donnees(),
    }
    assigner_lots(fichiers)
    # v18 : le thème de chaque chose, pour que la case du pion donne le ton.
    themes.poser(fichiers)
    for nom, contenu in fichiers.items():
        (DATA / nom).write_text(json.dumps(contenu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(nom, "écrit")


if __name__ == "__main__":
    main()
