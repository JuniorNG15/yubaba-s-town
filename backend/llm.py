import json
import os
import time
import urllib.error
import urllib.request

URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODELE = os.environ.get("OLLAMA_MODELE", "qwen2.5:1.5b-instruct")


def modeles():
    """Liste des modèles installés, ou None si Ollama ne répond pas."""
    try:
        with urllib.request.urlopen(URL + "/api/tags", timeout=3) as r:
            return [m["name"] for m in json.load(r).get("models", [])]
    except (urllib.error.URLError, OSError, ValueError):
        return None


def decider(systeme, question, options, timeout=120):
    """Demande un choix parmi `options`. Ne lève jamais d'exception : renvoie un dict."""
    schema = {
        "type": "object",
        "properties": {
            "choix": {"type": "string", "enum": list(options)},
            "raison": {"type": "string"},
        },
        "required": ["choix", "raison"],
    }
    corps = {
        "model": MODELE,
        "stream": False,
        "format": schema,
        "keep_alive": "10m",
        "options": {"temperature": 0, "seed": 42, "num_predict": 150, "num_ctx": 2048},
        "messages": [
            {"role": "system", "content": systeme},
            {"role": "user", "content": question},
        ],
    }
    requete = urllib.request.Request(
        URL + "/api/chat",
        data=json.dumps(corps).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    debut = time.time()

    def ms():
        return int((time.time() - debut) * 1000)

    try:
        with urllib.request.urlopen(requete, timeout=timeout) as r:
            contenu = json.load(r)["message"]["content"]
        obj = json.loads(contenu)
        choix = obj["choix"]
        raison = " ".join(str(obj["raison"]).split())
        if choix not in options:
            return {"ok": False, "erreur": f"choix invalide : {choix!r}", "ms": ms()}
        return {"ok": True, "choix": choix, "raison": raison[:140], "ms": ms()}
    except (urllib.error.URLError, OSError) as e:
        return {"ok": False, "erreur": f"Ollama injoignable ({e})", "ms": ms()}
    except (KeyError, ValueError, TypeError) as e:
        return {"ok": False, "erreur": f"réponse inexploitable ({e})", "ms": ms()}
