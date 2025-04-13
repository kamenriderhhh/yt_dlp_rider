import requests, datetime, re, traceback, sys, threading, subprocess
from time import sleep
from http.cookiejar import MozillaCookieJar


def get_live_stream_details(url, cookies_filepath=""):
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
        print(f"Error during the request: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def update_timer(url, save_path, cookies_filepath="", print_details=False):
    query_interval = 60 # wait for 1 min
    if print_details:
        print(f"Getting Live Stream Details of [{url}]\n")
    details = get_live_stream_details(url)
    if print_details:
        print(f"{details}\n")
    start_time = details["start_time"]

    if start_time is None:
        checkbroadcast(url, save_path, cookies_filepath)
        return

    time_until_start = details["time_until_start"]
    if time_until_start <= 1:
        checkbroadcast(url, save_path, cookies_filepath)
    else:
        details["time_until_start"]
        print(f"{details['time_until_start_str']} [next query {query_interval} sec]")
        sleep(query_interval)
        update_timer(url, save_path, cookies_filepath)

def checkbroadcast(url, save_path, cookies_filepath):
    dots = 0

    def check_isitbroad():
        nonlocal dots
        if isitbroad(url, cookies_filepath): 
            dots = (dots + 1) % 20  
            print(f"Waiting for streamer to start⦁{'⦁' *dots}")
            threading.Timer(0.5, check_isitbroad).start()
        else: 
            print("Starting Recording!! (˶˃ ᵕ ˂˶) .ᐟ.ᐟ")
            start_recording(url, save_path, cookies_filepath)
    
    check_isitbroad()

def get_session(cookies_filepath=""):
    session = requests.Session()
    if cookies_filepath:
        try:
            cookie_jar = MozillaCookieJar()
            cookie_jar.load(cookies_filepath, ignore_discard=True, ignore_expires=True)
            session.cookies.update(cookie_jar)
        except Exception as e:
            print(f"Error loading cookies: {str(e)}\n{traceback.format_exc()}\n")
            sys.exit(1)
    return session

def isitbroad(url, cookies_filepath):
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
        print(f"Error during the request: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False 
    
def start_recording(url, save_path, cookies_filepath=""):
    yt_dlp_command = f'yt-dlp -o "{save_path}/%(title)s.%(ext)s" -f bestvideo+bestaudio/best ' \
                     f'--merge-output-format mp4 --retries 3 ' \
                     f'--socket-timeout 30 {url}'
    if cookies_filepath:
        yt_dlp_command += " --cookies {token_file}"

    full_command = f'cmd.exe /c start cmd.exe /k "{yt_dlp_command}"'

    try:
        subprocess.Popen(full_command, shell=True)
        print("Recording started...")
    except Exception as e:
        print(f"An error occurred while starting the recording process: {str(e)}")

def extract_yt_video(video_url, save_path="C:/Users/USER/Downloads/yt-dlp-temp"):
    update_timer(video_url, save_path, print_details=True)
    


if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=yanhEf8jK8o"  # Replace with actual video URL 米津玄師 - 地球儀
    extract_yt_video(video_url)

