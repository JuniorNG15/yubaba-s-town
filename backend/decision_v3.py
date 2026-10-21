import llm
from decision_llm import ROLES, situation
from monde import MAISON

ENJEUX = ("Sortir te fait croiser d'autres habitants : tu peux te contaminer si certains sont malades, "
          "et si tu es toi-même malade, tu peux contaminer les autres. "
          "Rester chez toi protège tout le monde, mais tu ne vois personne et tu ne fais rien d'utile.")


def faits_lieu(h, lieu):
    """Ce que l'agent sait de ce lieu : ses croyances et sa mémoire."""
    faits = []
    if lieu == "Puits" and h.croyance_puits >= 0.5:
        faits.append("tu crois que son eau est contaminée")
    for x in h.memoire:
        if x["importance"] >= 2 and x["genre"] == "vu_malade" and f"({lieu})" in x["detail"]:
            qui = x["detail"].split(" semble")[0]
            faits.append(f"tu y as vu {qui} malade")
            break
    return faits


def lieux_annotes(h, lieux):
    textes = []
    for lieu in lieux:
        f = faits_lieu(h, lieu)
        textes.append(f"{lieu} ({' ; '.join(f)})" if f else lieu)
    return ", ".join(textes)


def decider(m, h, k=0):
    T = m.tour + 1
    systeme = (f"Tu es {h.nom}, {h.role} du quartier {h.quartier} de Yubaba's Town, une petite ville de "
               f"{len(m.habitants)} habitants touchée par une maladie, la fièvre grise. "
               f"{ROLES.get(h.role, '')} Tu réponds uniquement par un objet JSON.")
    faits = situation(m, h)
    consigne = 'Que fais-tu ce tour ? Réponds par un JSON : {"raison": "une phrase courte", "choix": "sortir" ou "rester"}.'
    options1 = ["sortir", "rester"] if k % 2 == 0 else ["rester", "sortir"]
    r1 = llm.decider(systeme, f"Tour {T}.\n{faits}\n{ENJEUX}\n{consigne}", options1, raison_d_abord=True)
    ms = r1["ms"]
    if not r1["ok"]:
        return {"ok": False, "erreur": r1["erreur"], "ms": ms}
    if r1["choix"] == "rester":
        return {"ok": True, "choix": MAISON, "raison": r1["raison"], "ms": ms}
    lieux = list(h.habituels)
    r = k % len(lieux)
    lieux = lieux[r:] + lieux[:r]
    q2 = (f"Tour {T}.\n{faits}\nTu as décidé de sortir. Où vas-tu ? Lieux possibles : {lieux_annotes(h, lieux)}. "
          'Réponds par un JSON : {"raison": "une phrase courte", "choix": "un des lieux, sans les parenthèses"}.')
    r2 = llm.decider(systeme, q2, lieux, raison_d_abord=True)
    ms += r2["ms"]
    if not r2["ok"]:
        return {"ok": False, "erreur": r2["erreur"], "ms": ms}
    return {"ok": True, "choix": r2["choix"], "raison": r2["raison"], "ms": ms}
