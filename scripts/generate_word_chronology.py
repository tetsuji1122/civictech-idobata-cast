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

STOP_WORDS = {
    'こと', 'そう', '何', 'の', '人', 'よう', '話', '時', '今', '前', '中', '気', '方', '私', 
    '自分', 'これ', 'それ', 'あれ', 'ため', 'さん', '氏', '石井', '太田', '小俣', 'ポッドキャスト', 
    '井戸端', 'キャスト', 'たち', 'やつ', 'とこ', 'ところ', 'もの', '感じ', '文字', '起こし',
    '今日', '今回', '内容', '詳細', '音声', 'ファイル', '提示', '分', '秒', '回', '年', '月', '日',
    '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万',
    'あと', 'ほか', 'ほう', 'わけ', 'みたい', 'お願い', 'よろしく', 'はい', 'いいえ', '本当', '結構',
    '全然', '一番', '最初', '最後', '最近', '以前', '現在', '以上', '以下', 'みんな', '皆さん',
    '部分', '点', '目', '線', '形', '的', '化', '性', '者', '間', '内', '外', '上', '下',
    'ニュース', '取り組み', '雑談', '形式', '文化', '入り口', '番組', 'ポッド', '井戸', '端',
    '岐阜', '埼玉', '川崎', '長崎', 'コード', 'フォー', '意味', '時間', '一緒', 'お届け', '話者',
    '自分たち', '名前', '言葉', '世界', '状態', '情報', '場所', '普通', '理由', '場合', '自身',
    'とき', '今年', '実際', '紹介', 'イメージ', 'ソン', 'ハッカ', 'カニ', 'ラーメン', '一応',
    'ページ', '時代', '登録', '確認', '更新', '変更', '作成', '開発'
}

SPECIAL_PHRASES = ['シビックテック', 'オープンデータ', '生成AI', 'ハッカソン', 'スマートシティ', 'マイナンバー', 'Code for Japan']

TRACKING_KEYWORDS = [
    'シビックテック',
    'オープンデータ',
    '生成AI',
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
    # 各キーワードの年別発話数カウント用
    keyword_year_counts = {kw: {y: 0 for y in YEARS} for kw in TRACKING_KEYWORDS}

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

            # キーワード推移カウント（発話単位）
            for kw in TRACKING_KEYWORDS:
                if kw.lower() in text.lower():
                    keyword_year_counts[kw][year] += 1

            # 特殊複合語カウント
            for phrase in SPECIAL_PHRASES:
                c = text.count(phrase)
                if c:
                    word_counter[phrase] += c

            # 形態素解析
            node = tagger.parseToNode(text)
            while node:
                feature = node.feature.split(',')
                pos = feature[0]
                pos2 = feature[1] if len(feature) > 1 else ''
                surface = node.surface.strip()

                if pos == '名詞' and pos2 in ('普通名詞', '固有名詞', '一般'):
                    if len(surface) >= 2 and surface not in STOP_WORDS and not re.match(r'^[0-9A-Za-z]+$', surface):
                        if surface not in ('シビック', 'テック', 'オープン', 'データ', '生成', 'AI', 'Code', 'for', 'Japan'):
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
        "notes": "2021年は9月開始（50話）・2026年は途中経過（92話）です。AIによる自動文字起こしデータをもとに集計しているため、誤変換や表記ゆれを含みうる点にご留意ください。"
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    file_size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"生成完了: {OUTPUT_FILE.name} ({file_size_kb:.1f} KB)")


if __name__ == "__main__":
    generate_chronology()
