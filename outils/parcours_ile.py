#!/usr/bin/env python3
"""Le parcours de l'île, écrit depuis les données du jeu (Victor, 2026-11-17).

Pour chaque âge : ce que vit le joueur, ce qu'il faut pour le quitter (savoirs, habitants, épreuve-porte et sa quête),
les besoins avec leurs savoirs, les aménagements avec leur épreuve et leur quête. Rien n'est écrit à la main ici :
on relance le script après chaque changement des packs.

    python3 outils/packs.py assembler && python3 outils/parcours_ile.py > docs/parcours-ile.md
"""
import json, os, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def lire(nom):
    with open(os.path.join(RACINE, "data", nom), encoding="utf8") as f:
        return json.load(f)


def fr(t):
    return (t or {}).get("fr", "") if isinstance(t, dict) else (t or "")


def main():
    ile = lire("ile.json")
    skills = lire("skills.json")
    comps = {c["id"]: c for c in skills["competences"]}
    stats = {s["id"]: fr(s["nom"]) for s in lire("regles.json")["stats"]}
    epreuves = {e["id"]: e for e in ile.get("epreuves", [])}
    amens = ile.get("amenagements", [])
    ep_amen = {e["amenagement"]: e for e in ile.get("epreuves", []) if e.get("amenagement")}
    ressources = {r["id"]: fr(r["nom"]).lower() for r in ile.get("ressources", [])}
    quartiers = {q["id"]: fr(q.get("nomFinal") or q["nom"]) for q in ile.get("quartiers", [])}
    R = ile["regles"]
    out = []
    w = out.append

    def savoir(i):
        c = comps.get(i)
        return f"{fr(c['nom'])} ({stats.get(c['stat'], c['stat'])})" if c else f"`{i}` (absent)"

    def quete(e):
        q = e.get("quete")
        if not q:
            return "aucune"
        return ", ".join(fr(o["nom"]).lower() + (" (sur une bête)" if o.get("chasse") else "") for o in q["objets"])

    def cout(a):
        c = a.get("cout") or {}
        return ", ".join(f"{v} {'crédits' if k == 'credits' else ressources.get(k, k)}" for k, v in c.items()) or "rien"

    w("# Le parcours de l'île")
    w("")
    w("Ce document est généré depuis les données du jeu par `outils/parcours_ile.py`. Il décrit ce que le joueur traverse, âge après âge, et ce qu'il doit apprendre, trouver et bâtir pour avancer.")
    w("")
    w("## Vue d'ensemble")
    w("")
    w("| Âge | Pour le quitter | Habitants au plus | Rien d'après |")
    w("|---|---|---|---|")
    ages = ile["ages"]
    for i, a in enumerate(ages):
        suivant = fr(ages[i + 1]["nom"]).lower() if i + 1 < len(ages) else None
        requis = [b for b in a.get("besoins", []) if not b.get("optionnel")]
        cond = []
        if requis:
            cond.append(f"{len(requis)} besoin{'s' if len(requis) > 1 else ''} couvert{'s' if len(requis) > 1 else ''}")
        if a.get("peuple"):
            cond.append(f"{a['peuple']} habitants")
        if a.get("epreuve"):
            cond.append(f"épreuve « {fr(epreuves[a['epreuve']]['nom'])} »")
        w(f"| {fr(a['nom'])} | {' + '.join(cond) if suivant and cond else 'âge à écrire' if not a.get('besoins') else 'dernier âge'} | {a.get('plafond', 'sans limite')} | {a.get('jusqua', '')} |")
    w("")
    w("« Rien d'après » : l'année limite des visiteurs et des achats d'Alyca à cet âge, pour éviter les anachronismes.")
    w("")
    q = R.get("quartier", {})
    w(f"Quartiers : à partir du village, chaque quartier s'ouvre pour {q.get('credits')} crédits (moitié prix après une bonne réponse) et demande du monde : {q.get('habitants_premier')} habitants pour le deuxième, puis {q.get('habitants')} de plus à chaque fois.")
    w(f"Population : {R.get('limites', {}).get('toits_base')} couchages sans rien bâtir, puis les toits des aménagements. Chaque épreuve réussie fait venir {R.get('demographie', {}).get('par_epreuve')} habitants s'il reste de la place.")
    w("")

    for i, a in enumerate(ages):
        w(f"## {i + 1}. {fr(a['nom'])}")
        w("")
        if a.get("description"):
            w(f"**Ce que vit le joueur.** {fr(a['description'])}")
            w("")
        besoins = a.get("besoins", [])
        if not besoins:
            w("Cet âge reste à écrire : pas encore de besoins.")
            w("")
        else:
            w("### Besoins et savoirs")
            w("")
            w("Un savoir maîtrisé suffit à couvrir un besoin.")
            w("")
            w("| Besoin | Savoirs qui y répondent | Aménagements débloqués |")
            w("|---|---|---|")
            for b in besoins:
                sav = b.get("savoirs", [])
                ouvre = [fr(x["nom"]) for x in amens if (x.get("age") or 0) <= a["rang"] and set(x.get("savoirs") or ([x["savoir"]] if x.get("savoir") else [])) & set(sav)]
                opt = " (optionnel)" if b.get("optionnel") else ""
                w(f"| {fr(b['nom'])}{opt} | {' ; '.join(savoir(s) for s in sav) or 'aucun'} | {', '.join(ouvre) or 'aucun'} |")
            w("")
            opts = [b for b in besoins if b.get("optionnel") and b.get("alerte")]
            for b in opts:
                w(f"- Négliger « {fr(b['nom'])} » : {fr(b['alerte'])}")
            if opts:
                w("")
        if a.get("epreuve"):
            e = epreuves[a["epreuve"]]
            w("### La porte vers l'âge suivant")
            w("")
            w(f"**Épreuve unique : {fr(e['nom'])}.** {fr(e.get('accroche'))}")
            w("")
            w(f"- Quête avant l'épreuve : {quete(e)}.")
            w(f"- Gestes : {', '.join(fr(s['titre']).lower() for s in e['etapes'])}.")
            if a.get("peuple"):
                w(f"- Il faut aussi {a['peuple']} habitants sur l'île.")
            w(f"- Ce qu'on en retient : {fr(e['chute']['texte'])} (source : {e['chute']['source']})")
            w("")
        elif a.get("peuple"):
            w(f"**Pour passer à l'âge suivant** : tous les besoins non optionnels couverts et {a['peuple']} habitants.")
            w("")
        ici = [x for x in amens if (x.get("age") or 1) == a["rang"]]
        if ici:
            w("### Aménagements qui deviennent possibles")
            w("")
            w("| Aménagement | Quartier | Savoir requis (un au choix) | Coût | Épreuve et quête |")
            w("|---|---|---|---|---|")
            for x in ici:
                e = ep_amen.get(x["id"])
                sav = x.get("savoirs") or ([x["savoir"]] if x.get("savoir") else [])
                apport = []
                if x.get("places"):
                    apport.append(f"{x['places']} places")
                if x.get("produit"):
                    apport.append("produit " + ", ".join(ressources.get(k, k) for k in x["produit"]))
                nom = fr(x["nom"]) + (f" ({', '.join(apport)})" if apport else "")
                w(f"| {nom} | {quartiers.get(x.get('quartier'), '')} | {' ; '.join(savoir(s) for s in sav)} | {cout(x)} | {('« ' + fr(e['nom']) + ' » : ' + quete(e)) if e else 'aucune'} |")
            w("")

    g = ile.get("grotte")
    grottes = ile.get("grottes") or ([g] if g else [])
    if grottes:
        w("## Les grottes")
        w("")
        for g in grottes:
            w(f"### {fr(g['nom'])}")
            w("")
            w(fr(g.get("description")))
            w("")
            for z in g.get("zones", []):
                req = ", ".join(savoir(s) for s in z.get("ouvre", []))
                w(f"- {fr(z['nom'])} : {len(z.get('recits', []))} récits" + (f" ; passage obligé avant : {req}" if req else "") + (f" ; ouverte à partir de l'âge {z['age'] + 1}" if z.get("age") is not None else "") + ".")
            w("")
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
