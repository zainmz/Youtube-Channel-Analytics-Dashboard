import datetime

import streamlit as st
import io
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.chart_container import chart_container
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.app_logo import add_logo

from prophet import Prophet

from channelDataExtraction import getChannelData
from channelVideoDataExtraction import *


########################################################################################################################
#                                               FUNCTIONS
########################################################################################################################
@st.cache_data
def download_data(api_key, channel_id):
    channel_details = getChannelData(api_key, channel_id)

    # check if bad channel id
    if channel_details is None:
        return None, None, None, None

    videos = getVideoList(api_key, channel_details["uploads"])
    videos_df = pd.DataFrame(videos)
    video_ids = [video['id'] for video in videos if video['id'] is not None]
    all_video_data = buildVideoListDataframe(api_key, video_ids)

    st.session_state.start_index = 0
    st.session_state.end_index = 10
    st.session_state['video_id'] = None
    st.session_state.all_video_df = all_video_data

    st.session_state.api_key = st.session_state.API_KEY

    return channel_details, videos, all_video_data, videos_df


def display_video_list(video_data, start_index, end_index, search_query=None):
    """Displays a list of videos in a tabular format with custom column order and buttons."""

    # Input widget for searching videos by title
    if search_query is None:
        search_query = ""
    new_search_query = st.text_input("Search Videos by Title", search_query)

    # Initialize start_index and end_index in session_state
    if 'start_index' not in st.session_state:
        st.session_state.start_index = start_index
    if 'end_index' not in st.session_state:
        st.session_state.end_index = end_index

    # If a new search query is entered, reset the start and end indices
    if new_search_query != search_query:
        st.session_state.start_index = start_index
        st.session_state.end_index = end_index

    # Filter videos based on the search query across the entire video_data list
    filtered_videos = [video for video in video_data if new_search_query.lower() in video['title'].lower()]

    # Paginate the filtered results
    paginated_videos = filtered_videos[st.session_state.start_index:st.session_state.end_index]

    for video in paginated_videos:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.image(video['thumbnail'])
        with col2:
            st.write(video['id'])
        with col3:
            st.write(video['title'])
        with col4:
            video_stats = st.button("Check Video Statistics", key=video['id'])
            if video_stats:
                st.session_state['video_id'] = video['id']
                switch_page("video_data")

    # Display a button to load the next 10 search results
    if st.session_state.end_index < len(filtered_videos):
        if st.button('Load next 10 videos', key='load_next'):
            st.session_state.start_index = st.session_state.end_index
            st.session_state.end_index += 10


########################################################################################################################
#                                       MAIN PAGE CONFIGURATION
########################################################################################################################
st.set_page_config(page_title="Youtube Channel Analytics Dashboard",
                   page_icon="📊",
                   layout="wide")

########################################################################################################################
#                                       SIDE BAR CONFIGURATION
########################################################################################################################
st.title("YouTube Analytics Dashboard")

# Sidebar
st.sidebar.title("Settings")

# Sidebar: Enter Channel ID and YouTube API Key
if 'API_KEY' not in st.session_state:
    st.session_state.API_KEY = ""
if 'CHANNEL_ID' not in st.session_state:
    st.session_state.CHANNEL_ID = ""

st.session_state.API_KEY = st.sidebar.text_input("Enter your YouTube API Key", st.session_state.API_KEY,
                                                 type="password")
st.session_state.CHANNEL_ID = st.sidebar.text_input("Enter the YouTube Channel ID", st.session_state.CHANNEL_ID)

if not st.session_state.API_KEY or not st.session_state.CHANNEL_ID:
    st.warning("Please enter your API Key and Channel ID.")
    # Display the GitHub link for the user manual
    user_manual_link = "https://github.com/zainmz/Youtube-Channel-Analytics-Dashboard"
    st.markdown(f"If you need help, please refer to the the GitHub Repository for the [User Manual]({user_manual_link}).")
    st.stop()

# Data Refresh Button
refresh_button = st.sidebar.button("Refresh Data")

# First Data Load
channel_details, videos, all_video_data, videos_df = download_data(st.session_state.API_KEY, st.session_state.CHANNEL_ID)

if channel_details is None:
    st.warning("Invalid YouTube Channel ID. Please check and enter a valid Channel ID.")
    st.stop()

if refresh_button:
    with st.spinner("Refreshing data..."):
        channel_details, videos, all_video_data, videos_df = download_data(st.session_state.API_KEY, st.session_state.CHANNEL_ID)

        if channel_details is None:
            st.warning("Invalid YouTube Channel ID. Please check and enter a valid Channel ID.")
            st.stop()

# Data Filters for fine-tuned data selection
st.sidebar.title("Data Filters")

num_videos = st.sidebar.slider("Select Number of Top Videos to Display:", 1, 50, 10)

# Convert the 'published_date' column to datetime format
all_video_data['published_date'] = pd.to_datetime(all_video_data['published_date'])

# Extract min and max publish dates
min_date = all_video_data['published_date'].min().date()  # Ensure it's a date object
max_date = all_video_data['published_date'].max().date()  # Ensure it's a date object

# Sidebar date input
start_date = st.sidebar.date_input("Select Start Date", min_date)
end_date = st.sidebar.date_input("Select End Date", max_date)

if start_date > end_date:
    st.sidebar.warning("Start date should be earlier than end date.")
    st.stop()

tag_search = st.sidebar.text_input("Search Videos by Tag")

date_range_start = pd.Timestamp(start_date)
date_range_end = pd.Timestamp(end_date)

filtered_data = all_video_data[(all_video_data['published_date'] >= date_range_start) &
                               (all_video_data['published_date'] <= date_range_end)]

if tag_search:
    filtered_data = filtered_data[filtered_data['tags'].apply(lambda x: tag_search in x)]

########################################################################################################################
#                                       CHANNEL DETAILS AREA CONFIGURATION
########################################################################################################################

# Display channel details
st.header("Channel Details", divider="green")

col1, col2, col3 = st.columns(3)

with col1:
    channel_thumbnail = channel_details['thumbnail']

    add_logo(channel_thumbnail, height=300)

    view_count = int(channel_details['viewCount'])
    subscriber_count = int(channel_details['subscriberCount'])

    # Format view count and subscriber count with commas
    view_count_formatted = "{:,}".format(view_count)
    subscriber_count_formatted = "{:,}".format(subscriber_count)

    st.markdown(f"**Channel Title:** {channel_details['title']}")
    st.markdown(f"**Channel Description:** {channel_details['description']}")

with col3:
    # Go to Channel Button
    st.link_button("Go to Channel", f"https://www.youtube.com/channel/{st.session_state.CHANNEL_ID}")

col1, col2, col3 = st.columns(3)
col1.metric("Total Views", view_count_formatted, "")
col2.metric("Subscribers", subscriber_count_formatted, "")
col3.metric("Total Videos", len(videos), "")
style_metric_cards(background_color="#000000",
                   border_left_color="#049204",
                   border_color="#0E0E0E"
                   )

########################################################################################################################
#                                            TOP  VIDEO GRAPHS AREA
########################################################################################################################

col1, col2, col3 = st.columns(3)
# Display statistical graphs for the top videos based on views
with col1:
    st.subheader(f"Top {num_videos} Videos Based on Views")
    sorted_video_data = filtered_data.sort_values(by='view_count', ascending=False)
    # Get the top videos from the sorted DataFrame
    top_views_df = sorted_video_data.head(num_videos)
    with chart_container(top_views_df):
        # Display statistical graphs for the top videos based on views
        # Create a bar chart using Plotly
        fig = px.bar(top_views_df, x='title', y='view_count')
        # Update the layout to rename the axes
        fig.update_layout(xaxis_title="Video Title",
                          yaxis_title="View Count")
        fig.update_traces(marker_color='green')
        # Display the bar chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader(f"Top {num_videos} Videos Based on Likes")
    sorted_video_data = filtered_data.sort_values(by='like_count', ascending=False)
    # Get the top 10 liked videos from the sorted DataFrame
    top_likes_df = sorted_video_data.head(num_videos)

    with chart_container(top_likes_df):
        # Display statistical graphs for the top 10 videos based on views
        # Create a bar chart using Plotly
        fig = px.bar(top_likes_df, x='title', y='like_count')
        # Update the layout to rename the axes
        fig.update_layout(xaxis_title="Video Title",
                          yaxis_title="Like Count")
        fig.update_traces(marker_color='orange')
        # Display the bar chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

with col3:
    st.subheader(f"Top {num_videos} Based on Comments")
    sorted_video_data = filtered_data.sort_values(by='comment_count', ascending=False)
    # Get the top 10 liked videos from the sorted DataFrame
    top_comments_df = sorted_video_data.head(num_videos)
    with chart_container(top_comments_df):
        # Display statistical graphs for the top 10 videos based on views
        # Create a bar chart using Plotly
        fig = px.bar(top_comments_df, x='title', y='comment_count')
        # Update the layout to rename the axes
        fig.update_layout(xaxis_title="Video Title",
                          yaxis_title="Comment Count")
        fig.update_traces(marker_color='green')
        # Display the bar chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

########################################################################################################################
#                                            CHANNEL GROWTH STATS
########################################################################################################################

st.subheader("Viewership Growth Over Time", divider="green")
views = filtered_data['view_count']
dates = filtered_data['published_date']

# Creating a time series plot using Plotly
fig = go.Figure()

fig.add_trace(
    go.Scatter(x=dates, y=views, mode='lines+markers', name='Views Over Time', line=dict(color='orange'))
)

fig.update_layout(title='Views Over Time',
                  xaxis_title='Published Date',
                  yaxis_title='Number of Views',
                  template="plotly_dark")

st.plotly_chart(fig, use_container_width=True)

st.subheader("Predicted Viewership Growth Over Time", divider="green")

with st.spinner("Predicting Views for the next Week"):
    # Prepare dataframe for Prophet
    forecast_df = all_video_data[['published_date', 'view_count']]
    forecast_df.columns = ['ds', 'y']

    # Initialize the Prophet model
    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=True,
        daily_seasonality=True,
        seasonality_mode='additive')

    # Fit the model with the data
    model.fit(forecast_df)

    # Dataframe for future dates
    future_dates = model.make_future_dataframe(periods=30)

    # Predict views for the future dates
    forecast = model.predict(future_dates)
    # Plot the original data and the forecast

    # Plotting using Plotly
    # Filter the forecast dataframe to include only the forecasted period
    forecasted_period = forecast[forecast['ds'] > forecast_df['ds'].max()]

    # Plotting using Plotly
    # Filter the forecast dataframe to include only the forecasted period
    forecasted_period = forecast[forecast['ds'] > forecast_df['ds'].max()]

    # Filter the original dataframe to include only the last 30 days
    last_date = forecast_df['ds'].max()
    start_date = last_date - datetime.timedelta(days=30)
    last_30_days = forecast_df[(forecast_df['ds'] > start_date) & (forecast_df['ds'] <= last_date)]

    # Plotting using Plotly
    trace1 = go.Scatter(x=last_30_days['ds'], y=last_30_days['y'], mode='lines', name='Actual Views (Last 30 Days)')
    trace2 = go.Scatter(x=forecasted_period['ds'], y=forecasted_period['yhat'], mode='lines',
                        name='Predicted Views (Next 30 Days)')
    layout = go.Layout(title="YouTube Views: Last 30 Days and Forecast for Next 30 Days", xaxis_title="Date",
                       yaxis_title="Views")
    fig = go.Figure(data=[trace1, trace2], layout=layout)

    # Display the combined historical and forecast data in Streamlit using Plotly
    st.plotly_chart(fig, use_container_width=True)
########################################################################################################################
#                                         WORD CLOUD & LIKE TO VIEW RATIO
########################################################################################################################

col1, col2 = st.columns(2)

with col1:
    st.divider()
    with st.spinner("Generating Word Cloud..."):
        st.subheader("Most Common Tags")
        # Extracting tags from DataFrame and creating a single string
        all_tags = " ".join(" ".join(tags) for tags in filtered_data['tags'])

        # Generating the word cloud
        wordcloud = WordCloud(width=800, height=400, background_color='black').generate(all_tags)

        # Plotting the word cloud using matplotlib
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)

        # Saving the figure to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight', pad_inches=0)
        buf.seek(0)

        st.image(buf, use_column_width=True)

with col2:
    # Calculating the Like-to-View Ratio
    filtered_data['like_to_view_ratio'] = filtered_data['like_count'] / filtered_data['view_count']

    # Extracting the like-to-view ratio and published dates from the dataframe
    like_to_view_ratio = filtered_data['like_to_view_ratio']

    st.divider()
    st.subheader("Like-to-View Ratio Over Time")

    # Creating a time series plot for Like-to-View Ratio using Plotly
    fig_ratio = go.Figure()

    fig_ratio.add_trace(go.Scatter(x=dates, y=like_to_view_ratio, mode='lines+markers', name='Like-to-View Ratio',
                                   line=dict(color='green')))

    fig_ratio.update_layout(xaxis_title='Published Date',
                            yaxis_title='Like-to-View Ratio',
                            template="plotly_dark")

    # Display the plot in Streamlit
    st.plotly_chart(fig_ratio, use_container_width=True)

########################################################################################################################
#                                         DETAILED VIDEO STATS SELECTION SECTION
########################################################################################################################

st.divider()
st.subheader("Detailed Video Statistics Video Selection")
st.write("Click on view statistics to get detailed information related to the selected video")
# latest 10 videos
display_video_list(videos, 0, 10)
