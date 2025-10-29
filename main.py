import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import math
from utils import haversine, plot_graph, cristo

# --- Chargement du CSV ---
data = pd.read_csv("data/villes.csv")

# plot_graph(data)

cristo(data)