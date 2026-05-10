from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "MeuWebhook OK!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json or {}
    # Scraping Shopee placeholder - expande depois
    produto = "Smartphone Samsung Galaxy"
    preco = "R$899"
    link = "https://shopee.com.br/produto?aff=18345360599"

    return jsonify({
        "response": f"Produto: {produto}
Preço: {preco}
Link afiliado: {link}"
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
