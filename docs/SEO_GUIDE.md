# SEO対策ガイド

このプロジェクトで実装しているSEO対策の説明です。

## 📋 実装済みのSEO対策

### 1. **メタタグ（Meta Tags）**

#### 基本メタタグ
- `<title>`: 各ページごとに適切なタイトルを設定
- `<meta name="description">`: ページの説明文（120-160文字程度）
- `<meta name="keywords">`: 関連キーワード
- `<link rel="canonical">`: 正規URLを指定

#### 例（index.html）
```html
<title>シビックテック井戸端キャスト - Civictech Idobata Cast | ポッドキャスト</title>
<meta name="description" content="ポッドキャスト文化からシビックテックの入り口を広げたい。シビックテックに関する取り組みや気になるニュースを雑談形式でお届けします。Spotify、Apple Podcasts、YouTubeで配信中。">
<meta name="keywords" content="シビックテック,CivicTech,ポッドキャスト,Code for Japan,地域活性化,オープンデータ,コミュニティ">
```

### 2. **OGP（Open Graph Protocol）**

SNS（Twitter、Facebook等）でシェアされた際に適切なプレビューを表示するためのタグです。

```html
<meta property="og:type" content="website">
<meta property="og:title" content="ページタイトル">
<meta property="og:description" content="ページの説明">
<meta property="og:url" content="https://civictech-idobata-cast.github.io/">
<meta property="og:image" content="https://civictech-idobata-cast.github.io/img/keyvisual.png">
<meta property="og:site_name" content="シビックテック井戸端キャスト">
```

### 3. **Twitter Card**

Twitterでシェアされた際の表示を最適化します。

```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="ページタイトル">
<meta name="twitter:description" content="ページの説明">
<meta name="twitter:image" content="https://civictech-idobata-cast.github.io/img/keyvisual.png">
```

### 4. **構造化データ（JSON-LD）**

検索エンジンがコンテンツを理解しやすくするための構造化データを実装しています。

#### トップページ（PodcastSeries）
```json
{
  "@context": "https://schema.org",
  "@type": "PodcastSeries",
  "name": "シビックテック井戸端キャスト",
  "description": "ポッドキャスト文化からシビックテックの入り口を広げたい...",
  "url": "https://civictech-idobata-cast.github.io/",
  "image": "https://civictech-idobata-cast.github.io/img/keyvisual.png",
  "webFeed": "https://anchor.fm/s/6981b208/podcast/rss"
}
```

#### エピソード詳細ページ（PodcastEpisode）
エピソードごとに動的に生成されます：
- エピソード番号
- タイトル
- 説明文
- 配信日
- 再生時間
- Spotify URL（利用可能な場合）

### 5. **動的メタタグ更新**

エピソード詳細ページでは、JavaScriptでメタタグを動的に更新しています：
- ページタイトル
- 説明文
- OGPタグ
- Twitter Card
- 構造化データ

### 6. **robots.txt**

検索エンジンクローラーへの指示を記載：
```
User-agent: *
Allow: /

Sitemap: https://civictech-idobata-cast.github.io/sitemap.xml
```

## 🔍 SEO対策のベストプラクティス

### タイトルタグ
- ✅ 各ページごとにユニークなタイトルを設定
- ✅ 50-60文字以内
- ✅ 主要キーワードを最初に配置
- ✅ サイト名を含める

### メタ説明文
- ✅ 120-160文字程度
- ✅ 内容を正確に要約
- ✅ 主要キーワードを含める
- ✅ クリックしたくなる魅力的な文章

### キーワード
- ✅ 関連するキーワードを5-10個程度
- ✅ カンマ区切りで記載
- ✅ 過度なキーワード詰め込みは避ける

### 構造化データ
- ✅ Schema.orgの形式に準拠
- ✅ ポッドキャスト用の構造化データ（PodcastSeries, PodcastEpisode）を使用
- ✅ 正しい形式で記述

### URL構造
- ✅ シンプルで分かりやすいURL
- ✅ 日本語URLは避ける（必要に応じてエンコード）
- ✅ canonical URLを設定

## 📈 今後の改善案

### 1. **sitemap.xmlの自動生成**
エピソードが追加されるたびに、sitemap.xmlを自動生成するスクリプトを作成する。

### 2. **パンくずリスト（Breadcrumb）**
構造化データでパンくずリストを実装する。

### 3. **画像の最適化**
- alt属性の充実
- WebP形式の対応
- 画像サイズの最適化

### 4. **ページ速度の最適化**
- 画像の遅延読み込み（lazy loading）
- CSS/JavaScriptの最適化
- CDNの利用

### 5. **モバイル対応**
- レスポンシブデザイン（既に実装済み）
- モバイルフレンドリーテストの確認

## 🛠️ SEOチェックツール

以下のツールでSEO対策を確認できます：

1. **Google Search Console**
   - https://search.google.com/search-console
   - 検索パフォーマンスの確認
   - 構造化データの検証

2. **Google構造化データテストツール**
   - https://search.google.com/test/rich-results
   - 構造化データが正しく認識されているか確認

3. **OGPチェッカー**
   - https://ogp.buta3.net/
   - OGPタグが正しく設定されているか確認

4. **PageSpeed Insights**
   - https://pagespeed.web.dev/
   - ページ速度とモバイル対応を確認

## 📚 参考資料

- [Google検索セントラル](https://developers.google.com/search)
- [Schema.org - Podcast](https://schema.org/PodcastSeries)
- [Open Graph Protocol](https://ogp.me/)
- [Twitter Cards](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/abouts-cards)
