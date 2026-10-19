import random
from dataclasses import dataclass, field

LIEUX_PUBLICS = ["Marché", "École", "Atelier", "Dispensaire", "Puits"]
MAISON = "Maison"
MEMOIRE_MAX = 30

PROFILS = [
    # seuil = pression nécessaire pour rester chez soi (1.0 = ne reste jamais chez soi par prudence)
    dict(nom="Mara", role="soignante", quartier="haut", confiance=0.9, croyance_puits=0.2,
         croyance_contact=0.8, seuil=1.0, habituels=["Dispensaire", "Marché"]),
    dict(nom="Tomas", role="commerçant", quartier="bas", confiance=0.5, croyance_puits=0.5,
         croyance_contact=0.3, seuil=0.8, habituels=["Marché", "Puits"]),
    dict(nom="Ilse", role="parent", quartier="bas", confiance=0.6, croyance_puits=0.7,
         croyance_contact=0.5, seuil=0.3, habituels=["École", "Marché", "Puits"]),
    dict(nom="Bram", role="sceptique", quartier="bas", confiance=0.2, croyance_puits=0.3,
         croyance_contact=0.1, seuil=0.9, habituels=["Atelier", "Marché", "Puits"]),
    dict(nom="Noa", role="personne âgée", quartier="haut", confiance=0.8, croyance_puits=0.4,
         croyance_contact=0.6, seuil=0.2, habituels=["Marché", "Dispensaire", "Puits"]),
]


@dataclass
class Habitant:
    nom: str
    role: str
    quartier: str
    confiance: float          # confiance envers le dispensaire (0 à 1)
    croyance_puits: float     # croit que le puits est la source (0 à 1)
    croyance_contact: float   # croit à la transmission par contacts (0 à 1)
    seuil: float
    habituels: list
    etat: str = "S"           # S = sain, I = infecté, R = guéri
    lieu: str = MAISON
    memoire: list = field(default_factory=list)
    decision: dict = field(default_factory=dict)

    def se_souvenir(self, tour, genre, detail, importance):
        self.memoire.append({"tour": tour, "genre": genre, "detail": detail, "importance": importance})
        if len(self.memoire) > MEMOIRE_MAX:
            # on oublie d'abord le moins important, et à égalité le plus ancien
            oubli = min(self.memoire, key=lambda m: (m["importance"], m["tour"]))
            self.memoire.remove(oubli)


class MondeAgents:
    def __init__(self, beta=0.5, gamma=0.1, graine=42, delai_bulletin=2, avec_comportement=True):
        self.rng = random.Random(graine)
        self.beta = beta
        self.gamma = gamma
        self.delai_bulletin = delai_bulletin          # le dispensaire publie avec du retard
        self.avec_comportement = avec_comportement
        self.tour = 0
        self.habitants = [Habitant(**dict(p, habituels=list(p["habituels"]))) for p in PROFILS]
        self.rng.choice(self.habitants).etat = "I"
        self.historique_infectes = [1]
        self.dernier_bulletin = 0

    def compter(self):
        return {e: sum(1 for h in self.habitants if h.etat == e) for e in "SIR"}

    def evenements_init(self):
        return [{"tour": 0, "habitant": h.nom, "type": "init", "lieu": h.lieu, "etat": h.etat,
                 "role": h.role, "quartier": h.quartier} for h in self.habitants]

    def bulletin(self):
        i = self.tour - self.delai_bulletin
        return self.historique_infectes[i] if i >= 0 else 0

    def _changer(self, evts, T, h, cible, nouvelle):
        attr = "croyance_" + cible
        ancienne = getattr(h, attr)
        nouvelle = max(0.0, min(1.0, nouvelle))
        if abs(nouvelle - ancienne) >= 0.01:
            setattr(h, attr, nouvelle)
            evts.append({"tour": T, "habitant": h.nom, "type": "croyance",
                         "cible": cible, "valeur": round(nouvelle, 2)})

    def _decider(self, h, risque, a_vu_malade):
        lieux = list(h.habituels)
        if not self.avec_comportement:
            return self.rng.choice(lieux), "R0_habitude", "va dans un de ses lieux habituels"
        if h.etat == "I" and self.rng.random() < 0.6:
            return MAISON, "R1_malade", "symptômes : reste à la maison"
        pression = min(1.0, h.confiance * h.croyance_contact * risque + (0.4 if a_vu_malade else 0.0))
        if pression > h.seuil:
            return MAISON, "R2_prudence", f"pression {pression:.2f} > seuil {h.seuil:.2f}"
        if h.croyance_puits > 0.5 and "Puits" in lieux and len(lieux) > 1:
            lieux.remove("Puits")
            return self.rng.choice(lieux), "R3_evite_puits", f"croit le puits contaminé ({h.croyance_puits:.2f})"
        return self.rng.choice(lieux), "R0_habitude", "va dans un de ses lieux habituels"

    def avancer(self):
        T = self.tour + 1
        evts = []
        bulletin = self.bulletin()
        risque = min(1.0, 2.0 * bulletin / len(self.habitants))
        bulletin_nouveau = bulletin != self.dernier_bulletin
        self.dernier_bulletin = bulletin

        # 1. Le bulletin du dispensaire renforce la croyance « contacts », selon la confiance
        if self.avec_comportement and bulletin > 0:
            for h in self.habitants:
                self._changer(evts, T, h, "contact",
                              h.croyance_contact + 0.1 * h.confiance * (1 - h.croyance_contact))
                if bulletin_nouveau:
                    h.se_souvenir(T, "bulletin", f"le dispensaire déclare {bulletin} cas", 2)

        # 2. Décisions (agents à règles) et déplacements
        for h in self.habitants:
            a_vu = any(m["genre"] == "vu_malade" and m["tour"] >= self.tour - 1 for m in h.memoire)
            choix, regle, detail = self._decider(h, risque, a_vu)
            h.decision = {"tour": T, "choix": choix, "regle": regle, "detail": detail}
            evts.append({"tour": T, "habitant": h.nom, "type": "decision",
                         "choix": choix, "regle": regle, "detail": detail})
            if choix != h.lieu:
                evts.append({"tour": T, "habitant": h.nom, "type": "deplacement", "de": h.lieu, "vers": choix})
                h.lieu = choix

        # 3. Rencontres dans les lieux publics : observations et rumeur du puits
        presents = {}
        for h in self.habitants:
            if h.lieu != MAISON:
                presents.setdefault(h.lieu, []).append(h)
        for lieu, groupe in presents.items():
            for h in groupe:
                autres = [x for x in groupe if x is not h]
                if not autres:
                    continue
                malade = next((x for x in autres if x.etat == "I"), None)
                if malade:
                    h.se_souvenir(T, "vu_malade", f"{malade.nom} semble malade ({lieu})", 2)
                if self.avec_comportement:
                    parleur = self.rng.choice(autres)
                    nouvelle = h.croyance_puits + 0.3 * (parleur.croyance_puits - h.croyance_puits) * (1 - 0.5 * h.confiance)
                    self._changer(evts, T, h, "puits", nouvelle)
                    h.se_souvenir(T, "conversation", f"a parlé avec {parleur.nom} ({lieu})", 1)

        # 4. Santé : contamination dans les lieux publics seulement, puis guérisons
        infectes_par_lieu = {}
        for h in self.habitants:
            if h.etat == "I" and h.lieu != MAISON:
                infectes_par_lieu[h.lieu] = infectes_par_lieu.get(h.lieu, 0) + 1
        nouveaux = [h for h in self.habitants
                    if h.etat == "S" and h.lieu != MAISON and infectes_par_lieu.get(h.lieu, 0) > 0
                    and self.rng.random() < 1 - (1 - self.beta) ** infectes_par_lieu[h.lieu]]
        for h in self.habitants:
            if h.etat == "I" and self.rng.random() < self.gamma:
                h.etat = "R"
                evts.append({"tour": T, "habitant": h.nom, "type": "guerison", "lieu": h.lieu})
        for h in nouveaux:
            h.etat = "I"
            evts.append({"tour": T, "habitant": h.nom, "type": "contamination", "lieu": h.lieu})

        self.tour = T
        self.historique_infectes.append(self.compter()["I"])
        return evts
