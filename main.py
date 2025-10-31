import pandas as pd
from benchmark import compare_algorithms

# ============ fichier principal  ===============
#
# Charge le CSV des villes
# Compare Christofides et Algorithme Génétique
# Avec plusieurs configurations de paramètres
#
# ================================================

# --- Chargement du CSV ---
data = pd.read_csv("data/villes.csv")

print("\n" + "="*70)
print("Travelling-merchant - résolution du TSP - COMPARAISON D'ALGORITHMES")
print(f"Nombre de villes : {len(data)}")
print("="*70)

# --- Configurations de l'algorithme génétique à tester ---
genetic_configs = [
    {"pop_size": 5, "generations": 10, "mutation_rate": 0.1, "elite_size": 5},
    {"pop_size": 10, "generations": 10, "mutation_rate": 0.1, "elite_size": 5},
    {"pop_size": 12, "generations": 10, "mutation_rate": 0.1, "elite_size": 5},
    {"pop_size": 13, "generations": 10, "mutation_rate": 0.1, "elite_size": 5},
]

# --- Lancer la comparaison ---
results_df = compare_algorithms(
    data,
    genetic_configs,
    save_to_csv=True,
    csv_filename="results/benchmark_results.csv"
)

print("\n✓ Comparaison terminée !")
print("✓ Les résultats ont été sauvegardés dans results/benchmark_results.csv")
print("\nVous pouvez maintenant :")
print("  - Ouvrir le CSV avec Excel/LibreOffice pour analyser les résultats")
print("  - Ajuster les paramètres dans main.py et relancer la comparaison")
print("  - Visualiser les tours avec visualize.py (à venir)")
