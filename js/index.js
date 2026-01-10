// index.html用のJavaScript
let app = new Vue({
  el: '#app',
  vuetify: new Vuetify(),
  data: { 
    loading: true,
    latestEpisodes: [],
    platformLinks: CONFIG.platforms,
  },
  methods: {
    async loadEpisodes() {
      try {
        const response = await fetch(CONFIG.paths.episodes);
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
    }
  },
  mounted() {
    this.loadEpisodes();
  }
});

