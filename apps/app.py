from pathlib import Path
from flask import Flask
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

csrf = CSRFProtect()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        # SQLiteの設定を追加
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{Path(__file__).parent.parent / 'local.sqlite'}",
        SQLALCHEMY_TRACK_MODIFICATIONS =False,
        SECRET_KEY = "ABCDEFG"
    )
    csrf.init_app(app)
    db.init_app(app)
    Migrate(app,db)
    from apps.sampleSite import views
    app.register_blueprint(views.sampleSite,url_prefix="/")

    return app