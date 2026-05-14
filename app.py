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

def send_text(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={'chat_id': chat_id, 'text': text})

def send_video(chat_id, video_path, caption):
    if os.path.exists(video_path):
        with open(video_path, 'rb') as f:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo", 
                         data={'chat_id': chat_id, 'caption': caption}, files={'video': f})

def create_fallback_video(query, chat_id):
    """Vídeo fallback se scraping falha"""
    aff_link = f"https://shopee.com.br/search?keyword={urllib.parse.quote(query)}&affiliateId={AFF_ID}"
    txt_clip = TextClip(f"Ofertas {query.title()}\
ID {AFF_ID}\
{aff_link}", fontsize=40, color='white', bg_color='blue').set_duration(10).set_fps(24)
    video_path = '/tmp/fallback.mp4'
    txt_clip.write_videofile(video_path, fps=24, logger=None)
    send_video(chat_id, video_path, f"Vídeo {query} pronto! Clique link acima.")
    txt_clip.close()

def scrape_shopee_video(query, chat_id):
    print(f"QUERY: {query}")  # Railway logs
    send_text(chat_id, f"🔍 Buscando '{query}' Shopee...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Referer': 'https://shopee.com.br/'
    }
    
    url = f"https://shopee.com.br/search?keyword={urllib.parse.quote(query)}"
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Selectors múltiplos Shopee 2026
    items = soup.find_all(['a', 'div'], class_=lambda x: x and ('product' in x.lower() or 'item' in x.lower() or 'sqe' in x.lower()))[:1]
    item = items[0] if items else None
    
    if not item:
        print("NO ITEMS")
        create_fallback_video(query, chat_id)
        return
    
    # Nome
    name_selectors = ['.title', '[data-testid="product-title"]', '.name', 'h3', '.KzDlHZ']
    name = "Produto Shopee"
    for sel in name_selectors:
        tag = item.select_one(sel)
        if tag:
            name = tag.get_text(strip=True)[:40]
            break
    
    # Img
    img_url = ""
    img_selectors = ['img[data-src]', 'img[src*="shopee"]', 'img']
    for sel in img_selectors:
        img_tag = item.select_one(sel)
        if img_tag:
            img_url = img_tag.get('data-src') or img_tag.get('src') or img_tag.get('data-lazy')
            if img_url and ('http' in img_url or img_url.startswith('//')):
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                break
    
    print(f"NOME: {name}, IMG: {img_url[:60]}")
    
    aff_link = f"https://shopee.com.br/search?keyword={urllib.parse.quote(query)}&affiliateId={AFF_ID}"
    
    if img_url:
        try:
            img_data = requests.get(img_url, headers=headers, timeout=10).content
            img_path = '/tmp/prod.jpg'
            with open(img_path, 'wb') as f:
                f.write(img_data)
            
            # Vídeo
            img_clip = ImageClip(img_path).resize(height=400).set_duration(10)
            txt_clip = TextClip(f"{name}\
Comprar agora!\
{aff_link}", fontsize=30, color='white', stroke_color='black', stroke_width=2).set_position('center').set_duration(10)
            video = CompositeVideoClip([img_clip, txt_clip])
            video_path = '/tmp/video.mp4'
            video.write_videofile(video_path, fps=24, verbose=False, logger=None)
            
            send_video(chat_id, video_path, f"🚀 {name}\
ID Afiliado: {AFF_ID}")
            os.remove(img_path)
            os.remove(video_path)
            video.close()
        except Exception as e:
            print(f"VIDEO ERROR: {e}")
            create_fallback_video(query, chat_id)
    else:
        create_fallback_video(query, chat_id)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"POST DATA: {data.get('message', {}).get('text', 'no text')}")
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        query = data['message'].get('text', 'shopee').strip().lower()
        if query in ['/start', 'oi']:
            send_text(chat_id, "Digite produto ex: 'tenis' 'celular' 'whey'")
            return jsonify({'ok': True})
        threading.Thread(target=scrape_shopee_video, args=(query, chat_id)).start()
    return jsonify({'ok': True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
