import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# 1. Load the aggregated weights data
df = pd.read_csv('club_weights.csv')

# 2. Create a directed graph from the edge list
G = nx.from_pandas_edgelist(
    df, 
    source='club_1', 
    target='club_2', 
    edge_attr='count', 
    create_using=nx.DiGraph()
)

# 3. Find the top 20 clubs based on total transfer volume
node_degrees = dict(G.degree(weight='count'))
top_nodes = sorted(node_degrees, key=node_degrees.get, reverse=True)[:20]

# 4. Create a subgraph containing ONLY these top 20 clubs and their internal transfers
subgraph = G.subgraph(top_nodes)

# 5. Set up the visualization
plt.figure(figsize=(12, 10))
# spring_layout tries to position connected nodes closer together
pos = nx.spring_layout(subgraph, k=0.8, seed=42) 

# Calculate node sizes based on their degree (scaled up for visibility)
sub_degrees = dict(subgraph.degree(weight='count'))
node_sizes = [max(sub_degrees.get(node, 0) * 40, 500) for node in subgraph.nodes()]

# Draw the nodes
nx.draw_networkx_nodes(
    subgraph, pos, 
    node_size=node_sizes, 
    node_color='lightcoral', 
    edgecolors='black',
    alpha=0.9
)

# Draw edges with varying widths based on the 'count' weight
edges = subgraph.edges(data=True)
edge_widths = [d['count'] * 0.3 for u, v, d in edges]
nx.draw_networkx_edges(
    subgraph, pos, 
    width=edge_widths, 
    alpha=0.6, 
    edge_color='gray', 
    arrows=True, 
    arrowsize=15,
    connectionstyle="arc3,rad=0.1" # Curves the edges slightly
)

# Draw the labels (club names)
nx.draw_networkx_labels(
    subgraph, pos, 
    font_size=9, 
    font_weight='bold',
    font_family='sans-serif'
)

# Add title and finalize
plt.title("Top 20 Soccer Clubs by Transfer Volume\n(Subset Visualization)", fontsize=16, fontweight='bold')
plt.axis('off') # Hide the grid and axes
plt.tight_layout()

# Save the figure to be used in your presentation
plt.savefig('subset_graph.png', dpi=300, bbox_inches='tight')
print(f"Created a subgraph with {subgraph.number_of_nodes()} nodes and {subgraph.number_of_edges()} edges.")