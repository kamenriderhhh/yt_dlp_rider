import argparse
from googleapiclient.errors import HttpError
from libs.extract_yt_video import extract_yt_video
from libs.upload_video import get_authenticated_service, initialize_upload

def parse_args():
    parser = argparse.ArgumentParser(description="Download a video from a YouTube URL")
    parser.add_argument("-l", "--link", type=str, required=True, help="The URL link of the video to download")
    parser.add_argument("-o", "--output_path", type=str, help="The URL link of the video to download")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    video_url = args.link

    if "youtube.com" not in video_url:
        raise Exception(f"Invalid YouTube link, your input is: {video_url}")

    if getattr(args, "output_path", None) is not None:
        save_path = args.output_path
    else:
        save_path="C:/Users/USER/Downloads/yt-dlp-temp"
    
    extract_yt_video(video_url=video_url, save_path=save_path)

    try:
        youtube = get_authenticated_service(args)
        initialize_upload(youtube, args)
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
