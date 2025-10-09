from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Token do Bot Telegram (use seu token do BotFather aqui)
TELEGRAM_TOKEN = '7624548707:AAHoVbbu4H0wxVcf-GjC23v9A0Mua4IKRI8'

@app.route('/')
def home():
    return "Aplicação rodando!"

@app.route('/webhook_telegram', methods=['POST'])
def telegram_webhook():
    data = request.json
    print("Mensagem recebida do Telegram:", data)

    chat_id = data['message']['chat']['id']
    mensagem = data['message']['text']

    resposta = f"Oi, recebi sua mensagem: {mensagem}"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": resposta
    }
    requests.post(url, json=payload)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
