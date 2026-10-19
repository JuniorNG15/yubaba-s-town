import sys


def patcher(chemin, deja, remplacements):
    with open(chemin, encoding="utf-8", newline=None) as f:
        texte = f.read()
    if deja in texte:
        print("Deja applique, rien a faire :", chemin)
        return
    for ancien, nouveau in remplacements:
        n = texte.count(ancien)
        if n != 1:
            print(f"ERREUR {chemin} : motif trouve {n} fois : {ancien!r}")
            sys.exit(1)
        texte = texte.replace(ancien, nouveau)
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(texte)
    print("OK", chemin)


patcher("backend/monde.py", "nouveaux: list", [
    ("    decision: dict = field(default_factory=dict)\n",
     "    decision: dict = field(default_factory=dict)\n    nouveaux: list = field(default_factory=list)\n"),
    ('        self.memoire.append({"tour": tour, "genre": genre, "detail": detail, "importance": importance})\n',
     '        self.memoire.append({"tour": tour, "genre": genre, "detail": detail, "importance": importance})\n'
     '        if importance >= 2:\n            self.nouveaux.append(self.memoire[-1])\n'),
    ("        self.tour = T\n",
     "        for h in self.habitants:\n"
     "            for m in h.nouveaux:\n"
     '                evts.append({"tour": T, "habitant": h.nom, "type": "souvenir", "genre": m["genre"], "detail": m["detail"]})\n'
     "            h.nouveaux.clear()\n"
     "        self.tour = T\n"),
])
patcher("backend/pont.py", '"souvenir"', [
    ('"decision", "croyance")', '"decision", "croyance", "souvenir")'),
])
