import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import math

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


def cristo(data):
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

    plt.figure(figsize=(10, 8))

    # --- Sommets ---
    # Tous les sommets : gris clair
    nx.draw_networkx_nodes(
        G, pos,
        node_color='lightgray',
        node_size=250,
        label='Sommets pairs'
    )

    # Sommets impairs : bleu et plus gros
    nx.draw_networkx_nodes(
        G, pos,
        nodelist=odd_nodes,
        node_color='dodgerblue',
        node_size=400,
        label='Sommets impairs'
    )

    # --- Arêtes ---
    # MST : vert continu
    nx.draw_networkx_edges(
        mst, pos,
        edge_color='green',
        width=1.5,
        label='MST'
    )

    # MWPM : rouge pointillé
    nx.draw_networkx_edges(
        G, pos,
        edgelist=list(matching),
        edge_color='red',
        style='dashed',
        width=2,
        label='MWPM'
    )

    # --- Labels ---
    # N’afficher les labels que pour les sommets impairs
    odd_labels = {node: node for node in odd_nodes}
    nx.draw_networkx_labels(G, pos, labels=odd_labels, font_size=9, font_color='black', font_weight='bold')

    # --- Légende & mise en forme ---
    plt.legend(
        loc='upper left',
        fontsize=9,
        frameon=True,
        fancybox=True,
        shadow=True
    )
    plt.title("MST + MWPM (Étapes de Christofides)\nSommets impairs en bleu", fontsize=12, fontweight='bold')
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.tight_layout()
    plt.show()
