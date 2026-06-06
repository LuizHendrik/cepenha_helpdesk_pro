from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name=None):
    """Factory para criar a aplicação Flask"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Faça login para continuar.'
    
    # Registrar blueprints
    with app.app_context():
        from app.routes import auth_bp, admin_bp, user_bp, api_bp, main_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(user_bp, url_prefix='/user')
        app.register_blueprint(api_bp, url_prefix='/api')
        
        # Criar tabelas
        db.create_all()
    
    # Handlers de erro
    register_error_handlers(app)
    
    # Context processors
    register_context_processors(app)
    
    return app

def register_error_handlers(app):
    """Registrar handlers de erro global"""
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Página não encontrada'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Erro interno do servidor'}, 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Acesso negado'}, 403

def register_context_processors(app):
    """Registrar context processors para templates"""
    
    @app.context_processor
    def inject_user_context():
        from flask_login import current_user
        return {'current_user': current_user}

@login_manager.user_loader
def load_user(user_id):
    from app.models import Usuario
    return Usuario.query.get(int(user_id))
