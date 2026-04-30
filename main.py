# main.py

# 将来的にこれ以上の機能を追加するならモジュール化を検討

# インポート
import uuid
from flask import Blueprint , render_template , request,redirect,url_for , session , jsonify

# 独自のモジュールのインポート
import chat_manager as chat
import set_prompt as spm
import config_manager as cfg
import error_manager as err
import database_manager as dbm

# db化に伴いコメントアウト
#import memory_manager as mem


# メッセージ用の構造体
message_structure = {
	"role" : "model",
	"name" : "defalt_name",
	"parts" : [{"text" : "これはデバッグ用の文章です。この文字が見えている場合は開発者に連絡をお願いします。"}]
	} 

# ** 閾値*******
THRESHOLD = 20
POST_COUNT = 30 # ひとまずは30件。検討すること。
MAX_INPUT_LENGTH = 200

# **************

USER_NAME = "user" # 今後設定できるような機能を追加するかもしれない

try :
	MODEL_NAME = cfg.load_persona()["persona"].get( "name" , "AI" ) 

except :
	MODEL_NAME = "AI"


NAME_STRUCT = {
	"user_name" : USER_NAME ,
	"model_name" : MODEL_NAME
	}

# 秘密鍵はapp.pyで設定

persona_data = cfg.load_persona()

chat_bp = Blueprint('chat_bp' , __name__)

@chat_bp.route('/' , methods = [ 'GET' , 'POST'])
def main():

	exception_message = ""

	if 'user_id' not in session :
		session['user_id'] = f'guest_{str(uuid.uuid4())}'
		session['count'] = 0

	current_user_id = session['user_id']
	if session.get( 'count' , 0) >= POST_COUNT :
		exception_message = err.get_error_message( 100 , persona_data )

	user_database = dbm.load_database(current_user_id) # ログデータを読み取る方式に変更
	message_list = user_database.get( "display_log" , [])
	
	do_method = request.method

	match do_method:
		case "GET" :
			return render_template("index.html" , name = NAME_STRUCT , model_icon_url = cfg.MODEL_ICON , all_message = message_list , exception_message = exception_message)

		case "POST" :
			try :
				if exception_message : 
					return jsonify({ "status": "error" , "message": exception_message}) , 500

				request_message = request.form.get( "user_input" , "").strip()

				if not request_message :
					exception_message = err.get_error_message( 101 , persona_data )
					return jsonify({ "status": "error" , "message": exception_message}) , 400

				elif len(request_message) > MAX_INPUT_LENGTH :
					exception_message = err.get_error_message( 102 , persona_data )
					return jsonify({ "status": "error" , "message": exception_message}) , 400

				model_message = model_reaction(current_user_id , request_message)
				session['count'] += 1

			except err.ApplicationError as app_error :

				error_str = str(app_error.message)

				print(f"エラーが発生しました >>　[{app_error.locat}] : {app_error.message}")

			# **エラーの表示 **************************************************************
				# レート制限
				if "429" in error_str:
					exception_message = err.get_error_message( 200 , persona_data )

				# フィルタリング
				elif "SAFETY" in error_str or "blocked" in error_str:
					exception_message = err.get_error_message( 201 , persona_data )

				# サーバーダウン
				elif "500" in error_str or "503" in error_str:
					exception_message = err.get_error_message( 202 , persona_data )

				# その他
				else: 
					exception_message = err.get_error_message( -999 , persona_data )
			# ****************************************************************************

				return jsonify({ "status": "error" , "message": exception_message}) , 500

			except Exception as e :
				print(f"予期せぬエラーが発生しました　>>　{e}")
				exception_message = err.get_error_message( -999 , persona_data )
				return jsonify({ "status": "error" , "message": exception_message}) , 500


			return jsonify({
				"status": "success",
				"user_message": request_message,
				"model_message": model_message
				})


# チャットボットからの返答
def model_reaction( user_id , user_message):
	try :	
		# 要約文のロード
		current_summary_text = dbm.load_database( user_id )["summary"]
	
		# チャットのインスタンスを生成
		chat_instance =  chat.ChatManager()

		message_extr = dbm.load_database(user_id)["message_list"]

		chat_instance.get_chat_bot( message_extr , current_summary_text)

		response = chat_instance.chat_bot.send_message(user_message) # メッセージを送信

		update_message = { "user_message" : user_message , "model_message" : response.text }

		# 履歴の更新
		dbm.update_chat_history( user_id , update_message)

		# 要約の判定
		message_extr = dbm.load_database(user_id)["message_list"] # 追加後に再度呼び出す
		summary_data = summary_check( chat_instance , current_summary_text , message_extr )

		if summary_data["summary"] is True :
			# 要約の更新
			dbm.update_summary_text( user_id , summary_data["content"])
			dbm.chat_history_manager( user_id )
			
		return response.text

	except err.ApplicationError as app_error :
		raise app_error

	except Exception as e :
		raise err.ApplicationError( "app - model_reaction" , str(e))

# 要約の判定(ここではあくまで判定とメッセージを返す)
def summary_check( chat_instance , old_summary , chat_message_list):
	message_list_len = len(chat_message_list )

	if  message_list_len >= THRESHOLD :
		try :

			summary_list_len = int(THRESHOLD*0.8)
			summary_list = chat_message_list[:summary_list_len]

			summary_prompt = spm.get_summary_prompt(old_summary , summary_list)

			return_data = {
				"summary" : True , 
				"content" : chat_instance.one_shot(summary_prompt),
				}

		except Exception as e :
			raise err.ApplicationError("app-summary_check" , str(e))

	else :
		return_data = {
				"summary" : False , 
				"content" : None,
				}

	return return_data