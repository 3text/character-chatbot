# chat_manager.py

#　インポート
from google import genai
from google.genai import types

# 独自のモジュールのインポート
import set_prompt as spm
import config_manager as cfg
import error_manager as err

# クラスとして設計
class ChatManager:
	def __init__(self):
		self.client = None
		self.chat_session = None

	def _get_client(self):
		if not self.client is None :
			return self.client

		my_key = cfg.api_key()

		if not my_key or my_key.strip() == "" :
			raise err.ApplicationError("chat_manager - get_client" , "APIキーが空です。")

		# クライアントの生成
		self.client = genai.Client(api_key = my_key)
		
		return self.client

	# AIの準備
	def get_chat_bot(self , history_data , summary_parts):

		client = self._get_client()

		try :
			chat_history_list = history_data
			summary_text = summary_parts

			self.chat_bot = client.chats.create(
				model = cfg.MODEL_NAME ,
				config = types.GenerateContentConfig(system_instruction = spm.get_prompt(summary_text)),
				history = chat_history_list
				)

			return self.chat_bot

		except Exception as e :
			raise err.ApplicationError("chat_manager - get_chat" , str(e))
			
	# ワンショット用(要約などで使用)
	def one_shot(self , oneshot_prompt):
		
		client = self._get_client()

		try :
			one_shot_reply = client.models.generate_content(
				model = cfg.MODEL_NAME,
				contents = oneshot_prompt
				)

			return one_shot_reply.text

		except Exception as e :
			raise err.ApplicationError("chat_manager - one_shot" , str(e))
