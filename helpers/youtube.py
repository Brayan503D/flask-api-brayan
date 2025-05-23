from yt_dlp import YoutubeDL
from flask import request

def descargar_youtube(url):
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
