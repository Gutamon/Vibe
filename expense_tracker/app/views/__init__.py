import os
from flask import Flask

def create_app():
    # 取得 __init__.py 所在的絕對路徑 (也就是 app/views/ 這個資料夾)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    app = Flask(
        __name__,
        # 強制綁定絕對路徑，Flask 就不會找錯地方
        template_folder=os.path.join(current_dir, "templates"),
        static_folder=os.path.join(current_dir, "static"),
        static_url_path="/static"  # 確保網址開頭是 /static
    )

    from app.controllers.main_routes import main_bp
    app.register_blueprint(main_bp)

    return app