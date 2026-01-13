#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSSフィードをチェックして新しいエピソードがあればX（Twitter）にポストするスクリプト
"""

import feedparser
import json
import os
import sys
import re
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import requests
from requests_oauthlib import OAuth1

# 共通ユーティリティのインポート
from utils import extract_episode_number, PROJECT_ROOT

# RSSフィードURL
RSS_FEED_URL = "https://anchor.fm/s/6981b208/podcast/rss"

# 状態ファイルのパス（前回の最新エピソード番号を保存）
STATE_FILE = PROJECT_ROOT / ".github" / "last_episode_state.json"

# X API設定（環境変数から取得）
X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")
X_BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")  # Bearer Token方式の場合

# X API v2 エンドポイント
X_API_V2_POST_URL = "https://api.twitter.com/2/tweets"


def load_last_episode_state() -> Optional[str]:
    """
    前回の最新エピソード番号を読み込む
    
    Returns:
        前回の最新エピソード番号、存在しない場合はNone
    """
    if not STATE_FILE.exists():
        return None
    
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('last_episode_number')
    except Exception as e:
        print(f"[WARNING] 状態ファイルの読み込みに失敗: {e}")
        return None


def save_last_episode_state(episode_number: str) -> None:
    """
    最新エピソード番号を保存
    
    Args:
        episode_number: エピソード番号
    """
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        'last_episode_number': episode_number,
        'updated_at': datetime.now().isoformat()
    }
    
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_latest_episode_from_rss() -> Optional[Dict[str, Any]]:
    """
    RSSフィードから最新のエピソードを取得
    
    Returns:
        最新エピソードの情報、取得できない場合はNone
    """
    print(f"[INFO] RSSフィードを取得中: {RSS_FEED_URL}")
    feed = feedparser.parse(RSS_FEED_URL)
    
    if feed.bozo:
        print(f"[WARNING] RSSフィードの解析にエラーがあります: {feed.bozo_exception}")
    
    if not feed.entries:
        print("[ERROR] RSSフィードにエントリーが見つかりません")
        return None
    
    # 最新のエントリー（最初のエントリー）を取得
    entry = feed.entries[0]
    
    # エピソード番号を抽出
    episode_number = extract_episode_number(entry.title)
    if not episode_number:
        print(f"[WARNING] エピソード番号が取得できませんでした: {entry.title}")
        return None
    
    return {
        'number': episode_number,
        'title': entry.title,
        'link': entry.get('link', ''),
        'published': entry.get('published', '')
    }


def create_tweet_text(episode: Dict[str, Any]) -> str:
    """
    ツイート文を作成
    
    Args:
        episode: エピソード情報
        
    Returns:
        ツイート文
    """
    # エピソード番号とタイトルを取得
    episode_number = episode['number']
    title = episode['title']
    
    # タイトルから「epX.X.X」の部分を除去（重複を避ける）
    title_clean = re.sub(r'^ep\d+\.\d+\.\d+\s+', '', title, flags=re.IGNORECASE).strip()
    
    # Spotify URLを取得（可能であれば）
    spotify_url = episode.get('link', '')
    if not spotify_url or 'spotify.com' not in spotify_url:
        spotify_url = "https://open.spotify.com/show/31JfR2D72gENOfOwq3AcKw"
    
    # ツイート文を作成（280文字以内）
    tweet = f"🎙️ 新着エピソード配信！\n\n{title_clean}\n\n#{episode_number.replace('.', '_')} #シビックテック井戸端キャスト\n\n{spotify_url}"
    
    # 280文字を超える場合は短縮
    if len(tweet) > 280:
        # タイトルを短縮
        max_title_length = 280 - len(f"🎙️ 新着エピソード配信！\n\n\n\n#{episode_number.replace('.', '_')} #シビックテック井戸端キャスト\n\n{spotify_url}")
        if max_title_length > 0:
            title_short = title_clean[:max_title_length - 3] + "..."
            tweet = f"🎙️ 新着エピソード配信！\n\n{title_short}\n\n#{episode_number.replace('.', '_')} #シビックテック井戸端キャスト\n\n{spotify_url}"
        else:
            # タイトルが長すぎる場合は最小構成
            tweet = f"🎙️ 新着エピソード配信！\n\n#{episode_number.replace('.', '_')} #シビックテック井戸端キャスト\n\n{spotify_url}"
    
    return tweet


def post_to_x_v2_oauth1(tweet_text: str) -> bool:
    """
    OAuth 1.0aを使用してXにポスト（X API v2）
    
    Args:
        tweet_text: ツイート文
        
    Returns:
        成功した場合True
    """
    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
        print("[ERROR] X API認証情報が不足しています（OAuth 1.0a）")
        return False
    
    auth = OAuth1(
        X_API_KEY,
        X_API_SECRET,
        X_ACCESS_TOKEN,
        X_ACCESS_TOKEN_SECRET
    )
    
    payload = {
        "text": tweet_text
    }
    
    try:
        response = requests.post(
            X_API_V2_POST_URL,
            json=payload,
            auth=auth,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"[OK] Xにポストしました: {result.get('data', {}).get('id', 'N/A')}")
            return True
        else:
            print(f"[ERROR] Xへのポストに失敗しました: {response.status_code}")
            print(f"レスポンス: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Xへのポスト中にエラーが発生しました: {e}")
        return False


def post_to_x_v2_bearer(tweet_text: str) -> bool:
    """
    Bearer Tokenを使用してXにポスト（X API v2）
    
    Args:
        tweet_text: ツイート文
        
    Returns:
        成功した場合True
    """
    if not X_BEARER_TOKEN:
        print("[ERROR] X Bearer Tokenが設定されていません")
        return False
    
    headers = {
        "Authorization": f"Bearer {X_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": tweet_text
    }
    
    try:
        response = requests.post(
            X_API_V2_POST_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"[OK] Xにポストしました: {result.get('data', {}).get('id', 'N/A')}")
            return True
        else:
            print(f"[ERROR] Xへのポストに失敗しました: {response.status_code}")
            print(f"レスポンス: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Xへのポスト中にエラーが発生しました: {e}")
        return False


def post_to_x(tweet_text: str) -> bool:
    """
    Xにポスト（認証方法を自動選択）
    
    Args:
        tweet_text: ツイート文
        
    Returns:
        成功した場合True
    """
    # Bearer Token方式を優先
    if X_BEARER_TOKEN:
        return post_to_x_v2_bearer(tweet_text)
    # OAuth 1.0a方式
    elif all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
        return post_to_x_v2_oauth1(tweet_text)
    else:
        print("[ERROR] X API認証情報が設定されていません")
        print("[INFO] 以下の環境変数を設定してください:")
        print("  - X_BEARER_TOKEN（推奨）")
        print("  または")
        print("  - X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET")
        return False


def main() -> None:
    """メイン処理"""
    print("[PODCAST] シビックテック井戸端キャスト - X投稿スクリプト")
    print("=" * 60)
    
    # 前回の最新エピソード番号を読み込む
    last_episode_number = load_last_episode_state()
    print(f"[INFO] 前回の最新エピソード: {last_episode_number or 'なし'}")
    
    # RSSフィードから最新エピソードを取得
    latest_episode = get_latest_episode_from_rss()
    
    if not latest_episode:
        print("[ERROR] 最新エピソードの取得に失敗しました")
        sys.exit(1)
    
    current_episode_number = latest_episode['number']
    print(f"[INFO] 現在の最新エピソード: {current_episode_number}")
    
    # 新しいエピソードかチェック
    if last_episode_number == current_episode_number:
        print("[INFO] 新しいエピソードはありません")
        sys.exit(0)
    
    print(f"[INFO] 新しいエピソードを検出: {current_episode_number}")
    
    # ツイート文を作成
    tweet_text = create_tweet_text(latest_episode)
    print(f"\n[INFO] ツイート内容:\n{tweet_text}\n")
    
    # Xにポスト
    if post_to_x(tweet_text):
        # 成功したら最新エピソード番号を保存
        save_last_episode_state(current_episode_number)
        print("\n" + "=" * 60)
        print("[SUCCESS] Xへの投稿が完了しました！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("[ERROR] Xへの投稿に失敗しました")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
