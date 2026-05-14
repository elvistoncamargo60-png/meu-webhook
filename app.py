from flask import Flask, request
import requests
import os
from moviepy.editor import *
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json or {}
    chat_id = data.get('message', {}).get('chat', {}).get('id', os.getenv('CHAT_ID'))
    
    # Scraping Shopee whey
    url = "https://shopee.com.br/search?keyword=whey"
    headers = {'User-Agent': 'Mozilla/5.0'}
    soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
    
    item = soup.find('div', {'data-sqe': '1'})
    img_src = item.find('img')['data-src'] if item else 'https://via.placeholder.com/400x400.jpg'
    
    img_data = requests.get(img_src).content
    with open('/tmp/produto.jpg', 'wb') as f:
        f.write(img_data)
    
    # Video dinâmico 10s
    img_clip = ImageClip('/tmp/produto.jpg').set_duration(10).resize(0.8)
    txt = TextClip("Whey Protein\
R$89,90\
https://shopee.com.br/whey?affiliateId=18345360599", fontsize=40, color='yellow').set_position('bottom').set_duration(10)
    video = CompositeVideoClip([img_clip, txt])
    video.write_videofile('/tmp/video.mp4', fps=24, verbose=False)
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    with open('/tmp/video.mp4', 'rb') as f:
        requests.post("https://api.telegram.org/bot" + token + "/sendVideo",
                      data={'chat_id': str(chat_id), 'caption': 'ID 18345360599'},
                      files={'video': f})
    
    return "Video Shopee whey enviado"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
