#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共通ユーティリティ関数

プロジェクト内の各スクリプトで共有される共通処理をまとめたモジュール
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional


def extract_episode_number(text: str) -> Optional[str]:
    """
    テキストからエピソード番号を抽出
    
    Args:
        text: エピソード番号を含むテキスト（ファイル名、タイトルなど）
        
    Returns:
        エピソード番号（例: "1.0.12"）、見つからない場合はNone
        
    Examples:
        >>> extract_episode_number("ep1.0.12.m4a")
        "1.0.12"
        >>> extract_episode_number("ep0.6.1 FOSS4Gって何？")
        "0.6.1"
    """
    match = re.search(r'ep(\d+\.\d+\.\d+)', text, re.IGNORECASE)
    return match.group(1) if match else None


def format_duration(duration_str: str) -> str:
    """
    再生時間をMM:SS形式に変換
    
    Args:
        duration_str: 時間文字列（例: "00:14:22"）
        
    Returns:
        MM:SS形式の時間（例: "14:22"）
        
    Examples:
        >>> format_duration("00:14:22")
        "14:22"
        >>> format_duration("01:30:45")
        "90:45"
        >>> format_duration("14:22")
        "14:22"
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


def parse_date(date_str: str) -> str:
    """
    日付をYYYY-MM-DD形式に変換
    
    Args:
        date_str: 日付文字列（例: "Thu, 08 Jan 2026 21:00:00 GMT"）
        
    Returns:
        YYYY-MM-DD形式の日付
        
    Examples:
        >>> parse_date("Thu, 08 Jan 2026 21:00:00 GMT")
        "2026-01-08"
    """
    try:
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return datetime.now().strftime("%Y-%m-%d")


def create_backup(file_path: Path, backup_dir: Path) -> Path:
    """
    ファイルのバックアップを作成
    
    Args:
        file_path: バックアップ対象のファイルパス
        backup_dir: バックアップ先ディレクトリ
        
    Returns:
        作成されたバックアップファイルのパス
        
    Raises:
        FileNotFoundError: 対象ファイルが存在しない場合
    """
    if not file_path.exists():
        raise FileNotFoundError(f"バックアップ対象のファイルが見つかりません: {file_path}")
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
    
    import shutil
    shutil.copy2(file_path, backup_path)
    
    return backup_path


def natural_sort_key(text: str) -> tuple:
    """
    自然順ソート用のキー関数
    
    Args:
        text: ソート対象のテキスト
        
    Returns:
        ソート用のキータプル
        
    Examples:
        >>> sorted(["ep0.1.2", "ep0.1.10", "ep0.1.1"], key=natural_sort_key)
        ["ep0.1.1", "ep0.1.2", "ep0.1.10"]
    """
    # エピソード番号形式の場合
    match = re.search(r'ep(\d+)\.(\d+)\.(\d+)', text, re.IGNORECASE)
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    
    # 一般的な自然順ソート
    def convert(part):
        return int(part) if part.isdigit() else part.lower()
    
    return tuple(convert(c) for c in re.split(r'(\d+)', text))


def validate_episode_number(episode_number: str) -> bool:
    """
    エピソード番号の形式が正しいかを検証
    
    Args:
        episode_number: 検証するエピソード番号
        
    Returns:
        形式が正しければTrue
        
    Examples:
        >>> validate_episode_number("1.0.12")
        True
        >>> validate_episode_number("abc")
        False
    """
    if not episode_number:
        return False
    return bool(re.match(r'^\d+\.\d+\.\d+$', episode_number))


def get_project_root() -> Path:
    """
    プロジェクトルートディレクトリを取得
    
    Returns:
        プロジェクトルートのPathオブジェクト
    """
    return Path(__file__).parent.parent


# プロジェクト設定
PROJECT_ROOT = get_project_root()
DATA_DIR = PROJECT_ROOT / "data"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
EPISODES_JSON_PATH = DATA_DIR / "episodes.json"
