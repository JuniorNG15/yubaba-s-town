import sys

import llm
from monde_llm import MondeLLM


def main():
    tours = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    noms = llm.modeles()
    if noms is None:
        print(f"Ollama ne répond pas sur {llm.URL}. Lancez l'application Ollama, puis recommencez.")
        return
    if llm.MODELE not in noms:
        print(f"Modèle {llm.MODELE} absent. Modèles installés : {noms}")
        return
    print(f"Ollama OK, modèle {llm.MODELE}")
    m = MondeLLM(agents_llm=("Ilse",), graine=42)
    print(f"Partie de {tours} tours : Ilse décide par LLM, les 4 autres par règles.")
    print("(le premier appel est plus lent : chargement du modèle)\n")
    print("tour S I R  choix d'Ilse  règle                     ms  raison")
    for _ in range(tours):
        evts = m.avancer()
        c = m.compter()
        d = next(e for e in evts if e["type"] == "decision" and e["habitant"] == "Ilse")
        ms = m.stats["ms"][-1]
        print(f"{m.tour:>4} {c['S']} {c['I']} {c['R']}  {d['choix']:<12}  {d['regle']:<22} {ms:>6}  {d['detail'][:60]}")

    s = m.stats
    print(f"\nAppels : {s['appels']}   valides : {s['ok']}   replis sur les règles : {s['replis']}")
    if s["ms"]:
        moy = sum(s["ms"]) / len(s["ms"]) / 1000
        print(f"Latence : moyenne {moy:.1f} s, max {max(s['ms']) / 1000:.1f} s, "
              f"total {sum(s['ms']) / 60000:.1f} min")
    repart = {}
    for j in m.journal:
        repart[j["choix"]] = repart.get(j["choix"], 0) + 1
    print("Choix du LLM :", repart)
    incoh = sum(1 for j in m.journal if j["choix"] == "Puits" and j["croyance_puits"] > 0.5)
    print(f"Incohérences (Puits alors qu'elle y croit à plus de 50 %) : {incoh}")


if __name__ == "__main__":
    main()
