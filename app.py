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
    return "AffiliateFlow AI v22 - Webhook OK!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        message = data.get("message", "").lower()
        chat_id = data.get("chat_id") or data.get("contact", {}).get("external_id")

        if not chat_id:
            return jsonify({"error": "No chat_id"}), 400

        if "oi" in message or "ola" in message or "start" in message:
            response = f"Oi! Digite 'ofertas' para ver produtos Shopee! 🔥🛒 ID: {SHOPEE_AFF_ID}"
        elif "ofertas" in message:
            products = scrape_shopee_offers()
            response = "
".join(products)
        else:
            response = "Digite 'oi' ou 'ofertas' para começar! 🤖"

        send_telegram_message(chat_id, response)
        print(f"Webhook: {message} -> {response}")

        return jsonify({"status": "OK", "response": response})

    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"error": str(e)}), 500

def scrape_shopee_offers():
    url = "https://shopee.com.br/Celulares-Smartphones/cat.134"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        products = []
        for item in soup.find_all("div", class_="shopee-search-item-result__item")[:3]:
            name = item.find("div", class_="item-name")
            price = item.find("span", class_="price")
            link_elem = item.find("a", href=True)
            if name and price and link_elem:
                name_text = name.get_text(strip=True)[:50]
                price_text = price.get_text(strip=True)
                aff_link = f"https://shopee.com.br{link_elem['href']}?af_id={SHOPEE_AFF_ID}"
                products.append(f"🔥 {name_text}
💰 {price_text}
🛒 {aff_link}")
        return products if products else ["Ofertas Shopee carregando... 🔥"]
    except:
        return ["Erro no scraping. Tente novamente! ⚠️"]

def send_telegram_message(chat_id, text):
    if not TELEGRAM_TOKEN:
        print("TELEGRAM_TOKEN não configurado")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
