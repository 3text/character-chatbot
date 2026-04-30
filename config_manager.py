# config_manager.py

# インポート
import json
import os 
from dotenv import load_dotenv
# 独自モジュールのインポート
import error_manager as err

# ** チートシート ****************
CONFIG_FILE_PATH = "character_config.json"
MODEL_NAME = "models/gemma-4-31b-it"  # 外部ファイルで管理する？要検討
MODEL_ICON = "images/icon.png"

#SUMMARY_MODEL_ID = "xxxxxxxxx" 用意する？検討中

#******************************

load_dotenv()

# 人格データのロード
def load_persona():
	try :
		with open( CONFIG_FILE_PATH ,"r" , encoding = "utf-8") as cfp:
			return json.load(cfp)

	except Exception as e :
		raise err.ApplicationError( "config_manager - load_persona" , str(e))
	
# APIキーの呼び出し
def api_key():
	try :
		my_key = os.getenv("MY_API_KEY")

		if not my_key :
			raise err.ApplicationError("config_manger - api_key" , "APIキーが設定されていません。")

		return my_key

	except Exception as e :
		raise err.ApplicationError("config_manager - api_key" , str(e))

# 秘密鍵の取得
def my_secret_key():
	try :
		secret_key = os.getenv("SECRET_KEY")

		if not secret_key :
			raise err.ApplicationError("config_manger - my_secret_key" , "secretキーが設定されていません。")

		return secret_key

	except Exception as e :
		raise err.ApplicationError("config_manager - my_secret_key" , str(e))


# databaseサーバーのロード
def data_base_uri():
	return os.getenv( "DATABASE_URI" , "sqlite:///chat_history.db")

