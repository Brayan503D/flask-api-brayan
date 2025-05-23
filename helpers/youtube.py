from yt_dlp import YoutubeDL
import requests
from flask import send_file, Response
import os

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def obtener_info_youtube(url):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'best',
            'noplaylist': True,
            'cookiefile': 'cookies.txt'
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title'),
                'url': info.get('url'),
                'thumbnail': info.get('thumbnail')
            }
    except Exception as e:
        return {'error': str(e)}

def descargar_archivo_youtube(url):
    try:
        ydl_opts = {
            "format": "18",
            "outtmpl": f"{DOWNLOAD_FOLDER}/video.mp4",
            "quiet": True,
            "noplaylist": True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(f"{DOWNLOAD_FOLDER}/video.mp4", as_attachment=True)
    except Exception as e:
        return {'error': str(e)}

def reproducir_stream_youtube(url):
    try:
        ydl_opts = {
            "format": "18",
            "quiet": True,
            "skip_download": True,
            "noplaylist": True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get("url")
        
        r = requests.get(video_url, stream=True)
        return Response(r.iter_content(chunk_size=1024), content_type="video/mp4")
    except Exception as e:
        return {'error': str(e)}
