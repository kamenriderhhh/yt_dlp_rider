import argparse, os, sys, gc
from googleapiclient.errors import HttpError
from datetime import datetime
from libs.extract_yt_video import extract_yt_video
from libs.upload_video import get_authenticated_service, initialize_upload, init_oauth_argparser, process_oauth_args
from libs.logger import Logger

def parse_args():
    parser = argparse.ArgumentParser(description="Download a video from a YouTube URL")
    parser.add_argument("-l", "--link", type=str, required=True, help="The URL link of the video to download")
    parser.add_argument("-o", "--output_path", type=str, help="The URL link of the video to download")
    init_oauth_argparser(add_to_parser=parser)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Force UTF-8 encoding for the console
    if os.name == "nt":  # Windows
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    current_time_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    logger = Logger(time_str=current_time_str).get_logger()
    logger.info("Starting the script...")
    
    video_url = args.link
    if "youtube.com" not in video_url:
        logger.error(f"Invalid YouTube link: {video_url}")
        raise Exception(f"Invalid YouTube link, your input is: {video_url}")

    if getattr(args, "output_path", None) is not None:
        save_path = args.output_path
    else:
        save_path = os.path.join(os.path.expanduser("~"), "Downloads", "yt-dlp-temp", "video", current_time_str)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

    logger.info(f"Video URL: {video_url}")
    logger.info(f"Video will be saved to: {save_path}")
    
    extract_yt_video(video_url=video_url, save_path=save_path, logger=logger)

    try:
        logger.info("Starting upload process...")
        process_oauth_args(args, target_dir=save_path)
        youtube = get_authenticated_service(args)
        initialize_upload(youtube, args, logger=logger)
    except HttpError as e:
        logger.error(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.info("Script finished.")
        # Clean up
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()
        logger = None
        gc.collect()