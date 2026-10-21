import llm
from monde import MAISON

ROLES = {
    "soignante": "Tu travailles au dispensaire et tu soignes les malades.",
    "commerçant": "Tu tiens une boutique au marché : si tu restes chez toi, tu ne vends rien.",
    "parent": "Tu es parent : tu t'inquiètes pour tes enfants, qui vont à l'école.",
    "sceptique": "Tu doutes des discours officiels et tu n'aimes pas qu'on te dise quoi faire.",
    "personne âgée": "Tu es âgé(e) et tu vis seul(e) : une maladie te ferait courir un grand danger.",
}


def sante_txt(etat):
    return {"S": "Tu es en bonne santé.", "I": "Tu es malade : tu as de la fièvre.", "R": "Tu as guéri."}[etat]


def contact_txt(p):
    if p >= 0.75:
        return "Tu es convaincu(e) que la maladie se transmet par contact."
    if p >= 0.5:
        return "Tu penses que la maladie se transmet probablement par contact."
    if p >= 0.3:
        return "Tu hésites : la maladie se transmet peut-être par contact."
    return "Tu doutes que la maladie se transmette par contact."


def puits_txt(p):
    if p >= 0.75:
        return "Tu es convaincu(e) que le puits est contaminé."
    if p >= 0.5:
        return "Tu penses que le puits est probablement contaminé."
    if p >= 0.3:
        return "Tu hésites : le puits est peut-être contaminé."
    return "Tu doutes que le puits soit contaminé."


def confiance_txt(c):
    if c >= 0.75:
        return "Tu fais très confiance au dispensaire."
    if c >= 0.4:
        return "Tu fais moyennement confiance au dispensaire."
    return "Tu te méfies du dispensaire."


def bulletin_txt(n, total):
    if n == 0:
        return "Le dispensaire ne signale aucun cas."
    return f"Le dispensaire signale {n} cas sur {total} habitants."


def situation(m, h):
    lignes = [sante_txt(h.etat), contact_txt(h.croyance_contact), puits_txt(h.croyance_puits),
              confiance_txt(h.confiance), bulletin_txt(m.bulletin(), len(m.habitants))]
    souvenirs = [x for x in h.memoire if x["importance"] >= 2][-3:]
    if souvenirs:
        lignes.append("Ce que tu as vu ou appris récemment :")
        lignes += [f"- {x['detail']}" for x in souvenirs]
    return "\n".join(lignes)


ENJEUX = ("Sortir te fait croiser d'autres habitants et peut te contaminer si certains sont malades. "
          "Rester chez toi te protège, mais tu ne vois personne et tu ne fais rien d'utile.")

PESER = ("Pèse d'abord ce que tu crois et ta confiance dans le dispensaire, puis ce que tu as vu toi-même, "
         "puis ton rôle. Si le danger te paraît réel, reste chez toi ; s'il te paraît faible, ou si tu n'y crois pas, sors. ")


def decider(m, h, variante="v1", k=0):
    """Décision en deux temps : sortir/rester, puis le lieu. k fait tourner l'ordre des options."""
    T = m.tour + 1
    systeme = (f"Tu es {h.nom}, {h.role} du quartier {h.quartier} de Yubaba's Town, une petite ville de "
               f"{len(m.habitants)} habitants touchée par une maladie, la fièvre grise. "
               f"{ROLES.get(h.role, '')} Tu réponds uniquement par un objet JSON.")
    faits = situation(m, h)
    consigne = 'Que fais-tu ce tour ? Réponds par un JSON : {"raison": "une phrase courte", "choix": "sortir" ou "rester"}.'
    if variante == "v2":
        consigne = PESER + consigne
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
    q2 = (f"Tour {T}.\n{faits}\nTu as décidé de sortir. Où vas-tu ? Lieux possibles : {', '.join(lieux)}. "
          'Réponds par un JSON : {"raison": "une phrase courte", "choix": "un des lieux"}.')
    r2 = llm.decider(systeme, q2, lieux, raison_d_abord=True)
    ms += r2["ms"]
    if not r2["ok"]:
        return {"ok": False, "erreur": r2["erreur"], "ms": ms}
    return {"ok": True, "choix": r2["choix"], "raison": r2["raison"], "ms": ms}
