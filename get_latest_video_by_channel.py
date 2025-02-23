import json, traceback, sys

from libs.env import load_env
from libs.extract_channel_latest_video import get_channel_id_by_username, get_latest_video_url
from libs.yt_download import download_video


class Main:
    def __init__(self) -> None:
        self.channel_info = {}
        self.config = load_env()

    def run(self):
        self.gather_all_channel_info()
        self.get_latest_video_url_from_channels()
        print(json.dumps(self.channel_info, indent=2, ensure_ascii=False))
        # self.download_video()

    def download_video(self):
        try:
            log_header = "[DOWNLOAD_VIDEO]"
            for channel_handle, channel_info in self.channel_info.items():
                print(
                    f"{log_header} Downloading video {channel_handle}:{channel_info['video_url']} ..."
                )
                download_video(channel_info["video_url"])
        except Exception as e:
            print(f"{log_header} Error: {str(e)}\n{traceback.format_exc()}")
            sys.exit()

    def get_latest_video_url_from_channels(self):
        for channel_handle, channel_info in self.channel_info.items():
            video_url, video_title = get_latest_video_url(channel_info["id"])
            self.channel_info[channel_handle]["video_title"] = video_title
            self.channel_info[channel_handle]["video_url"] = video_url

    def gather_all_channel_info(self):
        """Gather all channel info from handle, e.g. @IRyS"""
        for channel_handle in json.loads(self.config["YOUTUBE_CHANNELS"]):
            self.channel_info[channel_handle] = {
                "id": get_channel_id_by_username(channel_handle)
            }


if __name__ == "__main__":
    Main().run()
    # download_video("URL HERE")
