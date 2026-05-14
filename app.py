from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import logging

app = Flask(__name__)
BOT_TOKEN = "8762957424:AAEb-YUWZPO_oo9aXDiXAH-oXHeVPcRK8OQ"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(level=logging.INFO)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    logging.info(f"update={update}")
    
    if 'message' in update:
        chat_id
