from base_connaissances import BaseConnaissances

# clé : (question posée à la base, thèmes qu'un document doit couvrir pour être jugé pertinent)
QUESTIONS = {
    "transmission": ("La maladie se transmet-elle par contact avec une personne malade ?",
                     {"contact", "isolement", "symptomes", "soins"}),
    "fievre": ("Que faire si j'ai de la fièvre ?", {"isolement", "symptomes", "soins"}),
    "puits": ("Est-ce que l'eau du puits est contaminée ?", {"puits"}),
    "ecole": ("Dois-je envoyer mes enfants à l'école ?", {"ecole"}),
    "marche": ("Le marché est-il sûr, dois-je garder ma boutique ouverte ?", {"marche"}),
    "confiance": ("Peut-on faire confiance aux chiffres du dispensaire ?", {"confiance"}),
    "age": ("Dois-je rester chez moi à mon âge ?", {"isolement"}),
}
QUESTION_ROLE = {"parent": "ecole", "commerçant": "marche", "sceptique": "confiance", "personne âgée": "age"}


class BaseSimulation(BaseConnaissances):
    """Base de connaissances pour la simulation. On retire les documents qui contredisent la simulation :
    les bulletins chiffrés (l'agent reçoit déjà le vrai bulletin) et les mesures non encore implémentées."""

    def __init__(self, exclure_types=("bulletin",), exclure_ids=("D18", "D24"), **kw):
        super().__init__(**kw)
        self.docs = [d for d in self.docs if d["type"] not in exclure_types and d["id"] not in exclure_ids]


def cles_questions(h):
    """Ce que l'agent se demande selon son état, ses croyances et son rôle."""
    cles = ["transmission"]
    if h.etat == "I":
        cles.append("fievre")
    if h.croyance_puits >= 0.3:
        cles.append("puits")
    if h.role in QUESTION_ROLE:
        cles.append(QUESTION_ROLE[h.role])
    return cles


def recuperer(base, h, jour, k_par_question=2, maximum=4):
    """Une liste de documents, en alternant entre les questions pour qu'une seule ne monopolise pas le résultat."""
    par_question = {}
    for cle in cles_questions(h):
        texte, themes = QUESTIONS[cle]
        par_question[cle] = [(d, s) for d, s in base.rechercher(texte, jour, k_par_question)]
    resultat, deja = [], set()
    while len(resultat) < maximum and any(par_question.values()):
        for cle, liste in par_question.items():
            while liste and liste[0][0]["id"] in deja:
                liste.pop(0)
            if liste and len(resultat) < maximum:
                d, s = liste.pop(0)
                deja.add(d["id"])
                pertinent = bool(set(d["tags"]) & QUESTIONS[cle][1])
                resultat.append({"question": cle, "doc": d, "score": s, "pertinent": pertinent})
    return resultat


def texte_documents(resultats):
    if not resultats:
        return ""
    lignes = ["Informations retrouvées (de sources différentes, elles peuvent se contredire) :"]
    for r in resultats:
        d = r["doc"]
        lignes.append(f"- [jour {d['jour']}, {d['source']}] {d['contenu']}")
    return "\n".join(lignes)
