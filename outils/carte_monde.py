"""Fond de carte du monde pour les leçons (les lieux cités dans les masterclass sont pointés dessus).

Source : Natural Earth, terres au 1:50 000 000 (domaine public), dans la version TopoJSON du paquet npm
world-atlas 2.0.2 (fichier land-50m.json). Le fichier est lu comme donnée, aucun code du paquet n'est exécuté.

    npm pack world-atlas@2.0.2 && tar xzf world-atlas-2.0.2.tgz
    python3 outils/carte_monde.py package/land-50m.json

Écrit packs/socle/donnees/skills.json › carte : une grille équirectangulaire de 0,25° (1440 × 720 pixels),
1 = terre. Chaque ligne est codée en longueurs de plages alternées, en base 36, séparées par des points,
la première plage étant de la mer (elle peut valoir 0).
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

RACINE = Path(__file__).resolve().parent.parent
PAS = 0.25
SUR = 4  # suréchantillonnage : un pixel est terre si plus de la moitié de sa surface l'est


def base36(n):
    c = "0123456789abcdefghijklmnopqrstuvwxyz"
    s = ""
    while True:
        n, r = divmod(n, 36)
        s = c[r] + s
        if not n:
            return s


def anneaux(topo):
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for a in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in a:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    terre = topo["objects"]["land"]
    geoms = terre["geometries"] if terre["type"] == "GeometryCollection" else [terre]
    for g in geoms:
        for poly in g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]:
            for k, ring in enumerate(poly):
                pts = []
                for i in ring:
                    p = arcs[i] if i >= 0 else arcs[~i][::-1]
                    pts.extend(p if not pts else p[1:])
                yield k == 0, pts


def raster(topo):
    w, h = int(360 / PAS), int(180 / PAS)
    im = Image.new("L", (w * SUR, h * SUR), 0)
    d = ImageDraw.Draw(im)
    for plein, r in anneaux(topo):
        # longitudes déroulées : un anneau qui franchit l'antiméridien reste d'un seul tenant
        u = [r[0]]
        for lon, lat in r[1:]:
            while lon - u[-1][0] > 180:
                lon -= 360
            while lon - u[-1][0] < -180:
                lon += 360
            u.append((lon, lat))
        if abs(u[-1][0] - u[0][0]) > 180:  # l'anneau fait le tour d'un pôle (Antarctique) : on le ferme par ce pôle
            pole = -90 if sum(p[1] for p in u) < 0 else 90
            u += [(u[-1][0], pole), (u[0][0], pole)]
        for dec in (-360, 0, 360):
            pts = [((lon + dec + 180) / PAS * SUR, (90 - lat) / PAS * SUR) for lon, lat in u]
            if len(pts) > 2:
                d.polygon(pts, fill=255 if plein else 0)
    im = im.resize((w, h), Image.BOX)
    px = im.load()
    lignes = []
    for y in range(h):
        plages, cur, n = [], 0, 0
        for x in range(w):
            v = 1 if px[x, y] >= 128 else 0
            if v == cur:
                n += 1
            else:
                plages.append(n)
                cur, n = v, 1
        plages.append(n)
        lignes.append(".".join(base36(p) for p in plages))
    return {"pas": PAS, "largeur": w, "hauteur": h,
            "origine": "Natural Earth, terres 1:50m (domaine public), via world-atlas 2.0.2",
            "lignes": lignes}


def main():
    topo = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    chemin = RACINE / "packs" / "socle" / "donnees" / "skills.json"
    d = json.loads(chemin.read_text(encoding="utf-8"))
    d["carte"] = raster(topo)
    chemin.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("carte :", d["carte"]["largeur"], "×", d["carte"]["hauteur"], ",", sum(len(l) for l in d["carte"]["lignes"]), "caractères")


if __name__ == "__main__":
    main()
