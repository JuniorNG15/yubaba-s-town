import json
import os

from decision_rag import decider as decider_rag
from monde import MAISON, MondeAgents
from monde_llm2 import MondeLLM2
from rag_agents import BaseSimulation, recuperer, texte_documents

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "rag_log.jsonl")


class MondeRAG(MondeLLM2):
    """Décisions LLM (prompt v1) enrichies des documents retrouvés par RAG.
    Chaque décision enregistre ce qui a été retrouvé (journal_rag), pour évaluer la pertinence (F2)."""

    def __init__(self, agents_llm=("Ilse",), variante="v1", base=None, **kw):
        super().__init__(agents_llm=agents_llm, variante=variante, **kw)
        self.base = base or BaseSimulation()
        self.journal_rag = []

    def _decider(self, h, risque, a_vu_malade):
        if h.nom not in self.agents_llm:
            return MondeAgents._decider(self, h, risque, a_vu_malade)
        c_regles, r_regles, d_regles = MondeAgents._decider(self, h, risque, a_vu_malade)
        T = self.tour + 1
        res = recuperer(self.base, h, T)
        rep = decider_rag(self, h, texte_documents(res), variante=self.variante, k=0)
        self.stats["appels"] += 1
        self.stats["ms"].append(rep["ms"])
        entree = {"tour": T, "habitant": h.nom, "regle_reference": c_regles, "ms": rep["ms"],
                  "documents": [{"id": r["doc"]["id"], "jour": r["doc"]["jour"], "source": r["doc"]["source"],
                                 "verite": r["doc"]["verite"], "question": r["question"],
                                 "score": r["score"], "pertinent": r["pertinent"]} for r in res]}
        if not rep["ok"]:
            self.stats["replis"] += 1
            entree.update({"choix": c_regles, "origine": "REPLI", "raison": rep["erreur"]})
            self.journal_rag.append(entree)
            return c_regles, "REPLI_" + r_regles, f"{rep['erreur']} ; {d_regles}"
        self.stats["ok"] += 1
        self.stats["comparees"] += 1
        self.stats["llm_maison"] += rep["choix"] == MAISON
        self.stats["regles_maison"] += c_regles == MAISON
        self.stats["accord_maison"] += (rep["choix"] == MAISON) == (c_regles == MAISON)
        entree.update({"choix": rep["choix"], "origine": "LLM", "raison": rep["raison"]})
        self.journal_rag.append(entree)
        return rep["choix"], "LLM", rep["raison"]

    def ecrire_journal(self, chemin=LOG, graine=None, ajouter=False):
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "a" if ajouter else "w", encoding="utf-8") as f:
            for e in self.journal_rag:
                f.write(json.dumps(dict(e, graine=graine), ensure_ascii=False) + "\n")
        return os.path.normpath(chemin)
