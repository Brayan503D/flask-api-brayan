from yt_dlp import YoutubeDL
import requests
from flask import send_file, Response, request
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
                'descargar_api': f"{request.host_url}download/youtube/file?url={url}",
                'reproducir_api': f"{request.host_url}stream/youtube?url={url}"
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

def reproducir_stream_youtube(url):
    try:
        ydl_opts = {
            "format": "18",
            "quiet": True,
            "skip_download": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt"
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get("url")

        # Pasar la cabecera Range al servidor de YouTube
        headers = {}
        if 'Range' in request.headers:
            headers['Range'] = request.headers['Range']

        r = requests.get(video_url, headers=headers, stream=True)

        return Response(
            r.iter_content(chunk_size=1024),
            status=r.status_code,
            content_type=r.headers.get("Content-Type", "video/mp4"),
            headers={
                key: value for key, value in r.headers.items()
                if key.lower() in ["content-length", "content-range", "accept-ranges", "content-type"]
            }
        )
    except Exception as e:
        return {'error': str(e)}
