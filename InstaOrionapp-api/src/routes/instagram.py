import requests
from flask import Blueprint, request, jsonify

instagram_bp = Blueprint('instagram', __name__)

@instagram_bp.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON não fornecidos'}), 400

        url = data.get('url', '').strip()

        if not url or 'instagram.com' not in url:
            return jsonify({'error': 'URL do Instagram inválida ou ausente'}), 400

        # API de terceiros que usaremos como proxy
        target_api_url = "https://sssinstagram.com/api/convert"

        payload = {"url": url}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            "Content-Type": "application/json",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }

        print(f"Fazendo requisição proxy para: {target_api_url}")

        response = requests.post(target_api_url, headers=headers, json=payload, timeout=20)
        
        print(f"Status da resposta da API de terceiros: {response.status_code}")

        if response.status_code != 200:
            print(f"Erro da API de terceiros: {response.text[:200]}")
            return jsonify({'error': 'O serviço intermediário falhou.'}), response.status_code

        api_response = response.json()

        # Verifica se a resposta contém o que esperamos
        if not api_response.get('success') or not api_response.get('result'):
            print(f"Resposta inesperada da API de terceiros: {api_response}")
            return jsonify({'error': 'Post não encontrado ou formato de resposta inesperado.'}), 404
        
        result = api_response.get('result')
        
        # Extrair a primeira URL de vídeo encontrada
        video_url = None
        if result.get('video_versions'):
            video_url = result['video_versions'][0]['url']
        elif result.get('image_versions2'): # Fallback para imagens/reels
             if result.get('video_versions'):
                video_url = result['video_versions'][0]['url']

        if 'clips_media' in result:
             if result['clips_media'][0].get('video_versions'):
                video_url= result['clips_media'][0]['video_versions'][0]['url']
        
        if result.get('url'):
            video_url = result.get('url')

        if not video_url:
            return jsonify({'error': 'Não foi possível encontrar um vídeo para baixar.'}), 404

        title = "Video do Instagram"
        if result.get('title'):
            title = result.get('title')
        elif result.get('caption') and result['caption'].get('text'):
             title = result['caption']['text']


        return jsonify({
            'success': True,
            'video_url': video_url,
            'title': title,
            'message': 'Vídeo encontrado com sucesso!'
        })

    except requests.exceptions.Timeout:
        return jsonify({'error': 'A requisição ao serviço intermediário demorou demais (timeout).'}), 504
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return jsonify({'error': f'Ocorreu um erro inesperado: {str(e)}'}), 500
