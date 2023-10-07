import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

from channelVideoDataExtraction import *


comment_data = pd.read_excel("all_comments.xlsx", index_col=None)

# Create a directed graph
G = nx.DiGraph()

# Add nodes for each comment
for index, row in comment_data.iterrows():
    G.add_node(row['comment_id'], comment_text=row['comment_text'])

# Add directed edges representing the flow of information
for index, row in comment_data.iterrows():
    if pd.notna(row['linkage']):
        G.add_edge(row['linkage'], row['comment_id'])

# Visualize the network
pos = nx.spring_layout(G)  # You can choose different layout algorithms
nx.draw(G, pos, with_labels=False, node_size=50, node_color='skyblue', font_size=8)
edge_labels = {(u, v): v for u, v in G.edges()}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6, font_color='red')
plt.title("Information Flow Network")
plt.axis('off')
plt.show()
