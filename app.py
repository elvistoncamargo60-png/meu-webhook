from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import logging
import os

app = Flask(__name__)
BOT_TOKEN = "8762957424:AAEb-YUWZPO_oo9aXDiXAH-oXHeVPcRK8OQ"

def send_text(chat_id, msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": msg})

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        query = update['message'].get('text', 'shopee')
        send_text(chat_id, f"Processando '{query}' Shopee...")
        # Shopee scraping aqui
        send_text(chat_id, "5 produtos + links afiliados!")
    return jsonify({"ok": True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
