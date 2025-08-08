import os
from flask import Flask, jsonify
from flask_cors import CORS
from src.routes.instagram import instagram_bp

# Configuração da aplicação
app = Flask(__name__)

# Habilitar CORS para todas as rotas
CORS(app, origins=['*'])

# Registrar o blueprint da API do Instagram
app.register_blueprint(instagram_bp, url_prefix='/api/instagram')

# Rota de health check para o Render usar
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok'})

# O Gunicorn vai procurar a variável 'app' neste arquivo para iniciar o servidor.
