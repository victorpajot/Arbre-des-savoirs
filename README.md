# Arbre des savoirs, v10

Page jouable : https://claude.ai/artifact/XsArLs3oJmQyF2ua2GoHGa

## Organisation

| Dossier | Contenu |
| --- | --- |
| `data/` | Le contenu du jeu, généré par `outils/contenu.py` : `regles.json`, `skills.json`, `questions.json`, `succes.json`, `commentaires.json` (les répliques de l'IA), `ia.json` (ses masques), `objets.json` (le cabinet de curiosités), `avatar.json`, `plateau.json`, `frise.json`, `bibliotheque.json`, `ennemis.json`, `atomes.json` (les 118 éléments du jeu de Mendeleïev), plus `schema.json` qui les valide. |
| `web/moteur.js` | Les règles pures (XP, maîtrise, rappels, perte, gel, succès). Aucun affichage, aucun stockage. |
| `web/index.html` | L'interface web. |
| `outils/contenu.py` | Source du contenu : régénère `data/` (`python3 outils/contenu.py`). Il assemble `questions_nouvelles.py` (questions v2), `approfondissement_sciences.py` et `approfondissement_humain.py` (second losange, rangs 5 à 8), `philosophes.py` (branche Sagesse), `illustrations.py` (schémas SVG), `recompenses.py` (succès v2, objets, accessoires), `plateau.py` (63 cases, dates de la frise, succès du plateau), `bibliotheque.py` (32 livres), `ia.py` (répliques) et le pixel art (`dessin.py`, `objets32.py`, `avatar40.py`, `masques.py`, `masques_v4.py`, `savants.py`, `objectifs.py`, `icones32.py`, chacun exécutable pour produire une planche d'aperçu PNG). |
| `outils/valider.py` | Valide `data/` contre le schéma et vérifie les liens entre fichiers. |
| `outils/test_moteur.js` | Test du cycle quiz, rappel, perte, regain (`node outils/test_moteur.js`). |

## Nouveautés de la v10 (faveur de l'IA)

- L'IA a une jauge de faveur de 0 à 100, qui perd 8 points par jour. Un cadeau par jour la fait remonter selon l'éclat de l'objet : 12 points s'il est terne, 25 s'il brille, 45 s'il éblouit ou en fait trop. Un objet déjà offert peut l'être de nouveau après 14 jours, pour moitié moins.
- Quatre paliers : comblée (butin plus fréquent, une case de plus par épreuve réussie), contente (règles ordinaires), boudeuse (moitié moins de butin), furieuse (plus de butin, une case de moins, et chaque jour un piège posé devant le pion).
- Neuf objets brillants tirés de l'histoire des sciences (`outils/brillants.py`) : couronne de Hiéron, miroir ardent d'Archimède, nez de Tycho Brahe, lampe de la cathédrale de Pise, diamant de Lavoisier, feuille d'or de Rutherford, verre à l'uranium, bobine de Tesla, médailles Nobel dissoutes par Hevesy. 55 objets en tout.
- Le menu Personnage passe en onglets : Stats, Avatar, IA (faveur, cadeaux, masques), Ennemis (l'ancien bestiaire), Réglages. Sur l'accueil, la date disparaît et la bulle de l'IA ouvre son onglet, avec sa faveur affichée dessous.

## Nouveautés de la v9 (jeu de Mendeleïev)

- Cinq cases Mendeleïev sur le plateau (10, 31, 48, 53, 55), chacune justifiée par l'histoire de sa case. Les traverser ou s'y arrêter fait apparaître un atome sauvage, dont on ne connaît que le nom. Trois au plus attendent leur combat, sur l'accueil.
- Combat en trois questions : symbole, masse atomique, lieu où on le croise. Deux bonnes réponses le capturent ; sinon il s'enfuit et pourra revenir. Les leurres sont tirés pour ne jamais partager de mot avec la bonne réponse.
- Le tableau périodique, onglet Atomes des Collections, sert de Pokédex : 118 éléments en quatre raretés (commun, peu commun, rare, légendaire pour les superlourds), une fiche par atome capturé (masse, famille, trois lieux du quotidien, anecdote, source de la Royal Society of Chemistry).
- Dix succès (premier atome, 10, 30, 63 comme en 1869, 92, 118, familles complètes, fuites) et des répliques de l'IA pour l'apparition, la capture et la fuite. Contenu dans `outils/mendeleiev.py`.
- Les flèches de téléportation longent la route au lieu de traverser les cases.
- Les cartes de récompense affichent directement leur texte (notice, anecdote, citation), sans bouton à déplier.

## Nouveautés de la v8 (plateau ludique)

- Plateau en route sinueuse façon jeu de l'oie illustré : six allers-retours ondulés, cases multicolores numérotées, panneaux Départ et Arrivée, flèches de téléportation.
- Le fond est une planche ancienne qui suit l'humeur de l'IA : atlas céleste (neutre), carnet de Léonard (impressionnée), planche de l'Encyclopédie (moqueuse), tableau noir du physicien (déçue). Le plateau s'ouvre en vue d'ensemble, avec une caméra libre : pincement, molette ou boutons + et − pour zoomer, glisser pour se déplacer, sans faire bouger la page. Le pion a un halo, un double contour et une flèche. La bulle de l'IA a un fond teinté qui la détache du reste.
- Cinq cases cadeau (5, 23, 37, 47, 58) : un objet du cabinet tombe sans épreuve.
- 19 livres de plus pour l'Antiquité et le Moyen Âge (`outils/bibliotheque_v8.py`), débloqués sur les premières cases du plateau, et 10 livres de la Renaissance : 109 livres en tout.
- Huit nouvelles cases pièges (`outils/pieges.py`), chacune justifiée par l'histoire de sa case : reculs, téléportations en arrière, et révisions forcées. Une révision forcée bloque le pion jusqu'à ce qu'on révise la compétence maîtrisée dont le rappel est le plus lointain ; ratée, la compétence n'est pas perdue mais son rappel devient dû.

## Nouveautés de la v7 (lot 3)

- Frise en cylindre vue de côté : passé à gauche, futur à droite, dates non découvertes en ombres, glisser pour tourner, appui sur la date du centre pour la lire, sauts d'époque.
- Bibliothèque de 80 livres, un par compétence (`outils/bibliotheque_v7.py`), débloqués en maîtrisant la compétence.
- 40 savants jouables : 20 nouveaux, avec davantage de femmes et de figures non européennes.

## Nouveautés de la v7 (lot 2)

- Ennemis du plateau (`data/ennemis.json`, généré par `outils/ennemis.py`) : sept archétypes de la bêtise humaine et deux figures historiques (Lyssenko, Mesmer), posés au début de chaque tour ; le Charlatan attend en réserve. Passer sur un ennemi arrête le pion et lance un duel : cinq affirmations vraies ou fausses (80 au total, chacune avec son origine et une source), sans-faute obligatoire. Victoire : l'ennemi quitte le plateau jusqu'au tour suivant, le pion finit son trajet, un butin tombe, un succès à la première victoire. Défaite : le pion reste et le duel reprend à l'épreuve réussie suivante.
- Écran VS : l'avatar glisse de la gauche, l'ennemi de la droite, l'IA arbitre (contextes `ennemi`, `duel_gagne`, `duel_perdu`).
- Bestiaire (onglet Collections) : victoires, défaites, meilleure série et dernier duel par ennemi ; silhouettes pour ceux qu'on n'a pas croisés.
- Cadeaux à l'IA : depuis la fiche d'un objet, un par jour et une fois par objet (`objets[].cadeau`, `outils/cadeaux.py`). L'IA répond, garde parfois l'objet près de son masque, et fait avancer ou reculer le pion, déplace une case spéciale, ajoute un ennemi, ou rien.

## Nouveautés de la v7 (lot 1)

- Trois arbres ouverts au départ : Logique, Mécanique, Savoir (`regles.arbres_fondamentaux`). Les sept autres s'ouvrent par un succès pionnier (`succes[].ouvre`, généré par `outils/pionniers.py`) : Cicéron (2 compétences maîtrisées), Lavoisier (3), Galilée (4), Bacon (5), Faraday (6), William James (7), Socrate (9). Une partie existante garde les arbres où elle a déjà joué. Mode test : « Ouvrir tous les arbres ».
- Accueil : le rang et un surnom donné par l'IA (`commentaires.surnoms`), selon son humeur après la dernière épreuve, ou le succès du jour. Les pastilles de stats disparaissent.
- Personnage : les fiches de branche d'abord. Collections : Frise, Bibliothèque, Objets.
- Plateau zoomé sur le pion, qu'on fait glisser au doigt ; « Vue d'ensemble » et « Recentrer ». La caméra suit le pion dans le bilan.

## Nouveautés de la v6

- **Bilan en trois temps** : le verdict et la réplique de l'IA, puis chaque récompense seule et animée, puis un plateau réduit où le pion avance case par case. « Passer » mène directement au plateau.
- **Butin rare** : objets, livres, accessoires et masques ne se donnent plus d'office. Leur condition les rend « gagnables » (`partie.gagnables`), puis chaque épreuve réussie a une chance d'en faire tomber un seul (`plateau.regles.butin` : 40 % pour un rappel, de 45 % au rang 1 à 80 % au rang 8). Chaque butin appartient à un lot de 1 à 7 (`lot`, attribué par `assigner_lots` dans `contenu.py` selon la difficulté de sa condition) et ne tombe qu'à partir du tour de même numéro. Les reliques des tours restent données d'office. En simulation, la collection est complète entre le tour 12 et le tour 28. Moteur : `tirerButin`, `butinOuvert`, `chanceButin`.
- **Deux façons de jouer** : le bouton Jouer, ou une compétence choisie dans l'arbre. Une épreuve réussie fait avancer d'autant de cases que son rang, rappels compris, et de 2 de plus par Jouer. Les bonus sans faute, chrono et du jour ne comptent plus sur le plateau.
- **Stats** : sur l'accueil, dix pastilles de niveau ; dans Personnage, une fiche par branche avec son niveau, son titre (Novice, Apprenti…), une pastille par compétence et ce qu'il reste à faire.
- **Savant incarné** : le dernier débloqué par les succès (`savantActuel`). Les accessoires restent au choix.
- **Accueil** : la réplique de l'IA en tête, puis le personnage, Jouer et le plateau.
- **Sauvegarde** : même format (4). Les acquis restent ; le butin s'applique aux déblocages à venir.

## Nouveautés de la v5

- **Plateau lisible** : les cases sont posées sur une route en spirale, fléchée dans le sens de la marche, du fanion « Départ » à l'objectif central. La route parcourue et les cases visitées prennent la couleur, les prochaines cases atteignables sont cerclées en pointillé. Le liseré de l'objectif clignote doucement (coupé si le mouvement réduit est demandé).
- **Bouton « Jouer »** : l'IA choisit l'épreuve (un rappel dû d'abord, sinon le bonus du jour, la stat la plus faible ou le hasard) et l'annonce. Réussie, l'épreuve rapporte +2 cases (`plateau.regles.bonus.jouer`). Moteur : `choixIA`.
- **L'IA agit seule** : le joueur ne choisit plus son masque. Chaque masque porte des tons (`ia.json`, `tons`) ; l'IA prend un masque gagné qui va au ton de sa réplique (`masquePourTon`). Environ une réplique sur deux, elle se sert d'un objet ou d'un livre débloqué (`commentaires.json`, `apartes` ; moteur : `aparte`).
- **Farces** : après une épreuve ratée, une fois sur trois, l'IA déguise l'avatar pour 24 h (accessoire ou savant gagné). Bouton « Rendre mon visage ». Moteur : `tenterFarce`, `farceActive`, `rendreVisage`.
- **Succès** : les récompenses d'un bilan défilent une par une, avec une petite animation ; citations et notices sont repliées. « Ouvrir le livre » s'ouvre au-dessus du bilan et « Retour au bilan » y ramène.
- **Stats sur l'accueil** : radar compact et une jauge par stat sous l'avatar.
- **Sauvegarde** : même format (4). Le masque choisi par le joueur est simplement oublié à la lecture.

## Nouveautés de la v4

- **Second losange** : chaque branche passe de 4 à 8 compétences (40 nouvelles, 480 questions, 40 dates de frise). Le second losange se déplie quand le sommet du premier est maîtrisé. 80 compétences, 960 questions.
- **Niveaux** : 20 niveaux par branche. Un rappel réussi rapporte de plus en plus selon l'étape atteinte (5, 10, 15, 20, 30, 40, 50 XP) : garder un savoir longtemps fait monter. Une branche complète, jouée un an avec ses rappels, atteint le niveau 15.
- **Plateau depuis l'accueil** : panneau « Ton tour » sous le plateau (épreuves jouables triées par valeur, en faces de dé), le pion s'ouvre au toucher et avance case par case au retour d'un quiz.
- **Case centrale** : l'objectif du tour, encadré d'or. Sept reliques (flamme de Prométhée, pierre philosophale, mécanisme d'Anticythère, Principia, ruban de Turing, disque d'or de Voyager, démon de Laplace), chacune gagnée en terminant son tour, avec un succès et un masque.
- **24 masques de l'IA**, de Talos à AlphaGo : 12 par paliers de succès, 12 par des succès précis (dont les 7 tours). Le joueur choisit celui que porte l'IA.
- **20 savants jouables**, d'Aristote à Katherine Johnson, débloqués par des succès ou des compétences liés à leur histoire. Ils remplacent l'avatar ; les accessoires de visage restent, ceux de tête deviennent des déguisements ; le rang se lit au cadre.
- **Radar** gradué de 0 à 20 avec le niveau de chaque branche.
- 102 succès. Sauvegarde au format 4 ; `migrer()` reprend une partie v3 et recalcule l'XP des rappels déjà faits au nouveau barème.

## Nouveautés de la v3

- **Plateau de l'histoire** : un jeu de l'oie de 63 cases, du feu à l'IA, chacune avec son histoire sourcée et sa réplique. Pas de dé : rappel réussi +1, quiz de rang 1 +2, rangs 2 et 3 +3, rang 4 +4 ; +1 sans faute, +1 avec le chrono, +2 sur la branche du bonus du jour. Quiz raté : sur place ; rappel raté : 2 cases en arrière. Cases spéciales : Eurêka (multiples de 9, on rejoue la même distance), incendie d'Alexandrie, Fibonacci, peste, procès de Galilée, guillotine, Solvay. L'arrivée relance un tour où les pièges comptent double.
- **Collections** (remplace l'onglet Cabinet) : Objets, Frise (103 dates en 6 époques, filtrables par branche) et Bibliothèque (32 livres sur des étagères, résumé, importance, anecdote, réaction de l'IA).
- **L'IA** remplace le Comité de lecture : 208 répliques (89 % citent l'histoire des sciences), 27 contextes, jamais deux fois la même avant d'avoir épuisé le contexte. Six masques débloqués par paliers de succès, chacun avec cinq expressions.
- **Sagesse (Philosophes)** : 10e branche, découpée par époques, 48 questions, 8 succès, 5 objets.
- Pixel art doublé : objets et icônes en 32 × 32, avatar et masques en 40 × 48, avec modelé et contour.
- 93 succès. Sauvegarde au format 3 ; `migrer()` reprend une partie v2 sans perte (le pion part du feu, dates et livres déjà mérités sont rattrapés).
- Mode test : boutons « Pion +6 / +20 cases » dans l'onglet Personnage.

## Nouveautés de la v2

- 9 branches et 36 compétences : Alchimie (chimie), Cosmos (astronomie) et Étincelle (électricité) rejoignent les six premières ; Savoir se recentre sur le vivant (la génétique remplace les atomes, qui passent en Alchimie avec leur XP).
- 432 questions, dont 23 avec un schéma (champ `illustration`, ou `illustration_explication` quand le schéma donnerait la réponse).
- Le Comité de lecture (devenu l'IA en v3), narrateur moqueur : 90 répliques déclenchées par le contexte (quiz facile réussi ou raté, zéro, réponse fausse en moins de 2 s, quiz nocturne, mode test, retour après absence).
- 69 succès, tous cachés et sourcés, dont une série de mythes démontés.
- Avatar en pixel art : 5 rangs selon le niveau global, 11 accessoires gagnés par des succès, et un objet du cabinet à tenir en main.
- Cabinet de curiosités : 34 objets de l'histoire des sciences, chacun avec sa notice et sa source.
- La sauvegarde passe au format 2 ; `migrer()` reprend une partie v1 sans perte.

## Règles par défaut (modifiables dans `regles.json`)

- Quiz de 5 questions tirées parmi 12 ; maîtrise à 4/5. XP = 10 par bonne réponse + 20 de bonus.
- Rappels à 1, 3, 7, 14, 30, 90 puis 180 jours ; 3 questions, 2 justes requises ; +5, 10, 15, 20, 30, 40 puis 50 XP par rappel réussi selon l'étape.
- Rappel raté : compétence perdue, XP retirée, retour à « disponible ». Les compétences qui en dépendent sont gelées, pas perdues.
- Rappel en retard : pas de pénalité tant qu'il n'est pas raté.
- Chrono en option (onglet Personnage) : 30 s par question, +5 XP par bonne réponse ; temps écoulé = réponse fausse.
- Tous les succès sont cachés jusqu'à leur obtention.

## Intégration mobile et Unreal

- **Mobile** : embarquer `data/` dans l'app (ou le télécharger à jour) et porter `moteur.js` tel quel (React Native, Capacitor) ou fonction par fonction. La routine du matin = `rappelsDus()` + `suggestion()`, déclenchée par une notification locale.
- **Unreal** : chaque fichier contient un tableau plat d'objets à id texte stable. Le pixel art est stocké en lignes de caractères + palette : une texture se reconstruit pixel par pixel. Les schémas SVG n'utilisent que des classes (liste dans `outils/illustrations.py`). Un struct par type (`FCompetence`, `FQuestion`, `FSucces`) et un import JSON en DataTable suffisent ; les textes sont des objets `{"fr": "..."}` à aplatir en colonne par langue si besoin.
- **Sauvegarde** : un objet JSON versionné (`format: 4`) ; `migrer()` le met à niveau. Le même fichier exporté depuis le web peut être importé ailleurs.

## v11 : les masques de l'IA changent les règles

- Chaque matin, l'IA choisit de 1 à 3 masques parmi ceux qu'elle a gagnés, selon sa faveur : comblée, des masques cléments ou neutres ; furieuse, des masques cruels. Leurs règles s'additionnent jusqu'au lendemain (`outils/masques_regles.py`) : butin, cases d'avance, nombre de questions du quiz, ennemis absents ou en renfort, pièges désarmés, recul d'un rappel raté, seuil de capture d'un atome.
- Fiche IA : son visage du jour et son portrait en tête, puis ses masques du jour avec leurs règles.
- Objets : « Offrir à l'IA » en premier ; chaque objet a une citation de sa source (`outils/objets_v11.py`), affichée quand on l'offre ou qu'on le donne à son avatar. Un objet tenu donne un coup de pouce sur environ une épreuve réussie sur quatre (case, butin assuré ou faveur).

## v12 : le mur de la honte

- Chaque réponse fausse d'un quiz ou d'un rappel est épinglée au mur de la honte (`partie.oublis`, 30 jours), avec la réponse donnée.
- La vue « Le mur de la honte » range les ratées du jour par thème : énoncé, ta réponse, la bonne, l'explication, puis la fiche de révision du thème.
- Fiches de révision pour les 80 compétences (`outils/fiches.py`) : l'essentiel, le piège classique, un schéma (`outils/schemas_fiches.py`) et une source. Elles s'ouvrent aussi depuis la fiche d'une compétence dans l'arbre.
- À partir du lendemain, on peut retenter une question : réussie, elle est « réhabilitée » et quitte le mur. L'IA y envoie depuis sa bulle de l'accueil, un bloc de l'accueil et le bilan du quiz. 4 succès (`outils/honte.py`).

## v13 : plateau plus lisible

- Projecteur sur la case d'arrivée : à la fin du trajet, le plateau passe en gris, le pion s'efface, la case grandit avec son étiquette (numéro, année, titre), puis tout revient.
- Ennemis : portrait cerclé de rouge épinglé au-dessus de la case, avec un liseré qui pulse et un « ! ». À la rencontre, flash rouge, plateau teinté, l'ennemi bondit avec un bandeau « VS ».

## v14 : retours de lecture

- Plateau : l'assombrissement du projecteur est un voile (rectangle) au lieu d'un filtre CSS ; au glisser, une mise à jour par image et animations en pause, pour supprimer les à-coups.
- Frise : seules les dates découvertes s'affichent par défaut ; un interrupteur montre les autres.
- Bilan : le mur de la honte s'ouvre par-dessus le bilan ; « ← Bilan » ramène à la même étape.
- Textes de lecture (paroles de l'IA, succès, récompenses, notes) agrandis à 15-17 px.

## v15 : la case dicte l'épreuve

- Plateau : chaque case prend la couleur de son arbre. Le bouton Jouer tire l'épreuve dans l'arbre de la case du pion (les rappels dus passent d'abord) ; sur un arbre fermé, il propose son premier quiz, et le réussir ouvre l'arbre.
- Livres : pas d'anachronisme. Un livre ne tombe que s'il est paru avant la fin de l'époque de la case, de préférence dans cette époque.
- Schémas : dix planches légendées façon manuel (cellules, bactérie et virus, atome, ADN, neurone, cerveau, organes, eau, cycle du carbone), dans les retours de quiz et les fiches de révision ; un toucher les agrandit.
- Épreuves coupées : dès que le seuil n'est plus atteignable (quiz, rappel, duel, atome), l'épreuve s'arrête sans dévoiler les questions restantes.
- Une seule récompense (savant, livre ou objet) par épreuve ; la suivante attend l'épreuve d'après.
- Cases cachées : seules les cases où le pion s'arrête sont dévoilées et débloquent leur date et leurs livres. Bouton « Avancer d'une seule case » (sans bonus) sous « C'est parti ».
- Trou de mémoire (cases 17 et 60) et quatre ennemis (Ussher, Lyssenko, le complotiste, le raconteur) renvoient le pion à la plus ancienne case jamais vue, parmi les 15 derrière lui.
- Compteur d'épreuves par tour et record du tour le plus court.
- Case du pion (toucher le pion) : dessin et histoire en grand, « Où tu en es » (tour, étape, épreuves, arbre, proposition de l'IA, blocages, prochain ennemi) et « Jouer depuis cette case ». Fin d'épreuve : « Jouer l'épreuve suivante » sans repasser par l'accueil. Badge de compétence (couleur de l'arbre, symbole de outils/symboles.py, niveau) en tête des quiz. Fond vert ou mauve au verdict d'un duel.
- Duels : arène rouge sombre en flammes, rencontre rejouée quand l'ennemi bloque toujours le pion, 16 ennemis (outils/ennemis.py) dont l'IA poste sept à chaque tour, sur des cases décalées.
- Atomes : le combat demande le numéro atomique, plus la masse.
- Questions dont la réponse est une personne : portrait en pixel art et biographie au retour (outils/portraits.py).
- Chrono activé sur les nouvelles parties ; question en cours en encre dans la barre de progression.

## v16 : crédits et corruption

- Chaque succès rapporte des crédits selon son genre (`outils/credits.py`) ; l'IA multiplie le tarif selon son humeur, penchée par sa faveur, et le commente.
- Pot-de-vin quotidien dans l'onglet IA : au-dessus de son record, faveur et coup de pouce ; égal, moitié de faveur ; en dessous, elle se vexe et pose un piège.
- Les erreurs agacent l'IA : −2 de faveur par erreur, −6 de plus pour une épreuve ratée.
- Ses goûts (ce qui brille) se découvrent à l'usage, après plusieurs cadeaux.
- Frise : au premier tour, une date de compétence attend que le pion ait atteint son époque.
- « Avancer d'une seule case » : le joueur choisit l'arbre. Feuille Jouer ouverte sur la case du pion, en grand.
- Pion posé au-dessus de sa case, qui reste lisible ; silhouette et flash quand un avatar change.

## v17 : succès illustrés, ultimatum

- Chaque succès a son image en pixel art (`outils/succes_pixels.py` : 33 dessins neufs, sinon objet, case, ennemi ou savant).
- Carte de succès : « +20 crédits −10 (décision de l'IA) = 10 crédits ».
- Crédits affichés à côté du niveau. Ultimatum de l'IA : payer (exigence suivante ×1,5) ou refuser (elle verse la somme, retire 2 vrais niveaux).
- Plateau : plus d'animations en boucle dans le bilan ni sur Android, dessin repeint après le projecteur.
