from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

@app.get("/audio_info/{url:path}")
async def get_audio_info(url: str):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'forcejson': True,
            'extract_flat': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        audio_formats = [
            {
                "format_id": f["format_id"],
                "ext": f["ext"],
                "abr": f.get("abr", "unknown"),
                "filesize": f.get("filesize", None),
                "format_note": f.get("format_note", ""),
                "url": f.get("url", "")
            }
            for f in info['formats'] if f.get("vcodec") == "none"
        ]

        return {
            "title": info["title"],
            "uploader": info["uploader"],
            "thumbnail": info.get("thumbnail", ""),
            "duration": info.get("duration"),
            "view_count": info.get("view_count"),
            "audio_formats": audio_formats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))