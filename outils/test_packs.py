"""Tests de outils/packs.py (python3 outils/test_packs.py) : l'assemblage reproduit data/, et verifier refuse
chaque faute courante d'un pack avec un message qui dit quoi corriger."""
import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import packs as P

# 1. data/ est exactement l'assemblage des packs.
donnees, index = P.assembler(ecrire_data=False)
for f in P.FICHIERS_DATA:
    assert P.lire(P.DATA / f) == P.ordonner(f, donnees[f]), f"data/{f} n'est pas l'assemblage des packs : python3 outils/packs.py assembler"
assert P.verifier() == [], "les packs du dépôt doivent être valides"

# 2. Un petit pack d'essai, puis une faute à la fois.
MODELE = {
    "pack.json": {"format": 1, "id": "essai", "sorte": "domaine", "version": "1.0.0", "nom": {"fr": "Essai"},
                  "description": {"fr": "Pack de test."}, "auteurs": ["Test"], "licence": "CC BY-NC-SA 4.0",
                  "langue_source": "fr", "requiert": ["socle"], "prefixe": "essai"},
    "arbres.json": [{"id": "essai", "nom": {"fr": "Essai"}, "branche": {"fr": "Essai"}, "couleur": "#123456",
                     "couleurs": {"clair": "#123456", "sombre": "#654321"}, "description": {"fr": "Essai."}}],
    "competences.json": [{"id": "essai.un", "stat": "essai", "rang": 1, "prerequis": []}],
    "questions.json": [{"id": "essai.un.q01", "competence": "essai.un"}],
}


def avec(faute, completude=False):
    """Les packs du dépôt plus le pack d'essai abîmé par `faute(fichiers)` ; renvoie les erreurs de verifier
    (sans celles de complétude, sauf demande : le pack d'essai est volontairement minuscule)."""
    tmp = Path(tempfile.mkdtemp())
    try:
        shutil.copytree(P.PACKS / "socle", tmp / "socle")
        shutil.copytree(P.PACKS / "mecanique", tmp / "mecanique")
        fichiers = copy.deepcopy(MODELE)
        faute(fichiers)
        for nom, contenu in fichiers.items():
            P.ecrire(tmp / "essai" / nom, contenu)
        return [e for e in P.verifier(P.tous(tmp), cibles={"essai"})
                if not e.startswith("[assemblage]") and (completude or "complétude" not in e)]
    finally:
        shutil.rmtree(tmp)


def attendu(faute, morceau):
    erreurs = avec(faute)
    assert any(morceau in e for e in erreurs), f"attendu « {morceau} », reçu : {erreurs}"


assert avec(lambda f: None) == [], avec(lambda f: None)
attendu(lambda f: f["pack.json"].pop("licence"), "« licence » manquant")
attendu(lambda f: f["pack.json"].update(id="autre"), "doit être le nom du dossier")
attendu(lambda f: f["pack.json"].update(sorte="theme"), "« sorte » vaut")
attendu(lambda f: f["pack.json"].update(version="1"), "s'écrit 1.0.0")
attendu(lambda f: f["pack.json"].update(requiert=["socle", "inconnu"]), "absent de packs/")
attendu(lambda f: f["pack.json"].update(requiert=[]), "tout pack requiert « socle »")
attendu(lambda f: f["competences.json"][0].update(stat="ailleurs"), "arbre « ailleurs » inconnu")
attendu(lambda f: f["competences.json"][0].update(prerequis=["phys.forces"]), "prérequis « phys.forces » introuvable")
attendu(lambda f: f["questions.json"][0].update(competence="essai.deux"), "compétence « essai.deux » introuvable")
attendu(lambda f: f["questions.json"][0].update(id="autre.q01"), "préfixe du pack")
attendu(lambda f: f.update({"inconnu.json": []}), "fichier inconnu inconnu.json")
attendu(lambda f: f.update({"objets.json": [{"id": "x", "theme": "nulle-part"}]}), "thème « nulle-part » inconnu")
# Le prérequis d'un pack requis est accepté.
def requis(f):
    f["pack.json"]["requiert"] = ["socle", "mecanique"]
    f["competences.json"][0]["prerequis"] = ["phys.forces"]
assert avec(requis) == [], avec(requis)
# Un arbre incomplet est signalé, avec ce qui manque.
incomplet = avec(lambda f: None, completude=True)
for morceau in ("une par rang de 1 à 8", "au moins 10", "aucun livre", "aucune date", "aucun succès", "pionnier", "savant jouable", "theme_rate@essai", "case du plateau"):
    assert any(morceau in e for e in incomplet), f"complétude : attendu « {morceau} », reçu : {incomplet}"

# 3. L'assemblage refuse deux éléments de même identifiant.
tmp = Path(tempfile.mkdtemp())
try:
    shutil.copytree(P.PACKS / "socle", tmp / "socle")
    shutil.copytree(P.PACKS / "mecanique", tmp / "mecanique")
    shutil.copytree(P.PACKS / "mecanique", tmp / "copie")
    m = P.lire(tmp / "copie" / "pack.json"); m["id"] = "copie"; P.ecrire(tmp / "copie" / "pack.json", m)
    try:
        P.assembler(P.tous(tmp), ecrire_data=False)
        raise AssertionError("deux packs identiques auraient dû entrer en collision")
    except P.ErreurPack as e:
        assert "en double" in str(e)
finally:
    shutil.rmtree(tmp)
print(f"OK : assemblage identique à data/, {len(index['packs'])} packs valides, 14 fautes de pack refusées")
