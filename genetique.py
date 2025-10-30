import random
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from utils import haversine


# =======  Algorithme Genetique pour le TSP =======
#
# genetic_tsp() implemente un algorithme genetique classique
# avec selection par tournoi, croisement OX et mutation par swap
#
# =================================================


def calculate_tour_distance(tour, data):
    """
    Calcule la distance totale d'un tour (chemin hamiltonien ferme).

    Args:
        tour: Liste des noms de villes dans l'ordre de visite
        data: DataFrame avec colonnes Ville, Latitude, Longitude

    Returns:
        Distance totale en km
    """
    total_distance = 0
    for i in range(len(tour)):
        city1 = tour[i]
        city2 = tour[(i + 1) % len(tour)]  # retour e la premiere ville

        # Recuperer les coordonnees
        lat1, lon1 = data.loc[data["Ville"] == city1, ["Latitude", "Longitude"]].values[0]
        lat2, lon2 = data.loc[data["Ville"] == city2, ["Latitude", "Longitude"]].values[0]

        total_distance += haversine(lat1, lon1, lat2, lon2)

    return total_distance


def create_initial_population(cities, pop_size):
    """
    Cree une population initiale de tours aleatoires.

    Args:
        cities: Liste des noms de villes
        pop_size: Taille de la population

    Returns:
        Liste de tours (chaque tour est une liste de villes)
    """
    population = []
    for _ in range(pop_size):
        tour = cities.copy()
        random.shuffle(tour)
        population.append(tour)
    return population


def fitness(tour, data):
    """
    Calcule le fitness d'un tour (inverse de la distance pour maximiser).

    Args:
        tour: Liste des villes
        data: DataFrame des villes

    Returns:
        Fitness (1 / distance)
    """
    distance = calculate_tour_distance(tour, data)
    return 1 / distance if distance > 0 else 0


def tournament_selection(population, fitnesses, tournament_size=5):
    """
    Selection par tournoi : choisit le meilleur individu parmi un echantillon aleatoire.

    Args:
        population: Liste de tours
        fitnesses: Liste des fitness correspondants
        tournament_size: Taille du tournoi

    Returns:
        Un tour selectionne
    """
    tournament_indices = random.sample(range(len(population)), tournament_size)
    tournament_fitnesses = [fitnesses[i] for i in tournament_indices]
    winner_index = tournament_indices[tournament_fitnesses.index(max(tournament_fitnesses))]
    return population[winner_index].copy()


def order_crossover(parent1, parent2):
    """
    Croisement OX (Order Crossover) : preserve l'ordre relatif des villes.

    Args:
        parent1, parent2: Tours parents

    Returns:
        Deux enfants
    """
    size = len(parent1)

    # Choisir deux points de coupure
    start, end = sorted(random.sample(range(size), 2))

    # Creer l'enfant 1
    child1 = [None] * size
    child1[start:end] = parent1[start:end]

    # Remplir avec parent2 dans l'ordre
    pointer = end
    for city in parent2[end:] + parent2[:end]:
        if city not in child1:
            child1[pointer % size] = city
            pointer += 1

    # Creer l'enfant 2 (symetrique)
    child2 = [None] * size
    child2[start:end] = parent2[start:end]

    pointer = end
    for city in parent1[end:] + parent1[:end]:
        if city not in child2:
            child2[pointer % size] = city
            pointer += 1

    return child1, child2


def swap_mutation(tour, mutation_rate=0.1):
    """
    Mutation par echange : echange deux villes avec une certaine probabilite.

    Args:
        tour: Tour e muter
        mutation_rate: Probabilite de mutation

    Returns:
        Tour mute
    """
    tour = tour.copy()
    if random.random() < mutation_rate:
        i, j = random.sample(range(len(tour)), 2)
        tour[i], tour[j] = tour[j], tour[i]
    return tour


def inversion_mutation(tour, mutation_rate=0.1):
    """
    Mutation par inversion : inverse un segment du tour.

    Args:
        tour: Tour e muter
        mutation_rate: Probabilite de mutation

    Returns:
        Tour mute
    """
    tour = tour.copy()
    if random.random() < mutation_rate:
        i, j = sorted(random.sample(range(len(tour)), 2))
        tour[i:j] = reversed(tour[i:j])
    return tour


def genetic_tsp(data, pop_size=100, generations=500, mutation_rate=0.1, elite_size=5, verbose=True):
    """
    Algorithme genetique pour resoudre le TSP.

    Args:
        data: DataFrame avec colonnes Ville, Latitude, Longitude
        pop_size: Taille de la population
        generations: Nombre de generations
        mutation_rate: Taux de mutation
        elite_size: Nombre d'individus elites preserves
        verbose: Afficher les progres

    Returns:
        Dictionnaire contenant:
            - best_tour: Meilleur tour trouve
            - best_distance: Distance du meilleur tour
            - G: Graphe complet
            - pos: Positions des villes
            - history: Historique des distances par generation
    """
    cities = data["Ville"].tolist()

    # Creer le graphe complet pour la visualisation
    G = nx.Graph()
    for i, v1 in data.iterrows():
        for j, v2 in data.iterrows():
            if i < j:
                dist = haversine(v1["Latitude"], v1["Longitude"], v2["Latitude"], v2["Longitude"])
                G.add_edge(v1["Ville"], v2["Ville"], weight=dist)

    pos = {row["Ville"]: (row["Longitude"], row["Latitude"]) for _, row in data.iterrows()}

    # Population initiale
    population = create_initial_population(cities, pop_size)

    best_distance_history = []
    avg_distance_history = []

    best_ever_tour = None
    best_ever_distance = float('inf')

    if verbose:
        print("\n=== Algorithme Genetique - Demarrage ===")
        print(f"Population: {pop_size}, Generations: {generations}, Mutation: {mutation_rate}")

    for generation in range(generations):
        # Calculer les fitness
        fitnesses = [fitness(tour, data) for tour in population]
        distances = [calculate_tour_distance(tour, data) for tour in population]

        # Meilleur de cette generation
        best_idx = distances.index(min(distances))
        best_distance = distances[best_idx]
        best_tour = population[best_idx]

        # Mettre e jour le meilleur absolu
        if best_distance < best_ever_distance:
            best_ever_distance = best_distance
            best_ever_tour = best_tour.copy()

        # Historique
        best_distance_history.append(best_ever_distance)
        avg_distance_history.append(sum(distances) / len(distances))

        # Affichage periodique
        if verbose and (generation % 50 == 0 or generation == generations - 1):
            print(f"Generation {generation:3d} | Meilleur: {best_distance:.2f} km | "
                  f"Meilleur absolu: {best_ever_distance:.2f} km | Moy: {avg_distance_history[-1]:.2f} km")

        # elitisme : garder les meilleurs
        sorted_indices = sorted(range(len(distances)), key=lambda i: distances[i])
        elite = [population[i].copy() for i in sorted_indices[:elite_size]]

        # Nouvelle generation
        new_population = elite.copy()

        while len(new_population) < pop_size:
            # Selection
            parent1 = tournament_selection(population, fitnesses)
            parent2 = tournament_selection(population, fitnesses)

            # Croisement
            child1, child2 = order_crossover(parent1, parent2)

            # Mutation
            child1 = swap_mutation(child1, mutation_rate)
            child2 = inversion_mutation(child2, mutation_rate)

            new_population.extend([child1, child2])

        # Tronquer si necessaire
        population = new_population[:pop_size]

    if verbose:
        print(f"\n=== Resultat final ===")
        print(f"Meilleur tour trouve: {best_ever_distance:.2f} km")
        print(f"Ordre de visite: {' -> '.join(best_ever_tour[:5])} ... {' -> '.join(best_ever_tour[-3:])}")

    return {
        "best_tour": best_ever_tour,
        "best_distance": best_ever_distance,
        "G": G,
        "pos": pos,
        "history": {
            "best": best_distance_history,
            "avg": avg_distance_history
        }
    }


def genetic_plot(result, bg_color='lightblue', show_graph=True):
    """
    Affiche le meilleur tour trouve par l'algorithme genetique sur une carte.

    Args:
        result: Dictionnaire retourne par genetic_tsp()
        bg_color: Couleur de fond du continent
        show_graph: Afficher le graphe complet en arriere-plan
    """
    best_tour = result["best_tour"]
    best_distance = result["best_distance"]
    G = result["G"]
    pos = result["pos"]

    plt.figure(figsize=(12, 10))

    # --- Creation de la carte de fond ---
    m = Basemap(
        projection='merc',
        llcrnrlon=min(coord[0] for coord in pos.values()) - 1,
        llcrnrlat=min(coord[1] for coord in pos.values()) - 1,
        urcrnrlon=max(coord[0] for coord in pos.values()) + 1,
        urcrnrlat=max(coord[1] for coord in pos.values()) + 1,
        resolution='i'
    )
    m.drawcoastlines()
    m.drawcountries()
    m.fillcontinents(color=bg_color, lake_color='aqua')
    m.drawmapboundary(fill_color='aqua')

    # --- Convertir positions lat/lon en coordonnees projetees ---
    x, y = m([coord[0] for coord in pos.values()], [coord[1] for coord in pos.values()])
    projected_pos = {n: (x_i, y_i) for n, x_i, y_i in zip(G.nodes(), x, y)}

    # --- Graphe complet en arriere-plan (optionnel) ---
    if show_graph:
        nx.draw_networkx_edges(G, projected_pos, edge_color='gray', width=1, alpha=0.2)

    # --- Dessiner le tour ---
    tour_edges = [(best_tour[i], best_tour[(i + 1) % len(best_tour)]) for i in range(len(best_tour))]
    nx.draw_networkx_edges(G, projected_pos, edgelist=tour_edges,
                          edge_color='blue', width=3, alpha=0.8, label='Tour genetique')

    # --- Sommets ---
    nx.draw_networkx_nodes(G, projected_pos, node_color='red', node_size=250)

    # --- Labels ---
    nx.draw_networkx_labels(G, projected_pos, font_size=8, font_color='black', font_weight='bold')

    plt.legend(loc='upper left', fontsize=10, frameon=True, fancybox=True, shadow=True)
    plt.title(f"Algorithme Genetique - TSP\nDistance totale: {best_distance:.2f} km",
              fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.show()


def plot_genetic_convergence(history):
    """
    Affiche la courbe de convergence de l'algorithme genetique.

    Args:
        history: Dictionnaire avec keys 'best' et 'avg' (historique des distances)
    """
    plt.figure(figsize=(10, 6))
    plt.plot(history["best"], label="Meilleure distance", color='blue', linewidth=2)
    plt.plot(history["avg"], label="Distance moyenne", color='orange', linewidth=1, alpha=0.7)
    plt.xlabel("Generation", fontsize=12)
    plt.ylabel("Distance (km)", fontsize=12)
    plt.title("Convergence de l'Algorithme Genetique", fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
