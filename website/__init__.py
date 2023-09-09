from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from .env import db_secret_key, db_name, db_uri

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = db_secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.init_app(app)

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    create_database(app)

    return app


def create_database(app):
    if not path.exists('website/'+db_name):
        with app.app_context():
            db.create_all()
