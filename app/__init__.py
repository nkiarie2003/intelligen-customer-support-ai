from pathlib import Path
from flask import Flask
from flask_login import current_user
from dotenv import load_dotenv

from config import Config
from .extensions import csrf, db, login_manager
from .models import User
from .ai.engine import AIEngine


def create_app(config_object=Config):
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["ARTIFACT_DIR"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "error"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .auth import bp as auth_bp
    from .main import bp as main_bp
    from .complaints import bp as complaints_bp
    from .admin import bp as admin_bp
    from .api import bp as api_bp
    from .system_status import bp as system_status_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(complaints_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(system_status_bp)

    from .commands import create_admin_command, purge_old_closed_command, train_models_command
    app.cli.add_command(create_admin_command)
    app.cli.add_command(train_models_command)
    app.cli.add_command(purge_old_closed_command)

    with app.app_context():
        db.create_all()
        app.extensions["ai_engine"] = AIEngine(app)

    @app.context_processor
    def inject_globals():
        return {"current_user": current_user}

    return app
