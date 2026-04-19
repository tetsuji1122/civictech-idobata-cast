# ドキュメント索引

このディレクトリには、civictech-idobata-cast プロジェクトのドキュメントがカテゴリ別に整理されています。

## 📂 カテゴリ別ドキュメント一覧

### 🔄 ワークフロー（01-workflow）

ポッドキャストの収録から公開までの一連の流れを説明します。

| ドキュメント | 内容 |
|-------------|------|
| [WORKFLOW_GUIDE.md](workflow/WORKFLOW_GUIDE.md) | 書き起こし作成から公開までの全体フロー |
| [TRANSCRIPT_README.md](workflow/TRANSCRIPT_README.md) | 書き起こしデータの管理方法 |
| [UPDATE_EPISODES_README.md](workflow/UPDATE_EPISODES_README.md) | RSSフィードからのエピソード更新 |

**初心者向け読み順**: `WORKFLOW_GUIDE.md` → `TRANSCRIPT_README.md` → `UPDATE_EPISODES_README.md`

---

### 🐍 スクリプト（02-scripts）

Pythonスクリプトの使用方法と設定を説明します。

| ドキュメント | 内容 |
|-------------|------|
| [SCRIPTS_README.md](scripts/SCRIPTS_README.md) | 全スクリプトの一覧と基本的な使い方 |
| [WORD_TRENDS_README.md](scripts/WORD_TRENDS_README.md) | 頻出ワード年表の生成方法 |
| [CONFIG_README.md](scripts/CONFIG_README.md) | 共通設定（config.js）の説明 |

**初心者向け読み順**: `SCRIPTS_README.md` → 各スクリプトの詳細ドキュメント

---

### 🤖 X（Twitter）ボット（03-x-bot）

X（旧Twitter）への自動投稿ボットの設定方法を説明します。

| ドキュメント | 内容 |
|-------------|------|
| [X_API_SETUP.md](x-bot/X_API_SETUP.md) | X APIキーの取得方法（OAuth 1.0a） |
| [X_BOT_SETUP.md](x-bot/X_BOT_SETUP.md) | GitHub Actionsでのボット設定 |
| [X_DEVELOPER_POLICY.md](x-bot/X_DEVELOPER_POLICY.md) | 開発者アカウント申請用ポリシー説明文 |

**初心者向け読み順**: `X_API_SETUP.md` → `X_BOT_SETUP.md`

---

### 📚 リファレンス（04-reference）

技術的な詳細とベストプラクティスを説明します。

| ドキュメント | 内容 |
|-------------|------|
| [SECURITY_GUIDE.md](reference/SECURITY_GUIDE.md) | APIキー管理とセキュリティベストプラクティス |
| [SEO_GUIDE.md](reference/SEO_GUIDE.md) | SEO対策の実装詳細 |

---

## 🚀 クイックスタート

### 初めての方へ

1. **[ワークフローガイド](workflow/WORKFLOW_GUIDE.md)** を読んで全体の流れを把握
2. **[スクリプト一覧](scripts/SCRIPTS_README.md)** で必要なスクリプトを確認
3. 各スクリプトの詳細ドキュメントで具体的な使用方法を確認

### Xボットを設定したい方

1. **[X API取得ガイド](x-bot/X_API_SETUP.md)** でAPIキーを取得
2. **[Xボット設定ガイド](x-bot/X_BOT_SETUP.md)** でGitHub Actionsを設定

---

## 📝 ドキュメントのメンテナンス

このドキュメント構造は、プロジェクトの成長に合わせて適宜見直されます。

- 新規ドキュメントの追加
- 既存ドキュメントの統合・削除
- 構造の再編成

変更の提案は、GitHubのIssueまたはPull Requestでお知らせください。

---

**最終更新**: 2026-04-12