#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ポッドキャスト文字起こしスクリプト

Gemini APIを使用して音声ファイルを文字起こしし、
要約、サブタイトル、詳細説明を自動生成する
"""

import os
import json
import time
import shutil
import re
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 共通ユーティリティのインポート
from utils import extract_episode_number, PROJECT_ROOT

# 環境変数の読み込み
load_dotenv(PROJECT_ROOT / '.env')

# Gemini APIキーを設定
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError(
        "Gemini APIキーが設定されていません。\n"
        ".envファイルを作成し、GEMINI_API_KEY=your-api-key の形式で設定してください。"
    )

client = genai.Client(api_key=GEMINI_API_KEY)

# デフォルトパス設定
DEFAULT_INPUT_DIR = PROJECT_ROOT / 'data_voice'
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / 'data' / 'transcripts'
DEFAULT_BACKUP_DIR = PROJECT_ROOT / 'data_voice' / 'backup'

# 環境変数からパスを取得
PODCAST_INPUT_DIR = Path(os.getenv('PODCAST_INPUT_DIR', str(DEFAULT_INPUT_DIR)))
PODCAST_OUTPUT_DIR = Path(os.getenv('PODCAST_OUTPUT_DIR', str(DEFAULT_OUTPUT_DIR)))
PODCAST_BACKUP_DIR = Path(os.getenv('PODCAST_BACKUP_DIR', str(DEFAULT_BACKUP_DIR)))

# 音声ファイル設定
AUDIO_EXTENSIONS = [".m4a", ".mp3", ".wav", ".mp4"]
MIME_TYPE_MAP = {
    ".m4a": "audio/mp4",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".mp4": "video/mp4"
}

# Gemini モデル
MODEL_NAME = "gemini-3-flash-preview"


def get_mime_type(file_path: Path) -> str:
    """
    ファイル拡張子からMIMEタイプを取得
    
    Args:
        file_path: 音声ファイルのパス
        
    Returns:
        MIMEタイプ
    """
    ext = file_path.suffix.lower()
    return MIME_TYPE_MAP.get(ext, "audio/mp4")


def upload_audio_file(file_path: Path) -> Any:
    """
    音声ファイルをGemini APIにアップロード
    
    Args:
        file_path: 音声ファイルのパス
        
    Returns:
        アップロードされたファイルオブジェクト
        
    Raises:
        ValueError: アップロードに失敗した場合
    """
    print(f"音声ファイルをアップロード中: {file_path.name}")
    
    mime_type = get_mime_type(file_path)
    
    with open(file_path, 'rb') as f:
        audio_file = client.files.upload(file=f, config={"mime_type": mime_type})
    
    # ファイルの処理が完了するまで待機
    while audio_file.state.name == "PROCESSING":
        print("処理中...", end="\r")
        time.sleep(2)
        audio_file = client.files.get(name=audio_file.name)
    
    if audio_file.state.name == "FAILED":
        raise ValueError(f"ファイルのアップロードに失敗しました: {audio_file.state.name}")
    
    print(f"アップロード完了: {audio_file.uri}")
    return audio_file


def clean_ai_output(text: str, remove_prefixes: Optional[List[str]] = None) -> str:
    """
    AI出力から不要な装飾や前置きを削除
    
    Args:
        text: クリーンアップ対象のテキスト
        remove_prefixes: 削除する前置きパターンのリスト
        
    Returns:
        クリーンアップされたテキスト
    """
    text = text.strip()
    
    # 見出しや装飾記号を削除
    text = re.sub(r'^#{1,6}\s+.*$', '', text, flags=re.MULTILINE)  # Markdown見出し
    text = re.sub(r'^=+\s*$', '', text, flags=re.MULTILINE)  # ===
    text = re.sub(r'^-+\s*$', '', text, flags=re.MULTILINE)  # ---
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **太字**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # *強調*
    
    # 前置きを削除
    if remove_prefixes:
        pattern = '^(' + '|'.join(remove_prefixes) + r')[：:]\s*'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # クォートを削除
    text = re.sub(r'^["「](.+?)["」]$', r'\1', text)
    
    return text.strip()


def transcribe_audio(audio_file: Any) -> str:
    """
    音声ファイルを文字起こし
    
    Args:
        audio_file: アップロード済みの音声ファイルオブジェクト
        
    Returns:
        文字起こしテキスト
    """
    print("文字起こし中...")
    
    prompt = """
この音声ファイルの内容を詳細に文字起こししてください。

【出力形式の指示】
- 話者が複数いる場合は、「話者名：」の形式で話者を明確に区別してください
- 各発言の前に、その発言が始まる時間を [分:秒] の形式で記載してください（例：[1:23]）
- 時間は話者が変わるときに必ず入れてください
- 同じ話者が続けて話す場合は、重要な区切り（約1分ごと、またはトピックが変わるとき）に時間を入れてください
- 見出しや装飾、記号（===、---、**など）は一切使用しないでください
- 音声の内容のみを、そのまま文字起こししてください
- 改行は自然な会話の流れに沿って入れてください
- 日本語で出力してください

【出力例】
[0:00] 石井：今日はよろしくお願いします。
[0:15] 小俣：こちらこそ、よろしくお願いします。
[0:30] 石井：それでは、今日のトピックについて話していきましょう。
[1:45] 小俣：そのトピックについて、私はこう考えています。

上記の形式で、音声の内容をそのまま文字起こししてください。
"""
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, audio_file]
    )
    
    return clean_ai_output(response.text)


def generate_summary(transcript: str, max_length: int = 8000) -> str:
    """
    文字起こしから要約を生成
    
    Args:
        transcript: 文字起こしテキスト
        max_length: プロンプトに含める文字起こしの最大長
        
    Returns:
        要約テキスト
    """
    print("要約を生成中...")
    
    prompt = f"""
以下のポッドキャストの文字起こしから、要約を作成してください。

【出力形式の指示】
- 要約は300〜500文字程度で、主要なトピックと重要なポイントをまとめてください
- 見出しや装飾、記号（===、---、**など）は一切使用しないでください
- 改行は自然な文の流れで入れてください（段落は1〜2箇所程度）
- 日本語で出力してください
- 「要約：」「まとめ：」などの前置きは不要です

【出力例】
本ポッドキャストでは、3名のゲストが「生成AIの活用」について語り合っています。主要なトピックとして、生成AIを使ったハッカソンの成功事例が挙げられ、非エンジニアでも短期間でプロトタイプを作成できるようになったことが話題となりました。

文字起こし:
{transcript[:max_length]}
"""
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    
    return clean_ai_output(
        response.text,
        remove_prefixes=['要約', 'まとめ', 'サマリー', 'Summary']
    )


def generate_title(transcript: str, max_length: int = 8000) -> str:
    """
    文字起こしからサブタイトルを生成
    
    Args:
        transcript: 文字起こしテキスト
        max_length: プロンプトに含める文字起こしの最大長
        
    Returns:
        サブタイトル
    """
    print("サブタイトルを生成中...")
    
    prompt = f"""
以下のポッドキャストの文字起こしから、魅力的なサブタイトルを1つ提案してください。

【出力形式の指示】
- サブタイトルは20〜40文字程度で、内容を的確に表現し、聞きたくなるようなものにしてください
- サブタイトルのみを出力してください（説明や前置き、記号は一切不要です）
- 「サブタイトル：」「タイトル：」などの前置きは不要です
- 日本語で出力してください

【出力例】
生成AIが拓くシビックテックの未来

文字起こし:
{transcript[:max_length]}
"""
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    
    return clean_ai_output(
        response.text,
        remove_prefixes=['サブタイトル', 'タイトル', 'Title', 'Subtitle']
    )


def generate_detailed_description(
    transcript: str,
    sub_title: str,
    summary: str,
    max_length: int = 1000
) -> str:
    """
    文字起こしから詳細説明文を生成
    
    Args:
        transcript: 文字起こしテキスト
        sub_title: サブタイトル
        summary: 要約
        max_length: プロンプトに含める文字起こしの最大長
        
    Returns:
        詳細説明文
    """
    print("詳細説明文を生成中...")
    
    prompt = f"""
以下のポッドキャストの情報から、魅力的な詳細説明文を作成してください。

【出力形式の指示】
- 説明文は150〜250文字程度で、リスナーが興味を持つような内容にしてください
- 見出しや装飾、記号（===、---、**など）は一切使用しないでください
- 改行は1箇所程度で、自然な文の流れにしてください
- 日本語で出力してください
- 「説明：」「詳細説明：」などの前置きは不要です

【出力例】
生成AIの劇的な進化により、非エンジニアでも短期間でプロトタイプを作成できる時代が到来しました。本エピソードでは、実際の活用事例や今後の展望について、3名のゲストが語り合います。

サブタイトル: {sub_title}
要約: {summary}
文字起こし（抜粋）: {transcript[:max_length]}...
"""
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    
    return clean_ai_output(
        response.text,
        remove_prefixes=['説明', '詳細説明', 'Description']
    )


def process_audio_file(audio_path: Path) -> Dict[str, Any]:
    """
    音声ファイルを処理して全ての情報を生成
    
    Args:
        audio_path: 音声ファイルのパス
        
    Returns:
        処理結果の辞書
    """
    print(f"\n{'='*60}")
    print(f"処理開始: {audio_path.name}")
    print(f"{'='*60}\n")
    
    # 音声ファイルをアップロード
    audio_file = upload_audio_file(audio_path)
    
    try:
        # 文字起こし
        transcript = transcribe_audio(audio_file)
        
        # 要約、タイトル、詳細説明文を生成
        summary = generate_summary(transcript)
        sub_title = generate_title(transcript)
        detailed_description = generate_detailed_description(transcript, sub_title, summary)
        
        # エピソード番号を抽出
        episode_number = extract_episode_number(audio_path.name)
        if not episode_number:
            print(f"[WARNING] エピソード番号が取得できませんでした: {audio_path.name}")
            episode_number = "0.0.0"
        
        # 結果を辞書にまとめる
        result = {
            "episode_number": episode_number,
            "file_name": audio_path.name,
            "sub_title": sub_title,
            "detailed_description": detailed_description,
            "summary": summary,
            "transcript": transcript
        }
        
        return result
        
    finally:
        # アップロードしたファイルを削除（クォータの節約）
        try:
            client.files.delete(name=audio_file.name)
            print(f"アップロードファイルを削除: {audio_file.name}")
        except Exception as e:
            print(f"[WARNING] アップロードファイルの削除に失敗: {e}")


def save_results(result: Dict[str, Any], output_dir: Path) -> None:
    """
    結果をJSONファイルに保存
    
    Args:
        result: 処理結果の辞書
        output_dir: 出力ディレクトリのパス
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    episode_number = result["episode_number"]
    json_path = output_dir / f"ep{episode_number}.json"
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"JSONファイルを保存: {json_path}")


def move_to_backup(audio_file: Path, backup_dir: Path) -> None:
    """
    処理済み音声ファイルをバックアップフォルダに移動
    
    Args:
        audio_file: 音声ファイルのパス
        backup_dir: バックアップディレクトリのパス
    """
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    destination = backup_dir / audio_file.name
    shutil.move(str(audio_file), str(destination))
    print(f"音声ファイルをバックアップに移動: {destination}")


def get_audio_files(input_dir: Path) -> List[Path]:
    """
    入力ディレクトリから音声ファイルを取得
    
    Args:
        input_dir: 入力ディレクトリのパス
        
    Returns:
        音声ファイルのパスリスト
    """
    audio_files = []
    for ext in AUDIO_EXTENSIONS:
        audio_files.extend(input_dir.glob(f"*{ext}"))
    return sorted(audio_files)


def ensure_input_dir(input_dir: Path) -> bool:
    """
    入力ディレクトリの存在を確認し、必要に応じて作成
    
    Args:
        input_dir: 入力ディレクトリのパス
        
    Returns:
        ディレクトリが利用可能ならTrue
    """
    if input_dir.exists():
        return True
    
    print(f"[INFO] 入力フォルダ '{input_dir}' が見つかりません。作成します...")
    try:
        input_dir.mkdir(parents=True, exist_ok=True)
        print(f"[OK] 入力フォルダを作成しました: {input_dir}")
        print(f"[INFO] 音声ファイルを '{input_dir}' フォルダに配置してください。")
        return False
    except Exception as e:
        print(f"エラー: 入力フォルダ '{input_dir}' の作成に失敗しました: {e}")
        print(f"      手動でフォルダを作成してから再実行してください。")
        return False


def main() -> None:
    """メイン処理"""
    # パスの正規化（絶対パスに変換）
    input_dir = PODCAST_INPUT_DIR if PODCAST_INPUT_DIR.is_absolute() else PROJECT_ROOT / PODCAST_INPUT_DIR
    output_dir = PODCAST_OUTPUT_DIR if PODCAST_OUTPUT_DIR.is_absolute() else PROJECT_ROOT / PODCAST_OUTPUT_DIR
    backup_dir = PODCAST_BACKUP_DIR if PODCAST_BACKUP_DIR.is_absolute() else PROJECT_ROOT / PODCAST_BACKUP_DIR
    
    # 入力ディレクトリの確認
    if not ensure_input_dir(input_dir):
        return
    
    # 音声ファイルの取得
    audio_files = get_audio_files(input_dir)
    
    if not audio_files:
        print(f"エラー: 入力フォルダ '{input_dir}' 内に音声ファイルが見つかりません。")
        print(f"       音声ファイル（{', '.join(AUDIO_EXTENSIONS)}）を '{input_dir}' フォルダに配置してください。")
        return
    
    # 処理情報の表示
    print(f"\n[INFO] 入力フォルダ: {input_dir}")
    print(f"[INFO] 出力フォルダ: {output_dir}")
    print(f"[INFO] バックアップフォルダ: {backup_dir}\n")
    print(f"見つかった音声ファイル: {len(audio_files)}個")
    for audio_file in audio_files:
        print(f"  - {audio_file.name}")
    
    # 各音声ファイルを処理
    success_count = 0
    error_count = 0
    
    for audio_file in audio_files:
        try:
            result = process_audio_file(audio_file)
            save_results(result, output_dir)
            move_to_backup(audio_file, backup_dir)
            
            print(f"\n[OK] {audio_file.name} の処理が完了しました\n")
            success_count += 1
            
        except Exception as e:
            print(f"\n[ERROR] {audio_file.name} の処理中にエラーが発生しました: {e}\n")
            print(f"[INFO] {audio_file.name} は移動せずに {input_dir} に残します\n")
            traceback.print_exc()
            error_count += 1
    
    # 処理結果のサマリー
    print(f"\n{'='*60}")
    print("処理完了")
    print(f"  成功: {success_count}件")
    print(f"  失敗: {error_count}件")
    print(f"結果は '{output_dir}' フォルダに保存されています")
    print(f"処理済み音声ファイルは '{backup_dir}' に移動されました")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
