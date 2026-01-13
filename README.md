# civictech-idobata-cast

シビックテック井戸端キャストの公式ホームページ

## 🎙️ プロジェクト概要

ポッドキャスト文化からシビックテックの入り口を広げる、音声メディアプロジェクトです。

- **配信**: Spotify / Apple Podcasts / YouTube
- **サイト**: GitHub Pages でホスティング
- **技術**: Vue.js + Vuetify（静的サイト）

---

## 📁 フォルダ構成

```
civictech-idobata-cast/
├── index.html              # トップページ
├── episodes.html           # エピソード一覧
├── episode-detail.html     # エピソード詳細
├── about.html              # このポッドキャストについて
├── countdowntimer.html     # 収録用タイマー
│
├── js/                     # JavaScript
│   ├── config.js          # 共通設定
│   ├── index.js
│   ├── episodes.js
│   ├── episode-detail.js
│   └── about.js
│
├── css/                    # スタイルシート
├── img/                    # 画像
├── se/                     # 効果音
│
├── data/                   # データファイル
│   ├── episodes.json           # エピソード情報
│   └── transcripts/            # 書き起こしJSON
│
├── scripts/                # Pythonスクリプト
│   ├── transcribe_podcast.py       # 音声書き起こし
│   ├── edit_transcript.py          # 書き起こし編集（GUI）
│   └── update_episodes.py          # エピソード更新
│
└── docs/                   # ドキュメント
    ├── SCRIPTS_README.md           # スクリプト一覧
    ├── UPDATE_EPISODES_README.md   # エピソード更新ガイド
    ├── TRANSCRIPT_README.md        # トランスクリプト管理
    ├── CONFIG_README.md            # 共通設定ガイド
    ├── SECURITY_GUIDE.md           # セキュリティガイド
    └── WORKFLOW_GUIDE.md           # ワークフローガイド
```

---

## 🚀 スクリプトの使い方

### エピソード更新

```bash
python scripts/update_episodes.py
```

### 音声書き起こし

```bash
python scripts/transcribe_podcast.py
```

### 書き起こし編集

```bash
python scripts/edit_transcript.py
```

詳細は [docs/SCRIPTS_README.md](docs/SCRIPTS_README.md) をご覧ください。

---

## 🤖 自動更新（GitHub Actions）

エピソード情報はGitHub Actionsにより自動更新されます。

### エピソード情報の自動更新

- **スケジュール**: 毎日6:30 JST（UTC 21:30）
- **ワークフロー**: `.github/workflows/update_episodes.yml`
- **実行内容**: `scripts/update_episodes.py`を実行し、変更があれば自動コミット

### X（Twitter）への自動投稿

- **スケジュール**: 毎時0分にチェック
- **ワークフロー**: `.github/workflows/post_to_x.yml`
- **実行内容**: RSSフィードをチェックし、新しいエピソードがあればXに自動投稿

**設定方法**:
1. GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」を開く
2. 以下のSecretsを追加：
   - `X_BEARER_TOKEN`（推奨）: X API v2のBearer Token
   - または OAuth 1.0a方式の場合：
     - `X_API_KEY`
     - `X_API_SECRET`
     - `X_ACCESS_TOKEN`
     - `X_ACCESS_TOKEN_SECRET`

手動実行も可能です：
1. GitHubリポジトリの「Actions」タブを開く
2. 実行したいワークフローを選択
3. 「Run workflow」ボタンをクリック

---

## 🔧 開発

### ローカルサーバー起動

```bash
python -m http.server 8000
```

http://localhost:8000 にアクセス

### 必要な環境

- Python 3.7+
- 依存ライブラリ: `pip install -r requirements.txt`
- 環境変数: `.env` ファイル（書き起こし機能を使う場合）

---

## 📚 ドキュメント

- [スクリプト一覧](docs/SCRIPTS_README.md)
- [共通設定](docs/CONFIG_README.md)
- [セキュリティガイド](docs/SECURITY_GUIDE.md)
- [ワークフロー](docs/WORKFLOW_GUIDE.md)

---

## 🌐 リンク

- [GitHub リポジトリ](https://github.com/tetsuji1122/civictech-idobata-cast)
- [Spotify](https://open.spotify.com/show/31JfR2D72gENOfOwq3AcKw)
- [Apple Podcasts](https://podcasts.apple.com/jp/podcast/id1587297171)
- [YouTube](https://www.youtube.com/@civictechcast)
