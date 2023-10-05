import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


########################################################################################################################
#                                       FUNCTIONS
########################################################################################################################
# Function to suggest the next publishing date
def suggest_next_publish_date(video_data):
    video_data['published_date'] = pd.to_datetime(video_data['published_date'])
    df_sorted = video_data.sort_values(by='published_date', ascending=False)
    average_diff = (df_sorted['published_date'] - df_sorted['published_date'].shift(-1)).mean()
    return df_sorted['published_date'].iloc[0] + average_diff


########################################################################################################################
#                                       SCHEDULED POST DB CONFIG
########################################################################################################################
# Excel filepath
EXCEL_DB = 'scheduled_posts.xlsx'

# Try to read the Excel file, if it doesn't exist, create a new DataFrame
try:
    df = pd.read_excel(EXCEL_DB)
except FileNotFoundError:
    columns = ["title", "description", "date", "time"]
    df = pd.DataFrame(columns=columns)
    df.to_excel(EXCEL_DB, index=False)  # Create the Excel file with the columns

########################################################################################################################
#                                       PAGE CONFIGURATION
########################################################################################################################
st.set_page_config(page_title="Content Publishing Calender",
                   page_icon="📊",
                   layout="wide")

# Load video data
video_data = pd.read_excel('all_video_Data.xlsx')  # Replace with your video data file path

# Get the suggested date
suggested_date = suggest_next_publish_date(video_data)

########################################################################################################################
#                                       PAGE CONTENT CONFIGURATION
########################################################################################################################
# Display the suggested date with enhanced styling
st.markdown(f"""
<style>
    .suggested-date {{
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 20px;
        text-align: center;
    }}
</style>
<div class="suggested-date">Suggested next publishing date: {suggested_date.strftime('%Y-%m-%d %H:%M:%S')}</div>
""", unsafe_allow_html=True)

# Input fields
video_title = st.text_input("Video Title")
video_description = st.text_area("Video Description")
schedule_date = st.date_input("Schedule Date", suggested_date.date())  # Default to the suggested date
schedule_time = st.time_input("Schedule Time")

if st.button("Schedule Video"):
    # Append to DataFrame and save back to Excel
    df = df.append({
        "title": video_title,
        "description": video_description,
        "date": schedule_date,
        "time": schedule_time
    }, ignore_index=True)
    df.to_excel(EXCEL_DB, index=False)
    st.success("Video scheduled!")

# Display scheduled posts
st.subheader("Scheduled Videos")
st.table(df)
