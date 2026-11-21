#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
発話検索インデックス生成スクリプト
data/transcripts/*.json の segments と data/episodes.json を結合し、
年別に data/search-index-{年}.json を出力する（2021〜2026）。
"""

import os
import sys
import json
import glob
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any, List

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
EPISODES_FILE = DATA_DIR / "episodes.json"


def generate_search_index():
    print("エピソードメタデータを読み込み中...")
    with open(EPISODES_FILE, "r", encoding="utf-8") as f:
        episodes_data = json.load(f)
    
    episodes = episodes_data.get("episodes", [])
    ep_map: Dict[str, Dict[str, Any]] = {str(ep["number"]): ep for ep in episodes}
    print(f"エピソードメタデータ数: {len(ep_map)}")

    files = sorted(glob.glob(str(TRANSCRIPTS_DIR / "ep*.json")))
    print(f"書き起こしファイル数: {len(files)}")

    # 年別のレコードリスト
    yearly_records = defaultdict(list)
    missing_metadata_count = 0
    total_indexed_segments = 0

    for file_path_str in files:
        file_path = Path(file_path_str)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                t_data = json.load(f)
        except Exception as e:
            print(f"[WARNING] 読み込み失敗: {file_path.name}: {e}")
            continue

        ep_number = str(t_data.get("episode_number") or file_path.stem.replace("ep", ""))
        ep_info = ep_map.get(ep_number)
        if not ep_info:
            missing_metadata_count += 1
            continue

        title = ep_info.get("title", f"ep{ep_number}")
        date_str = ep_info.get("date", "")
        if not date_str or len(date_str) < 4:
            continue

        year = date_str[:4]
        segments = t_data.get("segments", [])

        for seg in segments:
            text = seg.get("text", "")
            if not text:
                continue

            record = {
                "episode_number": ep_number,
                "title": title,
                "date": date_str,
                "start_sec": seg.get("start_sec", 0),
                "speaker": seg.get("speaker"),
                "text": text
            }
            yearly_records[year].append(record)
            total_indexed_segments += 1

    print(f"\nインデックス対象外（episodes.json未登録）: {missing_metadata_count} ファイル")
    print(f"総インデックス発話数: {total_indexed_segments:,} 件\n")

    # 年別に出力（新しい日付順、同一エピソード内は start_sec 順）
    all_years = ["2021", "2022", "2023", "2024", "2025", "2026"]
    for y in all_years:
        records = yearly_records.get(y, [])
        records.sort(key=lambda r: (r["date"], -r["start_sec"]), reverse=True)
        # 同じ日付・エピソード内を start_sec 昇順に保つ
        records.sort(key=lambda r: r["date"], reverse=True)

        output_path = DATA_DIR / f"search-index-{y}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        file_size_kb = output_path.stat().st_size / 1024
        print(f"  {output_path.name}: {len(records):,} 発話 ({file_size_kb:.1f} KB)")

    print("\n検索インデックス生成完了。")


if __name__ == "__main__":
    generate_search_index()
