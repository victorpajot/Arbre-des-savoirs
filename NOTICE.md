# Arbre des savoirs : droits et licences

© 2026 Victor Pajot. Jeu conçu et dirigé par Victor Pajot, réalisé avec l'aide de Claude (Anthropic), une IA qui a écrit
une grande partie du code et des textes sous sa direction.

Le projet a deux licences : une pour le code, une pour le contenu.

## Le code : GPL 3.0

Licence : [GNU General Public License, version 3](LICENSE).

Couvre la logique du jeu : `web/moteur.js`, le script et les styles de `web/index.html`, les fonctions des scripts
`outils/*.py`, `mobile/` et `.github/`. Tu peux le copier, le modifier et le redistribuer, y compris contre paiement, à
condition de publier ton code sous la même licence.

## Le contenu : CC BY-NC-SA 4.0

Licence : [Creative Commons Attribution, Pas d'utilisation commerciale, Partage dans les mêmes conditions 4.0
International](licences/CC-BY-NC-SA-4.0.txt) ([résumé en français](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fr)).

Couvre tout ce qui se lit ou se voit dans le jeu : les fichiers `data/*.json`, et les textes, questions, répliques,
fiches et dessins en pixel art écrits dans les scripts `outils/*.py`. Tu peux les copier, les traduire et les adapter,
par exemple pour une autre version du jeu, à trois conditions :

- citer « Arbre des savoirs, Victor Pajot » avec un lien vers le dépôt, et dire ce que tu as changé ;
- ne pas en faire un usage commercial sans l'accord écrit de Victor Pajot ;
- publier ta version sous la même licence.

Victor Pajot, auteur, reste libre d'utiliser son contenu comme il veut, y compris commercialement.

## Ce qui n'est pas couvert

- **Les citations et extraits d'œuvres** (champ `extrait`, citations de savants dans les succès, les ennemis et la
  bibliothèque) restent la propriété de leurs auteurs ou sont dans le domaine public. Ils sont reproduits au titre du
  droit de courte citation, avec l'auteur et la source. La licence du contenu ne s'y applique pas.
- **Les faits** (dates, masses atomiques, découvertes) n'appartiennent à personne. Les sources consultées sont listées
  dans `outils/verifications.json`.
- **Le nom « Arbre des savoirs », le nom « Alyca » et l'icône de l'appli** ne sont pas sous licence libre. Une version
  dérivée doit porter un autre nom et une autre icône.

## Composants de tiers

| Composant | Auteur | Licence |
| --- | --- | --- |
| Police Atkinson Hyperlegible | Braille Institute of America | [SIL OFL 1.1](licences/OFL-atkinsonhyperlegible.txt) |
| Police Bricolage Grotesque | The Bricolage Grotesque Project Authors | [SIL OFL 1.1](licences/OFL-bricolagegrotesque.txt) |
| Police JetBrains Mono | The JetBrains Mono Project Authors | [SIL OFL 1.1](licences/OFL-jetbrainsmono.txt) |
| Capacitor (appli Android) | Ionic | MIT, avis inclus dans `mobile/node_modules/@capacitor/*/LICENSE` à la compilation |

Les polices sont embarquées dans `web/index.html`, réduites aux caractères latins (pyftsubset, fontTools) : le jeu
n'appelle aucun serveur de polices.

## Contribuer

Les contributions sont les bienvenues, sous les conditions de [CONTRIBUTING.md](CONTRIBUTING.md).
