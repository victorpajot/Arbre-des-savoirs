# Consignes pour les agents (IA) qui travaillent sur ce dépôt

Arbre des savoirs est un jeu d'apprentissage : des arbres de compétences façon RPG sur des savoirs réels, des quiz, des
rappels selon la courbe de l'oubli, un plateau et une IA narratrice moqueuse, Alyca. Le projet est en français.

## Où est quoi

- Le contenu est dans `packs/` (un dossier par pack) ; `data/` est **généré** par `python3 outils/packs.py assembler`.
- Ajouter ou modifier un domaine de savoir : suivre **[packs/LISEZMOI-IA.md](packs/LISEZMOI-IA.md)** (exemple complet :
  `packs/musique/`, squelette : `packs/_modele/`).
- Le moteur (`web/moteur.js`) et l'interface (`web/index.html`) ; l'appli mobile s'assemble avec `node mobile/construire.js`.

## Règles

1. **Rien d'inventé.** Chaque fait sourcé est vérifié en ligne puis inscrit avec
   `python3 outils/verifier_sources.py --inscrire CLE URL "contrôle"`. Un fait qu'on ne peut pas vérifier est retiré.
2. **Tests avant chaque commit** : `git config core.hooksPath .githooks` une fois par clone ; le crochet assemble les
   packs, vérifie les sources, la syntaxe JS, le schéma, puis lance `node outils/test_moteur.js`,
   `python3 outils/test_packs.py` et `node outils/test_packs.js` (une dizaine de secondes). Ne jamais le contourner.
3. **Questions de calcul** : l'explication pose la formule en lettres, fait le calcul complet et dit qui a trouvé la
   formule (champ `source`).
4. **Textes lisibles** : paroles d'Alyca, succès et récompenses à 17 px au moins dans l'interface.
5. Le workflow de compilation de l'APK sur `main` doit rester rapide.
