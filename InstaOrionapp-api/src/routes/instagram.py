import os
import requests
from flask import Blueprint, request, jsonify
from http.cookiejar import MozillaCookieJar

instagram_bp = Blueprint('instagram', __name__)

def get_session_id_from_cookie_file(cookie_file_path):
    """
    Analisa um arquivo de cookies no formato Netscape (como o cookies.txt)
    para encontrar o valor do 'sessionid' do Instagram.
    """
    jar = MozillaCookieJar(cookie_file_path)
    try:
        jar.load(ignore_discard=True, ignore_expires=True)
        for cookie in jar:
            if cookie.name == 'sessionid' and 'instagram.com' in cookie.domain:
                return cookie.value
    except FileNotFoundError:
        return None
    return None

@instagram_bp.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url', '').strip()

    if not url or 'instagram.com' not in url:
        return jsonify({'error': 'URL do Instagram inválida ou ausente'}), 400

    # O caminho para o arquivo de cookies
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cookie_file = os.path.join(base_dir, 'cookies.txt')
    
    session_id = get_session_id_from_cookie_file(cookie_file)

    if not session_id:
         return jsonify({'error': 'Falha ao carregar o cookie de sessão. A autenticação com o Instagram pode ter falhado.'}), 500

    # Usamos um endpoint de dados do Instagram que é muito mais rápido
    if '?' in url:
        json_url = url + '&__a=1&__d=dis'
    else:
        json_url = url + '?__a=1&__d=dis'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    
    cookies = {
        'sessionid': session_id
    }

    try:
        response = requests.get(json_url, headers=headers, cookies=cookies, timeout=8)
        response.raise_for_status()
        post_json = response.json()
        
        # A API do Instagram pode ter diferentes formatos de resposta
        media_data = None
        if 'items' in post_json and post_json['items']:
            media_data = post_json['items'][0]
        elif 'graphql' in post_json:
            media_data = post_json['graphql']['shortcode_media']

        if not media_data:
            return jsonify({'error': 'API do Instagram retornou uma resposta em formato desconhecido.'}), 500

        video_versions = media_data.get('video_versions', [])
        if not video_versions:
            return jsonify({'error': 'Não foram encontradas versões de vídeo neste post. É uma foto?'}), 400
        
        video_url = video_versions[0].get('url')
        caption_node = media_data.get('caption')
        title = caption_node.get('text', 'Vídeo do Instagram') if caption_node else 'Vídeo do Instagram'

        if not video_url:
            return jsonify({'error': 'Não foi possível extrair a URL do vídeo da resposta da API.'}), 404

        return jsonify({
            'success': True,
            'video_url': video_url,
            'title': title,
            'message': 'Vídeo encontrado com sucesso!'
        })

    except requests.exceptions.Timeout:
        return jsonify({'error': 'A requisição ao Instagram demorou demais (timeout).'}), 504
    except requests.exceptions.HTTPError:
        return jsonify({'error': 'O Instagram retornou um erro. O post é privado, foi deletado ou a URL está incorreta?'}), 404
    except Exception as e:
        return jsonify({'error': f'Ocorreu um erro inesperado: {str(e)}'}), 500
