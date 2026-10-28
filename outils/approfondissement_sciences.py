"""v4 : second losange (rangs 5 à 8) des branches scientifiques.

Logique, Mécanique, Savoir, Alchimie, Cosmos, Étincelle : 4 compétences chacune, 12 questions par compétence.
Convention : pour un QCM, la bonne réponse est écrite en premier.
"""
from aides import num, qcm, vf

BRANCHES = {
    "logique": [
        ("math.algebre", "Algèbre et équations", "Inconnues, équations, identités remarquables et systèmes."),
        ("math.statistiques", "Statistiques", "Moyenne, médiane, écart type, corrélation et échantillons."),
        ("math.geometrie", "Géométrie et trigonométrie", "Angles, aires, volumes, Pythagore, sinus et cosinus."),
        ("math.infini", "Suites, limites et infini", "Suites, séries, limites et les paradoxes de l'infini."),
    ],
    "mecanique": [
        ("phys.fluides", "Pression et fluides", "Pression, poussée d'Archimède, flottaison et écoulements."),
        ("phys.thermo", "Chaleur et thermodynamique", "Température, chaleur, entropie et machines thermiques."),
        ("phys.relativite", "Relativité", "Vitesse de la lumière, temps dilaté, E = mc² et gravitation d'Einstein."),
        ("phys.quantique", "Physique quantique", "Photons, dualité onde-particule, incertitude et atomes."),
    ],
    "savoir": [
        ("sci.corps", "Le corps humain", "Organes, circulation, respiration, digestion et squelette."),
        ("sci.immunite", "Microbes et immunité", "Bactéries, virus, vaccins, antibiotiques et défenses du corps."),
        ("sci.ecologie", "Écosystèmes", "Chaînes alimentaires, cycles de la matière, biodiversité et climat."),
        ("sci.biotech", "Biotechnologies", "ADN recombinant, PCR, CRISPR, clonage et vaccins à ARN."),
    ],
    "alchimie": [
        ("chim.etats", "États de la matière", "Solide, liquide, gaz, changements d'état et lois des gaz."),
        ("chim.organique", "Chimie organique", "Le carbone, les hydrocarbures, les polymères et les molécules du vivant."),
        ("chim.quotidien", "Chimie du quotidien", "Cuisine, savon, médicaments, piles et matériaux."),
        ("chim.noyau", "Radioactivité et noyau", "Isotopes, demi-vie, fission, fusion et datation."),
    ],
    "cosmos": [
        ("astro.observer", "Observer le ciel", "Constellations, saisons, télescopes et unités de distance."),
        ("astro.espace", "Conquête spatiale", "Fusées, satellites, missions habitées et sondes lointaines."),
        ("astro.exoplanetes", "Exoplanètes et vie ailleurs", "Détecter d'autres mondes et chercher la vie."),
        ("astro.sombre", "Matière et énergie noires", "Ce qui manque dans l'Univers : la masse invisible et l'accélération."),
    ],
    "etincelle": [
        ("elec.em", "Ondes électromagnétiques", "Radio, micro-ondes, infrarouge, rayons X : le spectre de Maxwell."),
        ("elec.electronique", "Électronique", "Diodes, transistors, condensateurs et circuits intégrés."),
        ("elec.energies", "Réseau et énergies", "Centrales, renouvelables, stockage et transport du courant."),
        ("elec.numerique", "Du transistor à l'ordinateur", "Binaire, portes logiques, processeurs et mémoire."),
    ],
}

Q = {}

# --- Logique -------------------------------------------------------------------

Q["math.algebre"] = [
    num("Si 3x + 5 = 20, combien vaut x ?", 5, "3x = 15, donc x = 5."),
    qcm("Développer (a + b)² donne :", ["a² + 2ab + b²", "a² + b²", "a² + ab + b²", "2a + 2b"], "C'est la première identité remarquable : le terme 2ab est souvent oublié."),
    qcm("Le mot « algèbre » vient :", ["de l'arabe al-jabr, dans le titre d'un traité d'al-Khwârizmî", "du grec algos, la douleur", "du latin algebra, le calcul", "du nom d'un mathématicien italien"], "Le traité d'al-Khwârizmî, vers 820, parle de « restauration » (al-jabr) et de « réduction »."),
    num("Combien vaut x si x / 4 = 7 ?", 28, "On multiplie les deux côtés par 4."),
    vf("L'équation x² = -1 n'a aucune solution parmi les nombres réels.", True, "Un carré réel est toujours positif ou nul. Il faut les nombres complexes, où i² = -1."),
    qcm("Factoriser x² - 9 donne :", ["(x - 3)(x + 3)", "(x - 3)²", "(x - 9)(x + 1)", "x(x - 9)"], "C'est la différence de deux carrés : a² - b² = (a - b)(a + b)."),
    num("Système : x + y = 10 et x - y = 4. Combien vaut x ?", 7, "En additionnant les deux équations : 2x = 14, donc x = 7 (et y = 3)."),
    qcm("Qui a introduit l'usage des lettres pour désigner les inconnues et les paramètres, à la fin du XVIe siècle ?", ["François Viète", "Euclide", "Blaise Pascal", "Isaac Newton"], "Viète utilise des voyelles pour les inconnues et des consonnes pour les quantités connues. Descartes fixera ensuite x, y, z."),
    vf("Une équation du second degré peut avoir deux solutions réelles.", True, "Quand son discriminant b² - 4ac est positif. Elle en a une s'il est nul, aucune s'il est négatif."),
    num("Combien vaut le discriminant de x² - 5x + 6 ?", 1, "b² - 4ac = 25 - 24 = 1. Les solutions sont 2 et 3."),
    qcm("Si on double un côté d'une égalité, il faut :", ["doubler aussi l'autre côté", "ne rien faire de l'autre côté", "diviser l'autre côté par deux", "ajouter 2 de l'autre côté"], "Une égalité reste vraie si l'on fait la même opération des deux côtés."),
    qcm("Au XVIe siècle, Tartaglia et Cardan se sont disputé la paternité :", ["de la résolution des équations du troisième degré", "du zéro", "du théorème de Pythagore", "des logarithmes"], "Tartaglia avait confié sa méthode à Cardan sous le sceau du secret ; Cardan la publia en 1545 dans l'Ars magna."),
]

Q["math.statistiques"] = [
    qcm("Dans la série 2, 3, 3, 8, 100, la médiane vaut :", ["3", "23,2", "8", "2"], "La médiane est la valeur du milieu une fois la série rangée. La moyenne, 23,2, est tirée vers le haut par le 100."),
    num("Quelle est la moyenne de 4, 8 et 12 ?", 8, "(4 + 8 + 12) / 3 = 8."),
    vf("Une moyenne peut être trompeuse quand quelques valeurs sont extrêmes.", True, "C'est pourquoi on donne souvent le salaire médian plutôt que le salaire moyen."),
    qcm("L'écart type mesure :", ["la dispersion des valeurs autour de la moyenne", "la valeur la plus fréquente", "la différence entre le maximum et le minimum", "le nombre de valeurs"], "Un petit écart type : les valeurs sont serrées autour de la moyenne."),
    qcm("Le mode d'une série, c'est :", ["la valeur la plus fréquente", "la valeur du milieu", "la moyenne", "l'écart entre extrêmes"], "Dans 1, 2, 2, 5, le mode est 2."),
    vf("Une forte corrélation entre deux variables prouve que l'une cause l'autre.", False, "Les ventes de glaces et les noyades sont corrélées : la cause commune est la chaleur de l'été."),
    num("Dans une loi normale, environ quel pourcentage des valeurs se trouve à moins d'un écart type de la moyenne ?", 68, "Environ 68 %, et environ 95 % à moins de deux écarts types.", tol=2, unite="%"),
    qcm("Qui a décrit l'« homme moyen » en appliquant les statistiques à la société, au XIXe siècle ?", ["Adolphe Quetelet", "Charles Darwin", "Louis Pasteur", "Auguste Comte"], "L'astronome belge Quetelet a aussi inventé l'indice de masse corporelle, en 1832."),
    qcm("Pourquoi tire-t-on un échantillon au hasard pour un sondage ?", ["pour qu'il ressemble à la population entière", "pour aller plus vite", "pour éviter les calculs", "pour choisir les réponses"], "Un échantillon choisi au hasard limite les biais de sélection."),
    vf("Plus l'échantillon d'un sondage est grand, plus la marge d'erreur est petite.", True, "La marge d'erreur diminue comme l'inverse de la racine carrée de la taille de l'échantillon."),
    qcm("En 1936, le Literary Digest prédit la défaite de Roosevelt malgré 2,4 millions de réponses parce que :", ["son échantillon venait surtout d'abonnés au téléphone et de propriétaires de voitures, plus aisés", "il avait mal additionné", "Roosevelt avait triché", "les réponses étaient arrivées trop tard"], "Gallup, avec un échantillon bien plus petit mais représentatif, avait vu juste."),
    qcm("Florence Nightingale est aussi connue pour :", ["ses diagrammes statistiques sur les causes de mortalité des soldats", "la découverte de la pénicilline", "l'invention du thermomètre", "la théorie des germes"], "Ses diagrammes « en crête de coq » de 1858 ont montré que les maladies tuaient plus que les blessures en Crimée."),
]

Q["math.geometrie"] = [
    num("Un triangle rectangle a des côtés de l'angle droit de 3 et 4. Combien mesure l'hypoténuse ?", 5, "3² + 4² = 9 + 16 = 25, et √25 = 5."),
    num("Quelle est la somme des angles d'un triangle, en degrés ?", 180, "Dans la géométrie d'Euclide, toujours 180°.", unite="°"),
    qcm("L'aire d'un disque de rayon r vaut :", ["π r²", "2 π r", "π d", "r²"], "2 π r est le périmètre, pas l'aire."),
    num("Combien vaut le cosinus de 60° ?", 0.5, "cos 60° = 1/2.", tol=0.01),
    qcm("Dans un triangle rectangle, le sinus d'un angle aigu est :", ["le côté opposé divisé par l'hypoténuse", "le côté adjacent divisé par l'hypoténuse", "le côté opposé divisé par le côté adjacent", "l'hypoténuse divisée par le côté opposé"], "Moyen mnémotechnique : SOH CAH TOA."),
    vf("Sur une sphère, la somme des angles d'un triangle peut dépasser 180°.", True, "Un triangle tracé du pôle Nord à l'équateur peut avoir trois angles droits : 270°."),
    num("Combien vaut le volume d'un cube de 3 cm de côté, en cm³ ?", 27, "3 × 3 × 3 = 27.", unite="cm³"),
    qcm("Thalès aurait mesuré la hauteur d'une pyramide grâce :", ["à son ombre, comparée à celle d'un bâton", "à une corde", "à un astrolabe", "à un sablier"], "Quand l'ombre d'un bâton égale sa hauteur, l'ombre de la pyramide égale aussi la sienne. L'anecdote est rapportée par Plutarque et Diogène Laërce."),
    qcm("Le nombre π vaut environ :", ["3,14159", "3,41", "2,718", "1,618"], "2,718 est e, et 1,618 le nombre d'or."),
    vf("Archimède a encadré π entre 3 + 10/71 et 3 + 1/7 avec des polygones à 96 côtés.", True, "Dans De la mesure du cercle, au IIIe siècle av. J.-C."),
    num("Combien d'arêtes a un cube ?", 12, "4 en haut, 4 en bas et 4 verticales."),
    qcm("Une géométrie où le postulat des parallèles d'Euclide est faux s'appelle :", ["non euclidienne", "fractale", "analytique", "projective"], "Lobatchevski et Bolyai la publient vers 1830. Einstein s'en servira pour la relativité générale."),
]

Q["math.infini"] = [
    qcm("La somme 1/2 + 1/4 + 1/8 + 1/16 + … (sans fin) vaut :", ["1", "l'infini", "2", "0,5"], "Chaque terme comble la moitié de ce qui manque pour atteindre 1."),
    vf("Il y a autant de nombres pairs que de nombres entiers.", True, "On les associe un à un : n avec 2n. Cantor a fondé sur cette idée la théorie des ensembles infinis."),
    qcm("Selon le paradoxe de Zénon, Achille ne rattrape jamais la tortue. L'erreur est de croire que :", ["une infinité d'étapes prend forcément un temps infini", "Achille court moins vite", "la tortue accélère", "la distance est infinie"], "Les durées des étapes forment une série dont la somme est finie."),
    vf("Cantor a montré que l'infini des nombres réels est plus grand que celui des entiers.", True, "Par son argument diagonal, publié en 1891 : on ne peut pas numéroter tous les réels."),
    num("Dans la suite de Fibonacci 1, 1, 2, 3, 5, 8, …, quel est le terme suivant ?", 13, "Chaque terme est la somme des deux précédents : 5 + 8 = 13."),
    qcm("Le quotient de deux termes consécutifs de la suite de Fibonacci tend vers :", ["le nombre d'or, environ 1,618", "π", "2", "e"], "8/5 = 1,6 ; 13/8 = 1,625 ; 21/13 ≈ 1,615…"),
    vf("La série 1 + 1/2 + 1/3 + 1/4 + … finit par dépasser n'importe quel nombre.", True, "La série harmonique diverge, très lentement : Nicole Oresme l'a démontré au XIVe siècle."),
    qcm("Le paradoxe de l'hôtel infini de Hilbert montre qu'un hôtel complet à une infinité de chambres :", ["peut quand même accueillir un nouveau client", "doit refuser tout client", "a forcément une chambre vide", "n'existe pas"], "On déplace chaque client de la chambre n à la chambre n + 1 : la chambre 1 se libère."),
    num("Dans la suite géométrique 3, 6, 12, 24, …, quel est le terme suivant ?", 48, "Chaque terme est multiplié par 2."),
    qcm("La notation ∞ pour l'infini a été introduite par :", ["John Wallis, en 1655", "Euclide", "Leibniz", "Cantor"], "Le mathématicien anglais l'utilise dans De sectionibus conicis."),
    vf("0,999… (avec une infinité de 9) est égal à 1.", True, "Leur différence serait plus petite que tout nombre positif : elle est nulle."),
    qcm("Le calcul infinitésimal a été inventé indépendamment par :", ["Newton et Leibniz", "Pascal et Fermat", "Euler et Gauss", "Descartes et Galilée"], "Leur querelle de priorité a empoisonné les relations entre mathématiciens anglais et continentaux pendant un siècle."),
]

# --- Mécanique -------------------------------------------------------------------

Q["phys.fluides"] = [
    qcm("La pression, c'est :", ["une force divisée par une surface", "une force multipliée par une surface", "une masse divisée par un volume", "une énergie par seconde"], "D'où l'intérêt des raquettes à neige : même poids, plus grande surface, moins de pression."),
    num("Environ combien de mètres de profondeur d'eau ajoutent la pression d'une atmosphère ?", 10, "Tous les 10 m environ, la pression augmente d'environ 1 bar.", tol=1, unite="m"),
    vf("Un objet coule s'il est plus dense que le liquide où on le pose.", True, "C'est le principe d'Archimède : la poussée vaut le poids du liquide déplacé."),
    qcm("Un bateau en acier flotte parce que :", ["sa coque déplace un volume d'eau qui pèse autant que lui", "l'acier est plus léger que l'eau", "le moteur le soutient", "l'eau salée l'empêche de couler"], "Rempli d'air, son volume total est bien moins dense que l'eau."),
    qcm("Torricelli invente le baromètre en 1643 avec :", ["un tube de mercure retourné sur une cuve", "un tube d'eau de 2 mètres", "un ballon gonflé", "une balance"], "La colonne se stabilise vers 76 cm : la pression de l'air la soutient."),
    vf("Au sommet d'une montagne, l'eau bout à moins de 100 °C.", True, "La pression y est plus faible. Au sommet de l'Everest, elle bout vers 70 °C."),
    qcm("En 1648, à la demande de Pascal, son beau-frère Florin Périer gravit le puy de Dôme pour montrer que :", ["la colonne de mercure baisse avec l'altitude", "l'eau bout plus vite en altitude", "la gravité diminue en montagne", "l'air est plus chaud en haut"], "La colonne avait baissé d'environ 8 cm : c'est le poids de l'air qui la soutient."),
    qcm("Selon l'effet Venturi, quand un fluide passe dans un rétrécissement :", ["il accélère et sa pression baisse", "il ralentit et sa pression monte", "il s'arrête", "sa température double"], "Ce principe sert dans les carburateurs et les débitmètres."),
    num("Quelle est la pression atmosphérique moyenne au niveau de la mer, en hectopascals ?", 1013, "Environ 1 013 hPa, soit 1 013 millibars.", tol=5, unite="hPa"),
    vf("Les hémisphères de Magdebourg n'ont pas pu être séparés par deux attelages de chevaux.", True, "En 1654, Otto von Guericke y avait fait le vide : la pression de l'air les plaquait l'une contre l'autre."),
    qcm("La presse hydraulique repose sur le fait que :", ["la pression se transmet intégralement dans un liquide", "les liquides se compriment facilement", "l'huile est plus légère que l'eau", "la chaleur dilate les liquides"], "Un petit piston poussé avec une petite force soulève un gros piston avec une grande force."),
    qcm("Un sous-marin plonge en :", ["remplissant ses ballasts d'eau", "chauffant sa coque", "tournant ses hélices vers le bas uniquement", "vidant ses réservoirs de carburant"], "Pour remonter, il chasse l'eau des ballasts avec de l'air comprimé."),
]

Q["phys.thermo"] = [
    qcm("La température mesure :", ["l'agitation moyenne des particules", "la quantité totale de chaleur", "la masse d'un corps", "la pression d'un gaz"], "Une baignoire tiède contient plus de chaleur qu'une étincelle, pourtant moins chaude."),
    num("À quelle température, en degrés Celsius, se trouve le zéro absolu ?", -273.15, "0 kelvin = -273,15 °C : les particules y ont l'agitation la plus faible possible.", tol=0.2, unite="°C"),
    vf("La chaleur passe spontanément d'un corps chaud vers un corps froid.", True, "C'est le deuxième principe de la thermodynamique, dans la formulation de Clausius."),
    qcm("Le premier principe de la thermodynamique dit que :", ["l'énergie se conserve", "l'entropie diminue", "la chaleur est une substance", "la température ne peut pas baisser"], "Elle change de forme, mais ne se crée ni ne se perd."),
    qcm("Au XVIIIe siècle, on pensait que la chaleur était un fluide invisible appelé :", ["le calorique", "le phlogistique", "l'éther", "le fluide électrique"], "Lavoisier lui-même le classe parmi les éléments. Rumford et Joule montreront que la chaleur est une forme d'énergie."),
    qcm("L'entropie mesure, en simplifiant :", ["le désordre ou le nombre de façons d'arranger un système", "la vitesse d'un gaz", "la chaleur d'un corps", "l'énergie de liaison"], "Dans un système isolé, elle ne peut qu'augmenter."),
    vf("Un moteur thermique peut transformer toute sa chaleur en travail.", False, "Sadi Carnot a montré en 1824 que le rendement est limité par l'écart de température entre la source chaude et la source froide."),
    num("Combien de minutes faut-il, environ, pour chauffer un litre d'eau de 20 à 100 °C avec une plaque de 1 000 W, sans pertes ?", 5.6, "Il faut 4 186 J par kilo et par degré : 4 186 × 80 ≈ 335 000 J, soit environ 335 s.", tol=0.6, unite="min"),
    qcm("Une bouteille d'eau oubliée au congélateur éclate parce que :", ["l'eau augmente de volume en gelant", "le verre rétrécit au froid", "l'air dissous explose", "la pression baisse"], "La glace est environ 9 % plus volumineuse que l'eau liquide."),
    qcm("La formule de l'entropie S = k log W est gravée :", ["sur la tombe de Ludwig Boltzmann à Vienne", "au fronton du Panthéon", "sur la médaille Nobel", "dans le Discours de la méthode"], "Elle relie l'entropie au nombre d'états microscopiques possibles."),
    vf("Un réfrigérateur fabrique du froid à partir de rien.", False, "Il pompe la chaleur de l'intérieur vers l'extérieur, en consommant de l'énergie. Son dos chauffe."),
    qcm("La conduction, la convection et le rayonnement sont :", ["les trois modes de transfert de la chaleur", "trois états de la matière", "trois types de moteurs", "trois échelles de température"], "Le Soleil nous chauffe par rayonnement : il n'y a pas de matière entre lui et nous."),
]

Q["phys.relativite"] = [
    num("Quelle est la vitesse de la lumière dans le vide, en km/s (arrondie) ?", 300000, "Exactement 299 792,458 km/s, par définition du mètre depuis 1983.", tol=1000, unite="km/s"),
    vf("Selon la relativité restreinte, une horloge en mouvement rapide bat plus lentement qu'une horloge au repos.", True, "C'est la dilatation du temps. Elle a été mesurée avec des horloges atomiques embarquées dans des avions en 1971."),
    qcm("Dans E = mc², c désigne :", ["la vitesse de la lumière", "la chaleur", "une constante de gravité", "la charge électrique"], "Un peu de masse contient énormément d'énergie, car c² est immense."),
    qcm("L'expérience de Michelson et Morley, en 1887, cherchait :", ["le mouvement de la Terre dans l'éther", "la masse de l'électron", "la vitesse du son", "la courbure de l'espace"], "Elle n'a rien trouvé. Ce résultat nul a préparé la relativité."),
    vf("Les GPS doivent corriger les effets de la relativité pour rester précis.", True, "Sans correction, l'erreur de position grandirait d'une dizaine de kilomètres par jour."),
    qcm("Pour la relativité générale (1915), la gravitation est :", ["une courbure de l'espace-temps par la masse et l'énergie", "une force à distance instantanée", "un effet magnétique", "une illusion d'optique"], "La matière dit à l'espace-temps comment se courber, et l'espace-temps dit à la matière comment bouger."),
    qcm("L'éclipse de 1919 observée par Eddington a confirmé que :", ["la lumière des étoiles est déviée par le Soleil", "la Lune est creuse", "le Soleil tourne sur lui-même", "la lumière est une onde"], "La déviation mesurée correspondait à la prédiction d'Einstein, le double de celle de Newton."),
    vf("Un objet qui a une masse peut atteindre la vitesse de la lumière s'il accélère assez longtemps.", False, "Il lui faudrait une énergie infinie : il s'en approche sans jamais l'atteindre."),
    qcm("Les ondes gravitationnelles ont été détectées directement pour la première fois en :", ["2015, par LIGO", "1919, par Eddington", "1905, par Einstein", "1969, pendant Apollo 11"], "Elles venaient de la fusion de deux trous noirs, à plus d'un milliard d'années-lumière."),
    qcm("En 1905, Einstein travaillait comme :", ["expert technique à l'Office des brevets de Berne", "professeur à Princeton", "assistant de Marie Curie", "ingénieur chez Siemens"], "Il n'obtient un poste universitaire qu'en 1909."),
    num("En combien de minutes, environ, la lumière du Soleil arrive-t-elle sur Terre ?", 8.3, "150 millions de km à 300 000 km/s : environ 500 secondes.", tol=0.5, unite="min"),
    qcm("Le paradoxe des jumeaux dit que le jumeau qui voyage à grande vitesse :", ["revient plus jeune que celui resté sur Terre", "revient plus vieux", "revient au même âge", "ne peut pas revenir"], "Ce n'est pas un vrai paradoxe : le voyageur change de référentiel en faisant demi-tour."),
]

Q["phys.quantique"] = [
    qcm("En 1900, Max Planck propose que l'énergie de la lumière soit échangée :", ["par petits paquets, les quanta", "de façon continue", "uniquement sous forme de chaleur", "à la vitesse du son"], "Une hypothèse de « désespoir », dira-t-il, pour expliquer le rayonnement des corps chauds."),
    vf("La lumière se comporte parfois comme une onde, parfois comme un flux de particules.", True, "C'est la dualité onde-particule. Les particules de lumière s'appellent photons."),
    qcm("L'effet photoélectrique, expliqué par Einstein en 1905, lui a valu :", ["le prix Nobel de physique 1921", "rien du tout", "le prix Nobel de chimie", "la médaille Fields"], "Pas la relativité, jugée trop controversée par le comité Nobel."),
    qcm("Le principe d'incertitude de Heisenberg dit qu'on ne peut pas connaître à la fois avec une précision parfaite :", ["la position et la vitesse d'une particule", "la masse et la charge", "la couleur et la forme", "l'âge et la taille"], "Ce n'est pas un défaut des instruments : c'est une propriété de la nature."),
    qcm("Le chat de Schrödinger (1935) devait montrer :", ["l'absurdité apparente d'appliquer la superposition quantique aux objets du quotidien", "que les chats voient dans le noir", "que la lumière est une onde", "la radioactivité des chats"], "Schrödinger critiquait l'interprétation de Copenhague, pas les félins."),
    vf("Dans l'expérience des fentes d'Young, des électrons envoyés un par un finissent par dessiner des franges d'interférence.", True, "Chaque électron semble passer par les deux fentes à la fois. L'expérience a été réalisée avec des électrons uniques en 1974 puis en 1989."),
    qcm("Selon le modèle de Bohr (1913), les électrons d'un atome :", ["occupent des niveaux d'énergie bien précis", "tournent n'importe où", "sont immobiles", "sont collés au noyau"], "En sautant d'un niveau à l'autre, ils émettent ou absorbent de la lumière de couleur précise."),
    qcm("« Dieu ne joue pas aux dés » est une objection d'Einstein :", ["au caractère probabiliste de la mécanique quantique", "à la relativité", "au Big Bang", "à la théorie de l'évolution"], "Dans une lettre à Max Born, en 1926. Bohr lui aurait répondu de cesser de dire à Dieu ce qu'il doit faire."),
    vf("L'effet tunnel permet à une particule de franchir une barrière qu'elle ne pourrait pas franchir classiquement.", True, "Il explique la radioactivité alpha et sert dans les microscopes à effet tunnel et les mémoires flash."),
    qcm("Lequel de ces appareils repose directement sur la physique quantique ?", ["le laser", "le levier", "la poulie", "la boussole"], "Le laser exploite l'émission stimulée, prédite par Einstein en 1917."),
    qcm("Au congrès Solvay de 1927, sur la célèbre photo, combien de participants avaient ou allaient recevoir un prix Nobel ?", ["17 sur 29", "2 sur 29", "29 sur 29", "aucun"], "Dont Marie Curie, seule femme présente, et deux fois lauréate."),
    vf("Un ordinateur quantique utilise des qubits, qui peuvent être dans une superposition de 0 et de 1.", True, "Pour certains problèmes, comme la factorisation, cela pourrait donner un avantage énorme."),
]

# --- Savoir (vivant) ----------------------------------------------------------------

Q["sci.corps"] = [
    num("Combien d'os compte le squelette d'un adulte ?", 206, "Un nouveau-né en a environ 300 : certains fusionnent en grandissant.", tol=0),
    qcm("William Harvey a démontré en 1628 que :", ["le sang circule en boucle, pompé par le cœur", "le sang est fabriqué par le foie et consommé par les organes", "le cœur sert à penser", "les artères contiennent de l'air"], "Il remplaçait la vision de Galien, admise depuis quatorze siècles."),
    qcm("Les échanges d'oxygène et de gaz carbonique dans les poumons se font dans :", ["les alvéoles pulmonaires", "la trachée", "le diaphragme", "les bronches principales"], "Environ 300 à 500 millions d'alvéoles, sur une surface d'environ 70 m²."),
    vf("Les globules rouges transportent l'oxygène grâce à l'hémoglobine.", True, "Le fer de l'hémoglobine fixe l'oxygène, et donne au sang sa couleur rouge."),
    qcm("Quel organe produit la bile, qui aide à digérer les graisses ?", ["le foie", "le pancréas", "l'estomac", "la rate"], "Elle est stockée dans la vésicule biliaire."),
    num("Au repos, combien de fois par minute bat environ le cœur d'un adulte ?", 70, "Entre 60 et 100 battements par minute en général.", tol=10),
    qcm("L'insuline, produite par le pancréas, sert à :", ["faire baisser le taux de sucre dans le sang", "digérer les protéines", "fabriquer les globules", "contracter les muscles"], "Sa découverte en 1921 par Banting et Best a transformé la vie des diabétiques."),
    vf("On n'utilise que 10 % de son cerveau.", False, "C'est un mythe : l'imagerie montre que toutes les zones servent, à des moments différents."),
    qcm("Le plus grand organe du corps humain est :", ["la peau", "le foie", "l'intestin", "le cerveau"], "Environ 2 m² et 4 kg chez l'adulte."),
    qcm("En 1543, Vésale publie la Fabrica, qui corrige Galien parce que :", ["Galien avait surtout disséqué des animaux, pas des humains", "Galien était aveugle", "Vésale avait inventé le microscope", "Galien niait l'existence des os"], "Vésale disséquait lui-même des corps humains, ce qui était rare."),
    num("Environ combien de litres de sang circulent dans le corps d'un adulte ?", 5, "Entre 4,5 et 6 litres selon la taille.", tol=1, unite="L"),
    qcm("Les reins servent principalement à :", ["filtrer le sang et produire l'urine", "digérer", "produire les hormones de croissance", "stocker le sucre"], "Ils filtrent environ 180 litres de sang par jour."),
]

Q["sci.immunite"] = [
    qcm("En 1796, Edward Jenner protège un enfant de la variole en lui inoculant :", ["la vaccine, une maladie de la vache", "du sang de variole chauffé", "un antibiotique", "un extrait de plante"], "Le mot « vaccin » vient du latin vacca, la vache."),
    vf("Les antibiotiques sont efficaces contre les virus.", False, "Ils agissent sur les bactéries. Contre un rhume ou la grippe, ils ne servent à rien et favorisent les résistances."),
    qcm("Un virus :", ["ne peut se reproduire qu'à l'intérieur d'une cellule", "est une petite bactérie", "fabrique sa propre énergie", "est toujours visible au microscope optique"], "Il détourne la machinerie de la cellule pour se copier."),
    qcm("Les anticorps sont produits par :", ["les lymphocytes B", "les globules rouges", "les plaquettes", "les neurones"], "Chaque anticorps reconnaît une forme précise, l'antigène."),
    vf("Ignace Semmelweis a fait chuter la mortalité des accouchées en imposant le lavage des mains.", True, "À Vienne en 1847, elle passe d'environ 10 % à environ 1 %. Ses collègues l'ont pourtant rejeté."),
    qcm("Le principe d'un vaccin est :", ["d'entraîner le système immunitaire sans provoquer la maladie", "de tuer directement les microbes", "de remplacer les globules blancs", "de soigner une maladie déjà déclarée"], "Le corps garde une mémoire de l'agresseur et réagit plus vite ensuite."),
    qcm("Robert Koch a identifié en 1882 l'agent :", ["de la tuberculose", "de la grippe", "du paludisme", "de la variole"], "Le bacille de Koch. Il en tire des postulats pour relier un microbe à une maladie."),
    num("En quelle année l'OMS a-t-elle déclaré la variole éradiquée ?", 1980, "Le dernier cas naturel date de 1977, en Somalie. C'est la seule maladie humaine éradiquée."),
    vf("L'immunité collective protège aussi les personnes qui ne peuvent pas être vaccinées.", True, "Quand assez de gens sont immunisés, le microbe circule mal."),
    qcm("La fièvre est en général :", ["une réaction de défense de l'organisme", "une maladie en elle-même", "causée par le froid", "toujours dangereuse"], "Elle gêne la multiplication de certains microbes et active les défenses."),
    qcm("Le paludisme est transmis par :", ["la piqûre de certains moustiques anophèles", "l'eau de boisson", "la toux", "les rats"], "Le parasite, un plasmodium, a été identifié par Alphonse Laveran en 1880."),
    qcm("Une bactérie résistante aux antibiotiques apparaît surtout parce que :", ["les antibiotiques sélectionnent les bactéries qui survivent", "les bactéries apprennent volontairement", "les antibiotiques créent les bactéries", "les vaccins les rendent résistantes"], "C'est la sélection naturelle, en accéléré. Fleming l'avait prédit dès 1945."),
]

Q["sci.ecologie"] = [
    qcm("Dans une chaîne alimentaire, les producteurs sont :", ["les plantes et les algues qui font la photosynthèse", "les herbivores", "les grands prédateurs", "les décomposeurs"], "Ils fabriquent la matière organique à partir de lumière, d'eau et de CO₂."),
    vf("Les décomposeurs, comme les champignons et les bactéries, recyclent la matière morte.", True, "Sans eux, les sols s'épuiseraient et les cadavres s'accumuleraient."),
    qcm("Le mot « écologie » a été forgé en 1866 par :", ["Ernst Haeckel", "Charles Darwin", "Rachel Carson", "Carl von Linné"], "Du grec oikos, la maison : la science de la maison du vivant."),
    num("Environ quel pourcentage de l'énergie passe d'un niveau de la chaîne alimentaire au suivant ?", 10, "La règle des 10 % : c'est pourquoi les grands prédateurs sont peu nombreux.", tol=5, unite="%"),
    qcm("La réintroduction des loups à Yellowstone en 1995 a :", ["modifié la végétation en changeant le comportement des cerfs", "fait disparaître tous les cerfs", "n'a eu aucun effet", "fait fuir les ours"], "C'est l'exemple classique d'une cascade trophique, même si son ampleur est débattue."),
    vf("Le gaz carbonique est un gaz à effet de serre.", True, "Tout comme la vapeur d'eau et le méthane. Svante Arrhenius en calcule l'effet dès 1896."),
    qcm("Une espèce clé de voûte est une espèce :", ["dont la disparition bouleverse tout l'écosystème", "très abondante", "en voie d'extinction", "introduite par l'humain"], "Exemple : l'étoile de mer Pisaster, étudiée par Robert Paine en 1966."),
    qcm("Dans Printemps silencieux (1962), Rachel Carson alerte sur :", ["les effets des pesticides comme le DDT", "le trou dans la couche d'ozone", "la déforestation amazonienne", "les marées noires"], "Le livre conduit à l'interdiction du DDT agricole aux États-Unis en 1972."),
    vf("Les récifs coralliens blanchissent quand l'eau devient trop chaude.", True, "Le corail expulse les algues qui le nourrissent et lui donnent sa couleur."),
    qcm("Le cycle du carbone décrit :", ["les échanges de carbone entre atmosphère, océans, roches et êtres vivants", "la rotation de la Terre", "la fabrication du diamant", "la vie des étoiles"], "Les océans absorbent environ un quart du CO₂ émis par les activités humaines."),
    qcm("Une espèce invasive est :", ["une espèce introduite qui prolifère au détriment des espèces locales", "une espèce qui migre chaque année", "un prédateur naturel", "une espèce disparue"], "Le lapin en Australie ou le frelon asiatique en France."),
    num("Les forêts couvrent environ quel pourcentage des terres émergées ?", 31, "Environ 31 %, selon la FAO.", tol=4, unite="%"),
]

Q["sci.biotech"] = [
    qcm("La PCR, inventée par Kary Mullis en 1983, permet :", ["de copier un morceau d'ADN des milliards de fois", "de lire les pensées", "de cloner un animal", "de fabriquer des protéines"], "Il dit avoir eu l'idée en conduisant de nuit en Californie. Elle lui vaut le Nobel de chimie 1993."),
    qcm("CRISPR-Cas9 est :", ["un outil pour couper et modifier l'ADN à un endroit précis", "un vaccin", "un antibiotique", "un microscope"], "Emmanuelle Charpentier et Jennifer Doudna reçoivent le Nobel de chimie 2020."),
    num("En quelle année est née la brebis Dolly, premier mammifère cloné à partir d'une cellule adulte ?", 1996, "Le 5 juillet 1996, en Écosse. Elle est présentée au public en février 1997."),
    vf("Un vaccin à ARN messager modifie l'ADN de la personne vaccinée.", False, "L'ARN reste hors du noyau et se dégrade en quelques jours, après avoir fait fabriquer une protéine."),
    qcm("Depuis 1982, l'insuline pour les diabétiques est surtout produite :", ["par des bactéries ou des levures génétiquement modifiées", "à partir de pancréas de porc uniquement", "par synthèse chimique pure", "à partir de plantes"], "Avant, on l'extrayait de pancréas d'animaux."),
    qcm("Le projet Génome humain, achevé en 2003, a révélé que nous avons environ :", ["20 000 gènes codant des protéines", "1 million de gènes", "500 gènes", "3 milliards de gènes"], "Bien moins que prévu. Le génome compte environ 3 milliards de paires de bases."),
    vf("Un OGM est un organisme dont le génome a été modifié par génie génétique.", True, "Par exemple un maïs qui produit une protéine insecticide."),
    qcm("Les empreintes génétiques, utilisées en justice, ont été mises au point en 1984 par :", ["Alec Jeffreys", "James Watson", "Rosalind Franklin", "Louis Pasteur"], "Elles ont servi pour la première fois dans une enquête criminelle en 1986-1987, en Angleterre."),
    qcm("Les cellules souches sont précieuses car elles :", ["peuvent se transformer en différents types de cellules", "ne meurent jamais", "contiennent plus d'ADN", "produisent de l'énergie"], "Shinya Yamanaka a montré en 2006 qu'on peut en fabriquer à partir de cellules adultes."),
    vf("Les vaccins à ARN messager ont été étudiés pendant des décennies avant la covid-19.", True, "Katalin Karikó et Drew Weissman reçoivent le Nobel 2023 pour leurs travaux des années 2000."),
    qcm("Les ciseaux de CRISPR viennent à l'origine :", ["d'un système de défense des bactéries contre les virus", "d'un champignon", "du venin de serpent", "d'un laboratoire militaire"], "Les bactéries gardent en mémoire des morceaux d'ADN de virus pour les reconnaître."),
    qcm("La conférence d'Asilomar, en 1975, a réuni des biologistes pour :", ["fixer des règles de prudence sur l'ADN recombinant", "lancer le séquençage du génome", "interdire les vaccins", "créer la première banque de sperme"], "Un rare cas de chercheurs qui se donnent eux-mêmes un moratoire."),
]

# --- Alchimie (chimie) ----------------------------------------------------------------

Q["chim.etats"] = [
    qcm("Le passage direct de l'état solide à l'état gazeux s'appelle :", ["la sublimation", "la fusion", "la condensation", "la vaporisation"], "La glace carbonique le fait à pression ordinaire."),
    num("À quelle température, en °C, l'eau pure bout-elle sous une pression d'une atmosphère ?", 100, "Ce point a servi à définir l'échelle Celsius.", unite="°C"),
    vf("Pendant qu'un glaçon fond, sa température reste à 0 °C.", True, "L'énergie reçue sert à casser la structure cristalline, pas à chauffer."),
    qcm("La loi de Boyle-Mariotte dit qu'à température constante, si on divise le volume d'un gaz par deux :", ["sa pression double", "sa pression est divisée par deux", "sa pression ne change pas", "il devient liquide"], "P × V reste constant. Boyle en 1662, Mariotte en 1676."),
    qcm("Le plasma, souvent appelé quatrième état de la matière, se trouve :", ["dans les étoiles et les éclairs", "dans les glaçons", "dans le sable", "dans l'huile"], "C'est un gaz si chaud que ses atomes ont perdu des électrons."),
    vf("Le verre est un liquide qui coule lentement : c'est pourquoi les vitraux anciens sont plus épais en bas.", False, "C'est un mythe : les vitriers posaient le côté le plus épais en bas. Le verre ne coulerait pas visiblement en des milliards d'années."),
    qcm("Quand on met du sel sur une route verglacée :", ["la température de fusion de la glace baisse", "le sel chauffe la route", "la glace devient du sel", "l'eau gèle plus vite"], "L'eau salée gèle à une température plus basse, jusqu'à environ -21 °C."),
    num("Un gaz parfait à 0 °C occupe environ combien de litres par mole sous une atmosphère ?", 22.4, "Le volume molaire, environ 22,4 L.", tol=0.3, unite="L"),
    qcm("La rosée sur l'herbe le matin vient :", ["de la condensation de la vapeur d'eau de l'air", "de la sueur des plantes", "de la pluie de la nuit", "de la fonte du givre uniquement"], "L'herbe refroidie la nuit fait passer la vapeur d'eau à l'état liquide."),
    vf("La glace flotte sur l'eau parce qu'elle est moins dense que l'eau liquide.", True, "C'est rare : la plupart des solides sont plus denses que leur liquide. Les lacs gèlent donc par le dessus."),
    qcm("L'azote liquide bout vers :", ["-196 °C", "0 °C", "-50 °C", "-273 °C"], "D'où la fumée froide quand on le verse à température ambiante."),
    qcm("Le mot « gaz » a été inventé au XVIIe siècle par :", ["Jan Baptist van Helmont, à partir du grec chaos", "Lavoisier", "Robert Boyle", "Aristote"], "Le chimiste flamand cherchait un nom pour ces « esprits » qui s'échappent des réactions."),
]

Q["chim.organique"] = [
    qcm("La chimie organique est la chimie :", ["des composés du carbone", "des organes", "des métaux", "des gaz rares"], "Le carbone peut former quatre liaisons et de longues chaînes : d'où l'immense variété des molécules."),
    vf("En 1828, Friedrich Wöhler fabrique de l'urée à partir de composés minéraux.", True, "Il ébranle l'idée qu'il faudrait une « force vitale » pour produire les molécules du vivant."),
    qcm("Le méthane a pour formule :", ["CH₄", "CO₂", "C₂H₆O", "H₂O"], "C'est le principal constituant du gaz naturel."),
    qcm("Un polymère, comme le plastique, est :", ["une très longue molécule formée de motifs répétés", "un mélange de métaux", "un gaz", "un atome lourd"], "Le polyéthylène est une chaîne de milliers de motifs –CH₂–CH₂–."),
    qcm("L'éthanol, l'alcool des boissons, est produit par :", ["la fermentation des sucres par des levures", "la distillation de l'eau", "la combustion du bois", "l'électrolyse"], "Pasteur a montré dans les années 1850 que la fermentation est l'œuvre d'êtres vivants."),
    vf("Le diamant et le graphite sont tous deux faits uniquement de carbone.", True, "Seul l'arrangement des atomes diffère : en tétraèdres pour le diamant, en feuillets pour le graphite."),
    qcm("Le nylon, inventé en 1935, est dû au chimiste :", ["Wallace Carothers, chez DuPont", "Alfred Nobel", "Leo Baekeland", "Marie Curie"], "Les bas nylon de 1940 déclenchent de véritables émeutes dans les magasins américains."),
    num("Combien de liaisons covalentes un atome de carbone forme-t-il en général ?", 4, "Il a quatre électrons de valence."),
    qcm("Les sucres, les graisses et les protéines sont des molécules :", ["organiques", "minérales", "radioactives", "métalliques"], "Elles sont construites autour du carbone."),
    qcm("La bakélite, premier plastique entièrement synthétique, date de :", ["1907", "1789", "1950", "1859"], "Leo Baekeland l'invente à New York, en cherchant un substitut à la gomme-laque."),
    vf("Les plastiques usuels se biodégradent en quelques mois dans la nature.", False, "La plupart mettent des décennies à des siècles à se fragmenter, en microplastiques."),
    qcm("Le pétrole est surtout composé :", ["d'hydrocarbures, molécules de carbone et d'hydrogène", "d'eau et de sel", "de métaux lourds", "d'oxygène"], "Il provient de matière organique enfouie et transformée pendant des millions d'années."),
]

Q["chim.quotidien"] = [
    qcm("La réaction de Maillard, qui dore la croûte du pain et la viande grillée, se produit entre :", ["des sucres et des acides aminés chauffés", "l'eau et le sel", "les graisses et l'oxygène uniquement", "le fer et le carbone"], "Décrite par le chimiste français Louis Camille Maillard en 1912."),
    qcm("Un savon nettoie car ses molécules ont :", ["une tête qui aime l'eau et une queue qui aime les graisses", "une acidité très forte", "un pouvoir magnétique", "une odeur qui chasse la saleté"], "Elles entourent les gouttes de graisse et les emportent dans l'eau."),
    vf("Mélanger de l'eau de Javel et un détartrant acide peut dégager du chlore toxique.", True, "Il ne faut jamais mélanger les produits ménagers."),
    qcm("Le bicarbonate de soude fait gonfler les gâteaux en libérant :", ["du gaz carbonique", "de l'oxygène", "de la vapeur de sel", "de l'hydrogène"], "Surtout au contact d'un acide et de la chaleur."),
    qcm("L'aspirine est dérivée d'une substance trouvée dans :", ["l'écorce de saule", "le pavot", "la quinine", "la menthe"], "Hippocrate recommandait déjà le saule. Bayer commercialise l'acide acétylsalicylique en 1899."),
    vf("La rouille est une oxydation du fer.", True, "Le fer réagit avec l'oxygène et l'eau pour former des oxydes hydratés."),
    qcm("Une pile électrique produit du courant grâce à :", ["une réaction d'oxydoréduction", "un aimant tournant", "la chaleur du soleil", "la pression de l'air"], "Des électrons passent du métal qui s'oxyde vers celui qui se réduit, à travers le circuit."),
    qcm("Les oignons font pleurer parce qu'en les coupant, on libère :", ["un composé soufré irritant qui se dissout dans les larmes", "du sel", "de l'acide citrique", "du gaz carbonique"], "Le syn-propanethial-S-oxyde, formé par une enzyme quand on abîme les cellules."),
    num("Quel est le pH de l'eau pure à 25 °C ?", 7, "Neutre : ni acide ni basique."),
    qcm("Le teflon des poêles a été découvert par accident en 1938 par :", ["Roy Plunkett, chez DuPont", "Thomas Edison", "Marie Curie", "Alexander Fleming"], "Une bouteille de gaz tétrafluoroéthylène s'était transformée en poudre blanche glissante."),
    vf("Le béton durcit en séchant, c'est-à-dire en perdant son eau.", False, "Il durcit par une réaction chimique avec l'eau, l'hydratation du ciment. Il durcit même sous l'eau."),
    qcm("Les feux d'artifice tirent leurs couleurs :", ["de sels métalliques, comme le strontium pour le rouge", "de colorants alimentaires", "de la poudre noire seule", "de la température de l'air"], "Le sodium donne le jaune, le cuivre le bleu, le baryum le vert."),
]

Q["chim.noyau"] = [
    qcm("Henri Becquerel découvre la radioactivité en 1896 grâce à :", ["des sels d'uranium qui voilent une plaque photographique dans un tiroir", "un éclair d'orage", "une explosion de laboratoire", "un tube à rayons X cassé"], "Le temps nuageux l'avait empêché de faire son expérience au soleil."),
    qcm("La demi-vie d'un élément radioactif, c'est :", ["le temps pour que la moitié de ses atomes se désintègrent", "la moitié de sa durée de vie totale", "son âge moyen", "le temps pour fondre"], "Après deux demi-vies, il en reste un quart, puis un huitième…"),
    num("Le carbone 14 a une demi-vie d'environ combien d'années ?", 5730, "D'où la datation des restes organiques jusqu'à environ 50 000 ans.", tol=100, unite="ans"),
    vf("Deux isotopes d'un même élément ont le même nombre de protons mais pas le même nombre de neutrons.", True, "Le carbone 12 et le carbone 14 ont 6 protons ; le second a 2 neutrons de plus."),
    qcm("La fission nucléaire, découverte en 1938, consiste à :", ["casser un noyau lourd en noyaux plus légers", "fusionner deux noyaux légers", "transformer un électron en proton", "brûler de l'uranium"], "Otto Hahn et Fritz Strassmann l'observent ; Lise Meitner et Otto Frisch l'expliquent."),
    qcm("Le Soleil produit son énergie par :", ["la fusion de l'hydrogène en hélium", "la fission de l'uranium", "la combustion du carbone", "des réactions chimiques"], "Environ 600 millions de tonnes d'hydrogène fusionnent chaque seconde."),
    vf("Marie Curie a découvert le polonium et le radium.", True, "En 1898, avec Pierre Curie. Le polonium porte le nom de la Pologne, son pays natal."),
    qcm("L'unité qui mesure le nombre de désintégrations par seconde s'appelle :", ["le becquerel", "le curie-watt", "le sievert", "le rad-ohm"], "Le sievert, lui, mesure l'effet des rayonnements sur le corps."),
    qcm("Les rayons alpha sont arrêtés par :", ["une feuille de papier", "un mur de plomb seulement", "rien", "un aimant"], "Les rayons bêta passent le papier mais pas l'aluminium ; les gamma demandent du plomb ou du béton."),
    vf("Les bananes sont légèrement radioactives à cause du potassium 40.", True, "C'est sans danger, mais assez pour amuser les physiciens, qui parlent de « dose équivalente banane »."),
    qcm("Dans les années 1920, des ouvrières américaines surnommées les « Radium Girls » ont été empoisonnées en :", ["affinant de la bouche leurs pinceaux de peinture au radium", "buvant de l'eau minérale", "travaillant dans une centrale", "manipulant des rayons X"], "Leur procès a fait progresser le droit du travail et la radioprotection."),
    num("En quelle année la première pile atomique, de Fermi, a-t-elle fonctionné à Chicago ?", 1942, "Le 2 décembre 1942, sous les gradins d'un stade de l'université de Chicago."),
]

# --- Cosmos ------------------------------------------------------------------------

Q["astro.observer"] = [
    qcm("Les saisons existent parce que :", ["l'axe de rotation de la Terre est incliné", "la Terre est plus proche du Soleil en été", "le Soleil change de puissance", "la Lune modifie la température"], "La Terre est même au plus près du Soleil début janvier, en plein hiver boréal."),
    num("Combien de constellations l'Union astronomique internationale reconnaît-elle officiellement ?", 88, "Leurs frontières ont été fixées en 1930."),
    qcm("Une année-lumière est :", ["une distance", "une durée", "une vitesse", "une luminosité"], "La distance parcourue par la lumière en un an : environ 9 460 milliards de km."),
    vf("L'étoile Polaire est l'étoile la plus brillante du ciel.", False, "C'est Sirius. La Polaire est utile parce qu'elle reste presque fixe au-dessus du pôle Nord."),
    qcm("Le télescope à miroir a été réalisé pour la première fois en 1668 par :", ["Isaac Newton", "Galilée", "Kepler", "Huygens"], "Un miroir évite les franges colorées des lentilles."),
    qcm("L'unité astronomique (ua) correspond :", ["à la distance moyenne entre la Terre et le Soleil", "au diamètre de la Galaxie", "à une année-lumière", "à la distance Terre-Lune"], "Environ 150 millions de km."),
    vf("On voit toujours la même face de la Lune depuis la Terre.", True, "Elle tourne sur elle-même en autant de temps qu'elle met à tourner autour de nous."),
    qcm("Les étoiles semblent tourner autour de nous dans le ciel nocturne parce que :", ["la Terre tourne sur elle-même", "les étoiles tournent autour de la Terre", "la Lune les entraîne", "l'atmosphère bouge"], "Foucault l'a montré avec son pendule en 1851."),
    qcm("Le télescope spatial James Webb, lancé en 2021, observe surtout :", ["dans l'infrarouge", "dans les rayons X", "en lumière ultraviolette seulement", "les ondes radio"], "L'infrarouge permet de voir les galaxies très lointaines, dont la lumière est décalée vers le rouge."),
    num("Combien de jours dure environ un cycle complet des phases de la Lune ?", 29.5, "Le mois synodique dure environ 29,5 jours.", tol=0.5, unite="jours"),
    qcm("Une étoile filante est :", ["un petit grain de poussière qui brûle en entrant dans l'atmosphère", "une étoile qui meurt", "une comète", "un satellite"], "Les Perséides d'août sont les débris de la comète Swift-Tuttle."),
    vf("Les couleurs des étoiles renseignent sur leur température.", True, "Les bleues sont les plus chaudes, les rouges les plus froides."),
]

Q["astro.espace"] = [
    num("En quelle année Spoutnik 1, premier satellite artificiel, a-t-il été lancé ?", 1957, "Le 4 octobre 1957, par l'URSS. Il émettait un simple bip radio."),
    qcm("Le premier humain dans l'espace est :", ["Youri Gagarine, en 1961", "Neil Armstrong, en 1969", "Alan Shepard, en 1961", "Valentina Terechkova, en 1963"], "Le 12 avril 1961, un tour de la Terre en 108 minutes."),
    qcm("Une fusée avance dans le vide en :", ["éjectant des gaz vers l'arrière, par action-réaction", "s'appuyant sur l'air", "utilisant des ailes", "étant tirée par la gravité"], "C'est la troisième loi de Newton. Elle fonctionne mieux encore sans air."),
    vf("Les astronautes flottent dans la Station spatiale internationale parce qu'il n'y a pas de gravité là-haut.", False, "La gravité y vaut encore environ 90 % de celle du sol. Ils sont en chute libre permanente autour de la Terre."),
    qcm("La première femme dans l'espace est :", ["Valentina Terechkova", "Sally Ride", "Claudie Haigneré", "Mae Jemison"], "En juin 1963, à bord de Vostok 6."),
    num("Combien d'humains ont marché sur la Lune ?", 12, "Six missions Apollo, de 1969 à 1972."),
    qcm("La sonde la plus lointaine envoyée par l'humanité est :", ["Voyager 1", "Pioneer 10", "New Horizons", "Hubble"], "Lancée en 1977, elle a quitté la bulle du Soleil en 2012 et emporte un disque d'or."),
    qcm("Les calculs de trajectoire de la mission de John Glenn en 1962 ont été vérifiés à sa demande par :", ["la mathématicienne Katherine Johnson", "Wernher von Braun", "Neil Armstrong", "Albert Einstein"], "Glenn se fiait plus à elle qu'aux ordinateurs IBM tout neufs."),
    vf("Konstantin Tsiolkovski a établi l'équation des fusées en 1903.", True, "Ce professeur russe rêvait déjà d'ascenseurs spatiaux et de colonies en orbite."),
    num("Combien de minutes a duré le vol de Youri Gagarine, le 12 avril 1961 ?", 108, "Une seule orbite, en 108 minutes. Il s'est éjecté avant l'atterrissage et a fini en parachute, ce que l'URSS a caché pendant des années.", tol=5, unite="min"),
    qcm("Le rover Perseverance explore depuis 2021 :", ["le cratère Jezero, sur Mars", "la face cachée de la Lune", "Europe, une lune de Jupiter", "Vénus"], "Il prélève des échantillons de roche qui pourraient garder des traces de vie ancienne."),
    num("À quelle vitesse, environ, en km/s, faut-il aller pour rester en orbite basse autour de la Terre ?", 7.8, "Environ 28 000 km/h : la Station fait le tour de la Terre en 90 minutes.", tol=0.5, unite="km/s"),
]

Q["astro.exoplanetes"] = [
    num("En quelle année Michel Mayor et Didier Queloz ont-ils découvert la première exoplanète autour d'une étoile semblable au Soleil ?", 1995, "51 Pegasi b, une géante gazeuse brûlante. Nobel de physique 2019."),
    qcm("La méthode des transits détecte une planète :", ["par la petite baisse de lumière quand elle passe devant son étoile", "en la photographiant directement", "par ses ondes radio", "par son odeur chimique"], "Le télescope Kepler en a trouvé des milliers ainsi."),
    qcm("La méthode des vitesses radiales détecte une planète :", ["par le léger va-et-vient de l'étoile, mesuré par effet Doppler", "par son ombre sur la Terre", "par la chaleur qu'elle émet", "par un écho radar"], "La planète et l'étoile tournent autour de leur centre de masse commun."),
    vf("On connaît aujourd'hui plus de 5 000 exoplanètes confirmées.", True, "Le cap des 5 000 a été franchi en 2022 selon la NASA."),
    qcm("La zone habitable d'une étoile est la région où :", ["l'eau peut rester liquide à la surface d'une planète", "la vie existe forcément", "il n'y a pas de radiations", "la gravité est la même que sur Terre"], "C'est une condition favorable, pas une garantie."),
    qcm("L'équation de Drake (1961) sert à :", ["estimer le nombre de civilisations communicantes dans la Galaxie", "calculer la masse des planètes", "mesurer la vitesse des étoiles", "dater l'Univers"], "Ses termes restent si incertains que les estimations vont de un à des millions."),
    qcm("« Mais où sont-ils donc ? » est la question attribuée à :", ["Enrico Fermi", "Carl Sagan", "Frank Drake", "Stephen Hawking"], "Lors d'un déjeuner à Los Alamos en 1950 : d'où le paradoxe de Fermi."),
    vf("Le signal « Wow! » capté en 1977 a été reçu une seule fois.", True, "Jerry Ehman avait entouré les données et écrit « Wow! » dans la marge. Il n'a jamais été réentendu."),
    qcm("Lequel de ces lieux du Système solaire est un candidat sérieux pour une vie microbienne, sous la glace ?", ["Europe, une lune de Jupiter", "Mercure", "le Soleil", "Io"], "Un océan d'eau salée existe sous sa croûte de glace, comme sous celle d'Encelade."),
    qcm("Une biosignature est :", ["un indice, comme certains gaz, qui pourrait trahir la vie", "la signature d'un astronome", "un type de planète", "un signal radio artificiel"], "L'oxygène et le méthane ensemble, par exemple, sont difficiles à maintenir sans vie."),
    num("Combien de planètes de taille terrestre compte le système TRAPPIST-1, annoncé en 2017 ?", 7, "Sept planètes, dont plusieurs dans la zone habitable d'une petite étoile froide."),
    vf("La planète Proxima b tourne autour de l'étoile la plus proche du Soleil.", True, "Proxima du Centaure, à environ 4,2 années-lumière."),
]

Q["astro.sombre"] = [
    qcm("Fritz Zwicky a soupçonné l'existence de la matière noire dès 1933 en observant :", ["que les galaxies de l'amas de Coma bougeaient trop vite", "une éclipse", "des trous noirs", "le fond diffus cosmologique"], "Il parlait de dunkle Materie : la masse visible ne suffisait pas à retenir l'amas."),
    qcm("Vera Rubin a montré dans les années 1970 que :", ["les étoiles au bord des galaxies tournent aussi vite que celles du centre", "les galaxies ne tournent pas", "l'Univers rétrécit", "les trous noirs n'existent pas"], "Il faut une masse invisible, en halo autour des galaxies."),
    vf("La matière noire n'émet ni n'absorbe de lumière.", True, "On ne la détecte que par ses effets gravitationnels."),
    num("Selon le modèle standard, environ quel pourcentage du contenu de l'Univers est de la matière ordinaire ?", 5, "Environ 5 %, contre 27 % de matière noire et 68 % d'énergie noire.", tol=1, unite="%"),
    qcm("L'énergie noire a été proposée pour expliquer :", ["l'accélération de l'expansion de l'Univers", "la rotation des galaxies", "la couleur des étoiles", "les marées"], "Découverte en 1998 avec des supernovae lointaines, Nobel 2011."),
    qcm("Les lentilles gravitationnelles permettent de cartographier la matière noire car :", ["sa masse dévie la lumière des galaxies situées derrière", "elle brille dans l'infrarouge", "elle fait du bruit radio", "elle est chaude"], "C'est une prédiction de la relativité générale."),
    vf("La matière noire est faite de trous noirs ordinaires, c'est prouvé.", False, "Sa nature reste inconnue. Les trous noirs classiques ne suffisent pas à l'expliquer."),
    qcm("L'amas de la Balle, observé en 2006, est un argument fort pour la matière noire parce que :", ["sa masse mesurée et son gaz visible ne sont pas au même endroit", "il est invisible", "il tourne à l'envers", "il est très jeune"], "Deux amas sont entrés en collision : le gaz a été freiné, pas la masse principale."),
    qcm("Einstein avait introduit une constante cosmologique pour :", ["obtenir un Univers statique", "expliquer la matière noire", "calculer la vitesse de la lumière", "décrire les atomes"], "Il l'abandonne après la découverte de l'expansion. Elle revient en 1998 pour décrire l'énergie noire."),
    num("Selon le satellite Planck, quel est l'âge de l'Univers, en milliards d'années ?", 13.8, "Environ 13,8 milliards d'années.", tol=0.2, unite="milliards d'années"),
    qcm("Les WIMP sont :", ["des particules hypothétiques candidates à la matière noire", "des petites étoiles", "des satellites", "des galaxies naines"], "Weakly Interacting Massive Particles. Malgré des décennies de recherche, aucune n'a été détectée."),
    vf("L'expansion de l'Univers signifie que les galaxies s'éloignent les unes des autres à grande échelle.", True, "Plus elles sont loin, plus elles s'éloignent vite : c'est la loi de Hubble-Lemaître."),
]

# --- Étincelle -----------------------------------------------------------------------

Q["elec.em"] = [
    qcm("James Clerk Maxwell a montré dans les années 1860 que la lumière est :", ["une onde électromagnétique", "un flux de particules de feu", "un son très aigu", "un fluide"], "Ses équations unifient électricité, magnétisme et lumière."),
    qcm("Heinrich Hertz a produit et détecté des ondes radio en :", ["1887", "1750", "1920", "1969"], "Il pensait que ces ondes n'auraient aucune application pratique."),
    vf("Les ondes radio, la lumière visible et les rayons X sont de même nature.", True, "Ce sont toutes des ondes électromagnétiques, de longueurs d'onde différentes."),
    qcm("Parmi ces ondes, laquelle a la longueur d'onde la plus courte ?", ["les rayons gamma", "les ondes radio", "les micro-ondes", "l'infrarouge"], "Plus la longueur d'onde est courte, plus l'énergie transportée est grande."),
    qcm("Le four à micro-ondes a été inventé après que Percy Spencer a remarqué que :", ["une barre chocolatée avait fondu dans sa poche près d'un radar", "son café restait chaud", "son repas était cru", "une ampoule s'allumait seule"], "Spencer travaillait chez Raytheon en 1945."),
    vf("Wilhelm Röntgen a reçu le premier prix Nobel de physique, en 1901, pour les rayons X.", True, "Il avait découvert ces rayons en 1895 et a refusé de les breveter."),
    num("Quelle est, environ, la plus petite longueur d'onde visible par l'œil humain, en nanomètres ?", 400, "Le visible va d'environ 400 nm (violet) à 700 nm (rouge).", tol=30, unite="nm"),
    qcm("Guglielmo Marconi a réalisé en 1901 :", ["la première transmission radio à travers l'Atlantique", "le premier téléphone", "la première télévision", "le premier radar"], "Un simple « S » en morse, entre la Cornouailles et Terre-Neuve."),
    qcm("Le Wi-Fi utilise principalement :", ["des micro-ondes", "des rayons X", "de la lumière visible", "des ultrasons"], "Autour de 2,4 et 5 GHz, comme les fours à micro-ondes pour la première bande."),
    vf("Les ondes électromagnétiques ont besoin d'un milieu matériel pour se propager.", False, "Elles traversent le vide, contrairement au son. C'est ainsi que la lumière des étoiles nous arrive."),
    qcm("Les coups de soleil sont causés surtout par :", ["les ultraviolets", "l'infrarouge", "les ondes radio", "la lumière verte"], "Les UV ont assez d'énergie pour abîmer l'ADN des cellules de la peau."),
    qcm("Le radar fonctionne en :", ["envoyant des ondes radio et en écoutant leur écho", "écoutant les bruits des avions", "mesurant la chaleur", "détectant les champs magnétiques"], "Développé intensément pendant la Seconde Guerre mondiale."),
]

Q["elec.electronique"] = [
    qcm("Le transistor a été inventé en 1947 aux laboratoires Bell par :", ["John Bardeen, Walter Brattain et William Shockley", "Thomas Edison", "Alan Turing", "Nikola Tesla"], "Nobel de physique 1956. Bardeen en recevra un second en 1972."),
    qcm("Une diode laisse passer le courant :", ["dans un seul sens", "dans les deux sens", "jamais", "seulement en alternatif"], "Elle sert notamment à transformer l'alternatif en continu."),
    vf("Les LED sont des diodes qui émettent de la lumière.", True, "Light-Emitting Diode. La LED bleue, mise au point dans les années 1990, a valu le Nobel 2014."),
    qcm("Un condensateur sert à :", ["stocker temporairement des charges électriques", "produire de la lumière", "mesurer la température", "transformer le courant en son"], "Le flash d'un appareil photo se décharge depuis un condensateur."),
    qcm("Le matériau de base de la plupart des puces électroniques est :", ["le silicium", "le cuivre", "l'or", "le fer"], "D'où le nom de Silicon Valley."),
    vf("Un semi-conducteur conduit mieux l'électricité qu'un métal.", False, "Il conduit moins bien, mais on peut contrôler sa conduction, ce qui le rend si utile."),
    qcm("Le circuit intégré, réunissant plusieurs composants sur une même puce, a été inventé en 1958-1959 par :", ["Jack Kilby et Robert Noyce", "Steve Jobs et Steve Wozniak", "Bill Gates", "John von Neumann"], "Kilby chez Texas Instruments, Noyce chez Fairchild, chacun de son côté."),
    qcm("Un transistor peut servir :", ["d'interrupteur ou d'amplificateur", "uniquement de pile", "de résistance chauffante", "d'aimant"], "Dans les ordinateurs, il sert d'interrupteur ultra-rapide."),
    num("Un processeur moderne compte environ combien de milliards de transistors (ordre de grandeur pour un grand processeur de 2023) ?", 100, "De quelques dizaines à plus de cent milliards selon les puces.", tol=90, unite="milliards"),
    qcm("Un tube à vide, ancêtre du transistor, :", ["chauffait, consommait beaucoup et grillait souvent", "était plus petit qu'un transistor", "ne servait que pour l'éclairage", "était fait de silicium"], "L'ENIAC en comptait plus de 17 000."),
    vf("Un circuit imprimé relie les composants par des pistes de cuivre.", True, "Gravées sur une plaque isolante."),
    qcm("Un capteur photo numérique transforme :", ["la lumière en signal électrique", "le son en lumière", "la chaleur en courant uniquement", "le courant en lumière"], "Chaque pixel accumule des charges proportionnelles à la lumière reçue."),
]

Q["elec.energies"] = [
    qcm("Le courant du réseau électrique domestique en France est :", ["alternatif, à 50 hertz", "continu", "alternatif, à 60 hertz", "à 1 000 hertz"], "Il change de sens cent fois par seconde. Les États-Unis utilisent 60 Hz."),
    qcm("La « guerre des courants » à la fin du XIXe siècle opposait :", ["Edison, partisan du continu, et Westinghouse avec Tesla, partisans de l'alternatif", "Volta et Galvani", "Ampère et Faraday", "Siemens et Philips"], "L'alternatif l'emporte car il se transporte mieux grâce aux transformateurs."),
    vf("Un transformateur ne fonctionne qu'avec du courant alternatif.", True, "Il repose sur l'induction, qui demande un champ magnétique variable."),
    qcm("On transporte l'électricité sous très haute tension parce que :", ["cela réduit les pertes par effet Joule dans les câbles", "c'est plus joli", "cela va plus vite", "les câbles sont plus légers"], "Pour une même puissance, plus de tension veut dire moins d'intensité, donc moins de pertes."),
    qcm("Une éolienne produit de l'électricité grâce à :", ["un alternateur entraîné par les pales", "des panneaux solaires", "la combustion du vent", "une réaction chimique"], "Comme dans presque toutes les centrales : un aimant qui tourne près de bobines."),
    vf("Les panneaux photovoltaïques transforment directement la lumière en électricité.", True, "Par l'effet photovoltaïque, observé par Edmond Becquerel en 1839, à 19 ans."),
    num("Environ quelle part de l'électricité française a été produite par le nucléaire en 2023, en pourcentage ?", 65, "Environ 65 % selon RTE, la plus forte proportion au monde.", tol=7, unite="%"),
    qcm("La plus ancienne grande forme d'électricité renouvelable est :", ["l'hydroélectricité", "le solaire", "l'éolien", "la géothermie"], "Les barrages fournissent encore la première source renouvelable d'électricité dans le monde."),
    qcm("Le réseau doit à chaque instant :", ["équilibrer production et consommation", "stocker toute l'électricité produite", "produire deux fois plus que nécessaire", "s'arrêter la nuit"], "Sinon la fréquence dérive et des coupures se déclenchent."),
    vf("Une batterie lithium-ion stocke l'énergie sous forme chimique.", True, "Prix Nobel de chimie 2019 pour Goodenough, Whittingham et Yoshino."),
    qcm("Une station de transfert d'énergie par pompage (STEP) stocke l'énergie en :", ["remontant de l'eau dans un réservoir en hauteur", "comprimant de l'air dans des pneus", "chauffant du sable", "chargeant des piles géantes"], "Elle la turbine plus tard, quand la demande est forte."),
    qcm("La première centrale électrique publique d'Edison, en 1882, se trouvait :", ["à Pearl Street, à New York", "à Paris", "à Londres", "à Berlin"], "Elle alimentait quelques centaines de clients en courant continu."),
]

Q["elec.numerique"] = [
    num("Combien vaut le nombre binaire 1011 en décimal ?", 11, "8 + 0 + 2 + 1 = 11."),
    qcm("Un octet est formé de :", ["8 bits", "2 bits", "10 bits", "1 024 bits"], "Un octet peut prendre 256 valeurs différentes."),
    qcm("La porte logique ET (AND) donne 1 seulement si :", ["ses deux entrées valent 1", "une seule entrée vaut 1", "ses deux entrées valent 0", "jamais"], "Claude Shannon a montré en 1937 que des circuits de relais peuvent réaliser toute l'algèbre de Boole."),
    vf("La machine analytique de Charles Babbage, conçue au XIXe siècle, a été entièrement construite de son vivant.", False, "Elle est restée à l'état de plans. Ada Lovelace en a pourtant écrit le premier programme publié, en 1843."),
    qcm("Le premier « bug » informatique documenté, en 1947, était :", ["un papillon de nuit coincé dans un relais du Harvard Mark II", "une erreur de calcul de Turing", "un virus", "une panne de courant"], "L'équipe de Grace Hopper l'a collé dans le cahier de bord avec la mention « premier cas réel de bug trouvé »."),
    qcm("La loi de Moore (1965) prévoit que :", ["le nombre de transistors sur une puce double à intervalles réguliers", "les ordinateurs coûtent deux fois plus chaque année", "la vitesse de la lumière limite les processeurs", "les puces rétrécissent de moitié chaque mois"], "Gordon Moore parlait d'abord d'un doublement chaque année, puis tous les deux ans."),
    vf("Dans l'architecture de von Neumann, le programme et les données sont stockés dans la même mémoire.", True, "Décrite en 1945, elle reste la base de presque tous les ordinateurs."),
    qcm("La mémoire vive (RAM) :", ["s'efface quand on éteint l'ordinateur", "garde les données sans électricité", "est le processeur", "stocke le système pour toujours"], "Les disques et la mémoire flash, eux, conservent les données."),
    num("Combien de valeurs différentes peut-on coder avec 3 bits ?", 8, "2 × 2 × 2 = 8, de 000 à 111."),
    qcm("Colossus, construit en 1943-1944 à Bletchley Park, servait à :", ["casser des chiffrements allemands", "calculer des trajectoires lunaires", "gérer des comptes bancaires", "jouer aux échecs"], "Il a été gardé secret jusque dans les années 1970."),
    qcm("Le mot « logiciel » a été proposé en français en 1969 pour remplacer :", ["software", "hardware", "computer", "bug"], "Le mot « ordinateur », lui, date de 1955 : proposé par le latiniste Jacques Perret à IBM France."),
    vf("Un ordinateur ne manipule au fond que des 0 et des 1.", True, "Textes, images et sons sont tous codés en binaire."),
]

# Une date de la frise par compétence : (id, année, titre, phrase, stat, compétence, détail, source)
DATES = [
    ("viete", 1591, "L'algèbre des lettres", "François Viète publie un calcul où les lettres remplacent les nombres.", "logique", "math.algebre",
     "Son Introduction à l'art analytique note les inconnues par des voyelles et les quantités connues par des consonnes. Viète, conseiller d'Henri IV, cassait aussi les codes secrets espagnols : Philippe II l'accusa de sorcellerie auprès du pape.",
     "François Viète, In artem analyticem isagoge, 1591"),
    ("nightingale", 1858, "Les diagrammes de Nightingale", "Florence Nightingale montre en graphiques que les soldats meurent surtout de maladies évitables.", "logique", "math.statistiques",
     "Ses diagrammes polaires, présentés au gouvernement britannique, contribuent à réformer l'hygiène des hôpitaux militaires. Elle est la première femme élue à la Royal Statistical Society, en 1858.",
     "Florence Nightingale, Notes on Matters Affecting the Health… of the British Army, 1858"),
    ("geometries-non-euclidiennes", 1829, "Les géométries non euclidiennes", "Lobatchevski publie une géométrie où les parallèles se comportent autrement.", "logique", "math.geometrie",
     "Bolyai fait la même découverte de son côté. Gauss y avait pensé sans publier, de peur des « cris des Béotiens », écrit-il.",
     "Nikolaï Lobatchevski, Messager de Kazan, 1829"),
    ("cantor", 1874, "Cantor compte les infinis", "Georg Cantor montre qu'on ne peut pas numéroter tous les nombres réels.", "logique", "math.infini",
     "Son travail choque une partie des mathématiciens, dont Kronecker. Hilbert dira plus tard : « Nul ne nous chassera du paradis que Cantor a créé pour nous. »",
     "Georg Cantor, Journal de Crelle, 1874 ; David Hilbert, « Über das Unendliche », 1926"),
    ("puy-de-dome", 1648, "L'expérience du puy de Dôme", "À la demande de Pascal, Florin Périer montre que l'air a un poids qui diminue avec l'altitude.", "mecanique", "phys.fluides",
     "La colonne de mercure mesure environ 71 cm au sommet contre 79 cm à Clermont : la nature n'a pas « horreur du vide », c'est l'air qui pousse.",
     "Blaise Pascal, Récit de la grande expérience de l'équilibre des liqueurs, 1648"),
    ("carnot-clausius", 1865, "L'entropie", "Rudolf Clausius invente le mot entropie et énonce que celle de l'Univers tend vers un maximum.", "mecanique", "phys.thermo",
     "Il forge le mot sur le grec tropê, la transformation, pour qu'il ressemble à « énergie ».",
     "Rudolf Clausius, Annalen der Physik, 1865"),
    ("eclipse-1919", 1919, "L'éclipse d'Eddington", "Des photos d'éclipse confirment que le Soleil dévie la lumière des étoiles.", "mecanique", "phys.relativite",
     "Les expéditions à Sobral, au Brésil, et sur l'île de Principe rendent Einstein célèbre du jour au lendemain. Le Times titre sur une « révolution dans la science ».",
     "Dyson, Eddington et Davidson, Philosophical Transactions A, 1920"),
    ("planck-quanta", 1900, "Les quanta de Planck", "Max Planck suppose qu'un oscillateur ne change d'énergie que par petits sauts.", "mecanique", "phys.quantique",
     "Il présente son idée le 14 décembre 1900 à la Société allemande de physique. Il n'y croit qu'à moitié : c'est un « acte de désespoir », écrira-t-il.",
     "Max Planck, Verhandlungen der Deutschen Physikalischen Gesellschaft, 1900"),
    ("harvey", 1628, "La circulation du sang", "William Harvey démontre que le cœur fait circuler le sang en boucle.", "savoir", "sci.corps",
     "Il calcule que le cœur pompe en une heure plus de sang que le corps n'en contient : il doit donc revenir. Sa théorie est longtemps moquée.",
     "William Harvey, Exercitatio anatomica de motu cordis et sanguinis, 1628"),
    ("semmelweis", 1847, "Le lavage des mains", "À Vienne, Ignace Semmelweis impose aux médecins de se laver les mains au chlore.", "savoir", "sci.immunite",
     "La mortalité des accouchées de son service chute d'environ 10 % à environ 1 %. Ses collègues, vexés d'être accusés de transmettre la mort, le rejettent. Il meurt en asile en 1865, avant que Pasteur et Lister lui donnent raison.",
     "Ignác Semmelweis, Die Ätiologie, der Begriff und die Prophylaxis des Kindbettfiebers, 1861"),
    ("haeckel-ecologie", 1866, "Le mot écologie", "Ernst Haeckel nomme la science des relations des êtres vivants avec leur milieu.", "savoir", "sci.ecologie",
     "Haeckel, grand diffuseur de Darwin en Allemagne, était aussi un dessinateur prodigieux : ses Formes artistiques de la nature ont inspiré l'Art nouveau.",
     "Ernst Haeckel, Generelle Morphologie der Organismen, 1866"),
    ("crispr", 2012, "CRISPR-Cas9", "Charpentier et Doudna décrivent des ciseaux moléculaires programmables.", "savoir", "sci.biotech",
     "Leur article de juin 2012 dans Science lance une révolution dans la modification du génome. Nobel de chimie 2020, le premier en sciences attribué à deux femmes seules.",
     "Jinek et al., Science, 2012"),
    ("boyle", 1662, "La loi de Boyle", "Robert Boyle montre que le volume d'un gaz varie à l'inverse de sa pression.", "alchimie", "chim.etats",
     "Son assistant Robert Hooke construit la pompe à air. Edme Mariotte publie la même loi en France en 1676, d'où le double nom.",
     "Robert Boyle, New Experiments Physico-Mechanicall, 2e éd., 1662"),
    ("wohler", 1828, "La synthèse de l'urée", "Friedrich Wöhler fabrique une molécule du vivant à partir de composés minéraux.", "alchimie", "chim.organique",
     "Il écrit à Berzelius qu'il peut faire de l'urée « sans avoir besoin de reins, ni d'homme ni de chien ». La frontière entre chimie du vivant et chimie minérale commence à tomber.",
     "Friedrich Wöhler, Annalen der Physik und Chemie, 1828"),
    ("maillard", 1912, "La réaction de Maillard", "Louis Camille Maillard décrit la réaction qui dore le pain et la viande.", "alchimie", "chim.quotidien",
     "Ce médecin et chimiste lorrain étudiait la formation des protéines. Sa réaction ne devient célèbre qu'avec l'industrie alimentaire, des décennies plus tard.",
     "Louis Camille Maillard, Comptes rendus de l'Académie des sciences, 1912"),
    ("becquerel", 1896, "La radioactivité", "Henri Becquerel découvre que l'uranium émet un rayonnement de lui-même.", "alchimie", "chim.noyau",
     "Il range des sels d'uranium avec une plaque photographique un jour sans soleil : la plaque est voilée quand même. Nobel de physique 1903, partagé avec les Curie.",
     "Henri Becquerel, Comptes rendus de l'Académie des sciences, 1896"),
    ("telescope-newton", 1668, "Le télescope de Newton", "Isaac Newton construit le premier télescope à miroir utilisable.", "cosmos", "astro.observer",
     "Long d'environ 15 cm, il grossit autant qu'une lunette d'un mètre. Il le présente à la Royal Society, qui l'élit membre en 1672.",
     "Isaac Newton, lettre à la Royal Society, 1672"),
    ("spoutnik", 1957, "Spoutnik", "L'URSS place le premier satellite artificiel en orbite.", "cosmos", "astro.espace",
     "Une sphère de 58 cm et 84 kg qui émet un bip audible par les radioamateurs du monde entier. Le choc pousse les États-Unis à créer la NASA en 1958.",
     "NASA, Sputnik and the Origins of the Space Age"),
    ("51-pegasi", 1995, "51 Pegasi b", "Mayor et Queloz découvrent la première exoplanète autour d'une étoile semblable au Soleil.", "cosmos", "astro.exoplanetes",
     "Une géante gazeuse qui fait le tour de son étoile en quatre jours : personne ne pensait que de tels mondes existaient. Nobel de physique 2019.",
     "Mayor et Queloz, Nature, 1995"),
    ("vera-rubin", 1970, "Les galaxies de Vera Rubin", "Vera Rubin mesure que les bords des galaxies tournent trop vite.", "cosmos", "astro.sombre",
     "Avec Kent Ford, elle observe Andromède. Ses mesures font de la matière noire une évidence pour la plupart des astronomes. L'observatoire Vera C. Rubin porte son nom.",
     "Rubin et Ford, Astrophysical Journal, 1970"),
    ("hertz", 1887, "Les ondes de Hertz", "Heinrich Hertz produit et détecte des ondes radio en laboratoire.", "etincelle", "elec.em",
     "Il confirme Maxwell. Interrogé sur l'utilité de sa découverte, il aurait répondu : « Aucune. » L'unité de fréquence porte son nom.",
     "Heinrich Hertz, Annalen der Physik, 1888"),
    ("transistor", 1947, "Le transistor", "Aux laboratoires Bell, Bardeen et Brattain font fonctionner le premier transistor.", "etincelle", "elec.electronique",
     "Le 16 décembre 1947, un morceau de germanium et une pointe d'or amplifient un signal. William Shockley, leur chef, améliore le dispositif dans la foulée.",
     "Nobel de physique 1956, nobelprize.org"),
    ("pearl-street", 1882, "La centrale de Pearl Street", "Edison ouvre à New York, à Pearl Street, sa première centrale électrique commerciale.", "etincelle", "elec.energies",
     "Le 4 septembre 1882, elle alimente environ 400 lampes chez 85 clients du quartier de Wall Street, en courant continu.",
     "Robert Friedel et Paul Israel, Edison's Electric Light, 1986"),
    ("shannon", 1937, "Le mémoire de Shannon", "Claude Shannon montre que des circuits de relais peuvent faire de la logique.", "etincelle", "elec.numerique",
     "Son mémoire de master au MIT, à 21 ans, relie l'algèbre de Boole aux circuits. On l'a appelé le mémoire le plus important du siècle.",
     "Claude Shannon, « A Symbolic Analysis of Relay and Switching Circuits », 1938"),
]
