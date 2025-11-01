import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from mpl_toolkits.basemap import Basemap
from utils import cristo_algo, basemap
from genetique import genetic_tsp


# ========= Visualisation et Comparaison des Tours =========
#
# Affiche les tours trouvés par différents algorithmes
# Permet de comparer visuellement les résultats
#
# ===========================================================

POPULATION = 5
GENERATIONS = 5
MUTATION_RATE = 0.6
ELITE_SIZE = 2


def compare_plot(data, genetic_params=None):
    """
    Compare visuellement Christofides et l'algorithme génétique côte à côte.

    Args:
        data: DataFrame des villes
        genetic_params: Paramètres pour l'algorithme génétique (dict)
    """
    if genetic_params is None:
        genetic_params = {"pop_size": POPULATION, "generations": GENERATIONS, "mutation_rate": MUTATION_RATE, "elite_size": ELITE_SIZE}

    print("\n" + "="*70)
    print("COMPARAISON VISUELLE DES TOURS")
    print("="*70)

    # --- Exécuter Christofides ---
    print("\n[1/2] Exécution de Christofides...")
    result_cristo = cristo_algo(data, verbose=True)

    # --- Exécuter Génétique ---
    print("\n[2/2] Exécution de l'algorithme génétique...")
    result_genetic = genetic_tsp(data, verbose=True, **genetic_params)

    # --- Créer figure avec 2 subplots ---
    fig = plt.figure(figsize=(20, 10))

    # === CHRISTOFIDES ===
    ax1 = fig.add_subplot(121)
    plt.sca(ax1)

    pos = result_cristo["pos"]
    m1 = basemap(pos)
    


    x, y = m1([coord[0] for coord in pos.values()], [coord[1] for coord in pos.values()])
    projected_pos = {n: (x_i, y_i) for n, x_i, y_i in zip(pos.keys(), x, y)}

    G1 = nx.Graph()
    tour_cristo = result_cristo["tour"]
    tour_edges_cristo = [(tour_cristo[i], tour_cristo[i + 1]) for i in range(len(tour_cristo) - 1)]
    if tour_cristo[0] != tour_cristo[-1]:
        tour_edges_cristo.append((tour_cristo[-1], tour_cristo[0]))  # fermer le tour si nécessaire

    # Supprimer les boucles (ville → elle-même)
    tour_edges_cristo = [(u, v) for u, v in tour_edges_cristo if u != v]

    for u, v in tour_edges_cristo:
        G1.add_edge(u, v)

    nx.draw_networkx_edges(G1, projected_pos, edgelist=tour_edges_cristo,
                          edge_color='green', width=3, alpha=0.8, ax=ax1)
    nx.draw_networkx_nodes(G1, projected_pos, node_color='orange', node_size=200, ax=ax1)
    nx.draw_networkx_labels(G1, projected_pos, font_size=7, font_color='black', font_weight='bold', ax=ax1)

    ax1.set_title(f"Christofides", fontsize=12, fontweight='bold', color='green')
    
        # ---- Infos sur la population et le nombre de générations -----------
    plt.text(0.95, 0.97,
         f"Distance totale : {result_cristo['distance']:.2f} km",
         transform=plt.gca().transAxes,
         ha='right', va='top',
         color='white',
         bbox=dict(boxstyle='round,pad=0.4',
                   ec='none', facecolor='green', alpha=0.9),
         fontsize=12)

    # === GÉNÉTIQUE ===
    ax2 = fig.add_subplot(122)
    plt.sca(ax2)

    pos2 = result_genetic["pos"]
    m2 = basemap(pos2)

    x2, y2 = m2([coord[0] for coord in pos2.values()], [coord[1] for coord in pos2.values()])
    projected_pos2 = {n: (x_i, y_i) for n, x_i, y_i in zip(pos2.keys(), x2, y2)}

    G2 = nx.Graph()
    tour_genetic = result_genetic["best_tour"]
    tour_edges_genetic = [(tour_genetic[i], tour_genetic[i + 1]) for i in range(len(tour_genetic) - 1)]
    if tour_genetic[0] != tour_genetic[-1]:
        tour_edges_genetic.append((tour_genetic[-1], tour_genetic[0]))

    tour_edges_genetic = [(u, v) for u, v in tour_edges_genetic if u != v]

    for u, v in tour_edges_genetic:
        G2.add_edge(u, v)

    nx.draw_networkx_edges(G2, projected_pos2, edgelist=tour_edges_genetic,
                          edge_color='blue', width=3, alpha=0.8, ax=ax2)
    nx.draw_networkx_nodes(G2, projected_pos2, node_color='red', node_size=200, ax=ax2)
    nx.draw_networkx_labels(G2, projected_pos2, font_size=7, font_color='black', font_weight='bold', ax=ax2)

    ax2.set_title(f"Algorithme Génétique",fontsize=12, fontweight='bold', color='blue')
    
    # ---- Infos sur la population et le nombre de générations -----------
    plt.text(0.95, 0.97,
         f"Population Size : {genetic_params['pop_size']}\n"
         f"Generations : {genetic_params['generations']}\n"
         f"Distance totale : {result_genetic['best_distance']:.2f} km",
         transform=plt.gca().transAxes,
         ha='right', va='top',
         multialignment='left',       # 👈 corrige l’alignement des lignes internes
         color='white',
         bbox=dict(boxstyle='round,pad=0.4',
                   ec='none', facecolor='#1E90FF', alpha=0.9),
         fontsize=12)


    # --- Comparaison ---
    diff = result_genetic['best_distance'] - result_cristo['distance']
    diff_percent = (diff / result_cristo['distance']) * 100

    fig.suptitle(f"Comparaison TSP - 20 villes françaises - différence: {diff:+.2f} km ({diff_percent:+.2f}%)",
                fontsize=14, fontweight='bold')
    

    # plt.tight_layout()
    plt.show()

    # --- Résumé textuel ---
    print("\n" + "="*70)
    print("RÉSUMÉ DE LA COMPARAISON")
    print("="*70)
    print(f"Christofides  : {result_cristo['distance']:.2f} km")
    print(f"Génétique     : {result_genetic['best_distance']:.2f} km")
    print(f"Différence    : {diff:+.2f} km ({diff_percent:+.2f}%)")
    if diff < 0:
        print("\n🏆 Génétique a trouvé un meilleur tour !")
    elif diff > 0:
        print("\n🏆 Christofides a trouvé un meilleur tour !")
    else:
        print("\n🏆 Les deux algorithmes ont trouvé le même tour !")



if __name__ == "__main__":
    # --- Chargement des données ---
    data = pd.read_csv("data/villes.csv")

    # --- Comparaison visuelle ---
    compare_plot(
        data,
        genetic_params={"pop_size": POPULATION, "generations": GENERATIONS, "mutation_rate": MUTATION_RATE, "elite_size": ELITE_SIZE}
    )
