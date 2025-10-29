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

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # rayon moyen de la Terre en km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c  # distance en km

def plot_graph(data):
    
    # --- Création du graphe ---
    G = nx.Graph()

    # Ajout des nœuds avec attributs (latitude, longitude)
    for _, row in data.iterrows():
        G.add_node(row["Ville"], pos=(row["Longitude"], row["Latitude"]))

    # --- Ajout des arêtes pondérées ---
    for i, v1 in data.iterrows():
        for j, v2 in data.iterrows():
            if i < j:  # éviter doublons
                d = haversine(v1["Latitude"], v1["Longitude"], v2["Latitude"], v2["Longitude"])
                G.add_edge(v1["Ville"], v2["Ville"], weight=d)

    # --- Récupération des positions géographiques ---
    pos = nx.get_node_attributes(G, "pos")

    # --- Affichage ---
    plt.figure(figsize=(10, 8))
    nx.draw(
        G, pos,
        with_labels=True,
        node_size=300,
        node_color="lightblue",
        font_size=8,
        edge_color="lightgray"
    )
    plt.title("Réseau des villes françaises (distance de Haversine)")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.show()

def plot_graph_map(data):
    # Crée le graphe complet comme avant
    G = nx.Graph()
    for _, row in data.iterrows():
        G.add_node(row["Ville"], pos=(row["Longitude"], row["Latitude"]))
    for i, v1 in data.iterrows():
        for j, v2 in data.iterrows():
            if i < j:
                d = haversine(v1["Latitude"], v1["Longitude"], v2["Latitude"], v2["Longitude"])
                G.add_edge(v1["Ville"], v2["Ville"], weight=d)

    pos = {n: (data.loc[data["Ville"] == n, "Longitude"].values[0],
               data.loc[data["Ville"] == n, "Latitude"].values[0])
           for n in G.nodes()}

    plt.figure(figsize=(10, 8))

    # --- Configuration de la carte ---
    m = Basemap(
        projection='merc',
        llcrnrlon=min(data["Longitude"]) - 1,
        llcrnrlat=min(data["Latitude"]) - 1,
        urcrnrlon=max(data["Longitude"]) + 1,
        urcrnrlat=max(data["Latitude"]) + 1,
        resolution='i'
    )
    # dessiner les côtes, continents, frontières
    m.drawcoastlines()
    m.drawcountries()
    m.fillcontinents(color='lightgray', lake_color='aqua')
    m.drawmapboundary(fill_color='aqua')

    # Convertir les positions (lon, lat) vers les coordonnées de la carte
    # Note : Basemap attend les coordonnées en (x, y) projetées
    x, y = m(
        [pos[n][0] for n in G.nodes()],
        [pos[n][1] for n in G.nodes()]
    )
    projected_pos = {n: (x_i, y_i) for n, (x_i, y_i) in zip(G.nodes(), zip(x, y))}

    # --- Dessiner le graphe par-dessus ---
    nx.draw_networkx_nodes(G, projected_pos, node_size=300, node_color="lightblue")
    nx.draw_networkx_edges(G, projected_pos, edge_color="gray")
    nx.draw_networkx_labels(G, projected_pos, font_size=8)

    plt.title("Réseau des villes (avec fond de carte)")
    plt.show()

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


# --- Fonction séquentielle pour visualiser étape par étape ---
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