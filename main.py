from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post("/audio_info")
async def get_audio_info(data: VideoRequest):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'forcejson': True,
            'extract_flat': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url, download=False)

        # Modificando para incluir os links de download diretamente
        audio_formats = [
            {
                "format_id": f["format_id"],
                "ext": f["ext"],
                "abr": f.get("abr", "unknown"),
                "filesize": f.get("filesize", None),
                "format_note": f.get("format_note", ""),
                "url": f.get("url", "")  # Incluindo a URL de download diretamente aqui
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
