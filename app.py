import os
from flask import Flask, request
import requests
import json
from bs4 import BeautifulSoup
import random

app = Flask(__name__)

# Seu token do bot do Telegram (vem das variáveis do Railway)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SEU_TOKEN_AQUI")
API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Seu link de afiliado (exemplo: base do Shopee com seu ID)
# Exemplo falso: "https://shopee.com.br/affiliatelink/12345"
# Você troca isso pelo seu link real
AFILIADO_BASE = "https://shopee.com.br/SEU_LINK_AQUI/"

# --- FUNÇÃO QUE FAZ O SCRAPING DA SHOPEE (SIMPLIFICADO) ---
def scrape_shopee(item_nome):
    # NOME DA LOJA OU PALAVRA-CHAVE QUE VOCÊ QUER USAR
    keyword = item_nome.strip()

    # URL de busca na Shopee (paginação básica, só o 1o resultado)
    url = f"https://shopee.com.br/search?keyword={keyword}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None, None

        soup = BeautifulSoup(resp.text, "html.parser")

        # BUSCA PELO PRIMEIRO PRODUTO (link e nome)
        produto = soup.find("a", class_="shopee-item-card")
        if not produto:
            return None, None

        # TENTA PEGAR O LINK DO PRODUTO
        link = produto.get("href", "")

        # TENTA PEGAR O NOME
        titulo = produto.find("div", class_="item-title")
        if titulo:
            nome = titulo.text.strip()
        else:
            # PEGAR POR OUTRO CAMPO COMUM
            nome = "Produto Shopee"

        # MONTAR LINK COM SEU AFILIADO
        if link and link.startswith("https://"):
            link_final = AFILIADO_BASE + link.split("shopee.com.br")[-1]
        else:
            link_final = f"{AFILIADO_BASE}?q={keyword}"

        return nome, link_final

    except Exception as e:
        print("Erro scraping Shopee:", e)
        return None, None


# --- ROTA DO WEBHOOK DO TELEGRAM ---
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # PEGAR O JSON QUE O TELEGRAM MANDA
        data = request.json
        if not data or "message" not in data:
            return "ok", 200

        msg = data["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "").strip()

        # AQUI VOCÊ ESCOLHE O QUE FAZER QUANDO MANDA "oi"
        if text.lower() == "oi":
          resposta = "Oi! Iniciando scraping Shopee via IA. Aguarde..." 

            # Chama a sua lógica de scraping e cria o link
            # Exemplo: você pode usar outra palavra depois de "oi"
            # Ex: "oi chinelo" -> chinelo = True
            nome_produto, link = scrape_shopee("Shopee via IA")

            if nome_produto and link:
                resposta = (
                    f"Produto encontrado na Shopee via IA!

"
                    f"**Título:** {nome_produto}

"
                    f"**Link afiliado:** {link}

"
                    "Acesse, veja o vídeo e compre direto no link abaixo.

"
                    "Se quiser, você pode me mandar outro nome de produto."
                )
            else:
                resposta = "Não consegui encontrar o produto agora. Tente novamente mais tarde."

            # MANDA RESPOSTA DIRETO PARA O TELEGRAM (sem SendPulse)
            payload = {
                "chat_id": chat_id,
                "text": resposta,
                "parse_mode": "Markdown"
            }
            r = requests.post(f"{API_URL}/sendMessage", json=payload)

            print("Resposta enviada:", resposta)
            return "ok", 200

        # MANDA UM "ok" para qualquer outra mensagem
        return "ok", 200

    except Exception as e:
        print("Erro no webhook:", e)
        return "ok", 200


# --- ROTA DE TESTE (se quiser ver se o servidor está ligado) ---
@app.route("/")
def index():
    return "Bot Shopee via IA no ar!"


# Roda o servidor (Railway usa isso)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
