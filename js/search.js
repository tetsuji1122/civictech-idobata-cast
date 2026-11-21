// search.html用のJavaScript
const config = (typeof CONFIG !== 'undefined' ? CONFIG : (typeof window !== 'undefined' && window.CONFIG ? window.CONFIG : null)) || {
  siteUrl: 'https://tetsuji1122.github.io/civictech-idobata-cast',
  externalLinks: {
    twitter: 'https://twitter.com/civictechcast',
    github: 'https://github.com/tetsuji1122/civictech-idobata-cast'
  }
};

new Vue({
  el: '#app',
  vuetify: new Vuetify(),
  data: {
    loading: false,
    drawer: false,
    externalLinks: config.externalLinks,
    searchQuery: '',
    selectedSpeaker: 'all',
    selectedYear: 'all',
    sampleQueries: ['オープンデータ', '生成AI', 'ハッカソン', '防災','教育','子育て','観光','自治体','行政','長崎','岐阜','猫'],
    years: ['all', '2026', '2025', '2024', '2023', '2022', '2021'],
    yearLabels: {
      'all': '全期間',
      '2026': '2026年',
      '2025': '2025年',
      '2024': '2024年',
      '2023': '2023年',
      '2022': '2022年',
      '2021': '2021年'
    },
    speakers: [
      { id: 'all', name: '全員' },
      { id: '石井', name: '石井' },
      { id: '太田', name: '太田' },
      { id: '小俣', name: '小俣' },
      { id: 'guest', name: 'ゲスト' }
    ],
    yearCache: {},
    searchResults: [],
    displayLimit: 50,
    hasSearched: false
  },
  computed: {
    displayedResults() {
      return this.searchResults.slice(0, this.displayLimit);
    },
    hasMore() {
      return this.searchResults.length > this.displayLimit;
    },
    totalUtteranceCount() {
      return this.searchResults.length;
    },
    distinctEpisodeCount() {
      const epSet = new Set(this.searchResults.map(r => r.episode_number));
      return epSet.size;
    }
  },
  methods: {
    setSampleQuery(query) {
      this.searchQuery = query;
      this.performSearch();
    },
    normalize(str) {
      if (!str) return '';
      return str.normalize('NFKC').toLowerCase();
    },
    escapeHtml(str) {
      if (!str) return '';
      return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    },
    formatTime(sec) {
      const s = Math.max(0, parseInt(sec) || 0);
      const m = Math.floor(s / 60);
      const rem = s % 60;
      return `${m}:${rem.toString().padStart(2, '0')}`;
    },
    getSpeakerClass(speaker) {
      if (speaker === '石井') return 'speaker-ishii';
      if (speaker === '太田') return 'speaker-ota';
      if (speaker === '小俣') return 'speaker-omata';
      return 'speaker-guest';
    },
    getSpeakerChipClass(speaker) {
      if (speaker === '石井') return 'speaker-chip-ishii';
      if (speaker === '太田') return 'speaker-chip-ota';
      if (speaker === '小俣') return 'speaker-chip-omata';
      return 'speaker-chip-guest';
    },
    getSpeakerDisplayName(speaker) {
      return speaker || '不明';
    },
    async loadYearIndex(year) {
      if (this.yearCache[year]) return this.yearCache[year];
      try {
        const response = await fetch(`data/search-index-${year}.json`);
        if (!response.ok) return [];
        const data = await response.json();
        this.yearCache[year] = data;
        return data;
      } catch (e) {
        return [];
      }
    },
    async loadTargetRecords() {
      if (this.selectedYear !== 'all') {
        return await this.loadYearIndex(this.selectedYear);
      }
      const list = ['2026', '2025', '2024', '2023', '2022', '2021'];
      const results = await Promise.all(list.map(y => this.loadYearIndex(y)));
      return results.flat();
    },
    createSnippetAndHighlight(rawText, terms) {
      if (!rawText) return '';
      const normText = this.normalize(rawText);
      let firstPos = -1;
      let matchedTermLen = 0;
      for (const term of terms) {
        const p = normText.indexOf(term);
        if (p !== -1 && (firstPos === -1 || p < firstPos)) {
          firstPos = p;
          matchedTermLen = term.length;
        }
      }

      let start = 0;
      let end = rawText.length;
      let hasLeadingEllipsis = false;
      let hasTrailingEllipsis = false;

      if (rawText.length > 160 && firstPos !== -1) {
        start = Math.max(0, firstPos - 80);
        end = Math.min(rawText.length, firstPos + matchedTermLen + 80);
        if (start > 0) hasLeadingEllipsis = true;
        if (end < rawText.length) hasTrailingEllipsis = true;
      }

      let snippet = rawText.substring(start, end);
      let escaped = this.escapeHtml(snippet);

      for (const term of terms) {
        if (!term) continue;
        const escapedTerm = this.escapeHtml(term);
        const regexSafe = escapedTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const reg = new RegExp(`(${regexSafe})`, 'gi');
        escaped = escaped.replace(reg, '<mark class="highlight">$1</mark>');
      }

      return (hasLeadingEllipsis ? '…' : '') + escaped + (hasTrailingEllipsis ? '…' : '');
    },
    async performSearch() {
      const q = this.searchQuery.trim();
      if (!q) {
        this.searchResults = [];
        this.hasSearched = false;
        return;
      }

      this.loading = true;
      this.hasSearched = true;
      this.displayLimit = 50;

      const terms = this.normalize(q).split(/\s+/).filter(t => t.length > 0);
      const records = await this.loadTargetRecords();
      const matched = [];
      const regularSpeakers = ['石井', '太田', '小俣'];

      for (const item of records) {
        if (this.selectedSpeaker !== 'all') {
          if (this.selectedSpeaker === 'guest') {
            if (regularSpeakers.includes(item.speaker)) continue;
          } else if (item.speaker !== this.selectedSpeaker) {
            continue;
          }
        }

        const normText = this.normalize(item.text);
        let allMatch = true;
        for (const t of terms) {
          if (!normText.includes(t)) {
            allMatch = false;
            break;
          }
        }
        if (!allMatch) continue;

        const highlighted = this.createSnippetAndHighlight(item.text, terms);
        matched.push({
          ...item,
          highlightedHtml: highlighted,
          detailUrl: `episode-detail.html?id=${item.episode_number}#t=${item.start_sec}`
        });
      }

      matched.sort((a, b) => {
        if (a.date !== b.date) return b.date.localeCompare(a.date);
        if (a.episode_number !== b.episode_number) return b.episode_number.localeCompare(a.episode_number);
        return a.start_sec - b.start_sec;
      });

      this.searchResults = matched;
      this.loading = false;
    },
    loadMore() {
      this.displayLimit += 50;
    },
    updateMetaTags() {
      const siteUrl = config.siteUrl;
      const title = '発話検索 - シビックテック井戸端キャスト';
      const description = 'シビックテック井戸端キャストの全エピソードから、発話単位でキーワード検索ができます。';
      document.title = title;
      setMetaTag('description', description);
      setLinkTag('canonical', `${siteUrl}/search.html`);
      setMetaProperty('og:title', title);
      setMetaProperty('og:description', description);
      setMetaProperty('og:url', `${siteUrl}/search.html`);
      setMetaProperty('og:image', `${siteUrl}/img/keyvisual.png`);
      setMetaTag('twitter:title', title);
      setMetaTag('twitter:description', description);
      setMetaTag('twitter:image', `${siteUrl}/img/keyvisual.png`);
    }
  },
  mounted() {
    this.updateMetaTags();
    const urlParams = new URLSearchParams(window.location.search);
    const q = urlParams.get('q');
    if (q) {
      this.searchQuery = q;
      this.performSearch();
    }
  }
});
