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
# 6. VISUALIZATION HELPERS
# -------------------------
def plot_top_subgraph_by_metric(
    graph,
    metric_scores,
    metric_name,
    output_file,
    top_n=20,
    min_node_size=500,
    size_scale=1.0,
    cmap=plt.cm.YlGnBu,
    edge_color="#2F3E46",
):
    # Select top nodes using full-graph metric values.
    top_nodes = sorted(metric_scores, key=metric_scores.get, reverse=True)[:top_n]
    subgraph = graph.subgraph(top_nodes).copy()

    # Keep sizing based on full graph scores (not subgraph recomputation).
    node_sizes = [max(metric_scores[n] * size_scale, min_node_size) for n in subgraph.nodes()]

    edge_weights = [d["weight"] for _, _, d in subgraph.edges(data=True)]
    if edge_weights:
        max_w = max(edge_weights)
        edge_widths = [(w / max_w) * 5 for w in edge_weights]
    else:
        edge_widths = []

    pos = nx.spring_layout(subgraph, k=2.5, seed=42)

    fig, ax = plt.subplots(figsize=(14, 11))
    nx.draw_networkx_nodes(
        subgraph,
        pos,
        ax=ax,
        node_size=node_sizes,
        node_color=[metric_scores[n] for n in subgraph.nodes()],
        cmap=cmap,
        alpha=0.9,
    )
    nx.draw_networkx_edges(
        subgraph,
        pos,
        ax=ax,
        width=edge_widths,
        edge_color=edge_color,
        alpha=0.45,
        arrows=True,
        arrowsize=15,
        connectionstyle="arc3,rad=0.08",
    )
    nx.draw_networkx_labels(subgraph, pos, font_size=8, ax=ax)

    sm = plt.cm.ScalarMappable(
        cmap=cmap,
        norm=plt.Normalize(
            vmin=min(metric_scores[n] for n in subgraph.nodes()),
            vmax=max(metric_scores[n] for n in subgraph.nodes()),
        ),
    )
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.75)
    cbar.set_label(metric_name)

    ax.set_title(
        f"Top {top_n} Clubs by {metric_name} (Full-Graph Scores Preserved)",
        fontsize=13,
    )
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(
        f"Saved {output_file} with {subgraph.number_of_nodes()} nodes and "
        f"{subgraph.number_of_edges()} edges"
    )


# -------------------------
# 7. VISUALIZATION: TOP 20 BY TOTAL DEGREE
# -------------------------
plot_top_subgraph_by_metric(
    graph=G,
    metric_scores=total_degrees,
    metric_name="Total Degree",
    output_file="top20_degree_subgraph.png",
    top_n=20,
    min_node_size=450,
    size_scale=35,
    cmap=plt.cm.YlOrRd,
    edge_color="#7A1F1F",
)


# -------------------------
# 8. VISUALIZATION: TOP 20 BY HUB SCORE
# -------------------------
plot_top_subgraph_by_metric(
    graph=G,
    metric_scores=hubs,
    metric_name="Hub Score",
    output_file="top20_hub_subgraph.png",
    top_n=20,
    min_node_size=500,
    size_scale=150000,
    cmap=plt.cm.YlOrRd,
    edge_color="#1B4332",
)


# -------------------------
# 9. VISUALIZATION: TOP 20 BY AUTHORITY SCORE
# -------------------------
plot_top_subgraph_by_metric(
    graph=G,
    metric_scores=authorities,
    metric_name="Authority Score",
    output_file="top20_authority_subgraph.png",
    top_n=20,
    min_node_size=500,
    size_scale=150000,
    cmap=plt.cm.YlOrRd,
    edge_color="#3D405B",
)


# -------------------------
# 10. VISUALIZATION: TOP 20 BY BETWEENNESS
# -------------------------
plot_top_subgraph_by_metric(
    graph=G,
    metric_scores=betweenness,
    metric_name="Betweenness Centrality",
    output_file="top20_betweenness_subgraph.png",
    top_n=20,
    min_node_size=500,
    size_scale=200000,
    cmap=plt.cm.YlOrRd,
    edge_color="#7A1F1F",
)
