from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import logging
import os
import threading
import urllib.parse
from urllib.parse import quote

app = Flask(__name__)

# Token via env (melhor que hardcoded)
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8762957424:AAEb-YUWZPO_oo9aXDiXAH-oXHeVPcRK8OQ')
AFF_ID = '18345360599'

def send_text(chat_id, msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})

def scrape_shopee(query):
    """Scraping real Shopee 2026 (headers anti-bot)"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    url = f"https://shopee.com.br/search?keyword={quote(query)}"
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    produtos = []
    for item in soup.find_all('div', {'data-sqe': True})[:5]:
        name = item.find('div', string=True) or 'Produto Top'
        link = item.get('data-url') or f"https://shopee.com.br/?keyword={quote(query)}"
        aff_link = f"{link}&affiliateId={AFF_ID}" if '?' in link else f"{link}?affiliateId={AFF_ID}"
        produtos.append(f"• {name.strip()[:50]}: [Comprar]({aff_link})")
    
    return "
".join(produtos) or "Nenhum produto encontrado (tente 'tênis')"

def process_async(chat_id, query):
    """Async: scraping + futuro vídeo"""
    msg = f"Processando '{query}' Shopee...

"
    send_text(chat_id, msg + scrape_shopee(query))

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    logging.info(f"Webhook recebido: {update}")
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        query = update['message'].get('text', 'shopee')
        
        # Resposta imediata anti-timeout
        send_text(chat_id, f"🔍 Buscando '{query}' no Shopee (ID {AFF_ID})...")
        
        # Thread para scraping pesado
        threading.Thread(target=process_async, args=(chat_id, query)).start()
    
    return jsonify({"ok": True}), 200

@app.route('/')
def home():
    return "AffiliateFlow AI v24 - Railway OK!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
