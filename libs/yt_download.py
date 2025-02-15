import yt_dlp

def download_video(url):
    # Define download options
    ydl_opts = {
        'format': 'best',  # You can specify 'bestaudio' for audio only
        'outtmpl': 'C:/Users/USER/Downloads/yt-dlp-temp/%(title)s_%(upload_date)s.%(ext)s',  # Save the video with title as filename
    }
    
    # Use yt-dlp to download the video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=yanhEf8jK8o"  # Replace with actual video URL 米津玄師 - 地球儀
    download_video(video_url)