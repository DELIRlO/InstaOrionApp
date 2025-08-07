import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.instagram import instagram_bp

# Configuração para Vercel - detectar se está rodando no Vercel
IS_VERCEL = os.environ.get('VERCEL') == '1'

if IS_VERCEL:
    # No Vercel, os arquivos estáticos são servidos diretamente
    app = Flask(__name__)
else:
    # Localmente, servir arquivos estáticos do diretório dist
    static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'dist')
    app = Flask(__name__, static_folder=static_folder)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Habilitar CORS para todas as rotas
CORS(app, origins=['*'])

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(instagram_bp, url_prefix='/api/instagram')

# Configuração do banco de dados
if IS_VERCEL:
    # No Vercel, usar um banco temporário ou configurar um banco externo
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    # Localmente, usar arquivo de banco
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# Rota de health check
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok', 'message': 'API funcionando corretamente'})

# Servir arquivos estáticos apenas localmente
if not IS_VERCEL:
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404

# Função para Vercel
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
