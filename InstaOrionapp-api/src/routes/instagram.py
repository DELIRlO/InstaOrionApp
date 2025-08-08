import re
import os
import requests
from flask import Blueprint, request, jsonify

instagram_bp = Blueprint('instagram', __name__)

COOKIE_FILE = os.path.join(os.path.dirname(__file__), "cookies.txt")

def get_session_id():
    """Lê o sessionid do arquivo de cookies."""
    try:
        with open(COOKIE_FILE, 'r') as f:
            for line in f:
                if 'sessionid' in line:
                    parts = line.strip().split('\t')
                    return parts[-1]
    except FileNotFoundError:
        print("AVISO: Arquivo de cookies não encontrado.")
        return None
    except Exception as e:
        print(f"AVISO: Erro ao ler o arquivo de cookies: {e}")
        return None

def extract_shortcode(url):
    """Extrai o shortcode de uma URL do Instagram."""
    match = re.search(r"/(reel|p)/([^/]+)", url)
    if match:
        return match.group(2)
    return None

@instagram_bp.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Dados JSON inválidos ou URL não fornecida'}), 400

    url = data['url'].strip()
    shortcode = extract_shortcode(url)

    if not shortcode:
        return jsonify({'error': 'URL do Instagram inválida ou não contém um post válido'}), 400

    session_id = get_session_id()
    if not session_id:
        return jsonify({'error': 'Falha na autenticação: sessionid não encontrado.'}), 500

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    cookies = {'sessionid': session_id}
    
    insta_url = f"https://www.instagram.com/p/{shortcode}/?__a=1&__d=dis"

    try:
        response = requests.get(insta_url, headers=headers, cookies=cookies)
        response.raise_for_status()
        json_data = response.json()
        
        video_url = None
        title = "Vídeo do Instagram"

        # Acessa a estrutura de dados correta
        media = json_data.get('data', {}).get('xdt_shortcode_media', {})
        
        if media and media.get('is_video') and media.get('video_versions'):
            video_url = media['video_versions'][0]['url']
            caption_edges = media.get('edge_media_to_caption', {}).get('edges', [])
            if caption_edges and 'node' in caption_edges[0]:
                title = caption_edges[0]['node'].get('text', title)
        else:
            return jsonify({'error': 'Este post não contém um vídeo ou os dados são inválidos.'}), 400

        if not video_url:
            return jsonify({'error': 'Não foi possível encontrar a URL do vídeo na resposta da API.'}), 404

        if len(title) > 150:
            title = title[:150] + "..."

        return jsonify({
            'success': True,
            'video_url': video_url,
            'title': title,
            'message': 'Vídeo encontrado com sucesso!'
        })

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return jsonify({'error': 'Post não encontrado. Verifique a URL.'}), 404
        elif e.response.status_code == 401 or e.response.status_code == 403:
             return jsonify({'error': 'Acesso negado. O cookie de sessão pode ser inválido ou expirado.'}), 403
        else:
            return jsonify({'error': f'Erro de comunicação com o Instagram: {e.response.status_code}'}), 500
    except Exception as e:
        return jsonify({'error': f'Ocorreu um erro inesperado no servidor: {str(e)}'}), 500
