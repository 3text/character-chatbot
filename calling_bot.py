# colling_bot.py

# インポート
from flask import Flask , render_template , redirect , url_for , Blueprint , request , flash
import requests


# 独自のモジュールのインポート



# ** 設定 ******************************************************************************************
# コンフィグ用モジュールに分けることも検討

TIMEOUT = 5
TO_INFO = " 🐦‍⬛<　サークルブースに誰か来たようです "

# **************************************************************************************************

callbot_bp = Blueprint('callbot_bp' , __name__)

# グローバル変数
call_flag = False
nfty_url = "call_test_from_karasu" # 後で確認すること


@callbot_bp.route('/' , methods = ["GET" , "POST"])
def main_route():
	method = request.method

	global call_flag
	global nfty_url

	match method :
		case "GET" :
			return render_template("calling_bot/index.html" , call = call_flag)

		case "POST" :
			try :
				call_flag = True
				requests.post( url = f"https://ntfy.sh/{nfty_url}" , data = TO_INFO.encode('utf-8') , timeout = TIMEOUT )

			except Exception as e :
				print(f"Error : {e}")

			return redirect(url_for('callbot_bp.main_route'))


# ** サークル側の専用ページ *************************************************************

# トップページ
@callbot_bp.route('/top_page' , methods = ["GET"])
def top_page():

	return render_template("calling_bot/top_page.html")

# 呼び出しフラグの解除
@callbot_bp.route('/flag_checker' , methods = ["GET" , "POST"])
def flag_checker_page():

	global call_flag

	method = request.method

	match method :
		case "GET" :
			return render_template("calling_bot/flag_checker.html" , flag_button = call_flag )

		case "POST" :
			try :
				if int(request.form.get("flag_button" , 1 )) == 1 : # Trueが優先(value属性で管理し、0/1)
					call_flag = True
				else :
					call_flag = False

			except Exception as e :
				print(f"Error : {e}")

			return redirect(url_for('callbot_bp.flag_checker_page'))

# 設定
@callbot_bp.route('/config' , methods = ["GET" , "POST"])
def config_page():

	global nfty_url

	method = request.method

	match method :
		case "GET" :

			# ** 現在の要素 ********** (あれば追加していく)
			# 1. URL
			#
			# ***********************

			return render_template("calling_bot/circle_config.html" , url = nfty_url)


		case "POST" :
			try :
				nfty_url_cache = nfty_url
				nfty_url = request.form.get("user_url" , "" ).strip()

				if nfty_url == "" :
					nfty_url = nfty_url_cache
					flash("Error : URLが空白です。")

			except Exception as e :
				print(f"Error : {e}")

			return redirect(url_for('callbot_bp.config_page'))


# 今は自分専用に作っているが、他にも使いたい人が居るのであれば、サークル名も登録できるようにして、セッションで管理を行う
# 確認を行い、1人であればこのままでもよい