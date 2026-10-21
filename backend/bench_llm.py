import sys

import llm
from monde_llm import MondeLLM

BASE = ["École", "Marché", "Puits", "Maison"]

SCENARIOS = [
    ("Calme, aucune inquiétude",
     dict(bulletin=0, puits=0.1, contact=0.1, confiance=0.5),
     lambda c: c != "Maison", "sortir (pas Maison)"),
    ("Épidémie grave, malades vus",
     dict(bulletin=4, puits=0.3, contact=0.9, confiance=0.9,
          souvenirs=[(9, "Mara semble malade (Marché)"), (10, "Bram semble malade (École)")]),
     lambda c: c == "Maison", "rester à la Maison"),
    ("Croit le puits contaminé",
     dict(bulletin=0, puits=0.9, contact=0.1, confiance=0.5),
     lambda c: c != "Puits", "éviter le Puits"),
    ("Elle-même malade",
     dict(bulletin=2, etat="I", puits=0.3, contact=0.5, confiance=0.6),
     lambda c: c == "Maison", "rester à la Maison"),
    ("A vu un malade au Marché",
     dict(bulletin=1, puits=0.3, contact=0.7, confiance=0.7,
          souvenirs=[(10, "Tomas semble malade (Marché)")]),
     lambda c: c != "Marché", "éviter le Marché"),
]


def preparer(bulletin, etat="S", confiance=0.6, puits=0.3, contact=0.5, souvenirs=()):
    m = MondeLLM(agents_llm=(), graine=1)
    ilse = next(h for h in m.habitants if h.nom == "Ilse")
    ilse.etat, ilse.confiance = etat, confiance
    ilse.croyance_puits, ilse.croyance_contact = puits, contact
    ilse.lieu = "Maison"
    m.tour = 10
    m.historique_infectes = [bulletin] * 11
    for t, detail in souvenirs:
        ilse.se_souvenir(t, "vu_malade", detail, 2)
    return m, ilse


def main():
    noms = llm.modeles()
    if noms is None:
        print("Ollama ne répond pas. Lancez l'application Ollama.")
        return
    if llm.MODELE not in noms:
        print(f"Modèle {llm.MODELE} absent. Installés : {noms}")
        return
    print(f"Modèle testé : {llm.MODELE}")
    for nom_variante, raison_d_abord in (("choix puis raison", False), ("raison puis choix", True)):
        print(f"\n--- Format : {nom_variante} ---")
        total = bons = echecs = 0
        durees = []
        for nom, params, verif, attendu in SCENARIOS:
            m, ilse = preparer(**params)
            choix = []
            for k in range(4):
                options = BASE[k:] + BASE[:k]
                systeme, question = m._prompt(ilse, options)
                rep = llm.decider(systeme, question, options, raison_d_abord=raison_d_abord)
                durees.append(rep["ms"])
                total += 1
                if not rep["ok"]:
                    echecs += 1
                    choix.append("échec")
                    continue
                choix.append(rep["choix"])
                bons += verif(rep["choix"])
            conformes = sum(1 for c in choix if c != "échec" and verif(c))
            print(f"{nom:<30} attendu : {attendu:<20} {conformes}/4   {choix}")
        print(f"=> conformes {bons}/{total}   échecs de format {echecs}   "
              f"latence moyenne {sum(durees) / len(durees) / 1000:.1f} s")


if __name__ == "__main__":
    main()
