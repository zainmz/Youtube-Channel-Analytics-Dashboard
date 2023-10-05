import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import igraph as ig
import plotly.subplots as sp

data = pd.read_excel("all_comments.xlsx")


def analyze_comments(data):
    # Reset the graph
    G = nx.DiGraph()

    # Add nodes to the graph representing authors
    for author in data['author'].unique():
        G.add_node(author)

    # Add edges to the graph representing replies
    for _, row in data.dropna(subset=['linkage']).iterrows():
        # Find the author of the main comment (the comment being replied to)
        main_comment_authors = data[data['comment_id'] == row['linkage']]['author'].values
        if main_comment_authors:
            main_comment_author = main_comment_authors[0]
            G.add_edge(row['author'], main_comment_author)

    # Calculate centrality measures again
    degree_centrality = nx.degree_centrality(G)
    in_degree_centrality = nx.in_degree_centrality(G)
    out_degree_centrality = nx.out_degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)

    # Create a DataFrame to display the results
    centrality_df = pd.DataFrame({
        'Author': list(degree_centrality.keys()),
        'Degree Centrality': list(degree_centrality.values()),
        'In-Degree Centrality': list(in_degree_centrality.values()),
        'Out-Degree Centrality': list(out_degree_centrality.values()),
        'Betweenness Centrality': list(betweenness_centrality.values()),
        'Closeness Centrality': list(closeness_centrality.values())
    }).sort_values(by='Degree Centrality', ascending=False)

    print(centrality_df.head(10))

    centrality_df.head(10).to_excel("centrality.xlsx", index=False)

    # Select the top N authors based on degree centrality for the subgraph
    N = 50
    top_authors = [author for author, _ in
                   sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True)[:N]]

    # Extract the subgraph
    subgraph = G.subgraph(top_authors)

    # Draw the subgraph
    fig_subgraph = plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(subgraph)
    nx.draw_networkx(subgraph, pos, with_labels=True, node_size=500, node_color='skyblue', font_size=10, alpha=0.6,
                     edge_color='gray')

    plt.title("Subgraph of Top 50 Authors based on Degree Centrality")
    plt.close(fig_subgraph)

    # Sample a subset of nodes for the subgraph
    sample_size = 500
    sampled_nodes = list(G.nodes())[:sample_size]

    # Extract the subgraph for the sampled nodes
    sampled_subgraph = G.subgraph(sampled_nodes)

    # Use the Girvan-Newman algorithm on the sampled subgraph
    sampled_communities_gn = nx.community.girvan_newman(sampled_subgraph)

    # Get the first partitioning of communities for the sampled subgraph
    sampled_first_partition = next(sampled_communities_gn)

    # Convert the first_partition into a more readable format
    sampled_community_list_gn = [list(community) for community in sampled_first_partition]

    # Display the number of detected communities and the size of each community for the sampled subgraph
    sampled_community_sizes_gn = {f"Sampled Community GN {i + 1}": len(community) for i, community in
                                  enumerate(sampled_community_list_gn)}
    no_of_communities = len(sampled_community_sizes_gn)

    # Generate a new position layout for the nodes in the sampled subgraph
    sampled_pos = nx.spring_layout(sampled_subgraph)

    # Helper function to get edges for a community
    def get_edges(G, community):
        return [(u, v) for u, v in G.edges() if u in community and v in community]

    # Visualize the communities in the sampled subgraph
    fig_communities = plt.figure(figsize=(15, 15))

    # Get unique colors for each community
    colors = plt.cm.rainbow(np.linspace(0, 1, len(sampled_community_list_gn)))

    # Draw nodes and edges with community colors
    for community, color in zip(sampled_community_list_gn, colors):
        nx.draw_networkx_nodes(sampled_subgraph, sampled_pos, nodelist=community, node_color=[color] * len(community),
                               node_size=500)
        nx.draw_networkx_edges(sampled_subgraph, sampled_pos, edgelist=get_edges(sampled_subgraph, community),
                               alpha=0.5)

    # Draw labels for nodes
    nx.draw_networkx_labels(sampled_subgraph, sampled_pos, font_size=10, font_weight="bold")

    plt.title("Communities in Sampled Subgraph")
    plt.axis("off")
    plt.close(fig_communities)

    return centrality_df, fig_subgraph, fig_communities, no_of_communities

# analyze_comments(data)
