#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ポッドキャストRSSフィードからエピソード情報を取得して episodes.json を更新するスクリプト
"""

import feedparser
import json
import re
from datetime import datetime
from pathlib import Path
import argparse
import sys

# プロジェクトルートのパスを取得
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 設定
RSS_FEED_URL = "https://anchor.fm/s/6981b208/podcast/rss"
EPISODES_JSON_PATH = str(PROJECT_ROOT / "data" / "episodes.json")
SPOTIFY_SHOW_URL = "https://open.spotify.com/show/31JfR2D72gENOfOwq3AcKw"
DEFAULT_THUMBNAIL = "img/logo.png"
TRANSCRIPTS_DIR = PROJECT_ROOT / "data" / "transcripts"

def parse_episode_number(title):
    """
    タイトルからエピソード番号を抽出
    例: "ep1.0.16 2025年エピソードランキング" -> "1.0.16"
    """
    match = re.search(r'ep(\d+\.\d+\.\d+)', title, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def format_duration(duration_str):
    """
    再生時間を MM:SS 形式に変換
    例: "00:14:22" -> "14:22"
    """
    if not duration_str:
        return "0:00"
    
    parts = duration_str.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = parts
        if hours == "00":
            return f"{int(minutes)}:{seconds}"
        return f"{int(hours) * 60 + int(minutes)}:{seconds}"
    elif len(parts) == 2:
        return duration_str
    return "0:00"

def parse_date(date_str):
    """
    日付を YYYY-MM-DD 形式に変換
    例: "Thu, 08 Jan 2026 21:00:00 GMT" -> "2026-01-08"
    """
    try:
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
        return dt.strftime("%Y-%m-%d")
    except:
        return datetime.now().strftime("%Y-%m-%d")

def extract_spotify_url(link):
    """
    RSSフィードからSpotify URLを抽出
    Spotify関連のURLであればそのまま返す
    """
    if 'spotify.com' in link or 'podcasters.spotify.com' in link:
        print(f"  → Spotify URL取得: {link}")
        return link
    
    # Spotify関連のURLでない場合は空文字列
    print(f"  → Spotify URLではありません: {link}")
    return ""

def generate_tags(title, description):
    """
    タイトルと説明からタグを自動生成（統一された10個のタグシステム）
    
    統一タグ: ゲスト、シビックテック、Code for、雑談、イベント、
             データ、地域、技術、文化、ライフスタイル
    """
    tags = set()
    text = (title + " " + description).lower()
    
    # キーワードマッチングによるタグ付け
    keywords_map = {
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
    
    # キーワードマッチング
    for tag, keywords in keywords_map.items():
        for keyword in keywords:
            if keyword in text:
                tags.add(tag)
                break
    
    # デフォルトで雑談タグがない場合は追加
    if len(tags) == 0:
        tags.add('雑談')
    
    # タグは最大3個まで（優先度順）
    tag_priority = [
        'ゲスト',
        'イベント', 
        'Code for',
        'シビックテック',
        'データ',
        '技術',
        '地域',
        'ライフスタイル',
        '文化',
        '雑談'
    ]
    
    sorted_tags = []
    for priority_tag in tag_priority:
        if priority_tag in tags:
            sorted_tags.append(priority_tag)
            if len(sorted_tags) >= 3:
                break
    
    return sorted_tags if sorted_tags else ['雑談']

def extract_urls_from_text(text):
    """
    テキストからURLを抽出
    
    Returns:
        tuple: (cleaned_text, urls_list)
    """
    # URLパターン（http/httpsで始まるURL）
    url_pattern = r'https?://[^\s<>"\'\)]+[^\s<>"\'\.,:;\)\]\}]'
    
    # URLを抽出
    urls = re.findall(url_pattern, text)
    
    # URLを削除（前後の空白も整理）
    cleaned_text = re.sub(url_pattern, '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    # 重複を除去
    unique_urls = list(dict.fromkeys(urls))
    
    return cleaned_text, unique_urls

def clean_description(description):
    """
    HTMLタグを除去して説明文をクリーンアップ
    """
    # HTMLタグを削除
    text = re.sub(r'<[^>]+>', '', description)
    # 余分な改行や空白を削除
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def fetch_episodes_from_rss(rss_url, limit=None):
    """
    RSSフィードからエピソード情報を取得
    
    Args:
        rss_url: RSSフィードのURL
        limit: 取得するエピソード数の上限（Noneの場合は全件取得）
    """
    print(f"[INFO] RSSフィードを取得中: {rss_url}")
    feed = feedparser.parse(rss_url)
    
    if feed.bozo:
        print(f"[WARNING] RSSフィードの解析にエラーがあります: {feed.bozo_exception}")
    
    # 取得対象のエントリー
    entries_to_process = feed.entries if limit is None else feed.entries[:limit]
    
    if limit:
        print(f"[INFO] 最新{limit}件のエピソードをチェックします")
    else:
        print(f"[INFO] 全{len(feed.entries)}件のエピソードをチェックします")
    
    episodes = []
    
    for entry in entries_to_process:
        # エピソード番号を抽出
        episode_number = parse_episode_number(entry.title)
        if not episode_number:
            print(f"[WARNING] エピソード番号が取得できませんでした: {entry.title}")
            continue
        
        # 再生時間
        duration = format_duration(entry.get('itunes_duration', '0:00'))
        
        # 配信日
        pub_date = parse_date(entry.published)
        
        # 説明文
        raw_description = clean_description(entry.get('description', entry.get('summary', '')))
        
        # 説明文からURLを抽出
        description, extracted_urls = extract_urls_from_text(raw_description)
        
        # タグ
        tags = generate_tags(entry.title, description)
        
        # Spotify URL
        # entry.linksから個別エピソードのURLを探す
        spotify_url = ""
        if hasattr(entry, 'links'):
            for link in entry.links:
                link_href = link.get('href', '')
                if 'spotify.com/episode' in link_href or 'podcasters.spotify.com/pod/show' in link_href:
                    spotify_url = extract_spotify_url(link_href)
                    break
        
        # linksから見つからない場合は、entry.linkをチェック
        if not spotify_url and hasattr(entry, 'link'):
            spotify_url = extract_spotify_url(entry.link)
        
        # それでも見つからない場合は、デフォルトの番組URLを使用
        if not spotify_url:
            print(f"  [WARNING] {episode_number}: 個別エピソードURLが見つかりません。番組URLを使用します。")
            spotify_url = SPOTIFY_SHOW_URL
        
        # 抽出したURLからリンクリストを作成
        links = []
        for url in extracted_urls:
            # SpotifyやAnchor関連のURLは除外（既にspotifyUrlとして保存されるため）
            if 'spotify.com' not in url and 'anchor.fm' not in url and 'cloudfront.net' not in url:
                links.append({
                    "title": "関連リンク",
                    "url": url
                })
        
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
            "transcript": "",  # 空の書き起こしフィールド
            "links": links,  # 抽出したリンク
            "has_transcript": has_transcript  # 書き起こしファイルの存在フラグ
        }
        
        episodes.append(episode_data)
    
    print(f"[OK] {len(episodes)}件のエピソードを取得しました")
    return episodes

def load_existing_episodes(json_path):
    """
    既存のepisodes.jsonを読み込む
    """
    path = Path(json_path)
    if not path.exists():
        print(f"[INFO] {json_path} が存在しないため、新規作成します")
        return []
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('episodes', [])

def check_transcript_exists(episode_number):
    """
    書き起こしJSONファイルの存在をチェック
    
    Args:
        episode_number: エピソード番号（例: "1.0.12"）
    
    Returns:
        bool: ファイルが存在する場合はTrue
    """
    transcript_file = TRANSCRIPTS_DIR / f"ep{episode_number}.json"
    return transcript_file.exists()

def merge_episodes(existing_episodes, new_episodes):
    """
    既存エピソードと新エピソードをマージ
    既存のエピソード番号がある場合は上書きせず、新しいものだけ追加
    ただし、Spotify URLが番組URLの場合は個別エピソードURLに更新する
    書き起こしファイルの存在チェックも行う
    
    Returns:
        tuple: (merged_episodes, added_count, updated_count, skipped_count, transcript_updated_count)
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
            # 書き起こしファイルの存在チェック
            new_ep['has_transcript'] = check_transcript_exists(new_ep['number'])
            added_episodes.append(new_ep)
        else:
            # 既存エピソードの場合、Spotify URLとlinksをチェック
            existing_ep = existing_dict[new_ep['number']]
            old_url = existing_ep.get('spotifyUrl', '')
            new_url = new_ep.get('spotifyUrl', '')
            updated = False
            
            # Spotify URLの更新チェック
            if old_url == SPOTIFY_SHOW_URL and new_url != SPOTIFY_SHOW_URL and 'episodes' in new_url:
                existing_ep['spotifyUrl'] = new_url
                updated = True
                print(f"  [UPDATE] {new_ep['number']}: Spotify URL更新")
            
            # linksの更新チェック（既存が空で、新しくlinksがある場合）
            existing_links = existing_ep.get('links', [])
            new_links = new_ep.get('links', [])
            if not existing_links and new_links:
                existing_ep['links'] = new_links
                updated = True
                print(f"  [UPDATE] {new_ep['number']}: 関連リンク追加（{len(new_links)}件）")
            
            # 書き起こしファイルの存在チェック（常に更新）
            has_transcript = check_transcript_exists(new_ep['number'])
            if existing_ep.get('has_transcript') != has_transcript:
                existing_ep['has_transcript'] = has_transcript
                updated = True
                print(f"  [UPDATE] {new_ep['number']}: 書き起こしファイル存在チェック更新 ({has_transcript})")
            
            if updated:
                updated_count += 1
            else:
                skipped_count += 1
    
    # 既存エピソードの書き起こしファイルの存在チェックを更新
    for ep in existing_episodes:
        current_has_transcript = check_transcript_exists(ep['number'])
        old_has_transcript = ep.get('has_transcript')
        
        # has_transcriptが未設定、または値が変更された場合に更新
        if old_has_transcript != current_has_transcript:
            ep['has_transcript'] = current_has_transcript
            transcript_updated_count += 1
            if old_has_transcript is None:
                print(f"  [UPDATE] {ep['number']}: 書き起こしファイル存在チェック追加 ({current_has_transcript})")
            else:
                print(f"  [UPDATE] {ep['number']}: 書き起こしファイル存在チェック更新 ({old_has_transcript} → {current_has_transcript})")
    
    if transcript_updated_count > 0:
        print(f"[INFO] 書き起こしファイル存在チェック更新: {transcript_updated_count}件")
    
    print(f"[INFO] 新規エピソード: {len(added_episodes)}件")
    print(f"[INFO] Spotify URL更新: {updated_count}件")
    if transcript_updated_count > 0:
        print(f"[INFO] 書き起こしフラグ更新: {transcript_updated_count}件")
    print(f"[INFO] 既存エピソード（変更なし）: {skipped_count}件")
    
    # transcript_updated_countがある場合は、updated_countに反映させる
    if transcript_updated_count > 0:
        updated_count += transcript_updated_count
    
    # 新規エピソードがなく、更新もない場合は既存データをそのまま返す
    # transcript_updated_countも考慮する（書き起こしフラグの更新があれば保存する）
    if not added_episodes and updated_count == 0:
        print("[INFO] 新しいエピソードや更新はありません")
        return existing_episodes, 0, updated_count, skipped_count, transcript_updated_count
    
    # 新しいエピソードを先頭に追加
    merged = added_episodes + existing_episodes
    
    # 配信日順にソートしてからIDを振り直す（昇順：古いエピソードが先頭）
    merged.sort(key=lambda ep: ep.get('date', '9999-99-99'))
    
    # IDを振り直す（1から順番に）
    for i, ep in enumerate(merged, start=1):
        ep['id'] = i
    
    return merged, len(added_episodes), updated_count, skipped_count, transcript_updated_count

def save_episodes(episodes, json_path, dry_run=False):
    """
    episodes.jsonに保存
    """
    if dry_run:
        print("\n[DRY-RUN] 実際には保存しません")
        print("\n保存される内容のプレビュー:")
        print(json.dumps({"episodes": episodes[:3]}, indent=2, ensure_ascii=False))
        print(f"\n... 他 {len(episodes) - 3}件のエピソード")
        return
    
    # バックアップを作成
    path = Path(json_path)
    if path.exists():
        backup_path = path.with_suffix('.json.backup')
        import shutil
        shutil.copy(path, backup_path)
        print(f"[BACKUP] バックアップを作成: {backup_path}")
    
    # 保存
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({"episodes": episodes}, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] {json_path} に保存しました")

def reindex_episodes(episodes, sort_by_date=True):
    """
    エピソードのIDを振り直す（1から順番に）
    配信日順にソートしてからIDを振り直す
    
    Args:
        episodes: エピソードのリスト
        sort_by_date: Trueの場合、配信日順（昇順、古いものが先頭）にソート
    
    Returns:
        list: IDを振り直したエピソードのリスト
    """
    if sort_by_date:
        # 配信日順にソート（昇順：古いエピソードが先頭）
        # dateフィールドが存在しない場合は最後に配置
        episodes.sort(key=lambda ep: ep.get('date', '9999-99-99'))
        print(f"[INFO] 配信日順（昇順、古いものが先頭）にソートしました")
    
    # IDを振り直す（1から順番に）
    for i, ep in enumerate(episodes, start=1):
        ep['id'] = i
    
    return episodes

def main():
    parser = argparse.ArgumentParser(
        description='RSSフィードからポッドキャストエピソード情報を取得してepisodes.jsonを更新'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='実際には保存せず、追加される内容だけ表示')
    parser.add_argument('--limit', type=int, default=20,
                        help='チェックする最新エピソード数（デフォルト: 20、全件取得は0を指定）')
    parser.add_argument('--output', type=str, default=EPISODES_JSON_PATH,
                        help=f'出力先のJSONファイルパス（デフォルト: {EPISODES_JSON_PATH}）')
    parser.add_argument('--all', action='store_true',
                        help='全エピソードを取得（--limit 0 と同じ）')
    parser.add_argument('--reindex', action='store_true',
                        help='既存のepisodes.jsonのIDを振り直す（RSSフィードの取得は行わない）')
    
    args = parser.parse_args()
    
    # --reindex が指定された場合
    if args.reindex:
        print("[PODCAST] シビックテック井戸端キャスト - ID振り直しスクリプト")
        print("=" * 60)
        
        try:
            # 既存エピソードを読み込み
            existing_episodes = load_existing_episodes(args.output)
            print(f"[INFO] 既存エピソード: {len(existing_episodes)}件")
            
            if not existing_episodes:
                print("[ERROR] エピソードが見つかりません")
                return
            
            # 書き起こしファイルの存在チェックを更新
            transcript_updated_count = 0
            for ep in existing_episodes:
                current_has_transcript = check_transcript_exists(ep['number'])
                old_has_transcript = ep.get('has_transcript')
                ep['has_transcript'] = current_has_transcript
                
                # 値が変更された場合のみログ出力
                if old_has_transcript != current_has_transcript:
                    transcript_updated_count += 1
                    if old_has_transcript is None:
                        print(f"  [UPDATE] {ep['number']}: 書き起こしファイル存在チェック追加 ({current_has_transcript})")
                    else:
                        print(f"  [UPDATE] {ep['number']}: 書き起こしファイル存在チェック更新 ({old_has_transcript} → {current_has_transcript})")
            
            if transcript_updated_count > 0:
                print(f"[INFO] 書き起こしファイル存在チェック更新: {transcript_updated_count}件")
            
            # IDを振り直す（配信日順にソート）
            reindexed_episodes = reindex_episodes(existing_episodes, sort_by_date=True)
            
            # 保存
            save_episodes(reindexed_episodes, args.output, dry_run=args.dry_run)
            
            print("\n" + "=" * 60)
            print("[SUCCESS] IDの振り直しが完了しました！")
            print(f"  合計エピソード数: {len(reindexed_episodes)}件")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n[ERROR] エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        return
    
    # --all が指定された場合は limit を 0 に
    if args.all:
        args.limit = 0
    
    print("[PODCAST] シビックテック井戸端キャスト - エピソード更新スクリプト")
    print("=" * 60)
    
    try:
        # RSSフィードから取得（効率化: 最初から件数制限）
        limit = None if args.limit == 0 else args.limit
        new_episodes = fetch_episodes_from_rss(RSS_FEED_URL, limit=limit)
        
        # 既存エピソードを読み込み
        existing_episodes = load_existing_episodes(args.output)
        print(f"[INFO] 既存エピソード: {len(existing_episodes)}件")
        
        # マージ
        merged_episodes, added_count, updated_count, skipped_count, transcript_updated_from_merge = merge_episodes(existing_episodes, new_episodes)
        
        # 書き起こしファイルの存在チェックを全エピソードに対して実行（最終確認）
        transcript_check_count = 0
        for ep in merged_episodes:
            current_has_transcript = check_transcript_exists(ep['number'])
            old_has_transcript = ep.get('has_transcript')
            if old_has_transcript != current_has_transcript:
                ep['has_transcript'] = current_has_transcript
                transcript_check_count += 1
                if old_has_transcript is None:
                    print(f"  [UPDATE] {ep['number']}: 書き起こしファイル存在チェック追加 ({current_has_transcript})")
                else:
                    print(f"  [UPDATE] {ep['number']}: 書き起こしファイル存在チェック更新 ({old_has_transcript} → {current_has_transcript})")
        
        # merge_episodes内での更新と最終確認での更新を合計
        total_transcript_updates = transcript_updated_from_merge + transcript_check_count
        
        if total_transcript_updates > 0:
            print(f"[INFO] 全エピソードの書き起こしファイル存在チェック完了: {total_transcript_updates}件を更新")
        
        # 新規エピソードも更新もない場合は保存をスキップ
        if added_count == 0 and updated_count == 0 and total_transcript_updates == 0 and not args.dry_run:
            print("\n" + "=" * 60)
            print("[INFO] 更新する内容がないため、保存をスキップしました")
            print("=" * 60)
            return
        
        # 保存
        save_episodes(merged_episodes, args.output, dry_run=args.dry_run)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] 完了しました！")
        print(f"  新規追加: {added_count}件")
        print(f"  URL更新: {updated_count}件")
        if total_transcript_updates > 0:
            print(f"  書き起こしフラグ更新: {total_transcript_updates}件")
        print(f"  既存スキップ: {skipped_count}件")
        print(f"  合計エピソード数: {len(merged_episodes)}件")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

