import requests
import os

API_KEY = 'YUBwR5CT7E68oMyKpgHiGUz72X7sMCTecBDuVyu75GVLZY2mJeqwFFmi'  # Sua chave API do Pexels
SEARCH_QUERY = 'nature'  # Palavra para buscar vídeos (pode mudar depois)
VIDEOS_PER_PAGE = 3
SAVE_FOLDER = 'videos_pexels'

headers = {
    'Authorization': API_KEY
}

def baixar_videos():
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

    url = f'https://api.pexels.com/videos/search?query={SEARCH_QUERY}&per_page={VIDEOS_PER_PAGE}'

    response = requests.get(url, headers=headers)
    data = response.json()

    for video in data.get('videos', []):
        video_url = video['video_files'][0]['link']
        video_id = video['id']
        filename = os.path.join(SAVE_FOLDER, f'video_{video_id}.mp4')

        print(f'Baixando vídeo {video_id}...')
        r = requests.get(video_url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f'Vídeo {video_id} salvo em {filename}')

if __name__ == '__main__':
    
    baixar_videos()