import time
import psutil
import os
import pandas as pd
import statistics
from datetime import datetime




# ========= Système de Benchmark et Comparaison =========
#
# Mesure temps d'exécution, CPU, mémoire pour les algorithmes TSP
# Enregistre les résultats dans un CSV pour analyse
#
# ========================================================


def measure_performance(algorithm_func, data, algo_name, min_total_wall_time=2, max_iters_cap=1000, **kwargs):
    """
    Mesure les performances d'un algorithme TSP en amortissant les répétitions.

    Args:
        algorithm_func: fonction à exécuter
        data: données d'entrée
        algo_name: nom pour l'affichage
        min_total_wall_time: durée mur minimale cumulée (s) à atteindre
        max_iters_cap: nombre maximal d'itérations
        **kwargs: paramètres supplémentaires passés à l'algorithme

    Returns:
        (metrics_dict, representative_result)
    """
    process = psutil.Process(os.getpid())
    # mémoire avant les itérations (RSS en MB) — utilisée pour estimer delta mémoire
    try:
        mem_before = process.memory_info().rss / (1024 * 1024)
    except Exception:
        mem_before = None

    wall_times = []
    cpu_times = []
    cpu_parent_list = []
    cpu_children_list = []
    thread_totals = []
    thread_deltas_last = []
    # nombre de threads actifs par itération (d > 0)
    active_threads_counts = []
    # pour l'agrégation par-thread sur toutes les itérations
    thread_deltas_by_tid = {}
    # mesures mémoire par itération (RSS en MB)
    mem_rss_list = []

    iters = 0
    wall_accum = 0.0

    representative_result = None
    representative_tour = None
    representative_distance = None
    best_distance_overall = float('inf')
    best_result_overall = None

    # boucle d'amortissement
    while (wall_accum < min_total_wall_time) and (iters < max_iters_cap):
        iters += 1

        # captures before
        try:
            cpu_parent_before = sum(process.cpu_times()[:2])
        except Exception:
            cpu_parent_before = 0.0

        children_before = {}
        try:
            for c in process.children(recursive=True):
                try:
                    cct = c.cpu_times()
                    children_before[c.pid] = cct.user + cct.system
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            children_before = {}

        threads_before = {}
        try:
            for t in process.threads():
                threads_before[t.id] = (getattr(t, 'user_time', 0.0) + getattr(t, 'system_time', 0.0))
        except Exception:
            threads_before = {}

        t0 = time.time()
        res = algorithm_func(data, **kwargs)
        t1 = time.time()

        try:
            cpu_parent_after = sum(process.cpu_times()[:2])
        except Exception:
            cpu_parent_after = 0.0

        children_after = {}
        try:
            for c in process.children(recursive=True):
                try:
                    cct = c.cpu_times()
                    children_after[c.pid] = cct.user + cct.system
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            children_after = {}

        threads_after = {}
        try:
            for t in process.threads():
                threads_after[t.id] = (getattr(t, 'user_time', 0.0) + getattr(t, 'system_time', 0.0))
        except Exception:
            threads_after = {}

        parent_delta = max(0.0, cpu_parent_after - cpu_parent_before)
        children_delta = 0.0
        for pid, after_val in children_after.items():
            before_val = children_before.get(pid)
            if before_val is not None:
                children_delta += max(0.0, after_val - before_val)
            else:
                children_delta += max(0.0, after_val)

        total_cpu = max(0.0, parent_delta + children_delta)

        # threads deltas
        t_deltas = []
        t_sum = 0.0
        try:
            for tid, av in threads_after.items():
                bv = threads_before.get(tid, 0.0)
                d = max(0.0, av - bv)
                if d > 0 or tid in threads_before:
                    t_deltas.append((tid, round(d, 6)))
                    t_sum += d
        except Exception:
            t_deltas = []
            t_sum = 0.0

        # compter threads actifs cette itération
        try:
            active_count = sum(1 for _, d in t_deltas if d > 0)
            active_threads_counts.append(active_count)
        except Exception:
            active_threads_counts.append(0)

        # enregistrer deltas par thread pour moyennes sur itérations
        try:
            for tid, d in t_deltas:
                thread_deltas_by_tid.setdefault(tid, []).append(d)
        except Exception:
            pass

        wall = t1 - t0
        wall_times.append(wall)
        cpu_times.append(total_cpu)
        cpu_parent_list.append(parent_delta)
        cpu_children_list.append(children_delta)
        thread_totals.append(t_sum)
        thread_deltas_last = t_deltas

        # mémoire après cette itération
        try:
            mem_rss_list.append(process.memory_info().rss / (1024 * 1024))
        except Exception:
            pass

        wall_accum += wall

        if isinstance(res, dict):
            current_distance = res.get('best_distance') or res.get('distance')
            if current_distance is not None and current_distance < best_distance_overall:
                best_distance_overall = current_distance
                best_result_overall = res


    # agrégation
    iterations = iters
    wall_mean = statistics.mean(wall_times) if wall_times else 0.0
    wall_std = statistics.pstdev(wall_times) if len(wall_times) > 1 else 0.0
    cpu_mean = statistics.mean(cpu_times) if cpu_times else 0.0
    cpu_std = statistics.pstdev(cpu_times) if len(cpu_times) > 1 else 0.0
    thread_total_mean = statistics.mean(thread_totals) if thread_totals else 0.0
    thread_total_std = statistics.pstdev(thread_totals) if len(thread_totals) > 1 else 0.0
    active_threads_mean = statistics.mean(active_threads_counts) if active_threads_counts else 0.0
    active_threads_std = statistics.pstdev(active_threads_counts) if len(active_threads_counts) > 1 else 0.0

    mem_after = process.memory_info().rss / (1024 * 1024)  # en MB
    # calculer moyenne et std de la mémoire observée durant les itérations
    mem_mean = statistics.mean(mem_rss_list) if mem_rss_list else mem_after
    mem_std = statistics.pstdev(mem_rss_list) if len(mem_rss_list) > 1 else 0.0
    mem_used = mem_mean - (locals().get('mem_before', mem_mean))

    cpu_cores = os.cpu_count() or 1
    cpu_percent_mean = (cpu_mean / wall_mean) * 100 if wall_mean > 0 else 0.0
    cpu_percent_per_core = cpu_percent_mean / cpu_cores

    # sanity / tick estimate: rassembler toutes les petites valeurs non-nulles observées
    observed_nonzero = []
    observed_nonzero.extend([v for v in cpu_times if v > 0])
    observed_nonzero.extend([d for lst in thread_deltas_by_tid.values() for d in lst if d > 0])
    cpu_tick_min = None
    cpu_tick_max = None
    cpu_tick_median = None
    cpu_tick_samples = len(observed_nonzero)
    if observed_nonzero:
        cpu_tick_min = round(min(observed_nonzero), 6)
        cpu_tick_max = round(max(observed_nonzero), 6)
        try:
            cpu_tick_median = round(statistics.median(observed_nonzero), 6)
        except Exception:
            cpu_tick_median = cpu_tick_min

    delta_diff = round(cpu_mean - thread_total_mean, 6)
    alert_threshold = max(0.005, 0.02 * cpu_mean)
    delta_flag = abs(delta_diff) > alert_threshold
    representative_result = best_result_overall
    representative_distance = best_distance_overall
    representative_tour = best_result_overall.get('best_tour') or best_result_overall.get('tour') if best_result_overall else None

    tour = representative_tour
    distance = representative_distance

    # if only one iteration, don't traiter tick comme estimation fiable
    if iterations <= 1:
        cpu_tick_min = None
        cpu_tick_max = None
        cpu_tick_median = None
        cpu_tick_samples = 0


    # metrics (compatibilité ascendante : inclure anciennes clés simples)
    metrics = {
        'algorithm': algo_name,
        'distance_km': round(representative_distance, 2) if representative_distance is not None else None,
        'execution_time_s_mean': round(wall_mean, 6),
        'execution_time_s_std': round(wall_std, 6),
        'execution_time_s': round(wall_mean, 6),
        'cpu_time_seconds_mean': round(cpu_mean, 6),
        'cpu_time_seconds_std': round(cpu_std, 6),
        'cpu_time_seconds': round(cpu_mean, 6),
        'cpu_parent_seconds_mean': round(statistics.mean(cpu_parent_list), 6) if cpu_parent_list else 0.0,
        'cpu_children_seconds_mean': round(statistics.mean(cpu_children_list), 6) if cpu_children_list else 0.0,
        'cpu_percent': round(cpu_percent_mean, 2),
        'cpu_percent_per_core': round(cpu_percent_per_core, 2),
        'cpu_cores': cpu_cores,
        'num_threads': process.num_threads() if hasattr(process, 'num_threads') else None,
        'thread_cpu_seconds_total_mean': round(thread_total_mean, 6),
        'thread_cpu_seconds_total': round(thread_total_mean, 6),
    'thread_cpu_seconds_total_std': round(thread_total_std, 6),
    'thread_cpu_deltas_last': str(thread_deltas_last),
    # moyennes par thread (tid -> mean,std)
    'thread_cpu_deltas_mean': {tid: (round(statistics.mean(lst), 6), round(statistics.pstdev(lst) if len(lst) > 1 else 0.0, 6)) for tid, lst in thread_deltas_by_tid.items()},
        'iterations': iterations,
    'amortized': True if iterations > 1 else False,
    'min_total_wall_time': min_total_wall_time,
    'active_threads_mean': round(active_threads_mean, 6),
    'active_threads_std': round(active_threads_std, 6),
    'active_threads_last': active_threads_counts[-1] if active_threads_counts else 0,
    'cpu_delta_diff': delta_diff,
    'cpu_delta_diff_flag': delta_flag,
    'cpu_tick_min': cpu_tick_min,
    'cpu_tick_max': cpu_tick_max,
    'cpu_tick_median': cpu_tick_median,
    'cpu_tick_samples': cpu_tick_samples,
    'memory_mb_mean': round(mem_mean, 6),
    'memory_mb_std': round(mem_std, 6),
    'memory_mb_used_estimate': round(mem_used, 6),
    'memory_total_mb': round(mem_after, 6),
        'tour': tour,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # ajouter paramètres
    metrics.update(kwargs)

    return metrics, representative_result


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
    from genetique import genetic_tsp, compute_distance_matrix
    matrix = compute_distance_matrix(data)


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

    print(f"  ✓ Meilleuresistance: {metrics_cristo['distance_km']} km")
    # Afficher temps / CPU avec précision si les mesures sont amorties
    if metrics_cristo.get('amortized'):
        print(f"  ✓ Temps (moyenne ± écart‑type) : {metrics_cristo.get('execution_time_s_mean')} ± {metrics_cristo.get('execution_time_s_std')} s — sur {metrics_cristo.get('iterations')} exécutions (seuil d'amortissement = {metrics_cristo.get('min_total_wall_time')} s)")
        print(f"  ✓ CPU (moyenne ± écart‑type) : {metrics_cristo.get('cpu_time_seconds_mean')} ± {metrics_cristo.get('cpu_time_seconds_std')} s ({metrics_cristo.get('cpu_percent', 'N/A')}% | {metrics_cristo.get('cpu_percent_per_core', 'N/A')}%/coeur) sur {metrics_cristo.get('cpu_cores', 'N/A')} cœurs")
    else:
        print(f"  ✓ Temps (exécution unique) : {metrics_cristo.get('execution_time_s')} s — 1 exécution")
        print(f"  ✓ CPU (exécution unique) : {metrics_cristo.get('cpu_time_seconds')} s CPU total ({metrics_cristo.get('cpu_percent','N/A')}% | {metrics_cristo.get('cpu_percent_per_core','N/A')}%/coeur) sur {metrics_cristo.get('cpu_cores','N/A')} cœurs")
    # Mémoire : afficher moyenne ± std si disponible (formaté)
    mem_mean = metrics_cristo.get('memory_mb_mean')
    mem_std = metrics_cristo.get('memory_mb_std')
    mem_used_est = metrics_cristo.get('memory_mb_used_estimate')
    if mem_mean is not None:
        try:
            mem_mean_f = float(mem_mean)
            mem_std_f = float(mem_std)
        except Exception:
            mem_mean_f = mem_mean
            mem_std_f = mem_std
        if mem_used_est is not None and abs(float(mem_used_est)) >= 0.01:
            print(f"  ✓ Mémoire (RSS moy ± écart‑type) : {mem_mean_f:.2f} ± {mem_std_f:.2f} MB — augmentation estimée {float(mem_used_est):.2f} MB")
        else:
            print(f"  ✓ Mémoire (RSS moy ± écart‑type) : {mem_mean_f:.2f} ± {mem_std_f:.2f} MB")
    else:
        print(f"  ✓ Mémoire: {metrics_cristo.get('memory_total_mb','N/A')} MB")
    # afficher nombre de threads total et nombre moyen de threads actifs
    print(f"  ✓ Threads (total): {metrics_cristo.get('num_threads','N/A')} — threads actifs (moy ± std): {metrics_cristo.get('active_threads_mean','N/A'):.2f} ± {metrics_cristo.get('active_threads_std','N/A'):.2f} (dernier: {metrics_cristo.get('active_threads_last','N/A')})")
    # Afficher breakdown parent / enfants / threads
    # Afficher breakdown parent / enfants / threads (utiliser les moyennes calculées)
    # Afficher breakdown parent/enfants/threads (préciser si moyennes ou single-run)
    if metrics_cristo.get('amortized'):
        print(f"  ✓ CPU parent (s) — moyenne : {metrics_cristo.get('cpu_parent_seconds_mean', 'N/A')}")
        print(f"  ✓ CPU enfants (s) — moyenne : {metrics_cristo.get('cpu_children_seconds_mean', 'N/A')}")
        print(f"  ✓ Détail threads (deltas en s) — dernière itération : {metrics_cristo.get('thread_cpu_deltas_last','N/A')}")
        print(f"  ✓ Threads — somme CPU (s) moyenne : {metrics_cristo.get('thread_cpu_seconds_total','N/A')}")
        print(f"  ✓ Écart (cpu_total - somme_thread_deltas) — moyenne : {metrics_cristo.get('cpu_delta_diff','N/A')} s")
        # afficher estimation de résolution (min et médiane des deltas non nuls) si suffisant
        tick_min = metrics_cristo.get('cpu_tick_min')
        tick_med = metrics_cristo.get('cpu_tick_median')
        tick_max = metrics_cristo.get('cpu_tick_max')
        tick_samples = metrics_cristo.get('cpu_tick_samples', 0)
        if tick_min is not None and tick_samples >= 3:
            print(f"  ✓ Résolution estimée — min : {tick_min:.3f} s, médiane : {tick_med:.3f} s, max : {tick_max:.3f} s (échantillons non nuls = {tick_samples})")
        else:
            print("  ✓ Résolution estimée : N/A (échantillons insuffisants)")
        # afficher moyennes par thread (filtrer threads inactifs)
        thread_means = metrics_cristo.get('thread_cpu_deltas_mean', {}) or {}
        active_threads = {tid: vals for tid, vals in thread_means.items() if vals[0] > 0}
        if active_threads:
            formatted = ", ".join([f"{tid}: {vals[0]:.3f}±{vals[1]:.3f}s" for tid, vals in active_threads.items()])
            print(f"  ✓ Détail threads (moy ± std) — threads actifs : {formatted}")
        else:
            print("  ✓ Détail threads (moy ± std) — aucun thread actif détecté")
    else:
        print(f"  ✓ CPU parent (s) — exécution unique : {metrics_cristo.get('cpu_parent_seconds_mean', 'N/A')}")
        print(f"  ✓ CPU enfants (s) — exécution unique : {metrics_cristo.get('cpu_children_seconds_mean', 'N/A')}")
        print(f"  ✓ Détail threads (deltas en s) — exécution unique : {metrics_cristo.get('thread_cpu_deltas_last','N/A')}")
        print(f"  ✓ Threads — somme CPU (s) — exécution unique : {metrics_cristo.get('thread_cpu_seconds_total','N/A')}")
        print(f"  ✓ Écart (cpu_total - somme_thread_deltas) — exécution unique : {metrics_cristo.get('cpu_delta_diff','N/A')} s")
        print("  ✓ Résolution estimée : N/A (exécution unique — pas d'estimation fiable)")

    results.append(metrics_cristo)

    # --- Test Algorithme Génétique avec différents paramètres ---
    for i, params in enumerate(genetic_params_list, start=2):
        print(f"\n[{i}/{len(genetic_params_list)+1}] Exécution Génétique - {params}...")

        metrics_genetic, result_genetic = measure_performance(
            lambda d, **kw: genetic_tsp(d, matrix=matrix, **kw),
            data,
            f"Genetique",
            verbose=False,
            **params
        )

        print(f"  ✓ Distance: {metrics_genetic['distance_km']} km")
        # Afficher temps / CPU avec indication amortisée vs single-run
        if metrics_genetic.get('amortized'):
            print(f"  ✓ Temps (moyenne ± écart‑type) : {metrics_genetic.get('execution_time_s_mean')} ± {metrics_genetic.get('execution_time_s_std')} s — sur {metrics_genetic.get('iterations')} exécutions (seuil d'amortissement = {metrics_genetic.get('min_total_wall_time')} s)")
            print(f"  ✓ CPU (moyenne ± écart‑type) : {metrics_genetic.get('cpu_time_seconds_mean')} ± {metrics_genetic.get('cpu_time_seconds_std')} s ({metrics_genetic.get('cpu_percent', 'N/A')}% | {metrics_genetic.get('cpu_percent_per_core', 'N/A')}%/coeur) sur {metrics_genetic.get('cpu_cores', 'N/A')} cœurs")
        else:
            print(f"  ✓ Temps (exécution unique) : {metrics_genetic.get('execution_time_s')} s — 1 exécution")
            print(f"  ✓ CPU (exécution unique) : {metrics_genetic.get('cpu_time_seconds')} s CPU total ({metrics_genetic.get('cpu_percent','N/A')}% | {metrics_genetic.get('cpu_percent_per_core','N/A')}%/coeur) sur {metrics_genetic.get('cpu_cores','N/A')} cœurs")
        # Mémoire : afficher moyenne ± std si disponible (formaté)
        mem_mean_g = metrics_genetic.get('memory_mb_mean')
        mem_std_g = metrics_genetic.get('memory_mb_std')
        mem_used_est_g = metrics_genetic.get('memory_mb_used_estimate')
        if mem_mean_g is not None:
            try:
                mem_mean_fg = float(mem_mean_g)
                mem_std_fg = float(mem_std_g)
            except Exception:
                mem_mean_fg = mem_mean_g
                mem_std_fg = mem_std_g
            if mem_used_est_g is not None and abs(float(mem_used_est_g)) >= 0.01:
                print(f"  ✓ Mémoire (RSS moy ± écart‑type) : {mem_mean_fg:.2f} ± {mem_std_fg:.2f} MB — variation estimée {float(mem_used_est_g):.2f} MB")
            else:
                print(f"  ✓ Mémoire (RSS moy ± écart‑type) : {mem_mean_fg:.2f} ± {mem_std_fg:.2f} MB")
        else:
            print(f"  ✓ Mémoire: {metrics_genetic.get('memory_total_mb','N/A')} MB")
        print(f"  ✓ Threads (total): {metrics_genetic.get('num_threads','N/A')} — threads actifs (moy ± std): {metrics_genetic.get('active_threads_mean','N/A'):.2f} ± {metrics_genetic.get('active_threads_std','N/A'):.2f} (dernier: {metrics_genetic.get('active_threads_last','N/A')})")
        # Afficher breakdown parent / enfants / threads
        print(f"  ✓ CPU parent (s) (moy): {metrics_genetic.get('cpu_parent_seconds_mean','N/A')}")
        print(f"  ✓ CPU enfants (s) (moy): {metrics_genetic.get('cpu_children_seconds_mean','N/A')}")
        print(f"  ✓ Thread breakdown (deltas en s) (dernière itération): {metrics_genetic.get('thread_cpu_deltas_last','N/A')}")
        print(f"  ✓ Threads CPU total (s) (moy): {metrics_genetic.get('thread_cpu_seconds_total','N/A')}")
        print(f"  ✓ Diff CPU total - sum(thread_deltas) (moy): {metrics_genetic.get('cpu_delta_diff','N/A')} s")
        tick_min_g = metrics_genetic.get('cpu_tick_min')
        tick_med_g = metrics_genetic.get('cpu_tick_median')
        tick_samples_g = metrics_genetic.get('cpu_tick_samples', 0)
        if tick_min_g is not None and tick_samples_g >= 3:
            print(f"  ✓ Résolution estimée — min : {tick_min_g:.3f} s, médiane : {tick_med_g:.3f} s (échantillons non nuls = {tick_samples_g})")
        else:
            print("  ✓ Résolution estimée : N/A (échantillons insuffisants)")
        thread_means_g = metrics_genetic.get('thread_cpu_deltas_mean', {}) or {}
        active_threads_g = {tid: vals for tid, vals in thread_means_g.items() if vals[0] > 0}
        if active_threads_g:
            formatted_g = ", ".join([f"{tid}: {vals[0]:.3f}±{vals[1]:.3f}s" for tid, vals in active_threads_g.items()])
            print(f"  ✓ Détail threads (moy ± std) — threads actifs : {formatted_g}")
        else:
            print("  ✓ Détail threads (moy ± std) — aucun thread actif détecté")
        if metrics_genetic.get('cpu_delta_diff_flag'):
            print("  ⚠️  Alerte: écart significatif entre cpu_time_seconds et somme des thread deltas (voir cpu_delta_diff)")

        results.append(metrics_genetic)

    # --- Créer DataFrame ---
    df_results = pd.DataFrame(results)

    # Réorganiser les colonnes (priorité aux métriques temporelles et CPU)
    cols_order = [
        "algorithm",
        "distance_km",
        "execution_time_s",
        "iterations",
        "cpu_time_seconds",
        "cpu_percent",
        "cpu_percent_per_core",
        "cpu_cores",
        "num_threads",
        "memory_mb",
    ]
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
    display_cols = ["algorithm", "distance_km", "execution_time_s", "cpu_time_seconds", "cpu_percent", "memory_mb"]
    # Certains runs peuvent ne pas contenir toutes les colonnes (sécurité)
    display_cols = [c for c in display_cols if c in df_results.columns]
    print(df_results[display_cols].to_string(index=False))

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
