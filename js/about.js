// About Page
new Vue({
  el: '#app',
  vuetify: new Vuetify(),
  data: {
    platformLinks: CONFIG.platforms,
    externalLinks: CONFIG.externalLinks
  },
  mounted() {
    // ページロード時の処理（必要に応じて追加）
    console.log('About page loaded');
  }
});

