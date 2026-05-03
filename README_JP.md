---
title: A2A パーソナルアシスタント
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---

# A2A パーソナルアシスタント

A2A（Agent-to-Agent）プロトコルに基づくマルチエージェントパーソナルアシスタントシステム。5つの独立したサービスがA2Aプロトコルを通じて通信し、メール、カレンダー、タスク管理を処理します。

## 🎭 デモモード

本プロジェクトは2つの実行モードをサポートしています：

### 本番モード（mainブランチ）
- Google OAuth認証情報（`credentials.json`）が必要
- 実際のGmailとCalendar APIコール
- 個人使用に適しています

### デモモード（demoブランチ）
- **Google API設定不要**
- ハードコードされたモックデータを使用
- クイック体験とデモに適しています
- 🚀 **HuggingFace Spacesにデプロイ済み**：https://huggingface.co/spaces/aeolusyansheng/a2a-personal-assistant

## システムアーキテクチャ

### コアコンポーネント

1. **タスクエージェント** (ポート 8003)
   - SQLiteベースのローカルタスク管理
   - スキル：create_task, list_tasks, complete_task, get_task
   - 外部依存なし

2. **メールエージェント** (ポート 8001)
   - Gmail API統合（OAuth2）
   - スキル：read_email, send_email, list_emails, search_emails
   - トークン：`email_token.json`

3. **カレンダーエージェント** (ポート 8002)
   - Google Calendar API統合（OAuth2）
   - スキル：list_events, create_event, today_schedule, get_event
   - トークン：`calendar_token.json`

4. **オーケストレーター** (ポート 8000)
   - Groq LLMによる意図認識
   - 起動時に自動的にエージェントを発見
   - クエリを適切なエージェントにルーティング
   - 5層モデルフォールバックシステム

5. **Streamlit UI** (ポート 8501)
   - モダンなチャットインターフェース（紫のグラデーショントップバー、ブランドサイドバー、バブルスタイルメッセージ）
   - リアルタイムエージェントステータス監視
   - サンプルクエリとチャット履歴
   - 多言語サポート（中国語、日本語、英語）

### 通信フロー

```
ユーザー → UI (8501) → オーケストレーター (8000) → [タスク/メール/カレンダーエージェント] → レスポンス
```

### Dockerデプロイアーキテクチャ（HuggingFace Spaces）

単一のDockerコンテナで実行されていますが、**すべてのエージェント間通信は実際のHTTP A2Aコール**です：

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
- ✅ 実際のAgent-to-Agent HTTP呼び出し（関数呼び出しではない）
- ✅ 各エージェントは独自のプロセスで独立して実行
- ✅ 完全なA2Aプロトコル実装（Agent Card + /tasksエンドポイント）
- ✅ OrchestratorはHTTPを通じて他のエージェントを発見・呼び出し
- ✅ デモモードはモックデータを使用し、外部API不要

## A2Aプロトコル実装

各エージェントは以下のエンドポイントを実装しています：

1. **エージェント発見**：`GET /.well-known/agent.json`
   - エージェントカード（名前、説明、エンドポイント、スキル）を返す

2. **タスク実行**：`POST /tasks`
   - リクエスト：`{"skill": "skill_name", "params": {...}}`
   - レスポンス：`{"status": "ok|error", "result": "...", "error": "..."}`

3. **ヘルスチェック**：`GET /health`
   - エージェントのステータスと接続性を返す

## 技術スタック

- **バックエンド**：FastAPI (Python)
- **フロントエンド**：Streamlit
- **LLM**：Groq API（5層フォールバック）
- **データベース**：SQLite（タスクエージェント）
- **API**：Gmail API, Google Calendar API
- **認証**：OAuth 2.0

## コア機能

### インテリジェントルーティング
- LLMがユーザーの意図を分析
- 適切なエージェントとスキルを自動選択
- 自然言語からパラメータを抽出

### マルチエージェント調整
- 独立したサービスがHTTPで通信
- 起動時に自動的にエージェントを発見
- 優雅なエラーハンドリング

### OAuth統合
- GmailとCalendarへの安全なアクセス
- トークンの自動更新
- 初回実行時の認証フロー

### 多言語サポート
- 完全な国際化（i18n）サポート
- サポート言語：簡体字中国語、日本語、英語
- UIのすべての要素が言語切り替えにリアルタイムで対応：タイトル、ラベル、エージェント名、サンプルクエリ
- 日本語は半角カタカナ形式を採用
- 英語サイドバータイトルの特別なフォーマット処理（改行表示）

### モデルフォールバックシステム
```python
TIER_TOP       = "openai/gpt-oss-120b"
TIER_UPPER_MID = "openai/gpt-oss-20b"
TIER_MID       = "qwen/qwen3-32b"
TIER_LOW       = "meta-llama/llama-4-scout-17b-16e-instruct"  # デフォルト
TIER_DEBUG     = "llama-3.1-8b-instant"  # フォールバック
```

レート制限（429エラー）に遭遇した場合、自動的に下位層にフォールバックします。

## 前提条件

- Python 3.8+
- Google Cloudプロジェクト（Gmail and Calendar APIが有効）
- Groq APIキー
- `credentials.json`（Google Cloud ConsoleのOAuth 2.0クライアントID）

## クイックスタート

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境設定

```bash
cp .env.example .env
# .envファイルを編集してGROQ_API_KEYを追加
```

### 3. Google OAuthセットアップ

- プロジェクトルートディレクトリに`credentials.json`があることを確認
- 初回実行時、各エージェントがブラウザを開いてOAuth認証を行います
- トークンは`email_token.json`と`calendar_token.json`として保存されます

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

**手動起動（デバッグ用）:**
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

ブラウザで以下にアクセス：http://localhost:8501

## 使用例

### 言語切り替え
右サイドバー上部の言語ボタン（`中/日/英`と表示）をクリックして異なる言語を選択：
- `中` - 簡体字中国語
- `日` - 日本語
- `英` - English

すべてのUI要素が即座に言語変更に対応します。

### タスク管理
- "高優先度のタスクを作成して提案をレビューする"
- "すべての保留中のタスクをリスト表示"
- "タスク1を完了としてマーク"

### メール操作
- "最新の5件のメールを表示"
- "john@example.comからのメールを検索"
- "jane@example.comに会議についてメールを送信"

### カレンダー操作
- "今日のスケジュールは？"
- "今後のイベントを表示"
- "明日の午後2時に会議を作成"

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

- **エージェントレスポンス**：< 200ms（タスク）、1-3秒（メール/カレンダー）
- **LLMルーティング**：2-5秒
- **エンドツーエンド**：3-8秒
- **メモリ**：合計約500MB
- **CPU**：アイドル < 5%、アクティブ < 30%

## トラブルシューティング

### よくある問題

1. **ポート競合**：ポート8000-8003、8501を使用しているプロセスを終了
2. **OAuthエラー**：トークンファイルを削除して再認証
3. **エージェント未発見**：ヘルスエンドポイントを確認し、再発見をトリガー
4. **レート制限**：システムが自動的に下位層モデルにフォールバック

### ログの確認

各サービスのターミナルウィンドウを確認：
- タスクエージェントログ
- メールエージェントログ
- カレンダーエージェントログ
- オーケストレーターログ
- Streamlitログ

## セキュリティ考慮事項

- OAuthトークンはローカルに保存（バージョン管理外）
- APIキーは`.env`ファイルに保存（gitignore済み）
- ハードコードされた認証情報なし
- 本番環境ではHTTPSの使用を推奨

## エラーハンドリング

- エージェント利用不可時の優雅なフォールバック
- OAuthトークンの自動更新
- レート制限の自動フォールバック
- 無効なスキル/パラメータのエラーメッセージ
- ネットワークタイムアウト処理

## テスト

詳細は`TESTING.md`を参照。以下を含みます：
- 個別エージェントテスト
- A2Aプロトコルテスト
- オーケストレータールーティングテスト
- UIエンドツーエンドテスト
- エラーハンドリングテスト

## 依存関係

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

## 今後の改善

- より多くのエージェントを追加（Slack、Notionなど）
- エージェント間通信の実装
- 会話メモリの追加
- マルチステップワークフローのサポート
- UI認証の追加
- クラウドへのデプロイ
- モニタリング/メトリクスの追加
- キャッシングの実装
- ユニットテストの追加
- マルチユーザーサポート

## プロジェクトステータス

✅ すべてのエージェント実装済み  
✅ A2Aプロトコル正常動作  
✅ オーケストレーターLLMルーティング完了  
✅ Streamlit UI機能正常  
✅ OAuth統合完了  
✅ 起動スクリプト作成済み  
✅ UI美化完了（トップバー、ブランドサイドバー、チャットバブル）  
✅ HuggingFace Spacesにデプロイ済み  
✅ ドキュメント完備  

**準備完了、テストとデプロイを開始できます！**

## サポート

問題が発生した場合：
1. セットアップ手順については`SETUP.md`を参照
2. テスト手順については`TESTING.md`を参照
3. エラーを見つけるためにエージェントログを確認
4. すべてのサービスが実行中であることを確認
5. curlを使用して個別のエージェントをテスト

## ライセンス

MIT License