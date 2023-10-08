# YouTube Analytics Dashboard

## Overview
This dashboard provides comprehensive analytics for YouTube channels. It allows users to visualize key metrics, such as views, likes, and comments, for their YouTube videos. Additionally, the dashboard offers predictive analytics, word clouds for tags, detailed statistics for individual videos, network analysis, and community detection functionalities.

## Features

### Channel Details
- Displays the channel's title, description, total views, subscribers, and total videos.
- Provides a direct link to the YouTube channel.

### Top Videos Graphs
- Visualizes the top videos based on views, likes, and comments.
- Allows users to filter the number of top videos displayed.

### Viewership Growth Over Time
- Shows the trend of views over time.
- Predicts viewership growth for the next 30 days using the Prophet forecasting model.

### Word Cloud & Like-to-View Ratio
- Generates a word cloud based on the most common tags used in the videos.
- Displays the like-to-view ratio over time, helping users understand viewer engagement.

### Network Analysis
- Visualizes the relationships between video commenters

### Community Detection
- Uses advanced algorithms to detect communities or clusters within the network of video commenters.

### Detailed Video Statistics
- Lists the latest videos with an option to view detailed statistics for each video.
- Provides a search functionality to filter videos by title.

## Usage
For Detailed View on features and usage, refer to the user manual [User Manual](https://github.com/zainmz/Youtube-Channel-Analytics-Dashboard/blob/4ac60719d5ba7366fcf6c400aace7765810174b8/User%20Manual.pdf)
1. **API Key & Channel ID**: Enter your YouTube API Key and Channel ID in the sidebar.
2. **Data Filters**: Fine-tune the data displayed using filters such as date range and tags.
3. **Refresh Data**: Use the "Refresh Data" button in the sidebar to fetch the latest data.
4. **Search & Pagination**: Search for videos by title and navigate through paginated results.
5. **Detailed Video Stats**: Click on "Check Video Statistics" for a specific video to view its detailed analytics.

## Installation & Setup
For Detailed instruction on installation and how to get Youtube Data API, refer to the user manual [User Manual](https://github.com/zainmz/Youtube-Channel-Analytics-Dashboard/blob/4ac60719d5ba7366fcf6c400aace7765810174b8/User%20Manual.pdf)
1. Clone the repository.
2. Install the required Python packages using `pip install -r requirements.txt`.
3. Run the Streamlit app using `streamlit run app.py`.

## Support & Feedback
For any queries or feedback, please raise an issue in the GitHub repository.

