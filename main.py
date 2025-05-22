from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return 'API activa'

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return 'Falta el parámetro url', 400

    try:
        res = requests.get(f'https://api.dl.downloadgram.org/?url={url}')
        return res.json()
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
