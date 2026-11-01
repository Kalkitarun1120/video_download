import os
from yt_dlp import YoutubeDL


DOWNLOAD_FOLDER = "downloads"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def get_media_info(url: str):
    """Fetch video metadata (title, thumbnail, duration) without downloading."""
    options = {
        "skip_download": True,
        "quiet": True,
        "noplaylist": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["web", "default"],
            }
        },
        "js_runtimes": {
            "deno": {}
        },
    }

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "id": info.get("id"),
            "title": info.get("title", "Video"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader") or info.get("channel") or "Unknown",
            "extractor": info.get("extractor_key", "Video"),
        }


def download_video(url: str, quality: str = "best", output_dir: str = DOWNLOAD_FOLDER):

    os.makedirs(output_dir, exist_ok=True)
    postprocessors = []

    if quality == "audio":
        format_selector = "bestaudio/best"
        postprocessors.append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        })
    elif quality == "1080p":
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

    options = {
        "format": format_selector,

        # Merge video + audio into MP4 if not audio-only
        "merge_output_format": None if quality == "audio" else "mp4",

        # Keep title as filename
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

        # Deno runtime
        "js_runtimes": {
            "deno": {}
        },

        # FFmpeg inside Docker / system
        "ffmpeg_location": "/usr/bin" if os.path.exists("/usr/bin/ffmpeg") else None,

        # Don't download playlists accidentally
        "noplaylist": True,
    }

    if postprocessors:
        options["postprocessors"] = postprocessors

    # Clean None values
    options = {k: v for k, v in options.items() if v is not None}

    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(
            url,
            download=True
        )

    return info