import os
from yt_dlp import YoutubeDL


DOWNLOAD_FOLDER = "downloads"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def download_video(url: str, quality: str = "best", output_dir: str = DOWNLOAD_FOLDER):

    if quality == "1080p":
        format_selector = (
            "bestvideo[height<=1080]+bestaudio/"
            "best[height<=1080]"
        )

    elif quality == "720p":
        format_selector = (
            "bestvideo[height<=720]+bestaudio/"
            "best[height<=720]"
        )

    elif quality == "480p":
        format_selector = (
            "bestvideo[height<=480]+bestaudio/"
            "best[height<=480]"
        )

    else:
        format_selector = "bestvideo*+bestaudio/best"

    os.makedirs(output_dir, exist_ok=True)

    options = {
        "format": format_selector,

        # Merge video + audio into MP4
        "merge_output_format": "mp4",

        # Keep YouTube title as filename
        "outtmpl": os.path.join(
            output_dir,
            "%(title)s.%(ext)s"
        ),

        "continuedl": True,
        "retries": 10,
        "fragment_retries": 10,

        "ignoreerrors": False,
        "quiet": False,
        "overwrites": True,

        # Modern extractor args to avoid bot detection
        "extractor_args": {
            "youtube": {
                "player_client": ["web", "default"],
            }
        },

        # Deno
        "js_runtimes": {
            "deno": {}
        },

        # FFmpeg inside Docker / system
        "ffmpeg_location": "/usr/bin" if os.path.exists("/usr/bin/ffmpeg") else None,

        # Don't download playlists accidentally
        "noplaylist": True,
    }

    # Clean None values
    options = {k: v for k, v in options.items() if v is not None}

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(
            url,
            download=True
        )

    return info