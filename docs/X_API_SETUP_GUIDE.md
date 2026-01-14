# X（Twitter）APIキー取得ガイド

X（Twitter）API v2を使用して自動投稿機能を設定するための、APIキー取得手順を詳しく説明します。

## 📋 前提条件

- X（Twitter）アカウントを持っていること
- メールアドレスと電話番号が認証済みであること

## 🚀 手順

### ステップ1: X Developer Portalにアクセス

1. ブラウザで [X Developer Portal](https://developer.twitter.com/) にアクセス
2. Xアカウントでログイン

### ステップ2: 開発者アカウントの申請（初回のみ）

**重要**: 初めてX APIを使用する場合は、開発者アカウントの申請が必要です。

1. 「Sign up」または「Apply」をクリック
2. 申請フォームに記入：
   - **使用目的**: 「Making a bot」または「Exploring the API」を選択
   - **使用用途**: ポッドキャストの新着エピソードを自動投稿するため
   - **アカウント情報**: 使用するXアカウントを選択
3. 利用規約に同意して申請
4. 審査が完了するまで待機（通常数時間〜数日）

### ステップ3: プロジェクトとアプリの作成

審査が完了したら、プロジェクトとアプリを作成します。

#### 3-1. プロジェクトの作成

1. Developer Portalのダッシュボードで「Create Project」をクリック
2. プロジェクト名を入力（例: "Civictech Cast Bot"）
3. 使用目的を選択（例: "Making a bot"）
4. プロジェクトの説明を入力（例: "ポッドキャストの新着エピソードを自動投稿するボット"）
5. 「Next」をクリック

#### 3-2. アプリの作成

1. アプリ名を入力（例: "civictech-cast-bot"）
   - **注意**: アプリ名は一意である必要があります
2. 「Next」をクリック
3. APIキーの生成を確認
4. 「Create App」をクリック

### ステップ4: APIキーとトークンの取得

プロジェクトとアプリが作成されると、認証情報を取得できます。

#### OAuth 1.0a（必須）

**重要**: X API v2の投稿エンドポイント（POST /2/tweets）はOAuth 1.0a User Contextが必要です。
Bearer Token（Application-Only）は投稿には使用できません。

**取得手順**:

1. プロジェクトのダッシュボードで「Keys and tokens」タブを開く
2. 以下の4つの認証情報を取得：

   **a. API Key と API Secret Key**
   - 「API Key and Secret」セクションで「Generate」をクリック
   - 生成された「API Key」と「API Secret Key」をコピー
   - **重要**: API Secret Keyは再表示できません

   **b. Access Token と Access Token Secret**
   - 「Access Token and Secret」セクションで「Generate」をクリック
   - 生成された「Access Token」と「Access Token Secret」をコピー
   - **重要**: Access Token Secretは再表示できません

### ステップ5: 権限の設定

1. 「Keys and tokens」タブで「App permissions」を確認
2. 投稿機能を使用するため、以下のいずれかを設定：
   - **Read and Write**（推奨）: 読み取りと投稿が可能
   - **Read and Write and Direct message**: さらにDM送信も可能
3. 必要に応じて「Edit」をクリックして変更
4. 変更後、Access Tokenを再生成する必要がある場合があります

### ステップ6: GitHub Secretsに設定

取得した認証情報をGitHub Secretsに設定します。

1. GitHubリポジトリのページを開く
2. 「Settings」タブをクリック
3. 左メニューから「Secrets and variables」→「Actions」を選択
4. 「New repository secret」をクリック

#### OAuth 1.0a方式（必須）:

以下の4つのSecretsを追加：

1. **Name**: `X_API_KEY`
   - **Value**: API Key

2. **Name**: `X_API_SECRET`
   - **Value**: API Secret Key

3. **Name**: `X_ACCESS_TOKEN`
   - **Value**: Access Token

4. **Name**: `X_ACCESS_TOKEN_SECRET`
   - **Value**: Access Token Secret

### ステップ7: 動作確認

1. GitHubリポジトリの「Actions」タブを開く
2. 「Post to X on New Episode」ワークフローを選択
3. 「Run workflow」をクリックして手動実行
4. 実行ログを確認して、エラーがないか確認

## ⚠️ 注意事項

### セキュリティ

- **認証情報は絶対に公開しないでください**
- GitHub Secretsに設定した認証情報は暗号化されて保存されます
- 認証情報をコミットやプッシュに含めないでください
- 認証情報を紛失した場合は、Developer Portalで再生成してください

### API制限

- X API v2にはレート制限があります
- 無料プランでは以下の制限があります：
  - 投稿: 1,500ツイート/月
  - 読み取り: 10,000ツイート/月
- 制限に達した場合は、翌月まで待つか、有料プランにアップグレード

### よくある問題

**Q: 開発者アカウントの申請が承認されない**
- 申請内容を詳しく記入する
- 使用目的を明確に説明する
- 数日待ってから再申請を検討

**Q: APIキーが表示されない**
- プロジェクトとアプリが正しく作成されているか確認
- ブラウザのキャッシュをクリアして再読み込み

**Q: 投稿が失敗する（403エラー: Unsupported Authentication）**
- **重要**: Bearer Tokenは投稿エンドポイントでは使用できません
- OAuth 1.0a方式の4つの認証情報（API Key, API Secret, Access Token, Access Token Secret）が正しく設定されているか確認
- 権限が「Read and Write」になっているか確認
- Access Tokenを再生成してみる
- ワークフローのログでエラーメッセージを確認

## 📚 参考リンク

- [X Developer Portal](https://developer.twitter.com/)
- [X API v2 ドキュメント](https://developer.twitter.com/en/docs/twitter-api)
- [X API 料金プラン](https://developer.twitter.com/en/products/twitter-api)
- [GitHub Actions Secrets ドキュメント](https://docs.github.com/ja/actions/security-guides/encrypted-secrets)

## 🔄 認証情報の再生成

認証情報を紛失した場合や、セキュリティ上の理由で再生成したい場合：

1. Developer Portalの「Keys and tokens」タブを開く
2. 該当する認証情報の「Regenerate」をクリック
3. 新しい認証情報をコピー
4. GitHub Secretsを更新

**注意**: 認証情報を再生成すると、古い認証情報は無効になります。
