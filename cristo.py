import pandas as pd
import networkx as nx
import math
from utils import haversine

# --- Étape 1 : lecture du CSV des villes ---
villes = pd.read_csv("data/villes.csv")

# --- Étape 2 : fonction pour calculer la distance de Haversine ---
# ---           importée depuis utils.py

# --- Étape 3 : créer le graphe complet pondéré ---
G = nx.Graph()
for i, v1 in villes.iterrows():
    for j, v2 in villes.iterrows():
        if i < j:
            dist = haversine(v1["Latitude"], v1["Longitude"], v2["Latitude"], v2["Longitude"])
            G.add_edge(v1["Ville"], v2["Ville"], weight=dist)

# --- Étape 4 : calculer le Minimum Spanning Tree ---
mst = nx.minimum_spanning_tree(G, weight="weight")

# --- Étape 5 : identifier les sommets de degré impair ---
odd_nodes = [node for node in mst.nodes() if mst.degree(node) % 2 == 1]

# --- Étape 6 : créer le sous-graphe induit par les sommets impairs ---
odd_subgraph = G.subgraph(odd_nodes)

# --- Étape 7 : calculer le Minimum Weight Perfect Matching ---
# NetworkX fournit un solveur intégré pour ça :
matching = nx.algorithms.matching.min_weight_matching(odd_subgraph, weight="weight")

# --- Étape 8 : affichage du résultat ---
print("Sommets impairs :", odd_nodes)
print("\nAppariements du MWPM :")
for u, v in matching:
    print(f"{u} — {v} : {G[u][v]['weight']:.2f} km")

# --- Étape 9 (optionnelle) : visualiser le MST + MWPM ---
import matplotlib.pyplot as plt

pos = {row["Ville"]: (row["Longitude"], row["Latitude"]) for _, row in villes.iterrows()}

plt.figure(figsize=(10, 8))

# # MST (en vert)
# nx.draw(mst, pos, with_labels=True, node_color='lightgreen', edge_color='green', width=1.5)

# # Matching (en rouge pointillé)
# nx.draw_networkx_edges(G, pos, edgelist=list(matching), edge_color='red', style='dashed', width=2)

# plt.title("MST + Minimum Weight Perfect Matching (Étapes de Christofides)")
# plt.show()





# # Tous les sommets
# nx.draw_networkx_nodes(G, pos, node_color='lightgray', node_size=300, label='Sommets (pair ou impair)')

# # Sommets impairs en bleu
# nx.draw_networkx_nodes(G, pos, nodelist=odd_nodes, node_color='blue', node_size=300, label='Sommets impairs')

# # MST en vert continu
# nx.draw(
#     mst, pos,
#     with_labels=True,
#     node_color='red',
#     edge_color='green',
#     width=1.5,
#     label='MST'
# )

# # MWPM en rouge pointillé
# nx.draw_networkx_edges(
#     G, pos,
#     edgelist=list(matching),
#     edge_color='red',
#     style='dashed',
#     width=2,
#     label='MWPM'
# )

# # Légende
# plt.legend(loc='upper left')

# plt.title("MST + MWPM (sommets impairs en bleu)")
# plt.xlabel("Longitude")
# plt.ylabel("Latitude")
# plt.show()




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
