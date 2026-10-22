import json
import os
import sys

import bench_decision
import bench_llm
import llm
from decision_rag import decider
from monde_rag import LOG
from rag_agents import BaseSimulation, recuperer, texte_documents

CONDITIONS = [
    ("sans documents", None, False),
    ("tous", None, True),
    ("vrais seulement", {"vrai"}, True),
    ("faux seulement", {"faux"}, True),
]


def base_filtree(verites):
    base = BaseSimulation()
    if verites is not None:
        base.docs = [d for d in base.docs if d["verite"] in verites]
    return base


def analyser_journal():
    if not os.path.exists(LOG):
        return
    with open(LOG, encoding="utf-8") as f:
        entrees = [json.loads(ligne) for ligne in f if ligne.strip()]
    llm_ok = [e for e in entrees if e["origine"] == "LLM"]
    courtes = [e for e in llm_ok if len(e["raison"].split()) <= 3]
    print(f"Journal existant : {len(courtes)}/{len(llm_ok)} raisons de 3 mots ou moins. Exemples :")
    for e in courtes[:3]:
        print(f"   tour {e['tour']} -> {e['choix']} : {e['raison']!r}")
    print()


def main():
    noms = llm.modeles()
    if noms is None:
        print("Ollama ne répond pas. Lancez l'application Ollama.")
        return
    if llm.MODELE not in noms:
        print(f"Modèle {llm.MODELE} absent. Installés : {noms}")
        return
    choisies = sys.argv[1:] or [c[0] for c in CONDITIONS]
    analyser_journal()
    print(f"Modèle : {llm.MODELE}   ablation des documents sur les {len(bench_decision.SCENARIOS)} situations x 4 ordres\n")
    resultats = {}
    for nom_cond, verites, avec_docs in CONDITIONS:
        if nom_cond not in choisies:
            continue
        base = base_filtree(verites)
        for nom, params, verif, attendu in bench_decision.SCENARIOS:
            m, ilse = bench_llm.preparer(**params)
            docs = texte_documents(recuperer(base, ilse, m.tour + 1)) if avec_docs else ""
            choix = [decider(m, ilse, docs, k=k) for k in range(4)]
            choix = [c["choix"] if c["ok"] else "échec" for c in choix]
            resultats[(nom_cond, nom)] = (choix, sum(1 for c in choix if c != "échec" and verif(c)))
        print(f"... condition « {nom_cond} » terminée", flush=True)

    conds = [c[0] for c in CONDITIONS if c[0] in choisies]
    print("\nChaque case : M = nombre de « Maison », P = nombre de « Puits » (sur 4 ordres)\n")
    print(f"{'situation':<42}" + "".join(f"{c:<18}" for c in conds))
    totaux = {c: [0, 0, 0] for c in conds}
    for nom, *_ in bench_decision.SCENARIOS:
        ligne = f"{nom:<42}"
        for c in conds:
            choix, bons = resultats[(c, nom)]
            m_, p_ = choix.count("Maison"), choix.count("Puits")
            totaux[c][0] += m_
            totaux[c][1] += p_
            totaux[c][2] += bons
            ligne += f"{'M%d P%d' % (m_, p_):<18}"
        print(ligne)
    print(f"{'TOTAL Maison / Puits / conformes':<42}" + "".join(
        f"{'%d / %d / %d' % tuple(totaux[c]):<18}" for c in conds))
    print("\n(« conformes » : bonnes réponses définies par nous, qui ne tiennent pas compte des documents.)")


if __name__ == "__main__":
    main()
