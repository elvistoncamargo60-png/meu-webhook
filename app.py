from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    return "App funcionando!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Recebido:", data)
    return "OK", 200

@app.route('/token-status')
def token_status():
    # Aqui você pode colocar a lógica para checar o token SendPulse
    return "Token SendPulse ativo e válido!"

if __name__ == '__main__':
    app.run()

