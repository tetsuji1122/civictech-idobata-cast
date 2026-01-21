// word-trends.html用のJavaScript（サンプル表示）
new Vue({
  el: '#app',
  vuetify: new Vuetify(),
  data: {
    drawer: false,
    externalLinks: CONFIG.externalLinks,
    selectedYear: null,
    selectedMetric: '頻出数',
    showDelta: true,
    trends: [
      {
        year: 2021,
        episodeCount: 18,
        totalWords: 68000,
        topWords: [
          { word: 'オープンデータ', count: 320 },
          { word: '行政', count: 290 },
          { word: '地域', count: 260 },
          { word: 'コミュニティ', count: 240 },
          { word: '参加', count: 210 }
        ],
        risingWords: [
          { word: 'コロナ', delta: 24 },
          { word: 'オンライン', delta: 18 },
          { word: '政策', delta: 12 }
        ],
        newWords: ['ワクチン', 'リモート', 'デジタル庁']
      },
      {
        year: 2022,
        episodeCount: 26,
        totalWords: 92000,
        topWords: [
          { word: 'デジタル', count: 380 },
          { word: '官民連携', count: 340 },
          { word: '市民', count: 300 },
          { word: 'オープンデータ', count: 290 },
          { word: '防災', count: 250 }
        ],
        risingWords: [
          { word: '官民連携', delta: 35 },
          { word: '防災', delta: 22 },
          { word: '利活用', delta: 16 }
        ],
        newWords: ['災害', 'DX', '連携協定']
      },
      {
        year: 2023,
        episodeCount: 31,
        totalWords: 118000,
        topWords: [
          { word: 'DX', count: 420 },
          { word: 'データ連携', count: 370 },
          { word: '公共', count: 310 },
          { word: '共創', count: 280 },
          { word: 'まちづくり', count: 260 }
        ],
        risingWords: [
          { word: 'データ連携', delta: 40 },
          { word: '共創', delta: 28 },
          { word: '教育', delta: 20 }
        ],
        newWords: ['マイナンバー', 'ガバナンス', 'リビングラボ']
      },
      {
        year: 2024,
        episodeCount: 32,
        totalWords: 125000,
        topWords: [
          { word: 'AI', count: 450 },
          { word: 'デジタル', count: 400 },
          { word: '住民', count: 330 },
          { word: '参加', count: 300 },
          { word: '政策形成', count: 270 }
        ],
        risingWords: [
          { word: 'AI', delta: 55 },
          { word: '政策形成', delta: 26 },
          { word: '住民参加', delta: 21 }
        ],
        newWords: ['生成AI', '説明責任', '合意形成']
      },
      {
        year: 2025,
        episodeCount: 35,
        totalWords: 132000,
        topWords: [
          { word: '生成AI', count: 480 },
          { word: 'AI', count: 460 },
          { word: 'データ活用', count: 390 },
          { word: '住民参加', count: 350 },
          { word: '持続可能性', count: 310 }
        ],
        risingWords: [
          { word: '生成AI', delta: 65 },
          { word: 'データ活用', delta: 38 },
          { word: '持続可能性', delta: 29 }
        ],
        newWords: ['LLM', 'サステナビリティ', 'カーボンニュートラル']
      }
    ]
  },
  computed: {
    yearOptions() {
      return this.trends.map(trend => trend.year).sort((a, b) => b - a);
    },
    metricOptions() {
      return ['頻出数', '特徴度(TF-IDF)', '前年差分'];
    },
    filteredTrends() {
      if (!this.selectedYear) {
        return this.trends;
      }
      return this.trends.filter(trend => trend.year === this.selectedYear);
    }
  },
  methods: {
    getWordBarStyle(word, trend) {
      const max = Math.max(...trend.topWords.map(item => item.count));
      const ratio = max === 0 ? 0 : (word.count / max) * 100;
      return {
        width: `${ratio}%`
      };
    },
    updateMetaTags() {
      const siteUrl = CONFIG.siteUrl;
      setLinkTag('canonical', `${siteUrl}/word-trends.html`);
      setMetaProperty('og:url', `${siteUrl}/word-trends.html`);
      setMetaProperty('og:image', `${siteUrl}/img/keyvisual.png`);
    }
  },
  mounted() {
    this.updateMetaTags();
  }
});
