// シビックテック井戸端キャスト - 共通設定
const CONFIG = {
  // サイトURL（カスタムドメイン取得時はここを変更）
  siteUrl: 'https://tetsuji1122.github.io/civictech-idobata-cast',
  
  // ポッドキャスト基本情報
  podcast: {
    name: 'シビックテック井戸端キャスト',
    nameEn: 'Civictech Idobata Cast',
    shortName: 'Cキャス',
    description: 'ポッドキャスト文化からシビックテックの入り口を広げたい'
  },
  
  // 配信プラットフォームURL
  platforms: {
    spotify: 'https://open.spotify.com/show/31JfR2D72gENOfOwq3AcKw',
    applePodcasts: 'https://podcasts.apple.com/jp/podcast/%E3%82%B7%E3%83%93%E3%83%83%E3%82%AF%E3%83%86%E3%83%83%E3%82%AF%E4%BA%95%E6%88%B8%E7%AB%AF%E3%82%AD%E3%83%A3%E3%82%B9%E3%83%88/id1587297171',
    youtube: 'https://www.youtube.com/@civictechcast',
    rssFeed: 'https://anchor.fm/s/6981b208/podcast/rss'
  },
  
  // 外部サイトURL
  externalLinks: {
    twitter: 'https://twitter.com/civictechcast',
    github: 'https://github.com/tetsuji1122/civictech-idobata-cast',
    creativeCommons: 'https://creativecommons.org/licenses/by/4.0/deed.ja',
    creativeCommonsBadge: 'https://i.creativecommons.org/l/by/4.0/88x31.png'
  },
  
  // データパス
  paths: {
    episodes: 'data/episodes.json',
    transcripts: 'data/transcripts/',
    images: 'img/'
  },
  
  // デフォルト画像
  defaultImage: 'img/logo.png',
  
  // ページネーション/ロード設定
  pagination: {
    itemsPerPage: 20,  // 1ページ/1回のロードあたりのアイテム数
    latestItemsOnTop: 3  // トップページに表示する最新エピソード数
  },
  
  // カラー設定
  colors: {
    primary: '#003049',
    accent: '#FFC300',
    spotify: '#1DB954'
  }
};

// グローバルに公開
if (typeof window !== 'undefined') {
  window.CONFIG = CONFIG;
}

