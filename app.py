from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

SHOPEE_AFF_ID = "18345360599"

@app.route("/", methods=["GET"])
def home():
    return "AffiliateFlow v22 OK!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data.get("message", "").lower()
    chat_id = data.get("chat_id")
    response = "Oi! Ofertas Shopee ID " + SHOPEE_AFF_ID if "oi" in message else "Link: https://shopee.com.br?af_id=" + SHOPEE_AFF_ID
    if chat_id and os.environ.get("TELEGRAM_TOKEN"):
        requests.post("https://api.telegram.org/bot" + os.environ["TELEGRAM_TOKEN"] + "/sendMessage", json={"chat_id": chat_id, "text": response})
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
