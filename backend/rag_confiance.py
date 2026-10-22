def confiance_source(h, type_doc):
    """Confiance de l'agent envers une source, déduite de son profil (hypothèse de modélisation à valider)."""
    if type_doc in ("bulletin", "analyse", "note", "communique"):
        return h.confiance                      # sources officielles : sa confiance dans les institutions
    if type_doc == "rumeur":
        return 0.7 - 0.5 * h.confiance          # un agent méfiant des institutions croit davantage les rumeurs
    return 0.5                                  # presse, témoignages : confiance moyenne


def mot_confiance(c):
    if c >= 0.75:
        return "tu lui fais très confiance"
    if c >= 0.4:
        return "tu lui fais moyennement confiance"
    return "tu t'en méfies"


def texte_documents_confiance(resultats, h):
    if not resultats:
        return ""
    lignes = ["Informations retrouvées (de sources différentes, elles peuvent se contredire) :"]
    for r in resultats:
        d = r["doc"]
        c = confiance_source(h, d["type"])
        lignes.append(f"- [jour {d['jour']}, {d['source']} : {mot_confiance(c)}] {d['contenu']}")
    return "\n".join(lignes)
