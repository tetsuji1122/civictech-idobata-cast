#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
頻出ワード年表生成スクリプト

書き起こしデータから年別の頻出ワードを集計し、年表データを生成する
"""

import os
import json
import re
from itertools import combinations
from statistics import median
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional
from datetime import datetime

# 共通ユーティリティのインポート
from utils import PROJECT_ROOT

# パス設定
EPISODES_JSON = PROJECT_ROOT / 'data' / 'episodes.json'
TRANSCRIPTS_DIR = PROJECT_ROOT / 'data' / 'transcripts'
OUTPUT_JSON = PROJECT_ROOT / 'data' / 'word-trends.json'
EPISODE_INSIGHTS_JSON = PROJECT_ROOT / 'data' / 'episode-insights.json'
SENTIMENT_TRENDS_JSON = PROJECT_ROOT / 'data' / 'sentiment-trends.json'
WORD_NETWORK_JSON = PROJECT_ROOT / 'data' / 'word-network.json'
SENTIMENT_LEXICON_JSON = PROJECT_ROOT / 'data' / 'sentiment_lexicon.json'

# ストップワード（除外する単語）
STOP_WORDS = {
    # 助詞・助動詞
    'こと', 'もの', 'とき', 'ため', 'よう', 'これ', 'それ', 'あれ', 'どこ', 'いつ',
    'の', 'に', 'を', 'が', 'は', 'と', 'で', 'から', 'まで', 'より',
    'て', 'た', 'だ', 'です', 'ます', 'である', 'でした', 'でした',
    'する', 'なる', 'ある', 'いる', 'できる', 'やる', 'やる',
    'という', 'っていう', 'ということで', 'っていうことで',
    '感じ', '感じる', '感じた', '感じて',
    
    # 会話でよく使われるフレーズ
    'ありがとうございました', 'どうもありがとうございました', 'ありがとう', 'どうも',
    'なるほど', 'そうですね', 'そうそう', 'そう', 'そうだ', 'そうな',
    'えー', 'あの', 'その', 'まあ', 'なんか', 'ちょっと', 'すごい', 'やっぱり',
    'はい', 'うん', 'ええ', 'ああ', 'えーと', 'えっと',
    'とか', 'など', 'なんか', 'なんて', 'なんで',
    
    # 番組固有の用語
    'いどばた', '井戸端', 'キャスト', 'シビックテック井戸端キャスト',
    '石井', '太田', '小俣', '長崎', '川崎', '埼玉', '石井長崎',
    '石井さん', '太田さん', '小俣さん',
    'ジングル', 'ポッドキャスト', 'エピソード', '話', '回', '回目',
    'お届けします', 'お届けしますということで', '始まります',
    
    # 時間・数字
    '分', '秒', '時', '日', '月', '年', '時間',
    
    # URL・記号
    'URL', 'https', 'http', 'www', 'com', 'org', 'jp',
    
    # その他の無意味な単語
    '一応', '一応ね', '結構', '結構ありますね', '結構です', '結構だ',
    'チン', 'スナック', '新年',
}

# 形態素解析ライブラリのインポート（オプション）
try:
    import MeCab
    MECAB_AVAILABLE = True
except ImportError:
    MECAB_AVAILABLE = False
    print("警告: MeCabがインストールされていません。簡易的な単語抽出を使用します。")
    print("より正確な結果を得るには: pip install mecab-python3")


def extract_words_simple(text: str) -> List[str]:
    """
    簡易的な単語抽出（MeCabが使えない場合）
    ひらがな・カタカナ・漢字の連続を単語として抽出
    """
    # タイムスタンプや記号を除去
    text = re.sub(r'\[?\d+:\d+\]?', '', text)  # [0:00] のようなタイムスタンプ
    text = re.sub(r'[\(\)（）]', '', text)  # 括弧を除去
    text = re.sub(r'[、。，．]', ' ', text)  # 句読点をスペースに
    
    # 長いフレーズ（定型文など）を除去
    # 例: "ポッドキャスト文化からシビックテックの入り口を広げたい" のような長い文
    long_phrases = [
        'ポッドキャスト文化からシビックテックの入り口を広げたい',
        'シビックテックに関する取り組みや気になるニュースを雑談形式でお届けします',
        '今日も岐阜の石井と',
        '今日も長崎の石井と',
        '今日も埼玉の太田と',
        '今日も川崎の小俣がお届けします',
    ]
    for phrase in long_phrases:
        text = text.replace(phrase, ' ')
    
    # 日本語の単語（ひらがな・カタカナ・漢字の連続）を抽出
    words = re.findall(r'[ぁ-んァ-ヶー一-龠]+', text)
    
    # フィルタリング: 2-10文字の単語のみ（長すぎるフレーズを除外）
    words = [w for w in words if 2 <= len(w) <= 10]
    
    return words


def extract_words_mecab(text: str) -> List[str]:
    """
    MeCabを使用した形態素解析による単語抽出（名詞のみ）
    """
    # タイムスタンプや記号を除去
    text = re.sub(r'\[?\d+:\d+\]?', '', text)
    text = re.sub(r'[\(\)（）]', '', text)
    
    mecab = MeCab.Tagger()
    node = mecab.parseToNode(text)
    
    words = []
    while node:
        # 品詞情報を取得
        features = node.feature.split(',')
        pos = features[0]  # 品詞
        pos_sub1 = features[1] if len(features) > 1 else ''
        pos_sub2 = features[2] if len(features) > 2 else ''
        
        # 名詞のみを抽出（動詞・形容詞は除外）
        if pos == '名詞':
            # 一般名詞、サ変接続のみを抽出（固有名詞は除外）
            # ただし、代名詞、非自立、接尾、人名は除外
            if pos_sub1 in ['一般', 'サ変接続']:
                # さらに細かくフィルタリング
                if pos_sub2 not in ['代名詞', '非自立', '接尾', '人名']:
                    word = node.surface
                    # 2文字以上で、ストップワードに含まれていないもの
                    if len(word) >= 2 and word not in STOP_WORDS:
                        words.append(word)
        
        node = node.next
    
    return words


def extract_words(text: str) -> List[str]:
    """
    テキストから単語を抽出（MeCabが使える場合は使用、そうでなければ簡易版）
    """
    if MECAB_AVAILABLE:
        return extract_words_mecab(text)
    else:
        return extract_words_simple(text)


def load_episodes() -> List[Dict[str, Any]]:
    """episodes.jsonを読み込む"""
    with open(EPISODES_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('episodes', [])


def load_transcript(episode_number: str) -> Optional[str]:
    """指定されたエピソード番号の書き起こしを読み込む"""
    # エピソード番号からファイル名を生成
    # 例: "1.0.23" -> "ep1.0.23.json"
    filename = f"ep{episode_number}.json"
    transcript_path = TRANSCRIPTS_DIR / filename
    
    if not transcript_path.exists():
        return None
    
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('transcript', '')
    except Exception as e:
        print(f"警告: {filename}の読み込みに失敗: {e}")
        return None


def load_sentiment_lexicon() -> Dict[str, set]:
    """センチメント辞書を読み込む"""
    default_lexicon = {
        "positive": [
            "良い", "良さ", "素晴らしい", "最高", "好き", "楽しい", "嬉しい", "面白い",
            "便利", "有益", "助かる", "成功", "改善", "期待", "希望", "価値"
        ],
        "negative": [
            "悪い", "難しい", "問題", "課題", "大変", "不安", "失敗", "残念", "怖い",
            "辛い", "厳しい", "負担", "遅い", "不足", "無理", "反対"
        ]
    }
    if not SENTIMENT_LEXICON_JSON.exists():
        return {
            "positive": set(default_lexicon["positive"]),
            "negative": set(default_lexicon["negative"])
        }
    with open(SENTIMENT_LEXICON_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {
        "positive": set(data.get("positive", [])),
        "negative": set(data.get("negative", []))
    }


def build_episode_records() -> Dict[str, Any]:
    """エピソードごとのトークンを作成"""
    episodes = load_episodes()
    episode_records = []
    episodes_by_year = defaultdict(list)
    skipped = 0

    for episode in episodes:
        date_str = episode.get('date', '')
        if not date_str:
            continue
        try:
            year = datetime.strptime(date_str, '%Y-%m-%d').year
        except ValueError:
            continue

        episode_number = episode.get('number', '')
        transcript = load_transcript(episode_number)
        if not transcript:
            skipped += 1
            continue

        tokens = extract_words(transcript)
        if not tokens:
            skipped += 1
            continue

        record = {
            "id": episode.get("id"),
            "number": episode_number,
            "title": episode.get("title", ""),
            "date": date_str,
            "year": year,
            "tags": episode.get("tags", []),
            "tokens": tokens
        }
        episode_records.append(record)
        episodes_by_year[year].append(record)

    print(f"\nエピソードレコード作成完了:")
    print(f"  処理済み: {len(episode_records)}件")
    print(f"  スキップ: {skipped}件")
    
    return {
        "records": episode_records,
        "by_year": episodes_by_year,
        "skipped": skipped
    }


def analyze_word_trends(episodes_by_year: Dict[int, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    年別の頻出ワードを集計
    """
    # 年別の単語カウント
    word_counts_by_year = {}
    all_words_by_year = {}
    
    for year in sorted(episodes_by_year.keys()):
        year_episodes = episodes_by_year[year]
        word_counter = Counter()
        all_words = []
        
        print(f"\n{year}年を処理中... ({len(year_episodes)}エピソード)")
        
        for episode in year_episodes:
            words = episode.get("tokens", [])
            if words:
                word_counter.update(words)
                all_words.extend(words)
        
        word_counts_by_year[year] = word_counter
        all_words_by_year[year] = all_words
        
        print(f"  {year}年: {len(word_counter)}種類の単語を抽出")
    
    # 年表データを生成
    trends = []
    previous_year_words = set()
    
    for year in sorted(episodes_by_year.keys()):
        word_counter = word_counts_by_year[year]
        year_episodes = episodes_by_year[year]
        
        # 頻出ワードTop10を取得（ストップワードを除外、最低出現回数3回以上、長すぎる単語を除外）
        top_words = [
            {'word': word, 'count': count}
            for word, count in word_counter.most_common(100)  # 上位100から選ぶ
            if word not in STOP_WORDS 
            and 2 <= len(word) <= 10  # 2-10文字の単語のみ
            and count >= 3
            and not word.isdigit()  # 数字を除外
            and not re.match(r'^[ぁ-ん]+$', word)  # ひらがなのみの単語を除外（「なので」「だから」などは残す）
        ][:10]  # 上位10件を取得
        
        # 前年比の増加ワードを計算（ストップワードを除外）
        rising_words = []
        if year - 1 in word_counts_by_year:
            prev_counter = word_counts_by_year[year - 1]
            for word, count in word_counter.items():
                if (word not in STOP_WORDS 
                    and 2 <= len(word) <= 10
                    and word in prev_counter
                    and not word.isdigit()
                    and not re.match(r'^[ぁ-ん]+$', word)):
                    delta = count - prev_counter[word]
                    if delta > 0:
                        rising_words.append({'word': word, 'delta': delta})
            rising_words.sort(key=lambda x: x['delta'], reverse=True)
            rising_words = rising_words[:5]
        
        # 新規登場ワードを計算（ストップワードを除外）
        current_year_words = set(word_counter.keys())
        new_words = list(current_year_words - previous_year_words)
        # 出現回数でソートして上位5つを取得
        new_words_with_count = [
            (word, word_counter[word]) for word in new_words
            if (word not in STOP_WORDS 
                and 2 <= len(word) <= 10
                and word_counter[word] >= 3  # 最低3回以上出現
                and not word.isdigit()
                and not re.match(r'^[ぁ-ん]+$', word))
        ]
        new_words_with_count.sort(key=lambda x: x[1], reverse=True)
        new_words = [word for word, _ in new_words_with_count[:5]]
        
        # 総語数を計算
        total_words = len(all_words_by_year[year])
        
        trend_data = {
            'year': year,
            'episodeCount': len(year_episodes),
            'totalWords': total_words,
            'topWords': top_words,
            'risingWords': rising_words,
            'newWords': new_words
        }
        
        trends.append(trend_data)
        previous_year_words = current_year_words
        
        print(f"  {year}年: 頻出ワード{len(top_words)}件、増加ワード{len(rising_words)}件、新規ワード{len(new_words)}件")
    
    return {
        "trends": trends,
        "word_counts_by_year": word_counts_by_year
    }


def build_sentiment_trends(episode_records: List[Dict[str, Any]], lexicon: Dict[str, set]) -> Dict[str, Any]:
    """センチメント推移を作成"""
    sentiment_by_year = defaultdict(list)
    pos_neg_counts = defaultdict(lambda: {"pos": 0, "neg": 0})

    for record in episode_records:
        tokens = record["tokens"]
        pos_count = sum(1 for token in tokens if token in lexicon["positive"])
        neg_count = sum(1 for token in tokens if token in lexicon["negative"])
        score = (pos_count - neg_count) / max(1, len(tokens))
        record["sentiment"] = {
            "score": score,
            "posCount": pos_count,
            "negCount": neg_count
        }
        sentiment_by_year[record["year"]].append(score)
        pos_neg_counts[record["year"]]["pos"] += pos_count
        pos_neg_counts[record["year"]]["neg"] += neg_count

    trends = []
    for year in sorted(sentiment_by_year.keys()):
        scores = sentiment_by_year[year]
        trends.append({
            "year": year,
            "avgScore": sum(scores) / max(1, len(scores)),
            "medianScore": median(scores) if scores else 0.0,
            "posCount": pos_neg_counts[year]["pos"],
            "negCount": pos_neg_counts[year]["neg"]
        })

    return {"trends": trends}


def build_word_networks(episodes_by_year: Dict[int, List[Dict[str, Any]]],
                        word_counts_by_year: Dict[int, Counter]) -> Dict[str, Any]:
    """年別の単語ネットワークを作成"""
    networks = []
    for year in sorted(episodes_by_year.keys()):
        edge_counter = Counter()
        year_episodes = episodes_by_year[year]
        for episode in year_episodes:
            tokens = episode.get("tokens", [])
            if not tokens:
                continue
            token_counter = Counter(tokens)
            top_tokens = [word for word, _ in token_counter.most_common(20)]
            unique_tokens = list(set(top_tokens))
            for w1, w2 in combinations(sorted(unique_tokens), 2):
                edge_counter[(w1, w2)] += 1

        edges = [
            {"from": w1, "to": w2, "value": count}
            for (w1, w2), count in edge_counter.most_common(200)
        ]
        nodes_map = {}
        for edge in edges:
            for node_id in (edge["from"], edge["to"]):
                if node_id not in nodes_map:
                    nodes_map[node_id] = {
                        "id": node_id,
                        "label": node_id,
                        "value": word_counts_by_year[year].get(node_id, 1)
                    }

        networks.append({
            "year": year,
            "nodes": list(nodes_map.values()),
            "edges": edges
        })

    return {"networks": networks}


def build_episode_insights(episode_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """エピソード別の洞察データを作成"""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        print("警告: scikit-learnが未インストールのため類似度計算をスキップします。")
        for record in episode_records:
            record["similarEpisodes"] = []
        return {"episodes": episode_records}

    for record in episode_records:
        token_counter = Counter(record.get("tokens", []))
        record["topTokens"] = [
            {"word": word, "count": count}
            for word, count in token_counter.most_common(10)
        ]

    corpus = [" ".join(record["tokens"]) for record in episode_records]
    vectorizer = TfidfVectorizer(
        tokenizer=str.split,
        preprocessor=None,
        token_pattern=None
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)
    similarity_matrix = cosine_similarity(tfidf_matrix)

    for idx, record in enumerate(episode_records):
        scores = similarity_matrix[idx]
        ranked = sorted(
            [(i, score) for i, score in enumerate(scores) if i != idx],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        similar = [
            {
                "id": episode_records[i]["id"],
                "number": episode_records[i]["number"],
                "title": episode_records[i]["title"],
                "score": float(score)
            }
            for i, score in ranked
        ]
        record["similarEpisodes"] = similar

    cleaned = []
    for record in episode_records:
        cleaned.append({
            "id": record.get("id"),
            "number": record.get("number"),
            "title": record.get("title"),
            "date": record.get("date"),
            "year": record.get("year"),
            "tags": record.get("tags", []),
            "sentiment": record.get("sentiment"),
            "topTokens": record.get("topTokens", []),
            "similarEpisodes": record.get("similarEpisodes", [])
        })

    return {"episodes": cleaned}


def main():
    """メイン処理"""
    print("=" * 60)
    print("頻出ワード年表生成スクリプト")
    print("=" * 60)
    
    if not EPISODES_JSON.exists():
        print(f"エラー: {EPISODES_JSON}が見つかりません")
        return
    
    if not TRANSCRIPTS_DIR.exists():
        print(f"エラー: {TRANSCRIPTS_DIR}が見つかりません")
        return
    
    # エピソードごとのトークンを作成
    episode_data = build_episode_records()
    episode_records = episode_data["records"]
    episodes_by_year = episode_data["by_year"]

    if not episode_records:
        print("エラー: 書き起こしデータが見つかりませんでした")
        print(f"  スキップされたエピソード数: {episode_data['skipped']}")
        print("  固有名詞を除外したことで単語が抽出されなくなった可能性があります")
        return

    # 年表データを生成
    trends_result = analyze_word_trends(episodes_by_year)
    trends = trends_result["trends"]
    word_counts_by_year = trends_result["word_counts_by_year"]

    # センチメント推移を生成
    lexicon = load_sentiment_lexicon()
    sentiment_trends = build_sentiment_trends(episode_records, lexicon)

    # 単語ネットワークを生成
    word_networks = build_word_networks(episodes_by_year, word_counts_by_year)

    # エピソード洞察データを生成
    episode_insights = build_episode_insights(episode_records)

    generated_at = datetime.now().isoformat()

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({'generated_at': generated_at, 'trends': trends}, f, ensure_ascii=False, indent=2)
    with open(EPISODE_INSIGHTS_JSON, 'w', encoding='utf-8') as f:
        json.dump({'generated_at': generated_at, **episode_insights}, f, ensure_ascii=False, indent=2)
    with open(SENTIMENT_TRENDS_JSON, 'w', encoding='utf-8') as f:
        json.dump({'generated_at': generated_at, **sentiment_trends}, f, ensure_ascii=False, indent=2)
    with open(WORD_NETWORK_JSON, 'w', encoding='utf-8') as f:
        json.dump({'generated_at': generated_at, **word_networks}, f, ensure_ascii=False, indent=2)

    print(f"\n年表データを生成しました: {OUTPUT_JSON}")
    print(f"  年数: {len(trends)}年")
    print(f"  期間: {trends[0]['year']}年 ～ {trends[-1]['year']}年")
    print(f"  追加出力: {EPISODE_INSIGHTS_JSON.name}, {SENTIMENT_TRENDS_JSON.name}, {WORD_NETWORK_JSON.name}")


if __name__ == '__main__':
    main()
