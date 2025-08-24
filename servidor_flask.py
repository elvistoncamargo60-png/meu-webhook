from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Recebido:", data)
    return 'Webhook recebido', 200

@app.route('/')
def index():
    return 'Servidor funcionando', 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)