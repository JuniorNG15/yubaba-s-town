import decision_llm

_situation_origine = decision_llm.situation


def decider(m, h, documents, variante="v1", k=0):
    """Même décision que decision_llm.decider (prompt v1), avec les documents retrouvés ajoutés à la situation.
    `documents` est le texte produit par rag_agents.texte_documents (vide = comportement v1 inchangé)."""
    if documents:
        decision_llm.situation = lambda mm, hh: _situation_origine(mm, hh) + "\n" + documents
    try:
        return decision_llm.decider(m, h, variante=variante, k=k)
    finally:
        decision_llm.situation = _situation_origine
