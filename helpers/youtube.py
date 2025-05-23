from yt_dlp import YoutubeDL
from flask import Flask, send_file, request
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

            formatos_disponibles = []
            for f in info['formats']:
                # Solo video mp4 con resolución válida (y que puede combinarse con audio)
                if (
                    f.get('vcodec') != 'none' and 
                    f.get('ext') == 'mp4' and 
                    f.get('height') is not None
                ):
                    formatos_disponibles.append({
                        'itag': f['format_id'],
                        'resolucion': f['height']
                    })

            formatos_disponibles.sort(key=lambda x: x['resolucion'])

            apis_descarga = {}
            for i, f in enumerate(formatos_disponibles):
                clave = "descargar_api" if i == 0 else f"descargar_api{i+1}"
                apis_descarga[clave] = f"{request.host_url}download/youtube/file?url={url}&itag={f['itag']}"

            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'formatos_disponibles': [f"{f['resolucion']}p (itag: {f['itag']})" for f in formatos_disponibles],
                **apis_descarga
            }
    except Exception as e:
        return {'error': str(e)}

def descargar_archivo_youtube(url):
    try:
        itag = request.args.get("itag")
        if not itag:
            return {"error": "Falta el parámetro itag"}

        # Descargar video con el itag dado y combinar con el mejor audio
        ydl_opts = {
            "format": f"{itag}+bestaudio/best",
            "merge_output_format": "mp4",
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
