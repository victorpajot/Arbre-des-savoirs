# Les images de l'île

Le jeu dessine l'île lui-même. Pour changer une image, dépose un fichier ici (ou dans le dossier `images/` de
n'importe quel pack), puis lance `python3 outils/packs.py assembler`. Aucun code à toucher : l'image prend la place
du dessin, et le jeu continue de poser par-dessus ce qui change (états, habitants, étiquettes, zones à toucher).
Retire le fichier, le dessin d'origine revient.

| Fichier | Ce qu'il remplace | Format conseillé |
|---|---|---|
| `carte.png` | Le fond de la carte : mer, côte, volcan, bois, lac, marais, chemins. | 1080 × 1830 (rapport 360 × 610) |
| `hameau-<quartier>.png` | Un quartier sur la carte (maisons et installations dessinées). | carré, 240 × 240, fond transparent |
| `quartier-<quartier>.png` | Le fond d'un quartier vu de près. | 1080 de large, hauteur libre (recadré) |
| `installation-<compétence>.png` | Une installation, sur la carte et dans son quartier. | carré, 256 × 256, fond transparent |
| `econome.png` | Le visage d'Ananké, l'IA économe (objectif du jour, présentation de l'île). | 200 × 240, fond transparent |

- `<quartier>` : `port`, `ville`, `artisans`, `industrie`, `champs`, `agora`, `campus`, `centrale`
  (liste et positions sur la carte dans `../donnees/ile.json`, champ `position` : [x, y] de 0 à 1).
- `<compétence>` : l'identifiant de la compétence, par exemple `installation-phys.machines.png`.
- Formats acceptés : PNG, WebP, JPEG, SVG. Les images sont embarquées dans `data/ile.json` : garde-les légères
  (quelques centaines de ko au plus pour la carte).
- Une installation en panne, en veille ou à l'abandon est ternie par le jeu : une seule image suffit par installation.
