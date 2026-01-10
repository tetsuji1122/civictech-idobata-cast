# 書き起こし管理ガイド

エピソードの書き起こしを別ファイルで管理する方法を説明します。

## 📁 フォルダ構造

```
data/
├── episodes.json              # エピソードのメタデータ
└── transcripts/              # 書き起こし専用フォルダ
    ├── ep1.0.12.json
    ├── ep1.0.11.json
    └── ep1.0.10.json

data_voice/
├── ep1.0.13.m4a              # 処理待ちの音声ファイル
└── backup/                   # 処理済み音声ファイル
    ├── ep1.0.12.m4a
    └── ep1.0.11.m4a
```

## 📄 書き起こしJSONの形式

**ファイル名**: `ep{エピソード番号}.json`  
例: `ep1.0.12.json`

**内容**:
```json
{
  "episode_number": "1.0.12",
  "file_name": "ep1.0.12.m4a",
  "sub_title": "生成AIで猫の気持ちを言語化！Code for Catが挑む「猫エージェント」の最前線",
  "detailed_description": "愛猫が「もし人間の言葉を話せたら？」そんな夢を最新の生成AIが叶えます...",
  "summary": "ポッドキャスト「シビックテック井戸端キャスト」の本放送では...",
  "transcript": "詳細な書き起こしテキスト..."
}
```

### フィールド説明

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `episode_number` | ✅ | エピソード番号（`"1.0.12"`形式） |
| `file_name` | ✅ | 音声ファイル名（`"ep1.0.12.m4a"`形式） |
| `sub_title` | ✅ | エピソードのサブタイトル（AI生成） |
| `detailed_description` | ✅ | エピソードの詳細説明（AI生成、150〜250文字程度） |
| `summary` | ✅ | エピソードの要約（AI生成した詳細なまとめ） |
| `transcript` | ✅ | 書き起こしテキスト（Markdown対応） |

**注**: `detailed_description`は書き起こしJSONのフィールドで、`episodes.json`の`description`とは別のものです。

## 🔄 ワークフロー

### 1. 音声ファイルを配置

録音した音声ファイルを `data_voice` フォルダに配置します：

```
data_voice/
├── ep1.0.12.m4a
└── ep1.0.11.m4a
```

### 2. 書き起こしスクリプトを実行

`transcribe_podcast.py`を使用して書き起こしを自動生成します：

```bash
python transcribe_podcast.py
```

このスクリプトは：
- `data_voice/` フォルダ内の音声ファイルを読み込み
- Gemini APIで書き起こしを生成
- `data/transcripts/` フォルダに直接JSONファイルを保存
- **処理完了後、音声ファイルを `data_voice/backup/` に自動移動**

### 3. GitHubにプッシュ

```bash
git add data/transcripts/ep1.0.12.json
git commit -m "Add transcript for ep1.0.12"
git push
```

**注意**: 音声ファイル（`data_voice/`フォルダ）は`.gitignore`で除外されているため、Gitにアップロードされません。

### 4. Webサイトでの表示

GitHub Pagesが更新されると、エピソード詳細ページで書き起こしが自動的に表示されます。

## 🎯 メリット

### ✅ RSSフィード更新前に書き起こしを追加できる
- エピソードがまだ配信されていなくても書き起こしを準備可能
- RSSフィード更新後、自動的にマッチング

### ✅ ファイルサイズの管理
- `episodes.json`のサイズが大きくなりすぎない
- 書き起こしが必要な時だけ読み込まれる

### ✅ 独立した更新
- エピソードのメタデータと書き起こしを別々に更新できる
- 書き起こしの修正が容易

## 🔍 書き起こしの確認方法

### ブラウザでの確認

1. ローカルサーバーを起動:
   ```bash
   python -m http.server 8000
   ```

2. ブラウザで開く:
   ```
   http://localhost:8000/episode-detail.html?id=1
   ```

3. 「書き起こし全文」セクションを確認

### 書き起こしの有無

- **書き起こしあり**: 「書き起こし全文」セクションが表示される
- **書き起こしなし**: セクション自体が表示されない

## 📝 書き起こしの編集

### Markdownスタイルの使用

書き起こしではMarkdown形式を使用できます：

```markdown
**話者名**: セリフ内容

**00:00 - 00:30**  
イントロダクション部分...

- リスト項目1
- リスト項目2
```

### タイムスタンプの記述

タイムスタンプは以下の形式で記述すると、自動的にハイライト表示されます：

```
**00:00 - 00:30（イントロダクション）**
**石井**: こんにちは...
```

## ⚠️ 注意事項

### エピソード番号の一致

書き起こしファイル名とエピソード番号は必ず一致させてください：

- ✅ 正しい: `ep1.0.12.json` → `"episode_number": "1.0.12"`
- ❌ 間違い: `ep1.0.12.json` → `"episode_number": "1.0.11"`

### ファイル名の形式

- 必ず `ep` で始める
- エピソード番号は `X.X.X` 形式
- 拡張子は `.json`

例: `ep1.0.12.json`, `ep0.23.15.json`

## 🚀 自動化（将来的な拡張）

### GitHub Actionsでの自動デプロイ

```yaml
# .github/workflows/deploy-transcript.yml
name: Deploy Transcript
on:
  push:
    paths:
      - 'data/transcripts/**'
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to GitHub Pages
        # デプロイ処理
```

### 音声認識APIとの連携

将来的には、音声ファイルをアップロードするだけで自動的に書き起こしJSONを生成する仕組みも検討できます。

## 📚 参考

- RSSフィード更新: `python update_episodes.py`
- ローカルサーバー起動: `python -m http.server 8000`

## 🔄 音声ファイルの管理

### 処理前
- `data_voice/` フォルダに音声ファイルを配置
- ファイル名は `epX.X.X.m4a` の形式にする

### 処理後
- 書き起こし完了後、音声ファイルは自動的に `data_voice/backup/` に移動
- 処理に失敗したファイルは移動せず、`data_voice/` に残る
- バックアップフォルダの音声ファイルは `.gitignore` で除外されているため、Gitにアップロードされません

### 処理エラー時の対応
- エラーが発生したファイルは `data_voice/` に残ります
- エラーメッセージを確認して問題を修正後、再実行してください

## ❓ トラブルシューティング

### 書き起こしが表示されない

1. **ファイル名を確認**
   - `data/transcripts/ep1.0.12.json` の形式になっているか？

2. **episode_numberを確認**
   - JSONファイル内の `episode_number` がファイル名と一致しているか？

3. **episodes.jsonにエピソードが存在するか確認**
   - RSSフィード更新: `python update_episodes.py`

4. **ブラウザのコンソールを確認**
   - F12キーを押して、エラーメッセージを確認

### 文字化けする

- JSONファイルのエンコーディングが **UTF-8** になっているか確認
- BOM無しUTF-8を使用してください

---

何か問題があれば、GitHubのIssueで報告してください！

