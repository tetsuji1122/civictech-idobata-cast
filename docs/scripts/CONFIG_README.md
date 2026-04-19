# 共通設定 (config.js)

`js/config.js`には、サイト全体で使用する共通設定が定義されています。

## 📋 設定内容

### ポッドキャスト基本情報
```javascript
CONFIG.podcast = {
  name: 'シビックテック井戸端キャスト',
  nameEn: 'Civictech Idobata Cast',
  shortName: 'Cキャス',
  description: 'ポッドキャスト文化からシビックテックの入り口を広げたい'
}
```

### 配信プラットフォームURL
```javascript
CONFIG.platforms = {
  spotify: 'https://open.spotify.com/show/31JfR2D72gENOfOwq3AcKw',
  applePodcasts: 'https://podcasts.apple.com/jp/podcast/...',
  youtube: 'https://www.youtube.com/@civictechcast',
  rssFeed: 'https://anchor.fm/s/6981b208/podcast/rss'
}
```

### データパス
```javascript
CONFIG.paths = {
  episodes: 'data/episodes.json',
  transcripts: 'data/transcripts/',
  images: 'img/'
}
```

### ページネーション設定
```javascript
CONFIG.pagination = {
  itemsPerPage: 20,           // 1ページあたりのアイテム数
  latestItemsOnTop: 3         // トップページに表示する最新エピソード数
}
```

### カラー設定
```javascript
CONFIG.colors = {
  primary: '#003049',
  accent: '#FFC300',
  spotify: '#1DB954'
}
```

---

## 🚀 使い方

### HTMLでの読み込み

各HTMLファイルで、Vue.jsの前に`config.js`を読み込んでください：

```html
<script src="https://cdn.jsdelivr.net/npm/vue@2.x/dist/vue.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vuetify@2.x/dist/vuetify.js"></script>
<script src="js/config.js"></script>
<script src="js/your-script.js"></script>
```

### JavaScriptでの使用

#### データとして定義
```javascript
new Vue({
  el: '#app',
  data: {
    platformLinks: CONFIG.platforms
  }
});
```

#### メソッド内で使用
```javascript
methods: {
  async loadEpisodes() {
    const response = await fetch(CONFIG.paths.episodes);
    // ...
  }
}
```

### HTMLテンプレートでの使用

Vue.jsのデータバインディングで使用：

```html
<v-btn :href="platformLinks.spotify" target="_blank">
  Spotifyで聴く
</v-btn>
```

---

## 📝 設定の変更方法

### プラットフォームURLの変更

`js/config.js`を編集：

```javascript
CONFIG.platforms = {
  spotify: 'https://your-new-spotify-url',
  // ...
}
```

すべてのページで自動的に反映されます。

### エピソード表示数の変更

```javascript
CONFIG.pagination = {
  itemsPerPage: 30,        // 20 → 30 に変更
  latestItemsOnTop: 5      // 3 → 5 に変更
}
```

---

## ✅ この設定を使用しているファイル

| ファイル | 使用している設定 |
|---------|----------------|
| `index.html` | `platforms` |
| `index.js` | `platforms`, `paths.episodes`, `pagination.latestItemsOnTop` |
| `episodes.html` | なし（JSで使用） |
| `episodes.js` | `paths.episodes`, `pagination.itemsPerPage` |
| `episode-detail.html` | なし（JSで使用） |
| `episode-detail.js` | `paths.episodes`, `paths.transcripts` |
| `about.html` | `platforms` |
| `about.js` | `platforms` |

---

## 💡 メリット

### 1. **一元管理**
URLやパスを1箇所で管理できるため、変更時の修正が容易です。

### 2. **タイポ防止**
ハードコードされたURLがなくなり、タイプミスを防げます。

### 3. **保守性向上**
設定ファイルを見るだけで、サイト全体の構成が把握できます。

### 4. **環境切り替え**
開発環境と本番環境で異なる設定を簡単に切り替えられます（将来的に）。

---

## ⚠️ 注意事項

- `config.js`は必ずVue.jsの**後**、各ページスクリプトの**前**に読み込んでください
- グローバル変数`CONFIG`として公開されるため、他のスクリプトから直接参照できます
- 設定を変更した場合、ブラウザのキャッシュをクリアしてください

