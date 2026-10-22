import sys

import bench_decision
import bench_llm
import llm
from ablation_rag import base_filtree
from decision_rag import decider
from rag_agents import recuperer
from rag_confiance import texte_documents_confiance

CONDITIONS = [("tous + confiance", None), ("vrais + confiance", {"vrai"})]


def main():
    noms = llm.modeles()
    if noms is None:
        print("Ollama ne répond pas. Lancez l'application Ollama.")
        return
    if llm.MODELE not in noms:
        print(f"Modèle {llm.MODELE} absent. Installés : {noms}")
        return
    print(f"Modèle : {llm.MODELE}   documents présentés avec la confiance de l'agent\n")
    resultats = {}
    for nom_cond, verites in CONDITIONS:
        base = base_filtree(verites)
        for nom, params, verif, attendu in bench_decision.SCENARIOS:
            m, ilse = bench_llm.preparer(**params)
            docs = texte_documents_confiance(recuperer(base, ilse, m.tour + 1), ilse)
            reps = [decider(m, ilse, docs, k=k) for k in range(4)]
            choix = [r["choix"] if r["ok"] else "échec" for r in reps]
            resultats[(nom_cond, nom)] = (choix, sum(1 for c in choix if c != "échec" and verif(c)))
        print(f"... condition « {nom_cond} » terminée", flush=True)

    conds = [c[0] for c in CONDITIONS]
    print("\nM = nombre de « Maison », P = nombre de « Puits » (sur 4 ordres)\n")
    print(f"{'situation':<42}" + "".join(f"{c:<20}" for c in conds))
    totaux = {c: [0, 0, 0] for c in conds}
    for nom, *_ in bench_decision.SCENARIOS:
        ligne = f"{nom:<42}"
        for c in conds:
            choix, bons = resultats[(c, nom)]
            m_, p_ = choix.count("Maison"), choix.count("Puits")
            totaux[c][0] += m_
            totaux[c][1] += p_
            totaux[c][2] += bons
            ligne += f"{'M%d P%d' % (m_, p_):<20}"
        print(ligne)
    print(f"{'TOTAL Maison / Puits / conformes':<42}" + "".join(
        f"{'%d / %d / %d' % tuple(totaux[c]):<20}" for c in conds))
    print("\nRepères de la mesure précédente (sans confiance) : sans documents 4/1/26, tous 12/2/22, vrais 32/0/20.")


if __name__ == "__main__":
    main()
