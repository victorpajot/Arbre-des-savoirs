"""Les QCM qui se trahissent : la bonne réponse se reconnaît à sa forme plutôt qu'à son sens (Victor, 2026-11-25).

    python3 outils/audit_qcm.py                 bilan par pack
    python3 outils/audit_qcm.py PACK [--tout]   les QCM de ce pack dont la bonne réponse est nettement la plus longue
                                                (--tout : y compris ceux qui ont déjà des leurres en réserve)

Une bonne réponse « nettement la plus longue » (30 % de plus que le plus long leurre) se devine sans rien savoir. Le
remède : des leurres en réserve (champ `leurres` de la question) aussi longs et aussi précis qu'elle ; le jeu prend à
chaque passage ceux qui lui ressemblent le plus (M.varierQuestion).
"""
import json
import sys
from pathlib import Path

PACKS = Path(__file__).resolve().parent.parent / "packs"
SEUIL = 1.3


def trahit(q):
    if q.get("type") != "qcm":
        return False
    bonne = len(q["choix"][q["reponse"]]["fr"])
    autres = [len(c["fr"]) for i, c in enumerate(q["choix"]) if i != q["reponse"]] + [len(c["fr"]) for c in q.get("leurres", [])]
    proches = sorted(autres, key=lambda n: abs(n - bonne))[:len(q["choix"]) - 1]
    return bonne > SEUIL * max(proches)


def questions(pack):
    f = PACKS / pack / "questions.json"
    if not f.exists():
        return []
    d = json.loads(f.read_text(encoding="utf-8"))
    return d if isinstance(d, list) else d.get("questions", [])


def main(args):
    if not args:
        total = 0
        for p in sorted(x.name for x in PACKS.iterdir() if x.is_dir()):
            qs = [q for q in questions(p) if q.get("type") == "qcm"]
            n = sum(trahit(q) for q in qs)
            total += n
            if qs:
                print(f"{p:20} {n:4} / {len(qs)} QCM trahis par la longueur")
        print(f"{'total':20} {total:4}")
        return 0
    for q in questions(args[0]):
        if trahit(q) or ("--tout" in args and q.get("leurres")):
            print(json.dumps({"id": q["id"], "enonce": q["enonce"]["fr"], "choix": [c["fr"] for c in q["choix"]],
                              "leurres": [c["fr"] for c in q.get("leurres", [])]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
