from flask import Flask
import requests, os
from moviepy.editor import TextClip
from telegram import Bot

app = Flask(__name__)
bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))

@app.route('/shopee_whey')
def shopee_whey():
    name = "Whey Max Titanium 900g"
    price = "R$89,90"
    link = "https://shopee.com.br/whey-max-titanium-900g?affiliateId=18345360599"
    
    clip = TextClip(f"{name}
{price}
Clique: {link}", fontsize=60, color='white', bg_color='red').set_duration(10)
    clip.write_videofile('/tmp/whey.mp4', fps=24, verbose=False)
    
    with open('/tmp/whey.mp4', 'rb') as video:
        bot.send_video(chat_id=os.getenv('CHAT_ID'), video=video, caption='🚀 Whey ID 18345360599')
    
    return "Vídeo whey PRODUÇÃO enviado BotLinkShopee2!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
