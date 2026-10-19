import json
import sys
import time

from confluent_kafka import Producer

from monde import MondeAgents

TOPIC = "evenements-monde"
SERVEUR = "localhost:9092"
N_TOURS = 40


def main():
    pause = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    graine = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    monde = MondeAgents(graine=graine)
    producteur = Producer({"bootstrap.servers": SERVEUR})
    erreurs = []
    compte = {}

    def rapport(err, msg):
        if err is not None:
            erreurs.append(str(err))

    def envoyer(e):
        # La clé = l'habitant : ses événements restent dans l'ordre
        producteur.produce(
            TOPIC,
            key=e["habitant"],
            value=json.dumps(e, ensure_ascii=False).encode("utf-8"),
            callback=rapport,
        )
        producteur.poll(0)
        compte[e["type"]] = compte.get(e["type"], 0) + 1

    for h in monde.habitants:
        envoyer({"tour": 0, "habitant": h.nom, "type": "init", "lieu": h.lieu, "etat": h.etat,
                 "role": h.role, "quartier": h.quartier, "confiance": h.confiance,
                 "croyance_puits": h.croyance_puits, "croyance_contact": h.croyance_contact})
    producteur.flush(10)

    for _ in range(N_TOURS):
        for e in monde.avancer():
            envoyer(e)
        producteur.flush(10)
        time.sleep(pause)

    print("Événements publiés :", compte)
    print("Erreurs de livraison :", len(erreurs))


if __name__ == "__main__":
    main()
