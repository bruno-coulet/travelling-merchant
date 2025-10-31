import pandas as pd
# from utils import haversine, plot_graph_map, plot_graph, cristo_algo, cristo_plot, crist_steps
from utils import cristo_algo, cristo_plot, crist_steps
from genetique import *

# ============ fichier principal  ===============
# 
# charge le csv des villes
# appelle les focntions de utils.py pour :
# - afficher le graph 
# - exécuter l'algo de Christofides
# 
# ============  ===============




# ---------- Chargement du CSV -------------
data = pd.read_csv("data/villes.csv")
# ------------------------------------------



# -------------  Christofides -------------
# Exécution de l'algo 
g_data = cristo_algo(data)
# Affichage étape par étape
crist_steps(g_data)
# -----------------------------------------





