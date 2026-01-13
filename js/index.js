// index.html用のJavaScript
let app = new Vue({
  el: '#app',
  vuetify: new Vuetify(),
  data: { 
    loading: true,
    latestEpisodes: [],
    platformLinks: CONFIG.platforms,
    externalLinks: CONFIG.externalLinks,
    drawer: false, // ハンバーガーメニューの開閉状態
  },
  methods: {
    async loadEpisodes() {
      try {
        const response = await fetchWithoutCache(CONFIG.paths.episodes);
        const data = await response.json();
        // 日付順にソートして最新3件を取得
        const sortedEpisodes = [...data.episodes].sort((a, b) => {
          return new Date(b.date) - new Date(a.date);
        });
        this.latestEpisodes = sortedEpisodes.slice(0, CONFIG.pagination.latestItemsOnTop);
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
      const siteUrl = CONFIG.siteUrl;
      
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

