import os
from flask import Flask
from app.models.db import init_db

def create_app():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    app = Flask(
        __name__,
        template_folder=os.path.join(current_dir, "templates"),
        static_folder=os.path.join(current_dir, "static"),
        static_url_path="/static"
    )

    # 設定 Session 密鑰 (請在正式環境使用更複雜的亂碼)
    app.secret_key = "vibe_expense_secret_key"
    
    # 建立資料庫與資料表
    init_db()

    from app.controllers.main_routes import main_bp
    from app.controllers.auth_routes import auth_bp
    from app.controllers.category_routes import category_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(category_bp)

    return app