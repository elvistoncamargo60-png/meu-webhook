from flask import Flask, request, jsonify
import os
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

SHOPEE_AFF_ID = "18345360599"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "AffiliateFlow AI v22 OK!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        message = data.get("message", "").lower()
        chat_id = data.get("chat_id")

        if not chat_id:
            return jsonify({"error": "No chat_id"}), 400

        if "oi" in message:
            response = f"Oi! Digite 'ofertas' ID {SHOPEE_AFF_ID}"
        elif "ofertas" in message:
            response = scrape_shopee_simple()
        else:
            response = "Digite 'oi' ou 'ofertas'!"

        send_telegram(chat_id, response)
        return jsonify({"status": "OK"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def scrape_shopee_simple():
    try:
        url = "https://shopee.com.br/search?keyword=celular"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("div", {"data-testid": "shop-search-item"})[:2]
        prods = []
        for item in items:
            name = item.get("aria-label", "Produto Shopee")[:50]
            link = f"https://shopee.com.br{item.find('a')['href']}?af_id={SHOPEE_AFF_ID}" if item.find('a') else "shopee.com.br"
            prods.append(f"🔥 {name}
🛒 {link}")
        return "
".join(prods) if prods else "Ofertas em breve!"
    except:
        return "Scraping OK - ofertas em teste!"

def send_telegram(chat_id, text):
    if TELEGRAM_TOKEN:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
