#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
既存文字起こしデータの一次変換スクリプト
data/transcripts/ep*.json の transcript を発話単位にセグメント化し、
segments と segment_count を追加する。
"""

import os
import sys
import json
import glob
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# スクリプトディレクトリの親ディレクトリ（プロジェクトルート）
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
TRANSCRIPTS_DIR = PROJECT_ROOT / "data" / "transcripts"

# 共通セグメントパーサーのインポート
sys.path.insert(0, str(SCRIPT_DIR))
from segments_util import parse_segments


def parse_args():
    parser = argparse.ArgumentParser(description="文字起こしJSONに segments と segment_count を一括生成します。")
    parser.add_argument("--dry-run", action="store_true", help="ファイルへの書き込みを行わず、レポートのみ出力します。")
    parser.add_argument("--force", action="store_true", help="すでに segments があるファイルも強制的に再変換します。")
    return parser.parse_args()


def create_backup():
    today_str = datetime.now().strftime("%Y%m%d")
    backup_dir = PROJECT_ROOT / "data" / f"transcripts_backup_{today_str}"
    print(f"バックアップを作成中: {backup_dir}")
    if backup_dir.exists():
        print(f"  既存のバックアップディレクトリを更新します: {backup_dir}")
    shutil.copytree(TRANSCRIPTS_DIR, backup_dir, dirs_exist_ok=True)
    print("バックアップ完了。")


def convert_transcripts(dry_run: bool = False, force: bool = False):
    files = sorted(glob.glob(str(TRANSCRIPTS_DIR / "ep*.json")))
    target_count = len(files)
    print(f"対象ファイル数: {target_count}")

    if not dry_run:
        create_backup()

    converted_files = []
    skipped_files = []
    failed_files = []
    total_segments = 0
    total_chars = 0
    file_segment_counts = {}

    for file_path_str in files:
        file_path = Path(file_path_str)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[ERROR] 読み込みエラー ({file_path.name}): {e}")
            failed_files.append((file_path.name, f"読み込み失敗: {e}"))
            continue

        # 既存の segments があり、--force でない場合はスキップ
        if not force and "segments" in data and isinstance(data["segments"], list) and len(data["segments"]) > 0:
            skipped_files.append(file_path.name)
            segs = data["segments"]
            total_segments += len(segs)
            total_chars += sum(len(s.get("text", "")) for s in segs)
            file_segment_counts[file_path.name] = len(segs)
            continue

        transcript = data.get("transcript", "")
        segments = parse_segments(transcript)

        if not segments:
            failed_files.append((file_path.name, "セグメント抽出0件"))
            continue

        # 既存キーの順序と内容を保持し、末尾に segments と segment_count を追加
        data["segments"] = segments
        data["segment_count"] = len(segments)

        converted_files.append(file_path.name)
        total_segments += len(segments)
        total_chars += sum(len(s.get("text", "")) for s in segments)
        file_segment_counts[file_path.name] = len(segments)

        if not dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    # レポート出力
    print("\n" + "=" * 60)
    print("変換結果レポート" + (" (DRY RUN)" if dry_run else ""))
    print("=" * 60)
    print(f"対象ファイル総数: {target_count}")
    print(f"今回変換したファイル数: {len(converted_files)}")
    print(f"スキップしたファイル数 (すでに変換済み): {len(skipped_files)}")
    print(f"変換できた総ファイル数: {len(converted_files) + len(skipped_files)}")
    print(f"変換できなかったファイル数: {len(failed_files)}")
    print(f"総発話数 (segments): {total_segments:,} 件")
    print(f"発話本文の総文字数: {total_chars:,} 文字")

    if failed_files:
        print("\n■ 変換できなかったファイル一覧:")
        for name, reason in failed_files:
            print(f"  - {name}: {reason}")
    else:
        print("\n■ 変換できなかったファイル: なし（全件変換成功）")

    # 異常に少ないファイル（5件未満）のチェック
    low_segment_files = [(name, count) for name, count in file_segment_counts.items() if count < 5]
    if low_segment_files:
        print(f"\n■ 発話数が異常に少ないファイル (< 5件): {len(low_segment_files)} 件")
        for name, count in low_segment_files:
            print(f"  - {name}: {count} 発話")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    args = parse_args()
    convert_transcripts(dry_run=args.dry_run, force=args.force)
