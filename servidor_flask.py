from flask import Flask, jsonify
from auth_sendpulse import SendPulseAuth
import requests
from datetime import datetime
import os  # Importar os para pegar variável de ambiente

app = Flask(__name__)  # Cria a aplicação Flask

# Rota raiz simples para testar
@app.route('/')
def home():
    return "Aplicação rodando!"

# Suas rotas SendPulse
auth = SendPulseAuth('645742e1b8885d1997b4096b035ed330', '03eb8ff4e2c73e76f5cfa9ff0a34b12d')

@app.route('/sendpulse-status')
def sendpulse_status():
    try:
        token = auth.get_token()  # Pega token
        headers = {
            "Authorization": f"Bearer {token}"
        }
        url = "https://api.sendpulse.com/smtp/statistics"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 400

@app.route('/token-status')
def token_status():
    last_renewal_timestamp = auth.get_last_renewal()
    if last_renewal_timestamp is None:
        return jsonify({"status": "Token ainda não renovado"})
    last_renewal_datetime = datetime.fromtimestamp(last_renewal_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return jsonify({"last_renewal": last_renewal_datetime})

# Correção para rodar no Heroku usando variável PORT dinâmica
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

