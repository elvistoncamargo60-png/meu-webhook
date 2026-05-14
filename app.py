from flask import Flask, request
import requests, os
from moviepy.config import change_settings
from moviepy.editor import TextClip

app = Flask(__name__)

# Fix ImageMagick Railway
change_settings({"IMAGEMAGICK_BINARY": None})

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    chat_id = str(update['message']['chat']['id'])
    
    clip = TextClip("Whey Max Titanium\
R$89,90\
shopee.com.br/whey?affiliateId=18345360599", fontsize=50, color='white', bg_color='red').set_duration(10)
    clip.write_videofile('/tmp/whey.mp4', fps=24, verbose=False, logger=None)
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    with open('/tmp/whey.mp4', 'rb') as f:
        requests.post("https://api.telegram.org/bot"+token+"/sendVideo", data={'chat_id': chat_id, 'caption': 'ID 18345360599'}, files={'video': f})
    
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
