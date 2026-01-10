// About Page
new Vue({
  el: '#app',
  vuetify: new Vuetify(),
  data: {
    platformLinks: CONFIG.platforms,
    externalLinks: CONFIG.externalLinks,
    drawer: false, // ハンバーガーメニューの開閉状態
  },
  mounted() {
    this.updateMetaTags();
  },
  methods: {
    updateMetaTags() {
      const siteUrl = CONFIG.siteUrl;
      setLinkTag('canonical', `${siteUrl}/about.html`);
      setMetaProperty('og:url', `${siteUrl}/about.html`);
      setMetaProperty('og:image', `${siteUrl}/img/keyvisual.png`);
    }
  }
});

