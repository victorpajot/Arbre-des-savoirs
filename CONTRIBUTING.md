# Contribuer à l'Arbre des savoirs

Merci de vouloir améliorer le jeu : code, questions, traductions, dessins ou corrections de sources.

## Règles du dépôt

- **Rien d'inventé.** Toute information avec une source est vérifiée en ligne puis inscrite par
  `python3 outils/verifier_sources.py --inscrire CLE URL "contrôle"`. Une citation est exacte, courte, et donne son
  auteur et sa source. Une traduction se fait depuis le texte original ou une traduction tombée dans le domaine public.
- **Tests avant chaque commit.** Active le hook une fois par clone : `git config core.hooksPath .githooks`. Lance aussi
  `node outils/test_moteur.js` et `python3 outils/valider.py`.
- **Le contenu se modifie dans `outils/*.py`**, puis `python3 outils/contenu.py` régénère `data/`.

## Accord de contribution (CLA)

Le projet est libre, mais son auteur veut pouvoir le financer (Patreon, Kickstarter) et le publier sur les magasins
d'applications. Pour cela, il doit avoir le droit d'utiliser chaque contribution. Avant ta première pull request,
ajoute dans sa description la phrase « J'accepte l'accord de contribution de CONTRIBUTING.md ».

En l'acceptant :

1. Tu restes propriétaire de ta contribution.
2. Tu accordes à Victor Pajot une licence mondiale, gratuite, non exclusive, perpétuelle et irrévocable d'utiliser,
   reproduire, modifier, traduire, distribuer et sous-licencier ta contribution, sous toute licence, y compris
   commerciale ou fermée, par exemple pour une publication sur l'App Store.
3. Ta contribution est aussi publiée sous les licences du dépôt (voir [NOTICE.md](NOTICE.md)) : GPL 3.0 pour le code,
   CC BY-NC-SA 4.0 pour le contenu.
4. Tu garantis qu'elle est ton œuvre, ou que tu as le droit de la donner, et qu'elle ne reprend pas de texte, d'image
   ou de traduction protégés au-delà d'une courte citation sourcée.
5. Si tu contribues pour ton employeur, tu as son accord.

Ce texte est une première version, à faire relire par un juriste avant la première contribution extérieure.
