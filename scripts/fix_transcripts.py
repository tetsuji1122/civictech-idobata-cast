#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
書き起こしJSONファイルの誤字修正スクリプト

使い方:
    # 全ファイルを修正
    python fix_transcripts.py
    
    # 特定のファイルのみ修正
    python fix_transcripts.py --file ep1.0.18.json
    
    # ドライラン（実際には修正しない）
    python fix_transcripts.py --dry-run
"""

import json
import argparse
from pathlib import Path
import shutil
from datetime import datetime
import sys

# プロジェクトルートのパスを取得
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# パス設定（プロジェクトルートからの相対パス）
TRANSCRIPTS_DIR = PROJECT_ROOT / "data" / "transcripts"
CORRECTIONS_FILE = PROJECT_ROOT / "data" / "corrections.json"
BACKUP_DIR = PROJECT_ROOT / "data" / "transcripts_backup"

# 修正対象のフィールド
TARGET_FIELDS = ["sub_title", "detailed_description", "summary", "transcript"]


def load_corrections():
    """修正辞書を読み込む"""
    if not CORRECTIONS_FILE.exists():
        print(f"[ERROR] 修正辞書が見つかりません: {CORRECTIONS_FILE}")
        return []
    
    with open(CORRECTIONS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # enabled=Trueのみを返す
        return [c for c in data.get('corrections', []) if c.get('enabled', True)]


def apply_corrections(text, corrections):
    """テキストに修正を適用"""
    if not text:
        return text, []
    
    original_text = text
    applied_corrections = []
    
    for correction in corrections:
        wrong = correction['wrong']
        correct = correction['correct']
        
        if wrong in text:
            text = text.replace(wrong, correct)
            applied_corrections.append(correction['description'])
    
    return text, applied_corrections


def fix_transcript_file(file_path, corrections, dry_run=False):
    """1つのJSONファイルを修正"""
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}処理中: {file_path.name}")
    
    # JSONファイルを読み込み
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 各フィールドに修正を適用
    total_corrections = []
    modified = False
    
    for field in TARGET_FIELDS:
        if field in data:
            new_text, applied = apply_corrections(data[field], corrections)
            
            if applied:
                if not dry_run:
                    data[field] = new_text
                modified = True
                total_corrections.extend(applied)
                print(f"  [{field}] {len(applied)}件の修正を適用")
    
    if modified:
        print(f"  → 合計 {len(total_corrections)}件の修正")
        
        if not dry_run:
            # バックアップを作成
            create_backup(file_path)
            
            # 修正後のJSONを保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✓ 保存完了")
        else:
            print(f"  ℹ DRY-RUNモード: ファイルは変更されません")
    else:
        print(f"  ℹ 修正不要")
    
    return modified


def create_backup(file_path):
    """バックアップを作成"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = BACKUP_DIR / backup_name
    
    shutil.copy(file_path, backup_path)
    print(f"  📦 バックアップ作成: {backup_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description='書き起こしJSONファイルの誤字を修正'
    )
    parser.add_argument(
        '--episode',
        type=str,
        help='修正するエピソード番号（例: 1.0.18）'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='修正する特定のファイル名（例: ep1.0.18.json）'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='全ファイルを一括処理（注意: 慎重に使用してください）'
    )
    parser.add_argument(
        '--wrong',
        type=str,
        action='append',
        help='誤った表記（複数指定可）'
    )
    parser.add_argument(
        '--correct',
        type=str,
        action='append',
        help='正しい表記（--wrongと対で指定）'
    )
    parser.add_argument(
        '--use-dict',
        action='store_true',
        help='辞書ファイルも併用する（--wrong/--correctと組み合わせ時）'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='ドライランモード（実際には修正しない）'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("書き起こしJSON修正スクリプト")
    print("=" * 60)
    
    # エピソード番号、ファイル名、--all のいずれかが必須
    if not args.episode and not args.file and not args.all:
        print("\n[ERROR] エピソード番号、ファイル名、または --all を指定してください")
        print("\n使い方:")
        print("  python scripts/fix_transcripts.py --episode 1.0.18 --wrong '誤字' --correct '正字'")
        print("  python scripts/fix_transcripts.py --file ep1.0.18.json --wrong '誤字' --correct '正字'")
        print("  python scripts/fix_transcripts.py --all  # 全ファイル処理（辞書ファイル使用）")
        print("\nヘルプ: python scripts/fix_transcripts.py --help")
        return
    
    # --wrong と --correct のチェック
    if args.wrong or args.correct:
        if not args.wrong or not args.correct:
            print("\n[ERROR] --wrong と --correct は対で指定してください")
            return
        if len(args.wrong) != len(args.correct):
            print(f"\n[ERROR] --wrong ({len(args.wrong)}個) と --correct ({len(args.correct)}個) の数が一致しません")
            return
    
    # 修正ルールを準備
    corrections = []
    
    # コマンドライン引数から修正ルールを作成
    if args.wrong and args.correct:
        print("\n[INFO] コマンドライン引数から修正ルールを作成")
        for wrong, correct in zip(args.wrong, args.correct):
            corrections.append({
                'wrong': wrong,
                'correct': correct,
                'description': f'コマンドライン指定: {wrong} → {correct}',
                'enabled': True
            })
            print(f"  - {wrong} → {correct}")
    
    # 辞書ファイルも使用する場合
    if args.use_dict or (not args.wrong and not args.correct):
        dict_corrections = load_corrections()
        if dict_corrections:
            if corrections:  # コマンドライン指定と併用
                print("\n[INFO] 辞書ファイルからも修正ルールを読み込みます")
                for c in dict_corrections:
                    print(f"  - {c['wrong']} → {c['correct']} ({c['description']})")
            corrections.extend(dict_corrections)
        elif not corrections:
            print("[ERROR] 修正ルールが見つかりません")
            print("  --wrong/--correct を指定するか、data/corrections.json を作成してください")
            return
    
    if not corrections:
        print("[ERROR] 修正ルールが指定されていません")
        return
    
    print(f"\n[INFO] 合計 {len(corrections)}件の修正ルールを使用します")
    
    # 処理対象ファイルを取得
    if args.episode:
        # エピソード番号から自動的にファイル名を生成
        filename = f"ep{args.episode}.json"
        target_files = [TRANSCRIPTS_DIR / filename]
        if not target_files[0].exists():
            print(f"\n[ERROR] ファイルが見つかりません: {filename}")
            print(f"[INFO] パス: {target_files[0]}")
            return
        print(f"\n[INFO] エピソード {args.episode} を処理します")
    elif args.file:
        target_files = [TRANSCRIPTS_DIR / args.file]
        if not target_files[0].exists():
            print(f"\n[ERROR] ファイルが見つかりません: {args.file}")
            return
        print(f"\n[INFO] ファイル {args.file} を処理します")
    elif args.all:
        target_files = sorted(TRANSCRIPTS_DIR.glob("ep*.json"))
        print(f"\n[WARNING] 全 {len(target_files)} ファイルを処理します")
        
        if not args.dry_run:
            # 全ファイル処理の場合は確認を求める
            response = input("\n本当に全ファイルを修正しますか？ (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("\n[INFO] キャンセルしました")
                return
    
    if not target_files:
        print("\n[ERROR] 処理対象のファイルが見つかりません")
        return
    
    if args.dry_run:
        print("\n[DRY-RUN] 実際にはファイルを変更しません\n")
    else:
        print()  # 空行
    
    # 各ファイルを処理
    modified_count = 0
    for file_path in target_files:
        if fix_transcript_file(file_path, corrections, args.dry_run):
            modified_count += 1
    
    # サマリー
    print("\n" + "=" * 60)
    print(f"[完了] {modified_count}/{len(target_files)}件のファイルを{'確認' if args.dry_run else '修正'}しました")
    
    if args.dry_run:
        print("\n実際に修正する場合は、--dry-run を外して実行してください")
    else:
        print(f"\nバックアップ: {BACKUP_DIR}/")
    
    print("=" * 60)


if __name__ == "__main__":
    main()

