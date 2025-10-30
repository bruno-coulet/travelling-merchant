import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import math
from mpl_toolkits.basemap import Basemap

# =======  Liste de fonctions utilisées dans le main.py =======
# 
# haversine() permet de calculer la distance entre 2 point géographiques
# plot_graph() permet d'affciher ke graph des villes
# cristo() implémente les étapes de l'algotithme de Christofides
# 
# =============================================================



# --- Distance de Haversine entre 2 points (lat, lon) ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # rayon moyen de la Terre en km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # distance en km


def calculate_tour_distance(tour, data):
    """
    Calcule la distance totale d'un tour (circuit hamiltonien fermé).

    Args:
        tour: Liste des noms de villes dans l'ordre de visite
        data: DataFrame avec colonnes Ville, Latitude, Longitude

    Returns:
        Distance totale en km
    """
    total_distance = 0
    for i in range(len(tour)):
        city1 = tour[i]
        city2 = tour[(i + 1) % len(tour)]  # retour à la première ville

        # Récupérer les coordonnées
        lat1, lon1 = data.loc[data["Ville"] == city1, ["Latitude", "Longitude"]].values[0]
        lat2, lon2 = data.loc[data["Ville"] == city2, ["Latitude", "Longitude"]].values[0]

        total_distance += haversine(lat1, lon1, lat2, lon2)

    return total_distance
# -------------------------------------------------------





# -------- Algo de Christofides ---------

# Version modulaire Christo algorithme
def cristo_algo(data):
    # --- Graphe complet pondéré ---
    G = nx.Graph()
    for i, v1 in data.iterrows():
        for j, v2 in data.iterrows():
            if i < j:
                dist = haversine(v1["Latitude"], v1["Longitude"], v2["Latitude"], v2["Longitude"])
                G.add_edge(v1["Ville"], v2["Ville"], weight=dist)

    # ---  Minimum Spanning Tree ---
    mst = nx.minimum_spanning_tree(G, weight="weight")

    # --- Sommets de degré impair ---
    odd_nodes = [node for node in mst.nodes() if mst.degree(node) % 2 == 1]

    # --- Sous-graphe des sommets impairs ---
    odd_subgraph = G.subgraph(odd_nodes)

    # --- Minimum Weight Perfect Matching du ous-graphe ---
    matching = nx.algorithms.matching.min_weight_matching(odd_subgraph, weight="weight")

    # --- Print le résultat ---
    print("Sommets impairs :", odd_nodes)
    print("\nAppariements du MWPM :")
    for u, v in matching:
        print(f"{u} — {v} : {G[u][v]['weight']:.2f} km")

    # --- Visualisation MST + MWPM ---
    import matplotlib.pyplot as plt

    pos = {row["Ville"]: (row["Longitude"], row["Latitude"]) for _, row in data.iterrows()}

    # g_data = G, mst, matching, odd_nodes, pos
    g_data = {
        "G": G,
        "mst": mst,
        "matching": matching,
        "odd_nodes": odd_nodes,
        "pos": pos
    }
    return g_data


# Christo algorithme +  tour hamiltonien et la distance
def cristo_complete(data, verbose=False):
    """
    Algorithme de Christofides complet : retourne le tour hamiltonien et la distance.

    Args:
        data: DataFrame avec colonnes Ville, Latitude, Longitude
        verbose: Afficher les informations de progression

    Returns:
        Dictionnaire contenant:
            - tour: Tour hamiltonien (liste de villes)
            - distance: Distance totale du tour en km
            - G: Graphe complet
            - mst: Arbre couvrant minimal
            - matching: Appariement de poids minimal
            - odd_nodes: Sommets de degré impair
            - pos: Positions des villes
    """
    # --- Graphe complet pondéré ---
    G = nx.Graph()
    for i, v1 in data.iterrows():
        for j, v2 in data.iterrows():
            if i < j:
                dist = haversine(v1["Latitude"], v1["Longitude"], v2["Latitude"], v2["Longitude"])
                G.add_edge(v1["Ville"], v2["Ville"], weight=dist)

    # ---  Minimum Spanning Tree ---
    mst = nx.minimum_spanning_tree(G, weight="weight")

    # --- Sommets de degré impair ---
    odd_nodes = [node for node in mst.nodes() if mst.degree(node) % 2 == 1]

    # --- Sous-graphe des sommets impairs ---
    odd_subgraph = G.subgraph(odd_nodes)

    # --- Minimum Weight Perfect Matching du sous-graphe ---
    matching = nx.algorithms.matching.min_weight_matching(odd_subgraph, weight="weight")

    if verbose:
        print(f"\nChristofides - Sommets impairs : {len(odd_nodes)}")
        print(f"Christofides - Appariements MWPM : {len(matching)}")

    # --- Créer un multi-graphe combinant MST et MWPM ---
    multigraph = nx.MultiGraph()
    multigraph.add_edges_from(mst.edges())
    multigraph.add_edges_from(matching)

    # --- Trouver un circuit eulérien ---
    eulerian_circuit = list(nx.eulerian_circuit(multigraph))

    # --- Convertir en tour hamiltonien (supprimer les doublons) ---
    visited = set()
    hamiltonian_tour = []

    for u, v in eulerian_circuit:
        if u not in visited:
            visited.add(u)
            hamiltonian_tour.append(u)

    # --- Calculer la distance totale ---
    total_distance = calculate_tour_distance(hamiltonian_tour, data)

    if verbose:
        print(f"Christofides - Distance totale : {total_distance:.2f} km")

    pos = {row["Ville"]: (row["Longitude"], row["Latitude"]) for _, row in data.iterrows()}

    return {
        "tour": hamiltonian_tour,
        "distance": total_distance,
        "G": G,
        "mst": mst,
        "matching": matching,
        "odd_nodes": odd_nodes,
        "pos": pos
    }


# --- Affichage avec fond de carte ---
def cristo_plot(g_data, show_full=True, show_mst=True, show_matching=True, bg_color='whitesmoke', label=''):

    G = g_data["G"]
    mst = g_data["mst"]
    matching = g_data["matching"]
    odd_nodes = g_data["odd_nodes"]
    pos = g_data["pos"]

    plt.figure(figsize=(12, 10))

    # --- Création de la carte de fond ---
    m = Basemap(
        projection='merc',
        llcrnrlon=min(row[0] for row in pos.values()) - 1,
        llcrnrlat=min(row[1] for row in pos.values()) - 1,
        urcrnrlon=max(row[0] for row in pos.values()) + 1,
        urcrnrlat=max(row[1] for row in pos.values()) + 1,
        resolution='i'
    )
    m.drawcoastlines()
    m.drawcountries()
    m.fillcontinents(color=bg_color, lake_color='aqua')
    m.drawmapboundary(fill_color='aqua')

    # --- Convertir positions lat/lon en coordonnées projetées ---
    x, y = m([coord[0] for coord in pos.values()], [coord[1] for coord in pos.values()])
    projected_pos = {n: (x_i, y_i) for n, x_i, y_i in zip(G.nodes(), x, y)}

    # --- Sommets ---
    nx.draw_networkx_nodes(
        G, projected_pos,
        node_color='orange',
        node_size=250,
        label='Sommets pairs'
    )
    nx.draw_networkx_nodes(
        G, projected_pos,
        nodelist=odd_nodes,
        node_color='red',
        node_size=300,
        label='Sommets impairs'
    )

    # --- Arêtes ---
    if show_full:
        nx.draw_networkx_edges(G, projected_pos, edge_color='gray', width=2, alpha=0.5, label='Graphe complet')
    if show_mst:
        nx.draw_networkx_edges(mst, projected_pos, edge_color='green', width=3, label='MST')
    if show_matching:
        nx.draw_networkx_edges(G, projected_pos, edgelist=list(matching),
                               edge_color='red', style='dashed', width=2, label='MWPM')

    # --- Labels pour les sommets impairs ---
    odd_labels = {node: node for node in odd_nodes}
    nx.draw_networkx_labels(G, projected_pos, labels=odd_labels, font_size=9, font_color='black', font_weight='bold')

    plt.legend(loc='upper left', fontsize=9, frameon=True, fancybox=True, shadow=True)
    plt.title(f"Algorithme de Christofides - étape {label}", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.show()

# --- Affichage séquentielle pour visualiser étape par étape ---
def crist_steps(g_data):
    
    steps = [
        ("Graphe complet", True, False, False),
        ("MST - arbre couvrant minimal", False, True, False),
        ("MWPM - minimum weight perfect matching", False, False, True),
        (" fusion de MST et MWPM", False, True, True)
    ]

    for title, show_full, show_mst, show_matching in steps:
        print(f"--- {title} ---")
        cristo_plot(g_data, show_full=show_full, show_mst=show_mst, show_matching=show_matching, label=title)
        input("Appuyez sur Entrée pour passer à l'étape suivante...")

# ----------------------------------------