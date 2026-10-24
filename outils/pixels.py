"""Pixel art du jeu : objets du cabinet de curiosités (16 × 16) et calques de l'avatar (20 × 24).

Chaque image est une liste de lignes de même longueur. Un caractère = un pixel, « . » = transparent,
les autres caractères renvoient à PALETTE. Ce format se lit tel quel dans n'importe quel moteur
(une texture se reconstruit pixel par pixel), il n'y a aucune image binaire à maintenir.
"""

PALETTE = {
    "k": "#1E1A2B", "n": "#2B2B33", "w": "#FFFFFF", "l": "#E3E3E8", "g": "#9AA0A8", "G": "#5D6470",
    "z": "#C9CED6", "Z": "#8D939E", "y": "#F2C14E", "Y": "#B8862B", "b": "#9A6534", "B": "#5E3B1C",
    "r": "#D94141", "R": "#8E2424", "o": "#E8873A", "O": "#A95A1F", "e": "#4CAF50", "E": "#2E7D32",
    "c": "#8FD8F2", "C": "#2A6F99", "u": "#3D63D9", "U": "#24408F", "p": "#9B59D0", "P": "#5E2F8A",
    "s": "#F2C9A0", "S": "#D9A07A", "m": "#B5523B", "h": "#6B4226", "H": "#3E2614",
    "v": "#F7EBD0", "V": "#D8C49A", "q": "#F4F4F4", "Q": "#C9C9D1", "x": "#F2F2EE",
}


def _asch():
    lignes = ["................", ".kkkkkkkkkkkkkk.", ".kwwwwwwwwwwwwk."]
    for r in range(3, 13):
        rangee = ["w"] * 12
        if 3 <= r <= 11:
            rangee[1] = "n"
            rangee[8] = "n"
        if 7 <= r <= 11:
            rangee[6] = "n"
        if 5 <= r <= 11:
            rangee[10] = "n"
        lignes.append(".k" + "".join(rangee) + "k.")
    lignes += [".kwwwwwwwwwwwwk.", ".kkkkkkkkkkkkkk.", "................"]
    return lignes


OBJETS = {
    "lunette-galilee": [
        "................", "..............kk", ".............kyk", "............kbYk",
        "...........kbbk.", "..........kbbk..", ".........kYbk...", "........kbbk....",
        ".......kbbk.....", "......kbYk......", ".....kbbk.......", "....kcbk........",
        "....kkk.........", ".....kBk........", "....kB.Bk.......", "...kB...Bk......",
    ],
    "prisme-newton": [
        "................", "................", "......kk........", ".....kcck.......",
        ".....kcck.......", "....kcccck......", "....kcwcck...rrr", "wwwkccwccckrrooo",
        "...kcccwcccooyyy", "..kcccccwccyyeee", "..kcccccccceeuuu", ".kccccccccccuu..",
        ".kkkkkkkkkkkkp..", "................", "................", "................",
    ],
    "pomme-newton": [
        "................", ".......kk.......", "........kB......", "......kkBkeek...",
        "....kkrrkeEek...", "...krrrrrkkk....", "..krrwrrrrrrk...", "..krwrrrrrrrk...",
        "..krrrrrrrrrk...", "..krrrrrrrrRk...", "..krrrrrrrRRk...", "...krrrrrRRk....",
        "....krrRRRk.....", ".....kk.kk......", "................", "................",
    ],
    "pile-volta": [
        "................", "....kkkkkkkk....", "...kooooooook...", "...kzzzzzzzzk...",
        "...kVVVVVVVVk...", "...kooooooook...", "...kzzzzzzzzk...", "...kVVVVVVVVk...",
        "...kooooooook...", "...kzzzzzzzzk...", "...kVVVVVVVVk...", "...kooooooook...",
        "...kzzzzzzzzk...", "..kBBBBBBBBBBk..", "..kkkkkkkkkkkk..", "................",
    ],
    "bouteille-leyde": [
        ".......kk.......", "......kzzk......", "......kzzk......", ".......kk.......",
        ".......kZk......", ".....kkkZkkk....", "....kBBBZBBBk...", "....kcccZccck...",
        "....kcccZccck...", "....kcccZccck...", "....kzzzZzzzk...", "....kzzzZzzzk...",
        "....kzzzzzzzk...", "....kZzzzzzZk...", ".....kkkkkkk....", "................",
    ],
    "cerf-volant-franklin": [
        "........k.......", ".......krk......", "......krrrk.....", ".....krrkrrk....",
        "....krrrkrrrk...", "...kkkkkkkkkkk..", "....kwwwkwwwk...", ".....kwwkwwk....",
        "......kwkwk.....", ".......kkk......", "........k.......", ".........k......",
        "..........k.....", "..........kyk...", "..........yky...", "...........y....",
    ],
    "bobine-faraday": [
        "................", "...y.......y....", "..kkkkkkkkkkk...", ".kZoooooooooZk..",
        ".kZoOoOoOoOoZk..", ".kZoooooooooZk..", ".kZoOoOoOoOoZk..", ".kZoooooooooZk..",
        "..kkkkkkkkkkk...", "................", "...kkkkkkkkkk...", "...krrrrkuuuuk..",
        "...krrrrkuuuuk..", "...kkkkkkkkkk...", "................", "................",
    ],
    "ampoule-edison": [
        "......kkkk......", ".....kwwwwk.....", "....kwwlllwk....", "...kwwlyylwwk...",
        "...kwwykkywwk...", "...kwwyllywwk...", "...kwwyllywwk...", "....kwlyylwk....",
        ".....kwyywk.....", "......kyyk......", "......kZZk......", ".....kzzzzk.....",
        ".....kZZZZk.....", ".....kzzzzk.....", "......kZZk......", ".......kk.......",
    ],
    "tableau-mendeleiev": [
        "................", "................", "................", "e..............p",
        "ee..........yyyp", "ee..........yyyp", "eeuuuuuuuuuuyyyp", "eeuuuuuuuuuuyyyp",
        "eeuuuuuuuuuuyyyp", "eeuuuuuuuuuuyyyp", "................", "...oooooooooooo.",
        "...rrrrrrrrrrrr.", "................", "................", "................",
    ],
    "balance-lavoisier": [
        "......kyyk......", ".kkkkkkyykkkkkk.", "..k....yy....k..", "..k....yy....k..",
        ".k.k...yy...k.k.", "k...k..yy..k...k", "kyyyk..yy..kyyyk", ".kkk...yy...kkk.",
        ".......yy.......", ".......yy.......", "......kYYk......", ".....kYYYYk.....",
        "....kkkkkkkk....", "................", "................", "................",
    ],
    "papier-tournesol": [
        "................", "........kv......", "........kv......", "........kv......",
        "..k.....kv....k.", "..kl....kv...lk.", "..kl....kr...lk.", "..kl....kr...lk.",
        "..krrrrrkrrrrrk.", "..krrrrrrrrrrrk.", "..krrrrrrrrrrrk.", "..kRrrrrrrrrrRk.",
        "...kkkkkkkkkkk..", "................", "................", "................",
    ],
    "modele-moleculaire": [
        "................", "................", "..kkk......kkk..", ".kwwwk....kwwwk.",
        ".kwwwkG..Gkwwwk.", "..kkk..GG..kkk..", ".......GG.......", ".....kkkkkk.....",
        "....krrrrrrk....", "....krwrrrrk....", "....krrrrrrk....", "....krrrrRRk....",
        ".....kkkkkk.....", "................", "................", "................",
    ],
    "alambic": [
        "................", ".....kkkk.......", "....koooOk......", "....kooOk.kkkk..",
        "...kkookkkoooOk.", "..kkoooooOkk..k.", ".koooooooooOk.ok", ".kooyooooooOk.ok",
        ".koooooooooOk.ok", ".kOoooooooOOk.kk", "..kOOOOOOOOk.kck", "...kkkkkkkk..kck",
        "...kBBBBBBk..kck", "..kBrrorrBBk.kkk", "..kkkkkkkkkk....", "................",
    ],
    "microscope-hooke": [
        "................", "......kk........", "......kyk.......", "......kYyk......",
        ".....kbbbk......", ".....kbybk......", ".....kbbbk......", ".....kbybk..kk..",
        "......kbk..kBk..", "......kGk.kBk...", "....kkkkkkBk....", "....kzzzzkk.....",
        "......kGkBk.....", "......kGkBk.....", "...kkkkkkkkkk...", "...kBBBBBBBBk...",
    ],
    "carnet-darwin": [
        "................", "..kkkkkkkkkkkk..", "..kBvvvvvvvvvk..", "..kBvvvvvnvnvk..",
        "..kBvvnvvnnvvk..", "..kBvvvnnvnvvk..", "..kBvvvvnnvvvk..", "..kBvvvvnvvvvk..",
        "..kBvvvvnvvvvk..", "..kBvvvvvvvvvk..", "..kBvnvnnvnnvk..", "..kBvvvvvvvvvk..",
        "..kBvnnvnvnnvk..", "..kBvvvvvvvvvk..", "..kkkkkkkkkkkk..", "................",
    ],
    "pois-mendel": [
        "................", "................", "..............E.", ".............kE.",
        "....kkkkkkkkkk..", "..kkEEEEEEEEEEk.", ".kEeeEeeEeeEeEk.", ".kEeeEeeEeeEeEk.",
        "..kEEEEEEEEEEk..", "...kkkkkkkkkk...", "................", "................",
        "................", "................", "................", "................",
    ],
    "boite-petri": [
        "................", ".....kkkkkk.....", "...kkllllllkk...", "..kllllllllllk..",
        ".klyylllllllylk.", ".kylllllllllyyk.", ".kyllleeeellllk.", ".kllleEeeelllyk.",
        ".kyllleeeelllyk.", ".kylllleelllyyk.", ".kyylllllllllyk.", ".klyyllllllyylk.",
        "..kllyyllyyllk..", "...kkllllllkk...", ".....kkkkkk.....", "................",
    ],
    "boulier": [
        "................", ".kkkkkkkkkkkkkk.", ".kBBBBBBBBBBBBk.", ".kBrrrgggggguBk.",
        ".kB..........Bk.", ".kBggrrrgggggBk.", ".kB..........Bk.", ".kBuuuuggggggBk.",
        ".kB..........Bk.", ".kBggggggrrrrBk.", ".kB..........Bk.", ".kBrrggggggguBk.",
        ".kBBBBBBBBBBBBk.", ".kkkkkkkkkkkkkk.", "................", "................",
    ],
    "des-pascal": [
        "................", "................", ".kkkkkkk........", ".kwwwwwk........",
        ".kwnwwwk........", ".kwwnwwk.kkkkkkk", ".kwwwnwk.kwwwwwk", ".kwwwwwk.kwnwnwk",
        ".kkkkkkk.kwwwwwk", ".........kwnwnwk", ".........kwwwwwk", ".........kkkkkkk",
        "................", "................", "................", "................",
    ],
    "compas-euclide": [
        ".......kk.......", "......kyyk......", "......kyyk......", ".......kk.......",
        "......kGGk......", ".....kGkkGk.....", ".....kGk.kGk....", "....kGk...kGk...",
        "....kGk...kGk...", "...kGk.....kGk..", "...kGk.....kGk..", "..kGk.......kGk.",
        "..kzk.......kGk.", "...k.........kok", "................", "................",
    ],
    "ardoise-boole": [
        "................", ".kkkkkkkkkkkkkk.", ".kbbbbbbbbbbbbk.", ".kbnnnnnnnnnnbk.",
        ".kbnnnnwnnnnnbk.", ".kbnnnwnwnnnnbk.", ".kbnnwnnnwnnnbk.", ".kbnnnnnnnnnnbk.",
        ".kbnwnwwwnwnnbk.", ".kbnwnwnwnwnnbk.", ".kbnwnwwwnwnnbk.", ".kbnnnnnnnnnnbk.",
        ".kbbbbbbbbbbbbk.", ".kkkkkkkkkkkkkk.", "................", "................",
    ],
    "machine-joule": [
        "................", ".kkk............", "kzzzk...........", "kzkzkkkkkkkk....",
        "kzzzk......k....", ".kkk.......k....", "..y........k....", "..y.....kkkkkkk.",
        "..y.....kcckcck.", "..y.....kckkkck.", ".kkk....kcckcck.", ".kGk....kcckcck.",
        ".kGk....kccccck.", ".kkk....kkkkkkk.", "................", "................",
    ],
    "diapason": [
        "................", "....kk....kk....", "....kzk..kzk....", "....kzk..kzk....",
        "..c.kzk..kzk.c..", ".c..kzk..kzk..c.", "..c.kzk..kzk.c..", "....kzk..kzk....",
        "....kzk..kzk....", ".....kzkkzk.....", "......kzzk......", ".......kzk......",
        ".......kzk......", ".......kzk......", ".......kzk......", "......kZZZk.....",
    ],
    "metre-etalon": [
        "................", "................", "......kkkk......", "......kZZk......",
        "......kkkk......", "kkkkkkkkkkkkkkkk", "kyyyyyyyyyyyyyyk", "knyynyynyynyynyk",
        "knyyyyynyyyyynyk", "kyyyyyyyyyyyyyyk", "kkkkkkkkkkkkkkkk", "................",
        "................", "................", "................", "................",
    ],
    "plaque-hubble": [
        "................", ".kkkkkkkkkkkkkk.", ".knnnnnnnnnnnnk.", ".knwnnnnnnnwnnk.",
        ".knnnnnwnnnnnnk.", ".knnnnnnnnnnnnk.", ".knnnnnrrrnnwnk.", ".knnnnrnwnrnnnk.",
        ".knnnnnrrrnnnnk.", ".knwnnnnnnnnnnk.", ".knnnnnnnnnwnnk.", ".knnnwnnnnnnnnk.",
        ".kkkkkkkkkkkkkk.", "................", "................", "................",
    ],
    "rouleau-aristote": [
        "................", "................", "..kkkkkkkkkkkk..", ".kVVkvvvvvvkVVk.",
        ".kVVkvnnvnvkVVk.", ".kVVkvvvvvvkVVk.", ".kVVkvnvnnvkVVk.", ".kVVkvvvvvvkVVk.",
        ".kVVkvnnvnvkVVk.", ".kVVkvvvvvvkVVk.", ".kVVkvnvnnvkVVk.", ".kVVkvvvvvvkVVk.",
        "..kkkkkkkkkkkk..", "................", "................", "................",
    ],
    "cailloux-demosthene": [
        "................", "................", "................", "................",
        "................", "..........kkk...", ".........kzzlk..", ".........kzzzk..",
        "..........kkk...", "...kkk..........", "..kgllk...kkkk..", ".kgggggk.kGGlGk.",
        ".kggggGkkGGGGGk.", "..kkkkk.kkkkkk..", "................", "................",
    ],
    "cartes-wason": [
        "................", "................", "................", ".kkkkkkk.kkkkkkk",
        ".kwwwwwk.kwwwwwk", ".kwuuuwk.kwrrrwk", ".kwuwwwk.kwwwrwk", ".kwuuwwk.kwwrwwk",
        ".kwuwwwk.kwwrwwk", ".kwuuuwk.kwrwwwk", ".kwwwwwk.kwwwwwk", ".kkkkkkk.kkkkkkk",
        "................", "................", "................", "................",
    ],
    "roue-loterie": [
        ".......yy.......", ".....kkkkkk.....", "...kkrwrwrwkk...", "..krwrwrwrwrwk..",
        ".kwrwrwrwrwrwrk.", ".krwrwrwrwrwrwk.", "kwrwrwrkkwrwrwrk", "krwrwrkyykrwrwrk",
        "kwrwrwkyykwrwrwk", "krwrwrwkkrwrwrwk", ".kwrwrwrwrwrwrk.", ".krwrwrwrwrwrwk.",
        "..kwrwrwrwrwrk..", "...kkwrwrwrkk...", ".....kkkkkk.....", ".......kk.......",
    ],
    "cloche-pavlov": [
        "................", ".......kk.......", "......kyyk......", ".....kyyyyk.....",
        "....kyyyyyyk....", "....kyywyyyk....", "....kyyyyyyk....", "...kyywyyyyyk...",
        "...kyyyyyyyyk...", "..kyyyyyyyyyyk..", ".kyyyyyyyyyyyyk.", ".kYYYYYYYYYYYYk.",
        "..kkkkkkkkkkkk..", ".......kYk......", "........k.......", "................",
    ],
    "lignes-asch": _asch(),
    "fiche-ebbinghaus": [
        "................", "..kkkkkkkkkkkk..", "..kvvvvvvvvvvk..", "..kvnnnvnnnvvk..",
        "..kvvvvvvvvvvk..", "..kvnnvnnnvvvk..", "..kvvvvvvvvvvk..", "..kvnnnvnnvvvk..",
        "..kvvvvvvvvvvk..", "..kvnnvvnnnvvk..", "..kvvvvvvvvvvk..", "..kvvvvvvvvvvk..",
        "..kkkkkkkkkkkk..", "................", "................", "................",
    ],
    "sphere-armillaire": [
        "................", "......kkkk......", "....kkyyyykk....", "...kyykkkkyyk...",
        "..kyk.kuuk.kyk..", ".kyk.kuuuuk.kyk.", ".kyyyyyyyyyyyyk.", ".kyk.kuuuuk.kyk.",
        "..kyk.kuuk.kyk..", "...kyykkkkyyk...", "....kkyyyykk....", "......kkkk......",
        ".......kk.......", ".......kk.......", ".....kkYYkk.....", "....kYYYYYYk....",
    ],
    "pendule-foucault": [
        "................", "...kkkkkkkkkk...", "...kBBBBBBBBk...", "...kkkkkkkkkk...",
        ".......g........", ".......g........", ".......g........", ".......g........",
        ".......g........", ".......g........", "......kkkk......", ".....kyyyyk.....",
        ".....kyYYYk.....", "......kkkk......", "................", "vvVvvVvvVvvVvvVv",
    ],
}


# --- Avatar ----------------------------------------------------------------------
# Calques 20 × 24, superposés dans l'ordre : corps, tenue, cheveux, visage, tête.
# Dans les tenues, X = vêtement principal, Z = bas, Q = détail ; chaque rang choisit ses couleurs.

CORPS = [
    "....................", "....................", "......kkkkkkkk......", ".....kssssssssk.....",
    ".....kssssssssk.....", ".....kssssssssk.....", ".....kssnssnssk.....", ".....kssssssssk.....",
    ".....ksssmmsssk.....", "......kssssssk......", ".......kkkkkk.......", "........kssk........",
    "....................", "....................", "....................", "....................",
    "....................", "....................", "..kssk........kssk..", "....................",
    "....................", "....................", "....................", "....................",
]

SILHOUETTE = [
    "....kkkkXssXkkkk....", "...kXXXXXXXXXXXXk...", "..kXXkXXXXXXXXkXXk..", "..kXXkXXXXXXXXkXXk..",
    "..kXXkXXXXXXXXkXXk..", "..kXXkXXXXXXXXkXXk..", "..kssk XXXXXXXXkssk.", "...kk.kZZZZZZk.kk...",
    "......kZZkkZZk......", "......kZZkkZZk......", ".....knnnkknnnk.....", ".....kkkk..kkkk.....",
]


def tenue(details):
    """Silhouette de base (lignes 12 à 23) avec quelques pixels de détail par rang."""
    base = [l.replace(" ", "") for l in SILHOUETTE]
    base[6] = "..ksskXXXXXXXXkssk.."
    lignes = ["." * 20] * 12 + [list(l) for l in base]
    lignes = [list(l) if isinstance(l, str) else l for l in lignes]
    for (r, c), ch in details.items():
        lignes[r][c] = ch
    return ["".join(l) for l in lignes]


RANGS = [
    {"id": "etudiant", "nom": "Étudiant", "niveau_min": 0, "couleurs": {"X": "#3D63D9", "Z": "#2F3B59", "Q": "#F2C14E"},
     "tenue": tenue({(13, 8): "Q", (13, 11): "Q", (14, 9): "Q", (14, 10): "Q"})},
    {"id": "assistant", "nom": "Assistant", "niveau_min": 5, "couleurs": {"X": "#F4F4F4", "Z": "#2F3B59", "Q": "#3D63D9"},
     "tenue": tenue({(13, 12): "Q", (14, 12): "Q", (15, 7): "k", (16, 7): "k", (15, 12): "k", (16, 12): "k"})},
    {"id": "chercheur", "nom": "Chercheur", "niveau_min": 15, "couleurs": {"X": "#F4F4F4", "Z": "#5D6470", "Q": "#D94141"},
     "tenue": tenue({(13, 9): "Q", (13, 10): "Q", (14, 9): "Q", (14, 10): "Q", (15, 9): "Q", (15, 10): "Q", (14, 7): "u", (14, 12): "y"})},
    {"id": "professeur", "nom": "Professeur", "niveau_min": 30, "couleurs": {"X": "#7A5230", "Z": "#3B3B3B", "Q": "#E8DDC0"},
     "tenue": tenue({(13, 8): "Q", (13, 9): "Q", (13, 10): "Q", (13, 11): "Q", (14, 9): "r", (14, 10): "r", (15, 9): "r", (16, 3): "Q", (16, 16): "Q"})},
    {"id": "academicien", "nom": "Membre de l'Académie", "niveau_min": 50, "couleurs": {"X": "#2E6B3F", "Z": "#1E1E24", "Q": "#F2C14E"},
     "tenue": tenue({(13, 6): "Q", (13, 13): "Q", (14, 6): "Q", (14, 13): "Q", (15, 7): "Q", (15, 12): "Q", (16, 8): "Q", (16, 11): "Q",
                     (14, 3): "Q", (14, 16): "Q", (17, 3): "Q", (17, 16): "Q", (14, 9): "y", (16, 10): "y"})},
]

CHEVEUX = [
    "....................", "......kkkkkkkk......", ".....khhhhhhhhk.....", ".....khhhhhhhhk.....",
    ".....khhhhhhhsk.....", ".....khsssssssk.....",
] + ["." * 20] * 18

# Accessoires : emplacement « tete » (remplace les cheveux) ou « visage » (par-dessus).
ACCESSOIRES = {
    "coiffure-einstein": ("tete", [
        "...k.k..k..k..k.k...", "..kzkzkkzkkzkkzkzk..", ".kzzzzzzzzzzzzzzzzk.", ".kzzzzzzzzzzzzzzzzk.",
        "..kzzzzzzzzzzzzzzk..", "..kzzsssssssssszzk..", "..kzzk........kzzk..", "...kk..........kk...",
    ] + ["." * 20] * 16),
    "perruque-poudree": ("tete", [
        "....................", "......kkkkkkkk......", "....kkxxxxxxxxkk....", "...kxxxxxxxxxxxxk...",
        "...kxxkssssssskxk...", "...kxxksssssssskxk..", "...kxxk......kxxk...", "...kxxk......kxxk...",
        "...kxxk......kxxk...", "...kxxk......kxxk...", "....kkk......kkk....",
    ] + ["." * 20] * 13),
    "chapeau-alu": ("tete", [
        ".........kk.........", "........kzzk........", ".......kzZzzk.......", "......kzzzZzzk......",
        ".....kzzZzzzZzk.....", "....kkkkkkkkkkkk....", ".....khsssssshk.....",
    ] + ["." * 20] * 17),
    "haut-de-forme": ("tete", [
        "......kkkkkkkk......", "......knnnnnnk......", "......knnnnnnk......", "......kRRRRRRk......",
        "...kkkkkkkkkkkkkk...", ".....khsssssshk.....",
    ] + ["." * 20] * 18),
    "laurier": ("tete", [
        "....................", "......kkkkkkkk......", ".....khhhhhhhhk.....", "....eEhhhhhhhhEe....",
        "....kEeEeEeEeEeEk...", ".....khsssssssk.....",
    ] + ["." * 20] * 18),
    "bonnet-de-nuit": ("tete", [
        "..y.................", ".kyk................", "..kukkkkkk..........", "...kuuuuuukkkk......",
        "....kuuuuuuuuuk.....", ".....kqqqqqqqqk.....", ".....khsssssshk.....",
    ] + ["." * 20] * 17),
    "lunettes-rondes": ("visage", ["." * 20] * 5 + [
        "......kkk..kkk......", ".....kkck..kckk.....", "......kkk..kkk......",
    ] + ["." * 20] * 16),
    "besicles-franklin": ("visage", ["." * 20] * 6 + [
        ".....kkcckkcckk.....", "......kkk..kkk......",
    ] + ["." * 20] * 16),
    "lunettes-protection": ("visage", ["." * 20] * 5 + [
        ".....kkkkkkkkkk.....", ".....kcccckcccck....", ".....kkkkkkkkkk.....",
    ] + ["." * 20] * 16),
    "monocle": ("visage", ["." * 20] * 5 + [
        "..........kkk.......", "..........kck.......", "..........kkk.......", "............y.......",
        "............y.......",
    ] + ["." * 20] * 14),
    "moustache": ("visage", ["." * 20] * 7 + [
        ".......zzzzzz.......",
    ] + ["." * 20] * 16),
}


def verifier():
    for nom, img in OBJETS.items():
        assert len(img) == 16 and all(len(l) == 16 for l in img), (nom, [len(l) for l in img])
        assert set("".join(img)) <= set(PALETTE) | {"."}, (nom, set("".join(img)) - set(PALETTE))
    calques = [("corps", CORPS), ("cheveux", CHEVEUX)] + [(r["id"], r["tenue"]) for r in RANGS] + [(k, v[1]) for k, v in ACCESSOIRES.items()]
    for nom, img in calques:
        assert len(img) == 24 and all(len(l) == 20 for l in img), (nom, len(img), [len(l) for l in img])
        assert set("".join(img)) <= set(PALETTE) | set(".XZQ"), (nom, set("".join(img)) - set(PALETTE))
