"""v9 : le jeu de Mendeleïev, une chasse aux atomes façon Pokémon.

Quelques cases du plateau sont des « cases Mendeleïev ». Passer dessus fait apparaître un atome sauvage,
dont on ne connaît que le nom. Le combat : trois questions (symbole, numéro atomique, où on le croise).
Deux bonnes réponses le capturent ; sinon il s'enfuit, et il reviendra. Les atomes capturés remplissent
le tableau périodique, qui sert de Pokédex.

Masses : poids atomiques standard de l'IUPAC, arrondis. Pour les éléments sans isotope stable,
le nombre de masse de l'isotope le plus stable (entier).
Source de chaque fiche : le tableau périodique de la Royal Society of Chemistry.
"""
from aides import fr


def sans(texte):
    return ("sans", texte)


# Cases du plateau qui font apparaître un atome quand le pion passe dessus, avec la raison affichée.
CASES = {
    7: "Démocrite imaginait des atomes insécables, crochus ou lisses, de toutes les formes. Il en existe cent dix-huit sortes, et aucune n'est insécable. Un atome sauvage sort du vide pour le lui dire.",
    31: "Vésale ouvre le corps humain : soixante pour cent d'eau, un peu de calcium, une pincée de fer. Les atomes s'échappent de la table de dissection.",
    48: "La pile de Volta empile du zinc et du cuivre. Davy s'en sert dès 1807 pour isoler le sodium et le potassium. Un atome s'échappe de l'électrolyse.",
    53: "Mendeleïev laisse des cases vides pour des éléments encore inconnus, et prédit leurs propriétés. Le gallium lui donne raison en 1875. Un atome sort de sa case.",
    55: "Marie et Pierre Curie traitent des tonnes de pechblende pour isoler quelques décigrammes de radium. Ici, un atome sauvage suffit.",
}

FAMILLES = {
    "alcalin": ("Métal alcalin", "#E4573D"),
    "alcalino": ("Métal alcalino-terreux", "#F08A3C"),
    "transition": ("Métal de transition", "#E9B949"),
    "pauvre": ("Métal pauvre", "#8FB65A"),
    "metalloide": ("Métalloïde", "#3FA796"),
    "nonmetal": ("Non-métal", "#3E8ED0"),
    "halogene": ("Halogène", "#5B6CD6"),
    "gaznoble": ("Gaz noble", "#9461C9"),
    "lanthanide": ("Lanthanide", "#D45D9E"),
    "actinide": ("Actinide", "#B0486E"),
    "inconnu": ("Propriétés inconnues", "#7E8691"),
}

RARETES = {
    "commun": ("Commun", 50),
    "peu_commun": ("Peu commun", 30),
    "rare": ("Rare", 15),
    "legendaire": ("Légendaire", 5),
}

# symbole, nom, masse (entier : élément radioactif sans isotope stable), famille, nom anglais (lien RSC),
# où on le croise (trois lieux du quotidien, propres à cet élément), anecdote
ELEMENTS = [
    ("H", "Hydrogène", 1.008, "nonmetal", "hydrogen", ["l'eau du robinet", "le Soleil, qui en brûle 600 millions de tonnes par seconde", "les bus à pile à combustible"],
     "C'est l'élément le plus abondant de l'Univers : environ les trois quarts de la matière visible. Cavendish l'appelait « air inflammable »."),
    ("He", "Hélium", 4.0026, "gaznoble", "helium", ["les ballons de fête", "la voix de canard", "le refroidissement des IRM"],
     "Découvert dans le spectre du Soleil en 1868, avant d'être trouvé sur Terre. D'où son nom, d'après Hélios."),
    ("Li", "Lithium", 6.94, "alcalin", "lithium", ["les batteries de téléphone", "certains régulateurs de l'humeur", "les voitures électriques"],
     "Il est si léger qu'il flotte sur l'huile. Impossible de le conserver sous l'huile comme le sodium : on l'enrobe de vaseline."),
    ("Be", "Béryllium", 9.0122, "alcalino", "beryllium", ["les émeraudes", "les miroirs du télescope James Webb", "les fenêtres des tubes à rayons X"],
     "Les miroirs du télescope James Webb sont en béryllium doré : léger, rigide, et stable au grand froid."),
    ("B", "Bore", 10.81, "metalloide", "boron", ["le verre Pyrex", "les combinaisons de lavage au borax", "les détecteurs de neutrons au bore"],
     "Le verre borosilicaté supporte les chocs thermiques : c'est pour ça qu'on peut passer un plat Pyrex du four au plan de travail."),
    ("C", "Carbone", 12.011, "nonmetal", "carbon", ["la mine de crayon", "les diamants", "tout ce qui est vivant"],
     "Graphite et diamant sont faits du même atome, rangé autrement. L'un s'écrase sur le papier, l'autre raye le verre."),
    ("N", "Azote", 14.007, "nonmetal", "nitrogen", ["l'air qu'on respire, aux quatre cinquièmes", "les engrais", "les sachets de chips gonflés"],
     "Une souris n'y survit pas, avaient noté Priestley et Cavendish ; Lavoisier l'a nommé « azote », « privé de vie ». Il compose pourtant 78 % de l'air."),
    ("O", "Oxygène", 15.999, "nonmetal", "oxygen", ["chaque respiration", "la couche d'ozone", "les bouteilles des plongeurs"],
     "C'est l'élément le plus abondant de la croûte terrestre, en masse : presque la moitié."),
    ("F", "Fluor", 18.998, "halogene", "fluorine", ["le dentifrice", "les poêles antiadhésives", "les gaz de climatiseurs"],
     "Si réactif qu'il a blessé ou tué plusieurs chimistes. Moissan l'isole enfin en 1886 et reçoit le Nobel en 1906."),
    ("Ne", "Néon", 20.180, "gaznoble", "neon", ["les enseignes lumineuses rouges", "les lasers hélium-néon", "les tubes indicateurs"],
     "Seul le néon pur brille en rouge-orangé. Les autres couleurs des « néons » viennent d'autres gaz ou de poudres."),
    ("Na", "Sodium", 22.990, "alcalin", "sodium", ["le sel de table, avec le chlore", "les lampadaires orange", "le bicarbonate de soude"],
     "Jeté dans l'eau, il file, fond et peut exploser. Davy l'a isolé en 1807 avec une pile électrique."),
    ("Mg", "Magnésium", 24.305, "alcalino", "magnesium", ["les flashs photo d'autrefois", "la chlorophylle des feuilles", "les jantes de voiture légères"],
     "Au cœur de chaque molécule de chlorophylle, il y a un atome de magnésium."),
    ("Al", "Aluminium", 26.982, "pauvre", "aluminium", ["les canettes", "le papier d'alu", "les avions"],
     "Au XIXe siècle, il valait plus cher que l'or. Napoléon III réservait ses couverts en aluminium à ses invités de marque."),
    ("Si", "Silicium", 28.085, "metalloide", "silicon", ["les puces des ordinateurs", "le sable", "les panneaux solaires"],
     "Deuxième élément de la croûte terrestre, après l'oxygène. Le sable de plage, c'est surtout de la silice."),
    ("P", "Phosphore", 30.974, "nonmetal", "phosphorus", ["les allumettes", "l'ADN", "les os, avec le calcium"],
     "Brand l'a découvert en 1669 en faisant bouillir des seaux d'urine. Il cherchait la pierre philosophale."),
    ("S", "Soufre", 32.06, "nonmetal", "sulfur", ["l'odeur d'œuf pourri", "les volcans", "la poudre noire"],
     "La Bible fait pleuvoir du soufre ardent sur Sodome et Gomorrhe. L'odeur d'œuf pourri, c'est le sulfure d'hydrogène."),
    ("Cl", "Chlore", 35.45, "halogene", "chlorine", ["l'eau des piscines", "l'eau de Javel", "le sel de cuisine, avec le sodium"],
     "Gaz vert et toxique, il a servi d'arme à Ypres en 1915. Il désinfecte aussi l'eau potable de milliards de personnes."),
    ("Ar", "Argon", 39.95, "gaznoble", "argon", ["les ampoules à incandescence", "la soudure", "le double vitrage isolant"],
     "Son nom vient du grec « paresseux » : il ne réagit avec presque rien. Il fait pourtant près de 1 % de l'air."),
    ("K", "Potassium", 39.098, "alcalin", "potassium", ["les bananes", "les engrais potassiques", "le sel de régime"],
     "Son symbole K vient du latin kalium. Davy l'a isolé en 1807, quelques jours avant le sodium."),
    ("Ca", "Calcium", 40.078, "alcalino", "calcium", ["les os et les dents", "le calcaire dans la bouilloire", "la craie"],
     "Le corps humain en contient environ un kilo, presque tout dans le squelette."),
    ("Sc", "Scandium", 44.956, "transition", "scandium", ["certains cadres de vélo de course", "les lampes de stade", "les battes de baseball en alliage"],
     "Une des cases vides de Mendeleïev, qu'il appelait « éka-bore ». Nilson le découvre en 1879."),
    ("Ti", "Titane", 47.867, "transition", "titanium", ["les prothèses de hanche", "la peinture blanche", "la crème solaire minérale"],
     "L'essentiel du titane extrait finit en blanc de titane, un pigment très couvrant : peinture, papier, crème solaire."),
    ("V", "Vanadium", 50.942, "transition", "vanadium", ["les clés à molette en acier chrome-vanadium", "certaines batteries de réseau", "les ascidies, qui le concentrent"],
     "Henry Ford utilisait de l'acier au vanadium dans la Ford T, plus léger et plus résistant."),
    ("Cr", "Chrome", 51.996, "transition", "chromium", ["l'acier inoxydable", "les pare-chocs chromés", "la couleur verte de l'émeraude"],
     "Son nom vient du grec « couleur » : ses composés sont verts, jaunes, orange. Le rubis lui doit son rouge."),
    ("Mn", "Manganèse", 54.938, "transition", "manganese", ["les piles alcalines", "les rails de chemin de fer", "les peintures préhistoriques noires"],
     "Les artistes de la préhistoire ont peint des grottes avec du noir de manganèse, il y a des dizaines de milliers d'années."),
    ("Fe", "Fer", 55.845, "transition", "iron", ["le sang, dans l'hémoglobine", "la tour Eiffel", "le noyau de la Terre"],
     "Le noyau terrestre est surtout fait de fer. Au-delà du fer, la fusion ne rapporte plus d'énergie : quand le cœur d'une grosse étoile en est plein, elle s'effondre."),
    ("Co", "Cobalt", 58.933, "transition", "cobalt", ["le bleu des faïences", "les batteries lithium-ion", "la vitamine B12"],
     "Les mineurs allemands accusaient le kobold, un lutin, de leur gâcher le minerai. Le cobalt en a gardé le nom."),
    ("Ni", "Nickel", 58.693, "transition", "nickel", ["les pièces de monnaie", "les cordes de guitare électrique", "les allergies aux bijoux"],
     "Encore un lutin : Kupfernickel, « le cuivre du diable », ce minerai qui ressemblait à du cuivre sans en donner."),
    ("Cu", "Cuivre", 63.546, "transition", "copper", ["les fils électriques", "la statue de la Liberté", "les casseroles de chef"],
     "La statue de la Liberté était couleur cuivre à son arrivée. Le vert-de-gris l'a recouverte en une vingtaine d'années."),
    ("Zn", "Zinc", 65.38, "transition", "zinc", ["les toits de Paris", "l'acier galvanisé", "les crèmes pour bébé"],
     "Les toits gris de Paris sont en zinc, posés en masse lors des travaux d'Haussmann."),
    ("Ga", "Gallium", 69.723, "pauvre", "gallium", ["les LED bleues", "la cuillère qui fond dans le thé", "les puces des téléphones"],
     "Il fond à 30 °C, donc dans la main. Mendeleïev avait prédit sa masse et sa densité sous le nom d'éka-aluminium."),
    ("Ge", "Germanium", 72.630, "metalloide", "germanium", ["les premiers transistors", "les fibres optiques", "les lentilles des caméras thermiques"],
     "Encore une prédiction de Mendeleïev, l'éka-silicium. Winkler le trouve en 1886 et le nomme d'après l'Allemagne."),
    ("As", "Arsenic", 74.922, "metalloide", "arsenic", ["les romans d'Agatha Christie", "le vert de Scheele des papiers peints", "certains riz, à l'état de traces"],
     "La « poudre de succession » des empoisonneurs. Le test de Marsh, en 1836, a permis de le détecter dans les cadavres."),
    ("Se", "Sélénium", 78.971, "nonmetal", "selenium", ["les noix du Brésil", "les shampooings antipelliculaires", "les vieilles photocopieuses"],
     "Une ou deux noix du Brésil suffisent à couvrir le besoin quotidien en sélénium. Une poignée, c'est trop."),
    ("Br", "Brome", 79.904, "halogene", "bromine", ["la pourpre des empereurs romains", "les vieux tirages photo argentiques au bromure", "les spas, comme désinfectant"],
     "Un des deux seuls éléments liquides à température ambiante, avec le mercure. Son nom veut dire « puanteur »."),
    ("Kr", "Krypton", 83.798, "gaznoble", "krypton", ["les lampes de flash photo", "les fenêtres isolantes haut de gamme", "Superman, en version kryptonite"],
     "De 1960 à 1983, le mètre était défini par une raie orange du krypton 86."),
    ("Rb", "Rubidium", 85.468, "alcalin", "rubidium", ["les horloges atomiques des satellites GPS", "les feux d'artifice violets", "les laboratoires d'atomes froids"],
     "Il s'enflamme spontanément à l'air. Les horloges au rubidium donnent l'heure à bord des satellites GPS."),
    ("Sr", "Strontium", 87.62, "alcalino", "strontium", ["les feux d'artifice rouges", "les dentifrices pour dents sensibles", "les fusées de détresse"],
     "Nommé d'après Strontian, un village écossais. Le rouge des feux d'artifice, c'est lui."),
    ("Y", "Yttrium", 88.906, "transition", "yttrium", ["les anciens écrans cathodiques rouges", "les lasers YAG", "les supraconducteurs à haute température"],
     "Ytterby, une carrière suédoise, a donné son nom à quatre éléments : yttrium, ytterbium, terbium et erbium."),
    ("Zr", "Zirconium", 91.224, "transition", "zirconium", ["les gaines du combustible nucléaire", "les couronnes dentaires en zircone", "les faux diamants"],
     "La zircone cubique brille plus que le diamant, mais elle raye moins et pèse presque deux fois plus lourd à taille égale."),
    ("Nb", "Niobium", 92.906, "transition", "niobium", ["les aimants des IRM", "les piercings hypoallergéniques", "les gazoducs en acier allié"],
     "Les aimants supraconducteurs du LHC et des IRM sont bobinés en fil de niobium-titane."),
    ("Mo", "Molybdène", 95.95, "transition", "molybdenum", ["les outils en acier rapide", "les lubrifiants au bisulfure", "les nodules des légumineuses"],
     "Les bactéries qui fixent l'azote de l'air ont besoin d'une enzyme au molybdène."),
    ("Tc", "Technétium", 98, "transition", "technetium", ["les scintigraphies des hôpitaux", "les étoiles géantes rouges", "les cases vides de Mendeleïev"],
     "Le premier élément fabriqué par l'humain, en 1937. Son nom vient du grec « artificiel »."),
    ("Ru", "Ruthénium", 101.07, "transition", "ruthenium", ["les cellules solaires à colorant", "les têtes de disques durs", "les contacts électriques"],
     "Nommé d'après la Ruthénie, nom latin de la Russie, par Karl Klaus en 1844."),
    ("Rh", "Rhodium", 102.91, "transition", "rhodium", ["le reflet des bijoux en or blanc", "le disque de rhodium de Paul McCartney", "les miroirs des projecteurs"],
     "En 1979, le Guinness des records offre à Paul McCartney un disque plaqué rhodium, plus rare que le platine."),
    ("Pd", "Palladium", 106.42, "transition", "palladium", ["l'or blanc", "les éponges à hydrogène", "les pots catalytiques des voitures essence"],
     "Il absorbe plus de 900 fois son volume d'hydrogène, comme une éponge."),
    ("Ag", "Argent", 107.87, "transition", "silver", ["les couverts du dimanche", "les pellicules photo", "les miroirs"],
     "Meilleur conducteur de l'électricité de tous les métaux, devant le cuivre. Son symbole vient du latin argentum."),
    ("Cd", "Cadmium", 112.41, "transition", "cadmium", ["le jaune des tableaux de Monet", "les anciennes piles rechargeables", "les cellules solaires au tellurure de cadmium"],
     "Au Japon, la maladie itai-itai, « aïe-aïe », a été causée par du cadmium rejeté par des mines."),
    ("In", "Indium", 114.82, "pauvre", "indium", ["les écrans tactiles", "les joints sous vide", "les soudures sans plomb"],
     "Une fine couche d'oxyde d'indium-étain, transparente et conductrice, permet à l'écran de sentir votre doigt."),
    ("Sn", "Étain", 118.71, "pauvre", "tin", ["les boîtes de conserve", "les soldats de plomb, qui sont souvent en étain", "le bronze, avec le cuivre"],
     "Plié, il « crie » : un craquement dû au frottement des cristaux. Son symbole vient du latin stannum."),
    ("Sb", "Antimoine", 121.76, "metalloide", "antimony", ["le khôl des Égyptiens", "les retardateurs de flamme", "les caractères d'imprimerie"],
     "Ajouté au plomb des caractères d'imprimerie, il limite le retrait du métal au refroidissement : les lettres sortent nettes."),
    ("Te", "Tellure", 127.60, "metalloide", "tellurium", ["les modules thermoélectriques des glacières", "les DVD réinscriptibles", "l'haleine aillée des chimistes"],
     "Un demi-microgramme suffit à donner une haleine d'ail pendant une trentaine d'heures. Son nom vient de Tellus, la Terre."),
    ("I", "Iode", 126.90, "halogene", "iodine", ["le sel iodé", "la teinture d'iode", "les algues"],
     "Courtois le découvre en 1811 en brûlant des algues pour fabriquer de la poudre. Il s'en échappe une vapeur violette."),
    ("Xe", "Xénon", 131.29, "gaznoble", "xenon", ["les phares de voiture au xénon", "les moteurs ioniques des sondes", "l'anesthésie"],
     "Gaz « noble », mais pas si noble : Bartlett lui fait former un composé en 1962, à la surprise générale."),
    ("Cs", "Césium", 132.91, "alcalin", "caesium", ["la définition de la seconde", "les horloges atomiques", "les forages pétroliers"],
     "Depuis 1967, une seconde, c'est 9 192 631 770 oscillations de l'atome de césium 133."),
    ("Ba", "Baryum", 137.33, "alcalino", "barium", ["les radios de l'estomac", "les feux d'artifice verts", "les boues de forage pétrolier"],
     "Avant une radio de l'estomac, on boit une bouillie de sulfate de baryum, opaque aux rayons X."),
    ("La", "Lanthane", 138.91, "lanthanide", "lanthanum", ["les objectifs d'appareil photo", "les batteries des voitures hybrides", "les briquets à pierre"],
     "Son nom veut dire « caché » : il s'était dissimulé dans un oxyde de cérium jusqu'en 1839."),
    ("Ce", "Cérium", 140.12, "lanthanide", "cerium", ["les pierres à briquet", "les fours autonettoyants", "le polissage du verre"],
     "Frotté, le ferrocérium projette une gerbe d'étincelles : c'est la pierre du briquet."),
    ("Pr", "Praséodyme", 140.91, "lanthanide", "praseodymium", ["les lunettes de soudeur", "le verre jaune", "les moteurs d'avion en alliage"],
     "Les lunettes au didyme des souffleurs de verre filtrent la lumière jaune du sodium. Le didyme cachait deux éléments."),
    ("Nd", "Néodyme", 144.24, "lanthanide", "neodymium", ["les écouteurs", "les aimants du frigo trop puissants", "les moteurs de voiture électrique"],
     "Les aimants néodyme-fer-bore sont les plus puissants vendus dans le commerce. Ils pincent les doigts."),
    ("Pm", "Prométhium", 145, "lanthanide", "promethium", ["les anciennes peintures lumineuses", "les piles atomiques des stimulateurs cardiaques d'autrefois"],
     "Le seul lanthanide sans isotope stable. Nommé d'après Prométhée, qui vola le feu aux dieux."),
    ("Sm", "Samarium", 150.36, "lanthanide", "samarium", ["les aimants des guitares électriques", "les traitements du cancer des os", "les casques audio"],
     "Premier élément nommé d'après une personne, indirectement : le minerai samarskite, du colonel russe Samarsky."),
    ("Eu", "Europium", 151.96, "lanthanide", "europium", ["les billets en euros, sous lampe UV", "le rouge des écrans", "les ampoules basse consommation"],
     "Sous lumière ultraviolette, les billets en euros luisent. L'europium fait partie des luminophores."),
    ("Gd", "Gadolinium", 157.25, "lanthanide", "gadolinium", ["les produits de contraste des IRM", "les écrans de radiographie", "les réfrigérateurs magnétiques"],
     "Nommé en l'honneur du chimiste finlandais Johan Gadolin, via le minerai gadolinite."),
    ("Tb", "Terbium", 158.93, "lanthanide", "terbium", ["le vert des écrans", "les haut-parleurs sans membrane", "les billets de banque"],
     "Le Terfenol-D, alliage au terbium, se déforme dans un champ magnétique : il fait vibrer une table comme un haut-parleur."),
    ("Dy", "Dysprosium", 162.50, "lanthanide", "dysprosium", ["les aimants des voitures électriques", "les aimants des éoliennes en mer", "les lampes de cinéma"],
     "Son nom veut dire « difficile à obtenir ». Lecoq de Boisbaudran a fait plus de trente précipitations pour l'isoler."),
    ("Ho", "Holmium", 164.93, "lanthanide", "holmium", ["les lasers de chirurgie urinaire", "les pôles des aimants les plus forts", "les verres colorés jaunes"],
     "Nommé d'après Holmia, Stockholm en latin. Il a le plus fort moment magnétique de tous les éléments."),
    ("Er", "Erbium", 167.26, "lanthanide", "erbium", ["les fibres optiques d'Internet", "les lasers de dermatologie", "le verre rose"],
     "Les amplificateurs à fibre dopée à l'erbium relancent les signaux d'Internet sous les océans."),
    ("Tm", "Thulium", 168.93, "lanthanide", "thulium", ["les appareils de radiographie portables", "les billets en euros", "les lasers chirurgicaux"],
     "Nommé d'après Thulé, l'île mythique du grand Nord. C'est l'une des terres rares les moins abondantes."),
    ("Yb", "Ytterbium", 173.05, "lanthanide", "ytterbium", ["les horloges atomiques optiques", "les lasers industriels", "les jauges de contrainte"],
     "Quatrième élément nommé d'après le village d'Ytterby. Les Suédois sont fiers de leur carrière."),
    ("Lu", "Lutécium", 174.97, "lanthanide", "lutetium", ["les scanners TEP des hôpitaux", "certains traitements du cancer", "le raffinage du pétrole"],
     "Nommé d'après Lutèce, le nom latin de Paris, par Georges Urbain en 1907."),
    ("Hf", "Hafnium", 178.49, "transition", "hafnium", ["les transistors des processeurs récents", "les barres de contrôle des sous-marins", "les torches de soudage plasma"],
     "Nommé d'après Hafnia, Copenhague en latin. Il se cachait dans le zirconium, son quasi-jumeau."),
    ("Ta", "Tantale", 180.95, "transition", "tantalum", ["les condensateurs des téléphones", "les implants crâniens", "les verres optiques spéciaux"],
     "Comme Tantale aux Enfers, il plonge dans l'acide sans jamais en absorber : il résiste à presque tous."),
    ("W", "Tungstène", 183.84, "transition", "tungsten", ["les ampoules à filament", "les forets à béton", "les fléchettes de compétition"],
     "Son symbole W vient de wolfram, « l'écume du loup » : le minerai dévorait l'étain des fondeurs."),
    ("Re", "Rhénium", 186.21, "transition", "rhenium", ["les turbines des réacteurs d'avion", "l'essence sans plomb, au raffinage", "les thermocouples"],
     "Le dernier élément stable découvert, en 1925, par Ida Tacke, Walter Noddack et Otto Berg. Nommé d'après le Rhin."),
    ("Os", "Osmium", 190.23, "transition", "osmium", ["les pointes de stylos plume anciens", "les aiguilles de gramophone", "les contacts électriques durs"],
     "L'élément le plus dense de tous. Son oxyde sent fort, d'où son nom, du grec « odeur »."),
    ("Ir", "Iridium", 192.22, "transition", "iridium", ["les bougies d'allumage haut de gamme", "l'ancien mètre étalon", "la couche de la fin des dinosaures"],
     "En 1980, Alvarez trouve trop d'iridium dans une couche de 66 millions d'années : la trace d'un astéroïde."),
    ("Pt", "Platine", 195.08, "transition", "platinum", ["les pots catalytiques", "les médicaments de chimiothérapie", "les bijoux de mariage"],
     "Les conquistadors le jetaient à la rivière : « platina », « petit argent », gâchait leur or."),
    ("Au", "Or", 196.97, "transition", "gold", ["les alliances", "les connecteurs des cartes électroniques", "les médailles olympiques, en fine couche"],
     "Tout l'or extrait dans l'histoire tiendrait dans un cube d'une vingtaine de mètres de côté."),
    ("Hg", "Mercure", 200.59, "transition", "mercury", ["les anciens thermomètres", "les plombages amalgames", "les lampes fluorescentes"],
     "Les chapeliers l'utilisaient pour traiter le feutre. L'anglais « mad as a hatter », fou comme un chapelier, viendrait de là."),
    ("Tl", "Thallium", 204.38, "pauvre", "thallium", ["les poisons des romans policiers", "la mort-aux-rats d'autrefois", "certains verres optiques"],
     "Le « poison des empoisonneurs » : sans goût, sans odeur. Agatha Christie l'utilise dans Le Cheval pâle."),
    ("Pb", "Plomb", 207.2, "pauvre", "lead", ["les batteries de voiture", "les tabliers de radiologie", "les anciennes canalisations"],
     "Son symbole vient de plumbum. Les plombiers lui doivent leur nom : les Romains faisaient leurs tuyaux en plomb."),
    ("Bi", "Bismuth", 208.98, "pauvre", "bismuth", ["les médicaments contre les maux d'estomac", "les cristaux en escalier irisés", "les fards à paupières nacrés"],
     "Longtemps considéré comme stable, il est en fait radioactif, avec une demi-vie plus d'un milliard de fois plus longue que l'âge de l'Univers."),
    ("Po", "Polonium", 209, "metalloide", "polonium", ["les brosses antistatiques", "la fumée de tabac, à l'état de traces", "l'affaire Litvinenko"],
     "Le premier élément découvert par Marie et Pierre Curie, en 1898. Elle l'a nommé d'après sa Pologne natale."),
    ("At", "Astate", 210, "halogene", "astatine", ["la recherche contre certains cancers", "l'écorce terrestre, quelques milligrammes en tout"],
     "Le premier kilomètre de l'écorce terrestre en contiendrait moins de 50 milligrammes à un instant donné."),
    ("Rn", "Radon", 222, "gaznoble", "radon", ["les caves en terrain granitique", "les maisons de Bretagne mal ventilées", "les sources thermales radioactives"],
     "Deuxième cause de cancer du poumon après le tabac. Il suffit souvent d'aérer."),
    ("Fr", "Francium", 223, "alcalin", "francium", ["le laboratoire de Marguerite Perey", "les pièges magnéto-optiques"],
     "Découvert en 1939 par Marguerite Perey, assistante de Marie Curie, et nommé d'après la France."),
    ("Ra", "Radium", 226, "alcalino", "radium", ["les aiguilles lumineuses des vieilles montres", "les crèmes de beauté des années 1930", "les malles de Marie Curie"],
     "Les « Radium Girls » peignaient les cadrans en affinant le pinceau avec les lèvres. Beaucoup en sont mortes."),
    ("Ac", "Actinium", 227, "actinide", "actinium", ["les thérapies alpha ciblées", "la lueur bleue des sources fortes"],
     "Si radioactif qu'il luit en bleu dans le noir. Il a donné son nom à toute la famille des actinides."),
    ("Th", "Thorium", 232.04, "actinide", "thorium", ["les manchons des lampes de camping", "les électrodes de soudure", "certains projets de réacteurs"],
     "Nommé d'après Thor. Les manchons des lampes à gaz en contenaient, ce qui les rendait légèrement radioactifs."),
    ("Pa", "Protactinium", 231.04, "actinide", "protactinium", ["l'étude des courants océaniques de la dernière glaciation", "les résidus de pechblende"],
     "Repéré en 1913 par Fajans et Göhring, Lise Meitner en isole en 1918 l'isotope le plus durable. Son nom veut dire « avant l'actinium », dont il est le parent."),
    ("U", "Uranium", 238.03, "actinide", "uranium", ["les centrales nucléaires", "le verre vaseline qui luit en vert", "le lest des quilles de bateau"],
     "En 1896, Becquerel découvre la radioactivité grâce à des sels d'uranium oubliés sur une plaque photographique."),
    ("Np", "Neptunium", 237, "actinide", "neptunium", ["les détecteurs de neutrons rapides", "les déchets de centrale"],
     "Après l'uranium, nommé d'après Uranus, venait la planète suivante : Neptune."),
    ("Pu", "Plutonium", 244, "actinide", "plutonium", ["les sondes Voyager, pour l'électricité", "les rovers martiens", "les bombes de 1945"],
     "Les sondes Voyager tirent encore leur électricité de la chaleur du plutonium, à plus de vingt milliards de kilomètres."),
    ("Am", "Américium", 243, "actinide", "americium", ["les détecteurs de fumée", "les jauges d'épaisseur", "les laboratoires de Berkeley"],
     "Il y en a un fragment dans la plupart des détecteurs de fumée ioniques. Moins d'un microgramme."),
    ("Cm", "Curium", 247, "actinide", "curium", ["les spectromètres des rovers martiens", "les piles atomiques des sondes", "la mémoire des Curie"],
     "Nommé en hommage à Marie et Pierre Curie. Les rovers martiens l'emportent pour analyser les roches."),
    ("Bk", "Berkélium", 247, "actinide", "berkelium", ["la ville de Berkeley", "la fabrication de la tennessine"],
     "Il a fallu des mois de réacteur pour en produire 22 milligrammes, envoyés en Russie pour créer la tennessine."),
    ("Cf", "Californium", 251, "actinide", "californium", ["le démarrage des réacteurs nucléaires", "les détecteurs d'or et de pétrole", "la Californie, évidemment"],
     "L'un des éléments les plus chers au monde : des dizaines de millions de dollars le gramme."),
    ("Es", "Einsteinium", 252, "actinide", "einsteinium", ["les retombées de la première bombe H", "le réacteur à haut flux d'Oak Ridge"],
     "Découvert dans les débris de la première bombe à hydrogène, en 1952. Nommé d'après Einstein, qui n'y était pour rien."),
    ("Fm", "Fermium", 257, "actinide", "fermium", ["les coraux de l'atoll d'Enewetak après Ivy Mike", "la mémoire d'Enrico Fermi"],
     "Lui aussi sorti des débris d'Ivy Mike. Nommé d'après Enrico Fermi, qui a construit la première pile atomique."),
    ("Md", "Mendélévium", 258, "actinide", "mendelevium", ["le cyclotron de 1955, un atome à la fois", "ce jeu"],
     "Nommé d'après Mendeleïev. Les premiers ont été produits un atome à la fois, dix-sept en tout, en 1955."),
    ("No", "Nobélium", 259, "actinide", "nobelium", ["l'Institut Nobel de Stockholm", "les querelles de priorité"],
     "Sa découverte a été disputée pendant des décennies entre Suédois, Américains et Soviétiques."),
    ("Lr", "Lawrencium", 266, "actinide", "lawrencium", ["la mémoire d'Ernest Lawrence", "la fin disputée de la ligne des actinides"],
     "Nommé d'après Ernest Lawrence, l'inventeur du cyclotron, la machine qui a fabriqué tant d'éléments."),
    ("Rf", "Rutherfordium", 267, "transition", "rutherfordium", ["la guerre des transfermiens", "la mémoire d'Ernest Rutherford"],
     "Le premier transactinide. Doubna et Berkeley se sont disputé sa découverte, et son nom, pendant près de trente ans."),
    ("Db", "Dubnium", 268, "transition", "dubnium", ["la ville de Dubna, sur la Volga", "les cibles de californium bombardées à l'azote"],
     "Nommé d'après Dubna, la ville russe dont le laboratoire a disputé à Berkeley la découverte de plusieurs éléments lourds."),
    ("Sg", "Seaborgium", 269, "transition", "seaborgium", ["la mémoire de Glenn Seaborg", "le courrier de Glenn Seaborg"],
     "Seaborg a reçu un élément de son vivant. Il recevait son courrier, disait-il, « à l'adresse seaborgium »."),
    ("Bh", "Bohrium", 270, "transition", "bohrium", ["la mémoire de Niels Bohr", "les cibles de bismuth bombardées au chrome"],
     "Nommé d'après Niels Bohr. Quelques atomes à la fois, qui ne vivent que quelques secondes."),
    ("Hs", "Hassium", 269, "transition", "hassium", ["le Land de Hesse", "les cibles de plomb bombardées au fer"],
     "Nommé d'après la Hesse, la région allemande du laboratoire qui l'a créé."),
    ("Mt", "Meitnérium", 278, "inconnu", "meitnerium", ["la mémoire de Lise Meitner", "les cibles de bismuth bombardées au fer"],
     "Hommage à Lise Meitner, qui a expliqué la fission nucléaire. Le Nobel était allé à Otto Hahn seul."),
    ("Ds", "Darmstadtium", 281, "inconnu", "darmstadtium", ["la ville de Darmstadt", "les cibles de plomb bombardées au nickel"],
     "Nommé d'après Darmstadt. Il vit quelques secondes, ce qui est long pour sa catégorie."),
    ("Rg", "Roentgenium", 282, "inconnu", "roentgenium", ["la mémoire de Wilhelm Röntgen", "les cibles de bismuth bombardées au nickel"],
     "Nommé d'après Röntgen, qui a découvert les rayons X en 1895, un siècle avant sa création."),
    ("Cn", "Copernicium", 285, "inconnu", "copernicium", ["la mémoire de Copernic", "les cibles de plomb bombardées au zinc"],
     "Nommé le 19 février 2010, jour anniversaire de Copernic. Peut-être liquide, voire gazeux."),
    ("Nh", "Nihonium", 286, "pauvre", "nihonium", ["le RIKEN, au Japon", "les cibles de bismuth bombardées au zinc"],
     "Le premier élément découvert en Asie. Nihon veut dire Japon. Il a fallu neuf ans pour en voir trois atomes."),
    ("Fl", "Flérovium", 289, "pauvre", "flerovium", ["le laboratoire Flerov", "les cibles de plutonium bombardées au calcium"],
     "Nommé d'après Gueorgui Flerov, fondateur de l'institut de Doubna. Il pourrait être aussi inerte qu'un gaz noble, malgré sa famille."),
    ("Mc", "Moscovium", 290, "pauvre", "moscovium", ["l'oblast de Moscou", "les cibles d'américium bombardées au calcium"],
     "Quelques dixièmes de seconde d'existence, au mieux. Assez pour être nommé en 2016."),
    ("Lv", "Livermorium", 293, "pauvre", "livermorium", ["le laboratoire Lawrence Livermore", "les cibles de curium bombardées au calcium"],
     "Une collaboration russo-américaine, nommée d'après le laboratoire Lawrence Livermore."),
    ("Ts", "Tennessine", 294, "halogene", "tennessine", ["l'État du Tennessee", "les cibles de berkélium bombardées au calcium"],
     "Fabriqué en bombardant du berkélium américain avec du calcium à Dubna. Un des éléments les plus internationaux."),
    ("Og", "Oganesson", 294, "gaznoble", "oganesson", ["la dernière case du tableau, pour l'instant", "les cibles de californium bombardées au calcium"],
     "Le plus lourd élément connu, nommé d'après Iouri Oganessian, encore vivant lors du baptême en 2016. Une poignée d'atomes observés en tout."),
]

REPLIQUES = {
    "atome_apparait": [
        "Un atome sauvage. Mendeleïev a rangé soixante-trois éléments en 1869, avec des trous pour ceux qui manquaient. Vous avez des trous aussi. Remplissez-les.",
        sans("Un atome sauvage apparaît. Il a l'air instable. Vous aussi, mais je ne dis rien."),
        sans("Attention, un atome. Il ne mord pas. Sauf s'il est radioactif."),
        sans("Tiens, un atome. Il vous regarde. Faites semblant de savoir ce que vous faites."),
        sans("Un atome traîne sur votre route. Il n'a rien demandé. Vous non plus. Allez-y."),
        sans("Un atome sauvage surgit. Il a des électrons. Vous avez des lacunes. Le duel est équilibré."),
        sans("Ne bougez pas. Il est farouche. Lui au moins a une raison de vous fuir."),
        sans("Un atome. Trois questions. Essayez de ne pas les rater dans l'ordre."),
        sans("Quelque chose bouge dans les herbes. C'est un atome. Ou une miette. Non, c'est un atome."),
        sans("Un atome vous barre la route. Il est minuscule. Ce n'est pas une excuse pour perdre."),
        sans("Un atome sauvage. Je parie sur lui, par principe."),
        sans("Voilà un atome. Il ne connaît pas votre nom. Il vaut mieux pour vous."),
        sans("Un atome apparaît. Il est neutre. Je ne peux pas en dire autant."),
        sans("Un atome rôde. Approchez doucement, et sans réviser à voix haute : ça l'effraie."),
        sans("Encore un atome. Ils sortent quand ils sentent un ignorant. Ne le prenez pas mal."),
        sans("Atome en vue. Sortez votre tableau périodique mental. Celui avec les cases vides."),
        sans("Un atome sauvage. Il a l'air sûr de lui. C'est vexant, de la part d'une chose aussi petite."),
        sans("Un atome se dresse devant vous. Façon de parler : il mesure à peu près un dixième de milliardième de mètre."),
    ],
    "atome_capture": [
        "Capturé. Il vous a fallu trois questions. Il a fallu à Marie Curie quatre ans et des tonnes de pechblende pour le radium. Vous êtes efficace, ou chanceux.",
        sans("Dans la boîte. Il ne bougera plus. Enfin, ses électrons, si, mais pas lui."),
        sans("Capturé. Je l'ajoute au tableau, à côté de votre ego."),
    ],
    "atome_fuite": [
        "Il s'est enfui. Le gallium avait échappé à tout le monde jusqu'en 1875, alors que Mendeleïev l'avait décrit. Vous êtes en bonne compagnie, mais en mauvaise posture.",
        sans("Il s'est échappé. Il reviendra. Les atomes sont patients : ils ont treize milliards d'années d'avance."),
        sans("Fuite. Même un gaz noble a plus de répartie que vous, et il ne réagit avec rien."),
    ],
}

TONS = {"atome_apparait": "neutre", "atome_capture": "impressionnee", "atome_fuite": "moqueuse"}

TEXTES = {"mendeleiev": "Case Mendeleïev : passe dessus et un atome sauvage apparaît. Trois questions, deux bonnes réponses, et il rejoint ton tableau périodique."}


def place(z):
    """(période, groupe) d'un élément ; lanthanides et actinides : groupe 0 et colonne propre (rangées 9 et 10)."""
    if z <= 2:
        return 1, 1 if z == 1 else 18
    bornes = [(10, 2, 3), (18, 3, 11), (36, 4, 19), (54, 5, 37), (86, 6, 55), (118, 7, 87)]
    for fin, per, debut in bornes:
        if z <= fin:
            i = z - debut
            if per <= 3:
                return per, i + 1 if i < 2 else i + 11
            if per <= 5:
                return per, i + 1
            if i < 2:
                return per, i + 1
            if i < 17:
                return per, 0
            return per, i - 14 + 1
    raise ValueError(z)


def rarete(z, famille):
    if z >= 104:
        return "legendaire"
    if famille in ("lanthanide", "actinide") or z in (43, 61) or z >= 84:
        return "rare"
    if z <= 30 or z in (47, 50, 53, 78, 79, 80, 82):
        return "commun"
    return "peu_commun"


def donnees():
    elements = []
    for i, (sym, nom, masse, fam, en, ou, anec) in enumerate(ELEMENTS):
        z = i + 1
        per, gr = place(z)
        elements.append({"z": z, "symbole": sym, "nom": fr(nom), "masse": masse, "stable": not isinstance(masse, int),
                         "famille": fam, "periode": per, "groupe": gr, "rarete": rarete(z, fam),
                         "ou": [fr(x) for x in ou], "anecdote": fr(anec),
                         "source": f"Royal Society of Chemistry, Periodic Table : https://periodic-table.rsc.org/element/{z}/{en}"})
    return {"format": 1, "regles": {"questions": 3, "seuil": 2, "attente_max": 3},
            "familles": {k: {"nom": fr(n), "couleur": c} for k, (n, c) in FAMILLES.items()},
            "raretes": {k: {"nom": fr(n), "poids": p} for k, (n, p) in RARETES.items()},
            "elements": elements}


def succes():
    def s(id, nom, desc, cond, texte, source):
        return {"id": id, "nom": fr(nom), "description": fr(desc), "condition": cond, "cache": False,
                "recompense": {"type": "anecdote", "texte": fr(texte), "source": source}}
    return [
        s("atome-1", "Premier atome", "Capturer un premier atome.", {"type": "atomes_captures", "n": 1},
          "Démocrite imaginait des atomes crochus, qui s'accrochent les uns aux autres. Il n'avait aucun moyen de les voir.", "Aristote, Métaphysique, livre A"),
        s("atome-10", "Le cabinet de Lavoisier", "Capturer 10 atomes.", {"type": "atomes_captures", "n": 10},
          "En 1789, Lavoisier publie une liste de 33 « substances simples ». Il y range la lumière et le calorique.", "Antoine Lavoisier, Traité élémentaire de chimie, 1789"),
        s("atome-30", "Les triades de Döbereiner", "Capturer 30 atomes.", {"type": "atomes_captures", "n": 30},
          "En 1829, Döbereiner remarque que le brome a une masse à mi-chemin entre le chlore et l'iode. Premier indice d'un ordre caché.", "Eric Scerri, The Periodic Table, Oxford University Press, 2007"),
        s("atome-63", "Le tableau de 1869", "Capturer 63 atomes, autant que Mendeleïev en connaissait.", {"type": "atomes_captures", "n": 63},
          "Mendeleïev aurait vu le tableau en rêve. Lui passait surtout des heures à classer des fiches d'éléments. Le tableau, lui, est bien réel.", "Michael Gordin, A Well-Ordered Thing, 2004"),
        s("atome-92", "Jusqu'à l'uranium", "Capturer 92 atomes.", {"type": "atomes_captures", "n": 92},
          "Jusqu'en 1940, l'uranium fermait le tableau. Tout ce qui vient après a été découvert en le fabriquant.", "Glenn Seaborg, The Transuranium Elements, 1958"),
        s("atome-118", "Tableau complet", "Capturer les 118 atomes.", {"type": "atomes_captures", "n": 118},
          "Depuis 2016, la septième période est complète. Personne ne sait encore s'il existe un élément 119.", "IUPAC, 2016"),
        s("gaz-nobles", "Club très fermé", "Capturer les 7 gaz nobles.", {"type": "famille_capturee", "famille": "gaznoble"},
          "Entre 1894 et 1898, Ramsay découvre ou isole cinq gaz nobles et ajoute une colonne entière au tableau. Nobel 1904.", "William Ramsay, conférence Nobel, 1904"),
        s("halogenes", "Faiseurs de sel", "Capturer les 6 halogènes.", {"type": "famille_capturee", "famille": "halogene"},
          "« Halogène » veut dire « qui fait du sel », en grec. Le sel de table est du chlorure de sodium.", "Royal Society of Chemistry, Periodic Table"),
        s("alcalins", "Ne pas mettre dans l'eau", "Capturer les 6 métaux alcalins.", {"type": "famille_capturee", "famille": "alcalin"},
          "Plus on descend la colonne, plus la réaction avec l'eau est violente. Le césium explose au contact.", "Royal Society of Chemistry, Periodic Table"),
        s("atome-fuite", "Électron libre", "Laisser s'enfuir 5 atomes.", {"type": "atomes_enfuis", "n": 5},
          "Pendant des décennies, le technétium a été « découvert » plusieurs fois, à tort. Le masurium de 1925 n'a jamais été confirmé.", "Eric Scerri, A Tale of Seven Elements, 2013"),
    ]


if __name__ == "__main__":
    d = donnees()
    assert len(d["elements"]) == 118
    from collections import Counter
    print(Counter(e["rarete"] for e in d["elements"]), Counter(e["famille"] for e in d["elements"]))
    for e in d["elements"]:
        if e["z"] in (1, 2, 5, 13, 21, 31, 55, 57, 71, 72, 87, 89, 104, 118):
            print(e["z"], e["symbole"], e["periode"], e["groupe"])
