from flask import Flask, request, jsonify
import os
import requests  # pra chamadas scraping/vídeo

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "AffiliateFlow AI v19 Webhook - Railway OK!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json  # SendPulse envia JSON (user msg, chat_id)
    if not data:
        return jsonify({"error": "No data"}), 400
    
    msg = data.get('message', '').lower()  # ex: "oi" ou "ofertas"
    chat_id = data.get('chat_id')  # Telegram ID
    
    # Lógica simples IA
    if 'oi' in msg or '/start' in msg:
        response = "Oi! Digite 'ofertas' pra top Shopee afiliados!"
    elif 'oferta' in msg:
        response = "🔥 TOP Shopee: iPhone R$3999 [LINK_AFILIADO] | Fone JBL R$199 [LINK] | TV R$1899 [LINK]"
        # Aqui chama scraping: os.system('python shopee_scraper.py') ou API
    else:
        response = "Digite 'ofertas' ou 'celular' pra links Shopee!"
    
    # Envia resposta Telegram (use seu TOKEN .env)
    token = os.getenv('TELEGRAM_TOKEN')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": response})
    
    # Log + trigger vídeo (futuro)
    print(f"Webhook: {msg} -> {response}")
    
    return jsonify({"status": "OK", "response": response})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
