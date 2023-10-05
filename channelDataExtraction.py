import googleapiclient.discovery


def getChannelData(api_key, channel_id):
    # Create a YouTube API object
    youtube = googleapiclient.discovery.build("youtube",
                                              "v3",
                                              developerKey=api_key)

    # Make an API request to get the channel details
    request = youtube.channels().list(part="snippet,contentDetails,statistics",
                                      id=channel_id)
    response = request.execute()

    # Get the channel details from the response
    channel = response["items"][0]

    # channel details dictionary
    channel_details = {
        "title": channel["snippet"]["title"],
        "description": channel["snippet"]["description"],
        "viewCount": channel["statistics"]["viewCount"],
        "subscriberCount": channel["statistics"]["subscriberCount"],
        "uploads": channel['contentDetails']['relatedPlaylists']['uploads'],
        "thumbnail": channel['snippet']['thumbnails']['medium']['url']
    }

    print(channel_details)

    return channel_details


#getChannelData(api_key, channel_id)
