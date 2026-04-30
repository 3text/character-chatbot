# app.py

# インポート
from flask import Flask

# 独自のモジュールのインポート
import database_manager as dbm
import config_manager as cfg

# ブループリントのインポート
from main import chat_bp
from calling_bot import callbot_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = cfg.data_base_uri()

app.secret_key = cfg.my_secret_key()


app.register_blueprint(chat_bp)
app.register_blueprint(callbot_bp , url_prefix='/calling')

dbm.db.init_app(app)

with app.app_context():
	dbm.db.create_all()

if __name__ == "__main__":
	app.run(debug = True , port=9680)