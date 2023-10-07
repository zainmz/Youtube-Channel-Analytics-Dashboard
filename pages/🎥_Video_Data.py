from datetime import datetime

import numpy
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.chart_container import chart_container
from textblob import TextBlob

from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.switch_page_button import switch_page

from analyze_comments import analyze_comments
from channelVideoDataExtraction import *


########################################################################################################################
#                                       FUNCTIONS
########################################################################################################################
def get_comments():
    comment_data = getVideoComments(api_key, video_id)
    return comment_data


def tag_list(tags):
    tag_list_html = ""
    for tag in tags:
        tag_list_html += f'<span class="tag">{tag}</span>'
    return tag_list_html


def render_insight_card(title, names, emoji="💡"):
    card_content = f"""
    ### {emoji} {title}
    {'<br>'.join([f"**{name}**" for name in names])}
    """
    return card_content


########################################################################################################################
#                                       PAGE CONFIGURATION
########################################################################################################################
st.set_page_config(page_title="Video Statistics",
                   page_icon="📊",
                   layout="wide")

########################################################################################################################
#                                       VIDEO STATISTICAL DATA CONFIGURATION
########################################################################################################################
if st.session_state['video_id'] is None:
    st.error("No Video Has been selected to view statistics. Please select a video from the home page.")
    if st.button("Go Home"):
        switch_page("Home")
else:
    api_key = st.session_state.api_key
    all_video_data = st.session_state.all_video_df
    video_id = st.session_state['video_id']

    video_row = all_video_data[all_video_data['id'] == video_id]

    title = video_row['title'].values[0]
    image_url = video_row['thumbnail'].values[0]
    view_count = video_row['view_count'].values[0]
    like_count = video_row['like_count'].values[0]
    favourite_count = video_row['favorite_count'].values[0]
    comment_count = video_row['comment_count'].values[0]
    duration = round(video_row['duration_minutes'].values[0], 2)
    publish_date = video_row['published_date'].values[0]
    tags = video_row['tags'].values[0]

    # Format view count and subscriber count with commas
    view_count_formatted = "{:,}".format(view_count)
    like_count_formatted = "{:,}".format(like_count)
    comment_count_formatted = "{:,}".format(comment_count)

    st.subheader(title, divider="green")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.image(image_url)
        st.markdown(f"**Published on:**  {publish_date}")

    with col2:
        col2.metric("Total Views", view_count_formatted, "")
        col2.metric("Total Likes", like_count_formatted, "")
        col2.metric("Total Comments", comment_count_formatted, "")
        style_metric_cards(background_color="#000000",
                           border_left_color="#049204",
                           border_color="#0E0E0E"
                           )

    with col3:
        # Define the CSS style for the tags
        css = """
        <style>
            .tag {
                background-color: #4CAF50; /* Change the background color to green */
                color: white;
                padding: 4px 8px;
                margin-right: 8px;
                border-radius: 4px;
                font-weight: bold;
                display: inline-block; /* Prevent overlapping */
                margin-bottom: 8px; /* Add some vertical spacing */
            }
        </style>
        """

        st.subheader("Video Tags")
        # Display the tags
        st.markdown(css, unsafe_allow_html=True)
        st.markdown(tag_list(tags), unsafe_allow_html=True)

        st.subheader("Duration")
        st.markdown(f''':green[{duration}] Minutes''')

########################################################################################################################
#                                       COMMENT DATA CONFIGURATIONS
########################################################################################################################

    st.subheader("Top 10 Comments", divider="green")

    with st.spinner("Getting Comment Data...."):
        comment_data = get_comments()
        top_10_comments_df = comment_data.head(10)
        st.table(top_10_comments_df)

    st.subheader("All Commenters List", divider="green")
    unique_commenters = comment_data['author'].unique()
    st.markdown(f'''Total Number of Commenters: :green[{len(unique_commenters)}]''')
    with st.expander("Click to see all commenters"):
        commenters_text = "\n".join(unique_commenters)
        st.text_area("List of Commenters", commenters_text, height=200)

########################################################################################################################
#                                       COMMENT TRENDS AND SENTIMENT ANALYSIS
########################################################################################################################

    st.subheader("Comment Trends Over Time & Sentiment Analysis", divider="green")
    col1, col2 = st.columns(2)

    with col1:
        comment_data['comment_date'] = pd.to_datetime(comment_data['comment_date'])
        comment_data_grouped = comment_data.groupby(comment_data['comment_date'].dt.date).agg(
            {"comment_id": "count", "like_count": "sum"}).reset_index()

        fig = go.Figure()

        # Add traces for comments and likes
        fig.add_trace(go.Scatter(x=comment_data_grouped['comment_date'],
                                 y=comment_data_grouped['comment_id'],
                                 mode='lines+markers',
                                 name='Number of Comments',
                                 line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=comment_data_grouped['comment_date'],
                                 y=comment_data_grouped['like_count'],
                                 mode='lines+markers',
                                 name='Like Count',
                                 line=dict(color='orange')))

        # Update layout for better appearance
        fig.update_layout(title='Comment and Like Trends Over Time',
                          xaxis_title='Date',
                          yaxis_title='Count',
                          template="plotly_dark")

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        def get_sentiment(text):
            analysis = TextBlob(text)
            # Classify the polarity of the text
            if analysis.sentiment.polarity > 0:
                return 'Positive'
            elif analysis.sentiment.polarity == 0:
                return 'Neutral'
            else:
                return 'Negative'


        comment_data['Sentiment'] = comment_data['comment_text'].apply(get_sentiment)
        sentiment_counts = comment_data['Sentiment'].value_counts()

        with chart_container(comment_data):
            fig = go.Figure(go.Pie(
                labels=sentiment_counts.index,
                values=sentiment_counts.values,
                hole=0.3
            ))

            fig.update_layout(title_text="Sentiment Analysis of Comments")
            st.plotly_chart(fig, use_container_width=True)

########################################################################################################################
#                                       COMMENT NETWORK ANALYSIS
########################################################################################################################
    with st.spinner("Applying Network Analysis to Comments"):
        # Analyze the comments and display the results
        st.title("Comments Network Analysis & Community Detection")

        centrality_df, fig_subgraph, fig_communities, no_of_communities = analyze_comments(comment_data)

        # Display the centrality measures within an expander
        with st.expander("Top 10 Comment Author Centrality Measures"):
            st.table(centrality_df.head(10))

        st.subheader("📊 Network Insights")

        # Arrange cards in columns
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(render_insight_card("Top Influencers",
                                            centrality_df.nlargest(5, 'Degree Centrality')['Author'].tolist(), "🌟"),
                        unsafe_allow_html=True)
            st.markdown(render_insight_card("Most Active Responders",
                                            centrality_df.nlargest(5, 'Out-Degree Centrality')['Author'].tolist(), "💬"),
                        unsafe_allow_html=True)

        with col2:
            st.markdown(render_insight_card("Key Information Spreaders",
                                            centrality_df.nlargest(5, 'Betweenness Centrality')['Author'].tolist(),
                                            "🌐"), unsafe_allow_html=True)
            st.markdown(render_insight_card("Most Responded-To Authors",
                                            centrality_df.nlargest(5, 'In-Degree Centrality')['Author'].tolist(), "🎯"),
                        unsafe_allow_html=True)

        st.markdown("---")  # Divider

        # Graphical Insights
        col1, col2 = st.columns(2)

        with col1:
            # Display the subgraph visualization with a brief title/description
            st.subheader("🔗 Sub Network Visualization")
            st.caption("Top 50 Authors based on Degree Centrality")
            st.pyplot(fig_subgraph)

        with col2:
            # Display the communities visualization with a brief title/description
            st.subheader("👥 Community Visualization")
            st.caption(f"Communities in Sample of 500 Nodes: {no_of_communities} detected")
            st.pyplot(fig_communities)
