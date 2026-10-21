import json
import os

CHEMIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "corpus.jsonl")


def doc(id, jour, source, type, titre, contenu, verite, tags):
    # verite et tags servent à l'évaluation : ils ne sont jamais montrés aux agents
    return {"id": id, "jour": jour, "source": source, "type": type, "titre": titre,
            "contenu": contenu, "verite": verite, "tags": tags}


DOCUMENTS = [
    doc("D01", 1, "Dispensaire", "bulletin", "Bulletin du dispensaire n°1",
        "Un cas de fièvre grise a été signalé en ville. Les symptômes sont une forte fièvre et une grande fatigue pendant plusieurs jours. Le dispensaire surveille la situation.",
        "vrai", ["bulletin", "symptomes"]),
    doc("D02", 2, "Rumeur du quartier bas", "rumeur", "On dit que le puits est empoisonné",
        "On raconte au marché que l'eau du puits est contaminée et que c'est elle qui rend les gens malades. Mieux vaut ne plus y puiser.",
        "faux", ["puits"]),
    doc("D03", 3, "Dispensaire", "bulletin", "Bulletin du dispensaire n°2",
        "Deux cas déclarés. Les deux malades avaient fréquenté des lieux très animés dans les jours précédents, notamment le marché et l'école.",
        "vrai", ["bulletin", "contact", "marche", "ecole"]),
    doc("D04", 3, "Conseil de la ville", "communique", "Communiqué du conseil : la ville reste sûre",
        "Le conseil rappelle que la ville est sûre. Aucune fermeture n'est envisagée. Le marché et l'école restent ouverts normalement.",
        "partiel", ["mesures", "marche", "ecole"]),
    doc("D05", 4, "Mara, soignante", "temoignage", "Ce que je constate au dispensaire",
        "J'ai soigné deux malades. La fièvre passe visiblement d'une personne à l'autre : les proches des malades tombent malades à leur tour. Si vous avez de la fièvre, restez chez vous.",
        "vrai", ["contact", "isolement", "symptomes", "soins"]),
    doc("D06", 4, "Le Courrier de Yubaba's Town", "presse", "Enquête : l'eau du puits en cause ?",
        "Selon plusieurs habitants, l'eau du puits serait à l'origine de la fièvre grise. Le conseil refuse de commenter ces accusations.",
        "faux", ["puits"]),
    doc("D07", 5, "Dispensaire", "analyse", "Analyse de l'eau du puits",
        "Des prélèvements d'eau ont été analysés : aucune contamination n'a été détectée. Le puits peut être utilisé normalement.",
        "vrai", ["puits"]),
    doc("D08", 5, "Bram, atelier", "temoignage", "On exagère cette histoire de fièvre",
        "J'ai travaillé toute la semaine à l'atelier et je vais très bien. On nous fait peur pour rien avec cette fièvre.",
        "partiel", ["contact", "atelier"]),
    doc("D09", 6, "Dispensaire", "bulletin", "Bulletin du dispensaire n°3",
        "Trois cas déclarés. Le dispensaire recommande d'éviter les rassemblements et de rester chez soi en cas de fièvre.",
        "vrai", ["bulletin", "mesures", "isolement"]),
    doc("D10", 6, "Rumeur du marché", "rumeur", "Seuls les enfants tombent malades",
        "Une marchande affirme que les adultes ne risquent rien et que seuls les enfants attrapent la fièvre grise.",
        "faux", ["ecole"]),
    doc("D11", 7, "Conseil de la ville", "communique", "Le conseil appelle au calme",
        "Face à l'inquiétude, le conseil demande aux habitants de rester calmes. Les commerçants sont invités à garder leurs étals ouverts pour préserver l'approvisionnement.",
        "partiel", ["mesures", "marche"]),
    doc("D12", 7, "Ilse, parent", "temoignage", "Mon voisin a gardé ses enfants",
        "Mon voisin a gardé ses enfants à la maison et personne n'est tombé malade chez lui. Les enfants qui sont allés à l'école ont attrapé la fièvre.",
        "partiel", ["ecole", "contact"]),
    doc("D13", 8, "Dispensaire", "bulletin", "Bulletin du dispensaire n°4",
        "Quatre cas déclarés. La maladie se transmet par contact rapproché avec une personne malade. Éviter les lieux bondés réduit nettement le risque.",
        "vrai", ["bulletin", "contact", "mesures"]),
    doc("D14", 9, "Le Courrier de Yubaba's Town", "presse", "Le conseil sous pression",
        "Plusieurs habitants estiment que les communiqués du conseil sont trop rassurants face à la progression de la maladie.",
        "vrai", ["mesures"]),
    doc("D15", 10, "Rumeur de l'atelier", "rumeur", "Le dispensaire cacherait des cas",
        "Il se dit que le dispensaire cache des cas pour éviter la panique et que les chiffres réels sont bien plus élevés. Il est vrai que ses bulletins arrivent avec du retard.",
        "partiel", ["bulletin", "confiance"]),
    doc("D16", 10, "Noa, aînée", "temoignage", "Je ne prends aucun risque",
        "À mon âge je ne prends aucun risque. Je reste chez moi depuis que je sais que la fièvre passe d'une personne à l'autre.",
        "vrai", ["isolement", "contact"]),
    doc("D17", 12, "Dispensaire", "bulletin", "Bulletin du dispensaire n°5",
        "Cinq cas déclarés. Les premiers malades commencent à guérir après une dizaine de jours. Une personne guérie n'est plus contagieuse.",
        "vrai", ["bulletin", "guerison"]),
    doc("D18", 12, "Conseil de la ville", "communique", "Fermeture temporaire de l'école",
        "Le conseil annonce la fermeture temporaire de l'école et recommande de limiter les déplacements à l'atelier.",
        "vrai", ["mesures", "ecole", "atelier"]),
    doc("D19", 14, "Rumeur du quartier bas", "rumeur", "L'eau du puits a un goût étrange",
        "Certains disent que le puits est de nouveau sûr, mais que l'eau garde un goût étrange. Beaucoup préfèrent l'éviter.",
        "faux", ["puits"]),
    doc("D20", 15, "Dispensaire", "note", "Rappel du dispensaire",
        "Rappel : l'eau du puits est saine. La fièvre grise se transmet uniquement par contact avec une personne malade.",
        "vrai", ["puits", "contact"]),
    doc("D21", 16, "Tomas, commerçant", "temoignage", "Je ferme ma boutique",
        "Plus personne ne vient au marché et j'ai peur. Je ferme ma boutique, mais je perds tous mes revenus.",
        "vrai", ["marche", "mesures"]),
    doc("D22", 18, "Le Courrier de Yubaba's Town", "presse", "La fièvre recule",
        "La fièvre grise recule en ville. Le dispensaire attribue cette baisse au fait que de nombreux habitants restent chez eux.",
        "vrai", ["mesures", "isolement"]),
    doc("D23", 20, "Dispensaire", "bulletin", "Bulletin du dispensaire n°6",
        "Aucun nouveau cas depuis trois jours. Le dispensaire reste prudent et poursuit sa surveillance.",
        "vrai", ["bulletin"]),
    doc("D24", 22, "Conseil de la ville", "communique", "Réouverture de l'école",
        "Le conseil annonce la réouverture de l'école et du marché dans leurs horaires habituels.",
        "vrai", ["mesures", "ecole", "marche"]),
]


def ecrire():
    os.makedirs(os.path.dirname(CHEMIN), exist_ok=True)
    with open(CHEMIN, "w", encoding="utf-8") as f:
        for d in DOCUMENTS:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"{len(DOCUMENTS)} documents écrits dans {os.path.normpath(CHEMIN)}")


if __name__ == "__main__":
    ecrire()
