from monde import MondeAgents

N_TOURS = 40


def main():
    m = MondeAgents(graine=42)
    evts = m.evenements_init()
    print("tour     S     I     R  maison")
    for _ in range(N_TOURS + 1):
        c = m.compter()
        chez = sum(1 for h in m.habitants if h.lieu == "Maison")
        if m.tour % 2 == 0:
            print(f"{m.tour:>4} {c['S']:>5} {c['I']:>5} {c['R']:>5} {chez:>7}")
        if m.tour < N_TOURS:
            evts += m.avancer()

    print("\nProfils et croyances finales :")
    for h in m.habitants:
        print(f"  {h.nom:<6} {h.role:<14} confiance={h.confiance:.1f}  contact={h.croyance_contact:.2f}  puits={h.croyance_puits:.2f}  état={h.etat}")

    types, regles = {}, {}
    for e in evts:
        types[e["type"]] = types.get(e["type"], 0) + 1
        if e["type"] == "decision":
            regles[e["regle"]] = regles.get(e["regle"], 0) + 1
    print("\nÉvénements :", types)
    print("Règles appliquées :", regles)

    ilse = next(h for h in m.habitants if h.nom == "Ilse")
    print("\nMémoire d'Ilse (3 derniers souvenirs) :")
    for s in ilse.memoire[-3:]:
        print("  ", s)

    print("\nComparaison sur 200 graines (moyennes) :")
    for avec, nom in ((False, "habitudes seules"), (True, "croyances et décisions")):
        touches = pics = 0
        for g in range(200):
            mm = MondeAgents(graine=g, avec_comportement=avec)
            pic = 0
            for _ in range(N_TOURS):
                mm.avancer()
                pic = max(pic, mm.compter()["I"])
            c = mm.compter()
            touches += c["I"] + c["R"]
            pics += pic
        print(f"  {nom:<24} touchés : {touches / 200:.2f}/5   pic d'infectés : {pics / 200:.2f}")


if __name__ == "__main__":
    main()
