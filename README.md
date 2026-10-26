# Arbre des savoirs, v5

Page jouable : https://claude.ai/artifact/XsArLs3oJmQyF2ua2GoHGa

## Organisation

| Dossier | Contenu |
| --- | --- |
| `data/` | Le contenu du jeu, généré par `outils/contenu.py` : `regles.json`, `skills.json`, `questions.json`, `succes.json`, `commentaires.json` (les répliques de l'IA), `ia.json` (ses masques), `objets.json` (le cabinet de curiosités), `avatar.json`, `plateau.json`, `frise.json`, `bibliotheque.json`, plus `schema.json` qui les valide. |
| `web/moteur.js` | Les règles pures (XP, maîtrise, rappels, perte, gel, succès). Aucun affichage, aucun stockage. |
| `web/index.html` | L'interface web. |
| `outils/contenu.py` | Source du contenu : régénère `data/` (`python3 outils/contenu.py`). Il assemble `questions_nouvelles.py` (questions v2), `approfondissement_sciences.py` et `approfondissement_humain.py` (second losange, rangs 5 à 8), `philosophes.py` (branche Sagesse), `illustrations.py` (schémas SVG), `recompenses.py` (succès v2, objets, accessoires), `plateau.py` (63 cases, dates de la frise, succès du plateau), `bibliotheque.py` (32 livres), `ia.py` (répliques) et le pixel art (`dessin.py`, `objets32.py`, `avatar40.py`, `masques.py`, `masques_v4.py`, `savants.py`, `objectifs.py`, `icones32.py`, chacun exécutable pour produire une planche d'aperçu PNG). |
| `outils/valider.py` | Valide `data/` contre le schéma et vérifie les liens entre fichiers. |
| `outils/test_moteur.js` | Test du cycle quiz, rappel, perte, regain (`node outils/test_moteur.js`). |

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
