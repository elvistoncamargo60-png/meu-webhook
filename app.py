from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

SHOPEE_AFF_ID = "18345360599"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "AffiliateFlow v22 OK - Links afiliados!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data.get("message", "").lower()
    chat_id = data.get("chat_id")

    if "oi" in message:
        response = "Oi! Digite 'ofertas' pra Shopee ID " + SHOPEE_AFF_ID
    elif "ofertas" in message:
        response = "Oferta1 Celular: https://shopee.com.br/search?keyword=celular&af_id=" + SHOPEE_AFF_ID + "\
Oferta2 Fone: https://shopee.com.br/search?keyword=fone&af_id=" + SHOPEE_AFF_ID
    else:
        response = "Digite 'oi' ou 'ofertas'!"

    if TELEGRAM_TOKEN:
        requests.post("https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage", json={"chat_id": chat_id, "text": response})

    return jsonify({"status": "OK"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
