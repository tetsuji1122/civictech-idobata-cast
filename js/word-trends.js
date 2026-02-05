// word-trends.html用のJavaScript（ダッシュボード）
new Vue({
  el: '#app',
  vuetify: new Vuetify(),
  data: {
    drawer: false,
    externalLinks: CONFIG.externalLinks,
    selectedYears: [],
    selectedTag: null,
    searchQuery: '',
    selectedMetric: '頻出数',
    showDelta: true,
    loading: true,
    trends: [],
    episodeInsights: [],
    sentimentTrends: [],
    wordNetworks: [],
    selectedEpisodeId: null,
    sentimentChart: null,
    networkInstance: null,
    updateTimer: null
  },
  computed: {
    yearOptions() {
      const years = this.trends.map(trend => trend.year);
      return years.sort((a, b) => b - a);
    },
    tagOptions() {
      const tagSet = new Set();
      this.episodeInsights.forEach(episode => {
        (episode.tags || []).forEach(tag => tagSet.add(tag));
      });
      return [
        { text: 'すべて', value: null },
        ...Array.from(tagSet).sort().map(tag => ({ text: tag, value: tag }))
      ];
    },
    metricOptions() {
      return ['頻出数', '特徴度(TF-IDF)', '前年差分'];
    },
    filteredTrends() {
      if (!this.selectedYears || this.selectedYears.length === 0) {
        return this.trends;
      }
      return this.trends.filter(trend => this.selectedYears.includes(trend.year));
    },
    filteredEpisodeInsights() {
      let results = [...this.episodeInsights];
      if (this.selectedYears && this.selectedYears.length > 0) {
        results = results.filter(item => this.selectedYears.includes(item.year));
      }
      if (this.selectedTag) {
        results = results.filter(item => (item.tags || []).includes(this.selectedTag));
      }
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        results = results.filter(item =>
          (item.title || '').toLowerCase().includes(query) ||
          (item.topTokens || []).some(token => token.word.toLowerCase().includes(query))
        );
      }
      return results;
    },
    episodeOptions() {
      return this.filteredEpisodeInsights.map(episode => ({
        text: `${episode.number} ${episode.title}`,
        value: episode.id
      }));
    },
    selectedEpisode() {
      return this.episodeInsights.find(item => item.id === this.selectedEpisodeId);
    }
  },
  watch: {
    filteredEpisodeInsights() {
      this.debouncedUpdate();
      if (this.selectedEpisodeId) {
        const exists = this.filteredEpisodeInsights.some(item => item.id === this.selectedEpisodeId);
        if (!exists) {
          this.selectedEpisodeId = null;
        }
      }
    },
    selectedYears() {
      this.debouncedUpdate();
    }
  },
  methods: {
    async loadData() {
      try {
        const [trendRes, insightsRes, sentimentRes, networkRes] = await Promise.all([
          fetchWithoutCache(CONFIG.paths.wordTrends || 'data/word-trends.json'),
          fetchWithoutCache(CONFIG.paths.episodeInsights || 'data/episode-insights.json'),
          fetchWithoutCache(CONFIG.paths.sentimentTrends || 'data/sentiment-trends.json'),
          fetchWithoutCache(CONFIG.paths.wordNetwork || 'data/word-network.json')
        ]);
        const trendData = await trendRes.json();
        const insightsData = await insightsRes.json();
        const sentimentData = await sentimentRes.json();
        const networkData = await networkRes.json();

        this.trends = trendData.trends || [];
        this.episodeInsights = insightsData.episodes || [];
        this.sentimentTrends = sentimentData.trends || [];
        this.wordNetworks = networkData.networks || [];

        if (!this.selectedYears || this.selectedYears.length === 0) {
          const maxYear = Math.max(...this.trends.map(item => item.year));
          this.selectedYears = [maxYear];
        }

        this.loading = false;
        this.$nextTick(() => {
          this.updateSentimentChart();
          this.updateNetwork();
        });
      } catch (error) {
        console.error('年表データの読み込みに失敗しました:', error);
        this.loading = false;
      }
    },
    resetFilters() {
      this.selectedYears = [];
      this.selectedTag = null;
      this.searchQuery = '';
      this.selectedMetric = '頻出数';
      this.showDelta = true;
    },
    debouncedUpdate() {
      if (this.updateTimer) {
        clearTimeout(this.updateTimer);
      }
      this.updateTimer = setTimeout(() => {
        this.updateSentimentChart();
        this.updateNetwork();
      }, 300);
    },
    formatScore(score) {
      return score.toFixed(3);
    },
    getWordBarStyle(word, trend) {
      const max = Math.max(...(trend.topWords || []).map(item => item.count));
      const ratio = max === 0 ? 0 : (word.count / max) * 100;
      return {
        width: `${ratio}%`
      };
    },
    getSentimentSeries() {
      const yearMap = new Map();
      this.filteredEpisodeInsights.forEach(item => {
        if (!item.sentiment) {
          return;
        }
        const entry = yearMap.get(item.year) || { scores: [] };
        entry.scores.push(item.sentiment.score);
        yearMap.set(item.year, entry);
      });
      const years = Array.from(yearMap.keys()).sort((a, b) => a - b);
      const averages = years.map(year => {
        const scores = yearMap.get(year).scores;
        if (!scores || scores.length === 0) {
          return 0;
        }
        const sum = scores.reduce((acc, score) => acc + score, 0);
        return sum / scores.length;
      });
      return { years, averages };
    },
    updateSentimentChart() {
      if (!this.$refs.sentimentChart) {
        return;
      }
      const { years, averages } = this.getSentimentSeries();
      if (this.sentimentChart) {
        this.sentimentChart.destroy();
      }
      this.sentimentChart = new Chart(this.$refs.sentimentChart.getContext('2d'), {
        type: 'line',
        data: {
          labels: years,
          datasets: [
            {
              label: '平均センチメント',
              data: averages,
              borderColor: '#003049',
              backgroundColor: 'rgba(0, 48, 73, 0.1)',
              fill: true,
              tension: 0.3
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              title: { display: true, text: 'スコア' }
            }
          }
        }
      });
    },
    buildNetworkFromEpisodes(episodes) {
      // パフォーマンス改善: エピソード数が多い場合は制限
      const maxEpisodes = 200;
      const limitedEpisodes = episodes.slice(0, maxEpisodes);
      
      const edgeCounts = new Map();
      const nodeCounts = new Map();

      limitedEpisodes.forEach(episode => {
        const topTokens = (episode.topTokens || []).slice(0, 10).map(item => item.word);
        const uniqueTokens = Array.from(new Set(topTokens));
        uniqueTokens.forEach(token => {
          nodeCounts.set(token, (nodeCounts.get(token) || 0) + 1);
        });
        // 組み合わせ数を制限
        for (let i = 0; i < Math.min(uniqueTokens.length, 8); i += 1) {
          for (let j = i + 1; j < Math.min(uniqueTokens.length, 8); j += 1) {
            const pair = [uniqueTokens[i], uniqueTokens[j]].sort().join('::');
            edgeCounts.set(pair, (edgeCounts.get(pair) || 0) + 1);
          }
        }
      });

      const edges = Array.from(edgeCounts.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 150)
        .map(([pair, value]) => {
          const [from, to] = pair.split('::');
          return { from, to, value };
        });

      // エッジに含まれるノードのみを抽出
      const edgeNodes = new Set();
      edges.forEach(edge => {
        edgeNodes.add(edge.from);
        edgeNodes.add(edge.to);
      });

      const nodes = Array.from(edgeNodes).map(id => ({
        id,
        label: id,
        value: nodeCounts.get(id) || 1
      }));

      return { nodes, edges };
    },
    updateNetwork() {
      if (!this.$refs.networkContainer) {
        return;
      }
      
      // データが空の場合はスキップ
      if (this.filteredEpisodeInsights.length === 0) {
        if (this.networkInstance) {
          this.networkInstance.setData({ nodes: new vis.DataSet([]), edges: new vis.DataSet([]) });
        }
        return;
      }

      const networkData = this.buildNetworkFromEpisodes(this.filteredEpisodeInsights);
      
      // ノードまたはエッジが空の場合はスキップ
      if (networkData.nodes.length === 0 || networkData.edges.length === 0) {
        if (this.networkInstance) {
          this.networkInstance.setData({ nodes: new vis.DataSet([]), edges: new vis.DataSet([]) });
        }
        return;
      }

      const data = {
        nodes: new vis.DataSet(networkData.nodes),
        edges: new vis.DataSet(networkData.edges)
      };
      const options = {
        nodes: { shape: 'dot', scaling: { min: 10, max: 30 } },
        edges: { smooth: true },
        physics: { stabilization: false, enabled: false }
      };

      if (this.networkInstance) {
        this.networkInstance.setData(data);
      } else {
        this.networkInstance = new vis.Network(this.$refs.networkContainer, data, options);
      }
    },
    updateMetaTags() {
      const siteUrl = CONFIG.siteUrl;
      setLinkTag('canonical', `${siteUrl}/word-trends.html`);
      setMetaProperty('og:url', `${siteUrl}/word-trends.html`);
      setMetaProperty('og:image', `${siteUrl}/img/keyvisual.png`);
    }
  },
  mounted() {
    this.loadData();
    this.updateMetaTags();
  }
});
