# Football Transfer Market Analysis
# COMP4602 Project, Undergrad 7 (Saugat Shrestha, Shuva Gautam, Jai Rana)

This project analyzes football player transfer-market data to build a player interaction network, compute graph metrics (such as degree, betweenness, hub, and authority), and correlate external club factors to graph measures.

plot_transfers.py is the main file that performs the analysis.

## Root Directory Overview

- `README.md` - Project overview and file descriptions.
- `requirements.txt` - Python dependencies required to run preprocessing and plotting scripts.
- `preprocess.py` - Main data preprocessing script for cleaning and preparing transfer/player data for analysis.
- `cleanup.py` - Helper script for cleaning intermediate/generated data artifacts.
- `plot_transfers.py` - Script for creating visualizations from processed transfer data.
- `club_weights.csv` - CSV data containing club-level weights/relationships used in the analysis pipeline.
- `premier-league-processed.csv` - Processed dataset focused on Premier League transfer/player information.
- `top20_degree_subgraph.png` - Visualization of the top-20 nodes by degree centrality.
- `top20_betweenness_subgraph.png` - Visualization of the top-20 nodes by betweenness centrality.
- `top20_hub_subgraph.png` - Visualization of the top-20 hub-score nodes.
- `top20_authority_subgraph.png` - Visualization of the top-20 authority-score nodes.
- `data/` - Data directory containing supporting dataset files (and its own `README.md`).
