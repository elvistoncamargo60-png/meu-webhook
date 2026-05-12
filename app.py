import os
import re
import logging
from threading import Thread
from urllib.parse import quote

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("CHAT_ID", "").strip()
AFFILIATE_ID = os.getenv("AFFILIATE_ID", "18345360599").strip()

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
SHOPEE_SEARCH_URL = "https://shopee.com.br/search?keyword={query}"


@app.route("/", methods=["GET"])
def home():
    return "AffiliateFlow AI OK", 200


def clean_text(value):
    return re.sub(r"s+", " ", str(value or "")).strip()


def build_affiliate_link(url):
    if not url:
        return ""
    if "affiliateId=" in url:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}affiliateId={AFFILIATE_ID}"


def send_telegram_message(chat_id, text):
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        return None
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    return requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=20)


def send_telegram_video(chat_id, video_url, caption=""):
    if not TELEGRAM_BOT_TOKEN or not chat_id or not video_url:
        return None
    payload = {
        "chat_id": chat_id,
        "video": video_url,
        "caption": caption[:1024],
        "supports_streaming": True,
    }
    return requests.post(f"{TELEGRAM_API}/sendVideo", json=payload, timeout=30)


def fetch_shopee_product(query):
    q = quote(clean_text(query))
    url = SHOPEE_SEARCH_URL.format(query=q)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    html = r.text

    title = "Produto Shopee"
    product_url = ""
    image_url = ""

    m_title = re.search(r'"name"s*:s*"([^"]+)"', html)
    if m_title:
        title = m_title.group(1)

    m_url = re.search(r'"product"[^}]*"url"s*:s*"([^"]+)"', html)
    if m_url:
        product_url = m_url.group(1).replace("\\/", "/")

    m_image = re.search(r'"image"s*:s*"([^"]+)"', html)
    if m_image:
        image_url = m_image.group(1).replace("\\/", "/")

    if product_url and product_url.startswith("/"):
        product_url = "https://shopee.com.br" + product_url

    affiliate_link = build_affiliate_link(product_url)

    return {
        "title": title,
        "product_url": product_url,
        "image_url": image_url,
        "affiliate_link": affiliate_link,
    }


def process_user_message(chat_id, text):
    try:
        send_telegram_message(chat_id, "Oi! Iniciando scraping Shopee via IA. Aguarde...")

        query = clean_text(text)
        if query.lower() in ["oi", "olá", "ola", "start", "/start"]:
            query = "whey protein"

        product = fetch_shopee_product(query)

        resposta = f"""Produto Shopee via IA encontrado!

<b>Título:</b> {product['title']}

<b>Link afiliado:</b> {product['affiliate_link']}

Acesse, veja o vídeo e compre direto no link abaixo.

Se quiser, você pode me mandar outro nome de produto."""

        send_telegram_message(chat_id, resposta)

        if product["image_url"]:
            caption = f"ID {AFFILIATE_ID}
{product['title']}
{product['affiliate_link']}"
            send_telegram_video(chat_id, product["image_url"], caption)

    except Exception as e:
        logging.exception("Erro no processamento")
        send_telegram_message(chat_id, f"Erro ao processar a solicitação: {e}")


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    logging.info("Update recebido: %s", data)

    message = data.get("message") or data.get("edited_message") or {}
    chat = message.get("chat") or {}
    text = message.get("text") or ""

    chat_id = chat.get("id") or CHAT_ID

    if not chat_id:
        return jsonify({"ok": False, "error": "chat_id ausente"}), 200

    Thread(target=process_user_message, args=(chat_id, text), daemon=True).start()
    return jsonify({"ok": True, "status": "received"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
