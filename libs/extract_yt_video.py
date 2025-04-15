import requests, datetime, re, traceback, sys, threading, subprocess, os
from time import sleep
from http.cookiejar import MozillaCookieJar
from yt_dlp import YoutubeDL


def get_live_stream_details(url, cookies_filepath="", logger=None):
    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    }
    session = get_session(cookies_filepath)
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()

        start_time_match = re.search(r'"scheduledStartTime":"(\d+)"', response.text)
        start_time = (
            datetime.datetime.fromtimestamp(int(start_time_match.group(1)))
            if start_time_match
            else None
        )
        title_match = re.search(r'"title":{"simpleText":"([^"]+)"', response.text)
        title = title_match.group(1) if title_match else None

        thumbnail_match = re.search(
            r'"thumbnail":{"thumbnails":\[{"url":"([^"]+)"', response.text
        )
        thumbnail_url = thumbnail_match.group(1) if thumbnail_match else None
        if thumbnail_url and thumbnail_url.startswith("//"):
            thumbnail_url = "https:" + thumbnail_url

        if start_time:
            start_time_str = (
                "The Stream will start on:【"
                + start_time.strftime("%b-%d-%Y at %I:%M:%p")
                + "】"
            )
        elif title:
            start_time_str = "The Stream has been started or Ended?"
        else:
            start_time_str = "Stream Not Found or Private"

        time_until_start = "NA"
        time_until_start_str = "NA"
        if start_time:
            time_until_start = (start_time - datetime.datetime.now()).total_seconds()
            hours, remainder = divmod(time_until_start, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_until_start_str = f"Waiting for live stream to start: {int(hours):02}:{int(minutes):02}:{int(seconds):02} left"
        return {
            "start_time_str": start_time_str,
            "start_time": start_time,
            "time_until_start": time_until_start,
            "time_until_start_str": time_until_start_str,
            "title": title,
            "thumbnail_url": thumbnail_url,
        }
    except requests.RequestException as e:
        log_or_print(f"Error during the request: {e}", logger, is_error=True)
        return None
    except Exception as e:
        log_or_print(f"Unexpected error: {e}", logger, is_error=True)
        return None


def update_timer(url, save_path, cookies_filepath="", print_details=False, logger=None):
    query_interval = 60  # wait for 1 min
    if print_details:
        log_or_print(f"Getting Live Stream Details of [{url}]\n", logger)
    details = get_live_stream_details(url, cookies_filepath, logger)
    if print_details:
        log_or_print(f"{details}\n", logger)
    start_time = details["start_time"]

    if start_time is None:
        checkbroadcast(url, save_path, cookies_filepath, logger)
        return

    time_until_start = details["time_until_start"]
    if time_until_start <= 1:
        checkbroadcast(url, save_path, cookies_filepath, logger)
    else:
        log_or_print(
            f"{details['time_until_start_str']} [next query {query_interval} sec]",
            logger,
        )
        sleep(query_interval)
        update_timer(url, save_path, cookies_filepath, print_details, logger)


def checkbroadcast(url, save_path, cookies_filepath, logger=None):
    def check_isitbroad():
        if isitbroad(url, cookies_filepath, logger):
            log_or_print(f"Waiting for streamer to start⦁⦁⦁", logger)
            threading.Timer(0.5, check_isitbroad).start()
        else:
            log_or_print("Starting Recording!! (˶˃ ᵕ ˂˶) .ᐟ.ᐟ", logger)
            start_recording(url, save_path, cookies_filepath, logger)

    check_isitbroad()


def get_session(cookies_filepath=""):
    session = requests.Session()
    if cookies_filepath:
        try:
            cookie_jar = MozillaCookieJar()
            cookie_jar.load(cookies_filepath, ignore_discard=True, ignore_expires=True)
            session.cookies.update(cookie_jar)
        except Exception as e:
            log_or_print(
                f"Error loading cookies: {str(e)}\n{traceback.format_exc()}\n",
                is_error=True,
            )
            sys.exit(1)
    return session


def isitbroad(url, cookies_filepath, logger=None):
    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    }
    session = get_session(cookies_filepath)
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()

        if '{"runs":[{"text":"Waiting for "}' in response.text:
            return True
        else:
            return False

    except requests.RequestException as e:
        log_or_print(f"Error during the request: {e}", logger, is_error=True)
        return False
    except Exception as e:
        log_or_print(f"Unexpected error: {e}", logger, is_error=True)
        return False


def start_recording(url, save_path, cookies_filepath="", logger=None):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # yt-dlp options
    ydl_opts = {
        "outtmpl": f"{save_path}/%(title)s.%(ext)s",    # Output template
        "format": "bestvideo+bestaudio/best",           # Best quality
        "merge_output_format": "mp4",                   # Merge into MP4
        "retries": 10,                                  # Retry on failure
        "socket_timeout": 60,                           # Timeout for connections
        "quiet": False,                                 # Show progress
        "logger": logger,                               # Use the provided logger
        "live_from_start": True,                        # Start downloading from the beginning of the live stream
        "hls_use_mpegts": True,                         # Use MPEG-TS for better compatibility with live streams
    }
    if cookies_filepath:
        ydl_opts["cookiefile"] = cookies_filepath

    def run_command():
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])  # Download the video
                log_or_print("Recording completed successfully.", logger)
        except Exception as e:
            log_or_print(f"An error occurred while recording: {e}", logger, is_error=True)

    # yt_dlp_command = f'yt-dlp -o "{save_path}/%(title)s.%(ext)s" -f bestvideo+bestaudio/best ' \
    #                  f'--merge-output-format mp4 --retries 10 ' \
    #                  f'--socket-timeout 60 {url}'
    # if cookies_filepath:
    #     yt_dlp_command += " --cookies {token_file}"

    # def run_command():
    #     try:
    #         result = subprocess.run(yt_dlp_command, shell=True, check=True, text=True)
    #         log_or_print("Recording completed successfully.", logger)
    #     except subprocess.CalledProcessError as e:
    #         log_or_print(f"An error occurred while recording: {e}", logger, is_error=True)
    #     except Exception as e:
    #         log_or_print(f"Unexpected error: {e}", logger, is_error=True)

    # Run the command in the main thread and wait for it to complete
    run_command()
    log_or_print("Recording process finished.", logger)


def log_or_print(message, logger=None, is_error=False):
    if logger:
        if is_error:
            logger.error(message)
        else:
            logger.info(message)
    else:
        print(message)


def extract_yt_video(video_url, save_path="C:/Users/USER/Downloads/yt-dlp-temp/video", logger=None):
    update_timer(video_url, save_path, print_details=True, logger=logger)


if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=yanhEf8jK8o"  # Replace with actual video URL 米津玄師 - 地球儀
    extract_yt_video(video_url)
