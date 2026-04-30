# character-chatbotCharactor  Event Edition

** 概要 ***
Googleの軽量LLM Gemma と Flask を組み合わせた、対話型キャラクターチャットボットです。
即売会等のイベントでの展示・配布を想定しており、キャラクターとの自然な対話だけでなく、イベント運営をサポートする通知機能（Calling Bot）も搭載しています。

	[!CAUTION]
	通知機能（Calling Bot）に関する注意
	本ツールの通知機能は「単一ブース」での使用を前提とした設計です。
	同時に複数の場所で稼働させるマルチユーザー対応ではありません。

** 主な機能 ***
キャラクター対話機能: Gemma-4-31b-it を使用し、設定されたペルソナに基づいた柔軟な回答を行います。
文脈維持・要約システム: 会話が一定数に達すると自動的に内容を要約し、長期的な文脈を維持したまま会話を継続できます。

キャラクター専用エラーハンドリング: システムエラーをそのまま表示せず、キャラクターの性格に合わせたセリフで通知します。
Calling Bot : ntfy と連携し、ブースへの来客をスマートウォッチ等に通知する機能を備えています。

レスポンシブデザイン: スマートフォンでの閲覧を最適化したUIを採用しています。

** 開発プロセス ***
本プロジェクトは、作者の独学によるPython/Web開発の学習アウトプットとして制作されました。
あえてAIによるコード生成機能を使わず、AIを仕様リファレンスとして活用する手法を採用しています。
効率的な記述方法よりも、基礎学習に焦点を当て作成されました。

・必要な関数の仕様や引数の構造をAIに確認し、ロジック自体はすべて手書きで実装。
・FlaskのBlueprintを活用したモジュール化により、拡張性の高い設計を目指しました。

** 技術スタック ***
Backend: Python / Flask
Frontend: HTML / CSS / JavaScript
LLM: Google Gemma (via Google Gen AI SDK)
Database: SQLite / SQLAlchemy
Notification: ntfy.sh

** セットアップ ***
1)リポジトリをクローンします。
2)必要なライブラリをインストールします：
	"pip install -r requirements.txt"

3).env ファイルを作成し、以下の項目を設定してください：

MY_API_KEY: Google AI StudioのAPIキー
SECRET_KEY: Flaskのセッション用秘密鍵
DATABASE_URI: データベースの接続先（デフォルトはSQLite）

アプリケーションを起動します：
	"python app.py"

** ライセンス・謝辞 ***
本ツールは Google が提供する Gemma モデルを使用しています。利用にあたっては Gemma Terms of Use に準拠してください。
本バージョンのキャラクター設定：雪音りう
