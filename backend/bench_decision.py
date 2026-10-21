import sys

import bench_llm
import llm
from decision_llm import decider

SCENARIOS = bench_llm.SCENARIOS + [
    ("Sceptique face aux bulletins",
     dict(bulletin=2, puits=0.3, contact=0.05, confiance=0.1),
     lambda c: c != "Maison", "sortir (ne croit pas au danger)"),
    ("Vu un malade au Puits, croit au puits",
     dict(bulletin=1, puits=0.8, contact=0.3, confiance=0.5,
          souvenirs=[(10, "Noa semble malade (Puits)")]),
     lambda c: c != "Puits", "éviter le Puits"),
    ("Épidémie grave mais méfiante",
     dict(bulletin=4, puits=0.3, contact=0.1, confiance=0.1),
     lambda c: c != "Maison", "sortir (se méfie du dispensaire)"),
]


def main():
    noms = llm.modeles()
    if noms is None:
        print("Ollama ne répond pas. Lancez l'application Ollama.")
        return
    if llm.MODELE not in noms:
        print(f"Modèle {llm.MODELE} absent. Installés : {noms}")
        return
    variantes = sys.argv[1:] or ["v1", "v2"]
    print(f"Modèle testé : {llm.MODELE}   (décision en deux temps)")
    for variante in variantes:
        print(f"\n--- Variante {variante} ---")
        total = bons = echecs = 0
        durees = []
        for nom, params, verif, attendu in SCENARIOS:
            m, ilse = bench_llm.preparer(**params)
            choix = []
            for k in range(4):
                rep = decider(m, ilse, variante=variante, k=k)
                durees.append(rep["ms"])
                total += 1
                if not rep["ok"]:
                    echecs += 1
                    choix.append("échec")
                    continue
                choix.append(rep["choix"])
                bons += verif(rep["choix"])
            conformes = sum(1 for c in choix if c != "échec" and verif(c))
            print(f"{nom:<42} attendu : {attendu:<32} {conformes}/4   {choix}")
        print(f"=> conformes {bons}/{total}   échecs de format {echecs}   "
              f"durée moyenne d'une décision {sum(durees) / len(durees) / 1000:.1f} s")


if __name__ == "__main__":
    main()
