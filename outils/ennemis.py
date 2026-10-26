"""v7 : les ennemis du plateau, figures de la bêtise humaine, et leurs duels de vrai ou faux.

Sept ennemis sont posés sur le plateau au début de chaque tour, un huitième attend en réserve
(il arrive quand un cadeau fait à l'IA tourne mal). Passer sur un ennemi arrête le pion et lance
un duel : cinq affirmations, il faut les juger toutes correctement. Les fausses sont des idées
reçues ou des fausses nouvelles célèbres, chacune avec son origine et une source.

Archétypes inventés, et deux figures historiques mortes depuis longtemps (Lyssenko, Mesmer).
Aucune personne vivante.
"""
from avatar40 import L, chapeau_alu, haut_de_forme, toile, frange_sous
from dessin import disque, ellipse, poly, rect, trait
from savants import barbe, c, coiffure, peindre_corps, tenue

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
