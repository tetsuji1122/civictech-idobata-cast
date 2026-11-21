# civictech-idobata-cast

シビックテック井戸端キャストの公式ホームページとオープンデータ基盤

## 🎙️ プロジェクト概要

ポッドキャスト文化からシビックテックの入り口を広げる、音声メディアプロジェクトです。
全エピソードのメタデータ、AI書き起こし全文、および発話単位にセグメント化されたデータをオープンデータとして公開しています。

- **配信**: Spotify / Apple Podcasts / YouTube
- **サイト**: GitHub Pages（https://civictech-idobata-cast.github.io/ または https://idobatacast.com/）
- **技術**: Vue.js + Vuetify（静的サイト）
- **オープンデータ**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ja)（詳細は [DATA.md](DATA.md) 参照）

---

## 📊 オープンデータについて

本サイトで公開するエピソードデータ、書き起こしテキスト、発話セグメントおよび派生データは、**クリエイティブ・コモンズ 表示 4.0 国際ライセンス（CC BY 4.0）**のもとで自由に利用できます。

- **収録期間**: 2021-09-08 〜（継続配信中）
- **規模**: 680話以上、総再生時間 約134時間、総発話数 4万件以上（約270万字）
- **データ仕様・構造**: [DATA.md](DATA.md) をご覧ください。

---

## 📁 フォルダ構成

```
civictech-idobata-cast/
├── index.html              # トップページ
├── episodes.html           # エピソード一覧
├── episode-detail.html     # エピソード詳細（発話リスト表示・アンカー対応）
├── search.html             # 発話検索・言葉の年表
├── about.html              # このポッドキャストについて
├── countdowntimer.html     # 収録用タイマー
├── DATA.md                 # オープンデータ仕様書
│
├── js/                     # JavaScript
│   ├── config.js          # 共通設定
│   ├── utils.js           # 共通ユーティリティ
│   ├── index.js           # トップページ用
│   ├── episodes.js        # エピソード一覧用
│   ├── episode-detail.js  # エピソード詳細用
│   ├── search.js          # 発話検索・言葉の年表用
│   └── about.js           # Aboutページ用
│
├── css/                    # スタイルシート
├── img/                    # 画像
├── se/                     # 効果音
│
├── data/                   # データファイル
│   ├── episodes.json           # エピソード情報一覧
│   ├── search-index-*.json     # 発話検索用インデックス（年別）
│   ├── word-chronology.json    # 言葉の年表データ
│   └── transcripts/            # 書き起こしJSON（発話セグメント含む）
│
├── scripts/                # Pythonスクリプト
│   ├── transcribe_podcast.py       # 音声書き起こし（セグメント自動生成）
│   ├── edit_transcript.py          # 書き起こし・セグメント編集（GUI）
│   ├── update_episodes.py          # エピソード更新
│   ├── convert_segments.py         # 既存書き起こしのセグメント一括変換
│   ├── generate_search_index.py    # 年別検索インデックス生成
│   ├── generate_word_chronology.py # 言葉の年表データ生成
│   └── segments_util.py            # 発話セグメント化共通モジュール
│
└── docs/                   # ドキュメント
    ├── README.md                   # ドキュメント索引
    ├── scripts/                    # スクリプト関連ガイド
    ├── workflow/                   # 運用・更新ワークフロー
    ├── reference/                  # セキュリティ・SEOガイド
    └── x-bot/                      # X自動投稿ボット設定
```

---

## 🚀 スクリプトの使い方

### エピソード更新

```bash
python scripts/update_episodes.py
```

### 音声書き起こし（新規エピソード）

```bash
python scripts/transcribe_podcast.py
```

### 書き起こし・セグメント編集（GUI）

```bash
python scripts/edit_transcript.py
```

### 検索インデックス生成

```bash
python scripts/generate_search_index.py
```

### 言葉の年表データ生成

```bash
python scripts/generate_word_chronology.py
```

詳細は [docs/scripts/SCRIPTS_README.md](docs/scripts/SCRIPTS_README.md) をご覧ください。

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

---

## 🔧 開発

### ローカルサーバー起動

```bash
python -m http.server 8000
```

ブラウザで `http://localhost:8000` にアクセス

### 必要な環境

- Python 3.8+
- 依存ライブラリ: `pip install -r requirements.txt`
- 環境変数: `.env` ファイル（書き起こし機能を使う場合）

---

## 📚 ドキュメント

- [データ仕様書（DATA.md）](DATA.md)
- [ドキュメント索引（docs/README.md）](docs/README.md)

---

## 🌐 リンク

- [GitHub リポジトリ](https://github.com/tetsuji1122/civictech-idobata-cast)
- [Spotify](https://open.spotify.com/show/31JfR2D72gENOfOwq3AcKw)
- [Apple Podcasts](https://podcasts.apple.com/jp/podcast/id1587297171)
- [YouTube](https://www.youtube.com/@civictechcast)

