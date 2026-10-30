# Écrire un pack pour Arbre des savoirs

Ce guide s'adresse à une IA (ou à une personne) qui veut ajouter un domaine de savoir au jeu, ou fabriquer une autre version du jeu qui enseigne d'autres compétences. Il suffit de le suivre dans l'ordre. Le pack **`packs/musique/`** est l'exemple complet à imiter ; **`packs/_modele/`** est un squelette à copier.

## 1. Ce qu'est un pack

Tout le contenu du jeu vit dans `packs/<id>/`. Le jeu, lui, lit `data/`, qui n'est que l'assemblage des packs :

```
packs/*/  ──  python3 outils/packs.py assembler  ──▶  data/*.json + data/packs.json  ──▶  le jeu
```

On n'édite **jamais** `data/` à la main : la prochaine assemblée l'écraserait, et le crochet de commit refuse un `data/` qui ne correspond pas aux packs.

Il existe trois sortes de packs (`"sorte"` dans `pack.json`) :

| Sorte | Rôle | Exemples |
| --- | --- | --- |
| `socle` | Le tronc commun : règles, plateau, Alyca et ses masques, avatar, interface. Un seul, toujours actif. | `socle` |
| `domaine` | Un ou plusieurs arbres de compétences, avec tout ce qui les accompagne. **C'est ce que ce guide apprend à écrire.** | `logique`, `cosmos`, `musique`… |
| `jeu` | Un jeu du plateau (contenu dans `donnees/`). Leur code est encore dans `web/moteur.js` : un nouveau pack de jeu demande donc aussi du code. | `atomes`, `ennemis` |

Le joueur peut éteindre chaque pack (sauf le socle) dans **Personnage › Réglages › Packs**. Un pack éteint disparaît du jeu ; ceux qui le requièrent s'éteignent avec lui ; la progression est conservée et revient quand on le rallume.

## 2. Démarrage rapide

```bash
cp -r packs/_modele packs/monpack           # le nom du dossier = l'id du pack
# 1. renommer : id dans pack.json, préfixe, ids des compétences, du savant, des succès…
# 2. écrire le contenu (sections 3 à 6)
python3 outils/packs.py verifier monpack    # liste précise de ce qui manque ou cloche
python3 outils/portrait.py monpack apercu.png   # dessine les savants depuis portraits.json
python3 outils/packs.py assembler           # régénère data/
python3 outils/valider.py                   # schéma et liens du contenu assemblé
python3 outils/verifier_sources.py          # liste les sources à vérifier en ligne (section 7)
node outils/test_moteur.js && python3 outils/test_packs.py && node outils/test_packs.js
```

Dans un nouveau clone, activer d'abord le crochet de commit : `git config core.hooksPath .githooks`. Il relance tout cela à chaque commit, et la compilation GitHub aussi.

Pour voir le pack dans le jeu : `node mobile/construire.js`, puis servir `mobile/www/` (par exemple `python3 -m http.server 8765 -d mobile/www`) et ouvrir la page. Le **mode test** (Personnage › Réglages) ouvre tous les arbres.

## 3. Le manifeste : `pack.json`

```json
{
 "format": 1,
 "id": "musique",
 "sorte": "domaine",
 "version": "1.0.0",
 "nom": {"fr": "Musique"},
 "description": {"fr": "Le son, la portée, les gammes, les accords et l'oreille…"},
 "auteurs": ["Victor Pajot", "Claude"],
 "licence": "CC BY-NC-SA 4.0",
 "langue_source": "fr",
 "requiert": ["socle", "mecanique"],
 "ordre": 110,
 "prefixe": "mus"
}
```

- **`id`** : minuscules, chiffres, tirets ; identique au nom du dossier.
- **`requiert`** : toujours `socle`, plus les packs dont on utilise les compétences (prérequis venus d'un autre pack). Pas de dépendance circulaire.
- **`prefixe`** : chaque compétence et chaque question commence par `<prefixe>.` (`mus.son`, `mus.son.q01`). Une liste est permise (`["chim", "sci.atomes"]`).
- **`ordre`** : place du pack dans l'assemblage et dans l'interface. Les domaines officiels vont de 10 à 110 : un nouveau domaine prend 120 ou plus.
- **Les autres ids** (dessins, livres, dates, succès, savants) sont communs à tous les packs : deux packs qui utilisent le même id entrent en collision à l'assemblage. Préfixer ceux du pack (`mus-croche`, `carto-boussole`) ; un savant garde le nom de la personne (`bach`).
- **Textes** : partout, un texte est un objet `{"fr": "…"}` dans la langue source du pack (`langue_source`). Les traductions ne vont pas à côté mais dans `langues/` (section 8).

## 4. Les fichiers d'un pack domaine

Un fichier par type de contenu. Chacun est une liste (ou un dictionnaire) qui s'ajoute à celle du jeu.

| Fichier | Contenu | Va dans |
| --- | --- | --- |
| `arbres.json` | Les arbres : id, nom, branche, couleur, `couleurs` `{clair, sombre}` (lisibles sur fond clair et sombre), description. `"fondamental": true` = ouvert dès le départ. | `regles.json › stats` |
| `competences.json` | 8 compétences par arbre, rangs 1 à 8 : nom, description, prérequis, fiche de révision (essentiel, piège, schéma SVG, source), symbole, emblème. | `skills.json` |
| `questions.json` | Au moins 10 questions par compétence. | `questions.json` |
| `livres.json` | Un livre par compétence au moins, pour la bibliothèque. | `bibliotheque.json` |
| `frise.json` | Une date par compétence au moins, pour la frise. | `frise.json` |
| `succes.json` | Le pionnier qui ouvre l'arbre, un succès par compétence, et d'autres (branche, sans-faute…). | `succes.json` |
| `piques.json` | `{id du succès: texte}` : la pique d'Alyca quand elle paie les crédits du succès. | `ia.json` |
| `savants.json` | Les savants jouables du domaine (un par compétence idéalement), avec leur portrait. | `avatar.json` |
| `portraits.json` | La recette de chaque portrait, lue par `outils/portrait.py` (pas assemblée). | — |
| `repliques.json` | Les répliques d'Alyca propres à l'arbre. | `commentaires.json` |
| `cases.json` | `{numéro de case: [compétences]}` : les cases du plateau qui évoquent le domaine. | `plateau.json` |
| `dessins.json` | `{id: 32 lignes de 32 caractères}` : pixel art pour les emblèmes et succès. | `succes.json › dessins` |
| `objets.json`, `masques.json`, `accessoires.json`, `tenues.json`, `apartes.json`, `figures.json`, `boutique.json` | Facultatifs : objets du cabinet, masques d'Alyca, accessoires, farces, apartés, figures interactives, articles de boutique. Copier la forme d'un pack existant (`grep -l` dans `packs/`). | voir `EMPLACEMENTS` dans `outils/packs.py` |

`verifications.json` (le registre des sources contrôlées) est écrit par l'outil, jamais à la main. `ordre.json` et `donnees/` sont réservés au socle et aux packs de jeu.

**Où trouver les images existantes** (pour un emblème ou une illustration) : `data/succes.json › dessins` (dessins de tous les packs), `data/objets.json › objets` (objets du cabinet), `data/plateau.json › icones` (icônes du plateau). `verifier` refuse un id introuvable.

### Compétences

```json
{"id": "mus.son", "stat": "musique", "rang": 1, "prerequis": [],
 "nom": {"fr": "Le son, une onde"}, "description": {"fr": "Fréquence, amplitude, vitesse du son et hertz."},
 "fiche": {"essentiel": [{"fr": "…"}, {"fr": "…"}, {"fr": "…"}, {"fr": "…"}],
           "piege": {"fr": "L'erreur la plus courante."},
           "schema": "<svg …>…</svg>",
           "source": "Wikipédia (en), « Speed of sound »"},
 "symbole": "Hz", "embleme": "diapason"}
```

- **Rangs** : 1 à 4 forment le premier losange (1 en haut, 2 et 3 au milieu, 4 en bas), 5 à 8 le second, accroché sous le 4. Prérequis : 2 et 3 requièrent 1 ; 4 requiert 2 et 3 ; 5 requiert 4 ; 6 et 7 requièrent 5 ; 8 requiert 6 et 7. Une compétence peut aussi requérir celle d'un autre pack, s'il est dans `requiert`.
- **Schéma** : un SVG en ligne, `viewBox` d'environ 400 de large, `role="img"` et un `aria-label`. Pas de couleurs en dur : des classes que le jeu colore selon le thème clair ou sombre : `t` (texte), `tm` (texte discret), `l` (trait), `lm` (trait discret), `f` (forme pleine), `f2` (forme discrète), `a` (remplissage d'accent), `al` (trait d'accent), `ok`, `ko`, `fond`.
- **Emblème** : l'id d'un dessin (`dessins.json` d'un pack), d'un objet du cabinet ou d'une icône du plateau (`plateau.json › icones`). C'est le badge de la compétence.

### Questions

Trois types. Pour un QCM, **la bonne réponse est toujours en premier** (`"reponse": 0`) : le jeu mélange les choix.

```json
{"id": "mus.son.q01", "competence": "mus.son", "type": "qcm",
 "enonce": {"fr": "…"}, "choix": [{"fr": "bonne"}, {"fr": "leurre"}, {"fr": "leurre"}, {"fr": "leurre"}],
 "reponse": 0, "explication": {"fr": "…"}}
{"id": "…q02", "competence": "mus.son", "type": "vrai_faux", "enonce": {"fr": "…"}, "reponse": false, "explication": {"fr": "…"}}
{"id": "…q03", "competence": "mus.son", "type": "numerique", "enonce": {"fr": "…"}, "reponse": 0.78, "tolerance": 0.01,
 "unite": "m", "explication": {"fr": "λ = v / f. Ici λ = 343 / 440 ≈ 0,78 m. Newton fut le premier…"},
 "source": "Isaac Newton, Philosophiae naturalis principia mathematica, Londres, 1687"}
```

- Leurres plausibles, jamais absurdes ; un énoncé ne se répète pas d'une question à l'autre, ni d'un pack à l'autre.
- **Questions de calcul** (règle de Victor) : l'explication pose la formule en lettres, fait le calcul complet, et dit qui a trouvé la formule ; le champ `source` donne la référence de cette attribution. Quand la formule n'a pas de découvreur (une définition comme f = 1/T, une règle de trois, une échelle), l'explication le dit (« c'est la définition de la fréquence ») et la question n'a pas de `source`. Une simple question de comptage (combien de noires dans une ronde) n'est pas une question de calcul.
- L'explication apprend quelque chose de plus que la réponse : un fait, une date, une personne.

### Livres, dates, succès

Voir `packs/musique/livres.json`, `frise.json` et `succes.json`. Points à respecter :

- **Livre** : résumé de 80 à 170 mots, `importance`, `anecdote`, `reaction` (le mot d'Alyca), `competence` rattachée, `condition` (en général `competence_maitrisee`), `embleme` et `couleur` de couverture.
- **Date** : `epoque` parmi `antiquite` (jusqu'à 475), `moyen-age` (476-1449), `renaissance` (1450-1599), `classique` (1600-1799), `xixe` (1800-1899), `xxe` (depuis 1900, XXIe siècle compris) ; `phrase` choc, `detail` en deux phrases, `condition` `competence_maitrisee`.
- **Succès** : `nom` moqueur, `description` qui dit comment l'obtenir puis ajoute une pique, `cache` (vrai s'il est une surprise), `recompense` `{"type": "anecdote", "texte", "source"}`, `illustration` (`objet`, `icone`, `dessin`, `savant` ou `ennemi` + id), `theme` (l'id de l'arbre).
- **Pionnier** : un succès avec `"ouvre": "<arbre>"` ouvre l'arbre. Condition habituelle `{"type": "competences_maitrisees", "n": N}`, où N compte les compétences maîtrisées dans n'importe quel arbre : plus N est grand, plus l'arbre arrive tard. Les arbres officiels utilisent N = 2 à 9 (Musique : 8). Plusieurs arbres peuvent avoir le même N. Son illustration est en général le savant pionnier.
- **Champ `source`** : obligatoire pour la fiche d'une compétence, chaque livre, chaque date, chaque récompense de succès, chaque savant, et chaque question qui attribue une formule ou une découverte. Les autres questions s'en passent : leur explication est vérifiée avec la fiche.
- Les conditions possibles sont listées dans `outils/schema.json` (`$defs.condition`).

### Savants

Un savant jouable devient le personnage du joueur quand il le débloque. Notice de trois à quatre phrases vérifiées, `annees` (« 1685 / 1750 », « vers 992 / vers 1050 »), `condition`, `source`, `theme`. Personne de vivant.

Le portrait fait 40 × 48 (calques `base` et `cheveux`, plus `couleurs`). On ne le dessine pas à la main : on écrit sa recette dans `portraits.json`, puis on **lance obligatoirement** `outils/portrait.py`, qui remplit ces trois champs dans `savants.json` (`verifier` refuse un savant sans portrait). Si vous produisez vos fichiers avec un script, relancez `portrait.py` après lui, sinon il effacera les portraits.

```json
{"id": "bach", "peau": "claire", "tenue": "manteau", "couleurs": ["#3B3B3B", "#1E1E24", "#EEF0F4"],
 "coiffure": ["perruque", "gris", 4], "barbe": null, "objet": "livre"}
```

`python3 outils/portrait.py monpack apercu.png` remplit les savants et dessine une planche à regarder. Les styles possibles sont listés en tête de `outils/portrait.py`.

### Dessins

32 × 32 caractères, `.` pour le transparent, les autres caractères pris dans la palette de `outils/dessin.py` (`FAMILLES` : gris, or, bois, rouge, vert, bleu, peau, parchemin…), lumière venant du haut à gauche, contour sombre `k`. `Toile.peindre(pixels, famille, modele)` prend le modelé `plat`, `biseau`, `sphere`, `cyl_v` ou `cyl_h` ; les formes sont `rect`, `ellipse`, `disque`, `anneau`, `poly`, `trait`, `courbe`, `arc`. Le plus simple est un petit script :

```python
import sys; sys.path.insert(0, "outils")
from dessin import Toile, trait, ellipse, poly, apercu
t = Toile(32, 32)
t.peindre(trait(19, 5, 19, 22, 2), "nuit", "plat", base=1)
t.peindre(ellipse(14.5, 23.5, 5, 3.4), "nuit", "sphere")
t.contour("k")
dessin = t.lignes()            # à mettre dans dessins.json
apercu({"croche": dessin}, "apercu.png", echelle=8)   # puis regarder l'image
```

### Répliques d'Alyca et cases du plateau

Chaque arbre a au moins **3** répliques `theme_jouer@<arbre>` (au lancement d'une épreuve ; `{comp}` est remplacé par le nom de la compétence), **4** `theme_reussi@<arbre>` et **4** `theme_rate@<arbre>`. `"reference": true` quand la réplique cite un fait réel.

`cases.json` relie le domaine au plateau : une case dont l'histoire évoque le domaine propose ses compétences comme épreuve. Les 63 cases et leur histoire sont dans `data/plateau.json › cases` (champ `n`, titre, histoire). Il en faut au moins une par arbre. Une case peut évoquer plusieurs packs : les listes s'additionnent.

## 5. Liste de contrôle d'un arbre

`python3 outils/packs.py verifier monpack` contrôle tout cela et dit, pour chaque manque, quoi ajouter et dans quel fichier :

- 8 compétences, une par rang de 1 à 8 ;
- au moins 10 questions par compétence ;
- pour chaque compétence : un livre, une date de la frise, un succès qui se gagne en la maîtrisant ;
- un succès de pionnier qui ouvre l'arbre (sauf arbre `fondamental`) ;
- au moins un savant jouable (`theme` = l'arbre) ;
- les répliques 3 / 4 / 4 ;
- au moins une case du plateau qui évoque l'arbre.

Il vérifie aussi les liens (préfixes, prérequis, compétences citées, thèmes, conditions ; un pack ne vise que lui-même et ce qu'il requiert), que chaque emblème et chaque illustration existe, que les dessins font 32 × 32 dans la palette, que les savants ont leur portrait 40 × 48, et que les résumés de livres font 80 à 170 mots.

Il ne juge pas le fond : l'exactitude des faits (section 7), la qualité des leurres, la voix d'Alyca. Relisez-vous, et regardez le pack dans le jeu.

## 6. La voix du jeu

- **Alyca**, l'IA narratrice, est moqueuse et drôle, façon *Dungeon Crawler Carl* : elle **vouvoie** le joueur, fait des phrases courtes, pique sans être méchante, et s'appuie sur un fait réel du domaine. Elle ne dit jamais qu'elle aime ce qui brille.
- Phrases complètes, français courant, pas de jargon non expliqué. Le joueur peut être n'importe qui.
- Les succès sont des clins d'œil : un échec peut en valoir un (le succès « Tour de Pise » pour un quiz raté).

## 7. Rien d'inventé

Règle absolue du projet : **chaque fait doit être vérifié en ligne avant d'entrer dans le jeu.**

1. Écrire le contenu avec ses champs `source` (fiches, questions de calcul, livres, dates, succès, savants…).
2. `python3 outils/verifier_sources.py` liste ce qui n'est pas encore vérifié.
3. Pour chaque élément : ouvrir une source en ligne fiable, contrôler chaque date, nom, chiffre et citation, **corriger le texte** si la source dit autre chose (ou retirer le fait), puis inscrire la vérification :
   ```bash
   python3 outils/verifier_sources.py --inscrire "succes:pionnier-mersenne:recompense" https://… "ce qui a été contrôlé"
   ```
   L'inscription va dans le `verifications.json` du pack. Elle porte une empreinte du texte : modifier le texte plus tard le fait redevenir « non vérifié ».
4. Le champ `source` dit d'où vient l'information (l'ouvrage, l'article ou la page vraiment consultée). Une anecdote douteuse se dit comme telle (« selon la seule lettre de son père… ») ou disparaît.

Le crochet de commit et la compilation GitHub refusent toute source non vérifiée.

## 8. Traduire un pack

Le jeu se joue en français ou en anglais (Personnage › Réglages). Chaque pack porte ses traductions, rangées **par texte source** : `langues/<xx>/<fichier>.json` vaut `{"texte source": "traduction"}` pour les textes de `<fichier>.json` (`langues/en/questions.json` pour `questions.json`, `langues/en/donnees-avatar.json` pour `donnees/avatar.json`). Se traduisent : les objets `{"fr": …}`, les étiquettes `<text>` et `aria-label` des schémas, et les champs `langue`, `traducteur`, `reference`, `titre`. Jamais les sources, URL et ids.

```bash
python3 outils/langues.py etat en                          # couverture de chaque pack
python3 outils/langues.py a-traduire en mon-pack questions.json  # ce qui manque, prêt à remplir
python3 outils/langues.py inscrire en mon-pack fait.json   # range des traductions faites
python3 outils/packs.py assembler                          # data/langues/en.json, ce que le jeu charge
```

- Un texte source modifié perd sa traduction : il s'affiche en français et `etat` le signale. Retraduire.
- **Balises et variables** (`<b>`, `{comp}`, `{n}`) : toutes gardées, l'ordre peut changer. Les tests le vérifient.
- **Rien d'inventé** vaut aussi en traduction : une citation dont l'original est connu en anglais reprend l'original (Newton, Darwin, Feynman) ; sinon, traduire au plus près. Un extrait dont l'original est en anglais garde le texte original en guise de traduction : le jeu ne l'affiche alors qu'une fois.
- **Schémas** : une étiquette peut se traduire différemment d'un schéma à l'autre (« noire » : la note en musique, la matière en astronomie) ; l'assemblage s'en charge. Une étiquette en deux lignes (« situation » / « initiale ») peut échanger ses mots pour suivre l'ordre anglais.
- **Anglais** : américain, point décimal (3.5), virgule des milliers (1,000) ; Alyca est « she » ; notes C D E F G A B ; le « tu » des descriptions devient « you ». L'interface se traduit dans `web/langues/en.json` (`python3 outils/langues.py interface en`).

## 9. Ce qu'un pack ne peut pas (encore) faire

- Ajouter des **cases au plateau** : il a 63 cases, dans le socle. Un pack s'y rattache par `cases.json`.
- Créer un **nouvel effet** en boutique : un article (`boutique.json`) reprend un rayon et un effet existants.
- Apporter du **code** : un pack de jeu (`sorte: jeu`) fournit des données, mais son jeu doit être programmé dans `web/moteur.js` et `web/index.html`.

## 9 bis. Distribuer un pack hors du dépôt (pack additionnel)

Un pack de **domaine** peut aussi se charger directement dans le jeu, sans passer par le dépôt : écran titre › Nouvelle partie › « Charger un pack », ou Personnage › Réglages › Packs.

1. `python3 outils/packs.py verifier <id>` puis `python3 outils/verifier_sources.py` : tout doit passer, comme pour le dépôt.
2. `python3 outils/packs.py paquet <id> [fichier]` écrit `<id>.pack.json` : le manifeste, les fragments posés à leur place (lots compris), les traductions et le compte des sources vérifiées.
3. Le joueur charge ce fichier (ou son adresse https). Le jeu refuse un pack de jeu (il porte du code), un identifiant qui existe déjà, un pack demandé absent ou un emplacement hors de ceux d'un domaine (`EMPLACEMENTS` d'`outils/packs.py`).

Le jeu affiche toujours l'avertissement : l'équipe du jeu ne garantit ni le contenu ni la sécurité des packs additionnels. Ils sont marqués « non officiel » et se retirent depuis les réglages ; la progression qu'ils ont donnée reste dans la partie.

## 10. Licence

En proposant un pack au dépôt, on accepte `CONTRIBUTING.md` (accord CLA). Le contenu des packs est sous CC BY-NC-SA 4.0 (`NOTICE.md`). Un pack qui reprend un texte d'un tiers (citation, extrait) le cite et n'en prend que le nécessaire.
