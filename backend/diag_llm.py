import llm
from monde_llm import MondeLLM

VARIANTES = [("choix puis raison", False), ("raison puis choix", True)]


def diagnostiquer(m, h):
    base = ["École", "Marché", "Puits", "Maison"]
    print(f"\n=== Situation : tour {m.tour + 1}, bulletin = {m.bulletin()} cas, "
          f"croyance puits {h.croyance_puits:.2f}, contacts {h.croyance_contact:.2f} ===")
    for nom, raison_d_abord in VARIANTES:
        choix, premiers, ms, exemple = [], 0, [], None
        for k in range(4):
            options = base[k:] + base[:k]          # on fait tourner l'ordre de la liste
            systeme, question = m._prompt(h, options)
            rep = llm.decider(systeme, question, options, raison_d_abord=raison_d_abord)
            ms.append(rep["ms"])
            if not rep["ok"]:
                choix.append("(échec)")
                continue
            choix.append(rep["choix"])
            premiers += rep["choix"] == options[0]
            if exemple is None:
                exemple = rep["raison"]
        print(f"{nom:<18} choix pour les 4 ordres : {choix}")
        print(f"{'':<18} premier de la liste choisi : {premiers}/4   latence moyenne : {sum(ms) / len(ms) / 1000:.1f} s")
        if exemple:
            print(f"{'':<18} exemple de raison : {exemple[:90]}")


def main():
    if llm.modeles() is None:
        print("Ollama ne répond pas. Lancez l'application Ollama.")
        return
    m = MondeLLM(agents_llm=(), graine=42)        # aucune décision LLM : on prépare seulement l'état
    ilse = next(h for h in m.habitants if h.nom == "Ilse")
    for _ in range(2):
        m.avancer()
    diagnostiquer(m, ilse)
    for _ in range(13):
        m.avancer()
    diagnostiquer(m, ilse)


if __name__ == "__main__":
    main()
