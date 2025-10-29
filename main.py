import pandas as pd
from utils import haversine, plot_graph_map, plot_graph, cristo_algo, cristo_plot, crist_steps

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

# cristo_et_affichage(data)

# plot_graph_map(data)

g_data = cristo_algo(data)

cristo_plot(g_data)

# Affichage étape par étape
crist_steps(g_data)