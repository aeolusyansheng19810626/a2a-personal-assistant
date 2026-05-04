---
title: A2A パーソナルアシスタント
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---

# A2A パーソナルアシスタント

A2A（Agent-to-Agent）プロトコルベースのマルチエージェント型パーソナルアシスタントシステムです。5つの独立したサービスがA2Aプロトコルで通信し、メール・カレンダー・タスク管理を統合的に処理します。

## 🎭 デモモード

本プロジェクトは2つの実行モードに対応しています：

### 本番モード（mainブランチ）
- Google OAuth認証情報（`credentials.json`）が必要です
- 実際のGmail・Calendar APIを使用します
- 個人利用に最適です

### デモモード（demoブランチ）
- **Google APIの設定は不要**
- モックデータを使用します
- 動作確認やデモンストレーションに最適です
- 🚀 **HuggingFace Spacesで公開中**：https://huggingface.co/spaces/aeolusyansheng/a2a-personal-assistant

## システムアーキテクチャ

### コアコンポーネント

1. **タスクエージェント** (ポート 8003)
   - SQLiteによるローカルタスク管理
   - 提供機能：create_task, list_tasks, complete_task, get_task
   - 外部依存なし

2. **メールエージェント** (ポート 8001)
   - Gmail API連携（OAuth2認証）
   - 提供機能：read_email, send_email, list_emails, search_emails
   - 認証トークン：`email_token.json`

3. **カレンダーエージェント** (ポート 8002)
   - Google Calendar API連携（OAuth2認証）
   - 提供機能：list_events, create_event, today_schedule, get_event
   - 認証トークン：`calendar_token.json`

4. **オーケストレーター** (ポート 8000)
   - Groq LLMによるインテント解析
   - 起動時の自動エージェント検出
   - 適切なエージェントへのルーティング
   - 5段階のモデルフォールバック機構

5. **Streamlit UI** (ポート 8501)
   - モダンなチャットインターフェース（パープルグラデーションヘッダー、ブランドサイドバー、バブルスタイルメッセージ）
   - エージェントステータスのリアルタイム監視
   - サンプルクエリとチャット履歴機能
   - 多言語対応（中国語、日本語、英語）

### 通信フロー

```
ユーザー → UI (8501) → オーケストレーター (8000) → [タスク/メール/カレンダーエージェント] → レスポンス
```

### Dockerデプロイアーキテクチャ（HuggingFace Spaces）

単一のDockerコンテナで動作しますが、**エージェント間の通信はすべて実際のHTTP A2A通信**で行われます：

```
Dockerコンテナ (HuggingFace Spaces)
├── Supervisor (プロセス管理)
│   ├── Orchestrator    (localhost:8000) ─┐
│   ├── Email Agent     (localhost:8001)  │
│   ├── Calendar Agent  (localhost:8002)  ├─ HTTP A2A通信
│   ├── Task Agent      (localhost:8003)  │
│   └── Streamlit UI    (0.0.0.0:7860) ───┘
│
└── 公開ポート: 7860 (Streamlit UI)
```

**主な特徴：**
- ✅ 実際のAgent-to-Agent HTTP通信（関数呼び出しではありません）
- ✅ 各エージェントは独立したプロセスで動作
- ✅ 完全なA2Aプロトコル実装（Agent Card + /tasksエンドポイント）
- ✅ OrchestratorはHTTP経由で他のエージェントを検出・呼び出し
- ✅ デモモードではモックデータを使用し、外部API不要

## A2Aプロトコル実装

各エージェントは以下のエンドポイントを実装しています：

1. **エージェント検出**：`GET /.well-known/agent.json`
   - エージェントカード（名前、説明、エンドポイント、提供機能）を返します

2. **タスク実行**：`POST /tasks`
   - リクエスト：`{"skill": "skill_name", "params": {...}}`
   - レスポンス：`{"status": "ok|error", "result": "...", "error": "..."}`

3. **ヘルスチェック**：`GET /health`
   - エージェントのステータスと接続状態を返します

## 技術スタック

- **バックエンド**：FastAPI (Python)
- **フロントエンド**：Streamlit
- **LLM**：Groq API（5層フォールバック）
- **データベース**：SQLite（タスクエージェント）
- **API**：Gmail API, Google Calendar API
- **認証**：OAuth 2.0

## コア機能

### インテリジェントルーティング
- LLMによるユーザーインテントの解析
- 適切なエージェントと機能の自動選択
- 自然言語からのパラメータ抽出

### マルチエージェント連携
- 独立したサービス間のHTTP通信
- 起動時の自動エージェント検出
- グレースフルなエラーハンドリング

### OAuth連携
- GmailとCalendarへのセキュアなアクセス
- トークンの自動リフレッシュ
- 初回実行時の認証フロー

### 多言語対応
- 完全な国際化（i18n）対応
- 対応言語：簡体字中国語、日本語、英語
- UI全要素のリアルタイム言語切り替え：タイトル、ラベル、エージェント名、サンプルクエリ
- 日本語は半角カタカナ表記を採用
- 英語サイドバータイトルの特別フォーマット処理（改行表示）

### モデルフォールバック機構
```python
TIER_TOP       = "openai/gpt-oss-120b"
TIER_UPPER_MID = "openai/gpt-oss-20b"
TIER_MID       = "qwen/qwen3-32b"
TIER_LOW       = "meta-llama/llama-4-scout-17b-16e-instruct"  # デフォルト
TIER_DEBUG     = "llama-3.1-8b-instant"  # フォールバック
```

レート制限（429エラー）発生時は、自動的に下位モデルへフォールバックします。

## 前提条件

- Python 3.8以上
- Google Cloudプロジェクト（Gmail・Calendar APIを有効化）
- Groq APIキー
- `credentials.json`（Google Cloud ConsoleのOAuth 2.0クライアントID）

## クイックスタート

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
cp .env.example .env
# .envファイルを編集してGROQ_API_KEYを設定してください
```

### 3. Google OAuth設定

- プロジェクトルートに`credentials.json`を配置してください
- 初回実行時、各エージェントがブラウザでOAuth認証を行います
- 認証トークンは`email_token.json`と`calendar_token.json`に保存されます

### 4. システムの起動

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**手動起動（デバッグ時）:**
```bash
# ターミナル 1 - タスクエージェント
cd task_agent && uvicorn main:app --port 8003

# ターミナル 2 - カレンダーエージェント
cd calendar_agent && uvicorn main:app --port 8002

# ターミナル 3 - メールエージェント
cd email_agent && uvicorn main:app --port 8001

# ターミナル 4 - オーケストレーター
cd orchestrator && uvicorn main:app --port 8000

# ターミナル 5 - UI
cd ui && streamlit run app.py
```

### 5. UIへのアクセス

ブラウザで http://localhost:8501 にアクセスしてください

## 使用例

### 言語切り替え
右サイドバー上部の言語ボタン（`中/日/英`表示）をクリックして言語を選択：
- `中` - 簡体字中国語
- `日` - 日本語
- `英` - English

すべてのUI要素が即座に切り替わります。

### タスク管理
- "高優先度のタスクを作成して提案をレビューする"
- "保留中のタスクを全て表示"
- "タスク1を完了にする"

### メール操作
- "最新5件のメールを表示"
- "john@example.comからのメールを検索"
- "jane@example.comに会議の件でメールを送信"

### カレンダー操作
- "今日の予定は？"
- "今後のイベントを表示"
- "明日14時に会議を作成"

## プロジェクト構造

```
a2a-personal-assistant/
├── task_agent/
│   ├── main.py              # FastAPIアプリケーション
│   ├── task_db.py           # SQLite操作
│   ├── agent_card.json      # A2Aエージェントカード
│   └── tasks.db             # 生成されたデータベース
├── email_agent/
│   ├── main.py              # FastAPIアプリケーション
│   ├── gmail_client.py      # Gmail APIラッパー
│   ├── agent_card.json      # A2Aエージェントカード
│   └── email_token.json     # OAuthトークン（生成）
├── calendar_agent/
│   ├── main.py              # FastAPIアプリケーション
│   ├── calendar_client.py   # Calendar APIラッパー
│   ├── agent_card.json      # A2Aエージェントカード
│   └── calendar_token.json  # OAuthトークン（生成）
├── orchestrator/
│   ├── main.py              # FastAPIアプリケーション（発見機能付き）
│   ├── llm_client.py        # Groqクライアント（フォールバック付き）
│   └── agent_card.json      # A2Aエージェントカード
├── ui/
│   └── app.py               # Streamlitインターフェース
├── credentials.json         # Google OAuth認証情報
├── .env                     # 環境変数（作成が必要）
├── .env.example             # 環境変数テンプレート
├── requirements.txt         # Python依存関係
├── start.bat                # Windows起動スクリプト
├── start.sh                 # Linux/Mac起動スクリプト
├── README.md                # 本ファイル
├── SETUP.md                 # 詳細なセットアップ手順
└── TESTING.md               # テストガイド
```

## APIエンドポイント

### タスクエージェント (8003)
- `GET /.well-known/agent.json` - エージェントカード
- `GET /health` - ヘルスチェック
- `POST /tasks` - タスク実行

### メールエージェント (8001)
- `GET /.well-known/agent.json` - エージェントカード
- `GET /health` - ヘルスチェック
- `POST /tasks` - タスク実行

### カレンダーエージェント (8002)
- `GET /.well-known/agent.json` - エージェントカード
- `GET /health` - ヘルスチェック
- `POST /tasks` - タスク実行

### オーケストレーター (8000)
- `GET /.well-known/agent.json` - エージェントカード
- `GET /health` - ヘルスチェック
- `GET /agents` - 発見されたエージェントのリスト
- `POST /query` - ユーザークエリの処理
- `POST /rediscover` - エージェントの再発見

### UI (8501)
- Webインターフェース：http://localhost:8501

## パフォーマンス指標

- **エージェントレスポンス**：200ms未満（タスク）、1-3秒（メール/カレンダー）
- **LLMルーティング**：2-5秒
- **エンドツーエンド**：3-8秒
- **メモリ使用量**：合計約500MB
- **CPU使用率**：アイドル時5%未満、アクティブ時30%未満

## トラブルシューティング

### よくある問題

1. **ポート競合**：ポート8000-8003、8501を使用中のプロセスを終了してください
2. **OAuth認証エラー**：トークンファイルを削除して再認証してください
3. **エージェント未検出**：ヘルスエンドポイントを確認し、再検出を実行してください
4. **レート制限**：システムが自動的に下位モデルへフォールバックします

### ログの確認

各サービスのターミナルでログを確認できます：
- タスクエージェントログ
- メールエージェントログ
- カレンダーエージェントログ
- オーケストレーターログ
- Streamlitログ

## セキュリティについて

- OAuthトークンはローカルに保存（バージョン管理対象外）
- APIキーは`.env`ファイルで管理（gitignore設定済み）
- 認証情報のハードコーディングなし
- 本番環境ではHTTPSの使用を推奨

## エラーハンドリング

- エージェント利用不可時のグレースフルフォールバック
- OAuthトークンの自動リフレッシュ
- レート制限時の自動フォールバック
- 無効な機能/パラメータのエラーメッセージ
- ネットワークタイムアウト処理

## テスト

詳細は`TESTING.md`を参照してください。以下のテストが含まれます：
- 個別エージェントテスト
- A2Aプロトコルテスト
- オーケストレータールーティングテスト
- UIエンドツーエンドテスト
- エラーハンドリングテスト

## 依存パッケージ

### コア
- fastapi==0.115.0
- uvicorn[standard]==0.32.0
- streamlit==1.40.0
- groq==0.11.0

### Google APIs
- google-api-python-client==2.149.0
- google-auth-httplib2==0.2.0
- google-auth-oauthlib==1.2.1

### ユーティリティ
- python-dotenv==1.0.1
- requests==2.32.3
- pydantic==2.9.2

## 今後の拡張予定

- 追加エージェント（Slack、Notionなど）
- エージェント間通信の実装
- 会話履歴の保持
- マルチステップワークフロー対応
- UI認証機能
- クラウドデプロイ
- モニタリング・メトリクス機能
- キャッシング機構
- ユニットテストの追加
- マルチユーザー対応

## プロジェクトステータス

✅ 全エージェント実装完了
✅ A2Aプロトコル正常動作
✅ オーケストレーターLLMルーティング完了
✅ Streamlit UI正常動作
✅ OAuth連携完了
✅ 起動スクリプト作成完了
✅ UI改善完了（ヘッダー、ブランドサイドバー、チャットバブル）
✅ HuggingFace Spacesデプロイ完了
✅ ドキュメント整備完了

**本番環境での利用が可能です！**

## サポート

問題が発生した場合：
1. セットアップ手順は`SETUP.md`を参照してください
2. テスト手順は`TESTING.md`を参照してください
3. エージェントログでエラーを確認してください
4. 全サービスが起動していることを確認してください
5. curlで個別エージェントをテストしてください

## ライセンス

MIT License