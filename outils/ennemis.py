"""v7 : les ennemis du plateau, figures de la bêtise humaine, et leurs duels de vrai ou faux.

Sept ennemis sont posés sur le plateau au début de chaque tour, un autre attend en réserve
(il arrive quand un cadeau fait à l'IA tourne mal). v15 : seize ennemis ; à partir du deuxième tour,
l'IA choisit ses sept parmi les quinze hors réserve, et leurs postes glissent de quelques cases. Passer sur un ennemi arrête le pion et lance
un duel : cinq affirmations, il faut les juger toutes correctement. Les fausses sont des idées
reçues ou des fausses nouvelles célèbres, chacune avec son origine et une source.

Archétypes inventés, et deux figures historiques mortes depuis longtemps (Lyssenko, Mesmer).
Aucune personne vivante.
"""
from avatar40 import L, chapeau_alu, haut_de_forme, toile, frange_sous
from dessin import anneau, bande, disque, ellipse, poly, rect, trait
from savants import barbe, c, coiffure, objet, peindre_corps, tenue

# id, nom, titre, figure (archetype | historique), années, description, peau, tenue, couleurs, tête, barbe, objet,
# défi (au début du duel), victoire (quand le joueur gagne), défaite (quand il perd), source
ENNEMIS = [
    ("sophiste", "Le Sophiste", "Maître Paralogisme", "archetype", None,
     "Il vend des raisonnements au poids. Plus ils sont faux, plus ils sont chers. Platon lui reprochait déjà de faire passer la thèse la plus faible pour la plus forte.",
     "claire", "toge", c("#E8DDC0", "#A8905E", "#B5476B"), ("couronne", "gris", 3), ("pleine", "gris", 3), "des",
     "Je vais te prouver que tu as perdu avant même de commencer. La preuve : tu m'écoutes.",
     "Bon. Disons que c'était un exercice de style.",
     "Tu vois ? Tout se démontre. Surtout le faux.",
     "Platon, Gorgias et Protagoras"),
    ("platiste", "Le Platiste", "Capitaine Bord-du-Monde", "archetype", None,
     "Il n'a jamais vu la courbure de la Terre. Il n'a jamais regardé non plus. Ératosthène l'a mesurée vers 240 avant notre ère avec un bâton et deux ombres.",
     "claire", "pull", c("#24408F", "#2F3B59", "#F2C14E"), ("casquette", None, None), None, "disque_plat",
     "Avance si tu l'oses. Au bout du plateau, tu tombes dans le vide.",
     "Je vais faire le tour du monde pour vérifier. En ligne droite.",
     "Tu as perdu. C'est plat, comme ta défense.",
     "Jeffrey Burton Russell, Inventing the Flat Earth, 1991"),
    ("influenceur", "L'Influenceur détox", "Coach Smoothie", "archetype", None,
     "Il vend des cures qui « éliminent les toxines », sans jamais dire lesquelles. Le foie et les reins font ce travail gratuitement depuis toujours.",
     "mate", "pull", c("#4CAF50", "#2F3B59", "#F28FB0"), ("ebouriffe", "orange", 1), None, "smoothie",
     "Avant le duel, une petite cure ? Code promo DUEL pour 10 % de réduction.",
     "Je me désabonne de toi.",
     "Tu as perdu. C'est les toxines. Ça tombe bien, j'ai un produit.",
     "Klein et Kiat, Journal of Human Nutrition and Dietetics, 2015"),
    ("astrologue", "L'Astrologue", "Madame Ascendant", "archetype", None,
     "Elle lit l'avenir dans des constellations qui ont glissé d'un signe depuis l'Antiquité, à cause de la précession des équinoxes. Kepler, lui, faisait des horoscopes pour payer son loyer.",
     "claire", "robe", c("#5E2F8A", "#3B1A5C", "#F2C14E"), ("pointu", None, None), None, "boule",
     "J'avais prévu ta venue. Et ta défaite. Mercure est rétrograde.",
     "Les astres s'étaient trompés. Ce n'est pas leur faute, ils sont très loin.",
     "Je l'avais lu dans les étoiles. Et dans tes réponses.",
     "Shawn Carlson, « A double-blind test of astrology », Nature, 1985"),
    ("mesmer", "Franz Anton Mesmer", "Magnétiseur, 1734-1815", "historique", "1734 / 1815",
     "À Paris, ses patients se tiennent autour d'un baquet de fer et entrent en « crise ». En 1784, une commission royale où siègent Franklin et Lavoisier montre qu'à l'aveugle, le « fluide magnétique » n'agit plus.",
     "claire", "manteau", c("#5E2F8A", "#3B3B3B", "#F2C14E"), ("perruque", "gris", 4), None, "baguette",
     "Regarde ma baguette. Tes paupières sont lourdes. Tu vas te tromper.",
     "Le fluide ne passe plus. Il paraît que c'est l'imagination. Franklin me l'avait dit.",
     "Tu as cédé au fluide. Ne t'inquiète pas : ce n'est que ton imagination.",
     "Rapport des commissaires chargés par le roi de l'examen du magnétisme animal, 1784"),
    ("lyssenko", "Trofim Lyssenko", "Agronome soviétique, 1898-1976", "historique", "1898 / 1976",
     "Il promettait de transformer le blé d'hiver en blé de printemps par le froid et la volonté, et niait la génétique. Soutenu par Staline, il fait écarter ses opposants. Le généticien Nikolaï Vavilov meurt en prison en 1943.",
     "claire", "manteau", c("#5D6470", "#3B3B3B", "#D94141"), ("court", "cheveux", 1), None, "epi",
     "La génétique est une science bourgeoise. Prépare-toi à être vernalisé.",
     "Les faits ont gagné. Ce n'est pas dans le plan quinquennal.",
     "Ta défaite était planifiée. Comme les récoltes. Qui ont raté aussi.",
     "Zhores Medvedev, The Rise and Fall of T. D. Lysenko, 1969"),
    ("complotiste", "Le Complotiste", "Œil Ouvert", "archetype", None,
     "Il a fait ses propres recherches, entre minuit et 4 heures. Les vrais complots existent, mais on les connaît par des archives et des enquêtes, pas par des vidéos.",
     "claire", "manteau", c("#6B6B3A", "#3B3B3B", "#C9CED6"), ("alu", None, None), None, "loupe",
     "Tu crois aux faits ? C'est exactement ce qu'ils veulent que tu croies.",
     "Ta victoire est suspecte. Je vais faire mes recherches.",
     "Réveille-toi. Ah non, tu as perdu, dors.",
     "Kathryn Olmsted, Real Enemies, 2009"),
    ("charlatan", "Le Charlatan", "Docteur Panacée", "archetype", None,
     "Son élixir soigne tout, sauf le doute. Ses ancêtres vendaient de la thériaque et de l'orviétan sur le Pont-Neuf. L'IA l'a sorti de son alambic.",
     "claire", "manteau", c("#8E2424", "#3B3B3B", "#F2C14E"), ("haut_de_forme", None, None), ("favoris", "cheveux", 1), "fiole",
     "Une gorgée de mon élixir et tu gagnes. Deux gorgées et tu ne te souviens plus avoir perdu.",
     "Remboursé. Enfin, pas toi.",
     "Tu vois ? Le placebo marche aussi sur les défaites.",
     "Ben Goldacre, Bad Science, 2008"),
    # v15 : huit ennemis de plus. Toujours sept sur le plateau : l'IA en change à chaque tour.
    ("pline", "Pline l'Ancien", "Naturaliste, 23-79", "historique", "23 / 79",
     "Son Histoire naturelle compile tout ce qu'on lui raconte : des hommes sans tête, des fourmis chercheuses d'or, des porcs-épics qui tirent leurs piquants. Il meurt en 79 en s'approchant du Vésuve pour observer l'éruption.",
     "mate", "toge", c("#E8DDC0", "#A8905E", "#8E2424"), ("court", "gris", 3), None, "ruban",
     "J'ai lu deux mille volumes. Tout ce qu'ils disent est vrai, puisque c'est écrit.",
     "Je note ta victoire dans mon livre. Entre la licorne et le basilic.",
     "Tu as perdu. C'est consigné au livre VIII, avec les éléphants qui adorent la Lune.",
     "Pline l'Ancien, Histoire naturelle ; Pline le Jeune, Lettres, VI, 16"),
    ("gall", "Franz Joseph Gall", "Phrénologue, 1758-1828", "historique", "1758 / 1828",
     "Il lit le caractère dans les bosses du crâne : bosse de la ruse, de l'amour des enfants, du meurtre. L'idée que le cerveau a des régions spécialisées était juste ; tâter le crâne pour les lire, non.",
     "claire", "manteau", c("#2F3B59", "#3B3B3B", "#E8E8EE"), ("perruque_courte", "gris", 4), None, "crane",
     "Laisse-moi tâter ton crâne. Hum. Bosse de la défaite, très développée.",
     "Je ne comprends pas. Ta bosse des maths est minuscule.",
     "Je l'avais senti au toucher. Ça ne se discute pas, ça se palpe.",
     "John van Wyhe, Phrenology and the Origins of Victorian Scientific Naturalism, 2004"),
    ("ussher", "James Ussher", "Archevêque d'Armagh, 1581-1656", "historique", "1581 / 1656",
     "En additionnant les générations de la Bible, il fixe la création du monde à la veille du dimanche 23 octobre 4004 av. J.-C. La radioactivité des roches donne à la Terre environ 4,5 milliards d'années.",
     "claire", "robe", c("#3B3B3B", "#1E1A2B", "#F2C14E"), ("coiffe", "gris", 3), ("pleine", "gris", 3), "sablier",
     "Le monde a commencé un samedi soir d'octobre. Ta défaite commence maintenant.",
     "Je refais mes calculs. Il me manque quelques milliards d'années.",
     "Perdu. C'était écrit, au jour près.",
     "James Ussher, Annales Veteris Testamenti, 1650"),
    ("diafoirus", "Le Docteur Diafoirus", "Médecin de Molière", "archetype", None,
     "Sorti du Malade imaginaire, il cite Hippocrate en latin et prescrit un clystère pour tout. L'IA l'a laissé moderniser ses idées reçues, pas ses méthodes.",
     "claire", "robe", c("#1E1A2B", "#3B3B3B", "#E8E8EE"), ("perruque", "cheveux", 1), None, "clystere",
     "Clysterium donare, postea seignare, ensuitta purgare. Et ensuite, un duel.",
     "Le malade est guéri. C'est intolérable.",
     "Tu as perdu selon les règles. Mieux vaut perdre selon les règles que gagner contre elles.",
     "Molière, Le Malade imaginaire, 1673 ; L'Amour médecin, 1665"),
    ("bessler", "Johann Bessler", "Orffyreus, inventeur, 1680-1745", "historique", "1680 / 1745",
     "En 1717, il fait sceller dans un château une roue qui tourne seule pendant des semaines. Sa servante affirmera plus tard qu'elle la faisait tourner, cachée dans la pièce voisine.",
     "claire", "manteau", c("#7A5418", "#3B3B3B", "#F2C14E"), ("perruque_courte", "cheveux", 2), None, "roue",
     "Ma roue tourne toute seule. Toi, tu vas tourner en rond.",
     "Ma roue s'est arrêtée. Quelqu'un a dû quitter la pièce d'à côté.",
     "Perdu. Le mouvement perpétuel existe : c'est toi qui recommences.",
     "Arthur Ord-Hume, Perpetual Motion, 1977"),
    ("raconteur", "Le Raconteur", "Monsieur Il-paraît-que", "archetype", None,
     "Il connaît toutes les anecdotes historiques, surtout celles qui ne sont jamais arrivées. Sa source préférée : « tout le monde sait ça ».",
     "foncee", "pull", c("#B5623B", "#2F3B59", "#F2C14E"), ("casquette", None, None), ("favoris", "cheveux", 1), "journal",
     "Il paraît que tu vas perdre. Je le tiens d'un cousin de Napoléon.",
     "Bon. Il paraît que tu as gagné. À vérifier.",
     "Tu as perdu. Je le raconterai, en mieux.",
     "Marc Bloch, Réflexions d'un historien sur les fausses nouvelles de la guerre, 1921"),
    ("lombroso", "Cesare Lombroso", "Criminologue, 1835-1909", "historique", "1835 / 1909",
     "Il croit reconnaître le « criminel-né » à ses mâchoires, ses oreilles ou ses arcades, mesurées au compas. En 1913, Charles Goring compare des milliers de détenus à des non-détenus : aucune différence.",
     "claire", "manteau", c("#3B3B3B", "#2B2B33", "#C9CED6"), ("raie", "cheveux", 1), ("pleine", "cheveux", 1), "compas",
     "Tes oreilles sont décollées. Ça ne trompe pas : tu vas tricher.",
     "Étrange. Tu n'as pas la tête d'un gagnant.",
     "Je l'avais mesuré à ton front : la défaite était innée.",
     "Charles Goring, The English Convict, 1913 ; Stephen Jay Gould, La Mal-mesure de l'homme, 1981"),
    ("tribun", "Le Tribun", "Maître Langue-de-bois", "archetype", None,
     "Il parle longtemps, fort, et sans jamais répondre à la question. Il cite des chiffres que personne n'a mesurés et des phrases que personne n'a dites.",
     "mate", "manteau", c("#24408F", "#2B2B33", "#D94141"), ("raie", "gris", 3), None, "porte_voix",
     "Je ne répondrai pas à ta question, mais je vais y répondre longuement.",
     "Je retire ce que je n'ai pas dit.",
     "Tu as perdu. Les chiffres le prouvent, je viens de les inventer.",
     "George Orwell, « Politics and the English Language », 1946"),
]

# Le huitième (le Charlatan) reste en réserve : il arrive par un cadeau à l'IA.
PLACEMENT = {"7": "sophiste", "15": "platiste", "26": "influenceur", "34": "astrologue", "44": "mesmer", "52": "lyssenko", "61": "complotiste"}
RESERVE = "charlatan"

# ennemi, vrai, affirmation, explication, origine, source
MYTHES = [
    # Le Sophiste : raisonnements et probabilités
    ("sophiste", False, "Après cinq « rouge » de suite à la roulette, le noir devient plus probable.",
     "Chaque tirage est indépendant : la roue n'a pas de mémoire. Le noir reste à 18 chances sur 37.",
     "C'est le sophisme du joueur. Le 18 août 1913 au casino de Monte-Carlo, le noir sort 26 fois de suite et des joueurs perdent des fortunes en misant sur le rouge.",
     "Darrell Huff, How to Take a Chance, 1959"),
    ("sophiste", False, "La foudre ne frappe jamais deux fois au même endroit.",
     "Elle frappe de préférence les points hauts, encore et encore. L'Empire State Building est touché en moyenne une vingtaine de fois par an.",
     "Un dicton anglais du XIXe siècle, pris au pied de la lettre.",
     "National Weather Service, « Lightning Myths »"),
    ("sophiste", False, "Les pays qui mangent le plus de chocolat ont le plus de prix Nobel : le chocolat rend donc plus intelligent.",
     "Une corrélation ne prouve pas une causalité. La richesse d'un pays explique à la fois sa consommation de chocolat et sa recherche.",
     "Une note volontairement provocante du cardiologue Franz Messerli, prise au sérieux par une partie de la presse.",
     "Franz Messerli, New England Journal of Medicine, 2012"),
    ("sophiste", False, "Dans un groupe de 23 personnes, il y a moins d'une chance sur dix que deux d'entre elles soient nées le même jour.",
     "Il y a un peu plus d'une chance sur deux (50,7 %), parce qu'on compare toutes les paires possibles : il y en a 253.",
     "Notre intuition compare chaque personne à soi-même, pas toutes les paires entre elles. C'est le paradoxe des anniversaires.",
     "Richard von Mises, 1939 ; William Feller, An Introduction to Probability Theory, 1950"),
    ("sophiste", False, "Au jeu de Monty Hall, une fois une porte perdante ouverte, garder ou changer de porte revient au même.",
     "Changer fait gagner 2 fois sur 3 : le présentateur, qui sait où est la voiture, n'ouvre jamais la bonne porte.",
     "En 1990, Marilyn vos Savant donne la bonne réponse dans le magazine Parade. Elle reçoit des milliers de lettres, dont beaucoup de docteurs, pour lui dire qu'elle se trompe.",
     "Marilyn vos Savant, Parade, 9 septembre 1990"),
    ("sophiste", False, "Un test fiable à 99 % est positif : il y a donc 99 % de chances d'être malade.",
     "Tout dépend de la rareté de la maladie. Si elle touche 1 personne sur 10 000, la plupart des tests positifs sont de faux positifs.",
     "On confond la fiabilité du test et la probabilité d'être malade. Le théorème de Bayes fait le lien, et des médecins s'y trompent aussi.",
     "Gerd Gigerenzer, Calculated Risks, 2002"),
    ("sophiste", False, "Pendant la guerre, il fallait blinder les avions là où ceux qui rentraient avaient le plus d'impacts.",
     "Il fallait blinder là où ils n'en avaient pas : les avions touchés à ces endroits-là ne rentraient pas.",
     "C'est le biais du survivant, mis en évidence par le statisticien Abraham Wald en 1943.",
     "Abraham Wald, Statistical Research Group, Columbia, 1943"),
    ("sophiste", True, "Dans beaucoup de données réelles, le premier chiffre est un 1 dans environ 30 % des cas.",
     "C'est la loi de Benford : le 1 sort environ 30 % du temps, le 9 moins de 5 %. Elle sert à repérer des comptes truqués.",
     "Simon Newcomb la remarque en 1881 en voyant les premières pages des tables de logarithmes plus usées que les autres.",
     "Frank Benford, Proceedings of the American Philosophical Society, 1938"),
    ("sophiste", True, "Une petite maternité connaît plus souvent qu'une grande des jours où plus de 60 % des bébés sont des garçons.",
     "Moins il y a de naissances, plus les proportions varient d'un jour à l'autre. C'est la loi des grands nombres, à l'envers.",
     "Dans l'expérience de Kahneman et Tversky, la plupart des gens répondaient que les deux maternités étaient à égalité.",
     "Kahneman et Tversky, Cognitive Psychology, 1972"),
    ("sophiste", True, "Zénon d'Élée soutenait qu'Achille ne rattraperait jamais une tortue partie avant lui.",
     "C'est son célèbre paradoxe : chaque fois qu'Achille atteint la position de la tortue, elle a un peu avancé. Les séries infinies montrent qu'une somme infinie de durées peut être finie.",
     "Aristote rapporte le paradoxe pour le réfuter.",
     "Aristote, Physique, VI, 9"),

    # Le Platiste : la Terre et le ciel
    ("platiste", False, "Au Moyen Âge, les savants pensaient que la Terre était plate.",
     "Les savants médiévaux la savaient ronde. Le manuel d'astronomie le plus lu, le De sphaera de Sacrobosco (vers 1230), l'explique dès son titre.",
     "Le mythe est inventé au XIXe siècle, notamment par la biographie romancée de Christophe Colomb écrite par Washington Irving en 1828.",
     "Jeffrey Burton Russell, Inventing the Flat Earth, 1991"),
    ("platiste", False, "Christophe Colomb avait raison sur la taille de la Terre contre les savants qui doutaient de son projet.",
     "Les savants avaient raison : Colomb croyait la Terre bien plus petite. Sans l'Amérique sur sa route, son équipage serait mort de faim.",
     "Le récit héroïque d'un Colomb seul contre l'obscurantisme vient lui aussi de Washington Irving.",
     "Samuel Eliot Morison, Admiral of the Ocean Sea, 1942"),
    ("platiste", False, "La Grande Muraille de Chine est visible à l'œil nu depuis la Lune.",
     "Elle est large de quelques mètres : même depuis l'orbite basse, on la distingue à peine. Le premier astronaute chinois, Yang Liwei, a dit ne pas l'avoir vue.",
     "L'affirmation apparaît dès 1938 dans un livre de Richard Halliburton, trente ans avant que quiconque aille sur la Lune.",
     "Richard Halliburton, Second Book of Marvels, 1938 ; Yang Liwei, 2003"),
    ("platiste", False, "Il fait plus chaud en été parce que la Terre est alors plus près du Soleil.",
     "Les saisons viennent de l'inclinaison de l'axe de la Terre. La Terre est même au plus près du Soleil début janvier, en plein hiver de l'hémisphère nord.",
     "Une erreur très répandue : dans le documentaire A Private Universe, la plupart des diplômés de Harvard interrogés la commettent.",
     "A Private Universe, Harvard-Smithsonian Center for Astrophysics, 1987"),
    ("platiste", False, "L'eau d'un lavabo tourne dans un sens dans l'hémisphère nord et dans l'autre dans l'hémisphère sud.",
     "La force de Coriolis est bien trop faible à cette échelle. Le sens dépend de la forme du lavabo et de l'eau versée.",
     "Une démonstration de touristes très populaire sur l'équateur, au Kenya ou en Équateur, où le guide tourne discrètement l'eau.",
     "Ascher Shapiro, Nature, 1962"),
    ("platiste", False, "Il n'y a pas de gravité dans la Station spatiale internationale.",
     "À 400 km d'altitude, la pesanteur vaut encore environ 90 % de celle du sol. Les astronautes flottent parce que la station et eux tombent ensemble autour de la Terre.",
     "On confond apesanteur et absence de gravité. Newton l'expliquait déjà avec un boulet tiré du haut d'une montagne.",
     "Isaac Newton, Principia, livre III, 1687"),
    ("platiste", False, "La face cachée de la Lune est toujours plongée dans le noir.",
     "Elle est cachée, pas sombre : elle est pleinement éclairée à la nouvelle lune. La Lune nous montre toujours la même face parce qu'elle tourne sur elle-même au rythme de son orbite.",
     "L'expression anglaise « dark side of the Moon » a fait le reste.",
     "NASA, Moon facts"),
    ("platiste", True, "Ératosthène a mesuré la circonférence de la Terre vers 240 avant notre ère avec des ombres.",
     "À midi au solstice, le Soleil éclaire le fond d'un puits à Syène, mais fait une ombre à Alexandrie. L'angle et la distance entre les deux villes donnent la taille de la Terre, à quelques pour cent près selon la valeur du stade.",
     "Le récit nous est parvenu par Cléomède.",
     "Cléomède, Théorie élémentaire, I, 10"),
    ("platiste", True, "Aristote prouvait que la Terre est ronde par l'ombre qu'elle projette sur la Lune pendant les éclipses.",
     "Cette ombre est toujours un arc de cercle, quelle que soit la position de la Lune : seule une sphère fait ça.",
     "Aristote ajoutait que les étoiles visibles changent quand on voyage vers le sud.",
     "Aristote, Du ciel, II, 14"),
    ("platiste", True, "Au bord de la mer, on voit disparaître la coque d'un bateau qui s'éloigne avant son mât.",
     "La courbure de la Terre cache d'abord le bas du bateau. C'est l'un des arguments classiques de la rotondité de la Terre.",
     "Le géographe Strabon le notait déjà au Ier siècle.",
     "Strabon, Géographie, I, 1, 20"),

    # L'Influenceur détox : alimentation
    ("influenceur", False, "Les cures détox débarrassent le corps de ses toxines.",
     "Aucune étude sérieuse ne montre qu'elles éliminent quoi que ce soit. Le foie et les reins s'en chargent en permanence.",
     "Un argument de vente : les produits nomment rarement les toxines qu'ils prétendent éliminer.",
     "Klein et Kiat, Journal of Human Nutrition and Dietetics, 2015"),
    ("influenceur", False, "Le sucre rend les enfants hyperactifs.",
     "Les essais en double aveugle ne trouvent aucun effet. Mais des parents qui croient leur enfant sucré le jugent plus agité.",
     "L'idée se répand dans les années 1970 avec le régime du pédiatre Benjamin Feingold.",
     "Wolraich et al., JAMA, 1995 ; Hoover et Milich, 1994"),
    ("influenceur", False, "On croit les épinards très riches en fer à cause d'une virgule mal placée par un chimiste.",
     "L'histoire de la virgule est elle-même un mythe : aucune trace de cette erreur dans les publications d'époque. Un mythe sur un mythe.",
     "Elle apparaît en 1981 dans un article du British Medical Journal, sans source, puis se répand comme exemple… de rigueur scientifique.",
     "Mike Sutton, Internet Journal of Criminology, 2010"),
    ("influenceur", False, "Un verre de jus de citron le matin rend le sang plus alcalin.",
     "Le pH du sang reste entre 7,35 et 7,45, réglé par les poumons et les reins, quoi qu'on mange. Hors de cet intervalle, on est à l'hôpital.",
     "Une idée des régimes « alcalins » des années 2000.",
     "Fenton et Huang, BMJ Open, 2016"),
    ("influenceur", False, "Le gluten est mauvais pour la santé de tout le monde.",
     "Il pose problème aux malades cœliaques et à quelques intolérants. Chez les autres, l'éviter n'apporte rien et prive souvent de céréales complètes.",
     "La vogue du « sans gluten » démarre aux États-Unis vers 2010, portée par des livres de régime.",
     "Lebwohl et al., BMJ, 2017"),
    ("influenceur", False, "Le glutamate des plats asiatiques provoque un « syndrome du restaurant chinois ».",
     "Les essais en double aveugle ne reproduisent pas ce syndrome. Le glutamate est aussi présent dans les tomates et le parmesan.",
     "Une simple lettre d'un médecin au New England Journal of Medicine en 1968, intitulée « Chinese-Restaurant Syndrome ».",
     "Geha et al., Journal of Allergy and Clinical Immunology, 2000"),
    ("influenceur", False, "Les micro-ondes rendent les aliments radioactifs.",
     "Les micro-ondes agitent les molécules d'eau pour chauffer. Elles ne sont pas ionisantes et ne laissent rien dans les aliments.",
     "On confond les ondes radio avec les rayonnements radioactifs.",
     "Organisation mondiale de la santé, « Les fours à micro-ondes », 2005"),
    ("influenceur", False, "Manger beaucoup de carottes donne une vision nocturne de chat.",
     "Un manque de vitamine A rend aveugle la nuit, mais un excès n'améliore rien.",
     "Pendant la guerre, la propagande britannique vante les carottes des pilotes de nuit, comme John Cunningham, alors que leur secret est le radar.",
     "John Stolarczyk, World Carrot Museum ; ministère britannique de l'Alimentation, 1940"),
    ("influenceur", True, "En 1747, James Lind a comparé six traitements du scorbut sur douze marins, et seuls les agrumes ont marché.",
     "C'est l'un des premiers essais cliniques comparatifs. Il faudra pourtant attendre 1795 pour que la Royal Navy distribue du jus de citron.",
     "Lind publie ses résultats en 1753.",
     "James Lind, A Treatise of the Scurvy, 1753"),
    ("influenceur", True, "Une banane est légèrement radioactive.",
     "Elle contient du potassium, dont une petite partie est du potassium 40 radioactif. La dose est infime : on parle même de « dose équivalent banane ».",
     "Les physiciens s'en servent pour expliquer les ordres de grandeur.",
     "Health Physics Society, « Ask the Experts »"),

    # L'Astrologue : astres et prédictions
    ("astrologue", False, "Il y a plus d'accouchements les nuits de pleine lune.",
     "Une étude sur plus de 500 000 naissances ne trouve aucun lien avec les phases de la Lune.",
     "Une croyance tenace dans les maternités, entretenue par le souvenir des nuits chargées.",
     "Arliss et al., American Journal of Obstetrics and Gynecology, 2005"),
    ("astrologue", False, "Le signe astrologique influence la personnalité.",
     "En double aveugle, des astrologues n'ont pas su relier les thèmes astraux aux profils de personnalité mieux que le hasard.",
     "Une tradition babylonienne et grecque, codifiée par Ptolémée dans son Tetrabiblos.",
     "Shawn Carlson, Nature, 1985"),
    ("astrologue", False, "Le Soleil se trouve aujourd'hui dans la constellation de votre signe le jour de votre anniversaire.",
     "À cause de la précession des équinoxes, les signes ont glissé d'environ une constellation depuis l'Antiquité. Un Bélier naît aujourd'hui avec le Soleil dans les Poissons.",
     "Les signes ont été fixés il y a plus de 2 000 ans. Hipparque découvre la précession vers 130 avant notre ère.",
     "Hipparque, rapporté par Ptolémée, Almageste, VII"),
    ("astrologue", False, "Le Soleil traverse douze constellations de même taille, une par mois.",
     "Il en traverse treize, avec le Serpentaire, et de tailles très inégales : il reste environ 7 jours dans le Scorpion, plus de 40 dans la Vierge.",
     "Les douze signes sont des découpages égaux de 30°, pas les vraies constellations.",
     "Union astronomique internationale, délimitation d'Eugène Delporte, 1930"),
    ("astrologue", False, "Quand Mercure est rétrograde, la planète change vraiment de sens sur son orbite.",
     "Elle continue sa route. C'est un effet de perspective : la Terre et Mercure tournent à des vitesses différentes, comme une voiture qu'on double semble reculer.",
     "Ptolémée expliquait la rétrogradation par des épicycles. Copernic la rend évidente avec le Soleil au centre.",
     "Nicolas Copernic, De revolutionibus, 1543"),
    ("astrologue", False, "Une bonne partie des étoiles visibles à l'œil nu sont déjà mortes.",
     "La plupart sont à quelques centaines d'années-lumière et vivent des millions d'années : leur lumière est récente à cette échelle.",
     "Une image poétique qui confond quelques cas célèbres avec la règle.",
     "Catalogue Hipparcos, Agence spatiale européenne, 1997"),
    ("astrologue", False, "La Lune agit sur notre corps comme sur les marées, puisque nous sommes faits d'eau.",
     "La marée vient de la différence d'attraction entre deux côtés d'un objet. Sur un corps humain, cette différence est infime ; la Lune soulève l'océan parce qu'il est grand comme une planète.",
     "Un argument d'analogie qui oublie l'échelle.",
     "Isaac Newton, Principia, livre III, 1687"),
    ("astrologue", True, "En 1948, des étudiants ont jugé très juste un portrait psychologique qui était le même pour tous.",
     "Bertram Forer leur distribue un texte vague tiré d'horoscopes. Note moyenne de justesse : 4,3 sur 5. C'est l'effet Barnum.",
     "On reconnaît dans les phrases floues ce qu'on veut y voir.",
     "Bertram Forer, Journal of Abnormal and Social Psychology, 1949"),
    ("astrologue", True, "En 1910, on a vendu des « pilules anti-comète » contre les gaz de la comète de Halley.",
     "Des astronomes avaient détecté du cyanogène dans sa queue, et la Terre devait la traverser. Des marchands en ont profité. Il ne s'est rien passé.",
     "La presse avait relayé l'inquiétude de quelques savants, dont Camille Flammarion.",
     "The New York Times, mai 1910"),
    ("astrologue", True, "Johannes Kepler, qui a découvert les lois du mouvement des planètes, faisait des horoscopes.",
     "C'était une partie de son métier de mathématicien impérial. Il disait que l'astrologie était la fille folle de l'astronomie, qui nourrit sa mère.",
     "À l'époque, les deux disciplines n'étaient pas séparées.",
     "Johannes Kepler, De fundamentis astrologiae certioribus, 1601"),

    # Mesmer : esprit et cerveau
    ("mesmer", False, "Un « fluide magnétique animal » peut guérir les malades.",
     "Les commissaires de 1784 bandent les yeux des patients : ils réagissent quand ils croient être magnétisés, pas quand ils le sont. Conclusion : c'est l'imagination.",
     "Mesmer présente sa théorie à Vienne en 1775, puis fait fortune à Paris.",
     "Rapport des commissaires, avec Franklin et Lavoisier, 1784"),
    ("mesmer", False, "Nous n'utilisons que 10 % de notre cerveau.",
     "L'imagerie montre que toutes les régions servent, et une lésion n'importe où a des conséquences.",
     "Une déformation de propos de psychologues du début du XXe siècle, popularisée par la préface d'un livre de Dale Carnegie en 1936.",
     "Vreeman et Carroll, « Medical myths », BMJ, 2007"),
    ("mesmer", False, "Écouter du Mozart rend les bébés plus intelligents.",
     "L'étude d'origine portait sur des étudiants, avec un léger effet de quelques minutes. Les méta-analyses n'ont rien trouvé de durable.",
     "Un article de 1993 dans Nature, transformé en CD pour bébés. L'État de Géorgie a même offert un disque classique à chaque nouveau-né.",
     "Chabris, Nature, 1999 ; Pietschnig et al., Intelligence, 2010"),
    ("mesmer", False, "On apprend mieux quand l'enseignement suit son style d'apprentissage, visuel, auditif ou kinesthésique.",
     "Les études bien conçues ne trouvent pas cet effet. Le meilleur format dépend surtout de ce qu'on apprend.",
     "Un modèle très vendu aux enseignants depuis les années 1970.",
     "Pashler et al., Psychological Science in the Public Interest, 2008"),
    ("mesmer", False, "Chacun est plutôt « cerveau gauche », logique, ou « cerveau droit », créatif.",
     "Une étude de plus de 1 000 cerveaux ne trouve pas de personnes plus « gauche » ou plus « droite ». Certaines fonctions sont latéralisées, pas les personnalités.",
     "Une vulgarisation abusive des travaux de Roger Sperry sur les cerveaux divisés, prix Nobel 1981.",
     "Nielsen et al., PLoS ONE, 2013"),
    ("mesmer", False, "Le détecteur de mensonges repère les menteurs de façon fiable.",
     "Il mesure le stress, pas le mensonge. Un innocent anxieux échoue, un menteur calme passe.",
     "Inventé en 1921 par John Larson ; l'un de ses promoteurs, William Marston, créera Wonder Woman et son lasso de vérité.",
     "National Research Council, The Polygraph and Lie Detection, 2003"),
    ("mesmer", False, "Des images subliminales « Buvez Coca-Cola » projetées au cinéma ont fait bondir les ventes.",
     "L'expérience n'a jamais eu lieu comme annoncé. Son auteur, James Vicary, a reconnu en 1962 avoir arrangé les chiffres.",
     "Vicary annonce ses résultats en 1957 pour lancer son entreprise.",
     "Advertising Age, entretien avec James Vicary, 1962"),
    ("mesmer", True, "Un cheval, Hans le Malin, semblait savoir compter, mais lisait en fait les gestes involontaires de son public.",
     "Le psychologue Oskar Pfungst montre en 1907 qu'il se trompe dès que le questionneur ignore la réponse.",
     "On appelle depuis « effet Hans le Malin » l'influence involontaire de l'expérimentateur.",
     "Oskar Pfungst, Clever Hans, 1907"),
    ("mesmer", True, "Dans une expérience célèbre, la majorité des participants ont accepté d'envoyer des chocs électriques apparemment dangereux sur ordre.",
     "Dans l'expérience de Milgram, 65 % vont jusqu'à 450 volts. Les chocs étaient simulés par un complice.",
     "Milgram cherchait à comprendre l'obéissance après le procès Eichmann.",
     "Stanley Milgram, Journal of Abnormal and Social Psychology, 1963"),
    ("mesmer", True, "Des volontaires occupés à compter des passes de ballon n'ont pas vu un gorille traverser la scène.",
     "Environ la moitié ne voit pas l'étudiant déguisé en gorille. C'est la cécité d'inattention.",
     "L'expérience de Simons et Chabris est devenue un classique de la psychologie de l'attention.",
     "Simons et Chabris, Perception, 1999"),

    # Lyssenko : le vivant
    ("lyssenko", False, "Les caractères acquis au cours de la vie se transmettent aux descendants : la girafe a allongé son cou à force de l'étirer.",
     "Ce sont les gènes qui se transmettent. Les girafes au cou un peu plus long ont mieux survécu et eu plus de petits.",
     "L'idée remonte à Lamarck. En URSS, Lyssenko en fait une doctrine d'État et persécute les généticiens.",
     "August Weismann, Essays upon Heredity, 1889"),
    ("lyssenko", False, "L'humain descend du chimpanzé.",
     "Nous partageons avec lui un ancêtre commun qui vivait il y a environ 6 à 7 millions d'années. Le chimpanzé a évolué aussi longtemps que nous.",
     "Une caricature de Darwin, dessiné avec un corps de singe dès 1871.",
     "Chimpanzee Sequencing and Analysis Consortium, Nature, 2005"),
    ("lyssenko", False, "Notre corps contient dix fois plus de cellules bactériennes que de cellules humaines.",
     "Une estimation récente donne à peu près autant des deux, environ 38 000 milliards de bactéries pour 30 000 milliards de cellules humaines.",
     "Le chiffre de dix pour un vient d'un calcul rapide de 1972, recopié pendant quarante ans.",
     "Sender, Fuchs et Milo, PLoS Biology, 2016"),
    ("lyssenko", False, "L'évolution mène vers des espèces de plus en plus parfaites.",
     "La sélection naturelle n'a pas de but : elle favorise ce qui marche dans un milieu donné. Les bactéries, apparues il y a plus de 3 milliards d'années, se portent très bien.",
     "L'image populaire d'une échelle qui monte jusqu'à l'humain, que Darwin évitait.",
     "Charles Darwin, L'Origine des espèces, 1859"),
    ("lyssenko", False, "Les poissons rouges ont une mémoire de trois secondes.",
     "Des poissons rouges ont appris à pousser un levier pour obtenir de la nourriture, et à le faire à une heure précise. Ils retiennent ce genre d'apprentissage pendant des semaines.",
     "Une phrase répétée par les vendeurs d'aquariums, jamais mesurée.",
     "Phil Gee, université de Plymouth, 2003"),
    ("lyssenko", False, "La « vernalisation » de Lyssenko a multiplié les récoltes de blé soviétiques.",
     "Ses promesses ne se sont jamais réalisées, et ses méthodes ont aggravé les pénuries. La génétique n'est réhabilitée en URSS qu'en 1965.",
     "Des résultats annoncés dans la presse du parti, sans essais contrôlés.",
     "Zhores Medvedev, The Rise and Fall of T. D. Lysenko, 1969"),
    ("lyssenko", False, "Les autruches enfouissent leur tête dans le sable quand elles ont peur.",
     "Elles s'aplatissent au sol ou s'enfuient à 70 km/h. Elles plongent aussi la tête dans leur nid creusé au sol pour retourner leurs œufs.",
     "L'idée est déjà chez Pline l'Ancien.",
     "Pline l'Ancien, Histoire naturelle, X, 1"),
    ("lyssenko", True, "Le généticien Nikolaï Vavilov, opposant de Lyssenko, est mort de faim en prison.",
     "Arrêté en 1940, il meurt en 1943 à Saratov. Il avait constitué l'une des plus grandes collections de semences du monde, que ses collègues ont protégée pendant le siège de Leningrad.",
     "Son histoire n'a été racontée librement qu'après la chute de Lyssenko.",
     "Peter Pringle, The Murder of Nikolai Vavilov, 2008"),
    ("lyssenko", True, "Des tardigrades ont survécu à une exposition directe au vide spatial.",
     "En 2007, sur la mission FOTON-M3, des tardigrades déshydratés sont restés dix jours dans l'espace. Certains ont survécu et se sont reproduits.",
     "Ces animaux de moins d'un millimètre résistent à des conditions extrêmes en se déshydratant.",
     "Jönsson et al., Current Biology, 2008"),
    ("lyssenko", True, "Gregor Mendel a publié ses lois de l'hérédité en 1866, mais elles ont été ignorées pendant 34 ans.",
     "Elles sont redécouvertes en 1900 par trois botanistes, de Vries, Correns et Tschermak.",
     "Mendel était moine, publiait dans une revue locale, et devint abbé avant qu'on le lise.",
     "Gregor Mendel, Versuche über Pflanzen-Hybriden, 1866"),

    # Le Complotiste : fausses nouvelles et vrais complots
    ("complotiste", False, "Les traînées blanches des avions sont des produits chimiques épandus en secret.",
     "Ce sont des traînées de condensation : la vapeur d'eau des moteurs gèle dans l'air froid. Sur 77 spécialistes interrogés, 76 n'ont trouvé aucune trace d'un programme secret.",
     "La théorie des « chemtrails » se répand à partir de 1996, après un exercice de prospective de l'armée de l'air américaine sur le contrôle de la météo.",
     "Shearer et al., Environmental Research Letters, 2016"),
    ("complotiste", False, "Les missions Apollo sur la Lune ont été tournées en studio.",
     "Des réflecteurs laissés par Apollo 11, 14 et 15 renvoient encore des tirs laser, et la sonde LRO a photographié les sites d'alunissage.",
     "Le livre de Bill Kaysing, We Never Went to the Moon, publié à compte d'auteur en 1976.",
     "NASA, Lunar Reconnaissance Orbiter, 2011"),
    ("complotiste", False, "Les vaccins provoquent l'autisme.",
     "Une étude sur plus de 650 000 enfants danois ne trouve aucun lien. L'article qui l'affirmait était frauduleux.",
     "L'article d'Andrew Wakefield dans The Lancet en 1998, retiré en 2010 ; Wakefield a été radié de l'ordre des médecins.",
     "Hviid et al., Annals of Internal Medicine, 2019"),
    ("complotiste", False, "Les pyramides d'Égypte sont trop parfaites pour avoir été construites par des humains de l'époque.",
     "On a retrouvé les villages des ouvriers à Gizeh, leurs tombes, et le journal de l'inspecteur Merer qui raconte le transport des blocs.",
     "Popularisée en 1968 par Erich von Däniken dans Présence des extraterrestres.",
     "Pierre Tallet, Les Papyrus de la mer Rouge, 2017"),
    ("complotiste", False, "Les antennes 5G propagent le Covid-19.",
     "Un virus ne voyage pas par ondes radio. L'épidémie a touché des pays qui n'avaient pas de 5G.",
     "Une rumeur de début 2020 ; au Royaume-Uni, des antennes ont été incendiées.",
     "Organisation mondiale de la santé, « Mythbusters », 2020"),
    ("complotiste", False, "On a photographié un visage sculpté sur Mars.",
     "La sonde Viking 1 a photographié en 1976 une colline qui ressemble à un visage sous un certain éclairage. Les photos à haute résolution de 2001 montrent une simple butte.",
     "C'est de la paréidolie, notre tendance à voir des visages partout.",
     "NASA, Mars Global Surveyor, 2001"),
    ("complotiste", False, "L'émission radio La Guerre des mondes d'Orson Welles a déclenché une panique massive aux États-Unis en 1938.",
     "Très peu de gens l'écoutaient, et les témoignages de panique sont rares. Les journaux, concurrencés par la radio, ont gonflé l'histoire.",
     "Une fausse nouvelle sur une fausse nouvelle, née dans la presse du lendemain.",
     "A. Brad Schwartz, Broadcast Hysteria, 2015"),
    ("complotiste", True, "Des médecins américains ont laissé des hommes atteints de syphilis sans traitement pendant 40 ans, pour observer la maladie.",
     "L'étude de Tuskegee dure de 1932 à 1972, même après l'arrivée de la pénicilline. Elle est révélée par la journaliste Jean Heller.",
     "Un vrai complot, établi par des documents et des enquêtes, qui a changé les règles de l'éthique médicale.",
     "Associated Press, Jean Heller, 1972"),
    ("complotiste", True, "La CIA a fait prendre du LSD à des personnes sans leur consentement.",
     "Le programme MKUltra, de 1953 à 1973, est révélé par une commission du Sénat. La plupart des archives avaient été détruites, mais pas toutes.",
     "Les vrais complots finissent souvent par laisser des documents.",
     "Audition du Sénat des États-Unis sur MKUltra, 1977"),
    ("complotiste", True, "En 1962, l'état-major américain a proposé de simuler des attentats pour justifier une guerre contre Cuba.",
     "C'est l'opération Northwoods. Le gouvernement Kennedy l'a refusée. Le document a été déclassifié en 1997.",
     "Une proposition réelle, connue grâce aux archives publiques, et jamais mise en œuvre.",
     "National Security Archive, Northwoods, 1997"),

    # Le Charlatan : médecine
    ("charlatan", False, "L'homéopathie est plus efficace qu'un placebo.",
     "L'analyse de 176 études par l'agence de santé australienne ne trouve aucune maladie pour laquelle elle fasse mieux qu'un placebo. Elle n'est plus remboursée en France depuis 2021.",
     "Inventée par Samuel Hahnemann en 1796.",
     "NHMRC, Australie, 2015 ; Haute Autorité de santé, 2019"),
    ("charlatan", False, "Les antibiotiques soignent la grippe.",
     "La grippe est due à un virus, les antibiotiques n'agissent que sur les bactéries. Les prendre pour rien favorise les résistances.",
     "Une confusion si répandue qu'elle a eu sa campagne : « Les antibiotiques, c'est pas automatique ».",
     "Assurance maladie, campagne de 2002"),
    ("charlatan", False, "Le sang de nos veines est bleu tant qu'il n'a pas touché l'air.",
     "Il est rouge sombre. Les veines paraissent bleues parce que la peau laisse mieux revenir la lumière bleue que la rouge.",
     "Les schémas qui colorient veines et artères en bleu et rouge.",
     "Kienle et al., Applied Optics, 1996"),
    ("charlatan", False, "Se baigner juste après un repas expose à des crampes qui font couler.",
     "Une revue de la Croix-Rouge américaine n'a trouvé aucun cas documenté de noyade lié à la digestion.",
     "Un conseil de prudence répété depuis des générations.",
     "American Red Cross Scientific Advisory Council, 2011"),
    ("charlatan", False, "La vitamine C à haute dose protège du rhume.",
     "Chez la plupart des gens, elle ne réduit pas le nombre de rhumes, et ne raccourcit leur durée que d'un peu.",
     "Le double prix Nobel Linus Pauling en fait la promotion dans un livre de 1970.",
     "Hemilä et Chalker, Cochrane, 2013"),
    ("charlatan", False, "Les cheveux et les ongles continuent de pousser après la mort.",
     "La peau se déshydrate et se rétracte, ce qui les fait paraître plus longs. La pousse demande des cellules vivantes.",
     "Des observations de croque-morts, mal interprétées.",
     "Vreeman et Carroll, « Medical myths », BMJ, 2007"),
    ("charlatan", False, "Il faut boire au moins huit verres d'eau par jour en plus de ce qu'on mange.",
     "Aucune étude ne le justifie. Une bonne partie de l'eau vient des aliments et des autres boissons.",
     "Une recommandation américaine de 1945 précisait que l'essentiel de cette eau se trouvait dans les aliments. Cette phrase a été oubliée.",
     "Vreeman et Carroll, « Medical myths », BMJ, 2007"),
    ("charlatan", True, "George Washington est mort après qu'on lui a retiré environ 40 % de son sang pour le soigner.",
     "En décembre 1799, ses médecins pratiquent quatre saignées en une journée pour une infection de la gorge.",
     "La saignée était un traitement courant depuis l'Antiquité.",
     "Vadakan, The Permanente Journal, 2005"),
    ("charlatan", True, "Semmelweis a fait chuter la mortalité d'une maternité en imposant le lavage des mains, et ses collègues l'ont rejeté.",
     "À Vienne en 1847, la mortalité tombe d'environ 10 % à environ 1 %. Mais il ne sait pas l'expliquer, et ses collègues se vexent d'être accusés.",
     "Pasteur et Lister lui donneront raison vingt ans plus tard.",
     "Ignace Semmelweis, Die Ätiologie… des Kindbettfiebers, 1861"),
    ("charlatan", True, "Un placebo peut soulager même quand le patient sait que c'est un placebo.",
     "Dans un essai sur le syndrome de l'intestin irritable, des patients prévenus ont quand même vu leurs symptômes diminuer.",
     "L'effet placebo tient aussi au rituel du soin.",
     "Kaptchuk et al., PLoS ONE, 2010"),

    # v15 — Pline l'Ancien : les animaux
    ("pline", False, "Les lemmings se jettent en masse du haut des falaises.",
     "Leurs populations explosent puis s'effondrent tous les trois ou quatre ans, et ils migrent alors en nombre. Ils ne se suicident pas.",
     "Le documentaire Disney White Wilderness (1958), dont l'équipe a elle-même poussé des lemmings dans une rivière.",
     "Brian Vallee, CBC, 1982 ; Alaska Department of Fish and Game"),
    ("pline", False, "La couleur rouge rend les taureaux furieux.",
     "Les bovins distinguent mal le rouge. C'est le mouvement de la cape qui déclenche la charge : agitée, une cape bleue fait le même effet.",
     "La muleta des corridas est rouge, surtout pour masquer le sang.",
     "MythBusters, Discovery Channel, 2007"),
    ("pline", False, "Les chauves-souris sont aveugles.",
     "Toutes voient, et les grandes roussettes ont même une très bonne vue. Beaucoup s'orientent aussi par écholocation.",
     "En 1793, Spallanzani constate que des chauves-souris aux yeux bandés évitent encore les obstacles. On en a conclu qu'elles n'avaient pas besoin de leurs yeux.",
     "Donald Griffin, Listening in the Dark, 1958"),
    ("pline", False, "Un ver de terre coupé en deux donne deux vers.",
     "Au mieux, la partie qui porte la tête survit et refait une queue. L'autre moitié meurt.",
     "Une confusion avec les planaires, des vers plats qui, eux, reforment un individu entier à partir d'un morceau.",
     "Thomas Hunt Morgan, Regeneration, 1901"),
    ("pline", False, "Les dromadaires stockent de l'eau dans leur bosse.",
     "La bosse est une réserve de graisse. Leur endurance vient de reins très économes et de globules rouges qui supportent de gonfler quand ils boivent d'un coup.",
     "Une explication intuitive : une bosse pour la traversée.",
     "Knut Schmidt-Nielsen, Desert Animals, 1964"),
    ("pline", False, "Le porc-épic projette ses piquants sur ses ennemis.",
     "Il ne peut pas les lancer. Les piquants se détachent au contact et restent plantés dans l'agresseur.",
     "Pline l'Ancien l'affirme dans son Histoire naturelle, et la légende a traversé les siècles.",
     "Pline l'Ancien, Histoire naturelle, VIII, 53"),
    ("pline", False, "Les hirondelles passent l'hiver endormies au fond des étangs.",
     "Elles migrent jusqu'en Afrique. Le baguage des oiseaux le montre au début du XXe siècle.",
     "Aristote parle d'hirondelles qui se cachent en hiver. En 1555, l'archevêque Olaus Magnus dessine des pêcheurs qui les remontent dans leurs filets.",
     "Olaus Magnus, Histoire des peuples septentrionaux, 1555"),
    ("pline", True, "Les deux tiers des neurones d'une pieuvre se trouvent dans ses bras.",
     "Sur environ 500 millions de neurones, la plupart sont dans les bras, qui peuvent goûter, saisir et réagir sans attendre le cerveau.",
     "Des comptages de neurones et des expériences sur des bras isolés.",
     "Peter Godfrey-Smith, Other Minds, 2016"),
    ("pline", True, "Les corneilles reconnaissent un visage humain et s'en souviennent des années.",
     "À Seattle, des chercheurs masqués ont capturé quelques corneilles. Des années plus tard, les oiseaux criaient encore contre ce masque, y compris ceux qui n'avaient jamais été capturés.",
     "Une expérience menée avec des masques de caoutchouc, pour séparer le visage de la personne.",
     "John Marzluff et al., Animal Behaviour, 2010"),
    ("pline", True, "En 1822, une cigogne est arrivée en Allemagne avec une flèche africaine plantée dans le cou.",
     "Cette « cigogne à flèche » a prouvé que les cigognes hivernaient en Afrique, à une époque où l'on doutait encore des grandes migrations.",
     "L'oiseau naturalisé est toujours exposé à l'université de Rostock.",
     "Université de Rostock, collection zoologique"),

    # Franz Joseph Gall : le cerveau et les sens
    ("gall", False, "On repère un menteur à son regard, qui part vers le haut et vers la droite.",
     "Des chercheurs ont filmé des personnes qui mentaient ou disaient vrai : la direction du regard ne permettait pas de les distinguer.",
     "La « programmation neuro-linguistique » des années 1970.",
     "Richard Wiseman et al., PLoS ONE, 2012"),
    ("gall", False, "Le détecteur de mensonges détecte les mensonges.",
     "Le polygraphe mesure le stress : pouls, respiration, sueur. Un innocent anxieux peut échouer, un menteur calme peut réussir.",
     "Inventé en 1921 par John Larson, popularisé par William Marston, qui a aussi créé Wonder Woman et son lasso de vérité.",
     "National Research Council, The Polygraph and Lie Detection, 2003"),
    ("gall", False, "La mémoire enregistre les événements comme une vidéo qu'on peut rejouer fidèlement.",
     "Chaque souvenir se reconstruit quand on le rappelle. On peut même faire croire à des gens qu'ils se sont perdus enfants dans un centre commercial.",
     "La métaphore de l'enregistrement, et l'affaire des « souvenirs retrouvés » des années 1990.",
     "Elizabeth Loftus et Jacqueline Pickrell, Psychiatric Annals, 1995"),
    ("gall", False, "Une soirée trop arrosée détruit des milliers de neurones.",
     "L'alcool perturbe les neurones et, à long terme et à forte dose, abîme leurs connexions. Mais on ne trouve pas de perte de neurones du cortex chez les grands buveurs.",
     "Une formule de prévention qui a pris le raccourci.",
     "Grethe Jensen et Bente Pakkenberg, The Lancet, 1993"),
    ("gall", False, "Nous avons cinq sens.",
     "Il faut ajouter au moins l'équilibre, la position du corps, la température et la douleur. Les physiologistes en comptent une dizaine, voire plus.",
     "La liste d'Aristote, dans De l'âme.",
     "Aristote, De l'âme, livre II ; Charles Sherrington, 1906"),
    ("gall", False, "La langue a des zones séparées pour le sucré, le salé, l'acide et l'amer.",
     "Toutes les parties de la langue qui portent des papilles perçoivent toutes les saveurs.",
     "Une thèse allemande de 1901, mal résumée en 1942 par le psychologue Edwin Boring, puis recopiée dans les manuels.",
     "David Hänig, 1901 ; Chandrashekar et al., Nature, 2006"),
    ("gall", False, "Le cerveau d'Einstein était plus gros que la moyenne.",
     "Il pesait environ 1 230 grammes, plutôt moins que la moyenne. Certaines régions avaient une forme inhabituelle, ce qui ne prouve pas grand-chose.",
     "On imagine le génie proportionnel à la taille, comme les phrénologues.",
     "Sandra Witelson et al., The Lancet, 1999"),
    ("gall", True, "Le cerveau consomme environ 20 % de l'énergie du corps au repos, pour 2 % de sa masse.",
     "Il ne s'éteint jamais : même au repos, il entretient ses neurones et leurs échanges.",
     "Des mesures de consommation d'oxygène et de glucose par imagerie.",
     "Marcus Raichle et Debra Gusnard, PNAS, 2002"),
    ("gall", True, "En 1848, Phineas Gage a survécu à une barre de fer qui lui a traversé le crâne.",
     "Il a vécu encore douze ans. Son caractère aurait changé, ce qui en a fait un cas d'école sur le rôle du lobe frontal.",
     "Le récit de son médecin, John Harlow, et le crâne conservé à Harvard.",
     "John Harlow, 1868 ; Malcolm Macmillan, An Odd Kind of Fame, 2000"),
    ("gall", True, "On peut avoir mal dans un bras qu'on n'a plus.",
     "C'est la douleur du membre fantôme. Un simple miroir, qui fait voir le bras restant à la place de l'autre, soulage certains patients.",
     "Les expériences de la « boîte à miroir » de Vilayanur Ramachandran.",
     "Ramachandran et Rogers-Ramachandran, Proceedings of the Royal Society B, 1996"),

    # James Ussher : le temps profond et l'évolution
    ("ussher", False, "Les premiers humains ont côtoyé les dinosaures.",
     "Les derniers dinosaures non aviens disparaissent il y a 66 millions d'années ; Homo sapiens a environ 300 000 ans.",
     "Les films, les dessins animés et les parcs à thème.",
     "Jean-Jacques Hublin et al., Nature, 2017"),
    ("ussher", False, "Les coquillages fossiles trouvés en montagne prouvent un déluge universel.",
     "La tectonique des plaques soulève d'anciens fonds marins : le sommet de l'Everest est fait de calcaire marin.",
     "Une explication courante jusqu'au XVIIIe siècle. Léonard de Vinci la contestait déjà : les coquillages sont rangés en couches, pas éparpillés par une crue.",
     "Léonard de Vinci, Codex Leicester, vers 1510"),
    ("ussher", False, "L'évolution, c'est le hasard pur.",
     "Les mutations surviennent au hasard, mais la sélection naturelle qui les trie ne l'est pas : elle garde ce qui marche.",
     "Un résumé trompeur du darwinisme, souvent utilisé pour le rejeter.",
     "Richard Dawkins, The Blind Watchmaker, 1986"),
    ("ussher", False, "Les dinosaures n'ont aucun lien avec les oiseaux.",
     "Les oiseaux sont des dinosaures théropodes, et beaucoup de dinosaures portaient des plumes.",
     "Les reconstitutions du XIXe siècle, en gros lézards, comme celles du Crystal Palace à Londres en 1854.",
     "Xu Xing et al., Nature, 2003"),
    ("ussher", False, "Les Néandertaliens étaient des brutes sans culture, sans rapport avec nous.",
     "Ils enterraient leurs morts et fabriquaient des parures. Les humains d'origine non africaine portent environ 2 % d'ADN néandertalien.",
     "La reconstitution voûtée de Marcellin Boule en 1911, faite d'après le squelette d'un vieil homme arthritique.",
     "Richard Green et al., Science, 2010"),
    ("ussher", False, "Les derniers mammouths avaient disparu bien avant la construction des pyramides d'Égypte.",
     "Une petite population a vécu sur l'île Wrangel, en Sibérie, jusqu'il y a environ 4 000 ans, quelques siècles après la grande pyramide de Gizeh.",
     "On imagine la préhistoire comme un bloc très lointain.",
     "Sergey Vartanyan et al., Nature, 1993"),
    ("ussher", False, "Darwin a renié l'évolution sur son lit de mort.",
     "Sa fille Henrietta a démenti en 1922 : il n'a jamais rien renié.",
     "Le récit d'une évangéliste, Lady Hope, publié en 1915, trente-trois ans après sa mort.",
     "James Moore, The Darwin Legend, 1994"),
    ("ussher", True, "Cléopâtre a vécu plus près de notre époque que de la construction de la grande pyramide.",
     "Elle meurt en 30 avant notre ère. La grande pyramide date d'environ 2560 avant notre ère, soit plus de 2 500 ans plus tôt.",
     "La chronologie des dynasties égyptiennes.",
     "Toby Wilkinson, The Rise and Fall of Ancient Egypt, 2010"),
    ("ussher", True, "Le tyrannosaure a vécu plus près de nous que du stégosaure.",
     "Le stégosaure vivait il y a environ 150 millions d'années, le tyrannosaure il y a 68 à 66 millions d'années.",
     "La datation des couches de roche où l'on trouve leurs fossiles.",
     "Natural History Museum, Londres"),
    ("ussher", True, "Un pin de Californie encore vivant a germé avant la construction des pyramides.",
     "« Mathusalem », un pin Bristlecone des Montagnes Blanches, a environ 4 800 ans.",
     "Ses cernes ont été comptés en 1957 sur une carotte prélevée dans le tronc.",
     "Edmund Schulman, National Geographic, 1958"),

    # Le Docteur Diafoirus : la santé au quotidien
    ("diafoirus", False, "Lire dans la pénombre abîme les yeux pour de bon.",
     "Cela fatigue les yeux, sans dommage durable.",
     "Un conseil de parents, de génération en génération.",
     "Rachel Vreeman et Aaron Carroll, « Medical myths », BMJ, 2007"),
    ("diafoirus", False, "Se faire craquer les doigts donne de l'arthrose.",
     "Un médecin s'est craqué les doigts d'une seule main pendant soixante ans : pas plus d'arthrose d'un côté que de l'autre. Le bruit vient d'une bulle de gaz dans l'articulation.",
     "Une mise en garde familiale. L'expérience a valu à son auteur un prix Ig Nobel en 2009.",
     "Donald Unger, Arthritis & Rheumatism, 1998"),
    ("diafoirus", False, "On perd la moitié de sa chaleur par la tête.",
     "La tête ne perd pas plus de chaleur qu'une autre partie du corps de même surface laissée nue.",
     "Une expérience militaire américaine des années 1950 : des volontaires en combinaison arctique, tête nue.",
     "Rachel Vreeman et Aaron Carroll, BMJ, 2008"),
    ("diafoirus", False, "Raser ses poils les fait repousser plus drus et plus foncés.",
     "Le rasoir coupe le poil à sa base, plus épaisse, ce qui le rend plus dur au toucher. La repousse est la même.",
     "La sensation du poil coupé net.",
     "Mildred Trotter, Anatomical Record, 1928"),
    ("diafoirus", False, "Un chewing-gum avalé reste sept ans dans l'estomac.",
     "Il n'est pas digéré, mais il est évacué en quelques jours comme les autres résidus. Seuls des enfants qui en avalaient énormément ont eu des bouchons.",
     "Une menace pour décourager les enfants.",
     "David Milov et al., Pediatrics, 1998"),
    ("diafoirus", False, "Un petit verre d'alcool réchauffe quand on a froid.",
     "Il dilate les vaisseaux de la peau : on se sent plus chaud, mais le corps perd sa chaleur plus vite. L'alcool favorise l'hypothermie.",
     "Le tonnelet des chiens saint-bernard, inventé par le peintre Edwin Landseer en 1820.",
     "Edwin Landseer, Alpine Mastiffs Reanimating a Distressed Traveller, 1820 ; Santé publique France"),
    ("diafoirus", False, "Réveiller un somnambule peut le tuer.",
     "Il sera confus, parfois agité, mais aucun décès n'est documenté. Le raccompagner doucement à son lit reste le plus simple.",
     "Une croyance ancienne autour du sommeil et de l'âme qui voyage.",
     "American Academy of Sleep Medicine"),
    ("diafoirus", True, "Avant Lister, des chirurgiens opéraient en redingote raidie de sang, et en étaient fiers.",
     "La crasse de la blouse passait pour un signe d'expérience. Lister introduit l'antisepsie au phénol en 1867.",
     "Les témoignages de l'époque victorienne réunis par les historiens de la chirurgie.",
     "Lindsey Fitzharris, The Butchering Art, 2017"),
    ("diafoirus", True, "Des médecins goûtaient l'urine de leurs patients pour reconnaître le diabète.",
     "Thomas Willis décrit au XVIIe siècle son goût sucré, « comme imprégnée de miel ». Le mot « mellitus » veut dire « miellé ».",
     "Avant les analyses chimiques, le goût était un outil de diagnostic.",
     "Thomas Willis, Pharmaceutice rationalis, 1674"),
    ("diafoirus", True, "On a vendu en pharmacie des cigarettes contre l'asthme.",
     "Jusqu'au milieu du XXe siècle, des cigarettes au datura étaient prescrites aux asthmatiques. Le datura détend un peu les bronches ; la fumée, beaucoup moins.",
     "Des publicités et des notices de pharmacie conservées.",
     "Mark Jackson, Asthma: The Biography, 2009"),

    # Johann Bessler : la physique
    ("bessler", False, "Une machine bien conçue peut produire plus d'énergie qu'elle n'en consomme.",
     "La conservation de l'énergie l'interdit. Dès 1775, l'Académie royale des sciences refuse d'examiner les projets de mouvement perpétuel.",
     "Des siècles de roues à poids, d'aimants et de vis d'Archimède en circuit fermé.",
     "Académie royale des sciences, délibération de 1775"),
    ("bessler", False, "Les vitraux anciens sont plus épais en bas parce que le verre coule lentement.",
     "À température ambiante, le verre médiéval mettrait plus que l'âge de l'Univers à s'affaisser visiblement. Les vitriers posaient le côté épais en bas.",
     "Une explication séduisante de l'épaisseur inégale des vitres anciennes.",
     "Edgar Zanotto, American Journal of Physics, 1998"),
    ("bessler", False, "Les objets lourds tombent plus vite que les légers.",
     "Sans air, tout tombe à la même vitesse. En 1971, l'astronaute David Scott lâche un marteau et une plume sur la Lune : ils touchent le sol ensemble.",
     "Aristote, et ce qu'on voit dans l'air, où une plume flotte.",
     "NASA, mission Apollo 15, 1971"),
    ("bessler", False, "Une pièce lâchée du haut de l'Empire State Building peut tuer un passant.",
     "Freinée par l'air, une pièce plafonne vers 80 km/h en tournoyant. Elle pique, sans plus.",
     "Une légende urbaine new-yorkaise.",
     "Louis Bloomfield, Université de Virginie ; MythBusters, 2003"),
    ("bessler", False, "Dans un fil électrique, les électrons filent presque à la vitesse de la lumière.",
     "Le signal se propage presque aussi vite, mais les électrons eux-mêmes avancent de quelques dixièmes de millimètre par seconde.",
     "On confond le courant, qui démarre partout à la fois, avec les électrons qui le portent.",
     "Richard Feynman, Le Cours de physique de Feynman, tome II"),
    ("bessler", False, "La chaleur est un fluide, le « calorique », qui passe du chaud au froid.",
     "La chaleur est l'agitation des particules. En 1798, Rumford le montre en forant des canons : ils chauffent tant qu'on fore, sans jamais épuiser un fluide.",
     "La théorie de Lavoisier, qui range le calorique parmi les éléments.",
     "Benjamin Thompson, comte Rumford, Philosophical Transactions, 1798"),
    ("bessler", False, "Un avion vole parce que l'air du dessus de l'aile va plus vite pour rejoindre en même temps l'air du dessous.",
     "Rien n'oblige l'air à se rejoindre : celui du dessus arrive même avant. L'aile dévie l'air vers le bas, et la différence de pression en découle.",
     "Une explication répandue dans les manuels, dite du « temps de transit égal ».",
     "NASA Glenn Research Center, « Incorrect Lift Theory »"),
    ("bessler", True, "Un même objet pèse un peu moins à l'équateur qu'aux pôles.",
     "La rotation de la Terre et le renflement de l'équateur font perdre environ 0,5 % de poids.",
     "Richer le constate en 1672 à Cayenne : son horloge à pendule y retarde.",
     "Jean Richer, 1672 ; Bureau international des poids et mesures"),
    ("bessler", True, "La tour Eiffel grandit de plus d'une dizaine de centimètres par forte chaleur.",
     "Le fer se dilate avec la chaleur. Le sommet s'écarte aussi du côté du soleil.",
     "Des mesures régulières depuis sa construction.",
     "Société d'exploitation de la tour Eiffel"),
    ("bessler", True, "Faire fondre un glaçon demande plus d'énergie que de chauffer ensuite la même eau de 0 à 50 °C.",
     "La fonte demande 334 joules par gramme, contre environ 210 pour gagner 50 degrés. C'est la chaleur latente.",
     "Joseph Black la mesure vers 1761 en regardant fondre la glace sans que sa température bouge.",
     "Joseph Black, Lectures on the Elements of Chemistry, 1803"),

    # Le Raconteur : l'histoire
    ("raconteur", False, "Napoléon était particulièrement petit.",
     "Il mesurait environ 1,69 m, dans la moyenne de son époque. Ses « cinq pieds deux pouces » français ont été lus en pouces anglais, plus courts.",
     "Les caricatures anglaises de James Gillray, qui le dessine en nain colérique.",
     "Andrew Roberts, Napoleon the Great, 2014"),
    ("raconteur", False, "Les Vikings portaient des casques à cornes.",
     "Aucun casque viking à cornes n'a été retrouvé. Le seul casque viking presque complet, celui de Gjermundbu, n'en a pas.",
     "Les costumes de l'opéra de Wagner, L'Anneau du Nibelung, en 1876.",
     "Roberta Frank, « The Invention of the Viking Horned Helmet », 2000"),
    ("raconteur", False, "Marie-Antoinette a dit : « Qu'ils mangent de la brioche ».",
     "Rousseau rapporte la phrase dans ses Confessions, écrites quand elle avait une dizaine d'années, et l'attribue à « une grande princesse ».",
     "Une phrase prêtée après coup à la reine la plus détestée de la Révolution.",
     "Jean-Jacques Rousseau, Les Confessions, livre VI ; Antonia Fraser, Marie-Antoinette, 2001"),
    ("raconteur", False, "Newton a découvert la gravitation en recevant une pomme sur la tête.",
     "Il racontait avoir vu une pomme tomber dans son jardin. Le choc sur la tête est un ajout plus tardif.",
     "Le récit de son ami William Stukeley, enjolivé ensuite.",
     "William Stukeley, Memoirs of Sir Isaac Newton's Life, 1752"),
    ("raconteur", False, "Einstein était nul en mathématiques à l'école.",
     "Il maîtrisait le calcul différentiel et intégral avant 15 ans. Quand la rumeur paraît en 1935, il la dément.",
     "Une rubrique de Ripley's Believe It or Not!, en 1935.",
     "Walter Isaacson, Einstein, 2007"),
    ("raconteur", False, "Les gladiateurs saluaient l'empereur d'un « Ave Caesar, morituri te salutant » avant chaque combat.",
     "La formule n'est attestée qu'une fois, par Suétone, lors d'une bataille navale sous Claude en 52, et prononcée par des condamnés.",
     "Le tableau de Jean-Léon Gérôme, Ave Caesar ! Morituri te salutant, en 1859.",
     "Suétone, Vie de Claude, 21"),
    ("raconteur", False, "Au Moyen Âge, personne ne se lavait.",
     "Les villes avaient des étuves, des bains publics : Paris en compte une trentaine vers 1300. La peur de la peste les fait fermer plus tard, à la Renaissance.",
     "On projette sur tout le Moyen Âge l'hygiène des siècles suivants.",
     "Georges Vigarello, Le Propre et le Sale, 1985"),
    ("raconteur", True, "L'université d'Oxford enseignait déjà quand l'empire aztèque a fondé Tenochtitlan.",
     "On enseigne à Oxford dès 1096. Tenochtitlan est fondée vers 1325.",
     "Les archives de l'université et l'archéologie de Mexico.",
     "University of Oxford ; Michael E. Smith, The Aztecs, 2012"),
    ("raconteur", True, "La dernière exécution à la guillotine en France a eu lieu l'année de la sortie de La Guerre des étoiles.",
     "Hamida Djandoubi est exécuté à Marseille le 10 septembre 1977 ; le film sort aux États-Unis en mai 1977. La peine de mort est abolie en 1981.",
     "Les archives judiciaires.",
     "Ministère de la Justice"),
    ("raconteur", True, "Les Romains lavaient leur linge à l'urine.",
     "Les foulons utilisaient l'ammoniac de l'urine collectée dans des jarres. Vespasien taxe cette urine : d'où « l'argent n'a pas d'odeur ».",
     "Suétone rapporte la réplique de Vespasien à son fils.",
     "Suétone, Vie de Vespasien, 23"),

    # Cesare Lombroso : la psychologie
    ("lombroso", False, "La pleine lune fait monter les crimes et les admissions aux urgences.",
     "Les études qui comptent vraiment les cas ne trouvent pas de lien. On retient seulement les nuits agitées de pleine lune.",
     "Une croyance qui a donné le mot « lunatique ».",
     "James Rotton et Ivan Kelly, Psychological Bulletin, 1985"),
    ("lombroso", False, "En amour, les contraires s'attirent.",
     "Les couples se ressemblent plutôt : âge, valeurs, éducation, opinions.",
     "Un ressort de comédie romantique.",
     "Montoya et al., Journal of Social and Personal Relationships, 2008"),
    ("lombroso", False, "Taper dans un coussin fait retomber la colère.",
     "Dans l'expérience, ceux qui tapent dans un sac en pensant à celui qui les a vexés sont ensuite plus agressifs que les autres.",
     "L'idée de la « catharsis », qu'il faudrait vider la colère comme une cocotte-minute.",
     "Brad Bushman, Personality and Social Psychology Bulletin, 2002"),
    ("lombroso", False, "En 1964, 38 voisins ont regardé Kitty Genovese se faire tuer sans rien faire.",
     "Peu de témoins ont compris ce qui se passait, et au moins deux ont appelé ou aidé. L'effet du témoin, lui, a été bien démontré depuis.",
     "Un article du New York Times, très exagéré, qui a fait le tour des manuels.",
     "Rachel Manning, Mark Levine et Alan Collins, American Psychologist, 2007"),
    ("lombroso", False, "La schizophrénie, c'est avoir une double personnalité.",
     "C'est un trouble où la pensée, les émotions et la perception se désaccordent, avec parfois des hallucinations. Rien à voir avec plusieurs personnalités.",
     "Le mot inventé par Eugen Bleuler en 1908, « esprit fendu », pris au pied de la lettre.",
     "Scott Lilienfeld et al., 50 Great Myths of Popular Psychology, 2010"),
    ("lombroso", False, "On peut juger de la fiabilité de quelqu'un sur son visage, en un coup d'œil.",
     "On se fait bien une impression en un dixième de seconde, mais elle ne prédit pas le comportement réel.",
     "La physiognomonie, dont Lombroso a fait une science du crime.",
     "Janine Willis et Alexander Todorov, Psychological Science, 2006 ; Alexander Todorov, Face Value, 2017"),
    ("lombroso", False, "Les femmes parlent trois fois plus que les hommes.",
     "En enregistrant près de 400 étudiants, on trouve environ 16 000 mots par jour pour les uns comme pour les autres.",
     "Un chiffre cité dans un livre à succès, sans source vérifiable.",
     "Matthias Mehl et al., Science, 2007"),
    ("lombroso", True, "Face à un groupe unanime, beaucoup de gens donnent une réponse visiblement fausse.",
     "Dans l'expérience de Solomon Asch, il faut dire quelle ligne est la plus longue : trois participants sur quatre suivent au moins une fois l'erreur du groupe.",
     "Les autres « participants » étaient des complices.",
     "Solomon Asch, Scientific American, 1955"),
    ("lombroso", True, "Répartir des gens au hasard en deux groupes suffit à créer du favoritisme.",
     "Henri Tajfel classe des adolescents selon un critère sans importance : ils avantagent aussitôt leur groupe.",
     "Le paradigme des « groupes minimaux ».",
     "Henri Tajfel, Scientific American, 1970"),
    ("lombroso", True, "Pressés, des étudiants en théologie ont enjambé un homme à terre en allant parler du bon Samaritain.",
     "Seuls 10 % des plus pressés s'arrêtent, contre près des deux tiers de ceux qui ont le temps. Le sujet de leur exposé ne change rien.",
     "Une expérience de 1973 à Princeton, sur le chemin d'un bâtiment à l'autre.",
     "John Darley et Daniel Batson, Journal of Personality and Social Psychology, 1973"),

    # Le Tribun : la langue et les discours
    ("tribun", False, "93 % de la communication passe par le non-verbal.",
     "Mehrabian mesurait des mots isolés chargés d'émotion, quand le ton contredit le mot. Il a lui-même mis en garde contre cette généralisation.",
     "Deux études de 1967, résumées en un chiffre qui fait le tour des formations.",
     "Albert Mehrabian, Silent Messages, 1971"),
    ("tribun", False, "Les Inuits ont des centaines de mots pour la neige.",
     "Leurs langues forment les mots en ajoutant des suffixes, ce qui multiplie les mots pour tout. Les racines pour la neige sont à peu près aussi nombreuses qu'en anglais.",
     "Une remarque de Franz Boas en 1911, gonflée de livre en livre.",
     "Laura Martin, American Anthropologist, 1986 ; Geoffrey Pullum, 1991"),
    ("tribun", False, "Churchill a dit : « Le succès, c'est aller d'échec en échec sans perdre son enthousiasme. »",
     "La phrase n'apparaît nulle part dans ses écrits ou ses discours.",
     "Une citation de motivation attribuée après sa mort.",
     "Richard Langworth, Churchill by Himself, 2008"),
    ("tribun", False, "« OK » vient de « 0 killed », sur les rapports de la guerre de Sécession.",
     "Le mot apparaît à Boston en 1839, abréviation pour rire de « oll korrect », mal écrit exprès.",
     "Une étymologie inventée, plus héroïque.",
     "Allen Walker Read, American Speech, 1963"),
    ("tribun", False, "Voltaire a écrit : « Je ne suis pas d'accord avec vous, mais je me battrai pour que vous puissiez le dire. »",
     "La phrase est d'Evelyn Beatrice Hall, en 1906, pour résumer l'attitude de Voltaire.",
     "Une biographe anglaise, citée sans guillemets puis prise pour Voltaire.",
     "S. G. Tallentyre (Evelyn Beatrice Hall), The Friends of Voltaire, 1906"),
    ("tribun", False, "Gandhi a dit : « Sois le changement que tu veux voir dans le monde. »",
     "On ne la trouve pas dans ses écrits. Il a écrit en 1913 une idée voisine, plus longue et moins bien taillée pour un mug.",
     "Une citation résumée et polie au fil des reprises.",
     "Brian Morton, The New York Times, 2011"),
    ("tribun", False, "« Élémentaire, mon cher Watson » vient des romans de Conan Doyle.",
     "Holmes dit « Elementary » et « my dear Watson », jamais dans la même phrase.",
     "Les adaptations, notamment le film The Return of Sherlock Holmes en 1929.",
     "Arthur Conan Doyle, intégrale des aventures de Sherlock Holmes"),
    ("tribun", True, "Démosthène s'entraînait à parler avec des cailloux dans la bouche.",
     "Pour corriger un défaut d'élocution, il déclamait aussi en courant et face aux vagues.",
     "Plutarque le raconte dans sa Vie de Démosthène.",
     "Plutarque, Vie de Démosthène, 11"),
    ("tribun", True, "Le discours de Gettysburg de Lincoln compte environ 270 mots.",
     "Il dure à peine deux minutes. L'orateur précédent, Edward Everett, avait parlé deux heures.",
     "Les copies manuscrites de Lincoln et les journaux de 1863.",
     "Garry Wills, Lincoln at Gettysburg, 1992"),
    ("tribun", True, "Le « ph » de « nénuphar » vient d'une fausse étymologie.",
     "Le mot vient de l'arabe et du persan, pas du grec. L'Académie française adopte « nénuphar » en 1935 ; on écrivait jusque-là surtout « nénufar ».",
     "La réforme de l'orthographe de 1990 propose de revenir à « nénufar ».",
     "Académie française, Dictionnaire, 8e édition, 1935 ; Rectifications de l'orthographe, 1990"),
]


# --- Dessins : le corps des savants, des sourcils froncés, un rictus, et leurs attributs ---------------

def mechant(t):
    """Sourcils froncés et sourire en coin, par-dessus le visage commun."""
    t.poser({(12, 11), (13, 11), (14, 12), (15, 12), (24, 12), (25, 12), (26, 11), (27, 11)}, "8")
    t.effacer({(17, 18), (22, 18)})
    for p in [(17, 18), (22, 18)]:
        t.px[p] = "S"
    t.poser({(17, 19), (18, 19), (19, 19), (20, 19), (21, 18), (22, 17)}, "m")


def objet_ennemi(t, nom):
    if nom == "des":
        t.peindre(rect(29, 30, 35, 36), "gris", "biseau", 4)
        t.poser({(30, 31), (32, 33), (34, 35)}, "k")
    elif nom == "disque_plat":
        t.peindre(ellipse(32, 34, 6.5, 2.4), "bleu", "plat", 2)
        t.poser({(30, 33), (31, 33), (34, 34), (35, 34), (33, 35)}, "e")
        t.poser(ellipse(32, 35.5, 6.5, 1.2) - ellipse(32, 34, 6.5, 2.4), "U")
    elif nom == "smoothie":
        t.peindre(rect(29, 30, 34, 41), "vert", "cyl_v", 2)
        t.peindre(rect(29, 29, 34, 30), "gris", "plat", 4)
        t.poser(trait(33, 24, 34, 29), "I")
    elif nom == "boule":
        t.peindre(rect(29, 38, 35, 40), "or", "biseau", 1)
        t.peindre(disque(32, 33, 4.6), "violet", "sphere", 2)
        t.poser({(30, 31), (31, 31)}, "w")
    elif nom == "baguette":
        t.poser(trait(28, 42, 36, 27, 1), "G")
        t.peindre(disque(36.5, 26.5, 1.6), "or", "sphere", 2)
    elif nom == "epi":
        t.poser(trait(31, 43, 33, 29), "Y")
        for i, y in enumerate(range(24, 31, 2)):
            t.peindre(ellipse(31.5 + (i % 2) * 2, y + 0.5, 1.2, 1.6), "or", "sphere", 2)
    elif nom == "loupe":
        t.poser(trait(34, 37, 37, 42, 1), "B")
        t.peindre(disque(32, 33, 4), "cyan", "sphere", 1)
        t.poser(disque(32, 33, 4.6) - disque(32, 33, 3.6), "g")
    elif nom == "fiole":
        t.peindre(rect(31, 26, 33, 29), "gris", "plat", 3)
        t.peindre(disque(32, 34, 4.2), "rouge", "sphere", 2)
        t.poser({(30, 32)}, "w")
    # v15 : attributs des huit nouveaux ennemis.
    elif nom == "crane":
        t.peindre(disque(32, 32, 4.4), "gris", "sphere", 5)
        t.peindre(rect(30, 35, 34, 38), "gris", "plat", 4)
        t.poser({(30, 32), (31, 32), (33, 32), (34, 32), (32, 34)}, "k")
        t.poser({(31, 37), (33, 37)}, "g")
        t.poser(trait(29, 30, 35, 30), "g")
    elif nom == "sablier":
        t.peindre(rect(28, 26, 36, 27) | rect(28, 41, 36, 42), "bois", "plat", 1)
        t.peindre(poly([(29, 28), (35, 28), (32, 34)]) | poly([(32, 34), (35, 40), (29, 40)]), "cyan", "plat", 1)
        t.peindre(poly([(30, 29), (34, 29), (32, 32)]) | poly([(31, 37), (33, 37), (35, 40), (29, 40)]), "or", "plat", 2)
    elif nom == "clystere":
        t.peindre(bande((28, 30), (36, 38), 2.4), "gris", "cyl_v", 4)
        t.poser(trait(36, 38, 40, 42), "G")
        t.poser(trait(25, 27, 28, 30) | trait(24, 28, 26, 26), "B")
    elif nom == "roue":
        t.poser(anneau(32, 34, 5.4, 1.1), "B")
        t.poser(trait(27, 34, 37, 34) | trait(32, 29, 32, 39) | trait(28, 30, 36, 38) | trait(36, 30, 28, 38), "b")
        t.peindre(disque(32, 34, 1.3), "or", "plat", 2)
        t.poser({(27, 31), (37, 37), (29, 39)}, "g")
    elif nom == "journal":
        t.peindre(rect(28, 28, 38, 40), "parchemin", "biseau", 2)
        t.poser(trait(29, 30, 37, 30), "k")
        for y, l in ((33, 8), (35, 6), (37, 8), (39, 5)):
            t.poser(trait(29, y, 29 + l, y), "g")
    elif nom == "porte_voix":
        t.peindre(poly([(28, 33), (38, 28), (38, 41), (28, 36)]), "rouge", "biseau", 2)
        t.peindre(ellipse(38, 34.5, 1.3, 6.5), "or", "plat", 2)
        t.poser(trait(30, 36, 30, 41), "B")
    else:
        objet(t, nom)


def tete(spec):
    style, fam, base = spec
    if style == "alu":
        return chapeau_alu()
    if style == "haut_de_forme":
        return haut_de_forme()
    if style == "casquette":
        t = toile()
        frange_sous(t, 10)
        t.peindre(ellipse(20, 7, 10.5, 5) & rect(0, 0, 39, 9), "rouge", "sphere", 2)
        t.peindre(rect(20, 8, 33, 9), "rouge", "plat", 0)
        return t.contour()
    if style == "pointu":
        t = toile()
        frange_sous(t, 10)
        t.peindre(poly([(20, -2), (29, 9), (11, 9)]), "violet", "biseau", 1)
        t.peindre(ellipse(20, 9.5, 12.5, 2), "violet", "plat", 0)
        t.poser({(18, 4), (22, 6), (19, 7), (20, 1)}, "y")
        return t.contour()
    return coiffure(style, fam, base)


def sprite(e):
    _, _, _, _, _, _, peau, style, couleurs, tete_, barbe_, objet_ = e[:12]
    t = toile()
    peindre_corps(t, peau)
    mechant(t)
    t2 = toile()
    tenue(t2, style)
    t.px.update(t2.px)
    if barbe_:
        b = toile()
        barbe(b, *barbe_)
        b.contour()
        t.px.update(b.px)
    o = toile()
    objet_ennemi(o, objet_)
    o.contour()
    t.px.update(o.px)
    return t.lignes(), tete(tete_).lignes()


def fr(x):
    return {"fr": x}


def donnees():
    ennemis = []
    for e in ENNEMIS:
        id, nom, titre, figure, annees, desc, peau, style, couleurs, tete_, barbe_, objet_, defi, victoire, defaite, source = e
        base, cheveux = sprite(e)
        d = {"id": id, "nom": fr(nom), "titre": fr(titre), "figure": figure, "description": fr(desc),
             "couleurs": couleurs, "base": base, "cheveux": cheveux,
             "defi": fr(defi), "victoire": fr(victoire), "defaite": fr(defaite), "source": source}
        if annees:
            d["annees"] = annees
        ennemis.append(d)
    compte = {}
    mythes = []
    for en, vrai, aff, expl, orig, src in MYTHES:
        compte[en] = compte.get(en, 0) + 1
        mythes.append({"id": f"mythe.{en}.{compte[en]:02d}", "ennemi": en, "vrai": vrai, "affirmation": fr(aff),
                       "explication": fr(expl), "origine": fr(orig), "source": src})
    return {"format": 1, "placement": PLACEMENT, "reserve": RESERVE, "questions_par_duel": 5,
            "ennemis": ennemis, "mythes": mythes}


def succes():
    """Un succès pour la première victoire contre chaque ennemi."""
    out = []
    for e in ENNEMIS:
        id, nom = e[0], e[1]
        cible = nom[0].lower() + nom[1:] if e[3] == "archetype" else nom
        out.append({"id": f"vaincu-{id}", "nom": fr(f"Victoire sur {cible}"),
                    "description": fr(f"Gagner un premier duel contre {cible}."),
                    "condition": {"type": "ennemi_vaincu", "id": id}, "cache": False,
                    "recompense": {"type": "anecdote", "texte": fr(e[5]), "source": e[15]}})
    return out


if __name__ == "__main__":
    d = donnees()
    from collections import Counter
    print(len(d["ennemis"]), "ennemis,", len(d["mythes"]), "affirmations", Counter(m["ennemi"] for m in d["mythes"]),
          sum(m["vrai"] for m in d["mythes"]), "vraies")
