import networkx as nx
import itertools
import matplotlib.pyplot as plt

def christofides_tsp(graph):
    # Step 1: Compute the Minimum Spanning Tree (MST)
    mst = nx.minimum_spanning_tree(graph)

    # Step 2: Find nodes with odd degree in the MST
    odd_degree_nodes = [v for v, d in mst.degree() if d % 2 == 1]

    # Step 3: Find Minimum Weight Perfect Matching among odd degree nodes
    subgraph = graph.subgraph(odd_degree_nodes)
    matching = nx.algorithms.matching.min_weight_matching(subgraph)

    # Step 4: Combine MST and Matching to form an Eulerian Graph
    eulerian_graph = nx.MultiGraph(mst)
    eulerian_graph.add_edges_from(matching)

    # Step 5: Find an Eulerian circuit
    eulerian_circuit = list(nx.eulerian_circuit(eulerian_graph))

    # Step 6: Shortcutting to form the final TSP tour
    tsp_tour = []
    visited = set()
    for u, v in eulerian_circuit:
        if u not in visited:
            tsp_tour.append(u)
            visited.add(u)
    tsp_tour.append(tsp_tour[0])  # Return to starting point

    return tsp_tour

# Example Graph with Four Cities
graph = nx.Graph()
cities = ['A', 'B', 'C', 'D']
distances = {
    ('A', 'B'): 1, ('A', 'C'): 2, ('A', 'D'): 3,
    ('B', 'C'): 4, ('B', 'D'): 5, ('C', 'D'): 6
}

for (u, v), w in distances.items():
    graph.add_edge(u, v, weight=w)

tsp_tour = christofides_tsp(graph)
print("TSP Tour:", " -> ".join(tsp_tour), "\n")
# Visualizing the Graph
pos = nx.spring_layout(graph)
nx.draw(graph, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=16)
labels = nx.get_edge_attributes(graph, 'weight')
nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)
plt.show()