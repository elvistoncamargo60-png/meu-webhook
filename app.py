from flask import Flask
import requests, os
from moviepy.editor import TextClip

app = Flask(__name__)

@app.route('/shopee_whey')
def shopee_whey():
    name = "Whey Max Titanium 900g"
    price = "R$89,90"
    link = "https://shopee.com.br/whey-max-titanium-900g?affiliateId=18345360599"
    
    text = name + "\
" + price + "\
" + link
    clip = TextClip(text, fontsize=60, color='white', bg_color='red').set_duration(10)
    clip.write_videofile('/tmp/whey.mp4', fps=24, verbose=False)
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    
    with open('/tmp/whey.mp4', 'rb') as video:
        requests.post(f"https://api.telegram.org/bot{token}/sendVideo",
                     data={'chat_id': chat_id, 'caption': 'Whey ID 18345360599'},
                     files={'video': video})
    
    return "Video whey funcionando BotLinkShopee2"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
