import networkx as nx
import json
with open('arguments.json', 'r') as file:
    data = json.load(file)

G = nx.DiGraph()
for entry in data:
    conclusion = entry["conclusion"]["statement"]
    G.add_node(conclusion, truth=entry["conclusion"]["truth"])
    
    # Add supporting statements as nodes
    for stmt in entry["supporting_statements"]:
        statement_text = stmt["statement"]
        G.add_node(statement_text, truth=stmt["truth"])
        
    # Add edges based on supporting rules
    for rule in entry["supporting_rules"]:
        supporting_statement = rule["supporting_statement"]["statement"]
        supported_statement = rule["supported_statement"]["statement"]
        
        # Create directed edges from supporting statements to the conclusion or other statements
        G.add_edge(supporting_statement, supported_statement)

# Export the graph to a GEXF file
nx.write_gexf(G, "statements_network.gexf")

print("GEXF file 'statements_network.gexf' has been created.")