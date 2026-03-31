import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


df = pd.read_csv("club_weights.csv")

# Remove rows where either club contains "U18"
df = df[
    ~df["club_1"].str.contains("U18") &
    ~df["club_2"].str.contains("U18")
]

G = nx.DiGraph()

for _, row in df.iterrows():
    club1 = row["club_1"]
    club2 = row["club_2"]
    weight = row["count"]
    
    G.add_edge(club1, club2, weight=weight)

print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())

# -------------------------
# 3. DEGREE ANALYSIS
# -------------------------
in_degrees = dict(G.in_degree())
out_degrees = dict(G.out_degree())
total_degrees = dict(G.degree())  # in + out

print("\nTop 20 nodes by total degree:")
print(sorted(total_degrees.items(), key=lambda x: x[1], reverse=True)[:20])

print("\nTop 20 nodes by out-degree (most transfers out):")
print(sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:20])

print("\nTop 20 nodes by in-degree (most transfers in):")
print(sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:20])

# -------------------------
# 3. HUB / AUTHORITY ANALYSIS
# -------------------------

# Compute HITS scores
hubs, authorities = nx.hits(G, max_iter=1000, normalized=True)

# Sort and print top 20 hubs (rounded)
print("\nTop 20 HUBS (clubs that send players to important clubs):")
top_hubs = sorted(hubs.items(), key=lambda x: x[1], reverse=True)[:20]
print([(club, round(score, 4)) for club, score in top_hubs])

# Sort and print top 20 authorities (rounded)
print("\nTop 20 AUTHORITIES (clubs that receive players from important clubs):")
top_auth = sorted(authorities.items(), key=lambda x: x[1], reverse=True)[:20]
print([(club, round(score, 4)) for club, score in top_auth])

# -------------------------
# 4. CENTRALITY / BETWEENNESS
# -------------------------

betweenness = nx.betweenness_centrality(G)
print("\nTop 20 nodes by betweenness:")
print(sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:20])

# -------------------------
# 5. HETEROPHILY / ASSORTATIVITY
# -------------------------




# -------------------------
# 6. VISUALIZATION (Top 20 nodes by total degree)
# -------------------------
top_n = 25
top_nodes = sorted(total_degrees, key=total_degrees.get, reverse=True)[:top_n]
H = G.subgraph(top_nodes).copy()

# Node size based on total degree from full graph
node_sizes = [total_degrees[n] * 25 for n in H.nodes()]

# Edge widths based on weight
edge_weights = [d["weight"] for _, _, d in H.edges(data=True)]
max_w = max(edge_weights)
edge_widths = [(w / max_w) * 5 for w in edge_weights]

# Layout
pos = nx.spring_layout(H, k=5, seed=42)

plt.figure(figsize=(12, 10))
nx.draw_networkx_nodes(H, pos, node_size=node_sizes, alpha=0.9)
nx.draw_networkx_edges(H, pos, width=edge_widths, edge_color="black", alpha=0.7, arrows=True, arrowsize=15, connectionstyle="arc3,rad=0.0")
nx.draw_networkx_labels(H, pos, font_size=8)
plt.title("Top 25 Club Directed Network (Node size = total degree, Edge width = transfer volume)")
plt.axis("off")
plt.show()
