from flask import Flask, request, jsonify
import os
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

SHOPEE_AFF_ID = "18345360599"

@app.route('/', methods=['GET'])
def home():
    return "Bot Shopee Afiliados OK - Webhook pronto!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        message = data.get('message', '').lower().strip() if data else ''
        chat_id = data.get('chat', {}).get('id') or data.get('chat_id')
       
        if not chat_id:
            return jsonify({"error": "No chat_id"}), 400
   
        if 'oi' in message or 'olá' in message:
            response = "Oi! Digite 'ofertas', 'celular', 'fone' ou 'tv' pra Shopee afiliados!"
        elif 'ofertas' in message or 'celular' in message:
            response = scrape_shopee("celular")
        elif 'fone' in message:
            response = scrape_shopee("fone bluetooth")
        elif 'tv' in message:
            response = scrape_shopee("tv smart")
        else:
            response = "Digite 'ofertas', 'celular', 'fone' ou 'tv' pra ver produtos Shopee!"
       
        token = os.getenv('TELEGRAM_TOKEN')
        if token:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                         json={"chat_id": chat_id, "text": response})
            return jsonify({"status": "OK", "response": response})
        else:
            return jsonify({"error": "No TELEGRAM_TOKEN"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def scrape_shopee(query):
    try:
        url = f"https://shopee.com.br/search?keyword={query.replace(' ', '%20')}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
       
        products = []
        # Selector atualizado Shopee BR 2026 - classe comum
        items = soup.find_all('div', {'data-testid': 'shop-search-item-result'}) or soup.select('.shop-search-result-view__item')
        for item in items[:3]:
            name = item.select_one('.item-name, [data-test="item-name"]')
            price = item.select_one('.price, .price-now')
            link_a = item.select_one('a')
            if name and price and link_a:
                name_text = name.get_text(strip=True)[:60] + "..."
                price_text = price.get_text(strip=True)
                link = link_a.get('href', '')
                if link.startswith('/'):
                    link = "https://shopee.com.br" + link
                aff_link = f"{link}?af_id={SHOPEE_AFF_ID}"
                products.append(f"🔥 {name_text}
💰 {price_text}
🛒 {aff_link}")
       
        return "

".join(products) or f"Nenhum {query} agora. Tente 'ofertas'!"
    except:
        return "Scraping temporariamente indisponível. Tente 'oi' pra menu!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
