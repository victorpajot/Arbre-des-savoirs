"""Questions de calcul : l'explication pose la formule, le calcul, et dit qui a trouvé l'équation (Victor, 2026-10-28).

Chaque entrée remplace l'explication de la question et lui ajoute une `source` : la routine
verifier_sources.py exige alors une vérification en ligne de l'attribution.
Les formules qui ne sont que des définitions (vitesse, période, énergie = puissance × durée) n'ont pas d'inventeur à citer.
"""

CALCULS = {
    "phys.energie.q03": (
        "Ec = ½ × m × v² = ½ × 2 × 3² = ½ × 2 × 9 = 9 J. Leibniz mesure la « force vive » d'un corps par m v² (1686). "
        "Coriolis y ajoute le ½ en 1829 : la variation de ½ m v² est alors exactement le travail des forces, un mot qu'il est le premier à employer en ce sens.",
        "Coriolis, Du calcul de l'effet des machines (1829) ; Leibniz, Brevis demonstratio (1686)"),
    "phys.energie.q10": (
        "Ep = m × g × h = 1 × 10 × 10 = 100 J. Le nom « énergie potentielle » vient de l'ingénieur écossais William Rankine, en 1853.",
        "Rankine (1853), d'après l'article Potential energy"),
    "phys.energie.q05": (
        "E = P × t = 10 W × 100 h = 1 000 Wh = 1 kWh. C'est la définition de l'énergie consommée : une puissance tenue pendant une durée.",
        None),
    "phys.forces.q03": (
        "F = m × a = 10 × 2 = 20 N. Newton énonce cette deuxième loi du mouvement dans les Principia (1687), mais pas sous cette forme : "
        "c'est Euler qui la met en équation au XVIIIe siècle.",
        "Sitko, Caderno Brasileiro de Ensino de Física 36-1 (2019)"),
    "phys.forces.q07": ("v = d / t = 100 m ÷ 20 s = 5 m/s.", None),
    "phys.forces.q12": ("a = Δv / Δt = (30 − 0) m/s ÷ 10 s = 3 m/s².", None),
    "phys.ondes.q03": (
        "d = v × t = 340 m/s × 3 s = 1 020 m, environ 1 km. La lumière de l'éclair arrive presque instantanément : "
        "Rømer a montré en 1676 que sa vitesse est finie, mais elle va près d'un million de fois plus vite que le son.",
        "Rømer (1676), d'après l'article Rømer's determination of the speed of light"),
    "phys.ondes.q09": ("f = 1 / T = 1 / 0,01 s = 100 Hz. La fréquence est le nombre de périodes par seconde.", None),
    "phys.relativite.q11": (
        "t = d / c = 150 000 000 km ÷ 300 000 km/s = 500 s, soit 500 ÷ 60 ≈ 8,3 min. "
        "Rømer est le premier à montrer, en 1676, que la lumière met du temps à voyager, en chronométrant les éclipses de Io, une lune de Jupiter.",
        "Rømer (1676), d'après l'article Rømer's determination of the speed of light"),
    "phys.thermo.q08": (
        "Q = m × c × ΔT = 1 kg × 4 186 J/(kg·°C) × 80 °C ≈ 335 000 J. Avec 1 000 W : t = Q / P ≈ 335 s, soit 335 ÷ 60 ≈ 5,6 min. "
        "L'idée que chaque substance a sa propre capacité à absorber la chaleur vient de Joseph Black, vers 1760.",
        "Joseph Black (1760), d'après sa biographie"),
    "phys.fluides.q02": (
        "ΔP = ρ × g × h = 1 000 kg/m³ × 10 m/s² × 10 m = 100 000 Pa = 1 bar, environ une atmosphère. "
        "Simon Stevin montre en 1586 que la pression d'un liquide ne dépend que de la hauteur de liquide au-dessus, pas de la forme du récipient.",
        "Stevin, De Beghinselen des Waterwichts (1586)"),
    "elec.ohm.q02": (
        "I = U / R = 12 V ÷ 4 Ω = 3 A. C'est la loi d'Ohm, publiée par Georg Ohm en 1827 dans Die galvanische Kette, mathematisch bearbeitet.",
        "Ohm, Die galvanische Kette, mathematisch bearbeitet (1827)"),
    "elec.ohm.q05": (
        "I = U / R = 9 V ÷ 3 Ω = 3 A. C'est la loi d'Ohm, publiée par Georg Ohm en 1827.",
        "Ohm, Die galvanische Kette, mathematisch bearbeitet (1827)"),
    "elec.ohm.q07": (
        "En dérivation : 1/R = 1/R₁ + 1/R₂ = 1/100 + 1/100 = 2/100, donc R = 100 ÷ 2 = 50 Ω. Deux chemins identiques laissent passer deux fois plus de courant. "
        "Cette règle se déduit des lois de Kirchhoff, publiées en 1845, et de la loi d'Ohm.",
        "Kirchhoff (1845), d'après l'article Kirchhoff's circuit laws"),
    "elec.puissance.q02": (
        "P = U × I = 230 V × 10 A = 2 300 W. Avec la loi d'Ohm (U = R × I), elle devient P = R × I² : "
        "c'est la loi que Joule trouve en 1841 en mesurant la chaleur dégagée par un fil parcouru par un courant.",
        "Joule, On the Heat evolved by Metallic Conductors of Electricity (1841)"),
    "elec.puissance.q03": ("E = P × t = 2 kW × 3 h = 6 kWh (2 000 W, c'est 2 kW).", None),
    "elec.puissance.q08": ("E = P × t = 5 W × 1 000 h = 5 000 Wh = 5 kWh.", None),
    "chim.acides.q10": (
        "pH = −log[H⁺] = −log(0,01) = −log(10⁻²) = 2. Le chimiste danois Søren Sørensen invente le pH en 1909, au laboratoire Carlsberg.",
        "Sørensen (1909), d'après l'article pH"),
    "chim.etats.q08": (
        "V = n × R × T / P = 1 × 8,314 × 273,15 ÷ 101 325 ≈ 0,0224 m³ = 22,4 L. C'est la loi des gaz parfaits, P V = n R T, énoncée par Émile Clapeyron en 1834.",
        "Clapeyron (1834), d'après l'article Ideal gas law"),
    "math.geometrie.q01": (
        "a² + b² = c² : 3² + 4² = 9 + 16 = 25, donc c = √25 = 5. Le théorème porte le nom de Pythagore, "
        "mais les Babyloniens s'en servaient déjà plus de mille ans avant lui. Euclide le démontre dans les Éléments (livre I, proposition 47).",
        "Euclide, Éléments, I, 47, commentaire de D. E. Joyce"),
    "math.algebre.q10": (
        "Δ = b² − 4ac avec a = 1, b = −5, c = 6 : (−5)² − 4 × 1 × 6 = 25 − 24 = 1. Les solutions (5 ± √1) ÷ 2 valent 2 et 3. "
        "Al-Khwârizmî est le premier à résoudre ces équations du second degré de façon systématique, au IXe siècle, en « complétant le carré ».",
        "Al-Khwârizmî, Abrégé du calcul par la restauration et la comparaison (vers 813-833)"),
    "math.probabilites.q11": (
        "E = 10 € × 1/5 + 0 € × 4/5 = 2 €. Christiaan Huygens développe la notion d'espérance dans son traité sur les jeux de hasard, De ratiociniis in ludo aleae (1657).",
        "Huygens, De ratiociniis in ludo aleae (1657)"),
    "math.infini.q05": (
        "Fₙ = Fₙ₋₁ + Fₙ₋₂ : 5 + 8 = 13. Fibonacci la présente en 1202 dans le Liber abaci avec un problème de lapins, "
        "mais des mathématiciens indiens la connaissaient dès le VIe siècle.",
        "Fibonacci, Liber abaci (1202)"),
    "biais.ancrage.q12": (
        "8! = 8 × 7 × 6 × 5 × 4 × 3 × 2 × 1 = 40 320. Les estimations rapides en sont très loin. La notation n! est due à Christian Kramp, en 1808.",
        "Kramp, Éléments d'arithmétique universelle (1808)"),
    "elec.numerique.q01": (
        "1011 = 1 × 8 + 0 × 4 + 1 × 2 + 1 × 1 = 11. Leibniz expose cette arithmétique binaire, avec les seuls chiffres 0 et 1, dans un mémoire publié en 1705.",
        "Leibniz, Explication de l'arithmétique binaire (1705)"),
}
