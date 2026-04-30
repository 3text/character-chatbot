# error_manager.py

# **今後独自の例外処理が欲しくなったらここで管理する******************************
DEFAULT_ERROR_MESSAGE = {
	# 独自の例外処理は100番台を使用
	"100" : "回数制限です", #回数制限
	"101" : "空白文字を受け取りました" , # 空白
	"102" : "文字数を超過しています" , # 文字数制限

	# APIエラーは200番台を使用
	"200" : "リクエストが集中しています<br>時間を空けてお試しください" , #429エラー
	"201" : "フィルタリングに抵触します" , #セーフティフィルタリング
	"202" : "回線が混雑しています" , #500,503エラー

	# 未定義のエラー
	"-999" : "未定義の不具合が発生<br>開発者に連絡してください"
}
# *****************************************************************************

# アプリケーション全体での共通の処理 (最初はこれだけで対応。後々細分化する。)
class ApplicationError(Exception):
	def __init__(self , locat , message):
		self.locat = locat
		self.message = message
		super().__init__(message)	


# エラーメッセージの生成
def get_error_message( code , persona_data = None):

	cfg_error_message = persona_data.get( "error_message_list" , DEFAULT_ERROR_MESSAGE )

	if code in cfg_error_message :
		error_message = cfg_error_message[code]
	else :
		error_message = DEFAULT_ERROR_MESSAGE[code]

	return error_message