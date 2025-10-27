import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import math

# --- Chargement du CSV ---
data = pd.read_csv("data/villes.csv")

# --- Création du graphe ---
G = nx.Graph()

# Ajout des nœuds avec attributs (latitude, longitude)
for _, row in data.iterrows():
    G.add_node(row["Ville"], pos=(row["Longitude"], row["Latitude"]))


# --- Fonction distance de Haversine ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # rayon moyen de la Terre en km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c  # distance en km

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
