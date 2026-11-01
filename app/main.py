import os
import shutil
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from starlette.concurrency import run_in_threadpool

from app.downloader import download_video


app = FastAPI(
    title="YouTube Downloader"
)


STATIC_DIR = Path("static")
DOWNLOAD_DIR = Path("downloads")

DOWNLOAD_DIR.mkdir(exist_ok=True)


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


class DownloadRequest(BaseModel):
    url: HttpUrl
    quality: str = "best"


def cleanup_directory(path: Path):
    """Safely remove temporary download folder and files to avoid filling cloud disk."""
    try:
        if path.exists() and path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
    except Exception as e:
        print(f"Error cleaning up directory {path}: {e}")


@app.get("/")
async def home():
    return FileResponse(
        "static/index.html"
    )


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }


@app.post("/api/download")
async def download(request: DownloadRequest, background_tasks: BackgroundTasks):

    allowed_quality = {
        "best",
        "1080p",
        "720p",
        "480p"
    }

    if request.quality not in allowed_quality:
        raise HTTPException(
            status_code=400,
            detail="Invalid quality"
        )

    # Unique directory per request to prevent race conditions between multiple users
    job_id = str(uuid.uuid4())
    job_dir = DOWNLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Run blocking yt-dlp in threadpool so other users aren't blocked
        info = await run_in_threadpool(
            download_video,
            str(request.url),
            request.quality,
            str(job_dir)
        )

        files = [
            file
            for file in job_dir.iterdir()
            if file.is_file()
        ]

        if not files:
            # Clean up empty dir if download failed
            cleanup_directory(job_dir)
            raise HTTPException(
                status_code=500,
                detail="Downloaded file not found"
            )

        downloaded_file = files[0]

        # Register cleanup task so disk doesn't fill up on the cloud server
        background_tasks.add_task(cleanup_directory, job_dir)

        # Return file with real filename and expose Content-Disposition header
        return FileResponse(
            path=downloaded_file,
            filename=downloaded_file.name,
            media_type="application/octet-stream",
            headers={
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )

    except HTTPException:
        cleanup_directory(job_dir)
        raise

    except Exception as e:
        cleanup_directory(job_dir)
        print(f"Download error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )