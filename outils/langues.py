"""Les langues : chaque pack porte ses traductions, l'interface a son catalogue.

    python3 outils/langues.py etat [xx]                      couverture par pack et par langue (en par défaut)
    python3 outils/langues.py a-traduire xx pack [fichier] [--max N]
                                                             les textes encore à traduire, au format d'un fichier de langue
    python3 outils/langues.py inscrire xx pack fichier.json  ajoute des traductions faites (dictionnaire texte → traduction)
    python3 outils/langues.py nettoyer [xx]                  retire les traductions dont le texte source a disparu
    python3 outils/langues.py interface [xx]                 met à jour le catalogue web/langues/xx.json (textes à traduire vides)

Une traduction se range par le texte source lui-même, pas par un chemin : packs/<id>/langues/<xx>/<fichier>.json vaut
{"texte source": "traduction"} pour les textes de packs/<id>/<fichier>. Quand le texte source change, sa traduction ne
correspond plus à rien : le texte s'affiche dans la langue source et « etat » le signale, sans rien bloquer.

Ce qui se traduit dans un pack : chaque objet texte {"fr": …} (la langue source du pack), les étiquettes <text> et
aria-label des schémas SVG, et quelques champs simples affichés tels quels (CHAMPS_SIMPLES). Les sources, les URL et les
identifiants ne se traduisent pas.

L'assemblage (outils/packs.py assembler) réunit les traductions de tous les packs dans data/langues/<xx>.json, que le jeu
charge quand le joueur choisit cette langue (Personnage › Réglages). L'interface (web/index.html, web/moteur.js) se
traduit de même par texte : web/langues/<xx>.json, rempli à partir des chaînes écrites __("…") (et des objets
{fr: "…"} que le code fabrique), réuni lui aussi dans data/langues/<xx>.json sous « interface ».
"""
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PACKS = RACINE / "packs"
DATA = RACINE / "data"
WEB = RACINE / "web"

LANGUES = {"fr": "Français", "en": "English"}
# Champs affichés tels quels, sans objet {"fr"} : la langue et la référence d'un extrait, le titre d'une figure.
CHAMPS_SIMPLES = {"langue", "traducteur", "reference", "titre"}
# Les clés qui ne contiennent jamais de texte à traduire.
CLES_IGNOREES = {"source", "url", "verification", "id", "base", "cheveux", "couleurs", "palette", "pixels", "dessin", "dessins"}

RE_TEXTE_SVG = re.compile(r"(<text\b[^>]*>)([^<]*)(</text>)")
RE_TSPAN_SVG = re.compile(r"(<tspan\b[^>]*>)([^<]*)(</tspan>)")
RE_ARIA = re.compile(r'(aria-label=")([^"]*)(")')
RE_MOT = re.compile(r"[A-Za-zÀ-ÿ]{2,}")


def lire(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def ecrire(p, d):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def a_traduire(s):
    """Un texte vaut d'être traduit s'il contient au moins un mot (pas un nombre, une formule seule, un symbole)."""
    return isinstance(s, str) and bool(RE_MOT.search(s.replace("&amp;", "&")))


def etiquettes_svg(svg):
    """Les textes visibles et lus d'un schéma : contenu des <text>/<tspan> et des aria-label."""
    out = []
    for r in (RE_TEXTE_SVG, RE_TSPAN_SVG, RE_ARIA):
        out += [m.group(2) for m in r.finditer(svg) if a_traduire(m.group(2))]
    return out


RE_BALISE = re.compile(r"<[^<>]*>|\{\w+\}")


def balises(s):
    """Les balises HTML et variables {x} d'un texte : une traduction les garde toutes (l'ordre peut changer)."""
    return sorted(RE_BALISE.findall(s))


def traduire_svg(svg, dico):
    """Le schéma avec ses étiquettes traduites ; une étiquette sans traduction reste telle quelle."""
    def rempl(m):
        return m.group(1) + dico.get(m.group(2), m.group(2)) + m.group(3)
    for r in (RE_TEXTE_SVG, RE_TSPAN_SVG, RE_ARIA):
        svg = r.sub(rempl, svg)
    return svg


def textes(o, source="fr", cle=None):
    """Tous les textes à traduire d'un fichier de pack, dans l'ordre où ils apparaissent (sans doublon)."""
    vus = {}

    def voir(o, cle):
        if isinstance(o, dict):
            if source in o and isinstance(o[source], str) and set(o) - {source} <= set(LANGUES):
                if a_traduire(o[source]):
                    vus.setdefault(o[source], cle)
                return
            for k, v in o.items():
                if k not in CLES_IGNOREES:
                    voir(v, k)
        elif isinstance(o, list):
            for v in o:
                voir(v, cle)
        elif isinstance(o, str):
            if "<svg" in o:
                for e in etiquettes_svg(o):
                    vus.setdefault(e, cle)
            elif cle in CHAMPS_SIMPLES and a_traduire(o):
                vus.setdefault(o, cle)
    voir(o, cle)
    return vus


# --- Packs -----------------------------------------------------------------------------------------------------------

def packs():
    return [d for d in sorted(PACKS.iterdir()) if (d / "pack.json").exists() and not d.name.startswith("_")]


def fichiers(dossier):
    """Les fichiers de contenu d'un pack (pack.json compris : son nom et sa description s'affichent dans les réglages)."""
    sauf = {"verifications.json", "ordre.json", "portraits.json"}
    fs = [f for f in sorted(dossier.glob("*.json")) if f.name not in sauf]
    fs += sorted((dossier / "donnees").glob("*.json")) if (dossier / "donnees").exists() else []
    return fs


def nom_langue(f, dossier):
    """Le nom du fichier de langue qui correspond à un fichier du pack : questions.json, donnees-avatar.json…"""
    return f.name if f.parent == dossier else "donnees-" + f.name


def source_de(dossier):
    return lire(dossier / "pack.json").get("langue_source", "fr")


def sources_du_pack(dossier):
    """{nom du fichier de langue: {texte source: champ}}."""
    src = source_de(dossier)
    return {nom_langue(f, dossier): textes(lire(f), src) for f in fichiers(dossier)}


def traductions(dossier, langue):
    d = dossier / "langues" / langue
    return {f.name: lire(f) for f in sorted(d.glob("*.json"))} if d.exists() else {}


def etat_pack(dossier, langue):
    """(textes source, traduits, manquants {fichier: [textes]}, orphelins {fichier: [textes]})."""
    sources, tr = sources_du_pack(dossier), traductions(dossier, langue)
    total = traduits = 0
    manquants, orphelins = {}, {}
    for f, ts in sources.items():
        t = tr.get(f, {})
        total += len(ts)
        faits = [s for s in ts if t.get(s)]
        traduits += len(faits)
        m = [s for s in ts if not t.get(s)]
        if m:
            manquants[f] = m
    for f, t in tr.items():
        o = [s for s in t if s not in sources.get(f, {})]
        if o:
            orphelins[f] = o
    return total, traduits, manquants, orphelins


def dictionnaire(langue, packs_=None):
    """Toutes les traductions des packs pour une langue : {texte source: traduction}. Un même texte traduit autrement
    par deux packs garde la première traduction (packs dans l'ordre alphabétique, socle compris)."""
    dico = {}
    for d in packs_ if packs_ is not None else packs():
        if source_de(d) == langue:
            continue
        sources = sources_du_pack(d)
        for f, t in traductions(d, langue).items():
            for s, v in t.items():
                if v and s in sources.get(f, {}):
                    dico.setdefault(s, v)
    return dico


def langues_presentes():
    out = {f.stem for f in (WEB / "langues").glob("*.json")} if (WEB / "langues").exists() else set()
    for d in packs():
        if (d / "langues").exists():
            out |= {x.name for x in (d / "langues").iterdir() if x.is_dir()}
    return sorted(out)


def assembler(ecrire_data=True):
    """data/langues/<xx>.json pour chaque langue présente dans un pack : {"format", "langue", "textes": {source: trad}}."""
    out = {}
    for l in langues_presentes():
        out[l] = {"format": 1, "langue": l, "textes": dictionnaire(l),
                  "interface": {k: v for k, v in catalogue(l)["textes"].items() if v}}
    if ecrire_data:
        dossier = DATA / "langues"
        for f in dossier.glob("*.json") if dossier.exists() else []:
            if f.stem not in out:
                f.unlink()
        for l, d in out.items():
            ecrire(dossier / (l + ".json"), d)
    return out


# --- Interface -------------------------------------------------------------------------------------------------------

# Une chaîne d'interface s'écrit __("…") dans web/index.html et web/moteur.js : son texte français est la clé du
# catalogue. Un objet texte fabriqué par le code, { fr: "…" }, se traduit de même (il peut être rangé dans la partie).
RE_L = re.compile(r"""(?<![\w.$])(?:__\(|\bfr:\s*)(["'])((?:\\.|(?!\1).)*)\1""")


def dejavascript(s, q):
    """Le texte d'un littéral JavaScript simple (échappements courants)."""
    return re.sub(r"\\(u[0-9a-fA-F]{4}|.)", lambda m: chr(int(m.group(1)[1:], 16)) if m.group(1)[0] == "u" and len(m.group(1)) == 5
                  else {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)), s)


def chaines_interface():
    out = []
    for f in (WEB / "index.html", WEB / "moteur.js"):
        for m in RE_L.finditer(f.read_text(encoding="utf-8")):
            s = dejavascript(m.group(2), m.group(1))
            if s not in out:
                out.append(s)
    return out


def catalogue(langue):
    p = WEB / "langues" / (langue + ".json")
    return lire(p) if p.exists() else {"format": 1, "langue": langue, "textes": {}}


def maj_interface(langue):
    cat = catalogue(langue)
    ch = chaines_interface()
    vieux = cat["textes"]
    cat["textes"] = {s: vieux.get(s, "") for s in ch}
    ecrire(WEB / "langues" / (langue + ".json"), cat)
    return cat


def etat_interface(langue):
    ch = chaines_interface()
    t = catalogue(langue)["textes"]
    return len(ch), sum(1 for s in ch if t.get(s)), [s for s in ch if not t.get(s)], [s for s in t if s not in ch]


# --- Ligne de commande -----------------------------------------------------------------------------------------------

def main(args):
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = args[0]
    if cmd == "etat":
        langue = args[1] if len(args) > 1 else "en"
        T = F = 0
        for d in packs():
            if source_de(d) == langue:
                continue
            total, faits, manq, orph = etat_pack(d, langue)
            T, F = T + total, F + faits
            o = sum(len(v) for v in orph.values())
            print(f"{d.name:12} {faits:5}/{total:<5} {100 * faits // max(total, 1):3} %" + (f"   {o} traduction(s) périmée(s)" if o else ""))
        n, f, manq, orph = etat_interface(langue)
        print(f"{'interface':12} {f:5}/{n:<5} {100 * f // max(n, 1):3} %" + (f"   {len(orph)} chaîne(s) périmée(s)" if orph else ""))
        print(f"{'total':12} {F + f:5}/{T + n:<5} {100 * (F + f) // max(T + n, 1):3} %")
        return 0
    if cmd == "a-traduire":
        langue, pack = args[1], args[2]
        quel = args[3] if len(args) > 3 and not args[3].startswith("--") else None
        mx = int(args[args.index("--max") + 1]) if "--max" in args else None
        _, _, manq, _ = etat_pack(PACKS / pack, langue)
        out = {}
        for f, l in manq.items():
            if quel and f != quel:
                continue
            for s in l:
                if mx is not None and sum(len(v) for v in out.values()) >= mx:
                    break
                out.setdefault(f, {})[s] = ""
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 0
    if cmd == "inscrire":
        langue, pack, fic = args[1], args[2], args[3]
        neuf, d = lire(fic), PACKS / pack
        sources = sources_du_pack(d)
        n = 0
        for f, t in neuf.items():
            if f not in sources:
                print(f"{f} : pas un fichier de {pack}", file=sys.stderr)
                return 1
            p = d / "langues" / langue / f
            vieux = lire(p) if p.exists() else {}
            for s, v in t.items():
                if s not in sources[f]:
                    print(f"{f} : texte inconnu, ignoré : {s[:70]}", file=sys.stderr)
                elif v:
                    vieux[s] = v
                    n += 1
            # Rangées dans l'ordre du fichier source, pour des relectures et des diffs lisibles.
            ecrire(p, {s: vieux[s] for s in sources[f] if s in vieux} | {s: v for s, v in vieux.items() if s not in sources[f]})
        print(f"{n} traduction(s) inscrite(s)")
        return 0
    if cmd == "nettoyer":
        for langue in [args[1]] if len(args) > 1 else langues_presentes():
            for d in packs():
                sources = sources_du_pack(d)
                for f, t in traductions(d, langue).items():
                    p = d / "langues" / langue / f
                    garde = {s: v for s, v in t.items() if s in sources.get(f, {})}
                    if len(garde) != len(t):
                        print(f"{d.name}/{f} : {len(t) - len(garde)} retirée(s)")
                        ecrire(p, garde) if garde else p.unlink()
        return 0
    if cmd == "interface":
        for langue in [args[1]] if len(args) > 1 else [l for l in LANGUES if l != "fr"]:
            cat = maj_interface(langue)
            print(f"web/langues/{langue}.json : {sum(1 for v in cat['textes'].values() if v)}/{len(cat['textes'])} traduites")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
