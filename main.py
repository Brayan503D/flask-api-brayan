from flask import Flask, request, jsonify, send_file, Response
from helpers.youtube import descargar_youtube
from helpers.twitter import descargar_twitter
import yt_dlp
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

# Ruta para descargar el video directamente (archivo)
@app.route("/download/youtube/file")
def download_video():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Falta el parámetro 'url'"}), 400

    ydl_opts = {
        "format": "18",
        "outtmpl": f"{DOWNLOAD_FOLDER}/video.mp4",
        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(f"{DOWNLOAD_FOLDER}/video.mp4", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para hacer streaming (proxy) del video YouTube
@app.route("/stream/youtube")
def stream_video():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Falta el parámetro 'url'"}), 400

    ydl_opts = {
        "format": "18",
        "quiet": True,
        "skip_download": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info["url"]

        r = requests.get(video_url, stream=True)
        return Response(r.iter_content(chunk_size=1024), content_type="video/mp4")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
