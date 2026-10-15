import json
import time

from confluent_kafka import Consumer

TOPIC = "evenements-monde"
SERVEUR = "localhost:9092"


def resume(etats):
    return {e: sum(1 for v in etats.values() if v == e) for e in "SIR"}


def main():
    consommateur = Consumer({
        "bootstrap.servers": SERVEUR,
        "group.id": "console-" + str(int(time.time())),
        "auto.offset.reset": "earliest",
    })
    consommateur.subscribe([TOPIC])
    etats = {}
    tour = 0
    recu = False
    dernier = time.time()
    print("En attente d'événements... (Ctrl+C pour quitter)")
    print("tour     S     I     R")
    try:
        while True:
            msg = consommateur.poll(1.0)
            if msg is None:
                if recu and time.time() - dernier > 8:
                    break
                continue
            if msg.error():
                print("Erreur :", msg.error())
                continue
            e = json.loads(msg.value().decode("utf-8"))
            if e["type"] not in ("init", "deplacement", "contamination", "guerison"):
                continue
            recu = True
            dernier = time.time()
            if e["tour"] > tour:
                c = resume(etats)
                print(f"{tour:>4} {c['S']:>5} {c['I']:>5} {c['R']:>5}")
                tour = e["tour"]
            if e["type"] == "init":
                etats[e["habitant"]] = e["etat"]
            elif e["type"] == "contamination":
                etats[e["habitant"]] = "I"
            elif e["type"] == "guerison":
                etats[e["habitant"]] = "R"
    except KeyboardInterrupt:
        pass
    c = resume(etats)
    print(f"{tour:>4} {c['S']:>5} {c['I']:>5} {c['R']:>5}")
    consommateur.close()


if __name__ == "__main__":
    main()
