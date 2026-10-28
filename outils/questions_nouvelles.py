"""Questions des compétences ajoutées en v2 : génétique, chimie, astronomie, électricité.

Même convention que contenu.py : pour un QCM, la bonne réponse est écrite en premier.
"""
from aides import num, qcm, vf

Q = {}

# --- Savoir : sciences du vivant ---------------------------------------------

Q["sci.genetique"] = [
    qcm("Qui a découvert les lois de l'hérédité en croisant des pois ?", ["Gregor Mendel", "Charles Darwin", "Louis Pasteur", "Thomas Morgan"], "Ses résultats, publiés en 1866, sont restés ignorés jusqu'à leur redécouverte en 1900."),
    qcm("Un gène est :", ["une portion d'ADN qui porte l'information pour fabriquer une molécule, souvent une protéine", "un chromosome entier", "une cellule sexuelle", "un organite"], "Un chromosome porte des centaines à des milliers de gènes."),
    vf("Un allèle récessif peut rester caché pendant plusieurs générations.", True, "Il ne s'exprime que chez les individus qui en ont deux copies. Les porteurs d'une seule copie le transmettent sans le montrer."),
    qcm("Deux parents Aa (A dominant, a récessif). Quelle proportion de leurs enfants montre le caractère récessif ?", ["1/4", "1/2", "3/4", "0"], "Le tableau donne AA, Aa, aA et aa. Seul aa montre le caractère récessif : une case sur quatre."),
    qcm("Qui a publié en 1953 la structure en double hélice de l'ADN ?", ["James Watson et Francis Crick", "Linus Pauling", "Gregor Mendel", "Erwin Chargaff"], "Ils se sont appuyés sur le cliché 51, une image de diffraction obtenue dans le laboratoire de Rosalind Franklin."),
    qcm("Dans l'ADN, l'adénine (A) s'apparie avec :", ["la thymine (T)", "la guanine (G)", "la cytosine (C)", "l'uracile (U)"], "A va avec T, G va avec C. C'est ce qui permet de copier un brin à partir de l'autre."),
    num("Combien de paires de chromosomes compte une cellule humaine ordinaire ?", 23, "46 chromosomes au total, rangés en 23 paires."),
    vf("Les vrais jumeaux ont presque exactement le même ADN.", True, "Ils viennent du même œuf fécondé. Seules quelques mutations survenues après la séparation les distinguent."),
    qcm("Chez l'humain, le sexe biologique dépend principalement :", ["des chromosomes X et Y", "de la température pendant la grossesse", "de l'alimentation de la mère", "du groupe sanguin"], "XX ou XY dans la plupart des cas. Chez beaucoup de tortues, c'est bien la température d'incubation qui décide."),
    qcm("Une mutation est :", ["une modification de la séquence d'ADN", "toujours mortelle", "un changement que l'organisme choisit", "un type de cellule"], "La plupart sont neutres, certaines sont nuisibles, quelques-unes avantageuses."),
    qcm("Le génome humain compte environ combien de gènes codant des protéines ?", ["20 000", "2 000", "200 000", "2 millions"], "Bien moins que les 100 000 attendus avant le séquençage. Le riz en a davantage que nous."),
    qcm("L'outil CRISPR-Cas9, prix Nobel de chimie 2020, sert à :", ["couper et modifier l'ADN à un endroit précis", "lire l'ADN plus vite", "cloner un animal entier", "voir les cellules au microscope"], "Emmanuelle Charpentier et Jennifer Doudna ont transformé un système de défense des bactéries en ciseaux moléculaires."),
]

# --- Alchimie : chimie ---------------------------------------------------------

Q["chim.liaisons"] = [
    qcm("Dans une liaison covalente, deux atomes :", ["mettent en commun des électrons", "échangent des protons", "fusionnent leurs noyaux", "se repoussent"], "La paire d'électrons partagée appartient aux deux atomes à la fois."),
    qcm("Le sel de table (NaCl) tient grâce à :", ["l'attraction entre ions Na⁺ et Cl⁻ (liaison ionique)", "des liaisons covalentes", "la gravité", "l'eau qu'il contient"], "Le sodium cède un électron au chlore. Les deux ions de charges opposées s'attirent."),
    vf("La glace flotte sur l'eau liquide parce qu'elle est moins dense.", True, "En gelant, les liaisons hydrogène rangent les molécules en un réseau ouvert : la glace prend environ 9 % de volume en plus."),
    num("Combien de liaisons covalentes forme habituellement un atome de carbone ?", 4, "Quatre électrons de valence, donc quatre liaisons. C'est ce qui permet les longues chaînes de la chimie du vivant."),
    qcm("Les gaz nobles (hélium, néon, argon) réagissent très peu car :", ["leur couche externe d'électrons est complète", "ils sont trop lourds", "ils n'ont pas de noyau", "ils sont radioactifs"], "Ils n'ont rien à gagner à partager ou échanger des électrons."),
    qcm("Quelle molécule a pour formule CH₄ ?", ["le méthane", "l'éthanol", "l'ammoniac", "le dioxyde de carbone"], "Un carbone entouré de quatre hydrogènes. C'est le principal composant du gaz naturel."),
    qcm("L'électronégativité d'un atome, c'est :", ["sa tendance à attirer vers lui les électrons d'une liaison", "la charge d'un électron", "sa masse", "la vitesse de ses électrons"], "Le fluor est l'élément le plus électronégatif. Dans l'eau, l'oxygène attire les électrons plus que l'hydrogène."),
    vf("Le diamant est très dur parce que chaque atome de carbone y est lié solidement à quatre voisins.", True, "Ce réseau rigide en trois dimensions le rend très dur. Dans le graphite, les atomes forment des feuillets qui glissent."),
    qcm("Pourquoi l'huile et l'eau ne se mélangent-elles pas ?", ["l'eau est polaire, l'huile ne l'est pas", "l'huile est plus lourde", "l'eau est acide", "l'huile est un métal"], "Les molécules d'eau s'attirent entre elles et laissent l'huile de côté. L'huile flotte parce qu'elle est moins dense."),
    qcm("Dans une molécule de dioxygène (O₂), les deux atomes sont reliés par :", ["une double liaison", "une liaison simple", "une liaison ionique", "aucune liaison"], "Chaque oxygène partage deux électrons avec l'autre."),
    qcm("Qui a proposé en 1916 qu'une liaison covalente est une paire d'électrons partagée ?", ["Gilbert Lewis", "Niels Bohr", "Linus Pauling", "Ernest Rutherford"], "On lui doit aussi la notation de Lewis, où les électrons sont dessinés en points autour des symboles."),
    qcm("L'eau dissout bien le sel parce que :", ["ses molécules polaires entourent et séparent les ions", "elle est chaude", "le sel est déjà liquide", "elle contient du chlore"], "Le côté oxygène de l'eau entoure les ions Na⁺, le côté hydrogène entoure les ions Cl⁻."),
]

Q["chim.acides"] = [
    qcm("Une solution de pH 3 est :", ["acide", "neutre", "basique", "impossible"], "En dessous de 7, la solution est acide. Au-dessus, elle est basique."),
    qcm("Passer de pH 4 à pH 3 rend la solution :", ["10 fois plus acide", "1 fois plus acide", "2 fois plus acide", "100 fois plus acide"], "L'échelle est logarithmique : chaque unité correspond à un facteur 10 sur la concentration en ions H⁺."),
    vf("Le jus de citron est acide.", True, "Son acide citrique lui donne un pH d'environ 2."),
    qcm("Un acide mélangé à une base en bonnes proportions donne :", ["de l'eau et un sel", "un métal", "un gaz noble", "toujours une explosion"], "C'est la neutralisation : H⁺ et OH⁻ forment de l'eau."),
    qcm("Selon Brønsted et Lowry (1923), un acide est une espèce qui :", ["cède un ion H⁺", "capte un ion H⁺", "cède un électron", "absorbe la lumière"], "Une base, à l'inverse, capte un ion H⁺."),
    qcm("Quel acide trouve-t-on dans l'estomac ?", ["l'acide chlorhydrique", "l'acide sulfurique", "l'acide citrique", "l'acide acétique"], "Le suc gastrique a un pH d'environ 1,5 à 3. La paroi de l'estomac se protège par une couche de mucus."),
    qcm("Le vinaigre doit son goût à :", ["l'acide acétique", "l'acide chlorhydrique", "la soude", "l'ammoniac"], "Des bactéries transforment l'alcool du vin en acide acétique."),
    vf("Il est dangereux de mélanger de l'eau de Javel avec un détartrant acide.", True, "Le mélange libère du dichlore, un gaz toxique."),
    qcm("Le papier de tournesol devient rouge au contact :", ["d'un acide", "d'une base", "d'eau pure", "de sel"], "Il vire au bleu au contact d'une base."),
    num("Une solution contient 0,01 mol/L d'ions H⁺. Quel est son pH ?", 2, "pH = −log[H⁺] = −log(10⁻²) = 2."),
    qcm("Pourquoi les océans s'acidifient-ils ?", ["ils absorbent une partie du CO₂ émis, qui forme de l'acide carbonique", "à cause du sel", "à cause des marées", "ils ne s'acidifient pas"], "Le pH de surface est passé d'environ 8,2 à 8,1 depuis le XIXe siècle : environ 30 % d'ions H⁺ en plus."),
    qcm("Les médicaments contre les brûlures d'estomac contiennent souvent :", ["une base faible, comme le bicarbonate ou le carbonate de calcium", "de l'acide citrique", "du vinaigre", "du sel de table"], "La base neutralise une partie de l'acide gastrique."),
]

Q["chim.reactions"] = [
    vf("Lors d'une réaction chimique, des atomes apparaissent ou disparaissent.", False, "Les atomes se réarrangent, ils ne se créent pas et ne se détruisent pas. C'est pourquoi on équilibre les équations."),
    num("Complète : 2 H₂ + O₂ → ? H₂O", 2, "4 atomes d'hydrogène et 2 d'oxygène de chaque côté : il faut 2 molécules d'eau."),
    qcm("La rouille est :", ["une oxydation du fer", "une réduction du fer", "une évaporation du fer", "une fusion du fer"], "Le fer réagit avec l'oxygène et l'eau pour former un oxyde de fer hydraté."),
    qcm("Pour qu'un feu prenne, il faut :", ["un combustible, un comburant (souvent l'oxygène) et une source de chaleur", "seulement de la chaleur", "seulement de l'oxygène", "de l'eau"], "C'est le triangle du feu. Retirer un seul côté éteint l'incendie."),
    qcm("Un catalyseur :", ["accélère une réaction sans être consommé", "est consommé par la réaction", "ralentit toujours la réaction", "change les produits obtenus"], "Les enzymes sont les catalyseurs du vivant. Le pot catalytique d'une voiture en contient aussi."),
    qcm("En oxydoréduction, s'oxyder signifie :", ["perdre des électrons", "gagner des électrons", "gagner des protons", "perdre des neutrons"], "L'espèce qui gagne les électrons est réduite. Les deux vont toujours ensemble."),
    vf("Une réaction exothermique libère de la chaleur.", True, "La combustion en est une. Une réaction endothermique absorbe de la chaleur, comme dans les poches de froid instantané."),
    qcm("La combustion complète du méthane produit de l'eau et :", ["du dioxyde de carbone", "du monoxyde de carbone", "de l'hydrogène", "de l'azote"], "Le monoxyde de carbone, toxique, apparaît quand l'oxygène manque."),
    qcm("Bicarbonate et vinaigre : les bulles qui se forment sont du :", ["dioxyde de carbone", "dioxygène", "dihydrogène", "dichlore"], "L'acide du vinaigre décompose le bicarbonate en eau, sel et CO₂."),
    qcm("Pourquoi met-on les aliments au réfrigérateur ?", ["le froid ralentit les réactions chimiques et la croissance des microbes", "le froid tue tous les microbes", "le froid ajoute de l'oxygène", "le froid rend les aliments acides"], "Une baisse de 10 °C divise souvent la vitesse des réactions par deux ou trois."),
    qcm("Qui a nommé l'oxygène et enterré la théorie du phlogistique ?", ["Antoine Lavoisier", "Robert Boyle", "Dmitri Mendeleïev", "Marie Curie"], "Scheele et Priestley l'avaient isolé ; Lavoisier a compris son rôle dans la combustion et lui a donné son nom en 1777."),
    qcm("Dans une pile, l'énergie électrique vient :", ["d'une réaction d'oxydoréduction", "de la gravité", "de la fusion nucléaire", "de la lumière"], "Les électrons passent du métal qui s'oxyde à l'espèce qui se réduit, à travers le circuit."),
]

# --- Cosmos : astronomie --------------------------------------------------------

Q["astro.systeme"] = [
    qcm("Quelle est la planète la plus proche du Soleil ?", ["Mercure", "Vénus", "Mars", "la Terre"], "Mercure tourne autour du Soleil en 88 jours."),
    qcm("Quelle est la planète la plus chaude du Système solaire ?", ["Vénus", "Mercure", "Mars", "Jupiter"], "Son épaisse atmosphère de CO₂ crée un effet de serre extrême : environ 465 °C au sol, plus que sur Mercure."),
    num("Combien de planètes compte le Système solaire depuis 2006 ?", 8, "Pluton a été reclassée planète naine par l'Union astronomique internationale en août 2006."),
    qcm("Qu'est-ce qui cause les saisons sur Terre ?", ["l'inclinaison de l'axe de rotation de la Terre", "les variations de distance au Soleil", "l'activité du Soleil", "la Lune"], "L'axe est incliné d'environ 23,4°. La Terre est même au plus près du Soleil début janvier, en plein hiver boréal."),
    qcm("Quelle est la plus grande planète du Système solaire ?", ["Jupiter", "Saturne", "Neptune", "la Terre"], "Sa masse vaut plus de deux fois celle de toutes les autres planètes réunies."),
    vf("La Lune montre toujours la même face à la Terre.", True, "Elle tourne sur elle-même en exactement le temps qu'elle met à faire le tour de la Terre."),
    qcm("La Lune passe entre la Terre et le Soleil (schéma). Que voit-on depuis la Terre ?", ["la nouvelle lune", "la pleine lune", "un premier quartier", "forcément une éclipse"], "La face éclairée regarde le Soleil, donc pas nous. L'éclipse n'a lieu que si l'alignement est parfait, car l'orbite lunaire est inclinée d'environ 5°."),
    qcm("La ceinture principale d'astéroïdes se trouve entre :", ["Mars et Jupiter", "la Terre et Mars", "Jupiter et Saturne", "Neptune et Pluton"], "Sa masse totale ne fait que quelques pour cent de celle de la Lune."),
    qcm("Les anneaux de Saturne sont surtout faits de :", ["glace d'eau et de poussières", "gaz", "roche en fusion", "métal"], "Des morceaux allant du grain de poussière au bloc de plusieurs mètres."),
    vf("Mars est rouge à cause de l'oxyde de fer de sa surface.", True, "Sa poussière est en quelque sorte rouillée."),
    qcm("Une comète est surtout faite de :", ["glace et poussières", "fer", "gaz en feu", "lave"], "Près du Soleil, la glace se sublime et forme une queue toujours orientée à l'opposé du Soleil."),
    qcm("Combien de temps la Terre met-elle à faire le tour du Soleil ?", ["environ 365,25 jours", "24 heures", "29,5 jours", "12 ans"], "Le quart de jour en trop s'accumule : d'où l'année bissextile tous les quatre ans."),
]

Q["astro.etoiles"] = [
    qcm("Une étoile produit son énergie par :", ["la fusion nucléaire de noyaux légers", "la combustion de charbon", "la fission de l'uranium", "la réflexion de la lumière"], "Au cœur du Soleil, à environ 15 millions de degrés, l'hydrogène fusionne en hélium."),
    qcm("Une année-lumière est une unité de :", ["distance", "temps", "vitesse", "luminosité"], "La distance parcourue par la lumière en un an : environ 9 460 milliards de km."),
    qcm("La couleur d'une étoile renseigne surtout sur :", ["sa température de surface", "sa distance", "son âge exact", "sa forme"], "Les étoiles bleues dépassent 10 000 °C, les rouges sont autour de 3 000 °C. Le Soleil, vers 5 500 °C, est jaune-blanc. La composition, elle, se lit dans les raies du spectre, pas dans la couleur."),
    vf("Quand on regarde une étoile lointaine, on la voit telle qu'elle était dans le passé.", True, "Sa lumière a mis des années, parfois des millénaires, à nous parvenir."),
    qcm("Quelle est l'étoile la plus proche du Soleil ?", ["Proxima du Centaure", "Sirius", "l'étoile Polaire", "Bételgeuse"], "À environ 4,2 années-lumière. Sa lumière met donc plus de quatre ans à nous parvenir."),
    qcm("Que deviendra le Soleil dans environ 5 milliards d'années ?", ["une géante rouge, puis une naine blanche", "un trou noir", "une supernova", "rien, il brillera toujours"], "Il est trop peu massif pour exploser en supernova ou devenir un trou noir."),
    qcm("L'or et les autres éléments très lourds ont surtout été produits :", ["lors d'explosions et de collisions d'étoiles", "au cœur du Soleil", "dans l'atmosphère de la Terre", "par les volcans"], "En 2017, la collision de deux étoiles à neutrons (GW170817) a été observée en direct, avec sa production d'éléments lourds."),
    qcm("L'étoile Polaire indique :", ["le nord", "le sud", "l'est", "l'heure"], "Elle se trouve presque dans l'axe de rotation de la Terre, au-dessus du pôle Nord."),
    vf("L'étoile Polaire est l'étoile la plus brillante du ciel nocturne.", False, "Elle n'est qu'une étoile moyenne. La plus brillante après le Soleil est Sirius."),
    qcm("Pourquoi les étoiles scintillent-elles ?", ["la turbulence de l'atmosphère dévie sans cesse leur lumière", "elles clignotent vraiment", "elles tournent sur elles-mêmes", "à cause de la Lune"], "Vues depuis l'espace, elles ne scintillent pas. Les planètes, moins ponctuelles, scintillent beaucoup moins."),
    qcm("Une naine blanche a à peu près la masse du Soleil et la taille :", ["de la Terre", "d'une ville", "de Jupiter", "du Soleil"], "Une cuillère à café de sa matière pèserait plusieurs tonnes."),
    qcm("Une constellation est :", ["un groupe d'étoiles qui semblent voisines vues de la Terre, mais peuvent être très éloignées entre elles", "un amas d'étoiles liées par la gravité", "une petite galaxie", "une planète très brillante"], "C'est une figure en perspective. L'Union astronomique internationale en reconnaît 88."),
]

Q["astro.orbites"] = [
    qcm("Selon la première loi de Kepler, les planètes décrivent :", ["des ellipses dont le Soleil occupe un foyer", "des cercles centrés sur le Soleil", "des spirales", "des lignes droites"], "Kepler l'a établi en 1609 à partir des mesures de Tycho Brahe sur Mars."),
    qcm("Sur cette orbite (schéma), où la planète va-t-elle le plus vite ?", ["au point A, près du Soleil", "au point B, loin du Soleil", "à la même vitesse partout", "cela dépend de sa masse"], "C'est la deuxième loi de Kepler : la ligne Soleil-planète balaie des aires égales en des temps égaux. Près du Soleil, il faut aller plus vite."),
    vf("Les astronautes de la Station spatiale flottent parce qu'il n'y a pas de gravité là-haut.", False, "À 400 km d'altitude, la gravité vaut encore environ 90 % de celle du sol. Ils flottent parce qu'ils tombent en permanence avec la station."),
    qcm("Pourquoi la Lune ne s'écrase-t-elle pas sur la Terre ?", ["elle tombe sans cesse vers la Terre, mais sa vitesse latérale la fait passer à côté", "il n'y a pas de gravité dans l'espace", "le Soleil la retient", "elle est trop légère"], "C'est l'intuition de Newton : une orbite est une chute qui rate toujours le sol."),
    qcm("Les marées sont dues surtout à :", ["l'attraction de la Lune, et dans une moindre mesure du Soleil", "au vent", "à la rotation de la Terre seule", "aux courants marins"], "Quand Soleil et Lune s'alignent, on a les grandes marées de vives-eaux."),
    num("En combien de minutes environ la Station spatiale internationale fait-elle le tour de la Terre ?", 92, "Environ 92 minutes, à près de 28 000 km/h : 15 à 16 tours par jour.", tol=5, unite="min"),
    qcm("Un satellite géostationnaire :", ["reste au-dessus du même point de l'équateur", "est immobile dans l'espace", "tourne autour de la Lune", "survole les pôles"], "À environ 35 800 km d'altitude, il fait un tour en un jour, au rythme de la Terre."),
    qcm("Qui a prédit par le calcul la position de Neptune en 1846 ?", ["Urbain Le Verrier", "Galilée", "Isaac Newton", "Edwin Hubble"], "Johann Galle l'a observée le 23 septembre 1846, à environ un degré de la position annoncée."),
    vf("Plus un satellite est proche de la Terre, plus il tourne vite autour d'elle.", True, "La Station spatiale fait un tour en 1 h 30, la Lune en 27 jours."),
    qcm("Pour échapper à l'attraction de la Terre sans propulsion, il faut partir à environ :", ["11,2 km/s", "1,1 km/s", "112 km/s", "340 m/s"], "C'est la vitesse de libération, soit plus de 40 000 km/h."),
    qcm("La troisième loi de Kepler relie :", ["la durée de révolution d'une planète à la taille de son orbite", "sa masse à sa couleur", "sa vitesse à sa température", "son nombre de lunes à sa taille"], "Le carré de la période est proportionnel au cube du demi-grand axe : T² ∝ a³."),
    qcm("Un trou noir est :", ["une région où la gravité est si forte que même la lumière ne peut en sortir", "un trou dans l'espace vide", "une étoile éteinte qui ne pèse plus rien", "un aspirateur qui avale tout dans la galaxie"], "Vu de loin, il attire comme n'importe quelle masse égale. La première image d'un trou noir (M87*) date de 2019."),
]

Q["astro.galaxies"] = [
    qcm("Comment s'appelle notre galaxie ?", ["la Voie lactée", "Andromède", "le Grand Nuage de Magellan", "Orion"], "Son nom vient de la bande laiteuse qu'elle dessine dans le ciel nocturne."),
    qcm("L'âge de l'Univers est estimé à environ :", ["13,8 milliards d'années", "4,5 milliards d'années", "6 000 ans", "100 milliards d'années"], "4,5 milliards d'années, c'est l'âge de la Terre."),
    qcm("Qui a montré en 1923-1924 qu'Andromède est une galaxie extérieure à la nôtre ?", ["Edwin Hubble", "Albert Einstein", "Galilée", "Carl Sagan"], "En repérant une étoile variable (une céphéide) dans Andromède, il a pu en mesurer la distance."),
    qcm("Le décalage vers le rouge de la lumière des galaxies lointaines indique que :", ["elles s'éloignent : l'Univers est en expansion", "elles sont plus chaudes", "elles se rapprochent", "elles sont réellement rouges"], "Plus une galaxie est loin, plus elle s'éloigne vite : c'est la loi de Hubble-Lemaître."),
    vf("Le Big Bang est une explosion qui a eu lieu en un point précis de l'espace.", False, "Ce n'est pas une explosion dans l'espace, mais l'expansion de l'espace lui-même, partout à la fois."),
    qcm("Le fond diffus cosmologique, découvert en 1965, est :", ["la plus ancienne lumière de l'Univers, émise environ 380 000 ans après le Big Bang", "le bruit de fond des étoiles", "la lumière du Soleil réfléchie", "un écho radio de la Terre"], "Penzias et Wilson ont d'abord soupçonné les fientes de pigeons dans leur antenne. Ils ont reçu le prix Nobel en 1978."),
    qcm("Au centre de la Voie lactée se trouve :", ["un trou noir supermassif, Sagittarius A*", "le Soleil", "une étoile géante", "rien du tout"], "Environ 4 millions de fois la masse du Soleil. Reinhard Genzel et Andrea Ghez ont reçu le prix Nobel 2020 pour l'avoir mis en évidence."),
    qcm("Combien d'étoiles compte la Voie lactée, environ ?", ["entre 100 et 400 milliards", "environ 1 million", "environ 10 000", "exactement 8"], "Et l'Univers observable compte des centaines de milliards de galaxies."),
    qcm("Andromède et la Voie lactée :", ["se rapprochent et devraient fusionner dans plusieurs milliards d'années", "s'éloignent l'une de l'autre", "sont une seule et même galaxie", "sont immobiles l'une par rapport à l'autre"], "Andromède fait exception à l'expansion : la gravité l'attire vers nous à environ 110 km/s."),
    vf("La matière ordinaire, celle des atomes, ne représente qu'environ 5 % du contenu de l'Univers.", True, "Le reste serait de la matière noire (environ 27 %) et de l'énergie noire (environ 68 %), selon les mesures du satellite Planck."),
    qcm("Qui a proposé en 1927 un Univers en expansion, puis en 1931 un « atome primitif » à son origine ?", ["Georges Lemaître", "Fred Hoyle", "Edwin Hubble", "Stephen Hawking"], "Un prêtre et physicien belge. Le nom « Big Bang » vient de Fred Hoyle, qui s'en moquait à la radio en 1949."),
    qcm("Une galaxie spirale comme la nôtre a la forme :", ["d'un disque aplati avec des bras", "d'une sphère parfaite", "d'un anneau vide", "d'un cube"], "Le Soleil se trouve dans un des bras, à environ 26 000 années-lumière du centre."),
]

# --- Étincelle : électricité ----------------------------------------------------

Q["elec.circuits"] = [
    qcm("Deux charges électriques de même signe :", ["se repoussent", "s'attirent", "s'annulent", "n'agissent pas l'une sur l'autre"], "Des charges de signes opposés s'attirent."),
    qcm("Dans un fil métallique, le courant électrique est un déplacement :", ["d'électrons", "de protons", "de neutrons", "d'atomes entiers"], "Les électrons vont de la borne − vers la borne +. Le sens conventionnel du courant, fixé avant leur découverte, est l'inverse."),
    vf("Sur ce schéma, l'interrupteur est ouvert. La lampe est allumée.", False, "Un interrupteur ouvert coupe la boucle : le courant ne circule plus et la lampe reste éteinte."),
    qcm("Un matériau isolant :", ["laisse très mal passer le courant", "laisse bien passer le courant", "produit du courant", "stocke la lumière"], "Plastique, verre, caoutchouc. C'est pour cela qu'ils gainent les câbles."),
    qcm("Lequel de ces matériaux conduit bien le courant ?", ["le cuivre", "le caoutchouc", "le verre", "le bois sec"], "Les métaux ont des électrons libres de se déplacer. Le cuivre est le métal des fils électriques."),
    qcm("Deux lampes en série (schéma). On dévisse la lampe 1. Que fait la lampe 2 ?", ["elle s'éteint", "elle brille plus fort", "elle ne change pas", "elle clignote"], "En série, il n'y a qu'un seul chemin. Le retirer ouvre le circuit."),
    qcm("Deux lampes en dérivation (schéma). On dévisse la lampe 1. Que fait la lampe 2 ?", ["elle reste allumée", "elle s'éteint", "elle grille", "elle change de couleur"], "Chaque lampe a sa propre boucle. C'est ainsi que sont câblées les prises d'une maison."),
    vf("Un court-circuit se produit quand le courant trouve un chemin de très faible résistance.", True, "Le courant devient alors énorme et chauffe les fils, d'où les fusibles et les disjoncteurs."),
    qcm("L'unité de charge électrique est :", ["le coulomb", "le volt", "l'ampère", "le watt"], "Un ampère, c'est un coulomb qui passe chaque seconde."),
    qcm("Un ballon frotté sur des cheveux attire les cheveux car :", ["des électrons sont passés des cheveux au ballon", "le frottement crée des charges", "le ballon devient un aimant", "le ballon chauffe"], "Les charges ne sont pas créées : elles changent de place. Le ballon devient négatif, les cheveux positifs."),
    qcm("Un fusible ou un disjoncteur sert à :", ["couper le circuit quand le courant devient trop fort", "augmenter la tension", "stocker l'électricité", "éclairer la pièce"], "Il protège les fils d'une surchauffe qui pourrait provoquer un incendie."),
    qcm("Qui a fabriqué la première pile électrique, en 1800 ?", ["Alessandro Volta", "Luigi Galvani", "Thomas Edison", "Benjamin Franklin"], "Un empilement de disques de cuivre et de zinc séparés par du carton imbibé d'eau salée. Le volt porte son nom."),
]

Q["elec.ohm"] = [
    qcm("La loi d'Ohm s'écrit :", ["U = R × I", "P = U × I", "E = mc²", "F = m × a"], "La tension U (en volts) égale la résistance R (en ohms) fois l'intensité I (en ampères)."),
    num("U = 12 V et R = 4 Ω. Quelle est l'intensité ?", 3, "I = U / R = 12 / 4 = 3 A.", unite="A"),
    qcm("L'intensité du courant se mesure en :", ["ampères", "volts", "ohms", "watts"], "Avec un ampèremètre, branché en série."),
    qcm("Pour mesurer une tension, on utilise :", ["un voltmètre branché en dérivation", "un ampèremètre branché en série", "un thermomètre", "une boussole"], "Le voltmètre compare deux points du circuit : on le branche à leurs bornes."),
    num("Sur ce schéma, quelle intensité traverse la résistance ?", 3, "I = U / R = 9 V / 3 Ω = 3 A.", unite="A"),
    vf("Deux résistances en série s'additionnent.", True, "R = R₁ + R₂ : le courant doit les traverser l'une après l'autre."),
    num("Deux résistances de 100 Ω montées en dérivation équivalent à une seule résistance de :", 50, "Deux chemins identiques laissent passer deux fois plus de courant : la résistance est divisée par deux.", unite="Ω"),
    qcm("En France, la tension du réseau domestique est de :", ["230 V", "110 V", "12 V", "1 000 V"], "Alternative, à 50 Hz. L'Amérique du Nord utilise environ 120 V à 60 Hz."),
    qcm("Un oiseau posé sur une seule ligne haute tension ne s'électrocute pas parce que :", ["ses deux pattes sont au même potentiel : aucun courant ne le traverse", "ses plumes l'isolent", "la tension est faible", "il est trop léger"], "Le danger viendrait d'un contact simultané avec deux câbles, ou avec un câble et un pylône."),
    vf("C'est le courant qui traverse le corps, plus que la tension seule, qui fait le danger.", True, "Quelques dizaines de milliampères suffisent à provoquer des troubles graves, d'où les disjoncteurs différentiels de 30 mA."),
    qcm("La résistance d'un fil augmente quand il est :", ["plus long ou plus fin", "plus court", "plus épais", "mieux isolé"], "Comme un tuyau d'eau : plus il est long et étroit, plus il freine le débit."),
    qcm("Si l'on compare un circuit électrique à un circuit d'eau, la tension correspond à :", ["la différence de pression", "le débit", "la longueur du tuyau", "la couleur de l'eau"], "L'intensité correspond au débit, la résistance à l'étroitesse du tuyau."),
]

Q["elec.puissance"] = [
    qcm("La puissance électrique se calcule par :", ["P = U × I", "P = U / I", "P = R / I", "P = I / U"], "Des watts = des volts × des ampères."),
    num("Un appareil branché sous 230 V consomme 10 A. Quelle est sa puissance ?", 2300, "P = 230 × 10 = 2 300 W.", unite="W"),
    num("Un radiateur de 2 000 W fonctionne pendant 3 heures. Combien de kWh consomme-t-il ?", 6, "2 kW × 3 h = 6 kWh.", unite="kWh"),
    qcm("Sur une facture, l'électricité consommée est comptée en :", ["kilowattheures", "kilowatts", "volts", "ampères"], "Le kilowatt mesure une puissance ; le kilowattheure, une énergie."),
    vf("Une ampoule LED éclaire autant qu'une ampoule à incandescence en consommant beaucoup moins.", True, "Environ 5 à 8 fois moins. L'ampoule classique transforme surtout l'électricité en chaleur."),
    qcm("Pourquoi transporte-t-on l'électricité à très haute tension ?", ["pour réduire les pertes par échauffement dans les câbles", "pour qu'elle aille plus vite", "parce que c'est moins dangereux", "pour la rendre plus propre"], "À puissance égale, une tension plus haute demande moins d'intensité. Or les pertes augmentent avec le carré de l'intensité."),
    qcm("L'effet Joule, c'est :", ["la chaleur dégagée quand le courant traverse une résistance", "la production de lumière par un aimant", "l'aimantation d'un fil", "la création de charges"], "Le grille-pain, la bouilloire et le radiateur l'exploitent."),
    num("Une ampoule de 5 W reste allumée 1 000 heures. Combien de kWh consomme-t-elle ?", 5, "5 W × 1 000 h = 5 000 Wh = 5 kWh.", unite="kWh"),
    qcm("Un appareil en veille :", ["consomme encore un peu d'électricité", "ne consomme rien", "produit de l'électricité", "consomme plus qu'allumé"], "Souvent quelques watts, mais 24 heures sur 24."),
    qcm("Une centrale nucléaire produit son électricité :", ["avec la chaleur de la fission, qui fait tourner une turbine à vapeur", "directement à partir des atomes", "avec des panneaux solaires", "par la fusion de l'hydrogène"], "C'est au fond une grosse bouilloire : comme une centrale à charbon, mais chauffée par la fission."),
    qcm("Un panneau photovoltaïque transforme :", ["la lumière en électricité", "la chaleur en lumière", "le vent en électricité", "l'électricité en lumière"], "Il repose sur l'effet photoélectrique, dont l'explication a valu à Einstein le prix Nobel de 1921."),
    vf("Le watt et le joule mesurent la même grandeur.", False, "Le joule mesure une énergie, le watt une puissance : un watt, c'est un joule par seconde."),
]

Q["elec.magnetisme"] = [
    qcm("Deux pôles nord d'aimants placés face à face :", ["se repoussent", "s'attirent", "s'annulent", "n'agissent pas l'un sur l'autre"], "Les pôles de même nom se repoussent, les pôles opposés s'attirent."),
    qcm("L'aiguille d'une boussole s'oriente selon :", ["le champ magnétique terrestre", "l'étoile Polaire", "la position du Soleil", "la gravité"], "Ce champ est produit par les mouvements du fer liquide dans le noyau de la Terre."),
    qcm("Qui a remarqué en 1820 qu'un courant électrique fait dévier une boussole ?", ["Hans Christian Ørsted", "Michael Faraday", "James Clerk Maxwell", "Nikola Tesla"], "La preuve qu'électricité et magnétisme sont liés, découverte pendant un cours selon la tradition."),
    qcm("Déplacer un aimant près d'une bobine y crée un courant. C'est :", ["l'induction électromagnétique", "l'effet Joule", "l'effet Doppler", "l'électrolyse"], "Découverte par Faraday en 1831. Toutes les centrales électriques reposent sur ce principe."),
    vf("Près du pôle Nord géographique se trouve un pôle sud magnétique.", True, "Le pôle nord de l'aiguille est attiré par un pôle sud magnétique : c'est donc lui qui se trouve dans l'Arctique."),
    qcm("Un électroaimant est :", ["une bobine qui devient un aimant quand le courant y passe", "un aimant permanent très puissant", "un aimant rempli de piles", "une pile magnétique"], "On peut l'allumer et l'éteindre : grues de ferrailleurs, sonnettes, haut-parleurs."),
    qcm("L'alternateur d'une centrale transforme :", ["la rotation d'une turbine en électricité", "l'électricité en mouvement", "la chaleur directement en lumière", "la lumière en électricité"], "Un aimant tourne devant des bobines : c'est l'induction."),
    qcm("Un moteur électrique transforme :", ["l'énergie électrique en mouvement", "le mouvement en électricité", "la chaleur en électricité", "la lumière en mouvement"], "C'est l'inverse de l'alternateur. Certains moteurs de voitures électriques font les deux, en récupérant l'énergie au freinage."),
    qcm("Qui a unifié électricité, magnétisme et lumière dans un même ensemble d'équations, en 1865 ?", ["James Clerk Maxwell", "Isaac Newton", "André-Marie Ampère", "Albert Einstein"], "Ses équations montrent que la lumière est une onde électromagnétique."),
    qcm("Les aurores polaires sont provoquées par :", ["des particules venues du Soleil, guidées par le champ magnétique terrestre", "des reflets de la banquise", "la Lune", "des orages en altitude"], "Elles excitent les atomes d'oxygène et d'azote de la haute atmosphère, qui émettent du vert, du rouge ou du violet."),
    vf("En coupant un aimant en deux, on sépare son pôle nord de son pôle sud.", False, "Chaque morceau devient un aimant complet, avec ses deux pôles."),
    qcm("Une plaque à induction chauffe la casserole grâce :", ["aux courants induits dans le fond métallique de la casserole", "à une flamme cachée", "à des micro-ondes", "à une résistance sous la vitre"], "La plaque elle-même chauffe peu : c'est la casserole qui s'échauffe par effet Joule."),
]
