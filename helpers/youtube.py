from yt_dlp import YoutubeDL
from flask import Flask, send_file, request, jsonify
import os
import ssl
import socket
import traceback

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
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('ext') == 'mp4' and f.get('height'):
                    filesize = f.get('filesize') or 0
                    formatos_disponibles.append({
                        'itag': f['format_id'],
                        'resolucion': f['height'],
                        'vcodec': f.get('vcodec'),
                        'filesize_bytes': filesize,
                        'filesize_mb': round(filesize / 1024 / 1024, 2),
                        'bitrate_kbps': int(f.get('tbr', 0)),
                        'descargar_url': f"{request.host_url}download/youtube/file?url={url}&itag={f['format_id']}"
                    })

            formatos_disponibles.sort(key=lambda x: x['resolucion'])

            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'formatos_disponibles': formatos_disponibles
            }
    except Exception as e:
        return {'error': f'Error obteniendo info: {str(e)}'}

def descargar_archivo_youtube(url):
    try:
        itag = request.args.get("itag")
        if not itag:
            return jsonify({"error": "Falta el parámetro itag"}), 400

        # Obtener info
        with YoutubeDL({
            "quiet": True,
            "skip_download": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt"
        }) as ydl:
            info = ydl.extract_info(url, download=False)
            formato = next((f for f in info.get('formats', []) if f['format_id'] == itag), None)
            if not formato:
                return jsonify({"error": f"No se encontró el itag {itag}"}), 404

            titulo = info.get("title", "video")
            resolucion = formato.get("height", "NA")
            caracteres_invalidos = r'<>:"/\|?*'
            titulo_limpio = "".join(c for c in titulo if c not in caracteres_invalidos).strip()
            nombre_archivo = f"{titulo_limpio} - {resolucion}p.mp4"
            ruta_salida = os.path.join(DOWNLOAD_FOLDER, nombre_archivo)

        # Descargar video
        ydl_opts = {
            "format": itag,
            "outtmpl": ruta_salida,
            "quiet": True,
            "noplaylist": True,
            "merge_output_format": "mp4",
            "cookiefile": "cookies.txt"
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except (ssl.SSLError, socket.error) as net_err:
            return jsonify({"error": f"Error de red/SSL: {str(net_err)}"}), 503
        except Exception as e:
            if os.path.exists(ruta_salida):
                os.remove(ruta_salida)
            app.logger.error(f"Error al descargar el video: {str(e)}")
            traceback.print_exc()
            return jsonify({"error": f"No se pudo descargar el archivo. {str(e)}"}), 500

        if not os.path.isfile(ruta_salida):
            return jsonify({"error": "El archivo no fue generado"}), 500

        return send_file(ruta_salida, as_attachment=True)

    except Exception as e:
        app.logger.error(f"Error inesperado en la descarga: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@app.route("/info/youtube")
def info_youtube():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Falta el parámetro url"}), 400
    resultado = obtener_info_youtube(url)
    if 'error' in resultado:
        return jsonify(resultado), 500
    return jsonify(resultado)

@app.route("/download/youtube/file")
def download_youtube():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Falta el parámetro url"}), 400
    return descargar_archivo_youtube(url)

@app.errorhandler(Exception)
def manejar_errores_globales(e):
    app.logger.error(f"Error global: {str(e)}")
    traceback.print_exc()
    return jsonify({"error": "Error interno en el servidor"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
