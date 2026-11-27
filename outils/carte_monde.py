"""Fond de carte du monde pour les leçons : les lieux cités dans les masterclass y sont pointés (Victor, 2026-11-27).

Source : Natural Earth (domaine public), échelle 1:10 000 000, fichiers GeoJSON du dépôt nvkelso/natural-earth-vector :
terres, lacs, fleuves, frontières terrestres, pays (noms et points d'étiquette), villes. Lus comme données.

    python3 outils/carte_monde.py DOSSIER     (DOSSIER contient les ne_10m_*.geojson)

Écrit data/carte.json, chargé par l'interface seulement quand une leçon montre une carte :
  - terrain : une ligne par rangée de la grille équirectangulaire (pas en degrés), en plages « classe + longueur en
    base 36 » séparées par des points ; classes 0 mer, 1 terre, 2 lac ;
  - traits : même codage ; 0 rien, 1 frontière, 2 fleuve (seulement sur la terre) ;
  - pays : [code, nom fr, nom en, longitude, latitude, rang d'étiquette, [o, s, e, n] du gros plan, autres noms fr,
    autres noms en, numéros des parties, nom fr non lié, nom en non lié] (« non lié » : nom trop ambigu pour devenir
    un lien dans les leçons, comme Maurice ou Niger) ; le rang (MIN_LABEL de Natural Earth) au-delà de 5 n'est pas écrit sur les cartes ;
  - etats : grille de 0,2° (codage « numéro+1.longueur » en base 36) : à quel pays (rang dans `pays`) appartient
    chaque pixel ; sert à surligner le pays qu'on touche dans une leçon ;
  - villes : [nom fr, nom en, longitude, latitude, rang] (rang petit = plus important).
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

RACINE = Path(__file__).resolve().parent.parent
PAS = 0.1
SUR = 4  # suréchantillonnage des surfaces : un pixel prend la classe qui couvre plus de la moitié de sa surface
FLEUVES_RANG = 6   # fleuves de rang Natural Earth ≤ 6 (les grands)
VILLES_RANG = 4    # villes de rang ≤ 4
PAYS_RANG = 5
PAS_ETATS = 0.2
# Autres noms sous lesquels un pays est cité dans les leçons ; noms trop ambigus pour être liés (prénoms, fleuves, villes).
ALIAS = {"CHN": (["Chine"], ["China"]), "USA": ([], ["United States", "USA"]), "CZE": (["République tchèque"], []),
         "VNM": (["Vietnam", "Viêtnam"], []), "GBR": (["Grande-Bretagne"], ["Britain", "Great Britain", "UK"]),
         "MMR": ([], ["Burma"]), "TLS": ([], ["Timor-Leste"]), "CIV": ([], ["Côte d'Ivoire"])}
AMBIGUS = {"Maurice", "Dominique", "Grenade", "Jersey", "Guernesey", "Niger", "Salvador", "Saint-Martin", "Jordan",
           "Georgia", "Chad", "Guernsey", "Saint Martin", "Sint Maarten"}
# Le Royaume-Uni est découpé en ses quatre nations, souvent citées seules.
PARTIES = {"GBR": ["ENG", "SCT", "WLS", "NIR"]}
W, H = int(360 / PAS), int(180 / PAS)


def b36(n):
    c, s = "0123456789abcdefghijklmnopqrstuvwxyz", ""
    while True:
        n, r = divmod(n, 36)
        s = c[r] + s
        if not n:
            return s


def lire(dossier, nom):
    return json.loads((Path(dossier) / f"{nom}.geojson").read_text(encoding="utf-8"))["features"]


def derouler(r):
    """Longitudes déroulées : un tracé qui franchit l'antiméridien reste d'un seul tenant."""
    u = [tuple(r[0][:2])]
    for lon, lat in (p[:2] for p in r[1:]):
        while lon - u[-1][0] > 180:
            lon -= 360
        while lon - u[-1][0] < -180:
            lon += 360
        u.append((lon, lat))
    return u


def polygones(features):
    for f in features:
        g = f["geometry"]
        if not g:
            continue
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            for k, ring in enumerate(poly):
                yield k == 0, ring


def surface(features, ech):
    im = Image.new("L", (W * ech, H * ech), 0)
    d = ImageDraw.Draw(im)
    for plein, r in polygones(features):
        u = derouler(r)
        if abs(u[-1][0] - u[0][0]) > 180:  # l'anneau fait le tour d'un pôle (Antarctique) : on le ferme par ce pôle
            pole = -90 if sum(p[1] for p in u) < 0 else 90
            u += [(u[-1][0], pole), (u[0][0], pole)]
        for dec in (-360, 0, 360):
            pts = [((lon + dec + 180) / PAS * ech, (90 - lat) / PAS * ech) for lon, lat in u]
            if len(pts) > 2:
                d.polygon(pts, fill=255 if plein else 0)
    return im.resize((W, H), Image.BOX) if ech > 1 else im


def lignes(features, garder=lambda p: True):
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    for f in features:
        g = f["geometry"]
        if not g or not garder(f["properties"]):
            continue
        for l in g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]:
            u = derouler(l)
            for dec in (-360, 0, 360):
                pts = [((lon + dec + 180) / PAS + .5, (90 - lat) / PAS + .5) for lon, lat in u]
                d.line(pts, fill=255, width=1)
    return im


def coder(grille):
    out = []
    for y in range(H):
        rang, x = [], 0
        while x < W:
            c, x1 = grille(x, y), x + 1
            while x1 < W and grille(x1, y) == c:
                x1 += 1
            rang.append(f"{c}{b36(x1 - x)}")
            x = x1
        out.append(".".join(rang))
    return out


def aire(r):
    return abs(sum(r[i][0] * r[i - 1][1] - r[i - 1][0] * r[i][1] for i in range(len(r)))) / 2


def pays_et_etats(dossier):
    """Les pays (Natural Earth, admin 0) et la grille qui dit à quel pays appartient chaque pixel."""
    unites = {f["properties"]["GU_A3"]: f for f in lire(dossier, "ne_10m_admin_0_map_units")}
    entrees, formes = [], []  # formes : (code, polygones extérieurs)
    for f in lire(dossier, "ne_10m_admin_0_countries"):
        p = f["properties"]
        code = p["ADM0_A3"]
        if not p.get("NAME_FR") or p.get("LABEL_X") is None or not f["geometry"]:
            continue
        g = f["geometry"]
        polys = [poly[0] for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]])]
        entrees.append((code, p, polys))
    for code, parts in PARTIES.items():
        for gu in parts:
            f = unites[gu]
            g = f["geometry"]
            entrees.append((gu, f["properties"], [poly[0] for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]])]))
    pays = []
    index = {}
    for code, p, polys in entrees:
        # Gros plan : le plus grand morceau (en Europe pour la France, pas la Guyane), plus les morceaux à moins de 3° de lui
        u = [derouler(r) for r in polys]
        grand = max(u, key=aire)
        o, s, e, n = min(x for x, _ in grand), min(y for _, y in grand), max(x for x, _ in grand), max(y for _, y in grand)
        for r in u:
            ro, rs, re_, rn = min(x for x, _ in r), min(y for _, y in r), max(x for x, _ in r), max(y for _, y in r)
            if ro > e + 3 or re_ < o - 3 or rs > n + 3 or rn < s - 3:
                continue
            o, s, e, n = min(o, ro), min(s, rs), max(e, re_), max(n, rn)
        fr = [] if p["NAME_FR"] in AMBIGUS else [p["NAME_FR"]]
        en = [] if (p.get("NAME_EN") or p["NAME"]) in AMBIGUS else [p.get("NAME_EN") or p["NAME"]]
        a = ALIAS.get(code, ([], []))
        index[code] = len(pays)
        pays.append([code, p["NAME_FR"], p.get("NAME_EN") or p["NAME"], round(p["LABEL_X"], 2), round(p["LABEL_Y"], 2),
                     round(p.get("MIN_LABEL") or 9, 1), [round(o, 1), round(s, 1), round(e, 1), round(n, 1)],
                     [x for x in fr[1:] + a[0]], [x for x in en[1:] + a[1]], [], not fr, not en])
        formes.append((code, u))
    for code, parts in PARTIES.items():
        pays[index[code]][9] = [index[g] for g in parts]
    # La grille : les grands pays d'abord, les petits par-dessus (une enclave reste visible dans le pays qui l'entoure).
    w, h = int(360 / PAS_ETATS), int(180 / PAS_ETATS)
    im = Image.new("I", (w, h), 0)
    d = ImageDraw.Draw(im)
    tracer = [(aire(r), index[code], r) for code, u in formes if not PARTIES.get(code) for r in u]
    for _, i, r in sorted(tracer, key=lambda t: -t[0]):
        if abs(r[-1][0] - r[0][0]) > 180:
            pole = -90 if sum(p[1] for p in r) < 0 else 90
            r = r + [(r[-1][0], pole), (r[0][0], pole)]
        for dec in (-360, 0, 360):
            pts = [((lon + dec + 180) / PAS_ETATS, (90 - lat) / PAS_ETATS) for lon, lat in r]
            if len(pts) > 2:
                d.polygon(pts, fill=i + 1)
    px = im.load()
    lignes_e = []
    for y in range(h):
        rang, x = [], 0
        while x < w:
            c, x1 = px[x, y], x + 1
            while x1 < w and px[x1, y] == c:
                x1 += 1
            rang += [b36(c), b36(x1 - x)]
            x = x1
        lignes_e.append(".".join(rang))
    return pays, lignes_e


def main():
    dossier = sys.argv[1]
    terre = surface(lire(dossier, "ne_10m_land"), SUR).load()
    lacs = surface(lire(dossier, "ne_10m_lakes"), SUR).load()
    front = lignes(lire(dossier, "ne_10m_admin_0_boundary_lines_land")).load()
    fleuves = lignes(lire(dossier, "ne_10m_rivers_lake_centerlines"),
                     lambda p: p.get("featurecla") == "River" and (p.get("scalerank") or 99) <= FLEUVES_RANG).load()

    def classe(x, y):
        return 0 if terre[x, y] < 128 else (2 if lacs[x, y] >= 128 else 1)

    def trait(x, y):
        if classe(x, y) != 1:
            return 0
        return 1 if front[x, y] else (2 if fleuves[x, y] else 0)

    pays, etats = pays_et_etats(dossier)
    villes = []
    for f in lire(dossier, "ne_10m_populated_places"):
        p = f["properties"]
        if p.get("SCALERANK") is not None and p["SCALERANK"] <= VILLES_RANG:
            lon, lat = f["geometry"]["coordinates"][:2]
            villes.append([p.get("NAME_FR") or p["NAME"], p.get("NAME_EN") or p["NAME"], round(lon, 2), round(lat, 2), p["SCALERANK"], -(p.get("POP_MAX") or 0)])
    carte = {"pas": PAS, "largeur": W, "hauteur": H,
             "origine": "Natural Earth 1:10m (domaine public) : terres, lacs, fleuves, frontières, pays, villes",
             "terrain": coder(classe), "traits": coder(trait), "pays": pays, "pas_etats": PAS_ETATS, "etats": etats,
             "villes": [v[:5] for v in sorted(villes, key=lambda v: (v[4], v[5], v[0]))]}
    chemin = RACINE / "data" / "carte.json"
    chemin.write_text(json.dumps(carte, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"carte : {W} × {H}, {len(pays)} pays, {len(villes)} villes, {chemin.stat().st_size // 1024} Ko")


if __name__ == "__main__":
    main()
