import uuid
import tempfile
from flask import send_file, jsonify
from yt_dlp import YoutubeDL
import os
import traceback

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

        if not host_url:
            host_url = "https://api-downloader-2cuz.onrender.com/"
        elif not host_url.endswith("/"):
            host_url += "/"

        formatos = []
        for f in info.get("formats", []):
            if f.get("vcodec") != "none" and f.get("ext") == "mp4" and f.get("height"):
                size = f.get("filesize") or 0
                formatos.append({
                    "itag": f["format_id"],
                    "resolucion": f["height"],
                    "filesize_mb": round(size / 1024 / 1024, 2),
                    "descargar_url": f"{host_url}download/youtube/file?url={url}&itag={f['format_id']}"
                })

        formatos.sort(key=lambda x: x["resolucion"])

        return {
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "formatos_disponibles": formatos
        }

    except Exception:
        error_trace = traceback.format_exc()
        print(error_trace)
        return {"error": "No se pudo obtener información del video.", "trace": error_trace}

def descargar_archivo_youtube(url, itag):
    try:
        # Obtener información
        with YoutubeDL({
            "quiet": True,
            "skip_download": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt"
        }) as ydl:
            info = ydl.extract_info(url, download=False)
            formato = next((f for f in info["formats"] if f["format_id"] == itag), None)
            if not formato:
                return jsonify({"error": f"No se encontró el itag {itag}"}), 400

            titulo = info.get("title", "video")
            resolucion = formato.get("height", "NA")
            titulo_limpio = "".join(c for c in titulo if c.isalnum() or c in " _-").strip()
            unique_id = str(uuid.uuid4())
            nombre = f"{titulo_limpio}_{resolucion}p_{unique_id}.mp4"
            ruta = os.path.join(tempfile.gettempdir(), nombre)

        # Descargar
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
            print("Archivo no generado:", ruta)
            return jsonify({"error": "El archivo no fue generado correctamente."}), 500

        print("Archivo generado correctamente:", ruta)
        response = send_file(ruta, as_attachment=True)
        os.remove(ruta)  # Borrar después de enviar
        return response

    except Exception:
        error_trace = traceback.format_exc()
        print("ERROR en descarga:", error_trace)
        return jsonify({"error": "Error al descargar el video.", "trace": error_trace}), 500
