import uuid
import os
import traceback
from flask import send_file, jsonify
from yt_dlp import YoutubeDL

def descargar_archivo_youtube(url, itag):
    try:
        # Verificar si el archivo de cookies existe
        cookies_file = "cookies.txt"
        usar_cookies = os.path.exists(cookies_file)

        # Configurar opciones para extraer información
        opciones_info = {
            "quiet": True,
            "skip_download": True,
            "noplaylist": True
        }
        if usar_cookies:
            opciones_info["cookiefile"] = cookies_file

        # Obtener información del video
        with YoutubeDL(opciones_info) as ydl:
            info = ydl.extract_info(url, download=False)

        formato = next((f for f in info["formats"] if f["format_id"] == itag), None)
        if not formato:
            return jsonify({"error": f"No se encontró el itag {itag}"}), 400

        # Preparar nombre y ruta temporal
        titulo = info.get("title", "video")
        resolucion = formato.get("height", "NA")
        titulo_limpio = "".join(c for c in titulo if c.isalnum() or c in " _-").strip()
        unique_id = str(uuid.uuid4())
        nombre = f"{titulo_limpio}_{resolucion}p_{unique_id}.mp4"
        ruta = f"/tmp/{nombre}"

        # Opciones para descargar
        opciones_descarga = {
            "format": itag,
            "outtmpl": ruta,
            "merge_output_format": "mp4",
            "quiet": True,
            "noplaylist": True
        }
        if usar_cookies:
            opciones_descarga["cookiefile"] = cookies_file

        # Descargar
        with YoutubeDL(opciones_descarga) as ydl:
            ydl.download([url])

        if not os.path.isfile(ruta):
            return jsonify({"error": "El archivo no fue generado correctamente"}), 500

        # Enviar y borrar
        response = send_file(ruta, as_attachment=True)
        os.remove(ruta)
        return response

    except Exception:
        error_trace = traceback.format_exc()
        print("ERROR en descarga:", error_trace)
        return jsonify({"error": "Error al descargar el video.", "trace": error_trace}), 500
