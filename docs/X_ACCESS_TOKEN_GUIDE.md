# Access Token と Access Token Secret の取得方法

X APIで投稿機能を使用するには、**4つの認証情報**が必要です：

1. ✅ API Key（Consumer Key）- 取得済み
2. ✅ API Secret Key（Consumer Secret）- 取得済み
3. ❌ Access Token - **これが必要です**
4. ❌ Access Token Secret - **これが必要です**

## 🔍 Access Token と Access Token Secret の取得手順

### ステップ1: Developer Portalにアクセス

1. [X Developer Portal](https://developer.twitter.com/)にログイン
2. プロジェクトのダッシュボードを開く

### ステップ2: Keys and tokens タブを開く

1. 左メニューまたはプロジェクトのダッシュボードから「Keys and tokens」タブをクリック
2. ページを下にスクロール

### ステップ3: Access Token and Secret を生成

「Keys and tokens」タブには以下のセクションがあります：

1. **API Key and Secret**（既に取得済み）
   - API Key
   - API Secret Key

2. **Access Token and Secret** ← **ここを探してください**
   - 「Generate」または「Regenerate」ボタンがあるはずです
   - このセクションでAccess TokenとAccess Token Secretを生成できます

### ステップ4: 生成とコピー

1. 「Access Token and Secret」セクションで「Generate」をクリック
2. 以下の2つが表示されます：
   - **Access Token**（長い文字列）
   - **Access Token Secret**（長い文字列）
3. **すぐにコピー**して安全な場所に保存
   - **重要**: これらのトークンは再表示できません
   - 紛失した場合は再生成が必要です

## ⚠️ 見つからない場合の対処法

### パターン1: 「Access Token and Secret」セクションが表示されない

**原因**: アプリの権限が「Read only」になっている可能性があります。

**解決方法**:
1. 「Keys and tokens」タブで「App permissions」を確認
2. 「Edit」をクリック
3. 「Read and Write」または「Read and Write and Direct message」を選択
4. 「Save」をクリック
5. ページを再読み込み
6. 「Access Token and Secret」セクションが表示されるはずです
7. 再度「Generate」をクリック

### パターン2: 「Generate」ボタンがグレーアウトしている

**原因**: 既に生成済みで、再生成が必要な場合があります。

**解決方法**:
1. 「Regenerate」ボタンをクリック
2. 既存のトークンが無効になることを確認
3. 新しいトークンを生成

### パターン3: 権限を変更した後、Access Tokenが表示されない

**原因**: 権限変更後、Access Tokenを再生成する必要があります。

**解決方法**:
1. 「Access Token and Secret」セクションで「Regenerate」をクリック
2. 新しいAccess TokenとAccess Token Secretを生成
3. GitHub Secretsを更新

## 📋 確認チェックリスト

以下の4つすべてが取得できているか確認してください：

- [ ] API Key（Consumer Key）
- [ ] API Secret Key（Consumer Secret）
- [ ] Access Token ← **これが必要**
- [ ] Access Token Secret ← **これが必要**

## 🔐 GitHub Secrets への設定

4つすべて取得できたら、GitHub Secretsに設定します：

1. GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」
2. 以下の4つのSecretsを追加：

   - **Name**: `X_API_KEY`
     - **Value**: API Key（Consumer Key）

   - **Name**: `X_API_SECRET`
     - **Value**: API Secret Key（Consumer Secret）

   - **Name**: `X_ACCESS_TOKEN`
     - **Value**: Access Token ← **新しく取得したもの**

   - **Name**: `X_ACCESS_TOKEN_SECRET`
     - **Value**: Access Token Secret ← **新しく取得したもの**

## 💡 よくある質問

**Q: API KeyとAccess Tokenの違いは？**
- **API Key（Consumer Key）**: アプリケーションを識別するためのキー
- **Access Token**: 特定のユーザー（Xアカウント）として操作するためのトークン
- 投稿機能を使用するには、両方が必要です

**Q: 2つだけでは投稿できないの？**
- いいえ、投稿機能には4つすべてが必要です
- API KeyとAPI Secret Keyだけでは、アプリケーションを識別できますが、ユーザーとして操作するにはAccess TokenとAccess Token Secretが必要です

**Q: Access Tokenを再生成するとどうなる？**
- 古いAccess Tokenは無効になります
- GitHub Secretsを新しいトークンで更新する必要があります

## 📚 参考

- [X API v2 認証ドキュメント](https://developer.twitter.com/en/docs/authentication/oauth-1-0a)
- [X Developer Portal](https://developer.twitter.com/en/portal/dashboard)
