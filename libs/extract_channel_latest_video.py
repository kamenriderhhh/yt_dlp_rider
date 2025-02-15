import traceback, sys, json, os
import googleapiclient.discovery

sys.path.append(os.path.join(__file__, *[os.pardir] * 2))
from libs.env import load_env

CONFIG = load_env()


def get_channel_id_by_username(channel_handle, quite=True):
    log_header = "[GET_CHANNEL_ID]"
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=CONFIG["YOUTUBE_API_KEY"]
    )

    request = youtube.search().list(
        part="snippet", q=channel_handle, type="channel", maxResults=1
    )
    try:
        response = request.execute()
        # Extract Channel ID from the response
        channel_id = response["items"][0]["snippet"]["channelId"]
        channel_title = response["items"][0]["snippet"]["channelTitle"]
        if not quite:
            print(
                f"{log_header}\n"
                f"Channel Title: {channel_title} | {channel_handle}\n"
                f"Channel ID: {channel_id}\n"
            )
        return channel_id

    except Exception as e:
        print(f"{log_header} Error: {str(e)}\n{traceback.format_exc()}\n{response}")
        sys.exit()


def get_latest_video_url(channel_id, quite=True):
    log_header = "[GET_LATEST_VIDEO]"
    # Create a YouTube API client
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=CONFIG["YOUTUBE_API_KEY"]
    )

    # Request the latest videos from the channel
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,  # IRyS channel ID
        maxResults=1,  # Get only the latest video
        order="date",  # Order by upload date
        type="video",  # Filter only video uploads and live streams
    )
    try:
        response = request.execute()
        # Extract video ID and title
        video_id = response["items"][0]["id"]["videoId"]
        video_title = response["items"][0]["snippet"]["title"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        if not quite:
            print(
                f"{log_header}\n"
                f"Latest video/stream title: {video_title}\n"
                f"URL: {video_url}\n"
            )
        return (video_url, video_title)

    except Exception as e:
        print(f"{log_header} Error: {str(e)}\n{traceback.format_exc()}\n{response}")
        sys.exit()


if __name__ == "__main__":
    for channel_handle in json.loads(CONFIG["YOUTUBE_CHANNELS"]):
        channel_id = get_channel_id_by_username(channel_handle, quite=False)
        get_latest_video_url(channel_id, quite=False)
