import json
import sys
import time

from confluent_kafka import Producer

from evenements import evenements_du_tour
from sim import Monde

TOPIC = "evenements-monde"
SERVEUR = "localhost:9092"


def main():
    pause = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    monde = Monde(["Mara", "Tomas", "Ilse", "Bram", "Noa"], beta=0.5)
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
        envoyer({"tour": 0, "habitant": h.nom, "type": "init", "lieu": h.lieu, "etat": h.etat})
    producteur.flush(10)

    for _ in range(40):
        for e in evenements_du_tour(monde):
            envoyer(e)
        producteur.flush(10)
        time.sleep(pause)

    print("Événements publiés :", compte)
    print("Erreurs de livraison :", len(erreurs))


if __name__ == "__main__":
    main()
