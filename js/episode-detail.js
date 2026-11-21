// episode-detail.html用のJavaScript
const config = (typeof CONFIG !== 'undefined' ? CONFIG : (typeof window !== 'undefined' && window.CONFIG ? window.CONFIG : null)) || {
  siteUrl: 'https://tetsuji1122.github.io/civictech-idobata-cast',
  externalLinks: {
    twitter: 'https://twitter.com/civictechcast',
    github: 'https://github.com/tetsuji1122/civictech-idobata-cast'
  },
  paths: {
    episodes: 'data/episodes.json',
    transcripts: 'data/transcripts/'
  }
};

let app = new Vue({
  el: '#app',
  vuetify: new Vuetify(),
  data: { 
    loading: true,
    episode: null,
    allEpisodes: [],
    previousEpisode: null,
    nextEpisode: null,
    showScrollTop: false,
    spotifyPlayerLoading: true,
    externalLinks: config.externalLinks,
    showCopySuccess: false,
    drawer: false, // ハンバーガーメニューの開閉状態
    highlightedSec: null, // アンカーでハイライトされた秒数
  },
  computed: {
    hasSegments() {
      return Boolean(
        this.episode &&
        Array.isArray(this.episode.segments) &&
        this.episode.segments.length > 0
      );
    },
    formattedSubTitle() {
      if (!this.episode || !this.episode.sub_title) return '';
      return this.parseMarkdown(this.episode.sub_title);
    },
    formattedSummary() {
      if (!this.episode || !this.episode.summary) return '';
      return this.parseMarkdown(this.episode.summary);
    },
    formattedTranscript() {
      if (!this.episode || !this.episode.transcript) return '';
      
      let transcript = this.episode.transcript;
      
      // タイムスタンプをハイライト表示（Markdown変換前に処理）
      transcript = transcript.replace(/\*\*(\d{1,2}:\d{2}(?:\s*-\s*\d{1,2}:\d{2})?)\*\*/g, '<span class="timestamp">$1</span>');
      transcript = transcript.replace(/\[(\d{1,2}:\d{2})\]/g, '<span class="timestamp">[$1]</span>');
      
      // Markdownをパース
      return this.parseMarkdown(transcript);
    },
    spotifyEmbedUrl() {
      if (!this.episode || !this.episode.spotifyUrl) return '';
      
      // Spotify URLを埋め込み形式に変換
      const url = this.episode.spotifyUrl;
      
      // podcasters.spotify.com 形式の場合
      // https://podcasters.spotify.com/pod/show/civictechcast/episodes/ep1-0-3-Sora-2-e3b6vi4
      // ↓
      // https://podcasters.spotify.com/pod/show/civictechcast/embed/episodes/ep1-0-3-Sora-2-e3b6vi4
      if (url.includes('podcasters.spotify.com/pod/show/civictechcast/episodes/')) {
        const episodeId = url.match(/episodes\/([^\/\?]+)/);
        if (episodeId && episodeId[1]) {
          // creators.spotify.com 形式はCSPエラー(frame-ancestors)が発生する場合があるため、
          // より互換性の高い podcasters.spotify.com の埋め込み形式を使用します
          return `https://podcasters.spotify.com/pod/show/civictechcast/embed/episodes/${episodeId[1]}`;
        }
      }
      
      // open.spotify.com/episode/ 形式の場合
      if (url.includes('open.spotify.com/episode/')) {
        const episodeId = url.match(/episode\/([a-zA-Z0-9]+)/);
        if (episodeId && episodeId[1]) {
          return `https://open.spotify.com/embed/episode/${episodeId[1]}`;
        }
      }
      
      // spotify.com/show/ 形式の場合（ショー全体の埋め込み）
      if (url.includes('spotify.com/show/')) {
        const showId = url.match(/show\/([a-zA-Z0-9]+)/);
        if (showId && showId[1]) {
          return `https://open.spotify.com/embed/show/${showId[1]}`;
        }
      }
      
      // フォールバック: ショー全体の埋め込みを使用
      // CSPエラーを回避するため、open.spotify.com形式を使用
      return 'https://open.spotify.com/embed/show/31JfR2D72gENOfOwq3AcKw';
    },
    hasValidLinks() {
      // 関連リンクが有効かどうかを厳密にチェック
      if (!this.episode) return false;
      if (!this.episode.links) return false;
      if (!Array.isArray(this.episode.links)) return false;
      if (this.episode.links.length === 0) return false;
      
      // 有効なリンクオブジェクトが含まれているかチェック
      const validLinks = this.episode.links.filter(link => 
        link && 
        typeof link === 'object' && 
        link.url && 
        typeof link.url === 'string' && 
        link.url.trim() !== ''
      );
      
      return validLinks.length > 0;
    },
    canUseWebShare() {
      // Web Share APIが利用可能かチェック（モバイルブラウザなど）
      return navigator.share !== undefined;
    },
    shareUrl() {
      if (!this.episode) return '';
      return `${config.siteUrl}/episode-detail.html?id=${this.episode.id}`;
    },
    shareTitle() {
      if (!this.episode) return 'シビックテック井戸端キャスト';
      return `${this.episode.title} - シビックテック井戸端キャスト`;
    },
    shareText() {
      if (!this.episode) return 'シビックテック井戸端キャスト';
      return `${this.episode.title}\n${this.episode.sub_title || this.episode.description || ''}`;
    },
    twitterShareUrl() {
      if (!this.episode) return '';
      const text = encodeURIComponent(`${this.episode.title} - シビックテック井戸端キャスト`);
      const url = encodeURIComponent(this.shareUrl);
      return `https://twitter.com/intent/tweet?text=${text}&url=${url}`;
    },
    facebookShareUrl() {
      const url = encodeURIComponent(this.shareUrl);
      return `https://www.facebook.com/sharer/sharer.php?u=${url}`;
    },
    lineShareUrl() {
      const url = encodeURIComponent(this.shareUrl);
      const text = encodeURIComponent(this.shareTitle);
      return `https://social-plugins.line.me/lineit/share?url=${url}&text=${text}`;
    }
  },
  methods: {
    parseMarkdown(text) {
      if (!text) return '';
      
      // marked.jsを使用してMarkdownをHTMLに変換
      if (typeof marked !== 'undefined') {
        // marked.jsの設定
        marked.setOptions({
          breaks: true,  // 改行を<br>に変換
          gfm: true,     // GitHub Flavored Markdown
        });
        return marked.parse(text);
      }
      
      // marked.jsが読み込まれていない場合は、改行のみ変換
      return text.replace(/\n/g, '<br>');
    },
    async loadEpisode() {
      try {
        // URLパラメータからエピソードIDを取得（数値IDまたは話数文字列）
        const urlParams = new URLSearchParams(window.location.search);
        const idParam = urlParams.get('id');
        
        if (!idParam) {
          this.loading = false;
          return;
        }
        
        // エピソードデータを読み込み（キャッシュを無効化）
        const response = await fetchWithoutCache(config.paths.episodes);
        const data = await response.json();
        this.allEpisodes = data.episodes;
        
        // 該当するエピソードを探す (1. 話数文字列で完全一致、2. 純粋な数字のみの場合は数値ID)
        const trimmedId = idParam.trim();
        const cleanId = trimmedId.replace(/^ep/i, '');
        
        // 1. まずエピソード番号（"0.0.1", "1.0.14" 等）で完全一致検索
        this.episode = this.allEpisodes.find(ep => 
          String(ep.number) === trimmedId || String(ep.number) === cleanId
        );
        
        // 2. 見つからず、パラメータが純粋な数字のみ（例: id=1, id=42）の場合に限り数値IDで検索
        if (!this.episode && /^\d+$/.test(cleanId)) {
          const numId = parseInt(cleanId, 10);
          this.episode = this.allEpisodes.find(ep => ep.id === numId);
        }
        
        if (this.episode) {
          const episodeId = this.episode.id;
          // ページタイトルとメタタグを更新
          this.updateMetaTags();
          
          // 構造化データを追加
          this.updateStructuredData();
          
          // Spotifyプレーヤーのローディング状態をリセット
          this.spotifyPlayerLoading = true;
          
          // 前後のエピソードを取得
          this.findAdjacentEpisodes(episodeId);
          
          // 書き起こしを別ファイルから読み込み（has_transcriptがtrueの場合のみ）
          if (this.episode.has_transcript === true) {
            await this.loadTranscript(this.episode.number);
          } else {
            console.log(`[INFO] 書き起こしファイルが存在しないため、読み込みをスキップ: ep${this.episode.number}`);
          }
        }
        
        this.loading = false;
        this.$nextTick(() => {
          this.handleHashAnchor();
        });
      } catch (error) {
        console.error('エピソードデータの読み込みに失敗しました:', error);
        this.loading = false;
      }
    },
    async loadTranscript(episodeNumber) {
      try {
        const transcriptPath = `${config.paths.transcripts}ep${episodeNumber}.json`;
        const response = await fetch(transcriptPath);
        
        if (response.ok) {
          const transcriptData = await response.json();
          // 書き起こしデータを追加
          this.episode.transcript = transcriptData.transcript || '';
          this.episode.summary = transcriptData.summary || '';
          this.episode.sub_title = transcriptData.sub_title || '';
          this.episode.detailed_description = transcriptData.detailed_description || '';
          this.episode.segments = transcriptData.segments || [];
          this.episode.segment_count = transcriptData.segment_count || 0;
          
          console.log(`[INFO] 書き起こしを読み込みました: ep${episodeNumber}`);
        } else if (response.status === 404) {
          // 書き起こしファイルが存在しない場合は静かに処理（エラーログを出さない）
          // トランスクリプトファイルは任意のため、存在しない場合は正常な状態
        } else {
          // 404以外のエラーの場合のみログ出力
          console.warn(`[WARNING] 書き起こしファイルの読み込みに失敗しました: ep${episodeNumber} (ステータス: ${response.status})`);
        }
      } catch (error) {
        // ネットワークエラーなど、fetch自体が失敗した場合
        // ただし、ブラウザによっては404もcatchされる可能性があるため、エラーメッセージを確認
        if (error.message && !error.message.includes('404')) {
          console.warn(`[WARNING] 書き起こしの読み込みでエラーが発生しました: ${error.message}`);
        }
        // 404エラーの場合は静かに処理（エラーログを出さない）
      }
    },
    findAdjacentEpisodes(currentId) {
      // sessionStorageからフィルター済みエピソードリストを取得
      let episodeList = this.allEpisodes;
      
      const savedFilteredNumbers = sessionStorage.getItem('filteredEpisodeNumbers');
      if (savedFilteredNumbers) {
        try {
          const filteredNumbers = JSON.parse(savedFilteredNumbers);
          // フィルター済みエピソード番号リストに基づいてエピソードを抽出
          episodeList = filteredNumbers
            .map(num => this.allEpisodes.find(ep => ep.number === num))
            .filter(ep => ep); // undefinedを除外
          
          console.log(`[INFO] フィルター済みエピソードリストを使用 (${episodeList.length}件)`);
        } catch (error) {
          console.error('フィルター済みエピソードリストの読み込みに失敗:', error);
        }
      }
      
      // 現在のエピソードのインデックスを探す
      const currentIndex = episodeList.findIndex(ep => ep.id === currentId);
      
      if (currentIndex > 0) {
        this.previousEpisode = episodeList[currentIndex - 1];
      }
      
      if (currentIndex >= 0 && currentIndex < episodeList.length - 1) {
        this.nextEpisode = episodeList[currentIndex + 1];
      }
    },
    scrollToTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    handleScroll() {
      this.showScrollTop = window.scrollY > 300;
    },
    onSpotifyPlayerLoad() {
      // iframeの読み込みが完了したらローディングを非表示
      this.spotifyPlayerLoading = false;
      console.log('[INFO] Spotify埋め込みプレーヤーの読み込みが完了しました');
    },
    async shareWithWebAPI() {
      if (!this.episode) return;
      
      const shareData = {
        title: this.shareTitle,
        text: this.shareText,
        url: this.shareUrl
      };
      
      try {
        if (navigator.share) {
          await navigator.share(shareData);
          console.log('[INFO] 共有が完了しました');
        }
      } catch (error) {
        // ユーザーが共有をキャンセルした場合など
        if (error.name !== 'AbortError') {
          console.error('[ERROR] 共有に失敗しました:', error);
        }
      }
    },
    copyUrlToClipboard() {
      const url = this.shareUrl;
      
      // Clipboard APIを使用（モダンブラウザ）
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(() => {
          this.showCopySuccess = true;
          setTimeout(() => {
            this.showCopySuccess = false;
          }, 2000);
          console.log('[INFO] URLをクリップボードにコピーしました');
        }).catch(error => {
          console.error('[ERROR] URLのコピーに失敗しました:', error);
          this.fallbackCopyUrl(url);
        });
      } else {
        // フォールバック方法
        this.fallbackCopyUrl(url);
      }
    },
    fallbackCopyUrl(text) {
      // 古いブラウザ用のフォールバック
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.select();
      
      try {
        document.execCommand('copy');
        this.showCopySuccess = true;
        setTimeout(() => {
          this.showCopySuccess = false;
        }, 2000);
        console.log('[INFO] URLをクリップボードにコピーしました（フォールバック）');
      } catch (error) {
        console.error('[ERROR] URLのコピーに失敗しました:', error);
        alert('URLのコピーに失敗しました。手動でコピーしてください。\n' + text);
      } finally {
        document.body.removeChild(textArea);
      }
    },
    updateMetaTags() {
      if (!this.episode) return;
      
      const title = `${this.episode.title} - シビックテック井戸端キャスト`;
      const description = this.episode.sub_title || this.episode.description || 'シビックテック井戸端キャストのエピソード詳細ページ。全文書き起こしを読むことができます。';
      const image = this.episode.thumbnail ? `${config.siteUrl}/${this.episode.thumbnail}` : `${config.siteUrl}/img/keyvisual.png`;
      const url = `${config.siteUrl}/episode-detail.html?id=${this.episode.id}`;
      
      // タイトルを更新
      document.title = title;
      
      // メタタグを更新
      setMetaTag('description', description);
      setMetaTag('keywords', this.episode.tags ? this.episode.tags.join(',') + ',シビックテック,ポッドキャスト' : 'シビックテック,ポッドキャスト');
      
      // OGPタグを更新
      setMetaProperty('og:title', title);
      setMetaProperty('og:description', description);
      setMetaProperty('og:url', url);
      setMetaProperty('og:image', image);
      if (this.episode.date) {
        setMetaProperty('article:published_time', `${this.episode.date}T00:00:00+09:00`);
      }
      
      // Twitter Cardを更新
      setMetaTag('twitter:title', title);
      setMetaTag('twitter:description', description);
      setMetaTag('twitter:image', image);
      
      // canonical URLを更新
      setLinkTag('canonical', url);
    },
    updateInitialMetaTags() {
      // エピソード読み込み前の初期メタタグを更新
      const siteUrl = config.siteUrl;
      setLinkTag('canonical', `${siteUrl}/episode-detail.html`);
      setMetaProperty('og:url', `${siteUrl}/episode-detail.html`);
      setMetaProperty('og:image', `${siteUrl}/img/keyvisual.png`);
      setMetaTag('twitter:image', `${siteUrl}/img/keyvisual.png`);
    },
    updateStructuredData() {
      if (!this.episode) return;
      
      // 既存の構造化データを削除
      const existingScript = document.querySelector('script[type="application/ld+json"]');
      if (existingScript) {
        existingScript.remove();
      }
      
      // エピソード用の構造化データを作成
      const structuredData = {
        "@context": "https://schema.org",
        "@type": "PodcastEpisode",
        "name": this.episode.title,
        "description": this.episode.sub_title || this.episode.description || '',
        "episodeNumber": this.episode.number,
        "datePublished": this.episode.date ? `${this.episode.date}T00:00:00+09:00` : null,
        "duration": this.episode.duration || null,
        "image": this.episode.thumbnail ? `${config.siteUrl}/${this.episode.thumbnail}` : `${config.siteUrl}/img/keyvisual.png`,
        "url": `${config.siteUrl}/episode-detail.html?id=${this.episode.id}`,
        "partOfSeries": {
          "@type": "PodcastSeries",
          "name": "シビックテック井戸端キャスト",
          "url": `${config.siteUrl}/`
        }
      };
      
      // Spotify URLがある場合は追加
      if (this.episode.spotifyUrl) {
        structuredData.associatedMedia = {
          "@type": "MediaObject",
          "contentUrl": this.episode.spotifyUrl
        };
      }
      
      // スクリプトタグを追加
      const script = document.createElement('script');
      script.type = 'application/ld+json';
      script.text = JSON.stringify(structuredData, null, 2);
      document.head.appendChild(script);
    },
    formatTime(start, startSec) {
      if (start) return start;
      const s = Math.max(0, parseInt(startSec) || 0);
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
    copySegmentUrl(seg) {
      if (!this.episode) return;
      const url = `${config.siteUrl}/episode-detail.html?id=${this.episode.number}#t=${seg.start_sec}`;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(() => {
          this.showCopySuccess = true;
          setTimeout(() => {
            this.showCopySuccess = false;
          }, 2000);
        }).catch(() => {
          this.fallbackCopyUrl(url);
        });
      } else {
        this.fallbackCopyUrl(url);
      }
    },
    handleHashAnchor() {
      const hash = window.location.hash;
      if (!hash || !hash.startsWith('#t=')) return;
      const targetSec = parseInt(hash.replace('#t=', ''), 10);
      if (isNaN(targetSec)) return;

      if (this.hasSegments) {
        let closestSeg = null;
        for (const seg of this.episode.segments) {
          if (seg.start_sec <= targetSec) {
            if (!closestSeg || seg.start_sec > closestSeg.start_sec) {
              closestSeg = seg;
            }
          }
        }
        if (!closestSeg && this.episode.segments.length > 0) {
          closestSeg = this.episode.segments[0];
        }

        if (closestSeg) {
          this.highlightedSec = closestSeg.start_sec;
          this.$nextTick(() => {
            const el = document.getElementById(`segment-${closestSeg.start_sec}`);
            if (el) {
              el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          });
        }
      }
    }
  },
  mounted() {
    // 初期メタタグを更新
    this.updateInitialMetaTags();
    this.loadEpisode();
    window.addEventListener('scroll', this.handleScroll);
    window.addEventListener('hashchange', this.handleHashAnchor);
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.handleScroll);
    window.removeEventListener('hashchange', this.handleHashAnchor);
  }
});

