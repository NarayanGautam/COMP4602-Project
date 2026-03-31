import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# 1. Load the aggregated weights data
df = pd.read_csv('club_weights.csv')

# Remove rows where either club contains "U18" 
df = df[
    ~df["club_1"].str.contains("U18") &
    ~df["club_2"].str.contains("U18")
]

# 2. Create a directed graph from the edge list
G = nx.from_pandas_edgelist(
    df, 
    source='club_1', 
    target='club_2', 
    edge_attr='count', 
    create_using=nx.DiGraph()
)

print(f"Full Graph -> Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

# -------------------------
# 3. DEGREE & CENTRALITY ANALYSIS
# -------------------------
# Factoring in 'count' to get actual transfer volumes
in_degrees = dict(G.in_degree(weight='count'))
out_degrees = dict(G.out_degree(weight='count'))
total_degrees = dict(G.degree(weight='count'))
# Betweenness centrality based on paths
betweenness = nx.betweenness_centrality(G)

print("\n--- Top 10 by total transfer volume ---")
for club, vol in sorted(total_degrees.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"{club}: {vol}")

print("\n--- Top 10 by Betweenness Centrality (Key Connectors) ---")
for club, score in sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"{club}: {score:.4f}")

# -------------------------
# 4. VISUALIZATION 1: Top 20 by Total Transfer Volume
# -------------------------
top_volume_nodes = sorted(total_degrees, key=total_degrees.get, reverse=True)[:20]
subgraph_vol = G.subgraph(top_volume_nodes)

plt.figure(figsize=(14, 12))
pos_vol = nx.spring_layout(subgraph_vol, k=1.2, iterations=100, seed=42) 

sub_degrees_vol = dict(subgraph_vol.degree(weight='count'))
# Increase the base size and scale to make the nodes visually distinct but readable
node_sizes_vol = [max(sub_degrees_vol.get(node, 0) * 15, 600) for node in subgraph_vol.nodes()]

nx.draw_networkx_nodes(
    subgraph_vol, pos_vol, 
    node_size=node_sizes_vol, 
    node_color='#E74C3C', # slightly sharper coral/red
    edgecolors='white',
    linewidths=2,
    alpha=0.85
)

edges_vol = subgraph_vol.edges(data=True)
# Thicken edges slightly but add an upper bound to avoid them obscuring nodes
edge_widths_vol = [min(d['count'] * 0.4, 6.0) for u, v, d in edges_vol]
nx.draw_networkx_edges(
    subgraph_vol, pos_vol, 
    width=edge_widths_vol, 
    alpha=0.4, 
    edge_color='#555555', 
    arrows=True, 
    arrowsize=18,
    connectionstyle="arc3,rad=0.15" # slightly more curve
)

# Label adjustments to prevent overlapping
nx.draw_networkx_labels(
    subgraph_vol, pos_vol, 
    font_size=10, 
    font_weight='bold',
    font_family='sans-serif',
    font_color='#2c3e50',
    bbox=dict(facecolor='white', edgecolor='none', alpha=0.6, pad=0.5) # Add a subtle background to text for readability
)

plt.title("Top 20 Soccer Clubs by Transfer Volume\n(Subset Visualization)", fontsize=16, fontweight='bold')
plt.axis('off')
plt.tight_layout()
plt.savefig('subset_graph_volume.png', dpi=300, bbox_inches='tight')
print(f"\n=> Saved visualization 1 to 'subset_graph_volume.png' ({subgraph_vol.number_of_nodes()} nodes, {subgraph_vol.number_of_edges()} edges)")

# -------------------------
# 5. VISUALIZATION 2: Top 20 by Betweenness Centrality
# -------------------------
top_bet_nodes = sorted(betweenness, key=betweenness.get, reverse=True)[:20]
subgraph_bet = G.subgraph(top_bet_nodes)

plt.figure(figsize=(14, 12))
pos_bet = nx.spring_layout(subgraph_bet, k=1.2, iterations=100, seed=42) 

# Scale node sizes based on betweenness score
# using a multiplier since betweenness is typically a small decimal (e.g., 0.05)
node_sizes_bet = [max(betweenness.get(node, 0) * 150000, 600) for node in subgraph_bet.nodes()]

nx.draw_networkx_nodes(
    subgraph_bet, pos_bet, 
    node_size=node_sizes_bet, 
    node_color='#3498DB', # Deep blue for contrast
    edgecolors='white',
    linewidths=2,
    alpha=0.85
)

edges_bet = subgraph_bet.edges(data=True)
# Keep edge widths bounded for visual clarity
edge_widths_bet = [min(d['count'] * 0.4, 6.0) for u, v, d in edges_bet]
nx.draw_networkx_edges(
    subgraph_bet, pos_bet, 
    width=edge_widths_bet, 
    alpha=0.4, 
    edge_color='#555555', 
    arrows=True, 
    arrowsize=18,
    connectionstyle="arc3,rad=0.15"
)

nx.draw_networkx_labels(
    subgraph_bet, pos_bet, 
    font_size=10, 
    font_weight='bold',
    font_family='sans-serif',
    font_color='#2c3e50',
    bbox=dict(facecolor='white', edgecolor='none', alpha=0.6, pad=0.5)
)

plt.title("Top 20 Soccer Clubs by Betweenness Centrality\n(Key Market Brokers and Connectors)", fontsize=16, fontweight='bold')
plt.axis('off')
plt.tight_layout()
plt.savefig('subset_graph_betweenness.png', dpi=300, bbox_inches='tight')
# -------------------------
# 6. VISUALIZATION 3: Bar Charts for Top 10 Metrics
# -------------------------
# Extract top 10 data for bar charts
top_10_vol = sorted(total_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
top_10_bet = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]

# --- NEW: Out-degree vs In-Degree (Buying vs Selling) ---
top_10_out = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
top_10_in = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:10]

plt.figure(figsize=(16, 12)) # Make it taller for 4 plots

# Subplot 1: Total Transfer Volume
plt.subplot(2, 2, 1)
clubs_vol = [x[0] for x in top_10_vol]
vols = [x[1] for x in top_10_vol]
clubs_vol.reverse()
vols.reverse()
bars1 = plt.barh(clubs_vol, vols, color='#E74C3C', edgecolor='black')
plt.title('Top 10 Clubs by Total Transfer Volume', fontsize=14, fontweight='bold')
plt.xlabel('Total Transfer Volume', fontsize=12)
for bar in bars1:
    plt.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2, 
             f'{int(bar.get_width())}', va='center', ha='left', fontsize=10)

# Subplot 2: Betweenness Centrality
plt.subplot(2, 2, 2)
clubs_bet = [x[0] for x in top_10_bet]
scores = [x[1] for x in top_10_bet]
clubs_bet.reverse()
scores.reverse()
bars2 = plt.barh(clubs_bet, scores, color='#3498DB', edgecolor='black')
plt.title('Top 10 Clubs by Betweenness Centrality', fontsize=14, fontweight='bold')
plt.xlabel('Betweenness Centrality Score', fontsize=12)
for bar in bars2:
    plt.text(bar.get_width() + 0.0002, bar.get_y() + bar.get_height()/2, 
             f'{bar.get_width():.4f}', va='center', ha='left', fontsize=10)

# Subplot 3: Out-Degree (Top Sellers)
plt.subplot(2, 2, 3)
clubs_out = [x[0] for x in top_10_out]
outs = [x[1] for x in top_10_out]
clubs_out.reverse()
outs.reverse()
bars3 = plt.barh(clubs_out, outs, color='#2ECC71', edgecolor='black') # Green
plt.title('Top 10 Clubs by Outgoing Transfers (Sellers)', fontsize=14, fontweight='bold')
plt.xlabel('Transfers Out', fontsize=12)
for bar in bars3:
    plt.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2, 
             f'{int(bar.get_width())}', va='center', ha='left', fontsize=10)

# Subplot 4: In-Degree (Top Buyers)
plt.subplot(2, 2, 4)
clubs_in = [x[0] for x in top_10_in]
ins = [x[1] for x in top_10_in]
clubs_in.reverse()
ins.reverse()
bars4 = plt.barh(clubs_in, ins, color='#F1C40F', edgecolor='black') # Yellow
plt.title('Top 10 Clubs by Incoming Transfers (Buyers)', fontsize=14, fontweight='bold')
plt.xlabel('Transfers In', fontsize=12)
for bar in bars4:
    plt.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2, 
             f'{int(bar.get_width())}', va='center', ha='left', fontsize=10)

plt.tight_layout(pad=3.0)
plt.savefig('top_10_bar_charts.png', dpi=300, bbox_inches='tight')
# -------------------------
# 7. VISUALIZATION 4: "Big Six" Internal Trading
# -------------------------
big_six_queries = ["Arsenal", "Chelsea", "Liverpool", "Manchester City", "Manchester United", "Tottenham"]

def map_to_big_six(name):
    for q in big_six_queries:
        if q.lower() in str(name).lower():
            return q
    return name

df_mapped = df.copy()
df_mapped['club_1'] = df_mapped['club_1'].apply(map_to_big_six)
df_mapped['club_2'] = df_mapped['club_2'].apply(map_to_big_six)

df_big_six = df_mapped[df_mapped['club_1'].isin(big_six_queries) & df_mapped['club_2'].isin(big_six_queries)]
df_big_six = df_big_six.groupby(['club_1', 'club_2'], as_index=False)['count'].sum()
df_big_six = df_big_six[df_big_six['club_1'] != df_big_six['club_2']]

G_big_six = nx.from_pandas_edgelist(
    df_big_six, source='club_1', target='club_2', edge_attr='count', create_using=nx.DiGraph()
)

plt.figure(figsize=(10, 8))
pos_big_six = nx.circular_layout(G_big_six)

degrees_six = dict(G_big_six.degree(weight='count'))
node_sizes_six = [max(degrees_six.get(node, 0) * 150, 1000) for node in G_big_six.nodes()]

nx.draw_networkx_nodes(
    G_big_six, pos_big_six, 
    node_size=node_sizes_six, 
    node_color='#9B59B6', # Purplish shade for Big Six
    edgecolors='white',
    linewidths=2,
    alpha=0.85
)

edges_six = G_big_six.edges(data=True)
edge_widths_six = [min(d['count'] * 1.5, 6.0) for u, v, d in edges_six]
nx.draw_networkx_edges(
    G_big_six, pos_big_six, 
    width=edge_widths_six, 
    alpha=0.6, 
    edge_color='#555555', 
    arrows=True, 
    arrowsize=20, 
    connectionstyle="arc3,rad=0.15"
)

nx.draw_networkx_labels(
    G_big_six, pos_big_six, 
    font_size=11, 
    font_weight='bold',
    font_family='sans-serif',
    font_color='#2c3e50',
    bbox=dict(facecolor='white', edgecolor='none', alpha=0.6, pad=0.5)
)

# Widen the axes slightly so node labels aren't cut off at the borders
ax = plt.gca()
ax.margins(0.2)

plt.title("The 'Big Six' Internal Transfer Network\n(Transfers strictly between these 6 clubs)", fontsize=16, fontweight='bold')
plt.axis('off')
plt.tight_layout()
plt.savefig('big_six_network.png', dpi=300, bbox_inches='tight')
plt.close() # Close figure to avoid memory warnings
print("=> Saved 'Big Six' visualization to 'big_six_network.png'")

# -------------------------
# 8. VISUALIZATION 5: Manchester United's Ego Network
# -------------------------
target_club = "Manchester United"

df_ego = df_mapped[(df_mapped['club_1'] == target_club) | (df_mapped['club_2'] == target_club)]
df_ego = df_ego.groupby(['club_1', 'club_2'], as_index=False)['count'].sum()
df_ego_top = df_ego.sort_values(by='count', ascending=False).head(20)

G_ego = nx.from_pandas_edgelist(
    df_ego_top, source='club_1', target='club_2', edge_attr='count', create_using=nx.DiGraph()
)

plt.figure(figsize=(14, 12))
pos_ego = nx.spring_layout(G_ego, k=1.0, seed=42)

ego_degrees = dict(G_ego.degree(weight='count'))

# Highlight MUFC in Red, trading partners in grey
node_colors = ['#E74C3C' if node == target_club else '#BDC3C7' for node in G_ego.nodes()]
node_sizes_ego = [max(ego_degrees.get(node, 0) * 50, 800) for node in G_ego.nodes()]

nx.draw_networkx_nodes(
    G_ego, pos_ego, 
    node_size=node_sizes_ego, 
    node_color=node_colors, 
    edgecolors='white',
    linewidths=2,
    alpha=0.9
)

edges_ego = G_ego.edges(data=True)
edge_widths_ego = [min(d['count'] * 0.8, 6.0) for u, v, d in edges_ego]
nx.draw_networkx_edges(
    G_ego, pos_ego, 
    width=edge_widths_ego, 
    alpha=0.5, 
    edge_color='#555555', 
    arrows=True, 
    arrowsize=15, 
    connectionstyle="arc3,rad=0.15"
)

nx.draw_networkx_labels(
    G_ego, pos_ego, 
    font_size=10, 
    font_weight='bold',
    font_family='sans-serif',
    font_color='#2c3e50',
    bbox=dict(facecolor='white', edgecolor='none', alpha=0.6, pad=0.5)
)

plt.title(f"{target_club} - Top 20 Transfer Connections\n(Ego Network)", fontsize=16, fontweight='bold')
plt.axis('off')
plt.tight_layout()
plt.savefig('ego_network.png', dpi=300, bbox_inches='tight')
plt.close()
print("=> Saved Ego Network visualization to 'ego_network.png'")