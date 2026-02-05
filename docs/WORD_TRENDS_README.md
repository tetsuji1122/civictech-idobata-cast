# 頻出ワード年表機能

書き起こしデータから年別の頻出ワードを抽出し、年表形式で表示する機能です。

## 📋 概要

全エピソードの書き起こしデータを年別に集計し、以下の情報を可視化します：

- **頻出ワードTop10**: その年に最も多く出現した単語
- **前年比増加ワード**: 前年と比較して増加した単語
- **新規登場ワード**: その年に初めて出現した単語
- **単語ネットワーク**: 共起関係をネットワークで表示
- **センチメント推移**: 年ごとの感情スコア推移
- **エピソード間類似度**: 類似エピソードのリスト表示

## 📦 必要な環境

- Python 3.7以上
- MeCab（形態素解析エンジン）
- 以下のPythonパッケージ:
  - `mecab-python3`: MeCabのPythonバインディング
  - `unidic-lite`: 軽量なMeCab辞書
  - `scikit-learn`: 類似度計算（TF-IDF + コサイン類似度）

## 🔧 セットアップ

### 1. 必要なライブラリをインストール

```bash
pip install -r requirements.txt
```

または個別にインストール:

```bash
pip install mecab-python3 unidic-lite scikit-learn
```

### 2. MeCabの動作確認

```bash
python -c "import MeCab; print('MeCab is available')"
```

正常に動作することを確認してください。

## 🚀 使い方

### 年表データの生成

```bash
python scripts/analyze_word_trends.py
```

このスクリプトは以下の処理を実行します：

1. `data/episodes.json` からエピソード情報を読み込み
2. 各エピソードの書き起こしデータ（`data/transcripts/`）を読み込み
3. MeCabを使用して形態素解析を実行
4. 年別に頻出ワードを集計
5. 前年比の増加ワードと新規登場ワードを計算
6. センチメント推移を集計
7. 単語ネットワークを作成
8. エピソード間類似度を計算
9. `data/word-trends.json` ほかに結果を出力

### 出力ファイル

生成されるファイル:

- `data/word-trends.json`: 年別頻出ワード
- `data/episode-insights.json`: エピソード別の洞察データ
- `data/sentiment-trends.json`: 年別センチメント推移
- `data/word-network.json`: 年別単語ネットワーク
- `data/sentiment_lexicon.json`: センチメント辞書（手動調整用）

`data/word-trends.json` の構造：

```json
{
  "generated_at": "2026-01-22T05:34:29.324134",
  "trends": [
    {
      "year": 2021,
      "episodeCount": 50,
      "totalWords": 997,
      "topWords": [
        {
          "word": "桑原",
          "count": 123
        },
        ...
      ],
      "risingWords": [
        {
          "word": "岐阜",
          "delta": 246
        },
        ...
      ],
      "newWords": ["桑原", "岐阜", ...]
    },
    ...
  ]
}
```

## 📊 年表ページの表示

生成されたデータは `word-trends.html` で表示されます。

### アクセス方法

1. ローカルサーバーを起動:
   ```bash
   python -m http.server 8000
   ```

2. ブラウザでアクセス:
   ```
   http://localhost:8000/word-trends.html
   ```

### 機能

- **年選択**: 特定の年のデータのみを表示
- **表示基準**: 頻出数、特徴度(TF-IDF)、前年差分から選択（可視化の切替用）
- **前年との差分表示**: 増加ワードと新規登場ワードの表示/非表示を切り替え
- **タグ・検索フィルタ**: ダッシュボード全体の絞り込み
- **単語ネットワーク**: 共起関係の可視化
- **センチメント推移**: 年ごとの平均スコア推移
- **エピソード類似度**: 基準回に近いエピソードの表示

## 🔍 単語抽出の仕様

### 抽出対象

- **品詞**: 名詞のみ
- **種類**: 固有名詞、一般名詞、サ変接続名詞
- **除外**: 代名詞、非自立、接尾

### ストップワード

以下の単語は除外されます：

- 助詞・助動詞（「こと」「もの」「ため」など）
- 会話でよく使われるフレーズ（「ありがとうございました」「なるほど」など）
- 番組固有の用語（「いどばた」「井戸端」「キャスト」など）
- 人名（「石井」「太田」「小俣」など）
- 時間・数字（「分」「秒」「時」「日」「月」「年」など）

### フィルタリング条件

- 単語の長さ: 2文字以上10文字以下
- 最低出現回数: 3回以上
- 数字のみの単語は除外

## ⚙️ カスタマイズ

### ストップワードの追加

`scripts/analyze_word_trends.py` の `STOP_WORDS` セットに単語を追加:

```python
STOP_WORDS = {
    # 既存のストップワード...
    '新しい単語',  # 追加
}
```

### 抽出する品詞の変更

`extract_words_mecab()` 関数内で品詞フィルタを変更:

```python
# 名詞のみを抽出
if pos == '名詞':
    # 条件を変更
```

### 表示する単語数の変更

`analyze_word_trends()` 関数内で変更:

```python
# 頻出ワードTop10を取得
top_words = [
    ...
][:10]  # この数字を変更（例: [:20] でTop20）
```

## 🐛 トラブルシューティング

### MeCabが動作しない

**エラー**: `Failed initializing MeCab`

**解決方法**:
1. `unidic-lite` がインストールされているか確認:
   ```bash
   pip install unidic-lite
   ```

2. MeCab本体が必要な場合（Windows）:
   - [MeCab公式サイト](https://taku910.github.io/mecab/)からインストーラーをダウンロード
   - または `mecab-python3` の最新版を使用

### 書き起こしデータが見つからない

**エラー**: `エラー: data/transcripts/ が見つかりません`

**解決方法**:
- `data/transcripts/` ディレクトリが存在することを確認
- 書き起こしデータが正しい形式で保存されているか確認

### メモリ不足

大量の書き起こしデータを処理する場合、メモリ不足が発生する可能性があります。

**解決方法**:
- 年ごとに処理を分割
- バッチサイズを小さくする

## 📝 注意事項

1. **処理時間**: 全エピソードの処理には数分かかる場合があります
2. **データ更新**: 新しいエピソードが追加されたら、年表データを再生成してください
3. **MeCabの精度**: MeCabの形態素解析の精度により、一部の単語が正しく抽出されない場合があります

## 🔄 自動更新

GitHub Actionsなどで自動更新する場合、`.github/workflows/` にワークフローを追加できます。

例:

```yaml
name: Update Word Trends

on:
  schedule:
    - cron: '0 0 * * 0'  # 毎週日曜日の0時
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python scripts/analyze_word_trends.py
      - run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add data/word-trends.json
          git commit -m "Update word trends" || exit 0
          git push
```

## 📚 関連ドキュメント

- [書き起こし機能](./TRANSCRIPT_README.md): 書き起こしデータの生成方法
- [エピソード更新](./UPDATE_EPISODES_README.md): エピソードデータの更新方法
- [スクリプト一覧](./SCRIPTS_README.md): その他のスクリプト

## 🆘 サポート

問題が発生した場合は、以下を確認してください：

1. Pythonのバージョン（3.7以上）
2. 必要なパッケージのインストール状況
3. 書き起こしデータの存在と形式
4. MeCabの動作状況

---

最終更新: 2026-01-22
