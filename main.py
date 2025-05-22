from flask import Flask, request, jsonify
from helpers.youtube import descargar_youtube
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
    return jsonify(descargar_youtube(url))

@app.route('/download/twitter')
def twitter():
    url = request.args.get('url')
    if not url:
        return 'Falta el parámetro url', 400
    return jsonify(descargar_twitter(url))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
