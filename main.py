import pandas as pd
from utils import haversine, plot_graph, cristo, plot_graph_map, crist, crist_plot

# ============ fichier principal  ===============
# 
# charge le csv des villes
# appelle les focntions de utils.py pour :
# - afficher le graph 
# - exécuter l'algo de Christofides
# 
# ============  ===============

# --- Chargement du CSV ---
data = pd.read_csv("data/villes.csv")

# plot_graph(data)

# cristo(data)

# plot_graph_map(data)

crist(data)
crist_plot(g_data)