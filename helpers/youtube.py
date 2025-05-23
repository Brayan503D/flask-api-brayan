from yt_dlp import YoutubeDL
import requests
from flask import send_file, request
import os

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def obtener_info_youtube(url):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': '18',
            'noplaylist': True,
            'cookiefile': 'cookies.txt'
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'url': video_url,
                'descargar_api': f"{request.host_url}download/youtube/file?url={url}"
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
            "cookiefile": "cookies.txt"
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(f"{DOWNLOAD_FOLDER}/video.mp4", as_attachment=True)
    except Exception as e:
        return {'error': str(e)}
