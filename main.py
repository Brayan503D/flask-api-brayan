from flask import Flask, request
import requests
import os

app = Flask(__name__)

def resolver_url(url):
    try:
        res = requests.head(url, allow_redirects=True, timeout=5)
        return res.url
    except:
        return url  # si falla, usa la original

@app.route('/')
def home():
    return 'API activa'

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return 'Falta el parámetro url', 400

    url_resuelta = resolver_url(url)

    try:
        res = requests.get(f'https://api.dl.downloadgram.org/?url={url_resuelta}', timeout=10)
        return res.json()
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
