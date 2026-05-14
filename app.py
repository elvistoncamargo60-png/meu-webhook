from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os
import threading
import urllib.parse
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip

app = Flask(__name__)
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8762957424:AAEb-YUWZPO_oo9aXDiXAH-oXHeVPcRK8OQ')
AFF_ID = '18345360599'

def send_video(chat_id, video_path, caption):
    with open(video_path, 'rb') as f:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo", 
                     data={'chat_id': chat_id, 'caption': caption}, files={'video': f})

def send_text(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={'chat_id': chat_id, 'text': text})

def make_video(query, chat_id):
    send_text(chat_id, f"🎥 Vídeo '{query}' Shopee ID {AFF_ID} pronto!")
    
    # Scraping simples
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15'}
    url = "https://shopee.com.br/search?keyword=" + urllib.parse.quote(query)
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    item = soup.select_one('[data-sqe]')
    if not item:
        send_text(chat_id, "Produto não encontrado. Tente 'tenis'")
        return
    
    name_tag = item.select_one('.KzDlHZ')
    name = name_tag.text[:30] if name_tag else "Produto Shopee"
    img_tag = item.select_one('img')
    img_url = img_tag['data-src'] if img_tag else ""
    
    if not img_url:
        send_text(chat_id, "Img não achada")
        return
    
    # Download img
    img_data = requests.get(img_url).content
    img_path = '/tmp/prod.jpg'
    with open(img_path, 'wb') as f:
        f.write(img_data)
    
    aff_link = f"https://shopee.com.br/search?keyword={urllib.parse.quote(query)}&affiliateId={AFF_ID}"
    
    # Vídeo
    img_clip = ImageClip(img_path).resize((512,512)).set_duration(8)
    txt = TextClip(f"{name}\
{aff_link}", fontsize=30, color='yellow', font='Arial-Bold').set_position('center').set_duration(8)
    final = CompositeVideoClip([img_clip, txt.set_pos('center')])
    video_path = '/tmp/shopee_video.mp4'
    final.write_videofile(video_path, fps=24, logger=None, audio=False)
    
    send_video(chat_id, video_path, f"🚀 {name}\
Link: {aff_link}\
ID: {AFF_ID}")
    
    final.close()
    img_clip.close()
    txt.close()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        query = data['message'].get('text', '').lower()
        send_text(chat_id, "🔍 Scraping + vídeo em 10s...")
        threading.Thread(target=make_video, args=(query, chat_id)).start()
    return jsonify({'status': 'ok'})

@app.route('/')
def index():
    return "AffiliateFlow AI - Video Bot OK!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
