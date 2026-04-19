# X（Twitter）自動投稿ボット設定ガイド

RSSフィードを監視し、新しいエピソードが配信されたら自動的にX（Twitter）に投稿する機能の設定方法を説明します。

## 📋 概要

IFTTTなどの外部サービスを使わずに、GitHub ActionsでRSSフィードを監視し、新しいエピソードを検出したらXに自動投稿します。

## 🔧 設定方法

### 1. X APIの認証情報を取得

**📖 詳しい手順は [X APIキー取得ガイド](X_API_SETUP.md) を参照してください。**

X API v2の投稿エンドポイント（POST /2/tweets）を使用するには、**OAuth 1.0a 方式**の4つの認証情報が必要です。

> ⚠️ **重要**: Bearer Token（Application-Only）は投稿には使用できません。OAuth 1.0a User Context 方式が必要です。

必要な認証情報：
- API Key（Consumer Key）
- API Secret Key（Consumer Secret）
- Access Token
- Access Token Secret

### 2. GitHub Secrets に設定

1. GitHubリポジトリの「Settings」を開く
2. 「Secrets and variables」→「Actions」を選択
3. 「New repository secret」をクリック
4. 以下のSecretsを追加：

| Name | Value |
|------|-------|
| `X_API_KEY` | API Key |
| `X_API_SECRET` | API Secret Key |
| `X_ACCESS_TOKEN` | Access Token |
| `X_ACCESS_TOKEN_SECRET` | Access Token Secret |

### 3. ワークフローの確認

`.github/workflows/post_to_x.yml`が正しく設定されているか確認してください。

デフォルトでは**毎時0分**にRSSフィードをチェックします。

---

## 🚀 動作の仕組み

1. **RSSフィードのチェック**: 指定されたスケジュールでRSSフィードを取得
2. **新規エピソードの検出**: 前回チェック時の最新エピソード番号と比較
3. **Xへの投稿**: 新しいエピソードがあれば、自動的にXに投稿
4. **状態の保存**: 最新エピソード番号を`.github/last_episode_state.json`に保存

---

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

---

## 🔍 トラブルシューティング

### 投稿されない場合

1. **GitHub Secretsの確認**: 認証情報が正しく設定されているか確認
2. **ワークフローの実行ログ**: GitHub Actionsのログを確認してエラーがないか確認
3. **X APIの制限**: X APIのレート制限に達していないか確認
4. **RSSフィードの確認**: RSSフィードが正しく取得できているか確認

### エラーメッセージ

| エラー | 原因 | 解決方法 |
|--------|------|----------|
| `X API認証情報が不足しています` | GitHub Secretsが設定されていない | 4つのSecretsを全て設定 |
| `Xへのポストに失敗しました` | X APIの認証エラーまたはレート制限 | 認証情報を再確認、レート制限を確認 |
| `最新エピソードの取得に失敗しました` | RSSフィードの取得に失敗 | インターネット接続を確認 |

---

## 📊 実行頻度の変更

デフォルトでは毎時0分にチェックしますが、`.github/workflows/post_to_x.yml`の`cron`設定を変更することで調整できます。

例：
| 頻度 | cron設定 |
|------|----------|
| 30分ごと | `*/30 * * * *` |
| 15分ごと | `*/15 * * * *` |
| 毎日6:00 JST | `0 21 * * *` (UTC 21:00) |

---

## 🔒 セキュリティ

- X APIの認証情報はGitHub Secretsに保存され、暗号化されています
- 認証情報はワークフローのログに表示されません
- 状態ファイル（`.github/last_episode_state.json`）はGit管理に含まれますが、機密情報は含まれません

---

## 📚 関連ドキュメント

- **[X APIキー取得ガイド](X_API_SETUP.md)** - APIキー取得の詳しい手順
- **[X開発者ポリシー説明文](X_DEVELOPER_POLICY.md)** - 申請用テンプレート
- [GitHub Actions公式ドキュメント](https://docs.github.com/ja/actions)
- [X API v2ドキュメント](https://developer.twitter.com/en/docs/twitter-api)
- [ワークフローガイド](../workflow/WORKFLOW_GUIDE.md)