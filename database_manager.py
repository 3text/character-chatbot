# database_manager.py

# インポート
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime ,timezone
from sqlalchemy import event
from sqlalchemy.engine import Engine

# 独自のモジュールのインポート
import error_manager as err

db = SQLAlchemy()

# ロック制限の解除
@event.listens_for(Engine , "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
	cursor = dbapi_connection.cursor()
	cursor.execute("PRAGMA journal_mode=WAL")
	cursor.execute("PRAGMA synchronous=NORMAL")
	cursor.close()


# 要約のテーブル　UserSummary( user_name , summary_text)
class UserSummary(db.Model):
	# テーブルの名前を定義
	__tablename__ = "user_summary"

	user_name = db.Column(db.String(25) , primary_key = True)
	summary_text = db.Column(db.Text , default = "まだ要約されていません")

# 会話ログのテーブル ChatHistory( user_name , role , message , history_bool)
class ChatLog(db.Model):
	# テーブルの名前を定義
	__tablename__ = "chat_log"

	id = db.Column( db.Integer , primary_key = True)
	
	user_name = db.Column( db.String(25) , nullable = False)
	role = db.Column( db.String(10) , nullable = False)
	message = db.Column(db.Text , nullable = False)

	# 履歴として渡すことを管理するフラグ
	history_bool = db.Column( db.Boolean , default = True , nullable = True )

	create_at = db.Column(db.DateTime , default = lambda : datetime.now(timezone.utc))


# 抽出
def load_database( user_id ):

	try :
		# 要約文の抽出
		db_summary = UserSummary.query.filter_by( user_name = user_id ).first()

		if db_summary :
			current_db_summary = db_summary.summary_text
		else :
			current_db_summary = "まだ要約されていません。"


		# 直近の会話の呼び出し
		user_chat_history = ChatLog.query.filter_by( user_name = user_id , history_bool = True )
		db_chat_history = user_chat_history.order_by(ChatLog.create_at.asc()).all()

		message_list = [{"role": c.role, "parts": [{"text": c.message}]} for c in db_chat_history]

		# 会話ログの呼び出し
		user_chat_log_table = ChatLog.query.filter_by( user_name = user_id)
		db_chat_log = user_chat_log_table.order_by(ChatLog.create_at.asc()).all()
		display_message_list = [{"role": l.role, "parts": [{"text": l.message}]} for l in db_chat_log]

	except Exception as e :
		raise err.ApplicationError( "database_manager - load_database" , str(e))		

	return {
		"summary" : current_db_summary , 
		"message_list" : message_list ,
		"display_log" : display_message_list
		}


# 要約文の出力
def update_summary_text( user_id , current_summary_text):

	try :
		# 要約文が存在するかの確認　存在すれば上書き/しなければ新規
		db_summary = UserSummary.query.filter_by( user_name = user_id ).first()

		if not db_summary :
			db_summary = UserSummary( user_name = user_id)
			db.session.add(db_summary)

		db_summary.summary_text = current_summary_text

		db.session.commit()

	except Exception as e :
		db.session.rollback()
		raise err.ApplicationError( "database_manager - update_summary_text" , str(e))


# 会話文の出力
def update_chat_history( user_id , update_message):

	try :
		# 会話文は初期値が空の配列のため最初から追記でよい
		add_user_log = ChatLog( user_name = user_id , role = "user" , message = update_message["user_message"] )
		add_model_log = ChatLog( user_name = user_id , role = "model" , message = update_message["model_message"] )

		db.session.add(add_user_log)
		db.session.add(add_model_log)
	
		db.session.commit()

	except Exception as e :
		db.session.rollback()
		raise err.ApplicationError( "database_manager - update_chat_history" , str(e))

# 直近の会話の管理
def chat_history_manager( user_id , keep_count = 4 ):
	try :
		keep_subquery = ( 
			db.session.query(ChatLog.id)
			.filter(ChatLog.user_name == user_id , ChatLog.history_bool == True )
			.order_by(ChatLog.create_at.desc())
			.limit(keep_count)
			.all()
			)

		keep_ids = [row.id for row in keep_subquery]

		if keep_ids :
			db.session.query(ChatLog).filter(
				ChatLog.user_name == user_id ,
				ChatLog.history_bool == True ,
				ChatLog.id.notin_(keep_ids)
				).update({"history_bool" : False} , synchronize_session=False )

		db.session.commit()

	except Exception as e :
		db.session.rollback()
		raise err.ApplicationError( "database_manager - chat_history_manager" , str(e))

