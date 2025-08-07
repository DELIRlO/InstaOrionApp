import yt_dlp
import os
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

instagram_bp = Blueprint('instagram', __name__)

@instagram_bp.route('/download', methods=['POST'])
@cross_origin()
def download_video():
    # --- INÍCIO DO CÓDIGO DE TESTE DE DIAGNÓSTICO ---
    # Este código ignora a lógica de download e retorna uma resposta fixa para
    # verificar se o problema é o tempo de execução (timeout).
    return jsonify({
        'success': True,
        'video_url': 'https://example.com/test.mp4',
        'title': 'Vídeo de Teste de Diagnóstico',
        'message': 'SUCESSO NO DIAGNÓSTICO: A API respondeu. O problema é com a demora no download do vídeo (timeout).'
    })
    # --- FIM DO CÓDIGO DE TESTE ---
