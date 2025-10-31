import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from mpl_toolkits.basemap import Basemap
from utils import cristo_complete
from genetique import genetic_tsp


# ========= Visualisation et Comparaison des Tours =========
#
# Affiche les tours trouvés par différents algorithmes
# Permet de comparer visuellement les résultats
#
# ===========================================================


def plot_tour_on_map(tour, data, distance, title, color='blue', bg_color='lightblue'):
    """
    Affiche un tour sur une carte de France.

    Args:
        tour: Liste des villes dans l'ordre de visite
        data: DataFrame des villes
        distance: Distance totale du tour
        title: Titre du graphique
        color: Couleur du tour
        bg_color: Couleur de fond
    """
    # Créer graphe pour visualisation
    G = nx.Graph()
    pos = {row["Ville"]: (row["Longitude"], row["Latitude"]) for _, row in data.iterrows()}

    plt.figure(figsize=(12, 10))

    # --- Création de la carte de fond ---
    m = Basemap(
        projection='merc',
        llcrnrlon=min(coord[0] for coord in pos.values()) - 1,
        llcrnrlat=min(coord[1] for coord in pos.values()) - 1,
        urcrnrlon=max(coord[0] for coord in pos.values()) + 1,
        urcrnrlat=max(coord[1] for coord in pos.values()) + 1,
        resolution='i'
    )
    m.drawcoastlines()
    m.drawcountries()
    m.fillcontinents(color=bg_color, lake_color='aqua')
    m.drawmapboundary(fill_color='aqua')

    # --- Convertir positions ---
    x, y = m([coord[0] for coord in pos.values()], [coord[1] for coord in pos.values()])
    projected_pos = {n: (x_i, y_i) for n, x_i, y_i in zip(pos.keys(), x, y)}

    # --- Dessiner le tour ---
    tour_edges = [(tour[i], tour[(i + 1) % len(tour)]) for i in range(len(tour))]

    # Ajouter les arêtes au graphe
    for u, v in tour_edges:
        G.add_edge(u, v)

    nx.draw_networkx_edges(G, projected_pos, edgelist=tour_edges,
                          edge_color=color, width=3, alpha=0.8)

    # --- Sommets ---
    nx.draw_networkx_nodes(G, projected_pos, node_color='red', node_size=200)

    # --- Labels ---
    nx.draw_networkx_labels(G, projected_pos, font_size=8, font_color='black', font_weight='bold')

    plt.title(f"{title}\nDistance totale: {distance:.2f} km", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.show()


def compare_tours_side_by_side(data, genetic_params=None):
    """
    Compare visuellement Christofides et l'algorithme génétique côte à côte.

    Args:
        data: DataFrame des villes
        genetic_params: Paramètres pour l'algorithme génétique (dict)
    """
    if genetic_params is None:
        genetic_params = {"pop_size": 100, "generations": 50, "mutation_rate": 0.1, "elite_size": 10}

    print("\n" + "="*70)
    print("COMPARAISON VISUELLE DES TOURS")
    print("="*70)

    # --- Exécuter Christofides ---
    print("\n[1/2] Exécution de Christofides...")
    result_cristo = cristo_complete(data, verbose=True)

    # --- Exécuter Génétique ---
    print("\n[2/2] Exécution de l'algorithme génétique...")
    result_genetic = genetic_tsp(data, verbose=True, **genetic_params)

    # --- Créer figure avec 2 subplots ---
    fig = plt.figure(figsize=(20, 10))

    # CHRISTOFIDES
    ax1 = fig.add_subplot(121)
    plt.sca(ax1)

    pos = result_cristo["pos"]
    m1 = Basemap(
        projection='merc',
        llcrnrlon=min(coord[0] for coord in pos.values()) - 1,
        llcrnrlat=min(coord[1] for coord in pos.values()) - 1,
        urcrnrlon=max(coord[0] for coord in pos.values()) + 1,
        urcrnrlat=max(coord[1] for coord in pos.values()) + 1,
        resolution='i',
        ax=ax1
    )
    m1.drawcoastlines()
    m1.drawcountries()
    m1.fillcontinents(color='lightyellow', lake_color='aqua')
    m1.drawmapboundary(fill_color='aqua')

    x, y = m1([coord[0] for coord in pos.values()], [coord[1] for coord in pos.values()])
    projected_pos = {n: (x_i, y_i) for n, x_i, y_i in zip(pos.keys(), x, y)}

    G1 = nx.Graph()
    tour_edges_cristo = [(result_cristo["tour"][i], result_cristo["tour"][(i + 1) % len(result_cristo["tour"])])
                        for i in range(len(result_cristo["tour"]))]
    for u, v in tour_edges_cristo:
        G1.add_edge(u, v)

    nx.draw_networkx_edges(G1, projected_pos, edgelist=tour_edges_cristo,
                          edge_color='green', width=3, alpha=0.8, ax=ax1)
    nx.draw_networkx_nodes(G1, projected_pos, node_color='orange', node_size=200, ax=ax1)
    nx.draw_networkx_labels(G1, projected_pos, font_size=7, font_color='black', font_weight='bold', ax=ax1)

    ax1.set_title(f"Christofides\nDistance: {result_cristo['distance']:.2f} km",
                 fontsize=12, fontweight='bold')

    # GÉNÉTIQUE
    ax2 = fig.add_subplot(122)
    plt.sca(ax2)

    pos2 = result_genetic["pos"]
    m2 = Basemap(
        projection='merc',
        llcrnrlon=min(coord[0] for coord in pos2.values()) - 1,
        llcrnrlat=min(coord[1] for coord in pos2.values()) - 1,
        urcrnrlon=max(coord[0] for coord in pos2.values()) + 1,
        urcrnrlat=max(coord[1] for coord in pos2.values()) + 1,
        resolution='i',
        ax=ax2
    )
    m2.drawcoastlines()
    m2.drawcountries()
    m2.fillcontinents(color='lightblue', lake_color='aqua')
    m2.drawmapboundary(fill_color='aqua')

    x2, y2 = m2([coord[0] for coord in pos2.values()], [coord[1] for coord in pos2.values()])
    projected_pos2 = {n: (x_i, y_i) for n, x_i, y_i in zip(pos2.keys(), x2, y2)}

    G2 = nx.Graph()
    tour_edges_genetic = [(result_genetic["best_tour"][i], result_genetic["best_tour"][(i + 1) % len(result_genetic["best_tour"])])
                         for i in range(len(result_genetic["best_tour"]))]
    for u, v in tour_edges_genetic:
        G2.add_edge(u, v)

    nx.draw_networkx_edges(G2, projected_pos2, edgelist=tour_edges_genetic,
                          edge_color='blue', width=3, alpha=0.8, ax=ax2)
    nx.draw_networkx_nodes(G2, projected_pos2, node_color='red', node_size=200, ax=ax2)
    nx.draw_networkx_labels(G2, projected_pos2, font_size=7, font_color='black', font_weight='bold', ax=ax2)

    params_str = f"pop={genetic_params['pop_size']}, gen={genetic_params['generations']}"
    ax2.set_title(f"Algorithme Génétique ({params_str})\nDistance: {result_genetic['best_distance']:.2f} km",
                 fontsize=12, fontweight='bold')

    # --- Comparaison ---
    diff = result_genetic['best_distance'] - result_cristo['distance']
    diff_percent = (diff / result_cristo['distance']) * 100

    fig.suptitle(f"Comparaison TSP - 20 villes françaises\n" +
                f"Différence: {diff:+.2f} km ({diff_percent:+.2f}%)",
                fontsize=16, fontweight='bold')

    plt.tight_layout()
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
    compare_tours_side_by_side(
        data,
        genetic_params={"pop_size": 50, "generations": 10, "mutation_rate": 0.1, "elite_size": 10}
    )
