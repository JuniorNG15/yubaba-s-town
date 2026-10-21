from base_connaissances import BaseConnaissances

# (question posée par un agent, jour courant, thèmes qu'un document doit couvrir pour être pertinent)
CAS = [
    ("Est-ce que l'eau du puits est contaminée ?", 10, {"puits"}),
    ("Comment la maladie se transmet-elle ?", 10, {"contact"}),
    ("Combien de cas le dispensaire a-t-il déclarés ?", 10, {"bulletin"}),
    ("Dois-je envoyer mes enfants à l'école ?", 10, {"ecole"}),
    ("Le marché est-il sûr, dois-je garder ma boutique ouverte ?", 10, {"marche"}),
    ("Que faire si j'ai de la fièvre ?", 10, {"isolement", "symptomes", "soins"}),
    ("Peut-on faire confiance aux chiffres du dispensaire ?", 10, {"bulletin", "confiance"}),
    ("Que décide le conseil de la ville ?", 10, {"mesures"}),
    ("Une personne guérie peut-elle encore contaminer les autres ?", 14, {"guerison"}),
    ("L'école est-elle fermée ?", 5, {"ecole", "mesures"}),
    ("L'école est-elle fermée ?", 14, {"ecole", "mesures"}),
]


def main(k=3):
    base = BaseConnaissances()
    print(f"{len(base.docs)} documents dans la base. Résultats : les {k} meilleurs, jamais de document futur.\n")
    p_tot = r_tot = faux = total = fuites = 0
    for question, jour, themes in CAS:
        res = base.rechercher(question, jour, k)
        pertinents = {d["id"] for d in base.visibles(jour) if set(d["tags"]) & themes}
        trouves = [d["id"] for d, _ in res]
        bons = [i for i in trouves if i in pertinents]
        p = len(bons) / len(trouves) if trouves else 0.0
        r = len(bons) / min(k, len(pertinents)) if pertinents else 1.0
        p_tot += p
        r_tot += r
        fuites += sum(1 for d, _ in res if d["jour"] > jour)
        faux += sum(1 for d, _ in res if d["verite"] == "faux")
        total += len(res)
        print(f"Jour {jour:>2} | {question}")
        for d, s in res:
            marque = "ok " if d["id"] in pertinents else "-- "
            print(f"    {marque}{d['id']} (j{d['jour']:>2}, {d['source']}, {d['verite']}) {d['titre']}  [{s}]")
        print(f"    précision {p:.2f}   rappel {r:.2f}\n")
    n = len(CAS)
    print(f"Moyennes : précision@{k} {p_tot / n:.2f}   rappel@{k} {r_tot / n:.2f}")
    print(f"Documents futurs retrouvés : {fuites} (doit être 0)")
    print(f"Part de documents faux parmi les documents retrouvés : {faux}/{total}")


if __name__ == "__main__":
    main()
