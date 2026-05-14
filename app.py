from flask import Flask, request
import requests
import os
from moviepy.editor import TextClip

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "AffiliateFlow AI v24 BotLinkShopee2 OK"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    chat_id = str(update['message']['chat']['id'])
    
    # Vídeo whey texto (sem img SSL erro)
    texto = "Whey Max Titanium 900g" + "\
R$89,90" + "\
https://shopee.com.br/whey-max-titanium-900g?affiliateId=18345360599"
    clip = TextClip(texto, fontsize=50, color='white', bg_color='red').set_duration(10)
    clip.write_videofile('/tmp/whey.mp4', fps=24, verbose=False)
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    with open('/tmp/whey.mp4', 'rb') as video:
        requests.post("https://api.telegram.org/bot" + token + "/sendVideo",
                      data={'chat_id': chat_id, 'caption': '🚀 ID 18345360599'},
                      files={'video': video})
    
    return "Vídeo whey enviado OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
