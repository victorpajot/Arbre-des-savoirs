"""v15 : le symbole de chaque compétence, pour son badge (couleur de l'arbre, symbole, rang).

Des caractères texte (math, grec, flèches, formes) plutôt que des emoji : le badge les dessine en blanc.
"""

SYMBOLES = {
    "math.arithmetique": "½", "math.proportions": "%", "math.probabilites": "⚄", "math.logique": "∧",
    "math.algebre": "x²", "math.statistiques": "σ", "math.geometrie": "△", "math.infini": "∞",
    "phys.unites": "m", "phys.forces": "F", "phys.energie": "E", "phys.ondes": "λ",
    "phys.fluides": "Pa", "phys.thermo": "°C", "phys.relativite": "c", "phys.quantique": "ħ",
    "sci.methode": "?", "sci.cellule": "◉", "sci.evolution": "⋔", "sci.genetique": "ADN",
    "sci.corps": "♥", "sci.immunite": "✚", "sci.ecologie": "♻", "sci.biotech": "✂",
    "rhet.argument": "∴", "rhet.figures": "❦", "rhet.persuasion": "☞", "rhet.sophismes": "≠",
    "rhet.debat": "⇄", "rhet.narration": "¶", "rhet.discours": "«»", "rhet.propagande": "‼",
    "biais.confirmation": "✓", "biais.ancrage": "#1", "biais.disponibilite": "!", "biais.surconfiance": "↑",
    "biais.decision": "€", "biais.statistiques": "≈", "biais.croyances": "?!", "biais.outils": "⚒",
    "psy.emotions": "☺", "psy.memoire": "↺", "psy.motivation": "➚", "psy.influence": "⇉",
    "psy.cerveau": "Ψ", "psy.developpement": "ABC", "psy.personnalite": "◐", "psy.bienetre": "☯",
    "sci.atomes": "⚛", "chim.liaisons": "H₂O", "chim.acides": "pH", "chim.reactions": "→",
    "chim.etats": "❄", "chim.organique": "⌬", "chim.quotidien": "⚗", "chim.noyau": "☢",
    "astro.systeme": "☉", "astro.etoiles": "✶", "astro.orbites": "⊕", "astro.galaxies": "@",
    "astro.observer": "☾", "astro.espace": "⇡", "astro.exoplanetes": "♁", "astro.sombre": "●",
    "elec.circuits": "+−", "elec.ohm": "Ω", "elec.puissance": "W", "elec.magnetisme": "NS",
    "elec.em": "∿", "elec.electronique": "⊳", "elec.energies": "kW", "elec.numerique": "01",
    "philo.antiquite": "Φ", "philo.medievale": "✠", "philo.classique": "✒", "philo.moderne": "∃",
    "philo.ethique": "⚖", "philo.politique": "⚑", "philo.esprit": "☁", "philo.sciences": "⊢",
}


# v29 (Victor) : quand un objet du jeu dit mieux la compétence qu'un caractère, le badge montre son pixel art.
# Le symbole reste pour les compétences sans objet parlant (σ, ∞, x² se lisent très bien).
EMBLEMES = {
    "math.arithmetique": "boulier", "math.probabilites": "des-pascal", "math.logique": "ardoise-boole",
    "math.geometrie": "compas-euclide",
    "phys.unites": "metre-etalon", "phys.forces": "pomme-newton", "phys.energie": "machine-joule",
    "phys.ondes": "prisme-newton", "phys.fluides": "couronne-hieron", "phys.thermo": "feu", "phys.relativite": "relativite",
    "sci.methode": "rasoir-ockham", "sci.cellule": "microscope-hooke", "sci.evolution": "carnet-darwin",
    "sci.genetique": "pois-mendel", "sci.immunite": "boite-petri", "sci.biotech": "adn",
    "rhet.figures": "plume", "rhet.persuasion": "rouleau-aristote", "rhet.narration": "enluminure",
    "rhet.discours": "cailloux-demosthene", "rhet.propagande": "presse",
    "biais.ancrage": "roue-loterie", "biais.outils": "lunettes",
    "psy.memoire": "fiche-ebbinghaus", "psy.influence": "lignes-asch",
    "sci.atomes": "atome", "chim.liaisons": "modele-moleculaire", "chim.acides": "papier-tournesol",
    "chim.reactions": "balance-lavoisier", "chim.etats": "bougie", "chim.noyau": "verre-uranium",
    "astro.systeme": "heliocentre", "astro.galaxies": "plaque-hubble", "astro.observer": "lunette-galilee",
    "astro.espace": "fusee", "astro.exoplanetes": "disque-voyager",
    "elec.circuits": "bouteille-leyde", "elec.ohm": "pile-volta", "elec.puissance": "ampoule-edison",
    "elec.magnetisme": "bobine-faraday", "elec.electronique": "puce", "elec.energies": "bobine-tesla",
    "elec.numerique": "ordinateur",
    "philo.antiquite": "lanterne-diogene", "philo.classique": "poele-descartes", "philo.moderne": "marteau-nietzsche",
    "philo.politique": "couronne", "philo.esprit": "ruban-turing",
}
