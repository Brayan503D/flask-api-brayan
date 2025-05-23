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
                if (
                    f.get('vcodec') != 'none' and 
                    f.get('ext') == 'mp4' and 
                    f.get('height') is not None
                ):
                    filesize = f.get('filesize', 0) or 0
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
        return {'error': str(e)}

def descargar_archivo_youtube(url):
    try:
        itag = request.args.get("itag")
        if not itag:
            return {"error": "Falta el parámetro itag"}

        # Obtener título y resolución
        ydl_info_opts = {
            "quiet": True,
            "skip_download": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt"
        }

        with YoutubeDL(ydl_info_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formato = next((f for f in info['formats'] if f['format_id'] == itag), None)
            if not formato:
                return {"error": f"No se encontró el itag {itag}"}

            titulo = info.get("title", "video")
            resolucion = formato.get("height", "NA")

            # Limpiar caracteres no válidos del título
            caracteres_invalidos = r'<>:"/\|?*'
            titulo_limpio = "".join(c for c in titulo if c not in caracteres_invalidos).strip()

            nombre_archivo = f"{titulo_limpio} - {resolucion}p.mp4"
            ruta_salida = os.path.join(DOWNLOAD_FOLDER, nombre_archivo)

        # Descargar
        ydl_opts = {
            "format": f"{itag}+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": ruta_salida,
            "quiet": True,
            "noplaylist": True,
            "cookiefile": "cookies.txt"
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(ruta_salida, as_attachment=True)
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

print(f"App escuchando en el puerto {port}")

if __name__ == "__main__":
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
