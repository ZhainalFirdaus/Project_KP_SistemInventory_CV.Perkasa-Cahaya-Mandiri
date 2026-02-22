import os
from flask import Flask
from dotenv import load_dotenv
from .extensions import db, login_manager, csrf, migrate

load_dotenv() # Load variables from .env

def create_app():
    app = Flask(__name__, 
                static_folder='../static', 
                template_folder='../templates')
    
    # Configuration from .env
    db_url = os.getenv('DATABASE_URL')
    
    # DEBUG: Print all environment variable names to help identify the correct DB URL one
    print(f"DEBUG: Available env vars: {list(os.environ.keys())}")
    
    if not db_url:
        print("CRITICAL ERROR: DATABASE_URL not found in environment variables!")
        # Fallback to a dummy or local sqlite just to prevent crash, 
        # but the app won't work correctly without MySQL.
        db_url = "sqlite:///fallback.db" 

    if db_url and db_url.startswith("mysql://"):
        db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
        
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_fallback_key_for_dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, '../' + os.getenv('UPLOAD_FOLDER', 'static/uploads'))
    
    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Import models to register them with SQLAlchemy
    from . import models
    
    # Register Blueprints
    from .routes.main import main as main_blueprint
    from .routes.auth import auth as auth_blueprint
    from .routes.items import items as items_blueprint
    from .routes.transactions import transactions as transactions_blueprint
    from .routes.reports import reports_blueprint
    from .routes.bulk import bulk
    from .routes.qr import qr_blueprint
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(items_blueprint)
    app.register_blueprint(transactions_blueprint, url_prefix='/transaction')
    app.register_blueprint(reports_blueprint)
    app.register_blueprint(bulk)
    app.register_blueprint(qr_blueprint)
    
    # Custom Jinja Filter: Konversi UTC ke WIB (UTC+7)
    from datetime import timedelta
    @app.template_filter('to_wib')
    def to_wib_filter(dt):
        if dt:
            return dt + timedelta(hours=7)
        return dt
    
    return app

