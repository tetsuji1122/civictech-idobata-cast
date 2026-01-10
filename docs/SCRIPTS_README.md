# スクリプト一覧

プロジェクトで使用するPythonスクリプトの一覧と使い方です。

## 📁 フォルダ構成

```
civictech-idobata-cast/
├── scripts/                    # Pythonスクリプト
│   ├── transcribe_podcast.py           # 音声書き起こし
│   ├── fix_transcripts.py              # 書き起こし修正
│   └── update_episodes.py              # エピソード更新
│
├── docs/                       # ドキュメント
│   ├── FIX_TRANSCRIPTS_README.md       # 修正ツールのガイド
│   ├── UPDATE_EPISODES_README.md       # 更新ツールのガイド
│   ├── TRANSCRIPT_README.md            # トランスクリプト管理ガイド
│   ├── CONFIG_README.md                # 共通設定ガイド
│   ├── SECURITY_GUIDE.md               # セキュリティガイド
│   └── WORKFLOW_GUIDE.md               # ワークフローガイド
│
└── data/                       # データファイル
    ├── episodes.json                   # エピソード情報
    ├── corrections.json                # 修正辞書
    └── transcripts/                    # 書き起こしJSON
```

---

## 🚀 スクリプトの使い方

### 📋 実行順序（推奨ワークフロー）

通常のワークフローでは、以下の順序でスクリプトを実行します：

```
1. transcribe_podcast.py     ← 音声ファイルを書き起こし
   ↓
2. fix_transcripts.py        ← 誤字を修正（必要に応じて）
   ↓
3. （エピソード配信）
   ↓
4. update_episodes.py        ← RSSフィードからエピソード情報を取得
```

#### 詳細なタイムライン

| タイミング | スクリプト | 説明 |
|-----------|-----------|------|
| **収録後** | `transcribe_podcast.py` | 音声ファイル（`data_voice/`）を自動書き起こし |
| **書き起こし確認後** | `fix_transcripts.py` | 誤字・表記ゆれを修正（必要に応じて） |
| **エピソード配信後** | `update_episodes.py` | RSSフィードから最新エピソード情報を取得 |

#### クイックリファレンス

```bash
# 1. 書き起こし生成（収録後）
python scripts/transcribe_podcast.py

# 2. 誤字修正（必要に応じて）
python scripts/fix_transcripts.py --episode 1.0.12 --wrong "誤字" --correct "正字"

# 3. エピソード更新（配信後）
python scripts/update_episodes.py
```

---

### ℹ️ 実行方法

すべてのスクリプトは**プロジェクトルートから**実行してください：

```bash
# プロジェクトルートにいることを確認
cd civictech-idobata-cast

# スクリプトを実行
python scripts/スクリプト名.py
```

---

## 📝 各スクリプトの説明

### 1. `transcribe_podcast.py` - 音声書き起こし

音声ファイルをGemini APIで書き起こし、JSON形式で保存します。

**機能:**
- 音声ファイルの自動文字起こし
- タイトル・説明・要約の自動生成
- 処理済みファイルの自動バックアップ

**使い方:**
```bash
# 基本的な使い方
python scripts/transcribe_podcast.py

# 環境変数が必要
# .env ファイルに GEMINI_API_KEY を設定
```

**詳細:** [docs/SECURITY_GUIDE.md](SECURITY_GUIDE.md)

---

### 2. `update_episodes.py` - エピソード更新

RSSフィードから最新のエピソード情報を取得して`episodes.json`を更新します。

**機能:**
- RSSフィードから自動取得
- 新しいエピソードのみ追加（重複なし）
- タグの自動生成
- Spotify URLの自動取得

**使い方:**
```bash
# 最新20件をチェック（推奨）
python scripts/update_episodes.py

# ドライラン
python scripts/update_episodes.py --dry-run

# 全エピソードを取得（初回のみ）
python scripts/update_episodes.py --all

# 特定件数をチェック
python scripts/update_episodes.py --limit 50
```

**詳細:** [docs/UPDATE_EPISODES_README.md](UPDATE_EPISODES_README.md)

---

### 3. `fix_transcripts.py` - 書き起こし修正

書き起こしJSONファイルの誤字・表記ゆれを修正します。

**機能:**
- コマンドライン引数で直接置換指定（推奨）
- 修正辞書ファイルも使用可能
- 自動バックアップ作成
- ドライランで事前確認
- エピソード番号を指定して安全に修正

**使い方:**
```bash
# コマンドライン引数で直接指定（推奨）
python scripts/fix_transcripts.py --episode 1.0.18 --wrong "誤字" --correct "正字" --dry-run

# 辞書ファイルを使用
python scripts/fix_transcripts.py --episode 1.0.18

# 全ファイルを一括修正（注意）
python scripts/fix_transcripts.py --all
```

**詳細:** [docs/FIX_TRANSCRIPTS_README.md](FIX_TRANSCRIPTS_README.md)

---

## 🔧 共通の設定

### 環境変数

`.env`ファイルで以下を設定：

```env
# 必須
GEMINI_API_KEY=your-api-key-here

# オプション（デフォルト値あり）
PODCAST_INPUT_DIR=data_voice
PODCAST_OUTPUT_DIR=data/transcripts
PODCAST_BACKUP_DIR=data_voice/backup
```

### パス設定

すべてのスクリプトは、内部的にプロジェクトルートからの相対パスを使用します。
`scripts/`フォルダ内にあっても、正しく動作します。

---

## 💡 よくある使い方

### 新しいエピソードのワークフロー

**収録後〜配信前:**
```bash
# 1. 音声ファイルを書き起こし
python scripts/transcribe_podcast.py

# 2. 書き起こしの誤字を修正（コマンドライン引数で直接指定）
python scripts/fix_transcripts.py --episode 1.0.XX --wrong "誤字" --correct "正字" --dry-run  # 確認
python scripts/fix_transcripts.py --episode 1.0.XX --wrong "誤字" --correct "正字"             # 実行
```

**配信後:**
```bash
# 3. RSSフィードから最新エピソード情報を取得
python scripts/update_episodes.py
```

### 定期メンテナンス

```bash
# 週1回: 新しいエピソードをチェック
python scripts/update_episodes.py

# 修正辞書を更新した場合のみ: 全書き起こしを一括修正
python scripts/fix_transcripts.py --all --dry-run  # 確認
python scripts/fix_transcripts.py --all            # 実行（確認プロンプトあり）
```

---

## ⚠️ 注意事項

1. **実行場所**: 必ずプロジェクトルートから実行してください
2. **API キー**: 書き起こし機能には`.env`ファイルが必要です
3. **バックアップ**: 重要な変更前にGitでコミットしてください
4. **ドライラン**: 初めて実行する場合は`--dry-run`で確認してください

---

## 📚 関連ドキュメント

- [共通設定ガイド](CONFIG_README.md)
- [セキュリティガイド](SECURITY_GUIDE.md)
- [ワークフローガイド](WORKFLOW_GUIDE.md)
- [書き起こし管理](TRANSCRIPT_README.md)
- [エピソード更新](UPDATE_EPISODES_README.md)
- [誤字修正ツール](FIX_TRANSCRIPTS_README.md)

