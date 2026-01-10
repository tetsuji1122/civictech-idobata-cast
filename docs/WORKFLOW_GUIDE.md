# ワークフローガイド

## 📝 書き起こし作成から公開までの流れ

### 🎯 全体の流れ

```
1. 収録
   ↓
2. 音声ファイルを配置 (data_voice/)
   ↓
3. 書き起こし生成 (transcribe_podcast.py)
   ↓
4. 書き起こしの編集・修正 (edit_transcript.py)
   ↓
5. Gitにコミット
   ↓
6. エピソード配信（Spotify等）
   ↓
7. RSSフィード更新 (update_episodes.py)
   ↓
8. GitHub Pagesで公開
```

---

## 📍 ステップ詳細

### ステップ1：音声を録音・編集

お好みのツールで録音と編集を行います。

**推奨形式**:
- M4A（推奨）
- MP3
- WAV

---

### ステップ2：音声ファイルを配置

編集済みの音声ファイルを `data_voice/` フォルダに配置します。

```bash
data_voice/
├── ep1.0.12.m4a  ← ここに配置
└── ep1.0.11.m4a
```

**ファイル名の形式**: `ep{エピソード番号}.m4a`  
例: `ep1.0.12.m4a`, `ep0.23.15.m4a`

---

### ステップ3：書き起こし生成

`transcribe_podcast.py`を実行して、自動的に書き起こしを生成します。

```bash
# プロジェクトのルートディレクトリで実行
python scripts/transcribe_podcast.py
```

**処理内容**:
1. `data_voice/` フォルダ内の音声ファイルを検索
2. Gemini APIにアップロードして書き起こし
3. タイトル、説明、要約を自動生成
4. `data/transcripts/ep1.0.12.json` として保存
5. **処理完了後、音声ファイルを `data_voice/backup/` に自動移動**

**生成されるファイル**:
```json
{
  "episode_number": "1.0.12",
  "file_name": "ep1.0.12.m4a",
  "sub_title": "生成されたサブタイトル",
  "detailed_description": "生成された説明文",
  "summary": "生成された要約",
  "transcript": "詳細な書き起こし全文"
}
```

---

### ステップ4：書き起こしの編集・修正

生成された書き起こしを確認し、誤字があればGUIエディタで修正します。

```bash
python scripts/edit_transcript.py
```

**処理内容**:
1. GUIエディタが起動します
2. ファイルを選択して編集
3. 検索・置換機能で誤字を修正
4. 保存時に自動的にバックアップを作成（`data/transcripts_backup/`）

---

### ステップ5：Gitにコミット

生成された書き起こしファイルをGitにコミットします。

```bash
# 書き起こしファイルを追加
git add data/transcripts/ep1.0.12.json

# コミット
git commit -m "Add transcript for ep1.0.12"

# プッシュ
git push
```

**重要**: 
- ✅ `data/transcripts/` の JSONファイルだけをコミット
- ❌ `data_voice/` の音声ファイルはコミットしない（.gitignoreで除外済み）

---

### ステップ6：エピソード配信

Spotifyなどのポッドキャスト配信プラットフォームに音声ファイルをアップロードします。

1. Anchor/Spotify for Podcastersにログイン
2. 新しいエピソードを作成
3. 音声ファイルをアップロード
4. タイトル・説明文を入力（書き起こしJSONの内容を参考に）
5. 公開

---

### ステップ7：RSSフィード更新

エピソードが配信されたら、RSSフィードから最新情報を取得します。

```bash
python scripts/update_episodes.py
```

**処理内容**:
1. RSSフィードから最新エピソード情報を取得
2. エピソード番号、タイトル、日付、説明などを抽出
3. `data/episodes.json` に追加
4. 自動的にタグを生成

**Gitにコミット**:
```bash
git add data/episodes.json
git commit -m "Update episodes.json with ep1.0.12"
git push
```

---

### ステップ8：GitHub Pagesで公開

GitHubにプッシュすると、GitHub Pagesが自動的に更新されます。

**確認**:
1. Webサイトにアクセス
2. エピソード一覧に新しいエピソードが表示される
3. エピソード詳細ページで書き起こしが表示される

---

## 🔄 実際のタイムライン例

### 例：ep1.0.12の場合

| 日時 | アクション |
|------|-----------|
| **12/1 18:00** | 録音 |
| **12/1 19:00** | 編集完了、`data_voice/ep1.0.12.m4a` に保存 |
| **12/1 19:10** | `transcribe_podcast.py` 実行（5分程度） |
| **12/1 19:15** | 書き起こし確認、誤字修正（必要に応じて） |
| **12/1 19:20** | Gitにコミット・プッシュ |
| **12/2 09:00** | Spotifyに音声アップロード |
| **12/2 09:30** | エピソード公開 |
| **12/2 10:00** | `update_episodes.py` 実行 |
| **12/2 10:05** | episodes.jsonをGitにコミット・プッシュ |
| **12/2 10:10** | GitHub Pagesで公開完了 ✨ |

---

## ⚡ クイックリファレンス

### 書き起こし生成
```bash
python scripts/transcribe_podcast.py
```

### 書き起こしの編集・修正
```bash
# GUIエディタで編集
python scripts/edit_transcript.py
```

### RSSフィード更新
```bash
python scripts/update_episodes.py
```

### ローカルプレビュー
```bash
python -m http.server 8000
# http://localhost:8000 にアクセス
```

### Gitコマンド
```bash
# 書き起こしをコミット
git add data/transcripts/ep1.0.12.json
git commit -m "Add transcript for ep1.0.12"

# エピソード情報をコミット
git add data/episodes.json
git commit -m "Update episodes.json with ep1.0.12"

# プッシュ
git push
```

---

## 🗂️ 音声ファイルの管理

### 処理前
- `data_voice/` フォルダに音声ファイルを配置
- ファイル名は `epX.X.X.m4a` の形式にする

### 処理後
- 書き起こし完了後、音声ファイルは**自動的に** `data_voice/backup/` に移動されます
- 処理に失敗したファイルは移動せず、`data_voice/` に残ります
- 再実行すると、残っているファイルのみが処理されます

### フォルダ構造
```
data_voice/
├── ep1.0.13.m4a         ← 処理待ち
└── backup/              ← 処理済み（自動移動）
    ├── ep1.0.12.m4a
    └── ep1.0.11.m4a
```

**注意**: `data_voice/` フォルダと `backup/` フォルダの内容は `.gitignore` で除外されており、Gitにアップロードされません。

---

## 📋 チェックリスト

エピソード公開前の確認事項：

- [ ] 音声ファイルが `data_voice/` に配置されている
- [ ] `.env` ファイルにAPIキーが設定されている
- [ ] `transcribe_podcast.py` が正常に実行された
- [ ] 生成された書き起こしを確認した
- [ ] 誤字があれば `edit_transcript.py` で修正した
- [ ] 修正後の書き起こしを再確認した
- [ ] 書き起こしをGitにコミット・プッシュした
- [ ] Spotifyに音声をアップロードした
- [ ] エピソードを公開した
- [ ] `update_episodes.py` を実行した
- [ ] `episodes.json` をGitにコミット・プッシュした
- [ ] Webサイトで正しく表示されることを確認した

---

## ❓ トラブルシューティング

### Q: transcribe_podcast.pyがエラーになる

**確認事項**:
1. `.env` ファイルが存在するか
2. `GEMINI_API_KEY` が正しく設定されているか
3. `data_voice/` フォルダが存在するか
4. 音声ファイルが配置されているか

### Q: 書き起こしが表示されない

**確認事項**:
1. JSONファイルが `data/transcripts/` に存在するか
2. ファイル名が `ep{エピソード番号}.json` の形式か
3. `episode_number` フィールドが正しいか
4. ブラウザのキャッシュをクリアしたか

### Q: RSSフィードに新しいエピソードが反映されない

**確認事項**:
1. Spotifyで実際に公開されているか
2. 公開から数分待ったか（RSSの更新に時間がかかる場合がある）
3. タイトルに `ep{番号}` が含まれているか

---

## 📚 関連ドキュメント

- [TRANSCRIPT_README.md](TRANSCRIPT_README.md) - 書き起こし管理の詳細
- [SECURITY_GUIDE.md](SECURITY_GUIDE.md) - セキュリティガイド
- [UPDATE_EPISODES_README.md](UPDATE_EPISODES_README.md) - RSSフィード更新の詳細

---

## 🎉 完成！

これで、録音から公開までのワークフローが完成しました。

何か問題があれば、GitHubのIssueで報告してください！

