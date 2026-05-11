import os
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip
from threading import Thread
import urllib.parse
import tempfile

app = Flask(__name__)

def processa(query):
    # Scraping Shopee
    url = f"https://shopee.com.br/search?keyword={urllib.parse.quote(query)}"
    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(resp.text, 'html.parser')
    item = soup.find('a', {'data-sqe': True})
    if not item: return
    img = item.find('img')['data-src']
    link = 'https://shopee.com.br' + item['href'] + f"&affiliateId=18345360599"
    
    # Download img
    img_resp = requests.get(img)
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        tmp.write(img_resp.content)
        img_path = tmp.name
    
    # Vídeo MoviePy
    img_clip = ImageClip(img_path, duration=10)
    txt = TextClip(f"Produto Shopee!
{link}", fontsize=40, color='white', bg_color='black').set_position('center').set_duration(10)
    video = CompositeVideoClip([img_clip, txt]).write_videofile('/tmp/video.mp4', fps=24)
    
    # Envia Telegram (seu CHAT_ID)
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    with open('/tmp/video.mp4', 'rb') as v:
        requests.post(f"https://api.telegram.org/bot{token}/sendVideo", data={'chat_id': chat_id, 'caption': f'ID 18345360599
{link}'}, files={'video': v})

@app.route('/')
def home(): return "AffiliateFlow AI v24 OK!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json or {}
    query = data.get('query', 'oi')
    Thread(target=processa, args=(query,)).start()
    return jsonify({"response": f"Produto Shopee encontrado!
Link afiliado: {urllib.parse.quote(link, safe='')}
Vídeo enviado ao canal."}), 200  # Ajuste link real pós-scraping
