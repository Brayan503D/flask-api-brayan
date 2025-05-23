from yt_dlp import YoutubeDL
import requests
from flask import Flask, send_file, Response, request
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def obtener_info_youtube(url):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'noplaylist': True,
            'cookiefile': 'cookies.txt',
            'format': 'bestvideo+bestaudio/best'
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            video_url = info.get('url')
            formatos_disponibles = []
            for f in info['formats']:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    formatos_disponibles.append({
                        'itag': f['format_id'],
                        'resolucion': f.get('height', 0)
                    })

            formatos_disponibles.sort(key=lambda x: x['resolucion'])

            apis_descarga = {}
            for i, f in enumerate(formatos_disponibles):
                clave = "descargar_api" if i == 0 else f"descargar_api{i+1}"
                apis_descarga[clave] = f"{request.host_url}download/youtube/file?url={url}&itag={f['itag']}"

            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'url': video_url,
                'formatos_disponibles': [f"{f['resolucion']}p (itag: {f['itag']})" for f in formatos_disponibles],
                'reproducir_api': f"{request.host_url}stream/youtube?url={url}",
                **apis_descarga
            }
    except Exception as e:
        return {'error': str(e)}

def descargar_archivo_youtube(url):
    try:
        itag = request.args.get("itag")
        if not itag:
            return {"error": "Falta el parámetro itag"}

        ydl_opts = {
            "format": itag,
            "outtmpl": f"{DOWNLOAD_FOLDER}/video_{itag}.mp4",
            "quiet": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt"
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(f"{DOWNLOAD_FOLDER}/video_{itag}.mp4", as_attachment=True)
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

@app.route("/info/youtube")
def info_youtube():
    url = request.args.get("url")
    if not url:
        return {"error": "Falta el parámetro url"}
    return obtener_info_youtube(url)

@app.route("/download/youtube/file")
def download_youtube():
    url = request.args.get("url")
    if not url:
        return {"error": "Falta el parámetro url"}
    return descargar_archivo_youtube(url)

@app.route("/stream/youtube")
def stream_youtube():
    url = request.args.get("url")
    if not url:
        return {"error": "Falta el parámetro url"}
    return reproducir_stream_youtube(url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
