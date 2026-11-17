#!/usr/bin/env python3
"""La vue nodale du parcours de l'île (Victor, 2026-11-17) : âges, besoins, savoirs, aménagements, épreuves et grottes
en nœuds reliés ; la fiche de ce qu'on sélectionne (nœud ou lien) s'affiche à côté. Tout vient des données du jeu.

    python3 outils/packs.py assembler && python3 outils/parcours_graphe.py > docs/parcours-ile-graphe.html

Le gabarit de la page est outils/parcours_graphe.html ; ce script y place le graphe (nœuds déjà positionnés, liens, fiches).
"""
import json, os, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Une colonne par âge ; dans la colonne, quatre couloirs : besoins, savoirs, aménagements, épreuves.
LARG, HAUT, PAS_X, PAS_Y, COL = 176, 46, 214, 60, 900


def lire(nom):
    with open(os.path.join(RACINE, "data", nom), encoding="utf8") as f:
        return json.load(f)


def fr(t):
    return (t or {}).get("fr", "") if isinstance(t, dict) else (t or "")


def main():
    ile = lire("ile.json")
    comps = {c["id"]: c for c in lire("skills.json")["competences"]}
    stats = {s["id"]: fr(s["nom"]) for s in lire("regles.json")["stats"]}
    epreuves = {e["id"]: e for e in ile.get("epreuves", [])}
    ep_amen = {e["amenagement"]: e for e in ile.get("epreuves", []) if e.get("amenagement")}
    ressources = {r["id"]: fr(r["nom"]).lower() for r in ile.get("ressources", [])}
    quartiers = {q["id"]: fr(q.get("nomFinal") or q["nom"]) for q in ile.get("quartiers", [])}
    ages, amens, grottes = ile["ages"], ile.get("amenagements", []), ile.get("grottes", [])
    zone_grotte = {z["id"]: g for g in grottes for z in g.get("zones", [])}
    N, L, bandes = {}, [], []

    def noeud(i, genre, nom, x, y, fiche, large=LARG):
        N[i] = {"id": i, "genre": genre, "nom": nom, "x": x, "y": y, "l": large, "h": HAUT, "fiche": fiche}

    def lien(a, b, genre, titre, texte):
        if a in N and b in N:
            L.append({"de": a, "vers": b, "genre": genre, "titre": titre, "texte": texte})

    def nom_savoir(i):
        c = comps.get(i)
        return fr(c["nom"]) if c else i

    def savoirs_de(x):
        return x.get("savoirs") or ([x["savoir"]] if x.get("savoir") else [])

    def cout(a):
        c = a.get("cout") or {}
        return ", ".join(f"{v} {'crédits' if k == 'credits' else ressources.get(k, k)}" for k, v in c.items()) or "rien"

    def quete(e):
        q = e.get("quete")
        return [fr(o["nom"]) + (" (sur une bête abattue)" if o.get("chasse") else (", " + fr(o["zone"]) if o.get("zone") else "")) for o in q["objets"]] if q else []

    def fiche_epreuve(e, role):
        f = [["Rôle", role], ["En deux mots", fr(e.get("accroche"))]]
        if e.get("quete"):
            f.append(["Quête avant l'épreuve", fr(e["quete"]["nom"]) + ". " + fr(e["quete"]["texte"])])
            f.append(["À trouver sur l'île", quete(e)])
        f.append(["Gestes", [fr(s["titre"]) + " : " + fr(s["consigne"]) for s in e["etapes"]]])
        f.append(["Ce qu'on en retient", fr(e["chute"]["texte"])])
        f.append(["Source", e["chute"]["source"]])
        return f

    bas = 0
    for i, a in enumerate(ages):
        x0, aid = i * COL, "age:" + a["id"]
        suivant = ages[i + 1] if i + 1 < len(ages) else None
        requis = [b for b in a.get("besoins", []) if not b.get("optionnel")]
        cond = []
        if requis:
            cond.append(f"{len(requis)} besoin{'s' if len(requis) > 1 else ''} couvert{'s' if len(requis) > 1 else ''} (hors optionnels)")
        if a.get("peuple"):
            cond.append(f"{a['peuple']} habitants sur l'île")
        if a.get("grotte") and a["grotte"] in zone_grotte:
            cond.append("le passage par " + fr(zone_grotte[a["grotte"]]["nom"]).lower())
        if a.get("epreuve"):
            cond.append("l'épreuve « " + fr(epreuves[a["epreuve"]]["nom"]) + " »")
        fa = [["Ce que vit le joueur", fr(a.get("description"))]]
        if suivant:
            fa.append(["Pour passer à : " + fr(suivant["nom"]).lower(), cond or ["âge à écrire"]])
        fa.append(["Habitants au plus", str(a.get("plafond", "sans limite"))])
        if a.get("jusqua") is not None:
            fa.append(["Rien d'après", f"l'an {a['jusqua']} : visiteurs et achats d'Alyca ne dépassent pas cette date"])
        if not a.get("besoins"):
            fa.append(["État", "Cet âge reste à écrire : pas encore de besoins."])
        noeud(aid, "age", fr(a["nom"]), x0, 0, fa, large=PAS_X + LARG)
        y, place_amen = 100, {}
        for b in a.get("besoins", []):
            bid, sav = f"besoin:{a['id']}:{b['id']}", [s for s in b.get("savoirs", []) if s in comps]
            fb = [["Âge", fr(a["nom"])], ["Pourquoi", fr(b.get("texte"))], ["Savoirs qui y répondent (un seul suffit)", [nom_savoir(s) for s in sav]],
                  ["Obligatoire", "non, optionnel" if b.get("optionnel") else "oui, pour quitter cet âge"]]
            if b.get("alerte"):
                fb.append(["Si on le néglige", fr(b["alerte"])])
            noeud(bid, "besoin", fr(b["nom"]) + (" (optionnel)" if b.get("optionnel") else ""), x0, y, fb)
            for k, s in enumerate(sav):
                sid, c = "savoir:" + s, comps[s]
                if sid not in N:
                    fs = [["Arbre", stats.get(c["stat"], c["stat"])], ["De quoi il s'agit", fr(c.get("description"))], ["S'apprend à l'âge", fr(a["nom"])]]
                    if any(s in z.get("ouvre", []) for z in zone_grotte.values() for z in z["zones"]):
                        g = [g for g in grottes for z in g["zones"] if s in z.get("ouvre", [])][0]
                        fs.append(["Passage exigé avant", fr(g["nom"])])
                    noeud(sid, "savoir", fr(c["nom"]), x0 + PAS_X, y + k * PAS_Y, fs)
                lien(bid, sid, "couvre", "Besoin couvert par ce savoir", f"Maîtriser « {fr(c['nom'])} » suffit à couvrir le besoin « {fr(b['nom'])} »." + (" Un autre savoir de ce besoin ferait aussi l'affaire." if len(sav) > 1 else ""))
            y += max(1, len(sav)) * PAS_Y + 14
        # Les aménagements de cet âge, chacun à la hauteur de son premier savoir quand la place est libre.
        ya = 100
        for x in [x for x in amens if (x.get("age") or 1) == a["rang"] or (a["rang"] == 0 and False)]:
            sav = [s for s in savoirs_de(x) if "savoir:" + s in N]
            vise = min([N["savoir:" + s]["y"] for s in sav] or [ya])
            ya = max(ya, vise)
            mid, e = "amen:" + x["id"], ep_amen.get(x["id"])
            fm = [["À quoi ça sert", fr(x.get("usage"))], ["Quartier", quartiers.get(x.get("quartier"), "")], ["Possible à partir de", fr(a["nom"])],
                  ["Savoir requis" + (" (un au choix)" if len(savoirs_de(x)) > 1 else ""), [nom_savoir(s) for s in savoirs_de(x)]], ["Coût", cout(x)]]
            if x.get("places"):
                fm.append(["Loge", f"{x['places']} habitants"])
            if x.get("produit"):
                fm.append(["Produit", ", ".join(ressources.get(k, k) for k in x["produit"])])
            if e:
                fm.append(["Épreuve à réussir avant de bâtir", fr(e["nom"])])
            noeud(mid, "amen", fr(x["nom"]), x0 + 2 * PAS_X, ya, fm)
            for s in sav:
                lien("savoir:" + s, mid, "permet", "Savoir qui permet de bâtir", f"« {nom_savoir(s)} » permet de bâtir « {fr(x['nom'])} »." + (" L'un des savoirs listés suffit." if len(savoirs_de(x)) > 1 else ""))
            if e:
                eid = "epreuve:" + e["id"]
                noeud(eid, "epreuve", fr(e["nom"]), x0 + 3 * PAS_X, ya, fiche_epreuve(e, f"Garde l'aménagement « {fr(x['nom'])} » : on ne le bâtit qu'après l'avoir réussie, une seule fois."))
                lien(mid, eid, "garde", "Épreuve à réussir avant de bâtir", f"Avant de bâtir « {fr(x['nom'])} », il faut réussir l'épreuve « {fr(e['nom'])} »." + (" Elle demande d'abord de trouver sur l'île : " + ", ".join(quete(e)) + "." if e.get("quete") else ""))
            ya += PAS_Y
        # L'épreuve qui garde la porte de l'âge suivant, en haut à droite de la colonne.
        if a.get("epreuve") and suivant:
            e, eid = epreuves[a["epreuve"]], "epreuve:" + a["epreuve"]
            noeud(eid, "epreuve", fr(e["nom"]), x0 + 3 * PAS_X, 0, fiche_epreuve(e, f"Porte vers l'âge suivant : {fr(suivant['nom']).lower()}. Elle n'apparaît qu'une fois les autres conditions réunies."))
        bandes.append({"x": x0 - 24, "l": COL - 20, "nom": fr(a["nom"]), "rang": i + 1, "id": aid})
        a["_bas"] = max(y, ya)
        bas = max(bas, y, ya)
    # Les grottes, sous les besoins de l'âge où elles apparaissent.
    libre = {}
    for g in grottes:
        rang = min(g.get("age") or 0, len(ages) - 1)
        a, x0 = ages[rang], rang * COL
        y = libre.get(rang, a["_bas"] + 30)
        gid = "grotte:" + g["id"]
        fg = [["Ce que c'est", fr(g.get("description"))], ["Apparaît à l'âge", fr(a["nom"])], ["Comment y entrer", "Envoyer un explorateur avec une torche : elle se cache sous le brouillard."]]
        for z in g.get("zones", []):
            fg.append(["À trouver dans les galeries", [fr(r["titre"]) for r in z.get("recits", [])]])
            fg.append(["Quiz", f"{z.get('seuil', len(z['recits']))} réponses justes sur {len(z['recits'])} pour graver le passage"])
            fg.append(["Sources", sorted({r["source"] for r in z.get("recits", [])})])
            ouvre = [nom_savoir(s) for s in z.get("ouvre", []) if s in comps] + ["l'épreuve qui fait quitter " + fr(b["nom"]).lower() for b in ages if b.get("grotte") == z["id"]]
            fg.append(["Ce que le passage ouvre", ouvre or "Rien pour l'instant."])
        noeud(gid, "grotte", fr(g["nom"]), x0, y, fg)
        libre[rang] = y + PAS_Y
        bas = max(bas, y + PAS_Y)
        for z in g.get("zones", []):
            for s in z.get("ouvre", []):
                lien(gid, "savoir:" + s, "passage", "Passage exigé avant ce savoir", f"« {nom_savoir(s)} » reste fermé tant qu'on n'a pas gravé le passage de {fr(g['nom']).lower()} : trouver tous ses récits, puis réussir son quiz.")
            for b in ages:
                if b.get("grotte") == z["id"] and b.get("epreuve"):
                    lien(gid, "epreuve:" + b["epreuve"], "passage", "Passage exigé avant cette épreuve", f"L'épreuve « {fr(epreuves[b['epreuve']]['nom'])} » n'apparaît qu'après le passage par {fr(g['nom']).lower()}. Le mythe d'abord, le rassemblement ensuite.")
    # La chaîne des âges, par l'épreuve-porte quand il y en a une.
    for i, a in enumerate(ages[:-1]):
        s, aid, sid = ages[i + 1], "age:" + a["id"], "age:" + ages[i + 1]["id"]
        cond = N[aid]["fiche"][1][1]
        resume = "Il faut : " + " ; ".join(cond) + "." if isinstance(cond, list) else ""
        if a.get("epreuve"):
            e = fr(epreuves[a["epreuve"]]["nom"])
            lien(aid, "epreuve:" + a["epreuve"], "porte", "Épreuve qui garde la porte", f"Pour quitter {fr(a['nom']).lower()}, une épreuve unique : « {e} ». " + resume)
            lien("epreuve:" + a["epreuve"], sid, "porte", "Passage à l'âge suivant", f"Réussir « {e} » ouvre : {fr(s['nom']).lower()}.")
        else:
            lien(aid, sid, "porte", "Passage à l'âge suivant", f"De {fr(a['nom']).lower()} à {fr(s['nom']).lower()}. " + (resume or "Cet âge reste à écrire."))
    for b in bandes:
        b["h"] = bas + 40
    R = ile["regles"]
    q = R.get("quartier", {})
    notes = [f"Quartiers : à partir du village, chacun s'ouvre pour {q.get('credits')} crédits et demande du monde : {q.get('habitants_premier')} habitants pour le deuxième, puis {q.get('habitants')} de plus à chaque fois.",
             f"Population : {R.get('limites', {}).get('toits_base')} couchages sans rien bâtir, puis les toits des aménagements. Chaque épreuve réussie fait venir {R.get('demographie', {}).get('par_epreuve')} habitants s'il reste de la place."]
    graphe = {"noeuds": list(N.values()), "liens": L, "bandes": bandes, "notes": notes}
    with open(os.path.join(RACINE, "outils", "parcours_graphe.html"), encoding="utf8") as f:
        page = f.read()
    sys.stdout.write(page.replace("/*GRAPHE*/null", json.dumps(graphe, ensure_ascii=False).replace("</", "<\\/")))


if __name__ == "__main__":
    main()
