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
    if not os.path.exists(cookie_file_path):
        print(f"Arquivo de cookies não encontrado: {cookie_file_path}")
        return None
        
    jar = MozillaCookieJar(cookie_file_path)
    try:
        jar.load(ignore_discard=True, ignore_expires=True)
        for cookie in jar:
            if cookie.name == 'sessionid' and 'instagram.com' in cookie.domain:
                print(f"SessionID encontrado: {cookie.value[:10]}...")
                return cookie.value
    except Exception as e:
        print(f"Erro ao carregar cookies: {e}")
        return None
    
    print("SessionID não encontrado no arquivo de cookies")
    return None

@instagram_bp.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON não fornecidos'}), 400
            
        url = data.get('url', '').strip()

        if not url or 'instagram.com' not in url:
            return jsonify({'error': 'URL do Instagram inválida ou ausente'}), 400

        # O caminho para o arquivo de cookies
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cookie_file = os.path.join(base_dir, 'cookies.txt')
        
        print(f"Procurando arquivo de cookies em: {cookie_file}")
        
        session_id = get_session_id_from_cookie_file(cookie_file)

        if not session_id or session_id == 'SEU_SESSIONID_AQUI':
            print("Erro: 'sessionid' não encontrado ou não configurado no arquivo cookies.txt.")
            return jsonify({
                'error': 'Cookie de sessão do Instagram não configurado. Verifique o arquivo cookies.txt e configure um sessionid válido.'
            }), 500
        
        print(f"Usando sessionid: {session_id[:15]}...")

        # Usamos um endpoint de dados do Instagram que é muito mais rápido
        if '?' in url:
            json_url = url + '&__a=1&__d=dis'
        else:
            json_url = url + '?__a=1&__d=dis'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        cookies = {
            'sessionid': session_id
        }

        print(f"Fazendo requisição para: {json_url}")
        
        response = requests.get(json_url, headers=headers, cookies=cookies, timeout=10)
        
        print(f"Status da resposta: {response.status_code}")
        
        if response.status_code == 404:
            return jsonify({'error': 'Post não encontrado. Verifique se a URL está correta e se o post não foi deletado.'}), 404
        elif response.status_code == 401:
            return jsonify({'error': 'Não autorizado. O sessionid pode estar expirado ou inválido.'}), 401
        elif response.status_code != 200:
            print(f"Erro do Instagram. Resposta: {response.text[:200]}") # Log da resposta
            return jsonify({'error': f'Instagram retornou erro {response.status_code}'}), response.status_code
            
        try:
            post_json = response.json()
        except ValueError:
            return jsonify({'error': 'Resposta do Instagram não é um JSON válido'}), 500
        
        # A API do Instagram pode ter diferentes formatos de resposta
        media_data = None
        if 'items' in post_json and post_json['items']:
            media_data = post_json['items'][0]
        elif 'graphql' in post_json and post_json['graphql']:
            media_data = post_json['graphql']['shortcode_media']

        if not media_data:
            return jsonify({'error': 'Formato de resposta da API do Instagram não reconhecido.'}), 500

        video_versions = media_data.get('video_versions', [])
        if not video_versions:
            return jsonify({'error': 'Este post não contém vídeo. Pode ser uma foto ou carrossel de imagens.'}), 400
        
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
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Erro de conexão com o Instagram. Verifique sua conexão com a internet.'}), 503
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': f'Erro HTTP: {str(e)}'}), 500
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return jsonify({'error': f'Ocorreu um erro inesperado: {str(e)}'}), 500
