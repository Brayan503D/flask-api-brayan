from yt_dlp import YoutubeDL
import requests
from flask import send_file, request
import os

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
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    formatos_disponibles.append({
                        'itag': f['format_id'],
                        'resolucion': f.get('height', 0)
                    })

            # Ordenar de menor a mayor calidad
            formatos_disponibles.sort(key=lambda x: x['resolucion'])

            # Generar múltiples descargar_api con resoluciones
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
