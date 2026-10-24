# Arbre des savoirs, v2

Page jouable : https://claude.ai/artifact/XsArLs3oJmQyF2ua2GoHGa

## Organisation

| Dossier | Contenu |
| --- | --- |
| `data/` | Le contenu du jeu, généré par `outils/contenu.py` : `regles.json`, `skills.json`, `questions.json`, `succes.json`, `commentaires.json` (le narrateur), `objets.json` (le cabinet de curiosités), `avatar.json`, plus `schema.json` qui les valide. |
| `web/moteur.js` | Les règles pures (XP, maîtrise, rappels, perte, gel, succès). Aucun affichage, aucun stockage. |
| `web/index.html` | L'interface web. |
| `outils/contenu.py` | Source du contenu : régénère `data/` (`python3 outils/contenu.py`). Il assemble `questions_nouvelles.py` (questions v2), `illustrations.py` (schémas SVG), `recompenses.py` (succès v2, narrateur, objets, accessoires) et `pixels.py` (pixel art). |
| `outils/valider.py` | Valide `data/` contre le schéma et vérifie les liens entre fichiers. |
| `outils/test_moteur.js` | Test du cycle quiz, rappel, perte, regain (`node outils/test_moteur.js`). |

## Nouveautés de la v2

- 9 branches et 36 compétences : Alchimie (chimie), Cosmos (astronomie) et Étincelle (électricité) rejoignent les six premières ; Savoir se recentre sur le vivant (la génétique remplace les atomes, qui passent en Alchimie avec leur XP).
- 432 questions, dont 23 avec un schéma (champ `illustration`, ou `illustration_explication` quand le schéma donnerait la réponse).
- Le Comité de lecture, narrateur moqueur : 90 répliques déclenchées par le contexte (quiz facile réussi ou raté, zéro, réponse fausse en moins de 2 s, quiz nocturne, mode test, retour après absence).
- 69 succès, tous cachés et sourcés, dont une série de mythes démontés.
- Avatar en pixel art : 5 rangs selon le niveau global, 11 accessoires gagnés par des succès, et un objet du cabinet à tenir en main.
- Cabinet de curiosités : 34 objets de l'histoire des sciences, chacun avec sa notice et sa source.
- La sauvegarde passe au format 2 ; `migrer()` reprend une partie v1 sans perte.

## Règles par défaut (modifiables dans `regles.json`)

- Quiz de 5 questions tirées parmi 12 ; maîtrise à 4/5. XP = 10 par bonne réponse + 20 de bonus.
- Rappels à 1, 3, 7, 14, 30, 90 puis 180 jours ; 3 questions, 2 justes requises ; +5 XP par rappel réussi.
- Rappel raté : compétence perdue, XP retirée, retour à « disponible ». Les compétences qui en dépendent sont gelées, pas perdues.
- Rappel en retard : pas de pénalité tant qu'il n'est pas raté.
- Chrono en option (onglet Personnage) : 30 s par question, +5 XP par bonne réponse ; temps écoulé = réponse fausse.
- Tous les succès sont cachés jusqu'à leur obtention.

## Intégration mobile et Unreal

- **Mobile** : embarquer `data/` dans l'app (ou le télécharger à jour) et porter `moteur.js` tel quel (React Native, Capacitor) ou fonction par fonction. La routine du matin = `rappelsDus()` + `suggestion()`, déclenchée par une notification locale.
- **Unreal** : chaque fichier contient un tableau plat d'objets à id texte stable. Le pixel art est stocké en lignes de caractères + palette : une texture se reconstruit pixel par pixel. Les schémas SVG n'utilisent que des classes (liste dans `outils/illustrations.py`). Un struct par type (`FCompetence`, `FQuestion`, `FSucces`) et un import JSON en DataTable suffisent ; les textes sont des objets `{"fr": "..."}` à aplatir en colonne par langue si besoin.
- **Sauvegarde** : un objet JSON versionné (`format: 2`) ; `migrer()` le met à niveau. Le même fichier exporté depuis le web peut être importé ailleurs.
