import pandas as pd
from genetique import genetic_tsp, genetic_plot, plot_genetic_convergence

# ============ fichier principal  ===============
#
# charge le csv des villes
# teste l'algorithme genetique
#
# ================================================

# --- Chargement du CSV ---
data = pd.read_csv("data/villes.csv")

print("\n" + "="*50)
print("TEST DE L'ALGORITHME GENETIQUE")
print("="*50)

# Execution de l'algorithme genetique
result_genetic = genetic_tsp(
    data,
    pop_size=50,
    generations=100,
    mutation_rate=0.1,      # Taux de mutation 10%
    elite_size=5,           # 5 meilleurs preserves
    verbose=True            # Afficher les progres
)

# Afficher le tour trouve
print("\n" + "="*50)
print(f"ReSULTAT : {result_genetic['best_distance']:.2f} km")
print("="*50)

# Visualisation du tour
genetic_plot(result_genetic, bg_color='lightblue', show_graph=False)

# Visualisation de la convergence
plot_genetic_convergence(result_genetic['history'])
