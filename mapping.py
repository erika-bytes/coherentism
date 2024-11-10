import matplotlib.pyplot as plt
import networkx as nx

# Define the family tree dataset
nodes = [
    {"id": "1", "name": "John"},
    {"id": "2", "name": "Mary"},
    {"id": "3", "name": "Alice"},
    {"id": "4", "name": "Bob"},
    {"id": "5", "name": "Charlie"},
    {"id": "6", "name": "Diana"},
    {"id": "7", "name": "Eve"},
    {"id": "8", "name": "Frank"},
    {"id": "9", "name": "Grace"},
    {"id": "10", "name": "Hank"}
]

links = [
    {"source": "1", "target": "3"},
    {"source": "2", "target": "3"},
    {"source": "1", "target": "4"},
    {"source": "2", "target": "4"},
    {"source": "3", "target": "5"},
    {"source": "3", "target": "6"},
    {"source": "4", "target": "5"},
    {"source": "4", "target": "6"},
    {"source": "5", "target": "7"},
    {"source": "5", "target": "8"},
    {"source": "6", "target": "7"},
    {"source": "6", "target": "8"},
    {"source": "7", "target": "9"},
    {"source": "8", "target": "10"}
]

# Create a directed graph
G = nx.DiGraph()

# Add nodes
for node in nodes:
    G.add_node(node["id"], label=node["name"])

# Add edges (relationships)
for link in links:
    G.add_edge(link["source"], link["target"])

# Set node labels
labels = {node["id"]: node["name"] for node in nodes}

# Draw the graph
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(G, seed=42)  # Use spring layout for a simple visualization
nx.draw(G, pos, with_labels=True, labels=labels, node_size=3000, node_color="lightblue", font_size=10, font_weight="bold", arrows=True)
plt.title("Simple Family Tree Visualization")
plt.show()