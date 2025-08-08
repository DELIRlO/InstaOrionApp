import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.instagram import instagram_bp

# Configuração da aplicação
app = Flask(__name__)

# Chave secreta
# É altamente recomendável usar variáveis de ambiente para a SECRET_KEY no Render
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_for_dev')

# Habilitar CORS para todas as rotas
CORS(app, origins=['*'])

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(instagram_bp, url_prefix='/api/instagram')

# Configuração do banco de dados
# ATENÇÃO: O SQLite não é ideal para produção no Render.
# O sistema de arquivos é efêmero e os dados podem ser perdidos.
# Considere usar o serviço de PostgreSQL gratuito do Render para uma solução mais robusta.
db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Cria as tabelas do banco de dados se não existirem
with app.app_context():
    db.create_all()

# Rota de health check para o Render usar
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok'})

# O Gunicorn vai procurar a variável 'app' neste arquivo para iniciar o servidor.
