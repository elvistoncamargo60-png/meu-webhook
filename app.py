import os
import re
import json
import logging
from threading import Thread
from urllib.parse import quote, urljoin

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
    r = requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=20)
    logging.info("sendMessage status=%s body=%s", r.status_code, r.text)
    return r


def send_telegram_video(chat_id, video_path, caption=""):
    if not TELEGRAM_BOT_TOKEN or not chat_id or not video_path:
        return None
    with open(video_path, "rb") as f:
        files = {"video": f}
        data = {
            "chat_id": chat_id,
            "caption": caption[:1024],
            "supports_streaming": True,
            "parse_mode": "HTML",
        }
        r = requests.post(f"{TELEGRAM_API}/sendVideo", data=data, files=files, timeout=120)
        logging.info("sendVideo status=%s body=%s", r.status_code, r.text)
        return r


def download_file(url, dest_path):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }
    r = requests.get(url, headers=headers, timeout=30, stream=True)
    r.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return dest_path


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
    price = "Preço não encontrado"
    product_url = ""
    image_url = ""

    for p in [r'"name"s*:s*"([^"]+)"', r'"title"s*:s*"([^"]+)"']:
        m = re.search(p, html)
        if m:
            title = m.group(1)
            break

    m_price = re.search(r'"price"s*:s*"?(d+(?:.d+)?)"?', html)
    if m_price:
        price = m_price.group(1)

    m_url = re.search(r'"product"[^}]*"url"s*:s*"([^"]+)"', html)
    if m_url:
        product_url = m_url.group(1).replace("\\/", "/")

    if not product_url:
        m_url2 = re.search(r'"url"s*:s*"([^"]+/product[^"]+)"', html)
        if m_url2:
            product_url = m_url2.group(1).replace("\\/", "/")

    m_image = re.search(r'"image"s*:s*"([^"]+)"', html)
    if m_image:
        image_url = m_image.group(1).replace("\\/", "/")

    if image_url.startswith("//"):
        image_url = "https:" + image_url

    if product_url.startswith("/"):
        product_url = urljoin("https://shopee.com.br", product_url)

    affiliate_link = build_affiliate_link(product_url)

    return {
        "title": title,
        "price": price,
        "product_url": product_url,
        "image_url": image_url,
        "affiliate_link": affiliate_link,
        "search_url": url,
    }


def handle_message(chat_id, text):
    try:
        logging.info("chat_id=%s text=%s", chat_id, text)
        send_telegram_message(chat_id, "Recebi sua mensagem no Railway. Processando...")

        query = clean_text(text)
        if query.lower() in ["oi", "olá", "ola", "start", "/start"]:
            query = "whey protein"

        product = fetch_shopee_product(query)
        logging.info("produto=%s", json.dumps(product, ensure_ascii=False))

        if not product["image_url"] or not product["affiliate_link"]:
            msg = f"""Não consegui montar vídeo agora.

<b>Título:</b> {product['title']}
<b>Preço:</b> {product['price']}
<b>Link:</b> {product['affiliate_link'] or 'não encontrado'}"""
            send_telegram_message(chat_id, msg)
            return

        image_path = "/tmp/shopee_image.jpg"
        video_path = "/tmp/shopee_video.mp4"

        download_file(product["image_url"], image_path)

        from moviepy.editor import ImageClip, TextClip, CompositeVideoClip

        txt = f"""Produto: {product['title']}
Preço: {product['price']}
{product['affiliate_link']}"""

        img = ImageClip(image_path).set_duration(8).resize(width=720)
        text = TextClip(
            txt,
            fontsize=34,
            color="white",
            bg_color="black",
            method="label",
            size=(680, None),
        ).set_position(("center", "bottom")).set_duration(8)

        video = CompositeVideoClip([img.set_position("center"), text])
        video.write_videofile(video_path, fps=24, codec="libx264", audio=False, verbose=False, logger=None)

        legenda = f"""ID {AFFILIATE_ID}
{product['title']}
{product['affiliate_link']}"""

        send_telegram_video(chat_id, video_path, legenda)

    except Exception as e:
        logging.exception("Erro no processamento")
        send_telegram_message(chat_id, f"Erro ao processar a solicitação: {e}")


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    logging.info("update=%s", json.dumps(data, ensure_ascii=False))
    message = data.get("message") or data.get("edited_message") or {}
    chat = message.get("chat") or {}
    text = message.get("text") or ""
    chat_id = chat.get("id") or CHAT_ID

    if not chat_id:
        return jsonify({"ok": False, "error": "chat_id ausente"}), 200

    Thread(target=handle_message, args=(chat_id, text), daemon=True).start()
    return jsonify({"ok": True, "status": "received"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
