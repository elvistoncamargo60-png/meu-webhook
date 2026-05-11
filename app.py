from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os
from threading import Thread
import urllib.parse

app = Flask(__name__)

def processa(query):
    try:
        url = f"https://shopee.com.br/search?keyword={urllib.parse.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        item = soup.find('a', {'data-sqe': True})
        if item:
            prod_name = item.get('aria-label', 'Produto Shopee')
            link = 'https://shopee.com.br' + item['href'] + '&affiliateId=18345360599'
            token = os.getenv('TELEGRAM_BOT_TOKEN')
            chat_id = os.getenv('CHAT_ID')
            if token and chat_id:
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                              data={'chat_id': chat_id, 'text': prod_name + '\
Link: ' + link + '\
ID 18345360599'})
    except:
        pass

@app.route('/')
def home():
    return 'AffiliateFlow AI v24 OK!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json() or {}
    query = data.get('query', 'oi')
    Thread(target=processa, args=(query,)).start()
    response_text = 'Produto Shopee via IA!\
Link afiliado: https://shopee.com.br/produto?aff=18345360599\
Vídeo em breve.'
    return jsonify({'response': response_text}), 200
