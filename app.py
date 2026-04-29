
from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Bot Link Shopee 2 - Webhook OK!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No data"}), 400
    
    msg = data.get('message', '').lower()
    chat_id = data.get('chat_id')
    
    if 'oi' in msg or '/start' in msg:
        response = "Oi! Digite 'ofertas' pra top Shopee!"
    elif 'oferta' in msg:
        response = "🔥 TOP Shopee: iPhone R$3999 [LINK] | Fone JBL R$199 [LINK] | TV R$1899 [LINK]"
    else:
        response = "Digite 'ofertas' ou 'celular' pra links Shopee!"
    
    token = os.getenv('TELEGRAM_TOKEN')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": response})
    
    print(f"Bot Shopee 2: {msg} -> {response}")
    
    return jsonify({"status": "OK"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
