"""v31 (Victor) : chaque case du plateau désigne les compétences qu'elle évoque, dans son arbre.

Sur « Les pois de Mendel », l'IA prend Génétique ; sur « Faraday et l'induction », Magnétisme et induction.
Le moteur (choixIA) les essaie d'abord, puis le reste de l'arbre de la case. Rangé à part dans plateau.json
(« competences_cases ») pour ne pas toucher aux cases sourcées.
"""

COMPETENCES = {
    1: ["sci.evolution", "sci.corps"], 2: ["math.arithmetique"], 3: ["phys.forces"], 4: ["rhet.narration"],
    5: ["astro.observer", "astro.systeme"], 6: ["math.geometrie", "math.arithmetique"], 7: ["sci.atomes"],
    8: ["psy.personnalite", "psy.cerveau"], 9: ["philo.antiquite", "philo.ethique"], 10: ["philo.antiquite", "philo.sciences"],
    11: ["math.geometrie", "math.logique"], 12: ["sci.methode"], 13: ["astro.systeme", "astro.orbites"],
    14: ["phys.fluides"], 15: ["astro.systeme", "astro.observer"], 16: ["astro.etoiles", "astro.observer"],
    17: ["phys.forces", "phys.unites"], 18: ["philo.antiquite"], 19: ["biais.croyances", "biais.disponibilite"],
    20: ["astro.systeme", "astro.orbites"], 21: ["math.arithmetique", "math.algebre"], 22: ["math.algebre"],
    23: ["phys.ondes"], 24: ["philo.medievale"], 25: ["math.arithmetique", "math.infini"], 26: ["phys.ondes"],
    27: ["philo.medievale", "philo.sciences"], 28: ["biais.croyances", "biais.statistiques"],
    29: ["rhet.propagande", "rhet.narration"], 30: ["astro.systeme", "astro.orbites"], 31: ["sci.corps"],
    32: ["psy.emotions", "psy.personnalite"], 33: ["astro.observer"], 34: ["astro.orbites"],
    35: ["astro.systeme", "astro.orbites"], 36: ["biais.outils", "biais.confirmation"], 37: ["math.probabilites"],
    38: ["sci.cellule"], 39: ["sci.immunite", "sci.cellule"], 40: ["phys.forces"], 41: ["sci.ecologie", "sci.evolution"],
    42: ["rhet.argument", "rhet.persuasion"], 43: ["elec.circuits"], 44: ["philo.classique", "philo.ethique"],
    45: ["chim.reactions"], 46: ["chim.reactions"], 47: ["sci.immunite"], 48: ["elec.circuits", "elec.ohm"],
    49: ["elec.magnetisme", "elec.energies"], 50: ["sci.evolution"], 51: ["elec.em"], 52: ["sci.genetique"],
    53: ["sci.atomes", "chim.liaisons"], 54: ["sci.immunite", "sci.biotech"], 55: ["chim.noyau"],
    56: ["phys.relativite", "phys.quantique"], 57: ["phys.quantique"], 58: ["astro.galaxies", "astro.sombre"],
    59: ["math.logique"], 60: ["sci.genetique", "sci.biotech"], 61: ["astro.espace"], 62: ["math.logique"],
    63: ["math.probabilites", "math.statistiques"],
}
