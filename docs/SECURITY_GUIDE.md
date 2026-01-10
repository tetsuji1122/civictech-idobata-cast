# セキュリティガイド

## 🔒 Git管理から除外される項目

このプロジェクトでは、以下のファイルが`.gitignore`により自動的に除外されます：

### 1. APIキー・認証情報

- `.env` - 環境変数ファイル
- `.env.local` - ローカル環境変数
- `config.ini` - 設定ファイル
- `secrets.json` - シークレット情報
- `api_keys.txt` - APIキー

### 2. 音声ファイル（録音データ）

- `*.m4a` - M4A形式の音声ファイル
- `*.mp3` - MP3形式の音声ファイル
- `*.wav` - WAV形式の音声ファイル
- その他の音声形式 (aac, flac, ogg, wma)

### 3. 書き起こし作業フォルダ

- `data_voice/` - 音声ファイル格納フォルダ
- `data_voice/backup/` - 処理済み音声ファイルのバックアップ
- `podcast/` - ポッドキャスト作業フォルダ
- `output/` - 出力フォルダ
- `transcripts_temp/` - 一時書き起こしフォルダ

### 4. バックアップファイル

- `*.backup`
- `data/episodes.json.backup*`

---

## 🔑 APIキーの安全な管理方法

### 方法1：環境変数ファイル（推奨）

#### 1. `.env`ファイルを作成

```bash
# Windowsの場合
copy env.example .env

# Mac/Linuxの場合
cp env.example .env
```

#### 2. `.env`ファイルを編集

```
GEMINI_API_KEY=your_actual_api_key_here
```

#### 3. Pythonで読み込む

```python
import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# APIキーを取得
api_key = os.getenv('GEMINI_API_KEY')
```

#### 必要なライブラリ

```bash
pip install python-dotenv
```

---

### 方法2：環境変数で直接設定

#### Windowsの場合

PowerShellで一時的に設定：
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
python scripts/transcribe_podcast.py
```

永続的に設定（システム環境変数）：
1. 「システムのプロパティ」→「環境変数」
2. 「新規」をクリック
3. 変数名: `GEMINI_API_KEY`
4. 変数値: `your_api_key_here`

#### Mac/Linuxの場合

```bash
export GEMINI_API_KEY="your_api_key_here"
python scripts/transcribe_podcast.py
```

永続的に設定（~/.bashrc または ~/.zshrc）：
```bash
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

---

## 📁 推奨フォルダ構造

```
# プロジェクトフォルダ（Git管理）
civictech-idobata-cast/
├── .gitignore              ✅ Git管理される
├── env.example             ✅ Git管理される（サンプル）
├── .env                    ❌ Git管理されない（実際のAPIキー）
├── transcribe_podcast.py   ✅ Git管理される（コード）
├── data_voice/             ❌ Git管理されない（音声ファイル格納）
│   ├── ep1.0.13.m4a       ❌ 処理待ちの音声ファイル
│   └── backup/            ❌ 処理済み音声ファイル（自動移動）
│       ├── ep1.0.12.m4a   ❌ 音声ファイル
│       └── ep1.0.11.m4a   ❌ 音声ファイル
└── data/
    ├── episodes.json       ✅ Git管理される
    └── transcripts/        ✅ Git管理される
        └── ep1.0.12.json   ✅ Git管理される（書き起こし結果のみ）
```

---

## ✅ 確認方法

### 1. `.gitignore`が正しく動作しているか確認

```bash
# Gitで管理されているファイル一覧
git ls-files

# 除外されているファイルを確認
git status --ignored
```

### 2. APIキーが含まれていないか確認

```bash
# 全ファイルから"GEMINI_API_KEY"を検索
git grep -i "api.*key" --cached
```

---

## ⚠️ 注意事項

### 誤ってAPIキーをコミットした場合

#### 1. 直ちにAPIキーを無効化
- Google Cloud Consoleでキーを削除
- 新しいキーを生成

#### 2. Gitの履歴から削除

```bash
# BFG Repo-Cleanerを使用（推奨）
bfg --replace-text passwords.txt

# または git filter-branch
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

#### 3. リポジトリを強制プッシュ

```bash
git push origin --force --all
git push origin --force --tags
```

---

## 🛡️ セキュリティベストプラクティス

### ✅ すべきこと

- `.env`ファイルにAPIキーを保存
- `.gitignore`にAPIキーファイルを追加
- 定期的にAPIキーをローテーション
- チーム内で`.env.example`を共有

### ❌ してはいけないこと

- APIキーをコードに直接記述
- APIキーをコミットメッセージに含める
- 公開リポジトリにAPIキーをプッシュ
- Slackなどのチャットでキーを共有

---

## 📚 参考リンク

- [Google AI Studio - API Keys](https://aistudio.google.com/app/apikey)
- [GitHub - .gitignore templates](https://github.com/github/gitignore)
- [python-dotenv documentation](https://pypi.org/project/python-dotenv/)

---

## ❓ トラブルシューティング

### Q: `.env`ファイルが読み込まれない

A: 以下を確認してください：
1. `.env`ファイルがプロジェクトのルートにあるか
2. `python-dotenv`がインストールされているか
3. `load_dotenv()`が実行されているか

### Q: 音声ファイルが誤ってコミットされそう

A: 以下を実行：
```bash
# キャッシュから削除（ファイル自体は削除されない）
git rm --cached podcast/*.m4a
git commit -m "Remove audio files from Git"
```

### Q: バックアップファイルがコミットされる

A: `.gitignore`に以下を追加：
```
*.backup
*.backup-*
```

---

何か問題があれば、GitHubのIssueで報告してください！

