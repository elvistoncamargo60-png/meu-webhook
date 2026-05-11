from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip
import os
import uuid
from threading import Thread
import time
import urllib.parse  # Para URL encode

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'SEU_TOKEN_BOTFATHER_AQUI')
CHAT_ID = os.environ.get('CHAT_ID', '@seu_canal_ou_chat_id')  # Seu chat/canal Telegram
AFFILIATE_ID = "18345360599"
SHOPEE_BASE = "https://shopee.com.br"

def process_scraping(query="whey protein"):
    """Task assíncrona: scrape → vídeo → envia Telegram"""
    try:
        # Scrape Shopee (simplificado BeautifulSoup; expanda Selenium se captcha)
        url = f"{SHOPEE_BASE}/search?keyword={urllib.parse.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        prod_link_tag = soup.find('a', {'data-sqe': True})
        prod_link = SHOPEE_BASE + prod_link_tag['href'] if prod_link_tag else None
        if not prod_link:
            send_telegram("Produto não encontrado.")
            return
        
        aff_link = f"{prod_link}?affiliateId={AFFILIATE_ID}"
        
        # Baixa imagem
        img_tag = soup.find('img', {'data-src': True})
        img_url = img_tag['data-src'] if img_tag else None
        img_path = f"/tmp/{uuid.uuid4()}.jpg"
        if img_url:
            img_resp = requests.get(img_url)
            with open(img_path, 'wb') as f:
                f.write(img_resp.content)
        else:
            send_telegram(f"Oferta Shopee: {aff_link}")
            return
        
        # Gera vídeo MoviePy 10s + overlay
        video_path = f"/tmp/{uuid.uuid4()}.mp4"
        img_clip = ImageClip(img_path, duration=10)
       txt_clip = TextClip(f"Compre agora!\
{aff_link}", fontsize=40, color='white', bg_color='black').set_position(('center', 'bottom')).set_duration(10) 
        final_clip = CompositeVideoClip([img_clip, txt_clip])
        final_clip.write_videofile(video_path, fps=24, verbose=False, logger=None)
        
        # Envia vídeo Telegram
        with open(video_path, 'rb') as vid:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo",
                data={'chat_id': CHAT_ID, 'caption': f'Oferta top! ID {AFFILIATE_ID}
{aff_link}'},
                files={'video': vid}
            )
        
        # Cleanup
        os.remove(img_path)
        os.remove(video_path)
        send_telegram("Vídeo enviado! Confira acima. 😎")
    except Exception as e:
        send_telegram(f"Erro: {str(e)}")

def send_telegram(msg):
    """Helper: envia msg rápida Telegram"""
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                  data={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'})

@app.route('/')
def home():
    return "AffiliateFlow AI v24 - 100% Autônomo!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json or {}
    query = data.get('query', 'oi').lower()
    
    # Resposta IMEDIATA para SendPulse (evita timeout) [Gemini ponto 2]
    Thread(target=process_scraping, args=(query,)).start()
    
    return jsonify({"response": "Oi! Scraping Shopee + vídeo gerado em background. Aguarde no chat! 🚀"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
