"""v26 : un extrait du vrai livre, dans sa langue, avec sa traduction. Demande de Victor (2026-10-28).

Règle : rien d'inventé. Chaque extrait est contrôlé mot pour mot sur un texte en ligne (Gutenberg, Wikisource,
Perseus, The Latin Library, archives…) avant d'entrer ici, et la trace du contrôle est gardée dans `verification`.
Sans texte exact trouvé, pas d'extrait. outils/verifier_sources.py refuse un extrait sans vérification.

Champs : texte (original), langue, traduction (absente si le texte est en français), traducteur (qui a traduit :
une traduction publiée, ou « traduction de l'IA »), reference (où dans le livre), verification {url, date, controle}.
Livres encore protégés : une ou deux phrases au plus (droit de citation).
"""

EXTRAITS = {
}


def donnees(id):
    e = EXTRAITS.get(id)
    if not e:
        return None
    out = {"texte": e["texte"], "langue": e["langue"], "reference": e["reference"], "verification": e["verification"]}
    if e.get("traduction"):
        out["traduction"] = {"fr": e["traduction"]}
        out["traducteur"] = e["traducteur"]
    return out
