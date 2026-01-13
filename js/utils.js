/**
 * 共通ユーティリティ関数
 * すべてのページで使用される共通のDOM操作・メタタグ管理関数
 */

// メタタグを設定または更新
function setMetaTag(name, content) {
  let meta = document.querySelector(`meta[name="${name}"]`);
  if (!meta) {
    meta = document.createElement('meta');
    meta.setAttribute('name', name);
    document.head.appendChild(meta);
  }
  meta.setAttribute('content', content);
}

// OGPプロパティを設定または更新
function setMetaProperty(property, content) {
  let meta = document.querySelector(`meta[property="${property}"]`);
  if (!meta) {
    meta = document.createElement('meta');
    meta.setAttribute('property', property);
    document.head.appendChild(meta);
  }
  meta.setAttribute('content', content);
}

// リンクタグを設定または更新
function setLinkTag(rel, href) {
  let link = document.querySelector(`link[rel="${rel}"]`);
  if (!link) {
    link = document.createElement('link');
    link.setAttribute('rel', rel);
    document.head.appendChild(link);
  }
  link.setAttribute('href', href);
}

/**
 * キャッシュを無効化してJSONファイルを取得
 * episodes.jsonが毎日更新されるため、常に最新版を取得する
 * 
 * @param {string} url - 取得するJSONファイルのURL
 * @returns {Promise<Response>} fetchのResponseオブジェクト
 */
async function fetchWithoutCache(url) {
  // クエリパラメータにタイムスタンプを追加してキャッシュを回避
  const timestamp = new Date().getTime();
  const urlWithCacheBust = `${url}?t=${timestamp}`;
  
  // fetch APIでキャッシュを無効化
  return fetch(urlWithCacheBust, {
    cache: 'no-store',
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
}
