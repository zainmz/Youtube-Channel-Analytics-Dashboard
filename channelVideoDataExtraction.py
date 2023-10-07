import re
import pandas as pd
import googleapiclient.discovery


def getVideoComments(api_key, video_id):
    # Create a YouTube Data API object
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    # Make an API request to get all the comments for the video
    request = youtube.commentThreads().list(part="snippet,replies",
                                            videoId=video_id,
                                            maxResults=100,
                                            textFormat='plainText')
    response = request.execute()

    all_comments = []

    for comment in response['items']:
        comment_data = {
            'comment_id': comment['id'],
            'author': comment["snippet"]["topLevelComment"]['snippet']
            .get('authorDisplayName', None),
            'like_count': comment["snippet"]["topLevelComment"]['snippet']
            .get('likeCount', None),
            'comment_text': comment["snippet"]["topLevelComment"]['snippet']
            .get('textOriginal', None),
            'comment_date': comment["snippet"]["topLevelComment"]['snippet']
            .get('publishedAt', None),
        }

        all_comments.append(comment_data)

        # Check if there are replies
        if 'replies' in comment:
            for reply in comment['replies']['comments']:
                reply_data = {
                    'comment_id': reply['id'],
                    'author': reply['snippet']
                    .get('authorDisplayName', None),
                    'comment_text': reply['snippet']
                    .get('textOriginal', None),
                    'comment_date': reply['snippet']
                    .get('publishedAt', None),
                    'like_count': reply['snippet']
                    .get('likeCount', None),
                    'linkage': comment_data['comment_id'],  # Link reply to the main comment
                }
                all_comments.append(reply_data)

    next_page_available = response.get('nextPageToken')
    is_other_pages = True

    while is_other_pages:
        if len(all_comments) == 1000:
            break
        if next_page_available is None:
            is_other_pages = False
        else:
            request = youtube.commentThreads() \
                .list(part="snippet,replies",
                      videoId=video_id,
                      maxResults=100,
                      textFormat='plainText',
                      pageToken=next_page_available)
            response = request.execute()

            for comment in response['items']:
                comment_data = {
                    'comment_id': comment['id'],
                    'author': comment["snippet"]["topLevelComment"]['snippet']
                    .get('authorDisplayName', None),
                    'like_count': comment["snippet"]["topLevelComment"]['snippet']
                    .get('likeCount', None),
                    'comment_text': comment["snippet"]["topLevelComment"]['snippet']
                    .get('textOriginal', None),
                    'comment_date': comment["snippet"]["topLevelComment"]['snippet']
                    .get('publishedAt', None),
                }

                all_comments.append(comment_data)

                # Check if there are replies
                if 'replies' in comment:
                    for reply in comment['replies']['comments']:
                        reply_data = {
                            'comment_id': reply['id'],
                            'author': reply['snippet']
                            .get('authorDisplayName', None),
                            'comment_text': reply['snippet']
                            .get('textOriginal', None),
                            'comment_date': reply['snippet']
                            .get('publishedAt', None),
                            'like_count': reply['snippet']
                            .get('likeCount', None),
                            'linkage': comment_data['comment_id'],
                        }
                        all_comments.append(reply_data)

            next_page_available = response.get('nextPageToken')

    # create the dataframe
    comment_data = pd.DataFrame(all_comments)

    # Define the regex pattern for illegal characters
    # For this example, I'll remove non-printable ASCII characters and the character '𝙄'
    pattern = r'[^\x20-\x7E]|𝙄'

    # Remove illegal characters from the entire dataframe
    comment_data.replace(pattern, '', regex=True, inplace=True)

    comment_data = comment_data.drop_duplicates()
    comment_data["like_count"] = comment_data["like_count"]\
                                 .apply(pd.to_numeric, errors='coerce')

    # Remove duplicates based on the 'comment_text' column
    comment_data = comment_data.drop_duplicates(subset='comment_text')

    # Convert 'published_date' to a pandas datetime object
    comment_data['comment_date'] = pd.to_datetime(comment_data['comment_date'])

    # Format 'published_date' with AM/PM in the timezone
    comment_data['comment_date'] = comment_data['comment_date']\
                                   .dt.strftime('%Y-%m-%d %I:%M:%S')

    # Sort the DataFrame by "like_count" in descending order
    comment_data = comment_data.sort_values(by="like_count", ascending=False)
    # Reset the index
    comment_data.reset_index(drop=True, inplace=True)

    comment_data.to_excel("all_comments.xlsx", index=False)

    print(comment_data.head(5))

    return comment_data


def getVideoList(api_key, playlist_id):
    # Create a YouTube API object
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    request = youtube.playlistItems().list(part="contentDetails,snippet",
                                           playlistId=playlist_id,
                                           maxResults=50)
    response = request.execute()

    all_videos = []

    for vid in response['items']:
        vid_stats = {
            'id': vid['contentDetails'].get('videoId', None),
            'title': vid['snippet'].get('title', None),
            'thumbnail': vid['snippet']['thumbnails']['default']['url']
        }
        all_videos.append(vid_stats)

    next_page_available = response.get('nextPageToken')
    is_next_pages = True

    while is_next_pages:
        if next_page_available is None:
            is_next_pages = False
        else:
            request = youtube.playlistItems().list(part="contentDetails,snippet",
                                                   playlistId=playlist_id,
                                                   maxResults=50,
                                                   pageToken=next_page_available)
            response = request.execute()

            for vid in response['items']:
                vid_stats = {
                    'id': vid['contentDetails'].get('videoId', None),
                    'title': vid['snippet'].get('title', None),
                    'thumbnail': vid['snippet']['thumbnails']['default']['url']
                }
                all_videos.append(vid_stats)

            next_page_available = response.get('nextPageToken')

    # print(all_videos)
    return all_videos


def buildVideoListDataframe(api_key, video_ids):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    all_vids_stats = []

    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=','.join(video_ids[i:i + 50]))
        response = request.execute()

        for vid in response['items']:
            thumbnail_url = vid['snippet']['thumbnails'].get('standard', {}).get('url', None)

            vid_stats = {
                'id': vid.get('id', None),
                'title': vid['snippet'].get('title', None),
                'published_date': vid['snippet'].get('publishedAt', None),
                'tags': vid['snippet'].get('tags', []),
                'duration': vid['contentDetails'].get('duration', None),
                'view_count': vid['statistics'].get('viewCount', None),
                'like_count': vid['statistics'].get('likeCount', None),
                'favorite_count': vid['statistics'].get('favoriteCount', None),
                'comment_count': vid['statistics'].get('commentCount', None),
                'thumbnail': thumbnail_url
            }
            all_vids_stats.append(vid_stats)

    # create the dataframe
    vids_info = pd.DataFrame(all_vids_stats)
    # Convert columns to numeric
    numeric_columns = ['comment_count', 'like_count', 'view_count']
    vids_info[numeric_columns] = vids_info[numeric_columns]\
                                  .apply(pd.to_numeric, errors='coerce')

    # Function to convert ISO 8601 duration to minutes
    def iso8601_duration_to_minutes(duration):
        minutes_match = re.search(r'(\d+)M', duration)
        seconds_match = re.search(r'(\d+)S', duration)

        # Get the minutes and seconds values, or default to 0 if they are not found.
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        seconds = int(seconds_match.group(1)) if seconds_match else 0

        # Calculate the total duration in minutes.
        total_minutes = minutes + seconds / 60.0

        return total_minutes

    # Apply the conversion function to the 'duration' column
    vids_info['duration_minutes'] = vids_info['duration']\
                                     .apply(iso8601_duration_to_minutes)

    # Convert 'published_date' to a pandas datetime object
    vids_info['published_date'] = pd.to_datetime(vids_info['published_date'])

    # Format 'published_date'
    vids_info['published_date'] = vids_info['published_date']\
                                   .dt.strftime('%Y-%m-%d %I:%M:%S')

    vids_info.to_excel("all_vids_info.xlsx", index=False)

    print(vids_info.head(5))

    return vids_info


# video_ids = getVideoList(API_KEY, playlist_id)
# video_ids = [video['id'] for video in video_ids if video['id'] is not None]
# buildVideoListDataframe(API_KEY, video_ids)

#getVideoComments(api_key, "video_id")
