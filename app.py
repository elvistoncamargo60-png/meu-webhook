from flask import Flask, request, jsonify
import os
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

SH OPEE_AFF_ID = "18345360599"

@app.route('/', methods=['GET'])
def home():
    return "Bot Shopee Afiliados OK!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    message = data.get('message', '').lower().strip()
    chat_id = data.get('chat_id')
    
    if 'oi' in message:
        response = "Oi! Digite 'celular', 'fone' ou 'tv' pra ofertas Shopee!"
    elif 'celular' in message:
        response = scrape_shopee("celular")
    elif 'fone' in message:
        response = scrape_shopee("fone bluetooth")
    elif 'tv' in message:
        response = scrape_shopee("tv smart")
    else:
        response = "Digite 'celular', 'fone' ou 'tv'!"
    
    # Envia resposta Telegram
    token = os.getenv('TELEGRAM_TOKEN')
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                 json={"chat_id": chat_id, "text": response})
    
    return jsonify({"status": "OK"})

def scrape_shopee(query):
    try:
        url = f"https://shopee.com.br/search?keyword={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        products = []
        for item in soup.find_all('div', {'data-sqe': re.compile('item')}')[:3]:
            name = item.find('div', string=re.compile(query))
            price = item.find('span', class_='price')
            link = "https://shopee.com.br" + item.find('a')['href']
            aff_link = f"{link}?af_id={SHOPEE_AFF_ID}"
            
            products.append(f"🔥 {name.text[:50]}... R${price.text} {aff_link}")
        
        return "

".join(products) if products else "Nenhum produto encontrado!"
    except:
        return "Erro no scraping. Tente novamente!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
