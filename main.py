import pandas as pd
from genetique import genetic_tsp, genetic_plot, plot_genetic_convergence
from utils import cristo_algo, cristo_plot

# ============ fichier principal  ===============
#
# charge le csv des villes
# teste l'algorithme genetique
# teste l'algorithme de Christofides
#
# ================================================


POP_SIZE = 2
GENRATIONS = 4
MUTATION_RATE = 0.1       # Taux de mutation 10%
ELITE_SIZE = 3            # 3 meilleurs preserves



# --- Chargement du CSV ---
data = pd.read_csv("data/villes.csv")
# --------------------------


# ----- Execution de l'algorithme genetique  ------
print("\n" + "="*50)
print("TEST DE L'ALGORITHME GENETIQUE")
print("="*50)
result_genetic = genetic_tsp(
    data,
    pop_size=POP_SIZE,
    generations=GENRATIONS,
    mutation_rate=MUTATION_RATE,
    elite_size=ELITE_SIZE,
    verbose=True            # Afficher les progres
)

# Afficher le tour trouve
print("\n" + "="*50)
print(f"RESULTAT : {result_genetic['best_distance']:.2f} km")
print("="*50)

# Visualisation du tour
genetic_plot(result_genetic, bg_color='lightblue', show_graph=False)

# Visualisation de la convergence
plot_genetic_convergence(result_genetic['history'])
# -------------------------------------------------------

# -------- Execution de l'algo de Christofides ---------
print("\n" + "="*50)
print("TEST DE L'ALGORITHME DE CHRISTOFIDES")
print("="*50)

# Exécution de l'algo 
g_data = cristo_algo(data)
# Affichage étape par étape
cristo_plot(g_data)
# ----------------------