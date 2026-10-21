import sys

import llm
from essai_comparaison import jouer
from monde import MondeAgents
from monde_llm2 import MondeLLM2
from monde_rag import MondeRAG


def resume_journal(journal):
    docs = [d for e in journal for d in e["documents"]]
    if not docs:
        return
    n = len(docs)
    print(f"Documents retrouvés : {n} pour {len(journal)} décisions ({n / len(journal):.1f} par décision)")
    print(f"  jugés pertinents (thèmes de la question) : {sum(d['pertinent'] for d in docs)}/{n}")
    print(f"  faux : {sum(d['verite'] == 'faux' for d in docs)}/{n}   "
          f"partiels : {sum(d['verite'] == 'partiel' for d in docs)}/{n}")
    print(f"  décisions avec au moins un document faux : "
          f"{sum(any(d['verite'] == 'faux' for d in e['documents']) for e in journal)}/{len(journal)}")
    print(f"  documents futurs retrouvés : {sum(d['jour'] > e['tour'] for e in journal for d in e['documents'])} (doit être 0)")


def main():
    tours = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    graine = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    comparer = len(sys.argv) > 3 and sys.argv[3] == "comparer"
    noms = llm.modeles()
    if noms is None:
        print("Ollama ne répond pas. Lancez l'application Ollama.")
        return
    if llm.MODELE not in noms:
        print(f"Modèle {llm.MODELE} absent. Installés : {noms}")
        return
    print(f"Modèle : {llm.MODELE}   Ilse avec RAG   {tours} tours   graine {graine}\n")
    regles = jouer(MondeAgents(graine=graine), tours)
    m = MondeRAG(graine=graine)
    rag = jouer(m, tours)
    chemin = m.ecrire_journal(graine=graine)
    s = m.stats
    print(f"Décisions LLM valides : {s['ok']}/{s['appels']}   replis : {s['replis']}   "
          f"latence moyenne {sum(s['ms']) / max(1, len(s['ms'])) / 1000:.1f} s")
    print(f"Journal des documents retrouvés : {chemin}\n")
    resume_journal(m.journal_rag)

    print("\nÉchantillon de décisions (documents retrouvés : identifiant, vérité, pertinence) :")
    pas = max(1, len(m.journal_rag) // 6)
    for e in m.journal_rag[::pas][:6]:
        docs = ", ".join(f"{d['id']}({d['verite'][:2]},{'ok' if d['pertinent'] else '--'})" for d in e["documents"])
        print(f"  tour {e['tour']:>2} -> {e['choix']:<11} [{e['origine']}]  {docs}")
        print(f"          raison : {e['raison'][:100]}")

    print("\nRésultat de la partie (graine %d) :" % graine)
    print(f"  Ilse touchée : règles {regles['ilse']}  RAG {rag['ilse']}   "
          f"tours à la Maison : règles {regles['maison']}  RAG {rag['maison']}   "
          f"habitants touchés : règles {regles['touches']}  RAG {rag['touches']}")
    if comparer:
        sans = jouer(MondeLLM2(graine=graine), tours)
        print(f"  Sans RAG (même prompt, même graine) : Ilse {sans['ilse']}   tours à la Maison {sans['maison']}   "
              f"touchés {sans['touches']}")
    print("(Une seule partie : indicatif seulement, d'autant que le LLM n'est pas strictement reproductible.)")


if __name__ == "__main__":
    main()
