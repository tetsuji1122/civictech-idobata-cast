# エピソード更新スクリプト

RSSフィードからポッドキャストのエピソード情報を自動取得して `data/episodes.json` を更新するPythonスクリプトです。

## 📦 必要な環境

- Python 3.7以上
- pip（Pythonパッケージマネージャー）

## 🔧 セットアップ

### 1. 必要なライブラリをインストール

```bash
pip install -r requirements.txt
```

または個別にインストール:

```bash
pip install feedparser requests python-dateutil
```

## 🚀 使い方

### 基本的な使い方（推奨）

```bash
python scripts/update_episodes.py
```

これで、RSSフィード（https://anchor.fm/s/6981b208/podcast/rss）から**最新20件**のエピソードをチェックし、新しいものだけを `data/episodes.json` に追加します。

> 💡 **効率的！** デフォルトで最新20件だけをチェックするため、処理が高速です。既存のエピソードは重複して追加されません。

### オプション

#### 最新の数件だけチェック（カスタム件数）

```bash
python scripts/update_episodes.py --limit 10
```

最新10件のエピソードだけをチェックします。通常の更新では、5〜20件で十分です。

#### 全エピソードを取得（初回セットアップ時）

```bash
python scripts/update_episodes.py --all
```

または

```bash
python scripts/update_episodes.py --limit 0
```

RSSフィードのすべてのエピソードを取得します。初回セットアップ時や、全データを再構築したい場合に使用します。

> 💡 **全件実行の効果**: `--all` を使用すると、既存エピソードのSpotify URLと関連リンクも更新されます。

#### Dry Run モード（実際には保存しない）

```bash
python scripts/update_episodes.py --dry-run
```

取得したエピソード情報を表示するだけで、実際にはファイルを更新しません。初めて実行する前に確認することをおすすめします。

#### 出力先を変更

```bash
python scripts/update_episodes.py --output test_episodes.json
```

デフォルトの `data/episodes.json` ではなく、別のファイルに保存します。

## 💡 使用シナリオ

### シナリオ1: 定期的な更新（推奨）

新しいエピソードが配信されたら、以下のコマンドを実行するだけ：

```bash
python scripts/update_episodes.py
```

- ✅ 最新20件だけチェックするので**高速**
- ✅ 新しいエピソードだけ追加される
- ✅ 既存データは上書きされない
- ✅ Spotify URLも自動取得
- ✅ 説明文のURLを自動抽出して関連リンクに保存

### シナリオ2: 初回セットアップ

最初にすべてのエピソードを取得する場合：

```bash
# まず確認
python scripts/update_episodes.py --all --dry-run

# 問題なければ実行
python scripts/update_episodes.py --all
```

### シナリオ3: 大量配信後の更新

1週間で30本配信したような場合：

```bash
python scripts/update_episodes.py --limit 50
```

通常より多めに取得範囲を広げます。

### シナリオ4: Spotify URLと関連リンクの一括更新

既存の全エピソードに対して、Spotify URLと関連リンクを更新する場合：

```bash
# 全件チェックして更新
python scripts/update_episodes.py --all
```

出力例：
```
[UPDATE] 1.0.16: Spotify URL更新
→ 0.23.22: 説明文から1個のURLを抽出（関連リンク: 1個）
[UPDATE] 0.23.22: 関連リンク追加（1件）
...
[INFO] 新規エピソード: 0件
[INFO] Spotify URL更新: 232件
[INFO] 関連リンク追加: 185件
```

### シナリオ5: トラブルシューティング

データに問題がある場合、全データを再構築：

```bash
# 既存ファイルを退避
mv data/episodes.json data/episodes.json.old

# 全件取得で再構築
python scripts/update_episodes.py --all
```

## 📋 実行例

### 通常の更新（新しいエピソードをチェック）

```bash
python scripts/update_episodes.py
```

出力例（新規エピソードあり）:
```
[PODCAST] シビックテック井戸端キャスト - エピソード更新スクリプト
============================================================
[INFO] RSSフィードを取得中: https://anchor.fm/s/6981b208/podcast/rss
[INFO] 最新20件のエピソードをチェックします
  → Spotify URL取得: https://podcasters.spotify.com/...
[OK] 3件のエピソードを取得しました
[INFO] 既存エピソード: 593件
[INFO] 新規エピソード: 3件
[INFO] 既存エピソード（スキップ）: 0件
[BACKUP] バックアップを作成: data/episodes.json.backup
[OK] data/episodes.json に保存しました

============================================================
[SUCCESS] 完了しました！
  新規追加: 3件
  既存スキップ: 0件
  合計エピソード数: 596件
============================================================
```

出力例（新規エピソードなし）:
```
[PODCAST] シビックテック井戸端キャスト - エピソード更新スクリプト
============================================================
[INFO] RSSフィードを取得中: https://anchor.fm/s/6981b208/podcast/rss
[INFO] 最新20件のエピソードをチェックします
[OK] 20件のエピソードを取得しました
[INFO] 既存エピソード: 593件
[INFO] 新規エピソード: 0件
[INFO] 既存エピソード（スキップ）: 20件
[INFO] 新しいエピソードはありません

============================================================
[INFO] 更新する内容がないため、保存をスキップしました
============================================================
```

### 初回セットアップ（全エピソードを取得）

```bash
python scripts/update_episodes.py --all --dry-run
```

出力例:
```
[PODCAST] シビックテック井戸端キャスト - エピソード更新スクリプト
============================================================
[INFO] RSSフィードを取得中: https://anchor.fm/s/6981b208/podcast/rss
[INFO] 全790件のエピソードをチェックします
[OK] 790件のエピソードを取得しました
[INFO] data/episodes.json が存在しないため、新規作成します
[INFO] 既存エピソード: 0件
[INFO] 新規エピソード: 790件
[INFO] 既存エピソード（スキップ）: 0件

[DRY-RUN] 実際には保存しません

保存される内容のプレビュー:
{
  "episodes": [
    {
      "id": 1,
      "number": "1.0.16",
      "title": "ep1.0.16 2025年エピソードランキング",
      ...
    }
  ]
}

... 他 787件のエピソード
============================================================
✨ 完了しました！
```

### 実際に更新

```bash
python scripts/update_episodes.py
```

### 最新10件だけ更新

```bash
python scripts/update_episodes.py --limit 10
```

## 🔄 定期実行

### Windowsの場合（タスクスケジューラ）

1. タスクスケジューラを開く
2. 「基本タスクの作成」を選択
3. トリガー: 毎日または毎週
4. 操作: `python scripts/update_episodes.py` を実行

### macOS/Linuxの場合（cron）

```bash
# crontabを編集
crontab -e

# 毎日午前9時に実行
0 9 * * * cd /path/to/civictech-idobata-cast && python scripts/update_episodes.py
```

## 📝 取得される情報

RSSフィードから以下の情報を自動取得します:

- **エピソード番号**: タイトルから抽出（例: ep1.0.16 → "1.0.16"）
- **タイトル**: エピソードのタイトル
- **配信日**: YYYY-MM-DD形式
- **再生時間**: MM:SS形式
- **概要**: エピソードの説明文（HTMLタグとURLを削除）
- **タグ**: タイトルと説明文から自動生成
- **サムネイル**: デフォルトで `img/logo.png`
- **SpotifyURL**: 個別エピソードのURL（利用可能な場合）
- **関連リンク**: 説明文から自動抽出されたURL（Spotify/Anchor以外）

### 🔗 関連リンクの自動抽出

エピソードの説明文にURLが含まれている場合、自動的に抽出して `links` フィールドに保存します。

**抽出されるURL:**
- `http://` または `https://` で始まるURL
- 説明文から抽出後、本文からは削除されます

**除外されるURL:**
- `spotify.com` - SpotifyのURLは `spotifyUrl` フィールドに保存
- `anchor.fm` - Anchorの内部リンク
- `cloudfront.net` - CDNのURL

**例:**
```json
{
  "number": "0.23.22",
  "title": "ep0.23.22 Code for Japan Summit2025",
  "description": "イベント紹介です。11/29にCode for Japan Summitが開催されます。",
  "links": [
    {
      "title": "関連リンク",
      "url": "https://summit.code4japan.org/"
    }
  ]
}
```

詳細ページでは、関連リンクがSpotifyボタンの上に自動的に表示されます。

## 🔄 既存エピソードの更新

新しいエピソードを追加するだけでなく、既存エピソードの情報も必要に応じて更新します。

### Spotify URLの更新

既存のエピソードが **番組全体のURL** を使用していて、RSSフィードに **個別エピソードのURL** がある場合、自動的に更新されます。

**更新対象:**
- 既存URL: `https://open.spotify.com/show/31JfR2D72gENOfOwq3AcKw`（番組URL）
- 新しいURL: `https://podcasters.spotify.com/pod/show/civictechcast/episodes/...`（個別エピソードURL）

**実行例:**
```bash
python scripts/update_episodes.py --all
```

出力:
```
[UPDATE] 1.0.16: Spotify URL更新
[UPDATE] 1.0.15: Spotify URL更新
...
[INFO] Spotify URL更新: 232件
```

### 関連リンクの追加

既存のエピソードに `links` フィールドが空（または存在しない）で、RSSフィードの説明文にURLが含まれている場合、自動的に追加されます。

**実行例:**
```bash
python scripts/update_episodes.py --all
```

出力:
```
→ 0.23.22: 説明文から1個のURLを抽出（関連リンク: 1個）
[UPDATE] 0.23.22: 関連リンク追加（1件）
...
```

### 更新の仕組み

スクリプトは以下の優先順位で処理します：

1. **新規エピソードの追加** - RSSフィードにあり、`episodes.json` にない
2. **Spotify URLの更新** - 既存が番組URLで、新しく個別URLが取得できた場合
3. **関連リンクの追加** - 既存に `links` が空で、新しくURLが抽出できた場合
4. **スキップ** - 上記に該当しない既存エピソード

> ⚠️ **注意**: 既存の `description`、`title`、`tags` などは上書きされません。これらを更新したい場合は、`episodes.json` を直接編集するか、該当エピソードを削除してから再実行してください。

## 🏷️ タグの自動生成

統一された **10個のタグ** から、エピソードの内容に合わせて最大3個まで自動的に付与されます:

### 統一タグ一覧

| タグ | キーワード例 |
|------|-------------|
| 🎤 **ゲスト** | ゲスト、突撃、Quiet Talk、メンバーファイル |
| 🏛️ **シビックテック** | シビックテック、CivicTech |
| 🌸 **Code for** | Code for、Summit、ブリゲード、コミュニティ |
| 🎉 **イベント** | イベント、ふりかえり、ランキング、Advent Calendar |
| 📊 **データ** | データ、オープンデータ、API、統計、プラットフォーム |
| 💻 **技術** | AI、GPT、Sora、システム、アプリ、GitHub、プログラミング |
| 🗾 **地域** | 地域、富山、長崎、東京、金沢、都市 |
| ☕ **ライフスタイル** | お店、グルメ、日本酒、おいしい、買ってよかった |
| 📚 **文化** | 歴史、文化、社会、教育 |
| 💬 **雑談** | 雑談、予想、占う |

### タグ付与の優先順位

1. ゲスト（ゲスト出演回を優先）
2. イベント
3. Code for
4. シビックテック
5. データ
6. 技術
7. 地域
8. ライフスタイル
9. 文化
10. 雑談（デフォルト）

キーワードがない場合は `雑談` タグが付きます。

## ⚙️ カスタマイズ

スクリプト内の設定を変更することで、動作をカスタマイズできます:

```python
# scripts/update_episodes.py の先頭部分

RSS_FEED_URL = "https://anchor.fm/s/6981b208/podcast/rss"  # RSSフィードURL
EPISODES_JSON_PATH = "data/episodes.json"  # 出力先
SPOTIFY_SHOW_URL = "https://open.spotify.com/show/31JfR2D72gENOfOwq3AcKw"  # SpotifyショーURL
DEFAULT_THUMBNAIL = "img/logo.png"  # デフォルトのサムネイル画像
```

### URLの抽出ルール

関連リンクとして抽出されるURLのルールをカスタマイズする場合:

```python
# extract_urls_from_text() 関数内
url_pattern = r'https?://[^\s<>"\'\)]+[^\s<>"\'\.,:;\)\]\}]'  # URLパターン

# merge_episodes() 関数内
# 除外するドメインを追加
if 'spotify.com' not in url and 'anchor.fm' not in url and 'cloudfront.net' not in url:
    # 除外したいドメインを追加可能
```

## 🔒 バックアップ

スクリプトは実行時に自動的にバックアップを作成します:

- `data/episodes.json.backup` に既存ファイルがコピーされます

## ❓ トラブルシューティング

### エラー: `ModuleNotFoundError: No module named 'feedparser'`

```bash
pip install feedparser
```

### エラー: RSSフィードの取得に失敗

- インターネット接続を確認してください
- RSSフィードのURL（https://anchor.fm/s/6981b208/podcast/rss）が有効か確認してください

### エピソード番号が取得できない

タイトルに `ep1.0.16` のような形式のエピソード番号が含まれていることを確認してください。

## 📚 参考情報

- RSSフィード: https://anchor.fm/s/6981b208/podcast/rss
- Spotify: https://open.spotify.com/show/31JfR2D72gENOfOwq3AcKw
- Apple Podcasts: https://podcasts.apple.com/jp/podcast/id1587297171

