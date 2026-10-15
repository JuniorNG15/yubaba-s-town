import json
from sim import Monde


def evenements_du_tour(monde):
    avant = {h.nom: (h.lieu, h.etat) for h in monde.habitants}
    monde.avancer()
    evts = []
    for h in monde.habitants:
        lieu0, etat0 = avant[h.nom]
        base = {"tour": monde.tour, "habitant": h.nom}
        if h.lieu != lieu0:
            evts.append({**base, "type": "deplacement", "de": lieu0, "vers": h.lieu})
        if etat0 == "S" and h.etat == "I":
            evts.append({**base, "type": "contamination", "lieu": h.lieu})
        elif etat0 == "I" and h.etat == "R":
            evts.append({**base, "type": "guerison", "lieu": h.lieu})
    return evts


def main():
    noms = ["Mara", "Tomas", "Ilse", "Bram", "Noa"]
    monde = Monde(noms, beta=0.5)
    compte = {}
    with open("backend/events.jsonl", "w", encoding="utf-8") as f:
        for _ in range(40):
            for e in evenements_du_tour(monde):
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
                compte[e["type"]] = compte.get(e["type"], 0) + 1
    print("Événements écrits dans backend/events.jsonl :", compte)


if __name__ == "__main__":
    main()
