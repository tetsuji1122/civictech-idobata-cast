// About Page
const config = (typeof CONFIG !== 'undefined' ? CONFIG : (typeof window !== 'undefined' && window.CONFIG ? window.CONFIG : null)) || {
  siteUrl: 'https://tetsuji1122.github.io/civictech-idobata-cast',
  platforms: {
    spotify: 'https://open.spotify.com/show/31JfR2D72gENOfOwq3AcKw',
    applePodcasts: 'https://podcasts.apple.com/jp/podcast/%E3%82%B7%E3%83%93%E3%83%83%E3%82%AF%E3%83%86%E3%83%83%E3%82%AF%E4%BA%95%E6%88%B8%E7%AB%AF%E3%82%AD%E3%83%A3%E3%82%B9%E3%83%88/id1587297171',
    youtube: 'https://www.youtube.com/@civictechcast',
    rssFeed: 'https://anchor.fm/s/6981b208/podcast/rss'
  },
  externalLinks: {
    twitter: 'https://twitter.com/civictechcast',
    github: 'https://github.com/tetsuji1122/civictech-idobata-cast'
  }
};

new Vue({
  el: '#app',
  vuetify: new Vuetify(),
  data: {
    platformLinks: config.platforms,
    externalLinks: config.externalLinks,
    drawer: false, // ハンバーガーメニューの開閉状態
  },
  mounted() {
    this.updateMetaTags();
  },
  methods: {
    updateMetaTags() {
      const siteUrl = config.siteUrl;
      setLinkTag('canonical', `${siteUrl}/about.html`);
      setMetaProperty('og:url', `${siteUrl}/about.html`);
      setMetaProperty('og:image', `${siteUrl}/img/keyvisual.png`);
    }
  }
});

