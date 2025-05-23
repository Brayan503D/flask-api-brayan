from flask import send_file, jsonify, request
from yt_dlp import YoutubeDL
import os
import traceback

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def obtener_info_youtube(url, host_url=None):
    try:
        opciones = {
            "quiet": True,
            "skip_download": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt",
        }

        with YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=False)

        formatos = []
        for f in info.get("formats", []):
            if f.get("vcodec") != "none" and f.get("ext") == "mp4" and f.get("height"):
                size = f.get("filesize") or 0
                formatos.append({
                    "itag": f["format_id"],
                    "resolucion": f["height"],
                    "filesize_mb": round(size / 1024 / 1024, 2),
                    "descargar_url": f"{host_url}download/youtube/file?url={url}&itag={f['format_id']}" if host_url else None
                })

        formatos.sort(key=lambda x: x["resolucion"])

        return {
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "formatos_disponibles": formatos
        }

    except Exception as e:
        traceback.print_exc()
        return {"error": f"No se pudo obtener información: {str(e)}"}

def descargar_archivo_youtube(url, itag):
    try:
        with YoutubeDL({
            "quiet": True,
            "skip_download": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt"
        }) as ydl:
            info = ydl.extract_info(url, download=False)
            formato = next((f for f in info["formats"] if f["format_id"] == itag), None)
            if not formato:
                return {"error": f"No se encontró el itag {itag}"}

            titulo = info.get("title", "video")
            resolucion = formato.get("height", "NA")
            titulo_limpio = "".join(c for c in titulo if c not in r'<>:"/\|?*').strip()
            nombre = f"{titulo_limpio} - {resolucion}p.mp4"
            ruta = os.path.join(DOWNLOAD_FOLDER, nombre)

        opciones_descarga = {
            "format": itag,
            "outtmpl": ruta,
            "merge_output_format": "mp4",
            "quiet": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt"
        }

        with YoutubeDL(opciones_descarga) as ydl:
            ydl.download([url])

        if not os.path.isfile(ruta):
            return {"error": "El archivo no fue generado correctamente"}

        return send_file(ruta, as_attachment=True)

    except Exception as e:
        traceback.print_exc()
        return {"error": f"Error al descargar el video: {str(e)}"}


# RUTAS FLASK

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/download/youtube')
def youtube():
    url = request.args.get('url')
    if not url:
        return 'Falta el parámetro url', 400
    return jsonify(obtener_info_youtube(url, host_url=request.host_url))

@app.route('/download/youtube/file')
def descargar_youtube_file():
    url = request.args.get('url')
    itag = request.args.get('itag')
    if not url or not itag:
        return jsonify({"error": "Faltan los parámetros url o itag"}), 400
    return descargar_archivo_youtube(url, itag)
