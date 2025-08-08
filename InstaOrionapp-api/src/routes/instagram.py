import re
import os
import instaloader
from flask import Blueprint, request, jsonify

instagram_bp = Blueprint('instagram', __name__)

# --- Início da Correção ---

# Inicializa o Instaloader
L = instaloader.Instaloader(
    download_videos=True,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False,
)

# Caminho para o arquivo de cookies
# Este arquivo deve estar no mesmo diretório que este script para o Render encontrar
# O arquivo `cookies.txt` deve conter as informações de sessão da sua conta do Instagram
COOKIE_FILE = os.path.join(os.path.dirname(__file__), "cookies.txt")
# Usaremos uma conta de usuário dummy para o instaloader
DUMMY_USERNAME = "orionapp"

try:
    print("Tentando carregar a sessão do arquivo de cookies...")
    L.load_session_from_file(DUMMY_USERNAME, COOKIE_FILE)
    print("Sessão carregada com sucesso a partir do arquivo de cookies.")
except FileNotFoundError:
    print("AVISO: Arquivo de cookies não encontrado. O download pode falhar para posts privados ou com restrições.")
except Exception as e:
    print(f"AVISO: Ocorreu um erro ao carregar a sessão: {e}. O download pode falhar.")

# --- Fim da Correção ---

def extract_shortcode(url):
    """Extrai o shortcode de uma URL do Instagram."""
    match = re.search(r"/(reel|p)/([^/]+)", url)
    if match:
        return match.group(2)
    return None

@instagram_bp.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON não fornecidos'}), 400

        url = data.get('url', '').strip()
        shortcode = extract_shortcode(url)

        if not shortcode:
            return jsonify({'error': 'URL do Instagram inválida ou não contém um post válido'}), 400

        print(f"Iniciando download com Instaloader para o shortcode: {shortcode}")

        try:
            # Obtém o post usando o shortcode
            post = instaloader.Post.from_shortcode(L.context, shortcode)

            if not post.is_video:
                return jsonify({'error': 'Este post não contém um vídeo.'}), 400

            video_url = post.video_url
            title = post.caption if post.caption else "Vídeo do Instagram"
            
            # Limita o tamanho do título para evitar textos muito longos
            if title and len(title) > 150:
                title = title[:150] + "..."

            if not video_url:
                 return jsonify({'error': 'Não foi possível extrair a URL do vídeo.'}), 404

            print(f"Vídeo encontrado: {video_url[:50]}...")

            return jsonify({
                'success': True,
                'video_url': video_url,
                'title': title,
                'message': 'Vídeo encontrado com sucesso!'
            })

        except instaloader.exceptions.PrivateProfileNotFollowedException:
            return jsonify({'error': 'Este post pertence a um perfil privado que você não segue.'}), 403
        except instaloader.exceptions.ProfileNotExistsException:
            return jsonify({'error': 'O perfil associado a este post não existe.'}), 404
        except instaloader.exceptions.LoginRequiredException:
             return jsonify({'error': 'Este post requer login para ser acessado. Verifique se a sessão de login é válida.'}), 401
        except instaloader.exceptions.PostChangedException:
            return jsonify({'error': 'O post foi alterado ou removido.'}), 404
        except instaloader.exceptions.NotFoundException:
            return jsonify({'error': 'Post não encontrado. Verifique se a URL está correta e se o post não foi deletado.'}), 404
        except Exception as e:
            # Captura outras exceções do instaloader que podem não ser específicas
            print(f"Um erro do Instaloader ocorreu: {str(e)}")
            return jsonify({'error': 'O serviço intermediário falhou.'}), 500


    except Exception as e:
        print(f"Erro inesperado no servidor: {str(e)}")
        return jsonify({'error': f'Ocorreu um erro inesperado no servidor: {str(e)}'}), 500
