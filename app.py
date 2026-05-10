from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "AffiliateFlow Webhook OK - Shopee Real!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data
