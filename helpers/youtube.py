from yt_dlp import YoutubeDL

def descargar_youtube(url):
    try:
        ydl_opts = {'quiet': True, 'skip_download': True, 'format': 'best', 'noplaylist': True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {'title': info.get('title'), 'url': info.get('url'), 'thumbnail': info.get('thumbnail')}
    except Exception as e:
        return {'error': str(e)}
