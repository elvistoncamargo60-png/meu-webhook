from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip
import logging
import io
import time

app = Flask(__name__)
BOT_TOKEN = "8762957424:AAEb-YUWZPO_oo9aXDiXAH-oXHeVPcRK8OQ"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(level=logging.INFO)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        query = update['message'].get('text', '').strip() or "tênis"
        
        def send_text(msg):
            requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": msg})
        
        send_text("Gerando 5 vídeos Shopee...")
        
        try:
            search_url = f"https://shopee.com.br/search?keyword={requests.utils.quote(query)}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            resp = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Seletor atualizado Shopee 2026 [web:56]
            product_elements = soup.find_all("div", class_="shopee-search-item-result__item")[:5]
            
            for i, element in enumerate(product_elements, 1):
                name_elem = element.find("div", class_="shopee-item-card__text-name")
                name = name_elem.text.strip()[:50] if name_elem else f"Produto {i}"
                img_elem = element.find("img")
                img = img_elem['src'] if img_elem else "https://via.placeholder.com/512x512?text=Shopee"
                link_elem = element.find("a", class_="shopee-item-card--link")
                product_url = "https://shopee.com.br" + link_elem['href'] if link_elem else search_url
                affiliate_link = f"https://shopee.sjv.io/c/18345360599?subId=bot&u={product_url}"
                
                img_resp = requests.get(img)
                img_data = io.BytesIO(img_resp.content)
                
                img_clip = ImageClip(img_data, duration=5).resize((512,512))
                txt_clip = TextClip(name + "
" + affiliate_link, fontsize=30, color='white', bg_color='black')
                txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(5)
                video = CompositeVideoClip([img_clip, txt_clip])
                video_path = f'/tmp/video{i}.mp4'
                video.write_videofile(video_path, fps=24, verbose=False, logger=None)
                
                with open(video_path, 'rb') as vid:
                    requests.post(f"{TELEGRAM_API}/sendVideo",
                                 data={"chat_id": chat_id, "caption": f"{i}/5 {name}\
{affiliate_link}"},
                                 files={"video": vid})
                
                time.sleep(2)
            
            send_text("5 vídeos + links enviados!")
        except Exception as e:
            send_text(f"Erro: {str(e)}")
    
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
