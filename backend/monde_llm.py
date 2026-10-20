from monde import MAISON, MondeAgents
import llm

ETATS = {"S": "en bonne santé", "I": "malade", "R": "guéri"}


class MondeLLM(MondeAgents):
    """Comme MondeAgents, mais certains habitants décident via un LLM local.
    Si le LLM échoue, l'habitant retombe sur les règles : la simulation ne s'arrête jamais."""

    def __init__(self, agents_llm=("Ilse",), **kw):
        super().__init__(**kw)
        self.agents_llm = set(agents_llm)
        self.stats = {"appels": 0, "ok": 0, "replis": 0, "ms": []}
        self.journal = []

    def _prompt(self, h, options):
        T = self.tour + 1
        systeme = (
            f"Tu es {h.nom}, {h.role} du quartier {h.quartier} de Yubaba's Town, "
            "une petite ville touchée par une maladie, la fièvre grise. "
            "Tu décides où aller ce tour. Réponds uniquement par un objet JSON."
        )
        lignes = [
            f"Tour {T}. Ton état de santé : {ETATS[h.etat]}. Tu es actuellement : {h.lieu}.",
            f"Ta confiance envers le dispensaire : {round(h.confiance * 100)} %.",
            f"Tu crois à {round(h.croyance_puits * 100)} % que le puits est contaminé "
            f"et à {round(h.croyance_contact * 100)} % que la maladie se transmet par contact.",
            f"Dernier bulletin du dispensaire (il date de {self.delai_bulletin} tours) : "
            f"{self.bulletin()} cas déclarés.",
        ]
        souvenirs = [m for m in h.memoire if m["importance"] >= 2][-4:]
        if souvenirs:
            lignes.append("Tes souvenirs récents :")
            lignes += [f"- tour {m['tour']} : {m['detail']}" for m in souvenirs]
        lignes.append("Lieux possibles : " + ", ".join(options) + f". ({MAISON} = rester chez toi.)")
        lignes.append('Choisis un lieu dans cette liste et donne une raison courte, en une phrase, '
                      'en français. Format : {"choix": "...", "raison": "..."}')
        return systeme, "\n".join(lignes)

    def _decider(self, h, risque, a_vu_malade):
        if h.nom not in self.agents_llm:
            return super()._decider(h, risque, a_vu_malade)
        options = list(dict.fromkeys(h.habituels + [MAISON]))
        systeme, question = self._prompt(h, options)
        rep = llm.decider(systeme, question, options)
        self.stats["appels"] += 1
        self.stats["ms"].append(rep["ms"])
        if rep["ok"]:
            self.stats["ok"] += 1
            self.journal.append({"tour": self.tour + 1, "habitant": h.nom, "choix": rep["choix"],
                                 "croyance_puits": h.croyance_puits, "ms": rep["ms"]})
            return rep["choix"], "LLM", rep["raison"]
        self.stats["replis"] += 1
        choix, regle, detail = super()._decider(h, risque, a_vu_malade)
        return choix, "REPLI_" + regle, f"{rep['erreur']} ; {detail}"
