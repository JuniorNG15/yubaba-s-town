from decision_llm import decider
from monde import MAISON, MondeAgents


class MondeLLM2(MondeAgents):
    """Certains habitants décident via un LLM (décision en deux temps).
    La décision que les règles auraient prise est calculée en parallèle (sans effet) pour comparaison.
    Si le LLM échoue, l'habitant retombe sur sa décision à règles."""

    def __init__(self, agents_llm=("Ilse",), variante="v1", **kw):
        super().__init__(**kw)
        self.agents_llm = set(agents_llm)
        self.variante = variante
        self.stats = {"appels": 0, "ok": 0, "replis": 0, "ms": [], "comparees": 0,
                      "accord_maison": 0, "llm_maison": 0, "regles_maison": 0}

    def _decider(self, h, risque, a_vu_malade):
        c_regles, r_regles, d_regles = super()._decider(h, risque, a_vu_malade)
        if h.nom not in self.agents_llm:
            return c_regles, r_regles, d_regles
        rep = decider(self, h, variante=self.variante, k=0)
        self.stats["appels"] += 1
        self.stats["ms"].append(rep["ms"])
        if not rep["ok"]:
            self.stats["replis"] += 1
            return c_regles, "REPLI_" + r_regles, f"{rep['erreur']} ; {d_regles}"
        self.stats["ok"] += 1
        self.stats["comparees"] += 1
        self.stats["llm_maison"] += rep["choix"] == MAISON
        self.stats["regles_maison"] += c_regles == MAISON
        self.stats["accord_maison"] += (rep["choix"] == MAISON) == (c_regles == MAISON)
        return rep["choix"], "LLM", rep["raison"]
