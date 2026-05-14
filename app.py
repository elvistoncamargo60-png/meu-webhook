from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os
import threading
import urllib.parse
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip
from moviepy.config import change_settings

app = Flask(__name__)
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8762957424:AAEb-YUWZPO_oo9aXDiXAH-oXHeVPcRK8OQ')
AFF_ID = '18345360599'

# Fix ffmpeg Railway
change_settings({"FFMPEG_BINARY": "ffmpeg"})

def send_video(chat_id, video_path, caption):
    with open(video_path, 'rb') as video:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
            data={'chat_id': chat_id, 'caption': caption},
            files={'video': video}
        )

def scrape_and_video(query, chat_id):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = f"https://shopee.com.br/search?keyword={urllib.parse.quote(query)}"
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    item = soup.find('div', {'data-sqe': True})
    if not item:
        send_text(chat_id, "Nenhum produto Shopee. Tente 'tenis'.")
        return
    
    name = item.find('div', string=True).text.strip()[:30] if item.find('div', string=True) else "Produto Top"
    img_src = item.find('img')['data-src'] if item.find('img') else ""
    link = item.get('href', f"https://shopee.com.br/search?keyword={query}") 
    aff_link = f"{link}&affiliateId={AFF_ID}"
    
    # Download img
    img_resp = requests.get(img_src)
    img_path = '/tmp/produto.jpg'
    with open(img_path, 'wb') as f:
        f.write(img_resp.content)
    
    # Vídeo: img 10s + texto link
    img_clip = ImageClip(img_path).set_duration(10)
    txt_clip = TextClip(f"Compre: {name}
{aff_link}", fontsize=40, color='white', bg_color='black').set_position('center').set_duration(10)
    video = CompositeVideoClip([img_clip, txt_clip]).set_fps(24)
    video_path = '/tmp/video.mp4'
    video.write_videofile(video_path, logger=None)
    
    send_video(chat_id, video_path, f"{name}
ID Afiliado: {AFF_ID}")
    video.close()
    img_clip.close()
    txt_clip.close()

def send_text(chat_id, msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={'chat_id': chat_id, 'text': msg})

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        query = update['message'].get('text', 'shopee')
        send_text(chat_id, f"🎥 Gerando vídeo '{query}' Shopee ID {AFF_ID}...")
        threading.Thread(target=scrape_and_video, args=(query, chat_id)).start()
    return jsonify({"ok": True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
