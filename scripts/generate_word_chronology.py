#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
言葉の年表データ生成スクリプト
data/search-index-{年}.json および data/episodes.json から
年別 Top 15 単語と固定キーワード推移を集計し、
data/word-chronology.json を出力する。
"""

import os
import sys
import json
import re
from pathlib import Path
from collections import Counter
from typing import Dict, Any, List
import MeCab

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
EPISODES_FILE = DATA_DIR / "episodes.json"
OUTPUT_FILE = DATA_DIR / "word-chronology.json"

tagger = MeCab.Tagger()

# ストップワード（定型語・挨拶・会話ノイズ・分割破片）
STOP_WORDS = {
    # 毎回の自己紹介・挨拶・定型語（仕様除外）
    'シビックテック', 'ポッドキャスト', '井戸端', 'キャスト', 'ポッド', '井戸', '端',
    '岐阜', '埼玉', '川崎', '長崎',
    '石井', '太田', '小俣', 'さん', '氏', 'ちゃん', 'くん',
    'ニュース', '取り組み', '雑談', '形式', '文化', '入り口', '番組', 'お届け', '収録', '配信',
    # 会話定型・代名詞・形式名詞・一般的動詞由来名詞
    'こと', 'そう', '何', 'の', '人', 'よう', '話', '時', '今', '前', '中', '気', '方', '私', 
    '自分', 'これ', 'それ', 'あれ', 'ため', 'たち', 'やつ', 'とこ', 'ところ', 'もの', '感じ', 
    '文字', '起こし', '今日', '今回', '内容', '詳細', '音声', 'ファイル', '提示', '分', '秒', 
    '回', '年', '月', '日', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', 
    '百', '千', '万', 'あと', 'ほか', 'ほう', 'わけ', 'みたい', 'お願い', 'よろしく', 'はい', 
    'いいえ', '本当', '結構', '全然', '一番', '最初', '最後', '最近', '以前', '現在', '以上', 
    '以下', 'みんな', '皆さん', '部分', '点', '目', '線', '形', '的', '化', '性', '者', 
    '間', '内', '外', '上', '下', 'コード', 'フォー', '意味', '時間', '一緒', '話者',
    '自分たち', '名前', '言葉', '世界', '状態', '情報', '場所', '普通', '理由', '場合', '自身',
    'とき', '今年', '実際', '紹介', 'イメージ', '一応', 'ページ', '時代', '登録', '確認', '更新', 
    '変更', '作成', '開発', '関係', '質問', '回答', '相談', '連絡', '共有', '参加', '活動',
    '前回', '今夜', '普段', '全部', '色々', 'いろいろ', '是非', 'ぜひ',
    # 単語の分割ノイズ（複合語として別途カウントするため、破片を除外）
    'ウェル', 'ビーイング', 'オン', 'ライン', 'ハッカ', 'ソン', 'オープン', 'データ', '生成', 'テック',
    'シビック', 'スマート', 'シティ', 'マイ', 'ナンバー', 'カニ', 'ラーメン', 'ネット', 'ワーク', 'ブック',
    'ボラン', 'ティア', 'ショップ', 'セッ', 'ション'
}

# 複合語として優先カウントする重要用語
COMPOUND_PHRASES = [
    'オープンデータ', '生成AI', 'ハッカソン', 'スマートシティ', 'マイナンバー',
    'Code for Japan', 'ウェルビーイング', 'オンライン', 'ネットワーク', 'エンジニア',
    'コミュニティ', 'テクノロジー', 'ワークショップ', 'セッション', 'ボランティア'
]

# キーワード推移グラフで追跡する固定キーワード
TRACKING_KEYWORDS = [
    'シビックテック',
    'オープンデータ',
    'AI',
    '生成AI',
    'コロナ',
    '岐阜',
    '長崎',
    'ハッカソン',
    '防災',
    'コミュニティ',
    'デジタル',
    'Code for Japan',
    'スマートシティ',
    'マイナンバー',
    'アプリ',
    '地図'
]

YEARS = ['2021', '2022', '2023', '2024', '2025', '2026']


def get_episode_counts_by_year() -> Dict[str, int]:
    with open(EPISODES_FILE, 'r', encoding='utf-8') as f:
        episodes = json.load(f).get('episodes', [])
    counts = Counter()
    for ep in episodes:
        d = ep.get('date', '')
        if len(d) >= 4:
            y = d[:4]
            if y in YEARS:
                counts[y] += 1
    return dict(counts)


def generate_chronology():
    print("言葉の年表データを生成中...")
    ep_counts = get_episode_counts_by_year()
    print(f"年別話数: {ep_counts}")

    yearly_data = []
    # 各キーワードの年別総出現回数（延べ出現回数）カウント用
    keyword_year_counts = {kw: {y: 0 for y in YEARS} for kw in TRACKING_KEYWORDS}

    # キーワード出現回数カウント用正規表現
    keyword_patterns = {}
    for kw in TRACKING_KEYWORDS:
        if kw == 'AI':
            keyword_patterns[kw] = re.compile(r'(?i)(?<![a-z])AI(?![a-z])')
        else:
            keyword_patterns[kw] = re.compile(re.escape(kw), re.IGNORECASE)

    for year in YEARS:
        idx_path = DATA_DIR / f"search-index-{year}.json"
        if not idx_path.exists():
            continue

        with open(idx_path, 'r', encoding='utf-8') as f:
            records = json.load(f)

        word_counter = Counter()

        for r in records:
            text = r.get('text', '')
            if not text:
                continue

            # キーワード推移カウント（延べ出現回数を集計）
            for kw in TRACKING_KEYWORDS:
                matches = keyword_patterns[kw].findall(text)
                keyword_year_counts[kw][year] += len(matches)

            # 複合フレーズのカウント（年別ランキング用）
            for phrase in COMPOUND_PHRASES:
                c = text.count(phrase)
                if c:
                    word_counter[phrase] += c

            # 3文字以上のカタカナ語を直接抽出（分割ノイズ防止）
            katakanas = re.findall(r'[\u30A1-\u30FA\u30FC]{3,}', text)
            for k in katakanas:
                if k not in STOP_WORDS and k not in COMPOUND_PHRASES and k not in ('シビックテック', 'ポッドキャスト'):
                    word_counter[k] += 1

            # 漢字名詞（2文字以上）の形態素抽出
            node = tagger.parseToNode(text)
            while node:
                feature = node.feature.split(',')
                pos = feature[0]
                pos2 = feature[1] if len(feature) > 1 else ''
                surface = node.surface.strip()

                if pos == '名詞' and pos2 in ('普通名詞', '固有名詞', '一般'):
                    if re.match(r'^[\u4E00-\u9FFF]{2,}$', surface):
                        if surface not in STOP_WORDS:
                            word_counter[surface] += 1
                node = node.next

        top_15 = []
        for rank, (word, count) in enumerate(word_counter.most_common(15), 1):
            top_15.append({
                "rank": rank,
                "word": word,
                "count": count
            })

        yearly_data.append({
            "year": year,
            "episode_count": ep_counts.get(year, 0),
            "words": top_15
        })

    # キーワード推移データの整形
    keyword_trends = []
    for kw in TRACKING_KEYWORDS:
        counts = keyword_year_counts[kw]
        max_val = max(counts.values()) if counts else 1
        keyword_trends.append({
            "keyword": kw,
            "counts": counts,
            "max": max_val
        })

    result = {
        "years": yearly_data,
        "keyword_trends": keyword_trends,
        "notes": "2021年は9月配信開始（50話）・2026年は途中経過（92話）です。AIによる自動文字起こしデータをもとに集計しているため、表記ゆれや誤変換を含みうる点にご留意ください。"
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    file_size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"生成完了: {OUTPUT_FILE.name} ({file_size_kb:.1f} KB)")


if __name__ == "__main__":
    generate_chronology()
