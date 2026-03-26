from flask import Flask
from flask_pymongo import PyMongo
from config import Config

mongo = PyMongo()

def create_app():
    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="views/static",
    )
    app.config.from_object(Config)
    app.config["MONGO_URI"] = Config.MONGO_URI

    mongo.init_app(app)

    from app.controllers.main_routes import main_bp
    app.register_blueprint(main_bp)

    return app
