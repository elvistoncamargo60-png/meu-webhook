from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def receber_webhook():
    data = request.get_json()
    print("--- Dados recebidos do SendPulse ---")
    print(data)
    try:
        evento = data[0]
        bot_id = evento["bot"]["id"]
        mensagem = evento["info"]["message"]["channel_data"]["message"]["text"]
        usuario = evento["contact"]["username"]
        print(f"Bot ID: {bot_id} | Mensagem: {mensagem} | Usuário: {usuario}")
    except Exception as e:
        print("Erro ao extrair dados:", e)

    return jsonify({"status": "OK"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)