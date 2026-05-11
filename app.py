from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip
import os
import uuid
from threading import Thread
import urllib.parse

app = Flask(__name__)

# Variáveis do ambiente (você vai colocar no Railway)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'SEU_TOKEN_BOTFATHER_AQUI')
CHAT_ID = os.environ.get('CHAT_ID', '@seu_canal_ou_chat_id')
AFFILIATE_ID = "18345360599"
SHOPEE_BASE = "https://shopee.com.br"


def process_scraping(query="whey protein"):
    """
    Função assíncrona: scrape Shopee → gera vídeo MoviePy → envia pro Telegram.
    """
    try:
        # 1. Scraping Shopee básico
        url = f"{SHOPEE_BASE}/search?keyword={urllib.parse.quote(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 2. Pega o link do produto
        prod_link_tag = soup.find('a', {'data-sqe': True})
        prod_link = SHOPEE_BASE + prod_link_tag.get('href') if prod_link_tag else None

        if not prod_link:
            send_telegram("Produto não encontrado no Shopee com essa busca.")
            return

        # 3. Monta o link afiliado
        aff_link = f"{prod_link}?affiliateId={AFFILIATE_ID}"

        # 4. Baixa imagem do produto
        img_tag = soup.find('img', {'data-src': True})
        img_url = img_tag.get('data-src') if img_tag else None
        img_path = f"/tmp/{uuid.uuid4()}.jpg"

        if img_url:
            img_resp = requests.get(img_url)
            with open(img_path, "wb") as f:
                f.write(img_resp.content)
        else:
            send_telegram(f"Oferta Shopee: {aff_link}")
            return

        # 5. Gera vídeo com MoviePy (10 segundos)
        video_path = f"/tmp/{uuid.uuid4()}.mp4"

        # 5.1 Clip de imagem
        img_clip = ImageClip(img_path, duration=10)

        # 5.2 Clip de texto (overlay com o link)
        txt_clip = TextClip(
            f"Compre agora!\
{aff_link}",
            fontsize=40,
            color="white",
            bg_color="black",
        ).set_position(("center", "bottom")).set_duration(10)

        # 5.3 Composita imagem + texto
        final_clip = CompositeVideoClip([img_clip, txt_clip])

        # 5.4 Gera vídeo
        final_clip.write_videofile(
            video_path, fps=24, verbose=False, logger=None
        )

        # 6. Envia o vídeo pro Telegram
        with open(video_path, "rb") as video_file:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo",
                data={
                    "chat_id": CHAT_ID,
                    "caption": f"Oferta top! ID {AFFILIATE_ID}\
{aff_link}",
                },
                files={"video": video_file},
            )

        # 7. Limpeza de arquivos temporários
        os.remove(img_path)
        os.remove(video_path)

        # 8. Envio de mensagem final
        send_telegram("Vídeo enviado com sucesso! Confira no seu canal.")
    except Exception as e:
        send_telegram(f"Erro durante o processo: {str(e)}")


def send_telegram(msg):
    """
    Envio simples de mensagem de texto no Telegram.
    """
    data = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown",
    }
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        data=data,
    )


@app.route("/")
def home():
    """
    Página inicial de teste.
    """
    return "AffiliateFlow AI v24 – 100% Funcionando!"


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Webhook chamado pelo SendPulse.
    - Retorna resposta rápida para evitar timeout.
    - Processa scraping/vídeo em background.
    """
    data = request.json or {}
    query = data.get("query", "oi").strip().lower()

    # 1. Inicia tarefa em segundo plano (Thread)
    Thread(target=process_scraping, args=(query,), daemon=True).start()

    # 2. Responde de imediato pra evitar timeout do SendPulse
    return jsonify(
        {
            "response": (
                "Oi! Iniciando scraping do Shopee + geração de vídeo. "
                "O vídeo será enviado ao seu canal em alguns segundos!"
            )
        }
    ), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
