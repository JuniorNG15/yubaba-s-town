import sys

import llm
from monde import MAISON, MondeAgents
from monde_llm2 import MondeLLM2


def jouer(monde, tours, nom="Ilse"):
    maison = malade_dehors = 0
    for _ in range(tours):
        h = next(x for x in monde.habitants if x.nom == nom)
        etat_avant = h.etat
        evts = monde.avancer()
        d = next(e for e in evts if e["type"] == "decision" and e["habitant"] == nom)
        maison += d["choix"] == MAISON
        malade_dehors += (etat_avant == "I" and d["choix"] != MAISON)
    ilse = next(x for x in monde.habitants if x.nom == nom)
    c = monde.compter()
    return {"touches": c["I"] + c["R"], "ilse": ilse.etat, "maison": maison, "malade_dehors": malade_dehors, "c": c}


def main():
    tours = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    nb = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    noms = llm.modeles()
    if noms is None:
        print("Ollama ne répond pas. Lancez l'application Ollama.")
        return
    if llm.MODELE not in noms:
        print(f"Modèle {llm.MODELE} absent. Installés : {noms}")
        return
    print(f"Modèle : {llm.MODELE}   prompt v1   {tours} tours   graines 0 à {nb - 1}")
    print("Ilse décide par règles (R) ou par LLM (L) ; les 4 autres habitants par règles.\n")
    print("graine | touchés R/L | Ilse R/L | tours à la Maison R/L | Ilse malade dehors R/L")
    res_r, res_l, agreg = [], [], {"appels": 0, "ok": 0, "replis": 0, "ms": [], "comparees": 0,
                                   "accord_maison": 0, "llm_maison": 0, "regles_maison": 0}
    for g in range(nb):
        r = jouer(MondeAgents(graine=g), tours)
        ml = MondeLLM2(graine=g)
        l = jouer(ml, tours)
        res_r.append(r)
        res_l.append(l)
        for cle, val in ml.stats.items():
            if cle == "ms":
                agreg["ms"] += val
            else:
                agreg[cle] += val
        print(f"{g:>6} | {r['touches']}/{l['touches']:<9} | {r['ilse']}/{l['ilse']:<6} | "
              f"{r['maison']:>2}/{l['maison']:<18} | {r['malade_dehors']}/{l['malade_dehors']}", flush=True)

    def moy(res, cle):
        return sum(x[cle] for x in res) / len(res)

    print(f"\nMoyennes sur {nb} graines : touchés R {moy(res_r, 'touches'):.1f} / L {moy(res_l, 'touches'):.1f}   "
          f"tours à la Maison R {moy(res_r, 'maison'):.1f} / L {moy(res_l, 'maison'):.1f}")
    if agreg["comparees"]:
        a = agreg
        print(f"Décisions LLM valides : {a['ok']}/{a['appels']}   replis sur les règles : {a['replis']}")
        print(f"Accord LLM / règles sur « Maison ou sortir » : {a['accord_maison']}/{a['comparees']}   "
              f"(Maison : LLM {a['llm_maison']}, règles {a['regles_maison']})")
    if agreg["ms"]:
        print(f"Latence moyenne d'une décision : {sum(agreg['ms']) / len(agreg['ms']) / 1000:.1f} s")

    t = ref = 0
    for g in range(200):
        m = MondeAgents(graine=g)
        for _ in range(tours):
            m.avancer()
        c = m.compter()
        t += c["I"] + c["R"]
        ref += next(x for x in m.habitants if x.nom == "Ilse").etat != "S"
    print(f"\nRéférence, règles seules sur 200 graines : touchés {t / 200:.2f}/5 en moyenne, "
          f"Ilse touchée dans {ref / 2:.0f} % des parties")
    print("(Avec si peu de graines, ces écarts sont indicatifs et non démontrés.)")


if __name__ == "__main__":
    main()
