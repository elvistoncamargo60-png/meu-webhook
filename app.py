from flask import Flask, request

app = Flask(_name_)

@app.route('/')
def index():
    return "App funcionando!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Recebido:", data)
    return "OK", 200

if _name_ == '_main_':
    app.run()
