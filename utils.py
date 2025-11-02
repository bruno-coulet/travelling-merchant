import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import math
import seaborn as sns
from mpl_toolkits.basemap import Basemap

# =======  Liste de fonctions utilisées dans le main.py =======
# 
# haversine().......... calcule la distance entre 2 point géographiques
# basemap()............ crée une carte de fond
# cristo_algo()........ implémente les étapes de l'algorithme de Christofides
# cristo_plot()........ affiche l'algorithme de Christofides sur le fond de carte
# cristo_step()........ décompose et affiche l'algorithme de Christofides sur le fond de carte
#
# =============================================================


# ------  palette de couleurs personnalisée  ------
# Sélectionne des couleurs
land_color = sns.color_palette("OrRd", 10)[0]
odd_color = sns.color_palette("OrRd", 10)[6]
cristofides_color = sns.color_palette("Greens", 10)[6]
sea_color = sns.color_palette("Blues", 10)[1]
genetic_color = sns.color_palette("Blues", 10)[8]
even_color = sns.color_palette("Oranges", 10)[6]
# Crée une palette personnalisée avec ces couleurs
ma_palette = [land_color, sea_color, odd_color, genetic_color, cristofides_color, even_color]
# Affiche la plalette personnalisée
# sns.palplot(ma_palette)



# --- Distance de Haversine entre 2 points (lat, lon) ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # rayon moyen de la Terre en km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c  # distance en km



# --- Création de la carte de fond ---
def basemap(pos):
    lons = [coord[0] for coord in pos.values()]
    lats = [coord[1] for coord in pos.values()]
    m = Basemap(
        projection='merc',
        llcrnrlon=min(lons) - 1,
        llcrnrlat=min(lats) - 1,
        urcrnrlon=max(lons) + 1,
        urcrnrlat=max(lats) + 1,
        resolution='i'
    )
    m.drawcoastlines()
    m.drawcountries()
    m.fillcontinents(color=land_color, lake_color=sea_color)
    m.drawmapboundary(fill_color=sea_color)
    return m

# -------- Algo de Christofides ---------

# Version modulaire cristo algorithme
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
    # --- Sommets de degré pair ---
    even_nodes = [node for node in mst.nodes() if mst.degree(node) % 2 == 0]

    # --- Sous-graphe des sommets impairs ---
    odd_subgraph = G.subgraph(odd_nodes)

    # --- Minimum Weight Perfect Matching du ous-graphe ---
    matching = nx.algorithms.matching.min_weight_matching(odd_subgraph, weight="weight")

    # --- Fusion MST + matching ---
    multigraph = nx.MultiGraph(mst)
    multigraph.add_edges_from(matching)

    # --- Trouver un cycle eulérien ---
    eulerian_circuit = list(nx.eulerian_circuit(multigraph))

    # --- Extraire la tournée finale (Hamiltonienne) ---
    visited = set()
    tour = []
    for u, v in eulerian_circuit:
        if u not in visited:
            tour.append(u)
            visited.add(u)
    tour.append(tour[0])  # retour au point de départ

    # --- Calcul du kilométrage total ---
    total_distance = 0
    for i in range(len(tour) - 1):
        total_distance += G[tour[i]][tour[i+1]]["weight"]

    print("Tournée :", " → ".join(tour))
    print(f"Kilométrage total : {total_distance:.2f} km")

    # --- Print le résultat ---
    print("Sommets impairs :", odd_nodes)
    print("\nAppariements du MWPM :")
    for u, v in matching:
        print(f"{u} — {v} : {G[u][v]['weight']:.2f} km")
    
            
    # --- Positions des villes ---
    pos = {row["Ville"]: (row["Longitude"], row["Latitude"]) for _, row in data.iterrows()}


    # g_data = G, mst, matching, odd_nodes, pos
    g_data = {
        "G": G,
        "mst": mst,
        "matching": matching,
        "odd_nodes": odd_nodes,
        "even_nodes": even_nodes,
        "pos": pos,
        "tour": tour,
        "total_distance": total_distance
    }
    return g_data


# --- Affichage avec fond de carte ---
def cristo_plot(g_data, show_full=True, show_mst=True, show_matching=True, label=''):

    # Récupère le retours de cristo_algo()
    G = g_data["G"]
    mst = g_data["mst"]
    matching = g_data["matching"]
    odd_nodes = g_data["odd_nodes"]
    even_nodes = g_data["even_nodes"]
    pos = g_data["pos"]
    total_distance = g_data["total_distance"]

    plt.figure(figsize=(12, 10))

    # --- Création de la carte de fond ---
    m = basemap(pos)

    # --- Convertir positions lat/lon en coordonnées projetées ---
    x, y = m([coord[0] for coord in pos.values()], [coord[1] for coord in pos.values()])
    projected_pos = {n: (x_i, y_i) for n, x_i, y_i in zip(G.nodes(), x, y)}

    # --- Sommets pairs---
    nx.draw_networkx_nodes(
        G, projected_pos,
        nodelist=even_nodes,
        node_color=cristofides_color,
        node_size=250,
        label='Sommets pairs'
    )

   # --- Sommets impairs---
    nx.draw_networkx_nodes(
        G, projected_pos,
        nodelist=odd_nodes,
        node_color=odd_color,
        node_size=300,
        label='Sommets impairs'
    )

    # --- Arêtes ---
    if show_full:
        nx.draw_networkx_edges(G, projected_pos, edge_color='gray', width=2, alpha=0.5, label='Graphe complet')
    if show_mst:
        nx.draw_networkx_edges(mst, projected_pos, edge_color=cristofides_color, width=3, label='MST')
    if show_matching:
        nx.draw_networkx_edges(G, projected_pos, edgelist=list(matching),
                               edge_color=odd_color, style='dashed', width=2, label='MWPM')

    # --- Labels pour les sommets impairs ---
    odd_labels = {node: node for node in odd_nodes}
    nx.draw_networkx_labels(G, projected_pos, labels=odd_labels, font_size=9, font_color='black', font_weight='bold')
    
    # --- Labels pour les sommets pairs ---
    even_labels = {node: node for node in even_nodes}
    nx.draw_networkx_labels(G, projected_pos, labels=even_labels, font_size=9, font_color='black', font_weight='bold')


    plt.legend(loc='upper left', fontsize=9, frameon=True, fancybox=True, shadow=True)
    plt.title(f"Algorithme de Christofides - {label}\nDistance totale : {total_distance:.2f} km", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.show()

# --- Affichage séquentielle pour visualiser étape par étape ---
def cristo_steps(g_data):
    
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
