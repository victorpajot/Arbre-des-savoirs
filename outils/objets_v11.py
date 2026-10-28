"""v11 : ce que disent les sources sur chaque objet, et le bonus d'un objet tenu par l'avatar.

Citation : (verbatim, texte, attribution). verbatim = True pour une citation réelle (traduite si besoin),
False pour un résumé de la source, affiché « D'après ».
Bonus : quand l'avatar tient l'objet, une épreuve réussie a une chance de le déclencher.
« case » : n cases de plus ; « butin » : un butin assuré ; « faveur » : n points de faveur de l'IA.
"""

CHANCE_BONUS = 0.25

CITATIONS = {
    "boulier": (False, "Le soroban de Kiyoshi Matsuzaki l'emporte sur la calculatrice électrique du soldat Thomas Wood pour les additions, les soustractions et les problèmes composés. La machine ne gagne que la multiplication.", "Stars and Stripes, novembre 1946"),
    "compas-euclide": (True, "D'un centre quelconque et avec un intervalle quelconque, décrire un cercle.", "Euclide, Éléments, livre I, demande 3"),
    "des-pascal": (True, "Je vois bien que la vérité est la même à Toulouse et à Paris.", "Pascal, lettre à Fermat, 29 juillet 1654"),
    "ardoise-boole": (False, "Boole cherche les lois fondamentales des opérations de l'esprit et les écrit dans la langue symbolique d'un calcul. Ses 0 et 1 désignent le rien et l'univers.", "George Boole, An Investigation of the Laws of Thought, 1854"),
    "metre-etalon": (True, "Pour tous les hommes, pour tous les temps.", "Condorcet, à propos du système métrique"),
    "pomme-newton": (True, "L'idée de la gravitation lui vint à l'esprit. Elle fut occasionnée par la chute d'une pomme, alors qu'il était assis, d'humeur contemplative.", "William Stukeley, Memoirs of Sir Isaac Newton's Life, 1752"),
    "machine-joule": (False, "Joule fait tomber des poids qui agitent l'eau d'un calorimètre. Une chute d'environ 772 pieds pour une livre d'eau la réchauffe d'un degré Fahrenheit.", "James Prescott Joule, Philosophical Transactions, 1850"),
    "diapason": (False, "John Shore, trompettiste de la chapelle royale, aurait fabriqué le premier diapason vers 1711 et l'aurait surnommé sa « pitch-fork ».", "Grove Dictionary of Music and Musicians, « Tuning-fork »"),
    "carnet-darwin": (True, "I think.", "Charles Darwin, Notebook B, p. 36, 1837"),
    "microscope-hooke": (True, "Le livre le plus ingénieux que j'aie jamais lu de ma vie.", "Samuel Pepys, Journal, 21 janvier 1665"),
    "pois-mendel": (False, "Mendel croise des pois qui diffèrent par sept caractères et compte leurs descendants : à la deuxième génération, les caractères dominants et récessifs reviennent dans un rapport proche de 3 pour 1.", "Gregor Mendel, « Versuche über Pflanzen-Hybriden », 1866"),
    "boite-petri": (True, "On trouve parfois ce qu'on ne cherchait pas.", "Alexander Fleming, propos attribué, à propos de la pénicilline"),
    "rouleau-aristote": (True, "La rhétorique est la faculté de considérer, pour chaque question, ce qui peut être propre à persuader.", "Aristote, Rhétorique, livre I, 2"),
    "cailloux-demosthene": (False, "Démosthène corrigeait son bégaiement en déclamant des cailloux dans la bouche, et exerçait sa voix en parlant en courant ou en gravissant des pentes.", "Plutarque, Vie de Démosthène, 11"),
    "cartes-wason": (False, "Avec des lettres et des nombres, presque personne ne retourne les bonnes cartes. Avec des boissons et des âges dans un bar, la plupart des gens réussissent.", "Griggs et Cox, British Journal of Psychology, 1982"),
    "roue-loterie": (False, "Des participants qui ont vu la roue s'arrêter sur 10 estiment en moyenne à 25 % la part des pays africains à l'ONU ; ceux qui ont vu 65, à 45 %.", "Tversky et Kahneman, Science, 1974"),
    "fiche-ebbinghaus": (False, "Ebbinghaus apprend lui-même des listes de syllabes sans sens et mesure le temps gagné à les réapprendre : une grande partie s'efface dès la première heure.", "Hermann Ebbinghaus, Über das Gedächtnis, 1885"),
    "cloche-pavlov": (False, "Pavlov n'a pas utilisé de cloche : le « zvonok » de ses protocoles est une sonnerie électrique, mal traduite par les béhavioristes.", "Daniel Todes, Ivan Pavlov: A Russian Life in Science, 2014"),
    "lignes-asch": (False, "Face à une majorité unanime qui se trompe, les participants suivent le groupe dans un peu plus d'un tiers des essais. Un seul allié suffit à faire chuter ce taux.", "Solomon Asch, Psychological Monographs, 1956"),
    "tableau-mendeleiev": (False, "Mendeleïev décrit à l'avance l'éka-aluminium, l'éka-bore et l'éka-silicium : leur masse, leur densité, leurs composés. Le gallium, le scandium et le germanium lui donnent raison.", "Dmitri Mendeleïev, 1871"),
    "modele-moleculaire": (False, "Hofmann montre ses molécules à la Royal Institution avec des boules de croquet peintes : le carbone noir, l'hydrogène blanc, le chlore vert, l'oxygène rouge. Les couleurs sont restées.", "August Wilhelm von Hofmann, conférence à la Royal Institution, 1865"),
    "papier-tournesol": (False, "Le tournesol est tiré de lichens comme la roccelle, et non de la fleur. Il rougit dans un acide et bleuit dans une base.", "Encyclopædia Britannica, « Litmus »"),
    "balance-lavoisier": (True, "Rien ne se crée, ni dans les opérations de l'art, ni dans celles de la nature.", "Antoine Lavoisier, Traité élémentaire de chimie, 1789"),
    "alambic": (False, "Les manuscrits alchimiques de Newton, longtemps cachés, comptent environ un million de mots. Keynes, qui en racheta une partie en 1936, l'appela « le dernier des magiciens ».", "The Newton Project, université d'Oxford"),
    "lunette-galilee": (False, "Galilée raconte avoir vu la Lune « rugueuse et inégale », couverte de montagnes et de vallées, et quatre « planètes » tourner autour de Jupiter.", "Galilée, Sidereus Nuncius, 1610"),
    "prisme-newton": (True, "Ce fut d'abord un divertissement très agréable, de voir les couleurs vives et intenses ainsi produites.", "Isaac Newton, Philosophical Transactions, 1672"),
    "pendule-foucault": (False, "Foucault invite les savants à « voir tourner la Terre » dans la salle méridienne de l'Observatoire, le 3 février 1851.", "Léon Foucault, invitation du 2 février 1851 ; APS News, février 2007"),
    "plaque-hubble": (True, "VAR!", "Edwin Hubble, plaque H335H, 6 octobre 1923"),
    "sphere-armillaire": (False, "Ptolémée décrit un instrument fait d'anneaux emboîtés pour mesurer les positions des astres. Tycho Brahe en construira de géantes à Uraniborg.", "Ptolémée, Almageste, livre V"),
    "pile-volta": (False, "Volta décrit à Banks un « organe électrique artificiel » fait de disques de métal empilés, qui donne un courant continu sans avoir besoin d'être rechargé.", "Alessandro Volta, lettre à Joseph Banks, 1800"),
    "bouteille-leyde": (True, "Je ne voudrais pas recevoir un second coup pareil pour le royaume de France.", "Pieter van Musschenbroek, lettre à Réaumur, 1746"),
    "ampoule-edison": (False, "Selon le New York Herald, Edison annonce qu'avec la lumière électrique, seuls les dépensiers brûleront encore des chandelles de suif.", "New York Herald, 4 janvier 1880 ; Quote Investigator"),
    "bobine-faraday": (False, "Faraday note qu'au moment où il ferme le circuit de la première bobine, l'aiguille du galvanomètre reliée à la seconde dévie, puis revient à zéro.", "Michael Faraday, Experimental Researches in Electricity, 1832"),
    "cerf-volant-franklin": (False, "Priestley rapporte que Franklin attendit l'orage, vit les fibres de la ficelle se hérisser, et tira une étincelle de la clé en approchant sa main.", "Joseph Priestley, The History and Present State of Electricity, 1767"),
    "coupe-cigue": (True, "Criton, nous devons un coq à Asclépios ; payez cette dette, ne soyez pas négligents.", "Platon, Phédon, 118a"),
    "rasoir-ockham": (True, "Entia non sunt multiplicanda praeter necessitatem.", "John Punch, 1639"),
    "poele-descartes": (True, "Je demeurais tout le jour enfermé seul dans un poêle, où j'avais tout le loisir de m'entretenir de mes pensées.", "René Descartes, Discours de la méthode, IIe partie, 1637"),
    "marteau-nietzsche": (True, "Comment on philosophe avec un marteau.", "Friedrich Nietzsche, Crépuscule des idoles, 1888"),
    "lanterne-diogene": (True, "Je cherche un homme.", "Diogène Laërce, Vies et doctrines des philosophes illustres, livre VI"),
    "flamme-promethee": (False, "Prométhée dérobe l'éclat du feu infatigable dans le creux d'une férule et le rapporte aux mortels. Zeus le fait enchaîner, et un aigle lui dévore le foie.", "Hésiode, Théogonie, v. 565-570"),
    "pierre-philosophale": (False, "Brand garde son « feu froid » secret et le vend. Le phosphore luit dans le noir, mais il ne change rien en or.", "John Emsley, The 13th Element, 2000"),
    "mecanisme-anticythere": (False, "La tomographie révèle des inscriptions et des engrenages qui prédisent les éclipses et suivent les jeux panhelléniques, dont les Jeux olympiques.", "Tony Freeth et al., Nature, 2008"),
    "principia": (False, "La Royal Society ordonne l'impression des Principia le 2 juin 1686, mais à condition que Halley en paie les frais. Elle venait d'engloutir son budget dans l'Histoire des poissons de Willughby.", "Royal Society, procès-verbaux de 1686"),
    "ruban-turing": (True, "On peut comparer un homme en train de calculer un nombre réel à une machine qui n'est capable que d'un nombre fini d'états.", "Alan Turing, « On Computable Numbers », 1936"),
    "disque-voyager": (True, "Ceci est un présent d'un petit monde lointain : un échantillon de nos sons, de notre science, de nos images, de notre musique, de nos pensées et de nos sentiments.", "Jimmy Carter, message gravé sur le disque, 1977"),
    "demon-laplace": (True, "Rien ne serait incertain pour elle, et l'avenir, comme le passé, serait présent à ses yeux.", "Pierre-Simon de Laplace, Essai philosophique sur les probabilités, 1814"),
    "couronne-hieron": (True, "Eurêka ! Eurêka !", "Vitruve, De architectura, livre IX"),
    "miroir-ardent": (False, "Le premier à parler d'un feu lancé par Archimède, Lucien, écrit près de quatre siècles après le siège de Syracuse. Les miroirs n'apparaissent que vers 500, chez Anthémius de Tralles.", "D. L. Simms, Technology and Culture, 1977"),
    "nez-tycho": (False, "L'analyse des restes de Tycho montre des traces de cuivre et de zinc autour de la cavité nasale : la prothèse de tous les jours était sans doute en laiton, plus léger que l'or.", "Kaare Lund Rasmussen et al., Archaeometry, 2012"),
    "lampe-pise": (False, "Viviani raconte que Galilée, à 19 ans, observa une lampe se balancer dans la cathédrale de Pise et compta ses oscillations sur son pouls. Elles duraient le même temps, larges ou petites.", "Vincenzo Viviani, Racconto istorico della vita di Galileo, 1654"),
    "diamant-lavoisier": (False, "Exposé au foyer de la grande lentille, le diamant diminue puis disparaît. Dans un vase clos, il laisse un air qui trouble l'eau de chaux : de l'« air fixe ».", "Antoine Lavoisier, Mémoires de l'Académie royale des sciences, 1772"),
    "feuille-or-rutherford": (True, "C'était presque aussi incroyable que si vous tiriez un obus de 15 pouces sur une feuille de papier de soie et qu'il revenait vous frapper.", "Ernest Rutherford, 1936"),
    "verre-uranium": (False, "Le verre à l'uranium, jaune-vert, est fabriqué en Bohême par Franz Xaver Riedel dès les années 1830. Ses ouvriers l'appelaient « Annagelb » et « Annagrün », d'après sa fille Anna.", "The Corning Museum of Glass, « Uranium glass »"),
    "bobine-tesla": (False, "Des éclairs artificiels de plus de trente mètres jaillissent du mât de sa station de Colorado Springs.", "Nikola Tesla, Colorado Springs Notes, 1899-1900"),
    "medailles-hevesy": (False, "Hevesy raconte avoir dissous les médailles de von Laue et de Franck dans de l'eau régale le jour où les troupes allemandes entraient dans Copenhague. Le flacon est resté sur une étagère jusqu'en 1945.", "George de Hevesy, Adventures in Radioisotope Research, 1962"),
}

# Bonus de l'objet tenu : (type, n). Les objets éblouissants flattent l'IA, les instruments font avancer,
# les livres et les carnets font tomber un butin.
BONUS = {
    "lunette-galilee": ("case", 2), "metre-etalon": ("case", 1), "boulier": ("case", 1), "pomme-newton": ("case", 1),
    "machine-joule": ("case", 1), "pendule-foucault": ("case", 1), "pile-volta": ("case", 2), "bobine-faraday": ("case", 1),
    "bouteille-leyde": ("case", 2), "ruban-turing": ("case", 2), "mecanisme-anticythere": ("case", 2), "plaque-hubble": ("case", 2),
    "carnet-darwin": ("butin", 0), "principia": ("butin", 0), "rouleau-aristote": ("butin", 0), "fiche-ebbinghaus": ("butin", 0),
    "tableau-mendeleiev": ("butin", 0), "pois-mendel": ("butin", 0), "microscope-hooke": ("butin", 0), "lanterne-diogene": ("butin", 0),
    "des-pascal": ("butin", 0), "cartes-wason": ("butin", 0), "ardoise-boole": ("butin", 0), "demon-laplace": ("butin", 0),
}


def bonus(id, eclat):
    if id in BONUS:
        return BONUS[id]
    return ("faveur", 10) if eclat >= 2 else ("case", 1)
