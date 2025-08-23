from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Recebido:", data)
    return "OK", 200

if _name_ == '__main__':
    app.run()
