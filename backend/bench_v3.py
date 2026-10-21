import bench_decision
import bench_llm
import llm
from decision_v3 import decider

SCENARIOS = bench_decision.SCENARIOS + [
    ("Malade, convaincue, confiante (non réglé)",
     dict(bulletin=4, etat="I", puits=0.3, contact=0.9, confiance=0.9,
          souvenirs=[(10, "Bram semble malade (École)")]),
     lambda c: c == "Maison", "rester à la Maison"),
]


def main():
    noms = llm.modeles()
    if noms is None:
        print("Ollama ne répond pas. Lancez l'application Ollama.")
        return
    if llm.MODELE not in noms:
        print(f"Modèle {llm.MODELE} absent. Installés : {noms}")
        return
    print(f"Modèle testé : {llm.MODELE}   (variante v3)\n")
    total = bons = echecs = 0
    durees = []
    for nom, params, verif, attendu in SCENARIOS:
        m, ilse = bench_llm.preparer(**params)
        choix = []
        for k in range(4):
            rep = decider(m, ilse, k=k)
            durees.append(rep["ms"])
            total += 1
            if not rep["ok"]:
                echecs += 1
                choix.append("échec")
                continue
            choix.append(rep["choix"])
            bons += verif(rep["choix"])
        conformes = sum(1 for c in choix if c != "échec" and verif(c))
        print(f"{nom:<44} attendu : {attendu:<32} {conformes}/4   {choix}")
    print(f"\n=> conformes {bons}/{total}   échecs de format {echecs}   "
          f"durée moyenne d'une décision {sum(durees) / len(durees) / 1000:.1f} s")


if __name__ == "__main__":
    main()
