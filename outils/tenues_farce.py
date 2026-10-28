"""v25 : les tenues de farce. L'IA ne remplace plus le personnage : elle repeint ses vêtements pour 24 h.

Chaque tenue remplace les sept couleurs de la tenue (haut sombre/moyen/clair « ! X * », pantalon « ~ Z »,
accents « + Q »). Les savants incarnés portent les mêmes clés, la farce marche donc aussi sur eux.
`theme` : l'arbre où l'IA la sort de préférence quand l'épreuve ratée en vient.
"""

# id, nom (avec article, pour ses répliques), notice, thème, couleurs
TENUES = [
    ("rose-bonbon", "une tenue rose bonbon",
     "Le rose n'a été rangé du côté des filles qu'au XXe siècle. En 1918, un magazine américain conseillait encore le rose aux garçons, couleur « plus décidée ».",
     "empathie",
     {"!": "#B83C78", "X": "#F06AAE", "*": "#FFB3DA", "~": "#8E2C5C", "Z": "#C9478A", "+": "#FFFFFF", "Q": "#FFE3F2"}),
    ("jaune-canari", "une tenue jaune canari",
     "Les mineurs descendaient un canari au fond : s'il cessait de chanter, le grisou ou le monoxyde de carbone rôdait. Vous voilà sentinelle.",
     "lucidite",
     {"!": "#B8961A", "X": "#F5D326", "*": "#FFF08A", "~": "#8A6F12", "Z": "#C9A51F", "+": "#2B2B33", "Q": "#5D6470"}),
    ("vert-scheele", "une tenue vert de Scheele",
     "Inventé en 1775 par Carl Wilhelm Scheele, ce vert doit son éclat à l'arsenic. Il a teint des papiers peints, des robes et des fleurs artificielles. Portez-le sans le lécher.",
     "alchimie",
     {"!": "#1F7A3A", "X": "#3FBF5C", "*": "#9BEA9E", "~": "#155229", "Z": "#24863F", "+": "#E8E8EE", "Q": "#FFFFFF"}),
    ("violet-perkin", "une tenue violet de Perkin",
     "En 1856, William Perkin, 18 ans, cherche la quinine et obtient une teinture mauve. La mauvéine lance l'industrie des colorants de synthèse. Vous, vous ne lancez rien.",
     "alchimie",
     {"!": "#5E2F8A", "X": "#9B59D0", "*": "#CDA6EE", "~": "#3B1A5C", "Z": "#5E2F8A", "+": "#F2C14E", "Q": "#FFE79A"}),
    ("orange-securite", "un gilet orange sécurité",
     "L'orange se repère de loin, même au crépuscule : chantiers, gilets, combinaisons de la NASA. Personne ne vous perdra de vue. C'est le but.",
     "mecanique",
     {"!": "#C24E0A", "X": "#FF7A1A", "*": "#FFB36B", "~": "#2B2B33", "Z": "#3D4048", "+": "#E8E8EE", "Q": "#FFFFFF"}),
    ("bleu-klein", "une tenue bleu Klein",
     "En 1960, Yves Klein dépose la formule de son bleu outremer sous enveloppe Soleau. Il peignait aussi avec des modèles nus enduits de bleu. Estimez-vous habillé.",
     "etincelle",
     {"!": "#001E8C", "X": "#002FA7", "*": "#3D63D9", "~": "#001257", "Z": "#001E8C", "+": "#F2C14E", "Q": "#FFE79A"}),
    ("pyjama-rayures", "un pyjama à rayures",
     "Le mot pyjama vient de l'hindi pāy-jāma, « vêtement de jambes », rapporté par les Britanniques. Vous en avez désormais un, en plein jour.",
     "sagesse",
     {"!": "#5D86C9", "X": "#A9C4EE", "*": "#FFFFFF", "~": "#5D86C9", "Z": "#A9C4EE", "+": "#FFFFFF", "Q": "#A9C4EE"}),
    ("blouse-tachee", "une blouse de labo tachée",
     "Marie Curie travaillait dans un hangar mal chauffé. Ses carnets sont encore radioactifs et se consultent avec une décharge. Votre blouse n'a que des taches de café.",
     "savoir",
     {"!": "#C9CED6", "X": "#F5F5F0", "*": "#FFFFFF", "~": "#7A5418", "Z": "#9A6534", "+": "#8E2424", "Q": "#B8862B"}),
    ("tenue-fluo", "une tenue vert fluo",
     "La fluorescence, décrite par George Stokes en 1852, réémet en visible la lumière ultraviolette. Sous une lampe UV, on vous verra depuis la rue d'en face.",
     "cosmos",
     {"!": "#5FBF00", "X": "#A6FF00", "*": "#E4FF8A", "~": "#3C7A00", "Z": "#5FBF00", "+": "#FF2BD6", "Q": "#FF8AEC"}),
    ("toge-pourpre", "une toge pourpre de travers",
     "Le pourpre de Tyr sortait de milliers de murex écrasés : à Rome, il était réservé aux puissants. Vous l'avez, mais l'IA l'a mise à l'envers.",
     "eloquence",
     {"!": "#5E1440", "X": "#8E2466", "*": "#C25A94", "~": "#F2C14E", "Z": "#FFE79A", "+": "#F2C14E", "Q": "#FFE79A"}),
]


def donnees():
    return [{"id": i, "nom": {"fr": n}, "notice": {"fr": t}, "theme": th, "couleurs": c} for i, n, t, th, c in TENUES]
