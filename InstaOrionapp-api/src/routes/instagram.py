import os
import re
import requests
import logging
from flask import Blueprint, request, jsonify

instagram_bp = Blueprint('instagram', __name__)

# --- Implementação aprimorada usando Requests e Variáveis de Ambiente ---

# A variável de ambiente é o método recomendado e mais seguro.
INSTAGRAM_SESSION_ID = os.environ.get("INSTAGRAM_SESSION_ID")

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
}

def get_shortcode_from_url(url: str) -> str | None:
    """Extrai o shortcode de uma URL do Instagram."""
    match = re.search(r"/(reel|reels|p)/([^/]+)", url)
    if match:
        return match.group(2)
    return None

def fetch_video_data(shortcode: str) -> dict:
    """Busca os dados do post e extrai as informações do vídeo."""
    if not INSTAGRAM_SESSION_ID:
        logging.error("Variável de ambiente INSTAGRAM_SESSION_ID não encontrada. Acesso não autenticado.")
        return {"error": "A variável de ambiente INSTAGRAM_SESSION_ID não está configurada no servidor."}

    api_url = f"https://www.instagram.com/p/{shortcode}/?__a=1&__d=dis"
    cookies = {"sessionid": INSTAGRAM_SESSION_ID}

    try:
        response = requests.get(api_url, headers=REQUEST_HEADERS, cookies=cookies, timeout=10)
        response.raise_for_status()
        data = response.json()

        video_url = None
        title = "Video do Instagram"
        
        media = data.get("items", [{}])[0]
        
        if media.get("video_versions"):
            video_url = media["video_versions"][0].get("url")
        elif media.get("carousel_media"):
            for item in media["carousel_media"]:
                if item.get("video_versions"):
                    video_url = item["video_versions"][0].get("url")
                    if video_url: break

        if media.get("caption"):
            title = media["caption"].get("text", title)

        if video_url:
            return {"success": True, "video_url": video_url, "title": title}
        else:
            return {"error": "Não foi possível encontrar a URL do vídeo. O post pode não ser um vídeo ou a estrutura da API mudou."}

    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 404:
            return {"error": "Post não encontrado. Verifique a URL."}
        if http_err.response.status_code in [401, 403]:
            return {"error": "Acesso não autorizado. O 'sessionid' pode ser inválido ou expirado."}
        return {"error": f"Erro HTTP: {http_err.response.status_code}"}
    except requests.exceptions.RequestException as req_err:
        return {"error": f"Erro de conexão com o Instagram: {req_err}"}
    except ValueError:
        return {"error": "Falha ao decodificar a resposta do Instagram."}

@instagram_bp.route('/download', methods=['POST'])
def download_video():
    """Endpoint da API que recebe a URL do frontend via POST."""
    req_data = request.get_json()
    if not req_data or 'url' not in req_data:
        return jsonify({"error": "Parâmetro 'url' não encontrado no corpo da requisição."}), 400

    post_url = req_data['url']
    if not post_url or not isinstance(post_url, str):
        return jsonify({"error": "URL inválida."}), 400

    shortcode = get_shortcode_from_url(post_url)
    if not shortcode:
        return jsonify({"error": "URL do Instagram não parece ser válida."}), 400

    result = fetch_video_data(shortcode)

    if "error" in result:
        return jsonify(result), 500
    
    result['message'] = 'Vídeo encontrado com sucesso!'
    return jsonify(result), 200

# Fim do arquivo
