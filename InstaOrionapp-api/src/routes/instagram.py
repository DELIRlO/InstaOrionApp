import yt_dlp
import os
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

instagram_bp = Blueprint('instagram', __name__)

@instagram_bp.route('/download', methods=['POST'])
@cross_origin()
def download_video():
    data = request.get_json()
    url = data.get('url', '').strip()

    if not url or 'instagram.com' not in url:
        return jsonify({'error': 'URL do Instagram inválida ou ausente'}), 400
    
    # Obter o caminho para o diretório de src
    # Constrói o caminho para o arquivo de cookies na pasta 'src'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cookie_file = os.path.join(base_dir, 'cookies.txt')

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'extract_flat': True,
    }

    if os.path.exists(cookie_file):
        ydl_opts['cookiefile'] = cookie_file


    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info:
                video_info = info['entries'][0]
            else:
                video_info = info

            video_url = video_info.get('url')
            title = video_info.get('title', 'Vídeo do Instagram')

            if not video_url:
                 return jsonify({'error': 'Não foi possível obter a URL do vídeo.'}), 400

            return jsonify({
                'success': True,
                'video_url': video_url,
                'title': title,
                'message': 'Vídeo encontrado! Clique no link para baixar.'
            })

    except yt_dlp.utils.DownloadError as e:
        return jsonify({'error': 'Não foi possível processar o vídeo. Verifique se a URL está correta e se o post é público.'}), 400
    except Exception as e:
        return jsonify({'error': f'Ocorreu um erro inesperado: {str(e)}'}), 500
