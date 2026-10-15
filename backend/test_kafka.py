import json
import time
from confluent_kafka import Consumer, Producer

TOPIC = "evenements-monde"
SERVEUR = "localhost:9092"

# Envoi
producteur = Producer({"bootstrap.servers": SERVEUR})
evt = {"tour": 0, "habitant": "Mara", "type": "test", "message": "Bonjour Kafka"}
producteur.produce(TOPIC, key="Mara", value=json.dumps(evt, ensure_ascii=False).encode("utf-8"))
producteur.flush(10)
print("Message envoyé.")

# Lecture
consommateur = Consumer({
    "bootstrap.servers": SERVEUR,
    "group.id": "test-" + str(int(time.time())),
    "auto.offset.reset": "earliest",
})
consommateur.subscribe([TOPIC])
fin = time.time() + 15
while time.time() < fin:
    msg = consommateur.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print("Erreur :", msg.error())
        continue
    print("Message reçu :", json.loads(msg.value().decode("utf-8")))
    break
else:
    print("Aucun message reçu en 15 secondes.")
consommateur.close()
