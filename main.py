from flask import Flask, request, jsonify, send_file, Response
from helpers.youtube import descargar_youtube
from helpers.twitter import descargar_twitter
from yt_dlp import YoutubeDL
import requests
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return 'API de descargas activa'

@app.route('/download/youtube')
def youtube():
    url = request.args.get('url')
    if not url:
        return 'Falta el parámetro url', 400
    return jsonify(descargar_youtube(url))

@app.route('/download/twitter')
def twitter():
    url = request.args.get('url')
    if not url:
        return 'Falta el parámetro url', 400
    return jsonify(descargar_twitter(url))

# Nueva ruta: descarga directa del video (archivo)
@app.route('/download/youtube/file')
def download_youtube_file():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Falta el parámetro 'url'"}), 400

    ydl_opts = {
        "format": "18",  # mp4 360p (puedes ajustar formato)
        "outtmpl": f"{DOWNLOAD_FOLDER}/video.mp4",
        "quiet": True,
        "noplaylist": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(f"{DOWNLOAD_FOLDER}/video.mp4", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Nueva ruta: streaming proxy del video
@app.route('/stream/youtube')
def stream_youtube():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Falta el parámetro 'url'"}), 400

    ydl_opts = {
        "format": "18",
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get("url")
        
        r = requests.get(video_url, stream=True)
        return Response(r.iter_content(chunk_size=1024), content_type="video/mp4")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
