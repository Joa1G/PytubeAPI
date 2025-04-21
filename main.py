from fastapi import FastAPI, HTTPException
import yt_dlp

app = FastAPI()

YDL_OPTS = {
            'cookies': './youtube_cookies.txt',
            'quiet': True,
            'skip_download': True,
            'forcejson': True,
            'extract_flat': False,
        }

def format_bytes(size):
    # Formata bytes para uma string legível
    if size is None:
        return "unknown"
    power = 1024
    n = 0
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    while size >= power and n < len(units) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}"


@app.get("/audio_info/{url:path}")
async def get_audio_info(url: str):
    try:
        
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        audio_formats = []
        for f in info['formats']:
            if f.get("vcodec") == "none":
                abr = f.get("abr")
                if abr is not None:
                    abr_str = f"{abr}kbps"
                else:
                    abr_str = "unknown"

                filesize = f.get("filesize") or f.get("filesize_approx")

                audio_formats.append({
                    "format_id": f["format_id"],
                    "ext": f["ext"],
                    "abr": abr_str,
                    "filesize": filesize,
                    "filesize_human": format_bytes(filesize),
                    "format_note": f.get("format_note", ""),
                    "url": f.get("url", "")
                })

        audio_formats.sort(
            key=lambda x: float(x["abr"].replace("kbps", "")) if "kbps" in x["abr"] else 0,
            reverse=True
        )

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


@app.get("/video_info/{url:path}")
async def get_video_with_audio_info(url: str):
    try:
        
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

        video_audio_formats = []
        for f in info['formats']:
            if f.get("vcodec") != "none" and f.get("acodec") != "none":
                filesize = f.get("filesize") or f.get("filesize_approx")

                video_audio_formats.append({
                    "format_id": f["format_id"],
                    "ext": f["ext"],
                    "vcodec": f.get("vcodec"),
                    "acodec": f.get("acodec"),
                    "height": f.get("height"),
                    "fps": f.get("fps"),
                    "filesize": filesize,
                    "filesize_human": format_bytes(filesize),
                    "format_note": f.get("format_note", ""),
                    "url": f.get("url", "")
                })

        video_audio_formats.sort(
            key=lambda x: x["height"] or 0,
            reverse=True
        )

        return {
            "title": info["title"],
            "uploader": info["uploader"],
            "thumbnail": info.get("thumbnail", ""),
            "duration": info.get("duration"),
            "view_count": info.get("view_count"),
            "video_formats": video_audio_formats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
