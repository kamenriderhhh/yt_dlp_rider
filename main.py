import argparse
from libs.extract_yt_video import extract_yt_video

def parse_args():
    parser = argparse.ArgumentParser(description="Download a video from a YouTube URL")
    parser.add_argument("-l", "--link", type=str, required=True, help="The URL link of the video to download")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    video_url = args.link

    if "youtube.com" not in video_url:
        raise Exception(f"Invalid YouTube link, your input is: {video_url}")

    extract_yt_video(video_url)