import os
from flask import Flask, request
import telebot

# Ler token do bot do Telegram da variável de ambiente
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Criar instância do bot usando o token seguro
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# Definir uma rota para receber atualizações (webhook)
@app.route('/webhook', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

# Exemplo de comando /start no bot
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Olá! Bot funcionando com token seguro.")

# Rota para testar se o servidor está funcionando
@app.route('/')
def index():
    return "Servidor Flask rodando para bot Telegram."

# Executar o app Flask
if __name__ == "__main__":
    # Definir porta para Heroku ou localhost
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
