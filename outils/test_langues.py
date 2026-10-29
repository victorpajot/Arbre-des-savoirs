"""Tests des langues (python3 outils/test_langues.py) : extraction, repli sur la langue source, traductions périmées,
balises et variables conservées, data/langues/ à jour, et lecture des traductions par le moteur."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import langues as L

# 1. Extraction : objets texte, étiquettes des schémas, champs simples ; jamais les sources ni les identifiants.
contenu = [{"id": "x.q01", "enonce": {"fr": "Combien font deux et deux ?"}, "choix": [{"fr": "Quatre"}, {"fr": "4"}],
            "source": "Euclide, Éléments", "illustration": '<svg role="img" aria-label="Deux pommes"><text>pomme</text><text>2</text></svg>',
            "extrait": {"langue": "latin, trad. maison", "texte": "Duo et duo"}}]
t = L.textes(contenu)
assert set(t) == {"Combien font deux et deux ?", "Quatre", "Deux pommes", "pomme", "latin, trad. maison"}, t
assert L.traduire_svg(contenu[0]["illustration"], {"pomme": "apple", "Deux pommes": "Two apples"}) == \
    '<svg role="img" aria-label="Two apples"><text>apple</text><text>2</text></svg>'

# 2. Un pack d'essai : couverture, périmées, inscription, assemblage.
tmp = Path(tempfile.mkdtemp())
try:
    p = tmp / "essai"
    (p / "langues" / "en").mkdir(parents=True)
    L.ecrire(p / "pack.json", {"id": "essai", "langue_source": "fr", "nom": {"fr": "Essai de pack"}})
    L.ecrire(p / "questions.json", contenu)
    L.ecrire(p / "langues" / "en" / "questions.json", {"Quatre": "Four", "Un texte qui n'existe plus": "Gone"})
    total, faits, manq, orph = L.etat_pack(p, "en")
    assert (total, faits) == (6, 1), (total, faits)
    assert orph == {"questions.json": ["Un texte qui n'existe plus"]}, "une traduction sans texte source est périmée"
    assert "Essai de pack" in manq["pack.json"], "le nom du pack se traduit aussi"
    d = L.dictionnaire("en", [p])
    assert d == {"Quatre": "Four"}, "une traduction périmée n'est jamais utilisée"
finally:
    shutil.rmtree(tmp)

# 3. Les traductions du dépôt : balises HTML et variables {x} identiques à la source, rien de vide qui traîne.
for langue in [f.stem for f in (L.WEB / "langues").glob("*.json")]:
    for s, v in L.catalogue(langue)["textes"].items():
        if not v:
            continue
        assert L.balises(s) == L.balises(v), f"web/langues/{langue}.json : balises ou variables différentes pour « {s[:60]} »"
for d in L.packs():
    for langue in (x.name for x in (d / "langues").iterdir()) if (d / "langues").exists() else []:
        for f, tr in L.traductions(d, langue).items():
            for s, v in tr.items():
                assert isinstance(v, str), f"{d.name}/langues/{langue}/{f} : « {s[:50]} » doit valoir un texte"
                if "<" in s or "{" in s:
                    assert L.balises(s) == L.balises(v), f"{d.name}/langues/{langue}/{f} : balises ou variables différentes pour « {s[:60]} »"

# 4. data/langues/ est exactement l'assemblage des traductions des packs et du catalogue.
for langue, attendu in L.assembler(ecrire_data=False).items():
    assert L.lire(L.DATA / "langues" / (langue + ".json")) == attendu, f"data/langues/{langue}.json n'est pas à jour : python3 outils/packs.py assembler"

# 5. Le moteur : repli sur la langue source, dictionnaire, catalogue, variables.
js = r"""
const M = require("./web/moteur.js"), assert = require("assert");
assert.strictEqual(M.TX({ fr: "Quatre" }), "Quatre");
assert.strictEqual(M.__("Bonjour {nom}", { nom: "Ada" }), "Bonjour Ada");
M.choisirLangue("en", { textes: { "Quatre": "Four" }, interface: { "Bonjour {nom}": "Hello {nom}", "Posé par l'IA.": "Set by the AI." } });
assert.strictEqual(M.TX({ fr: "Quatre" }), "Four");
assert.strictEqual(M.TX({ fr: "Cinq" }), "Cinq", "sans traduction : la langue source");
assert.strictEqual(M.TX({ fr: "Quatre", en: "4 (en)" }), "4 (en)", "une traduction posée dans l'objet passe d'abord");
assert.strictEqual(M.TX({ fr: "Posé par l'IA." }), "Set by the AI.", "un texte fabriqué par le code se lit dans le catalogue");
assert.strictEqual(M.TX({ en: "Only English" }), "Only English", "un pack d'une autre langue source");
assert.strictEqual(M.__("Bonjour {nom}", { nom: "Ada" }), "Hello Ada");
assert.strictEqual(M.__("Inconnu"), "Inconnu");
M.choisirLangue("fr");
assert.strictEqual(M.TX({ fr: "Quatre" }), "Quatre");
"""
r = subprocess.run(["node", "-e", js], cwd=L.RACINE, capture_output=True, text=True)
assert r.returncode == 0, r.stderr

print("Langues : OK")
