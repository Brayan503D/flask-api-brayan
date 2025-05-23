from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os
import traceback

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Obtener información de un video
@app.route("/info/youtube")
def obtener_info():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Falta el parámetro url"}), 400

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
                    "descargar_url": f"{request.host_url}download/youtube/file?url={url}&itag={f['format_id']}"
                })

        formatos.sort(key=lambda x: x["resolucion"])

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "formatos_disponibles": formatos
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"No se pudo obtener información: {str(e)}"}), 500

# Descargar archivo por itag
@app.route("/download/youtube/file")
def descargar_video():
    url = request.args.get("url")
    itag = request.args.get("itag")
    if not url or not itag:
        return jsonify({"error": "Faltan los parámetros url o itag"}), 400

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
                return jsonify({"error": f"No se encontró el itag {itag}"}), 404

            # Generar nombre válido de archivo
            titulo = info.get("title", "video")
            resolucion = formato.get("height", "NA")
            titulo_limpio = "".join(c for c in titulo if c not in r'<>:"/\|?*').strip()
            nombre = f"{titulo_limpio} - {resolucion}p.mp4"
            ruta = os.path.join(DOWNLOAD_FOLDER, nombre)

        # Opciones de descarga
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
            return jsonify({"error": "El archivo no fue generado correctamente"}), 500

        return send_file(ruta, as_attachment=True)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Error al descargar el video: {str(e)}"}), 500

@app.errorhandler(Exception)
def error_global(e):
    traceback.print_exc()
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
