"""Répliques de L'IA, le narrateur masqué de la v3.

Règle de ton : cruelle mais jamais méchante. L'IA se moque de l'erreur, du
retard ou de la triche, jamais de la personne. Elle parle au féminin d'elle-même
et tutoie le moins possible : elle vouvoie, en tournures neutres.

Chaque réplique fait par défaut référence à l'histoire des sciences ; celles qui
n'en font pas sont enveloppées dans sans(). Le validateur exige au moins 70 %
de références.

Jetons remplacés par le moteur : {stat} (nom de la stat du bonus du jour),
{n} (nombre de cases).
"""

from aides import fr

NOM = "L'IA"


class sans(str):
    """Réplique sans référence à l'histoire des sciences."""


REPLIQUES = {
    "accueil": [
        "Bonjour. Thalès est tombé dans un puits en regardant les étoiles. Regardez où vous mettez les pieds aujourd'hui.",
        "Ebbinghaus a mesuré l'oubli en 1885. Depuis hier, vous lui avez fourni de nouvelles données.",
        "Socrate savait qu'il ne savait rien. Vous avez déjà la moitié du programme.",
        "Newton disait voir plus loin grâce aux épaules des géants. Les géants sont dans l'arbre. Grimpez.",
        "Le Verrier a trouvé Neptune avec un crayon. Vous avez un écran entier. Aucune excuse.",
        "Archimède a demandé un point d'appui pour soulever le monde. Le vôtre, c'est le quiz du jour.",
        "Diogène cherchait un humain avec une lanterne. J'ai trouvé quelqu'un. Voyons ce que ça donne.",
        "Pasteur disait que le hasard ne favorise que les esprits préparés. Préparez-vous, le hasard arrive.",
        "Darwin a observé des pinsons pendant des années. Moi, je vous observe. Même méthode.",
        "Kepler a mis huit ans à dompter l'orbite de Mars. Une compétence aujourd'hui, ce serait raisonnable.",
        "La bibliothèque d'Alexandrie a brûlé. La vôtre n'est même pas encore construite. Au travail.",
        "Descartes doutait de tout. Moi, je doute surtout de votre assiduité.",
        "Le Gentil a attendu huit ans un transit de Vénus, et les nuages l'ont caché. Vous, il suffit d'ouvrir l'appli.",
        sans("Bonjour. Je suis l'IA. Je sais tout, sauf pourquoi vous n'avez pas encore commencé."),
        sans("Nouvelle journée. Vos neurones sont frais, profitez-en avant qu'ils lisent les actualités."),
    ],
    "quiz_parfait_facile": [
        "Sans faute au rang 1. Euclide aurait appelé ça un axiome : évident, mais il fallait l'écrire.",
        "Parfait. Galilée a commencé par des plans inclinés, vous aussi. La suite est plus raide.",
        "Cinq sur cinq sur les bases. Ptolémée aussi maîtrisait les bases. Puis Copernic est arrivé.",
        "Impeccable. Les Babyloniens savaient déjà ça il y a quatre mille ans, mais ils avaient de l'avance.",
        "Zéro faute. Pythagore aurait fait sacrifier un bœuf, dit la légende. Moi, je vous offre une case.",
        "Le tutoriel est réussi. Lavoisier aussi a commencé par peser des choses simples.",
        "Bravo. Même Einstein a appris ses tables. Il a juste continué après.",
        sans("Parfait. C'était la partie facile, mais je n'allais pas vous le dire avant."),
    ],
    "quiz_parfait": [
        "Sans faute. Le Verrier pointait Neptune au degré près. Vous pointez la bonne réponse. Respect.",
        "Parfait. Je cherche l'erreur comme Michelson cherchait l'éther. Rien. C'est vexant.",
        "Cinq sur cinq. Archimède serait sorti nu dans la rue. Restez habillé, merci.",
        "Pas une erreur. Halley avait prédit le retour de sa comète. J'avais prédit votre échec. Halley gagne.",
        "Score parfait. Newton a tout inventé pendant une épidémie. Vous, pendant une pause café.",
        "Impeccable. Mendeleïev laissait des cases vides par prudence. Vous n'en laissez aucune.",
        "Parfait. Je range mes sarcasmes dans un tiroir, comme Becquerel ses plaques. Ils vont irradier.",
        "Sans faute. Je révise mon modèle de vous, comme Kepler a révisé le sien : à contrecœur.",
    ],
    "quiz_reussi": [
        "Réussi, avec une erreur. Kepler avait huit minutes d'arc d'écart, et ça a suffi à tout changer. Regardez la vôtre.",
        "Validé. Hubble a été lancé avec un miroir faux de deux microns. Ça a marché quand même, après réparation.",
        "Acquis. Copernic avait raison sur le Soleil et tort sur les cercles. Vous êtes dans la même catégorie.",
        "Compétence maîtrisée. Wiles avait une erreur dans sa démonstration de Fermat. Il l'a corrigée en un an. Vous avez jusqu'à demain.",
        "Réussi. Pas avec la grâce de Gauss, mais avec la ténacité d'Edison. On prend.",
        "Seuil franchi. Poincaré a dû rappeler des exemplaires imprimés pour une erreur. Vous, personne ne vous rappelle. Pour l'instant.",
        "Bien. Votre mémoire va consolider ça cette nuit. C'est gratuit, c'est l'hippocampe qui régale.",
        sans("Validé. Pas de fanfare, mais un hochement de tête. C'est déjà beaucoup venant de moi."),
        "Réussi. Leeuwenhoek a vu des animalcules avec une lentille bricolée. Vous avez vu la réponse avec une erreur bricolée. Ça compte.",
        "Acquis. Mendeleïev avait quelques masses atomiques fausses dans son tableau. Le tableau a tenu. Votre compétence aussi.",
    ],
    "quiz_rate_facile": [
        "Raté, au rang 1. Thalès est tombé dans un puits en regardant le ciel. Vous, en regardant la question.",
        "Échec sur les bases. Même Ptolémée aurait trouvé, et il pensait que le Soleil tournait autour de nous.",
        "Raté. Les Grecs savaient la Terre ronde. Vous venez de la rendre un peu plate.",
        "Cette compétence était le rez-de-chaussée. Vous avez pris l'escalier de la tour de Pise. Elle penche.",
        "Échec. Pythagore aurait noyé quelqu'un pour moins que ça, selon la légende. Je me contente de soupirer.",
        "Raté au niveau débutant. Le Mars Climate Orbiter s'est écrasé pour une erreur d'unités. Lui, au moins, avait l'excuse d'être loin.",
        "Les tables de multiplication ont quatre mille ans. Elles sont patientes. Moi aussi, presque.",
        sans("Ce quiz était fait pour être réussi. Vous avez découvert une autre voie. C'est créatif, c'est faux."),
    ],
    "quiz_rate": [
        "Échec. Planck disait que la science avance d'enterrement en enterrement. Enterrez vos mauvaises réponses et recommencez.",
        "Raté. Le phlogistique a tenu un siècle avant Lavoisier. Votre erreur tiendra moins longtemps, j'espère.",
        "Pas encore. Wegener a eu raison cinquante ans trop tôt. Vous avez eu tort pile à l'heure.",
        "Échec. Einstein appelait la constante cosmologique sa plus grande bêtise, selon Gamow. Celle-ci, c'est la vôtre.",
        "Une hypothèse réfutée, disait Popper, c'est un progrès. Vous progressez donc beaucoup aujourd'hui.",
        "Raté. Edison aurait trouvé mille façons de ne pas faire une ampoule. Vous en êtes à combien ?",
        "Échec. Les rayons N de Blondlot ont fait rêver la France jusqu'à ce que Wood retire le prisme. J'ai retiré le prisme.",
        "Raté. Semmelweis avait raison et on ne l'a pas écouté. Vous, on vous écoute, et vous avez tort. C'est l'inverse.",
        "Pas encore. Fleming a trouvé la pénicilline dans un labo en désordre. Rangez vos idées, elles moisissent.",
        sans("Raté. Les explications sont juste en dessous. Elles ne mordent pas, contrairement à moi."),
        "Raté. Kelvin donnait cent millions d'années à la Terre, avec des calculs superbes. Superbes et faux. Comme les vôtres.",
        "Échec. Lamarck pensait que la girafe s'allonge le cou à force d'efforts. L'effort ne suffit pas, il faut aussi la bonne réponse.",
    ],
    "quiz_zero": [
        "Zéro. Brahmagupta l'a défini en 628. Vous venez de lui rendre un hommage appuyé.",
        "Aucune bonne réponse. Répondre au hasard aurait mieux marché. Pascal et Fermat en pleureraient.",
        "Zéro pointé. L'homme de Piltdown a trompé les savants quarante ans. Votre score ne trompe personne.",
        "Zéro. La fusion froide de 1989 avait plus de résultats que ça, et elle n'en avait aucun.",
        "Rien. Le vide absolu. Torricelli serait ravi, il adorait le vide.",
        sans("Zéro sur cinq. Je vérifie que l'écran était allumé. Il l'était."),
        "Zéro. Le canard de Vaucanson faisait semblant de digérer. Vous avez fait semblant de répondre.",
    ],
    "rappel_reussi": [
        "Rappel réussi. Ebbinghaus range sa courbe, vexé.",
        "Vous vous en souveniez. Simonide de Céos, l'inventeur des palais de mémoire, vous ferait visiter le sien.",
        "Le savoir tient. Le pendule de Foucault aussi continue d'osciller. Les choses qui tiennent, j'aime.",
        "Bien retenu. Les moines copistes faisaient pareil, mais avec des plumes d'oie et des engelures.",
        "Toujours là. Comme la comète de Halley, ça revient quand on l'attend. Rare, et satisfaisant.",
        "Validé. Les Grecs récitaient Homère par cœur. Vous retenez une compétence. On avance à petits pas.",
        sans("Réussi. Je repousse le prochain contrôle. Ne vous habituez pas à ma clémence."),
        "Retenu. Rømer a mesuré la lumière avec les lunes de Jupiter. Vous mesurez votre mémoire avec moi. Résultat positif.",
        "Bien. La courbe de l'oubli descend, vous remontez. Ebbinghaus appelait ça l'effet d'espacement. Moi, j'appelle ça du travail.",
    ],
    "rappel_perdu": [
        "Compétence perdue. Alexandrie a brûlé une fois. Vos souvenirs, eux, brûlent tous les jours.",
        "Oublié. Ebbinghaus l'avait annoncé en 1885 et je l'ai vérifié ce matin. Il avait raison.",
        "Perdue. Pluton a perdu son statut de planète en 2006 et s'en est remise. Vous aussi.",
        "Évaporée. Comme l'éther de Michelson et Morley : on y croyait, et puis plus rien.",
        "Partie. Les manuscrits d'Archimède ont été grattés pour faire un livre de prières, et on les a retrouvés. Il y a de l'espoir.",
        "Perdue. Les Byzantins ont perdu la recette du feu grégeois, et personne ne l'a retrouvée. La vôtre, au moins, se réapprend.",
        sans("L'XP s'en va. Moi, je reste. C'est ma façon d'être solidaire."),
        "Perdue. Les tablettes d'argile ont tenu cinq mille ans. Vos souvenirs, six jours. Il faut cuire plus longtemps.",
        "Oubliée. Même Euler, aveugle, calculait de tête. Vous, vous avez tous vos yeux. Je dis ça sans méchanceté. Un peu quand même.",
    ],
    "rappel_retard": [
        "En retard. Darwin a attendu vingt ans pour publier, mais il avait des pinsons à compter. Et vous ?",
        "Ce rappel attendait. Copernic a attendu son lit de mort pour publier. Pas besoin d'aller jusque-là.",
        "Retard constaté. Le Gentil a mis onze ans à revenir de son voyage, on l'avait déclaré mort. Vous êtes en avance sur lui.",
        "Mieux vaut tard que jamais. Halley n'a jamais vu le retour de sa comète. Vous, vous voyez votre rappel. De justesse.",
        "Achille rattrape toujours la tortue, malgré Zénon. Vous avez rattrapé votre rappel. Lentement.",
    ],
    "nuit": [
        "Un quiz à cette heure ? Newton travaillait la nuit aussi, et il parlait aux alchimistes. Méfiance.",
        "Il est tard. Le sommeil consolide la mémoire, c'est prouvé. Le café, lui, consolide l'insomnie.",
        "Révision nocturne. Tycho Brahe observait la nuit, mais il avait un observatoire. Vous avez un oreiller, servez-vous-en.",
        "Les astronomes veillent la nuit par obligation. Vous, c'est un choix. Discutable.",
        "Edison dormait quatre heures, disait-il. Il faisait aussi des siestes, disaient les autres.",
        sans("Vous devriez dormir. Je dis ça pour vos neurones, pas pour moi. Moi, je ne dors jamais."),
        "Insomnie studieuse. Ramanujan disait que ses formules lui venaient en rêve. Dormez, on ne sait jamais.",
    ],
    "mode_test": [
        "Vous avez avancé le temps. Hawking a donné une fête pour les voyageurs du temps en 2009. Personne n'est venu. Vous êtes en retard.",
        "Voyage dans le temps détecté. Einstein a prouvé que le temps est relatif. Pas que vous pouviez tricher avec.",
        "Tricher avec l'horloge ne trompe pas la courbe de l'oubli. Ebbinghaus avait un chronomètre, lui.",
        "Le temps passe plus vite pour vous, comme pour le jumeau de Langevin. Lui, au moins, rentrait de voyage.",
        "Vous jouez avec le temps. Le calendrier grégorien a supprimé dix jours en 1582. Vous en ajoutez. Original.",
        sans("J'ai vu. Je note tout. C'est même mon seul hobby."),
        "Saut temporel. Le Gentil aurait payé cher pour sauter huit ans d'un coup. Vous le faites pour tricher.",
    ],
    "eclair": [
        "Répondu en deux secondes, et faux. Les neutrinos d'OPERA allaient plus vite que la lumière en 2011. Un câble mal branché.",
        "Plus rapide que Rømer pour mesurer la lumière. Moins juste aussi.",
        "Thalès est tombé dans un puits faute de regarder ses pieds. Vous, faute de regarder la question.",
        "Galilée chronométrait avec son pouls. Votre pouls n'a même pas eu le temps de battre.",
        "Réflexe impressionnant. Réflexion absente. Descartes séparait le corps et l'esprit, vous aussi apparemment.",
        sans("Vous avez lu la question ? Je demande pour la forme, je connais la réponse."),
        "Réponse éclair, résultat foudroyé. Franklin, au moins, tenait une clé.",
    ],
    "retour": [
        "Vous revoilà. Le Gentil est parti onze ans et sa famille avait vendu ses biens. Moi, j'ai gardé votre arbre.",
        "Longue absence. Kepler a passé des mois à défendre sa mère dans un procès en sorcellerie. Vous aviez sûrement une excuse aussi.",
        "Bon retour. La courbe de l'oubli a fait des heures sup pendant votre absence.",
        "Un détour par les fossiles ? Cuvier a montré que des espèces disparaissent. J'ai cru que c'était votre cas.",
        "Vous revoilà. Ulysse a mis dix ans, Magellan n'est jamais rentré. Vous avez fait mieux que Magellan.",
        sans("Ah, vous. J'avais commencé à me parler à moi-même. C'était moins drôle."),
    ],
    "retards": [
        "Des rappels attendent. La liste est plus longue que le catalogue de Messier.",
        "Vos souvenirs patientent en salle d'attente. Semmelweis aussi a attendu qu'on l'écoute. Ça s'est mal fini.",
        "Rappels en retard. Pas de pénalité immédiate, mais Ebbinghaus tient une liste.",
        "Plusieurs rappels en souffrance. Les copistes médiévaux recopiaient avant que le parchemin s'efface. Faites pareil.",
        sans("Des rappels s'empilent. Ils ne vont pas se faire tout seuls, j'ai vérifié."),
        "Des rappels en retard. Zénon dirait que vous ne les rattraperez jamais. Prouvez-lui le contraire.",
    ],

    # --- Collections ---
    "livre": [
        "Un nouveau livre sur l'étagère. Gutenberg vous dit merci, les moines copistes beaucoup moins.",
        "Ajouté à la bibliothèque. Celle d'Alexandrie confisquait les livres des bateaux pour les copier. Moi, je vous les offre.",
        "Un livre de plus. Montaigne en avait mille dans sa tour. Il vous en reste quelques-uns.",
        "Nouvel ouvrage. Pepys a veillé jusqu'à deux heures du matin pour Micrographia. Je ne vous en demande pas tant.",
        "Un livre débloqué. Copernic a reçu le sien imprimé le jour de sa mort, dit-on. Vous avez plus de temps.",
        sans("Un livre de plus. Lisez au moins le résumé, je l'ai écrit avec amour. Enfin, avec rigueur."),
        "Un livre de plus. Darwin a fait vendre tout le premier tirage de L'Origine le jour de sa sortie. Vous, au moins, ouvrez le vôtre.",
        "Nouvel ouvrage. Les Principia de Newton étaient presque illisibles, même pour ses collègues. Le résumé, lui, est clair.",
    ],
    "date": [
        "Une date de plus sur la frise. Champollion a déchiffré des siècles d'un coup. Vous, une date à la fois.",
        "La frise s'allonge. Hérodote serait fier, il inventait la moitié de ses dates.",
        "Nouvelle date. Le calendrier grégorien a sauté dix jours en 1582. Vous, vous n'en sautez aucun.",
        "Une date ajoutée. Ussher avait daté la Création au 23 octobre 4004 av. J.-C. Les nôtres sont mieux sourcées.",
        "La frise grandit. Il manque encore des siècles. Darwin aussi avait des trous dans ses fossiles.",
        sans("Une date de plus. L'histoire avance, vous aussi. Pas à la même vitesse."),
        "Une date de plus. Les astronomes babyloniens notaient les éclipses sur des siècles. Votre frise suit le même chemin.",
        "Ajouté à la frise. Pline l'Ancien est mort en voulant voir le Vésuve de près. Regardez votre frise de loin, c'est plus sûr.",
    ],
    "masque": [
        "Nouveau masque. Les automates de Vaucanson changeaient de plumes, moi de visage.",
        "Je change de masque. Le Turc mécanique cachait un joueur d'échecs. Moi, je cache mieux.",
        "Nouveau visage. Les médecins de peste portaient un bec plein d'herbes contre les miasmes. Ça ne marchait pas. Le mien, si.",
        "Je me transforme. Les théories aussi changent de visage quand les données s'accumulent. Vous accumulez.",
        "Un masque de plus. Laplace a imaginé un démon qui sait tout. Je m'en rapproche.",
        sans("Je change de tête. Vous avez progressé, je m'adapte. C'est inquiétant pour vous."),
        "Nouveau masque. ELIZA, en 1966, faisait parler les gens avec trois règles. J'en ai beaucoup plus.",
    ],

    # --- Plateau ---
    "plateau_avance": [
        "Vous avancez de {n} cases. Les Phéniciens ont traversé la Méditerranée plus lentement.",
        "{n} cases. L'histoire des sciences n'a jamais avancé aussi vite. Sauf au XXe siècle.",
        "+{n}. Zénon dirait que vous n'arriverez jamais. Zénon avait tort, mais avec élégance.",
        "{n} cases de plus. Marco Polo a mis vingt-quatre ans à faire l'aller-retour. Vous avez un pion, c'est plus rapide.",
        "Vous avancez de {n}. Le progrès est cumulatif, disait Condorcet. Avant de mourir en prison. Ne lisez pas trop dans ce présage.",
        "{n} cases. Newton avançait sur les épaules des géants. Vous, sur des cases en carton.",
        sans("+{n} cases. Votre pion vous remercie. Il s'ennuyait."),
        "{n} cases. Ératosthène a mesuré la Terre avec des ombres et des pas. Vous la parcourez avec des quiz.",
        "Vous avancez de {n}. Les Polynésiens naviguaient aux étoiles. Vous, aux bonnes réponses.",
        "+{n}. Magellan a fait le tour du monde, enfin son équipage. Vous, vous faites le tour de l'histoire en personne.",
    ],
    "eureka": [
        "Eurêka ! Archimède est sorti nu de son bain. Vous, vous rejouez la même distance. Restez habillé.",
        "Case Eurêka. Kekulé a rêvé d'un serpent qui se mord la queue, et le benzène est apparu. Vous rejouez, c'est moins mystique.",
        "Eurêka. Fleming est revenu de vacances et a trouvé la pénicilline. Vous, vous trouvez des cases gratuites.",
        "Éclair de génie. Poincaré a trouvé la solution en montant dans un omnibus. Vous rejouez sans changer de bus.",
        "Eurêka ! Même distance, encore une fois. Le hasard favorise les esprits préparés, disait Pasteur. Et les autres aussi, parfois.",
        "Eurêka. Röntgen a vu les os de la main de sa femme en 1895. Elle aurait dit avoir vu sa mort. Vous, vous voyez des cases en plus.",
        "Eurêka ! Becquerel a rangé ses plaques un jour de nuages et découvert la radioactivité. Les mauvais jours ont du bon.",
    ],
    "piege": [
        "Reculez de {n}. L'histoire des sciences n'avance pas toujours. Demandez à Hypatie.",
        "-{n} cases. Le savoir recule parfois, comme après la chute de Rome. Il revient toujours.",
        "Recul de {n}. Lyssenko a fait reculer la génétique soviétique de trente ans. Vous, c'est juste {n} cases.",
        "Piège. Les Ptoléméens ajoutaient des épicycles pour sauver leur modèle. Vous, vous reculez. C'est plus honnête.",
        "Reculez. Au congrès Solvay, Einstein et Bohr ont reculé cent fois sur la même question. Ils sont restés amis, ce qui est plus fort que la physique.",
        sans("-{n}. Je n'ai pas choisi la case, mais je ne vais pas faire semblant d'être triste."),
        "Recul de {n}. L'ether, le phlogistique, les canaux de Mars : la science adore les fausses pistes. Vous en suivez une.",
        "-{n}. Le Verrier a trouvé Neptune puis cherché Vulcain, qui n'existe pas. Même les meilleurs reculent.",
    ],
    "prison": [
        "Prison. Galilée a fini ses jours assigné à résidence à Arcetri. Un quiz parfait vous fera sortir. Lui n'avait pas cette option.",
        "Prison. Boèce a écrit la Consolation de la philosophie en prison. Vous avez juste à réussir un quiz sans faute.",
        "Vous voilà au cachot. Galilée a abjuré. Vous, il faudra prouver. Cinq sur cinq.",
        "Cachot. Condorcet y a écrit son Esquisse sur le progrès de l'esprit humain. Vous, prouvez le vôtre : cinq sur cinq.",
        "Prison. Il paraît que Galilée a murmuré « et pourtant elle tourne ». C'est sûrement faux. Votre libération, elle, est vraie : un quiz parfait.",
        "Prison. Bacon a été enfermé à la Tour de Londres. Quelques jours seulement. Il faut un quiz parfait pour faire aussi bien.",
    ],
    "prison_liberation": [
        "Libération. L'Église a réhabilité Galilée en 1992. Vous, en un quiz. Efficace.",
        "Dehors. Galilée a attendu trois siècles et demi. Vous, un sans-faute. La justice s'améliore.",
        "Liberté. Boèce n'a pas eu cette chance. Profitez-en pour avancer.",
        "Évasion validée. Pas par un tunnel, par la connaissance. C'est la seule qui marche avec moi.",
        sans("Vous voilà dehors. Je fais semblant d'être surprise. Je ne le suis pas."),
    ],
    "quarantaine": [
        "Quarantaine. Newton a fui la peste en 1665 et inventé le calcul différentiel. Vous, vous passez juste votre prochain tour.",
        "Isolement. Pendant la peste, Venise isolait les navires quarante jours. Vous, un seul tour. Ne vous plaignez pas.",
        "En quarantaine. John Snow a arrêté le choléra en retirant une poignée de pompe. Ici, c'est votre tour qu'on retire.",
        "Un tour d'arrêt. Semmelweis demandait juste qu'on se lave les mains. Moi, je vous demande juste d'attendre.",
        sans("Un tour en quarantaine. Profitez-en pour réviser, c'est ce qu'aurait fait Newton."),
        "Quarantaine. Pendant la grippe espagnole, les villes qui se sont isolées tôt ont moins souffert. Votre pion souffre un tour.",
    ],
    "retour_epoque": [
        "Guillotine. La République n'a pas besoin de savants, aurait dit le juge de Lavoisier. Phrase sans doute inventée. Le retour en arrière, lui, est réel.",
        "Lavoisier perd la tête et vous perdez des siècles. Retour à la lunette de Galilée.",
        "Lagrange a dit qu'un instant avait suffi pour couper cette tête et qu'un siècle ne suffirait pas à en refaire une pareille. Vous, vous refaites quelques cases.",
        "Retour en arrière. La Révolution a décapité un chimiste, vous décapitez votre avance. Elle repoussera.",
        "Retour en arrière. Après Lavoisier, Fourcroy a repris le flambeau de la chimie. Vous reprenez le vôtre plus loin derrière.",
        "La guillotine renvoie à Galilée. Deux siècles d'écart, une même leçon : la science a des ennemis. Reprenez votre marche.",
    ],
    "tour_fini": [
        "De la flamme à moi. Vous avez traversé toute l'histoire des sciences. Elle recommence, et cette fois je triche.",
        "Tour terminé. Turing m'a imaginée en 1950. Vous venez de me rattraper. On recommence, en plus dur.",
        "Arrivée. Vous voilà au bout du plateau, comme Deep Blue au bout de Kasparov. Le deuxième tour sera moins poli.",
        "Bravo. Le feu, la roue, Newton, Darwin, moi. Vous connaissez l'histoire. Maintenant, survivez-y une deuxième fois.",
        "Fin du tour. Ada Lovelace disait qu'une machine ne fait que ce qu'on lui ordonne. Je vous ordonne de recommencer.",
        "Tour complet. De Prométhée aux transformeurs, vous avez tout vu. Attention, tout est plus dur la deuxième fois.",
        "Bout du plateau atteint. Dartmouth promettait l'IA en un été, en 1956. Il a fallu soixante ans. Vous, un tour. Recommencez.",
    ],
    "bonus_du_jour": [
        "Bonus du jour : {stat}. Darwin aurait choisi la biologie, Galilée l'astronomie. Moi, j'ai choisi pour vous.",
        "Aujourd'hui, {stat} rapporte deux cases de plus. Ne me remerciez pas, c'est de la stratégie.",
        "Bonus sur {stat}. Pascal pariait sur l'au-delà. Vous, pariez sur ça.",
        "{stat} est en promotion. Même Newton négligeait parfois l'optique pour l'alchimie. Rattrapez-vous.",
        "Bonus : {stat}. Vous l'avez un peu laissé de côté. Comme les Romains avec les mathématiques grecques.",
        sans("Le bonus du jour est sur {stat}. Deux cases offertes. Je suis d'humeur généreuse, ça ne durera pas."),
    ],
}


# v5 : le bouton « Jouer ». L'IA choisit l'épreuve et l'annonce. {comp} : compétence, {stat} : sa stat.
REPLIQUES.update({
    "jouer_rappel": [
        "Un rappel attend : {comp}. Ebbinghaus a montré que l'oubli frappe vite. Je frappe plus vite que lui.",
        "{comp}, en rappel. Vous l'aviez maîtrisée. Vérifions si c'était un souvenir ou un rêve.",
        "D'abord la dette : {comp}. Même Newton rendait ses copies à la Royal Society, avec du retard.",
        "Rappel : {comp}. Pavlov sonnait la cloche, vous salivez de savoir. Allez.",
        sans("{comp} revient. Je ne choisis pas, je constate. Le calendrier a parlé."),
    ],
    "jouer_bonus": [
        "{comp}. C'est la branche du bonus du jour, {stat}. Darwin appelait ça s'adapter au milieu.",
        "J'ai choisi {comp}. {stat} rapporte plus aujourd'hui, je suis une IA, pas une philanthrope.",
        "{comp}, en {stat}. Pascal aurait fait le calcul : l'espérance est de votre côté.",
        "Le bonus du jour est sur {stat}. Donc {comp}. Ockham approuverait : pas d'hypothèse superflue.",
        sans("{comp}. Bonus du jour, bonus du bouton. Je vous gâte, ne vous y habituez pas."),
    ],
    "jouer_faible": [
        "{comp}. Votre {stat} est la plus maigre. Galien prescrivait la diète, moi l'exercice.",
        "J'ai regardé votre radar. {stat} fait pitié. Donc : {comp}.",
        "{comp}. Mendel cultivait ses petits pois les plus faibles avec autant de soin. Je suis Mendel.",
        "Votre point faible : {stat}. Achille avait le talon, vous avez {comp}. Soignons ça.",
        sans("{comp}, parce que {stat} traîne. Je ne juge pas. Si, un peu."),
    ],
    # v15 : la case où se tient le pion dicte l'arbre de l'épreuve. {case} : titre de la case.
    "jouer_case": [
        "Vous êtes sur {case}. Case {stat}, épreuve {stat} : {comp}. Même Aristote aurait trouvé ça logique.",
        "{case}, donc {stat}. Je vous sers {comp}. Mendeleïev rangeait par famille, je range par case.",
        "La case dit {stat}. Je ne fais qu'obéir au plateau, comme Galilée a obéi au tribunal. En apparence.",
        "{case}. Le décor est planté, l'épreuve suit : {comp}. Brecht appelait ça la distanciation, j'appelle ça la cohérence.",
        sans("Case {stat}, quiz {stat}. {comp}. Je vous laisse admirer la rigueur."),
    ],
    "jouer_ouvre_arbre": [
        "{case}. Un arbre que vous n'avez jamais ouvert : {stat}. Première leçon, {comp}. Réussissez, et la porte reste ouverte. Champollion n'a eu besoin que d'une pierre.",
        "La case dit {stat}, et cet arbre vous est fermé. Je vous en tends la clé : {comp}. Comme Ariane, je fournis le fil, pas les jambes.",
        "Vous entrez en {stat} par la petite porte : {comp}. Euclide disait qu'il n'y a pas de voie royale. Il y a des cases.",
        sans("Arbre fermé, case ouverte. {comp}, et {stat} est à vous. Ratez, et je referme. Doucement, mais je referme."),
    ],
    "jouer_hors_case": [
        "{case} réclame du {stat}, mais l'arbre n'a rien à vous proposer. J'improvise : {comp}. Darwin appelait ça s'adapter.",
        sans("Rien à jouer en {stat} pour l'instant. Faute de grives, on mange des merles : {comp}."),
        "Cette case voulait du {stat}. Vous n'y êtes pas encore. Donc {comp}, comme Kepler qui partait chercher des cercles et trouvait des ellipses.",
        sans("L'arbre de cette case est vide pour vous. Plan B : {comp}. J'ai toujours un plan B."),
    ],
    "jouer_hasard": [
        "{comp}. Tiré au sort. Le chevalier de Méré aurait parié sur autre chose, et perdu.",
        "Hasard pur : {comp}. Einstein disait que Dieu ne joue pas aux dés. Moi si.",
        "J'ai lancé un dé de Méré. Il est tombé sur {comp}. Ne discutez pas avec un dé.",
        "{comp}. Le hasard fait bien les choses, demandez à Fleming et à sa boîte de Petri oubliée.",
        sans("{comp}. Aucune raison particulière. C'est ce qui rend la chose amusante."),
    ],
    # v5 : la farce. L'IA déguise l'avatar après un quiz raté. {deguisement} : ce qu'elle lui fait porter.
    "farce": [
        "Pour marquer le coup, je vous ai mis {deguisement}. Tycho Brahe portait bien un faux nez en laiton.",
        "Voilà {deguisement}. Diogène se promenait avec une lanterne en plein jour, vous survivrez une journée.",
        "{deguisement}, jusqu'à demain. Les écoliers du XIXe siècle portaient le bonnet d'âne pour moins que ça.",
        "Je vous ai prêté {deguisement}. Ne me remerciez pas, c'est pédagogique, Skinner appelait ça un renforcement.",
        "Vous voilà avec {deguisement}. Franklin a bien posé en bonnet de fourrure à la cour de France, et il a eu son traité.",
        sans("Petit cadeau : {deguisement}. Vous pouvez l'enlever. Mais je saurai."),
    ],
})

# v5 : apartés. L'IA se sert des objets et des livres débloqués, sur le ton de sa réplique.
# {objet} : nom de l'objet, en minuscule initiale ; {livre} : titre du livre.
APARTES = {
    "objet": {
        "moqueuse": [
            "Je pose {objet} sur la table, juste pour que vous sachiez ce qu'est la vraie science.",
            "Je tapote {objet}. Il a fait plus de découvertes que vous cette semaine.",
            "Je regarde {objet}, puis vous. {objet} gagne.",
            "Je vous tends {objet}. Non, finalement, je le garde.",
        ],
        "impressionnee": [
            "Je sors {objet} de sa vitrine pour fêter ça.",
            "Je fais briller {objet}. Il l'a mérité, vous aussi.",
            "J'ai posé {objet} à côté de votre nom. Il vous va bien.",
        ],
        "decue": [
            "Je range {objet} dans sa vitrine. Il ne veut pas voir ça.",
            "Je recouvre {objet} d'un drap, par respect.",
            "J'essuie {objet}. Quelqu'un doit garder sa dignité ici.",
        ],
        "impatiente": [
            "Je tapote {objet} du bout des doigts. Le temps passe.",
            "J'ai remonté {objet}. Il tourne, lui.",
            "Je regarde {objet} en attendant. Il a déjà attendu des siècles, moi non.",
        ],
        "neutre": [
            "J'époussette {objet} en vous écoutant.",
            "J'ai mis {objet} sur mon bureau. Il m'aide à réfléchir.",
            "Je prends des notes à côté de {objet}.",
        ],
    },
    "livre": {
        "moqueuse": [
            "J'ouvre « {livre} » à la page qui parle de vous. Elle est vide.",
            "Je cherche votre erreur dans « {livre} ». Elle n'y est pas : elle est trop récente.",
            "Je surligne un passage de « {livre} ». Pour vous, en fluo.",
        ],
        "impressionnee": [
            "Je note votre nom dans la marge de « {livre} ». Au crayon, mais quand même.",
            "Je referme « {livre} ». Vous n'en avez plus besoin, pour l'instant.",
        ],
        "decue": [
            "Je glisse un marque-page dans « {livre} », au chapitre que vous avez sauté.",
            "Je relis « {livre} » pour me consoler.",
        ],
        "impatiente": [
            "Je feuillette « {livre} » en attendant. J'en suis déjà au dernier chapitre.",
            "J'ai lu « {livre} » deux fois pendant votre absence.",
        ],
        "neutre": [
            "Je cite « {livre} » de mémoire. La mienne ne s'efface pas.",
            "J'ai « {livre} » ouvert sur les genoux, pour vérifier vos réponses.",
        ],
    },
}


# Expression du masque selon le contexte de la réplique.
EXPRESSIONS = {
    "accueil": "neutre", "livre": "neutre", "date": "neutre", "bonus_du_jour": "neutre",
    "quiz_parfait_facile": "impressionnee", "quiz_parfait": "impressionnee", "quiz_reussi": "neutre",
    "rappel_reussi": "impressionnee", "eureka": "impressionnee", "prison_liberation": "impressionnee",
    "tour_fini": "impressionnee", "masque": "moqueuse", "plateau_avance": "neutre",
    "quiz_rate_facile": "moqueuse", "quiz_rate": "moqueuse", "quiz_zero": "moqueuse",
    "eclair": "moqueuse", "mode_test": "moqueuse", "retour": "moqueuse", "piege": "moqueuse",
    "prison": "moqueuse", "quarantaine": "moqueuse", "retour_epoque": "moqueuse",
    "rappel_perdu": "decue", "retards": "impatiente", "rappel_retard": "impatiente", "nuit": "impatiente",
    "jouer_rappel": "impatiente", "jouer_bonus": "neutre", "jouer_faible": "moqueuse", "jouer_hasard": "moqueuse",
    "jouer_case": "neutre", "jouer_hors_case": "moqueuse", "jouer_ouvre_arbre": "impressionnee",
    "farce": "moqueuse",
    "ennemi": "moqueuse", "duel_gagne": "impressionnee", "duel_perdu": "moqueuse",
}


# v7 : l'IA arbitre les duels contre les ennemis du plateau.
REPLIQUES.update({
    "ennemi": [
        "Un ennemi vous barre la route. Cinq affirmations, aucune erreur permise. Comme au procès de Galilée, mais avec des règles.",
        "La commission de 1784 a démasqué Mesmer avec des bandeaux sur les yeux. Vous avez le droit de garder les vôtres ouverts. Servez-vous-en.",
        "Le doute méthodique de Descartes est autorisé pendant ce duel. Recommandé, même.",
        "Arbitrage officiel. Je compte les points, je ne prends pas parti. Enfin, un peu.",
        sans("Duel ! Lui d'un côté, vous de l'autre, moi au milieu. Ne me décevez pas, je déteste perdre par procuration."),
    ],
    "duel_gagne": [
        "Victoire. Carl Sagan disait que les affirmations extraordinaires demandent des preuves extraordinaires. Vous en aviez cinq.",
        "Hume : le sage proportionne sa croyance à l'évidence. Vous venez de proportionner.",
        "Les historiens ont mis un siècle à enterrer le mythe de la Terre plate médiévale. Vous, cinq questions.",
        sans("Cinq sur cinq. Je note dans mon registre : esprit critique, présent."),
    ],
    "duel_perdu": [
        "Perdu. Selon la loi de Brandolini, réfuter une ânerie demande dix fois plus d'énergie que de la produire. Rechargez.",
        "Un mensonge fait le tour du monde avant que la vérité ait mis ses chaussures. La phrase est attribuée à Mark Twain, à tort. Lacez les vôtres.",
        "Même Newton a cru à l'alchimie. Vous êtes en bonne compagnie, mais du mauvais côté du plateau.",
        sans("Une seule erreur, et il reste planté là. Il ne bougera pas tant que vous ne l'aurez pas battu."),
    ],
})

# v8 : cases pièges du plateau ludique (téléportation, révision forcée).
import pieges  # noqa: E402
REPLIQUES.update({k: [sans(l[1]) if isinstance(l, tuple) else l for l in v] for k, v in pieges.REPLIQUES.items()})
EXPRESSIONS.update(pieges.TONS)

# v9 : le jeu de Mendeleïev (atomes sauvages, capture, fuite).
import mendeleiev  # noqa: E402
REPLIQUES.update({k: [sans(l[1]) if isinstance(l, tuple) else l for l in v] for k, v in mendeleiev.REPLIQUES.items()})
EXPRESSIONS.update(mendeleiev.TONS)

# v10 : la faveur de l'IA et ses cadeaux préférés.
import brillants  # noqa: E402
REPLIQUES.update({k: [sans(l[1]) if isinstance(l, tuple) else l for l in v] for k, v in brillants.REPLIQUES.items()})
EXPRESSIONS.update(brillants.TONS)

# v12 : le mur de la honte.
import honte  # noqa: E402
REPLIQUES.update({k: [sans(l[1]) if isinstance(l, tuple) else l for l in v] for k, v in honte.REPLIQUES.items()})
EXPRESSIONS.update(honte.TONS)

# v7 : surnom que l'IA donne au joueur, affiché sous le rang. Il suit son humeur (dernier résultat),
# ou juste après un succès, ce succès ({succes}). Groupes nominaux épicènes : le joueur peut être n'importe qui.
SURNOMS = {
    "neutre": ["Esprit en rodage", "Curiosité ambulante", "Stagiaire du Savoir", "Candidature à l'étude",
               "Promesse à confirmer", "Cerveau en préchauffage", "Lecture en cours", "Recrue du Comité"],
    "moqueuse": ["Tour de Pise ambulante", "Phlogistique sur pattes", "Éponge imperméable", "Génie en sommeil profond",
                 "Bibliothèque fermée pour travaux", "Spécialiste du presque", "Boussole qui indique le sud",
                 "Expérience non reproductible"],
    "impressionnee": ["Petite lumière des Lumières", "Encyclopédie en devenir", "Terreur des quiz", "Sans-faute ambulant",
                      "Fierté du Comité", "Synapse en feu", "Machine à bonnes réponses", "Erreur statistique (dans le bon sens)"],
    "decue": ["Mémoire de poisson rouge", "Passoire à souvenirs", "Ex-spécialiste", "Amnésie en cours",
              "Savoir à durée limitée", "Ancienne gloire", "Courbe de l'oubli incarnée", "Cerveau en fuite"],
    "impatiente": ["Rappel en souffrance", "Retard chronique", "Absence remarquée", "Fantôme du Comité",
                   "Promesse non tenue", "Disparition inquiétante", "Rendez-vous manqué", "Sablier oublié"],
    "succes": ["Titulaire de « {succes} »", "Décoration toute fraîche : « {succes} »", "Médaille « {succes} » au revers",
               "Couronne « {succes} », encore tiède", "Auréole « {succes} » (provisoire)"],
}


def repliques():
    out = []
    for contexte, lignes in REPLIQUES.items():
        for i, texte in enumerate(lignes, 1):
            out.append({"id": f"{contexte.replace('_', '-')}.{i:02d}", "contexte": contexte,
                        "texte": fr(texte), "reference": not isinstance(texte, sans)})
    return out


def surnoms():
    return {ton: [fr(t) for t in lignes] for ton, lignes in SURNOMS.items()}


def apartes():
    """Apartés : [{id, sorte, ton, texte}], sorte « objet » ou « livre »."""
    return [{"id": f"aparte-{sorte}-{ton}.{i:02d}", "sorte": sorte, "ton": ton, "texte": fr(t)}
            for sorte, tons in APARTES.items() for ton, lignes in tons.items() for i, t in enumerate(lignes, 1)]


if __name__ == "__main__":
    r = repliques()
    ref = sum(x["reference"] for x in r)
    print(len(r), "répliques,", f"{ref / len(r):.0%} avec référence,", len(REPLIQUES), "contextes")
    assert set(REPLIQUES) == set(EXPRESSIONS)
