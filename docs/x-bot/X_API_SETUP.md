# X API キー取得ガイド

X（Twitter）API v2 を使用して自動投稿機能を設定するための、APIキー取得手順を詳しく説明します。

## 📋 前提条件

- X（Twitter）アカウントを持っていること
- メールアドレスと電話番号が認証済みであること

## 🔑 必要な認証情報

X API v2 の投稿エンドポイント（POST /2/tweets）を使用するには、**OAuth 1.0a 方式**の以下の4つの認証情報が必要です：

| 認証情報 | 別名 | 用途 |
|---------|------|------|
| API Key | Consumer Key | アプリケーションを識別 |
| API Secret Key | Consumer Secret | アプリケーションの秘密鍵 |
| Access Token | - | ユーザーとして操作するためのトークン |
| Access Token Secret | - | Access Token の秘密鍵 |

> ⚠️ **重要**: Bearer Token（Application-Only）は投稿エンドポイントでは使用できません。OAuth 1.0a User Context 方式が必要です。

---

## 🚀 取得手順

### ステップ1: X Developer Portal にアクセス

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

**申請用のポリシー説明文**は、[X_DEVELOPER_POLICY.md](X_DEVELOPER_POLICY.md) をご覧ください。

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

1. プロジェクトのダッシュボードで「Keys and tokens」タブを開く
2. 以下の4つの認証情報を取得：

#### a. API Key と API Secret Key

1. 「API Key and Secret」セクションで「Generate」をクリック
2. 生成された「API Key」と「API Secret Key」をコピー
3. **重要**: API Secret Keyは再表示できません

#### b. Access Token と Access Token Secret

1. 「Access Token and Secret」セクションで「Generate」をクリック
2. 生成された「Access Token」と「Access Token Secret」をコピー
3. **重要**: Access Token Secretは再表示できません

> 💡 **見つからない場合**: 「Access Token and Secret」セクションが表示されない場合は、[トラブルシューティング](#トラブルシューティング) をご覧ください。

### ステップ5: 権限の設定

1. 「Keys and tokens」タブで「App permissions」を確認
2. 投稿機能を使用するため、以下を設定：
   - **Read and Write**（推奨）: 読み取りと投稿が可能
3. 必要に応じて「Edit」をクリックして変更
4. 変更後、Access Tokenを再生成する必要がある場合があります

### ステップ6: GitHub Secrets に設定

取得した認証情報をGitHub Secretsに設定します。

1. GitHubリポジトリのページを開く
2. 「Settings」タブをクリック
3. 左メニューから「Secrets and variables」→「Actions」を選択
4. 「New repository secret」をクリック

以下の4つのSecretsを追加：

| Name | Value |
|------|-------|
| `X_API_KEY` | API Key |
| `X_API_SECRET` | API Secret Key |
| `X_ACCESS_TOKEN` | Access Token |
| `X_ACCESS_TOKEN_SECRET` | Access Token Secret |

### ステップ7: 動作確認

1. GitHubリポジトリの「Actions」タブを開く
2. 「Post to X on New Episode」ワークフローを選択
3. 「Run workflow」をクリックして手動実行
4. 実行ログを確認して、エラーがないか確認

---

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

---

## 🔧 認証情報の再生成

認証情報を紛失した場合や、セキュリティ上の理由で再生成したい場合：

1. Developer Portalの「Keys and tokens」タブを開く
2. 該当する認証情報の「Regenerate」をクリック
3. 新しい認証情報をコピー
4. GitHub Secretsを更新

**注意**: 認証情報を再生成すると、古い認証情報は無効になります。

---

## 🐛 トラブルシューティング

### Access Token が見つからない

#### パターン1: 「Access Token and Secret」セクションが表示されない

**原因**: アプリの権限が「Read only」になっている可能性があります。

**解決方法**:
1. 「Keys and tokens」タブで「App permissions」を確認
2. 「Edit」をクリック
3. 「Read and Write」を選択
4. 「Save」をクリック
5. ページを再読み込み
6. 「Access Token and Secret」セクションが表示されるはずです
7. 再度「Generate」をクリック

#### パターン2: 「Generate」ボタンがグレーアウトしている

**原因**: 既に生成済みで、再生成が必要な場合があります。

**解決方法**:
1. 「Regenerate」ボタンをクリック
2. 既存のトークンが無効になることを確認
3. 新しいトークンを生成

### 投稿が失敗する（403エラー: Unsupported Authentication）

**原因**: Bearer Token は投稿エンドポイントでは使用できません。

**解決方法**:
1. OAuth 1.0a 方式の4つの認証情報が正しく設定されているか確認
2. 権限が「Read and Write」になっているか確認
3. Access Tokenを再生成してみる
4. ワークフローのログでエラーメッセージを確認

### 開発者アカウントの申請が承認されない

- 申請内容を詳しく記入する
- 使用目的を明確に説明する
- 数日待ってから再申請を検討

---

## 📚 参考リンク

- [X Developer Portal](https://developer.twitter.com/)
- [X API v2 ドキュメント](https://developer.twitter.com/en/docs/twitter-api)
- [X API 料金プラン](https://developer.twitter.com/en/products/twitter-api)
- [GitHub Actions Secrets ドキュメント](https://docs.github.com/ja/actions/security-guides/encrypted-secrets)
- [Xボット設定ガイド](X_BOT_SETUP.md) - GitHub Actionsでの設定方法
- [X開発者ポリシー説明文](X_DEVELOPER_POLICY.md) - 申請用テンプレート