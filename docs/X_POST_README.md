# X（Twitter）自動投稿機能

RSSフィードを監視し、新しいエピソードが配信されたら自動的にX（Twitter）に投稿する機能です。

## 📋 概要

IFTTTなどの外部サービスを使わずに、GitHub ActionsでRSSフィードを監視し、新しいエピソードを検出したらXに自動投稿します。

## 🔧 設定方法

### 1. X APIの認証情報を取得

**📖 詳しい手順は [X APIキー取得ガイド](X_API_SETUP_GUIDE.md) を参照してください。**

X API v2を使用するため、以下のいずれかの方法で認証情報を取得します。

#### 方法A: Bearer Token（推奨・簡単）

1. [X Developer Portal](https://developer.twitter.com/)にログイン
2. 開発者アカウントの申請（初回のみ）
3. プロジェクトとアプリを作成
4. 「Keys and tokens」タブで「Bearer Token」を生成
5. 生成されたBearer Tokenをコピー（再表示不可のため注意）

#### 方法B: OAuth 1.0a（4つの認証情報が必要）

1. [X Developer Portal](https://developer.twitter.com/)にログイン
2. 開発者アカウントの申請（初回のみ）
3. プロジェクトとアプリを作成
4. 「Keys and tokens」タブで以下の4つを取得：
   - API Key
   - API Secret Key
   - Access Token
   - Access Token Secret

### 2. GitHub Secretsに設定

1. GitHubリポジトリの「Settings」を開く
2. 「Secrets and variables」→「Actions」を選択
3. 「New repository secret」をクリック
4. 以下のSecretsを追加：

**Bearer Token方式（推奨）の場合:**
- Name: `X_BEARER_TOKEN`
- Value: 取得したBearer Token

**OAuth 1.0a方式の場合:**
- Name: `X_API_KEY` → Value: API Key
- Name: `X_API_SECRET` → Value: API Secret Key
- Name: `X_ACCESS_TOKEN` → Value: Access Token
- Name: `X_ACCESS_TOKEN_SECRET` → Value: Access Token Secret

### 3. ワークフローの確認

`.github/workflows/post_to_x.yml`が正しく設定されているか確認してください。

デフォルトでは**毎時0分**にRSSフィードをチェックします。

## 🚀 動作の仕組み

1. **RSSフィードのチェック**: 指定されたスケジュールでRSSフィードを取得
2. **新規エピソードの検出**: 前回チェック時の最新エピソード番号と比較
3. **Xへの投稿**: 新しいエピソードがあれば、自動的にXに投稿
4. **状態の保存**: 最新エピソード番号を`.github/last_episode_state.json`に保存

## 📝 投稿内容

投稿されるツイートの形式：

```
🎙️ 新着エピソード配信！

[エピソードタイトル]

#[エピソード番号] #シビックテック井戸端キャスト

[Spotify URL]
```

例：
```
🎙️ 新着エピソード配信！

生成AIが拓くシビックテックの未来

#1_0_12 #シビックテック井戸端キャスト

https://open.spotify.com/show/31JfR2D72gENOfOwq3AcKw
```

## 🔍 トラブルシューティング

### 投稿されない場合

1. **GitHub Secretsの確認**: 認証情報が正しく設定されているか確認
2. **ワークフローの実行ログ**: GitHub Actionsのログを確認してエラーがないか確認
3. **X APIの制限**: X APIのレート制限に達していないか確認
4. **RSSフィードの確認**: RSSフィードが正しく取得できているか確認

### エラーメッセージ

- `X API認証情報が不足しています`: GitHub Secretsが設定されていない
- `Xへのポストに失敗しました`: X APIの認証エラーまたはレート制限
- `最新エピソードの取得に失敗しました`: RSSフィードの取得に失敗

## 📊 実行頻度の変更

デフォルトでは毎時0分にチェックしますが、`.github/workflows/post_to_x.yml`の`cron`設定を変更することで調整できます。

例：
- 30分ごと: `'*/30 * * * *'`
- 15分ごと: `'*/15 * * * *'`
- 毎日6:00 JST: `'0 21 * * *'` (UTC 21:00)

## 🔒 セキュリティ

- X APIの認証情報はGitHub Secretsに保存され、暗号化されています
- 認証情報はワークフローのログに表示されません
- 状態ファイル（`.github/last_episode_state.json`）はGit管理に含まれますが、機密情報は含まれません

## 📚 関連ドキュメント

- **[X APIキー取得ガイド](X_API_SETUP_GUIDE.md)** - APIキー取得の詳しい手順
- [GitHub Actions公式ドキュメント](https://docs.github.com/ja/actions)
- [X API v2ドキュメント](https://developer.twitter.com/en/docs/twitter-api)
- [ワークフローガイド](WORKFLOW_GUIDE.md)
