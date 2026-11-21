// index.html用のJavaScript
const config = (typeof CONFIG !== 'undefined' ? CONFIG : (typeof window !== 'undefined' && window.CONFIG ? window.CONFIG : null)) || {
  podcast: {
    name: 'シビックテック井戸端キャスト',
    nameEn: 'Civictech Idobata Cast',
    shortName: 'Cキャス',
    description: 'ポッドキャスト文化からシビックテックの入り口を広げたい'
  },
  platforms: {
    spotify: 'https://open.spotify.com/show/31JfR2D72gENOfOwq3AcKw',
    applePodcasts: 'https://podcasts.apple.com/jp/podcast/%E3%82%B7%E3%83%93%E3%83%83%E3%82%AF%E3%83%86%E3%83%83%E3%82%AF%E4%BA%95%E6%88%B8%E7%AB%AF%E3%82%AD%E3%83%A3%E3%82%B9%E3%83%88/id1587297171',
    youtube: 'https://www.youtube.com/@civictechcast',
    rssFeed: 'https://anchor.fm/s/6981b208/podcast/rss'
  },
  externalLinks: {
    twitter: 'https://twitter.com/civictechcast',
    github: 'https://github.com/tetsuji1122/civictech-idobata-cast'
  },
  paths: {
    episodes: 'data/episodes.json',
    transcripts: 'data/transcripts/',
    images: 'img/'
  },
  pagination: {
    itemsPerPage: 20,
    latestItemsOnTop: 3
  },
  siteUrl: 'https://tetsuji1122.github.io/civictech-idobata-cast'
};

let app = new Vue({
  el: '#app',
  vuetify: new Vuetify(),
  data: { 
    loading: true,
    latestEpisodes: [],
    platformLinks: config.platforms,
    externalLinks: config.externalLinks,
    drawer: false, // ハンバーガーメニューの開閉状態
  },
  methods: {
    async loadEpisodes() {
      try {
        const response = await fetchWithoutCache(config.paths.episodes);
        const data = await response.json();
        // 日付順にソートして最新3件を取得
        const sortedEpisodes = [...data.episodes].sort((a, b) => {
          return new Date(b.date) - new Date(a.date);
        });
        this.latestEpisodes = sortedEpisodes.slice(0, config.pagination.latestItemsOnTop);
        this.loading = false;
      } catch (error) {
        console.error('エピソードデータの読み込みに失敗しました:', error);
        this.loading = false;
      }
    },
    scrollToContent() {
      const target = document.getElementById('latest-episodes');
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    },
    goToDetail(episodeId) {
      // トップ画面から詳細ページに移動する場合は、エピソード一覧のフィルター状態をクリア
      sessionStorage.removeItem('episodeFilterState');
      sessionStorage.removeItem('filteredEpisodeNumbers');
      // 詳細ページに遷移
      window.location.href = `episode-detail.html?id=${episodeId}`;
    },
    updateMetaTags() {
      // メタタグを動的に更新
      const siteUrl = config.siteUrl;
      
      // canonical URL
      setLinkTag('canonical', `${siteUrl}/index.html`);
      
      // OGP
      setMetaProperty('og:url', `${siteUrl}/`);
      setMetaProperty('og:image', `${siteUrl}/img/keyvisual.png`);
      
      // Twitter Card
      setMetaTag('twitter:image', `${siteUrl}/img/keyvisual.png`);
      
      // 構造化データのURLを更新
      const structuredDataScript = document.querySelector('script[type="application/ld+json"]');
      if (structuredDataScript) {
        try {
          const data = JSON.parse(structuredDataScript.textContent);
          data.url = `${siteUrl}/`;
          data.image = `${siteUrl}/img/keyvisual.png`;
          structuredDataScript.textContent = JSON.stringify(data, null, 2);
        } catch (error) {
          console.error('構造化データの更新に失敗しました:', error);
        }
      }
    }
  },
  mounted() {
    this.loadEpisodes();
    this.updateMetaTags();
  }
});


