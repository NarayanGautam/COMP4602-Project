import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


df = pd.read_csv("club_weights.csv")

# Remove non-club entities and youth teams
invalid_names = ["U18", "U21", "U23", "Without Club", "Retired", "Career break", "Unknown"]
for name in invalid_names:
    df = df[
        ~df["club_1"].str.contains(name, case=False, na=False) &
        ~df["club_2"].str.contains(name, case=False, na=False)
    ]

# Fix duplicate naming conventions (Kaggle dataset mixing formal/casual names)
normalization_map = {
    "Arsenal": "Arsenal FC",
    "Chelsea": "Chelsea FC",
    "Everton": "Everton FC",
    "Liverpool": "Liverpool FC",
    "Newcastle": "Newcastle United",
    "Sunderland": "Sunderland AFC",
    "Tottenham": "Tottenham Hotspur",
    "Man City": "Manchester City",
    "Man Utd": "Manchester United",
    "West Ham": "West Ham United",
    "Birmingham": "Birmingham City",
    "Portsmouth": "Portsmouth FC",
    "QPR": "Queens Park Rangers",
    "Sheff Utd": "Sheffield United",
    "Sheff Wed": "Sheffield Wednesday"
}
df['club_1'] = df['club_1'].replace(normalization_map)
df['club_2'] = df['club_2'].replace(normalization_map)

G = nx.DiGraph()

for _, row in df.iterrows():
    club1 = row["club_1"]
    club2 = row["club_2"]
    weight = row["count"]
    
    if G.has_edge(club1, club2):
        G[club1][club2]['weight'] += weight
    else:
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
# 5. COMMUNITY / HOMOPHILY DETECTION (LOUVAIN)
# -------------------------
import networkx.algorithms.community as nx_comm
G_un = G.to_undirected()
louvain_comms = nx_comm.louvain_communities(G_un, weight='weight', seed=42)
print(f"\nFound {len(louvain_comms)} communities using Louvain algorithm.")
comms_sorted = sorted(louvain_comms, key=len, reverse=True)
for i, comm in enumerate(comms_sorted[:5]):
    print(f"Community {i+1} ({len(comm)} clubs):")
    comm_clubs = sorted(list(comm), key=lambda x: total_degrees.get(x, 0), reverse=True)
    print("  Top members:", comm_clubs[:10])

# -------------------------
# 5.1. STRONGLY CONNECTED COMPONENTS
# -------------------------
scc = list(nx.strongly_connected_components(G))
scc_sorted = sorted(scc, key=len, reverse=True)
print("\nLargest Strongly Connected Components (Closed trading circuits):")
for i, comp in enumerate(scc_sorted[:3]):
    if len(comp) > 1:
        comp_clubs = sorted(list(comp), key=lambda x: total_degrees.get(x, 0), reverse=True)
        print(f"SCC {i+1} ({len(comp)} clubs) - Top members:", comp_clubs[:10])

# -------------------------
# 5.2. RIVALRY WEIGHTS
# -------------------------
rivalries = [
    ("Arsenal FC", "Tottenham Hotspur"),
    ("Arsenal FC", "Chelsea FC"),
    ("Arsenal FC", "Manchester United"),
    ("Arsenal FC", "Liverpool FC"),
    ("Arsenal FC", "Manchester City"),
    ("Manchester United", "Manchester City"),
    ("Manchester United", "Liverpool FC"),
    ("Manchester United", "Chelsea FC"),
    ("Liverpool FC", "Everton FC"),
    ("Liverpool FC", "Manchester City"),
    ("Liverpool FC", "Chelsea FC"),
    ("Chelsea FC", "Manchester City"),
    ("Newcastle United", "Sunderland AFC")
]

print("\nRivalry Transfer Counts (Direct Trading):")
for c1, c2 in rivalries:
    # Adding a helper to fetch edges even if the exact string differs slightly
    # But using the exact name is best based on our previous database inspection
    w1 = G[c1][c2]["weight"] if G.has_edge(c1, c2) else 0
    w2 = G[c2][c1]["weight"] if G.has_edge(c2, c1) else 0
    print(f"  {c1} -> {c2}: {int(w1)} transfers")
    print(f"  {c2} -> {c1}: {int(w2)} transfers")
    print(f"  Total {c1} <-> {c2} trades: {int(w1 + w2)}\n")# -------------------------
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

# -------------------------
# 11. PEARSON CORRELATION (FINANCIAL POWER VS DEGREE AUTHORITY)
# -------------------------
import scipy.stats as stats

# Approximate 2022 Transfermarkt squad values in millions of Euros
financial_values = {
    "Manchester City": 1050,
    "Chelsea FC": 850,
    "Liverpool FC": 860,
    "Manchester United": 790,
    "Tottenham Hotspur": 580,
    "Arsenal FC": 560,
    "Aston Villa": 450,
    "Everton FC": 400,
    "Newcastle United": 380,
    "West Ham United": 350,
    "Southampton FC": 250,
    "Crystal Palace": 260,
    "Sunderland AFC": 40,
    "Stoke City": 45,
    "Birmingham City": 35,
    "Hull City": 40,
    "Queens Park Rangers": 30,
    "Portsmouth FC": 15,
    "Sheffield United": 120,
    "Wolverhampton Wanderers": 320
}

# Correlate wealth with different graph metrics
degrees_list = []
hubs_list = []
auth_list = []
between_list = []
wealth_list = []

for club, wealth in financial_values.items():
    if club in total_degrees:
        wealth_list.append(wealth)
        degrees_list.append(total_degrees[club])
        hubs_list.append(hubs[club])
        auth_list.append(authorities[club])
        between_list.append(betweenness[club])

print("\n--- Pearson Correlations: Financial Power vs Graph Metrics ---")
print(f"Matched {len(wealth_list)} top clubs for the correlation tests.")

if len(wealth_list) > 2:
    r_deg, p_deg = stats.pearsonr(wealth_list, degrees_list)
    r_hub, p_hub = stats.pearsonr(wealth_list, hubs_list)
    r_auth, p_auth = stats.pearsonr(wealth_list, auth_list)
    r_btw, p_btw = stats.pearsonr(wealth_list, between_list)
    
    print(f"\n1. Wealth vs Total Connectivity: r = {r_deg:.4f} (p-value = {p_deg:.4e})")
    print(f"2. Wealth vs Hub Score (Selling Power): r = {r_hub:.4f} (p-value = {p_hub:.4e})")
    print(f"3. Wealth vs Authority Score (Buying Power): r = {r_auth:.4f} (p-value = {p_auth:.4e})")
    print(f"4. Wealth vs Betweenness Centrality (Broker/Bridge): r = {r_btw:.4f} (p-value = {p_btw:.4e})")

# -------------------------
# 12. PEARSON CORRELATION (ACADEMY OUTPUT VS HUB/BETWEENNESS SCORES)
# -------------------------
print("\n--- Pearson Correlation: Academy Output vs Hub/Betweenness Score ---")
# To compute this, we use the raw un-filtered dataset to count the number of 
# transfers coming OUT of a club's U18/U21/U23/Reserve branches to any other club.
raw_df = pd.read_csv("club_weights.csv")

youth_prefixes = {
    "Manchester City": ["Man City U18", "Man City U21", "Man City U23", "Man City Res."],
    "Chelsea FC": ["Chelsea U18", "Chelsea U21", "Chelsea U23", "Chelsea Res."],
    "Liverpool FC": ["Liverpool U18", "Liverpool U21", "Liverpool U23", "Liverpool Res."],
    "Manchester United": ["Man Utd U18", "Man Utd U21", "Man Utd U23", "Man Utd Res."],
    "Tottenham Hotspur": ["Spurs U18", "Spurs U21", "Spurs U23", "Spurs Res.", "Tottenham U18", "Tottenham U21", "Tottenham U23", "Tottenham Res."],
    "Arsenal FC": ["Arsenal U18", "Arsenal U21", "Arsenal U23", "Arsenal Res."],
    "Aston Villa": ["Aston Villa U18", "Aston Villa U21", "Aston Villa U23", "Aston Villa Res."],
    "Everton FC": ["Everton U18", "Everton U21", "Everton U23", "Everton Res."],
    "Newcastle United": ["Newcastle U18", "Newcastle U21", "Newcastle U23", "Newcastle Res."],
    "West Ham United": ["West Ham U18", "West Ham U21", "West Ham U23", "West Ham Res."],
    "Southampton FC": ["Southampton U18", "Southampton U21", "Southampton U23", "Southampton Res."],
    "Crystal Palace": ["Palace U18", "Palace U21", "Palace U23", "Palace Res.", "Crystal Palace U18"],
    "Sunderland AFC": ["Sunderland U18", "Sunderland U21", "Sunderland U23", "Sunderland Res."],
    "Stoke City": ["Stoke U18", "Stoke U21", "Stoke U23", "Stoke Res."],
    "Birmingham City": ["Birmingham U18", "Birmingham U21", "Birmingham U23", "Birmingham Res."],
    "Hull City": ["Hull U18", "Hull U21", "Hull U23", "Hull Res."],
    "Queens Park Rangers": ["QPR U18", "QPR U21", "QPR U23", "QPR Res."],
    "Portsmouth FC": ["Portsmouth U18", "Portsmouth U21", "Portsmouth U23", "Portsmouth Res."],
    "Sheffield United": ["Sheff Utd U18", "Sheff Utd U21", "Sheff Utd U23", "Sheff Utd Res."],
    "Wolverhampton Wanderers": ["Wolves U18", "Wolves U21", "Wolves U23", "Wolves Res."]
}

academy_output = []
hub_scores_for_academy = []
between_scores_for_academy = []

for club, prefixes in youth_prefixes.items():
    if club in hubs:
        total_youth_out = raw_df[raw_df['club_1'].isin(prefixes)]['count'].sum()
        
        academy_output.append(total_youth_out)
        hub_scores_for_academy.append(hubs[club])
        between_scores_for_academy.append(betweenness[club])

if len(academy_output) > 2:
    r_acad_hub, p_acad_hub = stats.pearsonr(academy_output, hub_scores_for_academy)
    r_acad_btw, p_acad_btw = stats.pearsonr(academy_output, between_scores_for_academy)
    print(f"Matched {len(academy_output)} clubs for Academy Output computation.")
    print(f"Academy Output vs Hub Score (Selling Power): r = {r_acad_hub:.4f} (p-value = {p_acad_hub:.4e})")
    print(f"Academy Output vs Betweenness Centrality (Broker): r = {r_acad_btw:.4f} (p-value = {p_acad_btw:.4e})")
