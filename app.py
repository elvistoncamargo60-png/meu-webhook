from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Bot Link Shopee 2 OK!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    msg = data.get('message', '').lower()
    chat_id = data.get('chat_id')
    if 'oi' in msg:
        response = "Oi! Digite 'ofertas' pra Shopee!"
    elif 'oferta' in msg or 'ofertas' in msg:
        response = "🔥 TOP: iPhone R$3999 [LINK_AFILIADO] | Fone JBL R$199 [LINK] | TV R$1899 [LINK]"
    else:
        response = "Digite 'ofertas' ou 'celular'!"
    token = os.getenv('TELEGRAM_TOKEN')
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": response})
    print(f"Webhook: {msg} -> {response}")
    return jsonify({"status": "OK", "response": response})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
