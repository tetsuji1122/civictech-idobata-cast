#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ポッドキャストRSSフィードからエピソード情報を取得して episodes.json を更新するスクリプト
"""

import feedparser
import json
import re
import sys
import shutil
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any

# 共通ユーティリティのインポート
from utils import (
    extract_episode_number,
    format_duration,
    parse_date,
    EPISODES_JSON_PATH,
    TRANSCRIPTS_DIR
)

# 設定
RSS_FEED_URL = "https://anchor.fm/s/6981b208/podcast/rss"
SPOTIFY_SHOW_URL = "https://open.spotify.com/show/31JfR2D72gENOfOwq3AcKw"
DEFAULT_THUMBNAIL = "img/logo.png"

# タグシステムの定義
TAG_KEYWORDS_MAP = {
    'シビックテック': ['シビックテック', 'civictech', 'civic tech'],
    'Code for': ['code for', 'summit', 'ブリゲード', 'コミュニティ'],
    'データ': ['データ', 'オープンデータ', 'data', 'api', '統計', 'プラットフォーム'],
    'ゲスト': ['ゲスト', 'guest', '突撃', 'quiet talk', 'メンバーファイル'],
    'イベント': ['イベント', 'ふりかえり', 'ランキング', 'アドベントカレンダー', 'advent'],
    '技術': ['ai', 'gpt', 'sora', 'システム', 'アプリ', 'github', 'プログラミング', '開発', 'chatgpt'],
    '地域': ['地域', '富山', '長崎', '東京', '金沢', '福井', '石川', '都市', '市', '町'],
    'ライフスタイル': ['お店', 'グルメ', '日本酒', 'おいしい', '買ってよかった', 'クリスマス'],
    '文化': ['歴史', '文化', '社会', '教育', '猫'],
    '雑談': ['雑談', '予想', '占う']
}

TAG_PRIORITY = [
    'ゲスト', 'イベント', 'Code for', 'シビックテック',
    'データ', '技術', '地域', 'ライフスタイル', '文化', '雑談'
]


def extract_spotify_url(link: str) -> str:
    """
    RSSフィードからSpotify URLを抽出
    
    Args:
        link: チェックするURL
        
    Returns:
        Spotify関連のURLであればそのまま返す、そうでなければ空文字列
    """
    if 'spotify.com' in link or 'podcasters.spotify.com' in link:
        print(f"  → Spotify URL取得: {link}")
        return link
    
    print(f"  → Spotify URLではありません: {link}")
    return ""


def generate_tags(title: str, description: str, max_tags: int = 3) -> List[str]:
    """
    タイトルと説明からタグを自動生成
    
    Args:
        title: エピソードタイトル
        description: エピソード説明
        max_tags: 最大タグ数
        
    Returns:
        タグのリスト（最大max_tags個）
    """
    tags = set()
    text = (title + " " + description).lower()
    
    # キーワードマッチング
    for tag, keywords in TAG_KEYWORDS_MAP.items():
        if any(keyword in text for keyword in keywords):
            tags.add(tag)
    
    # タグがない場合はデフォルトで雑談を追加
    if not tags:
        tags.add('雑談')
    
    # 優先度順にソートして最大数まで返す
    sorted_tags = [tag for tag in TAG_PRIORITY if tag in tags]
    return sorted_tags[:max_tags] if sorted_tags else ['雑談']


def extract_urls_from_text(text: str) -> Tuple[str, List[str]]:
    """
    テキストからURLを抽出して除去
    
    Args:
        text: URL を含むテキスト
        
    Returns:
        (cleaned_text, urls_list): URLを除去したテキストとURLリスト
    """
    url_pattern = r'https?://[^\s<>"\'\)]+[^\s<>"\'\.,:;\)\]\}]'
    
    # URLを抽出
    urls = re.findall(url_pattern, text)
    
    # URLを削除（前後の空白も整理）
    cleaned_text = re.sub(url_pattern, '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    # 重複を除去
    unique_urls = list(dict.fromkeys(urls))
    
    return cleaned_text, unique_urls


def clean_description(description: str) -> str:
    """
    HTMLタグを除去して説明文をクリーンアップ
    
    Args:
        description: HTML を含む可能性のある説明文
        
    Returns:
        クリーンアップされた説明文
    """
    # HTMLタグを削除
    text = re.sub(r'<[^>]+>', '', description)
    # 余分な改行や空白を削除
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def check_transcript_exists(episode_number: str) -> bool:
    """
    書き起こしJSONファイルの存在をチェック
    
    Args:
        episode_number: エピソード番号（例: "1.0.12"）
    
    Returns:
        ファイルが存在する場合はTrue
    """
    transcript_file = TRANSCRIPTS_DIR / f"ep{episode_number}.json"
    return transcript_file.exists()


def create_episode_links(urls: List[str]) -> List[Dict[str, str]]:
    """
    URLリストからエピソードのリンクリストを作成
    
    Args:
        urls: URLのリスト
        
    Returns:
        リンク情報の辞書リスト
    """
    links = []
    excluded_domains = ['spotify.com', 'anchor.fm', 'cloudfront.net']
    
    for url in urls:
        if not any(domain in url for domain in excluded_domains):
            links.append({
                "title": "関連リンク",
                "url": url
            })
    
    return links


def fetch_episodes_from_rss(rss_url: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    RSSフィードからエピソード情報を取得
    
    Args:
        rss_url: RSSフィードのURL
        limit: 取得するエピソード数の上限（Noneの場合は全件取得）
        
    Returns:
        エピソード情報の辞書リスト
    """
    print(f"[INFO] RSSフィードを取得中: {rss_url}")
    feed = feedparser.parse(rss_url)
    
    if feed.bozo:
        print(f"[WARNING] RSSフィードの解析にエラーがあります: {feed.bozo_exception}")
    
    entries_to_process = feed.entries if limit is None else feed.entries[:limit]
    
    if limit:
        print(f"[INFO] 最新{limit}件のエピソードをチェックします")
    else:
        print(f"[INFO] 全{len(feed.entries)}件のエピソードをチェックします")
    
    episodes = []
    
    for entry in entries_to_process:
        # エピソード番号を抽出
        episode_number = extract_episode_number(entry.title)
        if not episode_number:
            print(f"[WARNING] エピソード番号が取得できませんでした: {entry.title}")
            continue
        
        # 基本情報を取得
        duration = format_duration(entry.get('itunes_duration', '0:00'))
        pub_date = parse_date(entry.published)
        raw_description = clean_description(entry.get('description', entry.get('summary', '')))
        
        # 説明文からURLを抽出
        description, extracted_urls = extract_urls_from_text(raw_description)
        
        # タグを生成
        tags = generate_tags(entry.title, description)
        
        # Spotify URLを取得
        spotify_url = ""
        if hasattr(entry, 'links'):
            for link in entry.links:
                link_href = link.get('href', '')
                if 'spotify.com/episode' in link_href or 'podcasters.spotify.com/pod/show' in link_href:
                    spotify_url = extract_spotify_url(link_href)
                    break
        
        # linksから見つからない場合はentry.linkをチェック
        if not spotify_url and hasattr(entry, 'link'):
            spotify_url = extract_spotify_url(entry.link)
        
        # それでも見つからない場合はデフォルトの番組URLを使用
        if not spotify_url:
            print(f"  [WARNING] {episode_number}: 個別エピソードURLが見つかりません。番組URLを使用します。")
            spotify_url = SPOTIFY_SHOW_URL
        
        # リンクリストを作成
        links = create_episode_links(extracted_urls)
        
        if extracted_urls:
            print(f"  → {episode_number}: 説明文から{len(extracted_urls)}個のURLを抽出（関連リンク: {len(links)}個）")
        
        # 書き起こしファイルの存在チェック
        has_transcript = check_transcript_exists(episode_number)
        
        episode_data = {
            "number": episode_number,
            "title": entry.title,
            "date": pub_date,
            "duration": duration,
            "description": description,
            "thumbnail": DEFAULT_THUMBNAIL,
            "spotifyUrl": spotify_url,
            "tags": tags,
            "transcript": "",
            "links": links,
            "has_transcript": has_transcript
        }
        
        episodes.append(episode_data)
    
    print(f"[OK] {len(episodes)}件のエピソードを取得しました")
    return episodes


def load_existing_episodes(json_path: Path) -> List[Dict[str, Any]]:
    """
    既存のepisodes.jsonを読み込む
    
    Args:
        json_path: JSONファイルのパス
        
    Returns:
        既存のエピソードリスト
    """
    if not json_path.exists():
        print(f"[INFO] {json_path} が存在しないため、新規作成します")
        return []
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('episodes', [])


def update_episode_transcript_flag(episode: Dict[str, Any]) -> bool:
    """
    エピソードの書き起こしフラグを更新
    
    Args:
        episode: エピソード情報の辞書
        
    Returns:
        更新があった場合True
    """
    current_has_transcript = check_transcript_exists(episode['number'])
    old_has_transcript = episode.get('has_transcript')
    
    if old_has_transcript != current_has_transcript:
        episode['has_transcript'] = current_has_transcript
        
        if old_has_transcript is None:
            print(f"  [UPDATE] {episode['number']}: 書き起こしファイル存在チェック追加 ({current_has_transcript})")
        else:
            print(f"  [UPDATE] {episode['number']}: 書き起こしファイル存在チェック更新 ({old_has_transcript} → {current_has_transcript})")
        
        return True
    
    return False


def merge_episodes(
    existing_episodes: List[Dict[str, Any]], 
    new_episodes: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], int, int, int, int]:
    """
    既存エピソードと新エピソードをマージ
    
    Args:
        existing_episodes: 既存のエピソードリスト
        new_episodes: 新規エピソードリスト
        
    Returns:
        (merged_episodes, added_count, updated_count, skipped_count, transcript_updated_count)
    """
    # 既存エピソードを辞書化（エピソード番号をキーに）
    existing_dict = {ep['number']: ep for ep in existing_episodes}
    
    added_episodes = []
    updated_count = 0
    skipped_count = 0
    transcript_updated_count = 0
    
    for new_ep in new_episodes:
        if new_ep['number'] not in existing_dict:
            # 新規エピソード
            new_ep['has_transcript'] = check_transcript_exists(new_ep['number'])
            added_episodes.append(new_ep)
        else:
            # 既存エピソードの場合、Spotify URLとlinksをチェック
            existing_ep = existing_dict[new_ep['number']]
            old_url = existing_ep.get('spotifyUrl', '')
            new_url = new_ep.get('spotifyUrl', '')
            updated = False
            
            # Spotify URLの更新チェック
            if old_url == SPOTIFY_SHOW_URL and new_url != SPOTIFY_SHOW_URL and 'episode' in new_url:
                existing_ep['spotifyUrl'] = new_url
                updated = True
                print(f"  [UPDATE] {new_ep['number']}: Spotify URL更新")
            
            # linksの更新チェック
            existing_links = existing_ep.get('links', [])
            new_links = new_ep.get('links', [])
            if not existing_links and new_links:
                existing_ep['links'] = new_links
                updated = True
                print(f"  [UPDATE] {new_ep['number']}: 関連リンク追加（{len(new_links)}件）")
            
            # 書き起こしファイルの存在チェック
            if update_episode_transcript_flag(existing_ep):
                updated = True
            
            if updated:
                updated_count += 1
            else:
                skipped_count += 1
    
    # 全既存エピソードの書き起こしフラグを更新
    for ep in existing_episodes:
        if update_episode_transcript_flag(ep):
            transcript_updated_count += 1
    
    if transcript_updated_count > 0:
        print(f"[INFO] 書き起こしファイル存在チェック更新: {transcript_updated_count}件")
    
    print(f"[INFO] 新規エピソード: {len(added_episodes)}件")
    print(f"[INFO] Spotify URL更新: {updated_count}件")
    if transcript_updated_count > 0:
        print(f"[INFO] 書き起こしフラグ更新: {transcript_updated_count}件")
    print(f"[INFO] 既存エピソード（変更なし）: {skipped_count}件")
    
    # transcript_updated_countをupdated_countに反映
    if transcript_updated_count > 0:
        updated_count += transcript_updated_count
    
    # 新規エピソードも更新もない場合
    if not added_episodes and updated_count == 0:
        print("[INFO] 新しいエピソードや更新はありません")
        return existing_episodes, 0, updated_count, skipped_count, transcript_updated_count
    
    # マージして配信日順にソート（昇順：古いエピソードが先頭）
    merged = added_episodes + existing_episodes
    merged.sort(key=lambda ep: ep.get('date', '9999-99-99'))
    
    # IDを振り直す（1から順番に）
    for i, ep in enumerate(merged, start=1):
        ep['id'] = i
    
    return merged, len(added_episodes), updated_count, skipped_count, transcript_updated_count


def save_episodes(episodes: List[Dict[str, Any]], json_path: Path, dry_run: bool = False) -> None:
    """
    episodes.jsonに保存
    
    Args:
        episodes: エピソードリスト
        json_path: 保存先のJSONファイルパス
        dry_run: Trueの場合は実際には保存しない
    """
    if dry_run:
        print("\n[DRY-RUN] 実際には保存しません")
        print("\n保存される内容のプレビュー:")
        print(json.dumps({"episodes": episodes[:3]}, indent=2, ensure_ascii=False))
        print(f"\n... 他 {len(episodes) - 3}件のエピソード")
        return
    
    # バックアップを作成
    if json_path.exists():
        backup_path = json_path.with_suffix('.json.backup')
        shutil.copy(json_path, backup_path)
        print(f"[BACKUP] バックアップを作成: {backup_path}")
    
    # 保存
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({"episodes": episodes}, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] {json_path} に保存しました")


def reindex_episodes(episodes: List[Dict[str, Any]], sort_by_date: bool = True) -> List[Dict[str, Any]]:
    """
    エピソードのIDを振り直す
    
    Args:
        episodes: エピソードのリスト
        sort_by_date: Trueの場合、配信日順（昇順）にソート
        
    Returns:
        IDを振り直したエピソードのリスト
    """
    if sort_by_date:
        episodes.sort(key=lambda ep: ep.get('date', '9999-99-99'))
        print(f"[INFO] 配信日順（昇順、古いものが先頭）にソートしました")
    
    # IDを振り直す
    for i, ep in enumerate(episodes, start=1):
        ep['id'] = i
    
    return episodes


def handle_reindex(args: argparse.Namespace) -> None:
    """
    既存episodes.jsonのIDを振り直す処理
    
    Args:
        args: コマンドライン引数
    """
    print("[PODCAST] シビックテック井戸端キャスト - ID振り直しスクリプト")
    print("=" * 60)
    
    # 既存エピソードを読み込み
    json_path = Path(args.output)
    existing_episodes = load_existing_episodes(json_path)
    print(f"[INFO] 既存エピソード: {len(existing_episodes)}件")
    
    if not existing_episodes:
        print("[ERROR] エピソードが見つかりません")
        return
    
    # 書き起こしフラグを更新
    transcript_updated_count = sum(
        update_episode_transcript_flag(ep) for ep in existing_episodes
    )
    
    if transcript_updated_count > 0:
        print(f"[INFO] 書き起こしファイル存在チェック更新: {transcript_updated_count}件")
    
    # IDを振り直す
    reindexed_episodes = reindex_episodes(existing_episodes, sort_by_date=True)
    
    # 保存
    save_episodes(reindexed_episodes, json_path, dry_run=args.dry_run)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] IDの振り直しが完了しました！")
    print(f"  合計エピソード数: {len(reindexed_episodes)}件")
    print("=" * 60)


def handle_update(args: argparse.Namespace) -> None:
    """
    RSSフィードから新規エピソードを取得して更新する処理
    
    Args:
        args: コマンドライン引数
    """
    print("[PODCAST] シビックテック井戸端キャスト - エピソード更新スクリプト")
    print("=" * 60)
    
    # RSSフィードから取得
    limit = None if args.limit == 0 else args.limit
    new_episodes = fetch_episodes_from_rss(RSS_FEED_URL, limit=limit)
    
    # 既存エピソードを読み込み
    json_path = Path(args.output)
    existing_episodes = load_existing_episodes(json_path)
    print(f"[INFO] 既存エピソード: {len(existing_episodes)}件")
    
    # マージ
    merged_episodes, added_count, updated_count, skipped_count, transcript_updated_from_merge = merge_episodes(
        existing_episodes, new_episodes
    )
    
    # 全エピソードの書き起こしフラグを最終確認
    transcript_check_count = sum(
        update_episode_transcript_flag(ep) for ep in merged_episodes
    )
    
    total_transcript_updates = transcript_updated_from_merge + transcript_check_count
    
    if total_transcript_updates > 0:
        print(f"[INFO] 全エピソードの書き起こしファイル存在チェック完了: {total_transcript_updates}件を更新")
    
    # 更新がない場合は保存をスキップ
    if added_count == 0 and updated_count == 0 and total_transcript_updates == 0 and not args.dry_run:
        print("\n" + "=" * 60)
        print("[INFO] 更新する内容がないため、保存をスキップしました")
        print("=" * 60)
        return
    
    # 保存
    save_episodes(merged_episodes, json_path, dry_run=args.dry_run)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] 完了しました！")
    print(f"  新規追加: {added_count}件")
    print(f"  URL更新: {updated_count}件")
    if total_transcript_updates > 0:
        print(f"  書き起こしフラグ更新: {total_transcript_updates}件")
    print(f"  既存スキップ: {skipped_count}件")
    print(f"  合計エピソード数: {len(merged_episodes)}件")
    print("=" * 60)


def main() -> None:
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='RSSフィードからポッドキャストエピソード情報を取得してepisodes.jsonを更新'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='実際には保存せず、追加される内容だけ表示')
    parser.add_argument('--limit', type=int, default=20,
                        help='チェックする最新エピソード数（デフォルト: 20、全件取得は0を指定）')
    parser.add_argument('--output', type=str, default=str(EPISODES_JSON_PATH),
                        help=f'出力先のJSONファイルパス（デフォルト: {EPISODES_JSON_PATH}）')
    parser.add_argument('--all', action='store_true',
                        help='全エピソードを取得（--limit 0 と同じ）')
    parser.add_argument('--reindex', action='store_true',
                        help='既存のepisodes.jsonのIDを振り直す（RSSフィードの取得は行わない）')
    
    args = parser.parse_args()
    
    # --all が指定された場合は limit を 0 に
    if args.all:
        args.limit = 0
    
    try:
        if args.reindex:
            handle_reindex(args)
        else:
            handle_update(args)
            
    except Exception as e:
        print(f"\n[ERROR] エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
