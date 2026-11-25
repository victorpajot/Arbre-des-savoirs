"""Inscrire des leurres en réserve dans les QCM d'un pack, avec leur traduction (Victor, 2026-11-25).

    python3 outils/inscrire_leurres.py PACK fichier.json

fichier.json : {"id de question": [["leurre fr", "leurre en"], …], …}. Les leurres s'ajoutent au champ `leurres` de la
question (sans doublon, ni avec ses choix) ; leur traduction anglaise va dans packs/PACK/langues/en/questions.json.
Voir outils/audit_qcm.py pour trouver les QCM qui en ont besoin.
"""
import json
import sys
from pathlib import Path

PACKS = Path(__file__).resolve().parent.parent / "packs"


def ecrire(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main(pack, fichier):
    ajouts = json.loads(Path(fichier).read_text(encoding="utf-8"))
    fq = PACKS / pack / "questions.json"
    qs = json.loads(fq.read_text(encoding="utf-8"))
    liste = qs if isinstance(qs, list) else qs["questions"]
    par_id = {q["id"]: q for q in liste}
    fl = PACKS / pack / "langues" / "en" / "questions.json"
    trad = json.loads(fl.read_text(encoding="utf-8")) if fl.exists() else {}
    n = 0
    for qid, leurres in ajouts.items():
        q = par_id.get(qid)
        if not q or q.get("type") != "qcm":
            sys.exit(f"{qid} : pas un QCM du pack {pack}")
        deja = {c["fr"] for c in q["choix"]} | {c["fr"] for c in q.get("leurres", [])}
        neufs = []
        for fr, en in leurres:
            if fr in deja:
                continue
            deja.add(fr)
            neufs.append({"fr": fr})
            if en:
                trad[fr] = en
        if neufs:
            # Le champ se range juste après les choix.
            nq = {}
            for k, v in q.items():
                if k == "leurres":
                    continue
                nq[k] = v
                if k == "choix":
                    nq["leurres"] = q.get("leurres", []) + neufs
            q.clear(); q.update(nq)
            n += len(neufs)
    ecrire(fq, qs)
    if trad:
        fl.parent.mkdir(parents=True, exist_ok=True)
        ecrire(fl, trad)
    print(f"{n} leurres inscrits dans {pack}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
