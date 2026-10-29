# Publier Arbre des savoirs sur Google Play : guide pas à pas

À faire depuis un ordinateur (la Play Console est pénible sur téléphone). Les textes à coller sont dans `FICHE.md`.

L'APK perso ne change pas : il continue de sortir à chaque push sur main, avec sa clé à lui. Play a sa propre clé et son propre workflow, lancé à la main.

## 1. Créer le compte développeur (environ 30 min, puis quelques jours d'attente)

1. Aller sur [play.google.com/console/signup](https://play.google.com/console/signup) avec le compte Google qui possédera l'app.
2. Choisir **Pour moi** (compte personnel).
3. Payer les frais d'inscription uniques de 25 $.
4. Vérifier ton identité (pièce d'identité) et ton numéro de téléphone. Google répond en général sous quelques jours.
5. Donner une adresse e-mail de contact : elle sera **publique** sur la fiche.
6. Déclarer le statut **non commerçant** (règlement européen DSA), puisque l'app est gratuite et sans revenus.

## 2. Clé d'envoi dans GitHub (5 min)

La clé est prête dans les fichiers du projet : `play-store/cle-envoi-secrete/A-COLLER-DANS-GITHUB.txt`. Elle n'est **pas** dans le dépôt, et ne doit jamais y aller.

1. Sur GitHub : dépôt arbre-des-savoirs > **Settings** > **Secrets and variables** > **Actions** > **New repository secret**.
2. Créer les 4 secrets du fichier : `PLAY_KEY_ALIAS`, `PLAY_KEYSTORE_PASSWORD`, `PLAY_KEY_PASSWORD`, `PLAY_KEYSTORE_BASE64` (nom exact, valeur copiée sans espace).
3. Garder une copie du fichier `upload.keystore` hors du projet (clé USB, gestionnaire de mots de passe). Perdue, elle se remplace depuis la Console, mais ça prend quelques jours.

## 3. Politique de confidentialité en ligne (2 min)

La page est dans le dépôt : `docs/confidentialite.md`.

1. Sur GitHub : **Settings** > **Pages** > Source **Deploy from a branch** > branche `main`, dossier `/docs` > **Save**.
2. Une minute après, la page est à : `https://victorpajot.github.io/arbre-des-savoirs/confidentialite.html`. C'est l'URL à donner à Google.

## 4. Fabriquer l'AAB (2 min)

1. Sur GitHub : onglet **Actions** > **Google Play** > **Run workflow** > branche `main` > **Run workflow**.
2. Environ 6 minutes plus tard, ouvrir le run terminé (coche verte). En bas, section **Artifacts** : télécharger **arbre-des-savoirs-aab** (un zip qui contient `app-release.aab`).

## 5. Créer l'app dans la Console (30 min)

1. **Créer une application** : nom, langue fr-FR, Jeu, Gratuit, cocher les déclarations.
2. Tableau de bord > **Configurer votre application** : remplir chaque rubrique avec `FICHE.md`, section « Contenu de l'application ».
3. **Fiche principale du Play Store** : descriptions et visuels de `FICHE.md`.
4. **Signature d'application** : laisser Google gérer la clé de signature (Play App Signing, proposé par défaut au premier envoi).

## 6. Test fermé : 12 testeurs pendant 14 jours (obligatoire)

Règle des comptes personnels récents : pas de publication publique avant un test fermé avec **au moins 12 testeurs** restés inscrits **14 jours d'affilée**. S'ils se désinscrivent et reviennent, le compteur repart à zéro.

1. **Tester** > **Test fermé** > **Créer un canal** (ou utiliser « Alpha »).
2. **Testeurs** : créer une liste d'adresses Gmail (collègues, famille, amis). En prévoir 15 à 20 pour avoir de la marge.
3. **Créer une release** : glisser `app-release.aab`, donner un nom (ex. « 1.0 test »), enregistrer, **Envoyer en examen**.
4. Une fois validée (souvent 1 à 3 jours), copier le **lien d'inscription** et l'envoyer aux testeurs. Ils doivent cliquer sur le lien, accepter, puis installer depuis Play.
5. Demander aux testeurs d'ouvrir l'app plusieurs fois pendant les 14 jours : Google regarde si l'app est vraiment utilisée.
6. Pour une nouvelle version pendant le test : relancer l'étape 4, puis **Créer une release** sur le même canal.

## 7. Passer en production

1. Après 14 jours, Tableau de bord > **Demander l'accès à la production**.
2. Répondre au questionnaire (comment tu as recruté les testeurs, ce qu'ils ont remonté, ce que tu as corrigé). Je peux te rédiger les réponses à partir de leurs retours.
3. Examen de Google : 7 jours ou moins. Ensuite : **Production** > **Créer une release** > même AAB > publication.

## Passer de l'APK perso à la version Play sur ton téléphone

Les deux versions ont le même nom de paquet mais des signatures différentes : Android refuse d'installer l'une par-dessus l'autre.

1. Dans le jeu : Personnage > Réglages > **Exporter** la partie.
2. Désinstaller l'app, installer la version Play.
3. **Importer** le fichier exporté.

Si tu préfères garder l'APK perso pour tes tests rapides, ne fais rien : il reste le circuit principal.
