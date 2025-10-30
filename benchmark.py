import time
import psutil
import os
import pandas as pd
from datetime import datetime


# ========= Système de Benchmark et Comparaison =========
#
# Mesure temps d'exécution, CPU, mémoire pour les algorithmes TSP
# Enregistre les résultats dans un CSV pour analyse
#
# ========================================================


def measure_performance(algorithm_func, data, algo_name, **kwargs):
    """
    Mesure les performances d'un algorithme TSP.

    Args:
        algorithm_func: Fonction de l'algorithme à tester (cristo_complete ou genetic_tsp)
        data: DataFrame des villes
        algo_name: Nom de l'algorithme pour l'affichage
        **kwargs: Paramètres spécifiques à l'algorithme

    Returns:
        Dictionnaire avec les métriques de performance et le résultat
    """
    # --- Récupération du processus actuel ---
    process = psutil.Process(os.getpid())

    # --- Mémoire avant ---
    mem_before = process.memory_info().rss / (1024 * 1024)  # en MB

    # --- CPU avant ---
    cpu_percent_before = process.cpu_percent(interval=0.1)

    # --- Temps d'exécution ---
    start_time = time.time()

    # Exécution de l'algorithme
    result = algorithm_func(data, **kwargs)

    end_time = time.time()
    execution_time = end_time - start_time

    # --- CPU après ---
    cpu_percent_after = process.cpu_percent(interval=0.1)
    cpu_usage = (cpu_percent_before + cpu_percent_after) / 2

    # --- Mémoire après ---
    mem_after = process.memory_info().rss / (1024 * 1024)  # en MB
    mem_used = mem_after - mem_before

    # --- Extraction des résultats ---
    if "best_tour" in result:  # Génétique
        tour = result["best_tour"]
        distance = result["best_distance"]
    else:  # Christofides
        tour = result["tour"]
        distance = result["distance"]

    # --- Métriques ---
    metrics = {
        "algorithm": algo_name,
        "distance_km": round(distance, 2),
        "execution_time_s": round(execution_time, 4),
        "cpu_percent": round(cpu_usage, 2),
        "memory_mb": round(mem_used, 2),
        "memory_total_mb": round(mem_after, 2),
        "tour": tour,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Ajouter les paramètres spécifiques
    metrics.update(kwargs)

    return metrics, result


def compare_algorithms(data, genetic_params_list, save_to_csv=True, csv_filename="results/benchmark_results.csv"):
    """
    Compare Christofides avec plusieurs configurations de l'algorithme génétique.

    Args:
        data: DataFrame des villes
        genetic_params_list: Liste de dictionnaires de paramètres pour l'algorithme génétique
                            Ex: [{"pop_size": 50, "generations": 100}, {"pop_size": 100, "generations": 200}]
        save_to_csv: Sauvegarder les résultats dans un CSV
        csv_filename: Nom du fichier CSV

    Returns:
        DataFrame avec tous les résultats
    """
    from utils import cristo_complete
    from genetique import genetic_tsp

    print("\n" + "="*70)
    print("COMPARAISON DES ALGORITHMES TSP")
    print("="*70)

    results = []

    # --- Test Christofides ---
    print("\n[1/X] Exécution de Christofides...")
    metrics_cristo, result_cristo = measure_performance(
        cristo_complete,
        data,
        "Christofides",
        verbose=False
    )

    print(f"  ✓ Distance: {metrics_cristo['distance_km']} km")
    print(f"  ✓ Temps: {metrics_cristo['execution_time_s']} s")
    print(f"  ✓ CPU: {metrics_cristo['cpu_percent']}%")
    print(f"  ✓ Mémoire: {metrics_cristo['memory_mb']} MB")

    results.append(metrics_cristo)

    # --- Test Algorithme Génétique avec différents paramètres ---
    for i, params in enumerate(genetic_params_list, start=2):
        print(f"\n[{i}/{len(genetic_params_list)+1}] Exécution Génétique - {params}...")

        metrics_genetic, result_genetic = measure_performance(
            genetic_tsp,
            data,
            f"Genetique",
            verbose=False,
            **params
        )

        print(f"  ✓ Distance: {metrics_genetic['distance_km']} km")
        print(f"  ✓ Temps: {metrics_genetic['execution_time_s']} s")
        print(f"  ✓ CPU: {metrics_genetic['cpu_percent']}%")
        print(f"  ✓ Mémoire: {metrics_genetic['memory_mb']} MB")

        results.append(metrics_genetic)

    # --- Créer DataFrame ---
    df_results = pd.DataFrame(results)

    # Réorganiser les colonnes
    cols_order = ["algorithm", "distance_km", "execution_time_s", "cpu_percent", "memory_mb"]
    param_cols = [col for col in df_results.columns if col not in cols_order + ["tour", "timestamp", "memory_total_mb"]]
    cols_order.extend(param_cols)
    cols_order.extend(["memory_total_mb", "timestamp"])

    df_results = df_results[cols_order]

    # --- Sauvegarder dans CSV ---
    if save_to_csv:
        # Créer le dossier results s'il n'existe pas
        os.makedirs(os.path.dirname(csv_filename), exist_ok=True)

        # Sauvegarder
        df_results.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"\n✓ Résultats sauvegardés dans {csv_filename}")

    # --- Afficher le tableau récapitulatif ---
    print("\n" + "="*70)
    print("TABLEAU RÉCAPITULATIF")
    print("="*70)
    print(df_results[["algorithm", "distance_km", "execution_time_s", "cpu_percent", "memory_mb"]].to_string(index=False))

    # --- Analyse comparative ---
    print("\n" + "="*70)
    print("ANALYSE COMPARATIVE")
    print("="*70)

    best_distance_idx = df_results["distance_km"].idxmin()
    fastest_idx = df_results["execution_time_s"].idxmin()
    lowest_memory_idx = df_results["memory_mb"].idxmin()

    print(f"\n🏆 Meilleure distance: {df_results.loc[best_distance_idx, 'algorithm']} - {df_results.loc[best_distance_idx, 'distance_km']} km")
    print(f"⚡ Plus rapide: {df_results.loc[fastest_idx, 'algorithm']} - {df_results.loc[fastest_idx, 'execution_time_s']} s")
    print(f"💾 Moins de mémoire: {df_results.loc[lowest_memory_idx, 'algorithm']} - {df_results.loc[lowest_memory_idx, 'memory_mb']} MB")

    # Ratio de performance
    cristo_dist = df_results[df_results["algorithm"] == "Christofides"]["distance_km"].values[0]
    for idx, row in df_results[df_results["algorithm"] == "Genetique"].iterrows():
        ratio = ((row["distance_km"] - cristo_dist) / cristo_dist) * 100
        print(f"\nGénétique (gen={row.get('generations', 'N/A')}, pop={row.get('pop_size', 'N/A')}): {ratio:+.2f}% vs Christofides")

    print("\n" + "="*70)

    return df_results


def load_benchmark_history(csv_filename="results/benchmark_results.csv"):
    """
    Charge l'historique des benchmarks depuis un CSV.

    Args:
        csv_filename: Nom du fichier CSV

    Returns:
        DataFrame avec l'historique
    """
    if os.path.exists(csv_filename):
        return pd.read_csv(csv_filename)
    else:
        print(f"Fichier {csv_filename} introuvable.")
        return None


def append_to_benchmark_history(new_results, csv_filename="results/benchmark_results.csv"):
    """
    Ajoute de nouveaux résultats à l'historique existant.

    Args:
        new_results: DataFrame des nouveaux résultats
        csv_filename: Nom du fichier CSV
    """
    if os.path.exists(csv_filename):
        history = pd.read_csv(csv_filename)
        combined = pd.concat([history, new_results], ignore_index=True)
        combined.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"✓ Résultats ajoutés à {csv_filename}")
    else:
        new_results.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"✓ Nouveau fichier créé : {csv_filename}")
