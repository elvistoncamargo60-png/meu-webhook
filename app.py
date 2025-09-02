from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    html_content = """
    <html>
        <head><title>App Flask</title></head>
        <body>
            <h1>App funcionando!</h1>
            <p>Bem vindo à aplicação Flask rodando no Heroku.</p>
        </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Recebido:", data)
    return "OK", 200

@app.route('/token-status')
def token_status():
    return "Token SendPulse ativo e válido!"
