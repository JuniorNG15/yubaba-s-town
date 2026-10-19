import json
import socket
import time

from confluent_kafka import Consumer

TOPIC = "evenements-monde"
SERVEUR_KAFKA = "localhost:9092"
HOTE, PORT = "127.0.0.1", 8765
TYPES = ("init", "deplacement", "contamination", "guerison", "decision", "croyance")


def servir(client):
    """Relit tout le topic depuis le début et le transmet à Godot."""
    consommateur = Consumer({
        "bootstrap.servers": SERVEUR_KAFKA,
        "group.id": "pont-" + str(int(time.time())),
        "auto.offset.reset": "earliest",
    })
    consommateur.subscribe([TOPIC])
    envoyes = 0
    try:
        while True:
            msg = consommateur.poll(0.5)
            if msg is None:
                continue
            if msg.error():
                print("Erreur Kafka :", msg.error())
                continue
            valeur = msg.value()
            if json.loads(valeur.decode("utf-8")).get("type") not in TYPES:
                continue
            client.sendall(valeur + b"\n")
            envoyes += 1
    except OSError:
        print(f"Godot s'est déconnecté ({envoyes} événements transmis).")
    finally:
        consommateur.close()
        client.close()


def main():
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serveur.bind((HOTE, PORT))
    serveur.listen(1)
    serveur.settimeout(1.0)
    print(f"Pont prêt sur {HOTE}:{PORT}. En attente de Godot... (Ctrl+C pour quitter)")
    try:
        while True:
            try:
                client, _ = serveur.accept()
            except socket.timeout:
                continue
            print("Godot connecté.")
            servir(client)
            print("En attente de Godot...")
    except KeyboardInterrupt:
        print("Arrêt du pont.")
    finally:
        serveur.close()


if __name__ == "__main__":
    main()

