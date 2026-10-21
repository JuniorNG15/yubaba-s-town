import bench_v3
import decision_v3

# v4 = v3 avec un énoncé des enjeux équilibré (sortir a des avantages, rester a un coût)
decision_v3.ENJEUX = (
    "Sortir te permet de continuer ta vie et tes activités, mais tu croises d'autres habitants : "
    "tu peux te contaminer si certains sont malades, et si tu es toi-même malade, tu peux contaminer les autres. "
    "Rester chez toi t'évite ces risques, mais tu ne vois personne et tu ne fais rien d'utile."
)

if __name__ == "__main__":
    print("Variante v4 : v3 avec enjeux équilibrés")
    bench_v3.main()
