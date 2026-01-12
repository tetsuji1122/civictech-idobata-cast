// episodes.html用のJavaScript
let app = new Vue({
  el: '#app',
  vuetify: new Vuetify(),
  data: { 
    loading: true,
    allEpisodes: [],
    filteredEpisodes: [],
    displayedEpisodes: [],
    searchQuery: '',
    selectedTag: null,
    sortOrder: '新しい順',
    sortOptions: [
      { text: '新しい順', value: '新しい順' },
      { text: '古い順', value: '古い順' }
    ],
    allTags: [],
    showScrollTop: false,
    // 無限スクロール
    itemsPerPage: CONFIG.pagination.itemsPerPage,
    currentIndex: 0,
    isLoadingMore: false,
    hasMoreItems: true,
    // スクロール位置復元用
    savedScrollPosition: 0,
    savedCurrentIndex: 0,
    // 外部リンク
    externalLinks: CONFIG.externalLinks,
    // ハンバーガーメニューの開閉状態
    drawer: false,
  },
  methods: {
    async loadEpisodes() {
      try {
        const response = await fetch(CONFIG.paths.episodes);
        const data = await response.json();
        this.allEpisodes = data.episodes;
        this.filteredEpisodes = [...this.allEpisodes];
        this.extractTags();
        
        // フィルター条件を復元
        this.restoreFilterState();
        
        this.sortEpisodes(); // これがloadInitialEpisodesを呼ぶ
        this.loading = false;
      } catch (error) {
        console.error('エピソードデータの読み込みに失敗しました:', error);
        this.loading = false;
      }
    },
    saveFilterState() {
      // フィルター条件をsessionStorageに保存
      const scrollPos = window.scrollY || window.pageYOffset || 0;
      const filterState = {
        searchQuery: this.searchQuery,
        selectedTag: this.selectedTag,
        sortOrder: this.sortOrder,
        scrollPosition: scrollPos,
        currentIndex: this.currentIndex || this.displayedEpisodes.length  // 表示済みエピソード数も保存
      };
      sessionStorage.setItem('episodeFilterState', JSON.stringify(filterState));
      
      // フィルター済みエピソードのリストも保存（前/次ナビゲーション用）
      const episodeNumbers = this.filteredEpisodes.map(ep => ep.number);
      sessionStorage.setItem('filteredEpisodeNumbers', JSON.stringify(episodeNumbers));
      
      console.log(`[INFO] フィルター状態を保存: スクロール位置=${filterState.scrollPosition}px, 表示数=${filterState.currentIndex}`);
    },
    restoreFilterState() {
      // sessionStorageからフィルター条件を復元
      const savedState = sessionStorage.getItem('episodeFilterState');
      if (savedState) {
        try {
          const filterState = JSON.parse(savedState);
          this.searchQuery = filterState.searchQuery || '';
          this.selectedTag = filterState.selectedTag || null;
          this.sortOrder = filterState.sortOrder || '新しい順';
          
          // フィルターを適用（sortEpisodesは呼ばない、後で呼ばれるため）
          this.filterEpisodesWithoutSort();
          
          // 保存されたスクロール位置と表示インデックスを記憶
          this.savedScrollPosition = filterState.scrollPosition || 0;
          // currentIndexが0の場合はitemsPerPageを使用（初回表示分）
          this.savedCurrentIndex = (filterState.currentIndex && filterState.currentIndex > 0) 
            ? filterState.currentIndex 
            : this.itemsPerPage;
          
          console.log(`[INFO] フィルター条件を復元: スクロール位置=${this.savedScrollPosition}px, 表示数=${this.savedCurrentIndex}件`);
        } catch (error) {
          console.error('フィルター状態の復元に失敗しました:', error);
        }
      }
    },
    filterEpisodesWithoutSort() {
      // ソートを呼ばないフィルター処理（復元時用）
      let results = [...this.allEpisodes];
      
      // 検索クエリでフィルター
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        results = results.filter(episode => 
          episode.title.toLowerCase().includes(query) ||
          episode.description.toLowerCase().includes(query) ||
          episode.number.includes(query) ||
          episode.tags.some(tag => tag.toLowerCase().includes(query))
        );
      }
      
      // タグでフィルター
      if (this.selectedTag) {
        results = results.filter(episode => 
          episode.tags.includes(this.selectedTag)
        );
      }
      
      this.filteredEpisodes = results;
    },
    extractTags() {
      const tagsSet = new Set();
      this.allEpisodes.forEach(episode => {
        episode.tags.forEach(tag => tagsSet.add(tag));
      });
      this.allTags = [
        { text: 'すべて', value: null },
        ...Array.from(tagsSet).map(tag => ({ text: tag, value: tag }))
      ];
    },
    filterEpisodes() {
      let results = [...this.allEpisodes];
      
      // 検索クエリでフィルター
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        results = results.filter(episode => 
          episode.title.toLowerCase().includes(query) ||
          episode.description.toLowerCase().includes(query) ||
          episode.number.includes(query) ||
          episode.tags.some(tag => tag.toLowerCase().includes(query))
        );
      }
      
      // タグでフィルター
      if (this.selectedTag) {
        results = results.filter(episode => 
          episode.tags.includes(this.selectedTag)
        );
      }
      
      this.filteredEpisodes = results;
      this.sortEpisodes(); // ソートとリセットを実行
      this.saveFilterState(); // フィルター条件を保存
    },
    sortEpisodes() {
      switch (this.sortOrder) {
        case '新しい順':
          // 日付の新しい順（降順）
          this.filteredEpisodes.sort((a, b) => {
            return new Date(b.date) - new Date(a.date);
          });
          break;
        case '古い順':
          // 日付の古い順（昇順）
          this.filteredEpisodes.sort((a, b) => {
            return new Date(a.date) - new Date(b.date);
          });
          break;
      }
      this.loadInitialEpisodes();
      this.saveFilterState(); // ソート順変更時も保存
    },
    loadInitialEpisodes() {
      // スクロール位置復元のために保存されたインデックスまでロード
      this.currentIndex = 0;
      this.displayedEpisodes = [];
      this.hasMoreItems = true;
      
      // 保存されたインデックスがある場合は、その位置までロード
      if (this.savedCurrentIndex > 0) {
        console.log(`[INFO] 保存された位置までエピソードをロード: ${this.savedCurrentIndex}件`);
        // 一気にロード（アニメーションなし）
        const episodes = this.filteredEpisodes.slice(0, this.savedCurrentIndex);
        this.displayedEpisodes = episodes;
        this.currentIndex = this.savedCurrentIndex;
        
        // これ以上データがない場合
        if (this.currentIndex >= this.filteredEpisodes.length) {
          this.hasMoreItems = false;
        }
        
        // スクロール位置を復元（DOMが完全に構築されるまで待つ）
        if (this.savedScrollPosition > 0) {
          const savedPosition = this.savedScrollPosition;
          // 複数のタイミングで試行して確実に復元
          this.$nextTick(() => {
            // 最初の試行（DOM更新直後）
            setTimeout(() => {
              window.scrollTo(0, savedPosition);
              console.log(`[INFO] スクロール位置を復元（1回目）: ${savedPosition}px`);
              
              // 2回目の試行（画像読み込みなどを考慮）
              setTimeout(() => {
                const currentScroll = window.scrollY;
                if (Math.abs(currentScroll - savedPosition) > 100) {
                  window.scrollTo(0, savedPosition);
                  console.log(`[INFO] スクロール位置を復元（2回目）: ${savedPosition}px`);
                }
              }, 500);
            }, 100);
          });
        }
        
        // 復元後はリセット（少し遅らせる）
        setTimeout(() => {
          this.savedCurrentIndex = 0;
          this.savedScrollPosition = 0;
        }, 1000);
      } else {
        // 通常の初回ロード
        this.loadMoreEpisodes();
      }
    },
    loadMoreEpisodes() {
      if (this.isLoadingMore || !this.hasMoreItems) {
        return;
      }
      
      this.isLoadingMore = true;
      
      // アニメーションのために少し遅延を追加
      setTimeout(() => {
        // 次の20件を取得
        const start = this.currentIndex;
        const end = start + this.itemsPerPage;
        const newEpisodes = this.filteredEpisodes.slice(start, end);
        
        if (newEpisodes.length > 0) {
          this.displayedEpisodes = [...this.displayedEpisodes, ...newEpisodes];
          this.currentIndex = end;
        }
        
        // これ以上データがない場合
        if (end >= this.filteredEpisodes.length) {
          this.hasMoreItems = false;
        }
        
        this.isLoadingMore = false;
      }, 300);
    },
    filterByTag(tag) {
      this.selectedTag = tag;
      this.filterEpisodes();
      // ページトップにスクロール
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    clearFilters() {
      this.searchQuery = '';
      this.selectedTag = null;
      this.sortOrder = '新しい順';
      this.filterEpisodes();
      // フィルター状態をクリア
      sessionStorage.removeItem('episodeFilterState');
      sessionStorage.removeItem('filteredEpisodeNumbers');
    },
    scrollToTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    goToDetail(episodeId) {
      // スクロール位置を保存してから詳細ページに遷移
      // currentIndexを確実に保存するため、displayedEpisodesの長さを使用
      const currentDisplayedCount = this.displayedEpisodes.length || this.currentIndex || this.itemsPerPage;
      const originalIndex = this.currentIndex;
      this.currentIndex = currentDisplayedCount; // 一時的に設定
      this.saveFilterState();
      this.currentIndex = originalIndex; // 元に戻す
      
      // 少し遅延を入れてから遷移（保存を確実に実行）
      setTimeout(() => {
        window.location.href = `episode-detail.html?id=${episodeId}`;
      }, 100);
    },
    handleScroll() {
      // スクロールトップボタンの表示制御
      this.showScrollTop = window.scrollY > 300;
      
      // ページの下部に近づいたら次を読み込む
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      
      // 下部から300pxの位置に到達したら読み込み
      if (scrollTop + windowHeight >= documentHeight - 300) {
        this.loadMoreEpisodes();
      }
    },
    updateMetaTags() {
      const siteUrl = CONFIG.siteUrl;
      setLinkTag('canonical', `${siteUrl}/episodes.html`);
      setMetaProperty('og:url', `${siteUrl}/episodes.html`);
      setMetaProperty('og:image', `${siteUrl}/img/keyvisual.png`);
    },
    exportToCSV() {
      // CSVデータを生成
      const headers = ['エピソード番号', 'タイトル', '配信日', '再生時間', '説明', 'タグ', 'Spotify URL', '書き起こし有無'];
      
      // ヘッダー行
      const csvRows = [headers.map(header => this.escapeCSV(header)).join(',')];
      
      // データ行（全エピソードをエクスポート）
      this.allEpisodes.forEach(episode => {
        const hasTranscript = episode.has_transcript === true ? 'あり' : 'なし';
        const row = [
          episode.number || '',
          episode.title || '',
          episode.date || '',
          episode.duration || '',
          episode.description || '',
          (episode.tags && episode.tags.length > 0) ? episode.tags.join('; ') : '',
          episode.spotifyUrl || '',
          hasTranscript
        ];
        csvRows.push(row.map(cell => this.escapeCSV(cell)).join(','));
      });
      
      // CSV文字列を生成
      const csvContent = csvRows.join('\n');
      
      // BOMを追加してUTF-8でエンコード（Excelで日本語が正しく表示されるように）
      const BOM = '\uFEFF';
      const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
      
      // ダウンロードリンクを作成
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      
      // ファイル名を生成（日付を含める）
      const now = new Date();
      const dateStr = now.getFullYear() + 
        String(now.getMonth() + 1).padStart(2, '0') + 
        String(now.getDate()).padStart(2, '0');
      const fileName = `episodes_${dateStr}.csv`;
      
      link.setAttribute('download', fileName);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log(`[INFO] CSVエクスポート完了: ${this.allEpisodes.length}件`);
    },
    escapeCSV(value) {
      // CSVの値をエスケープ
      if (value === null || value === undefined) {
        return '';
      }
      
      const stringValue = String(value);
      
      // カンマ、改行、ダブルクォートが含まれる場合はダブルクォートで囲む
      if (stringValue.includes(',') || stringValue.includes('\n') || stringValue.includes('"')) {
        // ダブルクォートは2つにエスケープ
        return '"' + stringValue.replace(/"/g, '""') + '"';
      }
      
      return stringValue;
    }
  },
  mounted() {
    // ブラウザの自動スクロール復元を無効化（手動で制御するため）
    if ('scrollRestoration' in history) {
      history.scrollRestoration = 'manual';
    }
    
    this.loadEpisodes();
    this.updateMetaTags();
    window.addEventListener('scroll', this.handleScroll);
    // ページを離れる前にフィルター状態を保存
    window.addEventListener('beforeunload', () => {
      this.saveFilterState();
    });
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.handleScroll);
    // 最後にフィルター状態を保存
    this.saveFilterState();
  }
});

