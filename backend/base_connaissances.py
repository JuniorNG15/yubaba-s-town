import json
import math
import re
import unicodedata
from collections import Counter

import corpus

STOP = set("le la les un une des de du d l et ou en au aux a est sont que qui qu pour par sur dans ce cette ces "
           "se sa son ses ne pas plus il elle ils elles on nous vous leur leurs y mais comme avec sans si tu te "
           "ton ta tes je j m mon ma mes c s n t ai as avez avons ont fait etre avoir dois faut peut".split())


def normaliser(texte):
    t = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def tokens(texte):
    mots = re.findall(r"[a-z0-9]+", normaliser(texte))
    # racinisation très simple : les 6 premières lettres (pluriels, conjugaisons proches)
    return [m[:6] for m in mots if m not in STOP and len(m) > 1]


class BaseConnaissances:
    """Recherche lexicale BM25. Un agent ne voit que les documents publiés au plus tard au jour courant."""

    def __init__(self, chemin=corpus.CHEMIN, k1=1.5, b=0.75):
        with open(chemin, encoding="utf-8") as f:
            self.docs = [json.loads(ligne) for ligne in f if ligne.strip()]
        self.k1, self.b = k1, b
        self.tf = {d["id"]: Counter(tokens(d["titre"] + " " + d["source"] + " " + d["contenu"])) for d in self.docs}

    def visibles(self, jour):
        return [d for d in self.docs if d["jour"] <= jour]

    def rechercher(self, requete, jour, k=3):
        vus = self.visibles(jour)
        if not vus:
            return []
        n = len(vus)
        longueurs = {d["id"]: sum(self.tf[d["id"]].values()) for d in vus}
        moyenne = sum(longueurs.values()) / n
        termes = set(tokens(requete))
        resultats = []
        for d in vus:
            score = 0.0
            for t in termes:
                f = self.tf[d["id"]].get(t, 0)
                if f == 0:
                    continue
                df = sum(1 for x in vus if self.tf[x["id"]].get(t, 0) > 0)
                idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
                score += idf * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * longueurs[d["id"]] / moyenne))
            if score > 0:
                resultats.append((d, round(score, 3)))
        resultats.sort(key=lambda x: (-x[1], x[0]["jour"], x[0]["id"]))
        return resultats[:k]
