import random
import sys
from dataclasses import dataclass

LIEUX = ["Marché", "École", "Atelier", "Dispensaire", "Puits"]


@dataclass
class Habitant:
    nom: str
    etat: str = "S"  # S = sain, I = infecté, R = guéri
    lieu: str = "Marché"


class Monde:
    def __init__(self, noms, beta=0.5, gamma=0.1, graine=42, infectes_initiaux=1):
        self.rng = random.Random(graine)  # graine fixe = résultats reproductibles
        self.beta = beta    # probabilité de contamination par infecté présent
        self.gamma = gamma  # probabilité de guérison par tour
        self.tour = 0
        self.habitants = [Habitant(nom, lieu=self.rng.choice(LIEUX)) for nom in noms]
        for h in self.rng.sample(self.habitants, infectes_initiaux):
            h.etat = "I"

    def compter(self):
        return {e: sum(1 for h in self.habitants if h.etat == e) for e in "SIR"}

    def avancer(self):
        # 1. Déplacements
        for h in self.habitants:
            h.lieu = self.rng.choice(LIEUX)

        # 2. Nombre d'infectés dans chaque lieu
        infectes_par_lieu = {lieu: 0 for lieu in LIEUX}
        for h in self.habitants:
            if h.etat == "I":
                infectes_par_lieu[h.lieu] += 1

        # 3. Qui est contaminé ce tour
        nouveaux = []
        for h in self.habitants:
            n = infectes_par_lieu[h.lieu]
            if h.etat == "S" and n > 0 and self.rng.random() < 1 - (1 - self.beta) ** n:
                nouveaux.append(h)

        # 4. Guérisons, puis mise à jour des nouveaux infectés
        for h in self.habitants:
            if h.etat == "I" and self.rng.random() < self.gamma:
                h.etat = "R"
        for h in nouveaux:
            h.etat = "I"

        self.tour += 1


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    noms = (["Mara", "Tomas", "Ilse", "Bram", "Noa"] + [f"Hab{i}" for i in range(6, n + 1)])[:n]
    beta = 0.5 if n <= 10 else 0.05  # moins contagieux quand la ville est grande
    monde = Monde(noms, beta=beta)

    print(f"{n} habitants, beta={beta}, gamma={monde.gamma}")
    print("tour     S     I     R")
    for _ in range(41):
        c = monde.compter()
        assert sum(c.values()) == n  # personne ne disparaît
        print(f"{monde.tour:>4} {c['S']:>5} {c['I']:>5} {c['R']:>5}")
        monde.avancer()


if __name__ == "__main__":
    main()
