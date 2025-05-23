from flask import Flask, request, jsonify
from helpers.youtube import obtener_info_youtube, descargar_archivo_youtube
from helpers.twitter import descargar_twitter

app = Flask(__name__)

@app.route('/')
def home():
    return 'API de descargas activa'

@app.route('/download/youtube')
def youtube():
    url = request.args.get('url')
    if not url:
        return 'Falta el parámetro url', 400
    return jsonify(obtener_info_youtube(url))

@app.route('/download/youtube/file')
def youtube_file():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Falta el parámetro url'}), 400
    respuesta = descargar_archivo_youtube(url)
    if isinstance(respuesta, dict):
        return jsonify(respuesta), 500
    return respuesta

@app.route('/download/twitter')
def twitter():
    url = request.args.get('url')
    if not url:
        return 'Falta el parámetro url', 400
    return jsonify(descargar_twitter(url))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
