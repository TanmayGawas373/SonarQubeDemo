from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from config.config import DevelopmentConfig, TestingConfig, ProductionConfig
from config.db import db
from utils.error_handler import register_error_handlers
from middleware.auth_middleware import jwt_middleware
from controller.register_blueprints import register_blueprints
from controller.v2.register_blueprints_v2 import register_v2_blueprints
import os

def create_app(config_class=None):
    if config_class is None:
        env = os.getenv('FLASK_ENV', 'development')
        config_map = {
            'development': DevelopmentConfig,
            'testing': TestingConfig,
            'production': ProductionConfig,
        }
        config_class = config_map.get(env, DevelopmentConfig)

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    Migrate(app, db)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from dao.user_dao import get_user_by_id
        return get_user_by_id(user_id)

    @login_manager.request_loader
    def load_user_from_request(request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
            try:
                from utils.jwt_util import decode_token
                from dao.user_dao import get_user_by_id
                payload = decode_token(token)
                user_id = payload.get('sub')
                if user_id:
                    return get_user_by_id(user_id)
            except Exception:
                return None
        return None

    # Register JWT middleware before blueprints so it runs for all requests
    jwt_middleware(app)

    # Register blueprints (registers all root and UI/admin blueprints)
    register_blueprints(app)

    # Register v2 API blueprints (JSON only)
    register_v2_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    @app.route("/health")
    def health():
        return {"status": "Hello Jenkins!!"}, 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
