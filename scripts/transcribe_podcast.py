import os
from google import genai
from google.genai import types
from pathlib import Path
import json
import time
import re
import shutil
from dotenv import load_dotenv
import sys

# プロジェクトルートのパスを取得
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# .envファイルから環境変数を読み込む（プロジェクトルートの.envを読み込む）
load_dotenv(PROJECT_ROOT / '.env')

# Gemini APIキーを設定
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError(
        "Gemini APIキーが設定されていません。\n"
        ".envファイルを作成し、GEMINI_API_KEY=your-api-key の形式で設定してください。"
    )

client = genai.Client(api_key=GEMINI_API_KEY)

# 環境変数からパスを取得（プロジェクトルートからの相対パス）
PODCAST_INPUT_DIR = os.getenv('PODCAST_INPUT_DIR', str(PROJECT_ROOT / 'data_voice'))
PODCAST_OUTPUT_DIR = os.getenv('PODCAST_OUTPUT_DIR', str(PROJECT_ROOT / 'data' / 'transcripts'))
PODCAST_BACKUP_DIR = os.getenv('PODCAST_BACKUP_DIR', str(PROJECT_ROOT / 'data_voice' / 'backup'))

def extract_episode_number(filename):
    """
    ファイル名からエピソード番号を抽出
    例: ep1.0.12.m4a -> "1.0.12"
    """
    match = re.search(r'ep(\d+\.\d+\.\d+)', filename, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def upload_audio_file(file_path):
    """音声ファイルをGemini APIにアップロード"""
    print(f"音声ファイルをアップロード中: {file_path}")
    
    # ファイル拡張子からMIMEタイプを決定
    file_path_obj = Path(file_path)
    ext = file_path_obj.suffix.lower()
    mime_type_map = {
        ".m4a": "audio/mp4",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".mp4": "video/mp4"
    }
    mime_type = mime_type_map.get(ext, "audio/mp4")
    
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

def transcribe_audio(audio_file):
    """音声ファイルを文字起こし"""
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
        model="gemini-3-flash-preview",
        contents=[prompt, audio_file]
    )
    # 不要な装飾を削除（念のため）
    text = response.text.strip()
    # 見出しや装飾記号を削除
    text = re.sub(r'^#{1,6}\s+.*$', '', text, flags=re.MULTILINE)  # Markdown見出し
    text = re.sub(r'^=+\s*$', '', text, flags=re.MULTILINE)  # ===見出し
    text = re.sub(r'^-\s*$', '', text, flags=re.MULTILINE)  # ---区切り線
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **太字**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # *強調*
    return text.strip()

def generate_summary(transcript):
    """文字起こしから要約を生成"""
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
{transcript[:8000]}
"""
    
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )
    # 不要な装飾を削除
    text = response.text.strip()
    # 見出しや装飾記号を削除
    text = re.sub(r'^#{1,6}\s+.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^=+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^-\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    # 前置きを削除
    text = re.sub(r'^(要約|まとめ|サマリー|Summary)[：:]\s*', '', text, flags=re.IGNORECASE)
    return text.strip()

def generate_title(transcript):
    """文字起こしからサブタイトルを生成"""
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
{transcript[:8000]}
"""
    
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )
    # 不要な装飾や前置きを削除
    text = response.text.strip()
    # 前置きを削除
    text = re.sub(r'^(サブタイトル|タイトル|Title|Subtitle)[：:]\s*', '', text, flags=re.IGNORECASE)
    # クォートを削除
    text = re.sub(r'^["「](.+?)["」]$', r'\1', text)
    # 記号を削除
    text = re.sub(r'^[-\s]+', '', text)
    text = re.sub(r'[-\s]+$', '', text)
    return text.strip()

def generate_detailed_description(transcript, sub_title, summary):
    """文字起こしから詳細説明文を生成"""
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
文字起こし（抜粋）: {transcript[:1000]}...
"""
    
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )
    # 不要な装飾を削除
    text = response.text.strip()
    # 見出しや装飾記号を削除
    text = re.sub(r'^#{1,6}\s+.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^=+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^-\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    # 前置きを削除
    text = re.sub(r'^(説明|詳細説明|Description)[：:]\s*', '', text, flags=re.IGNORECASE)
    return text.strip()

def process_audio_file(audio_path):
    """音声ファイルを処理して全ての情報を生成"""
    print(f"\n{'='*60}")
    print(f"処理開始: {audio_path.name}")
    print(f"{'='*60}\n")
    
    # 音声ファイルをアップロード
    audio_file = upload_audio_file(str(audio_path))
    
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
        # デフォルトのエピソード番号を使用するか、エラーにする
        episode_number = "0.0.0"
    
    # 結果を辞書にまとめる（仕様に合わせた構造）
    result = {
        "episode_number": episode_number,
        "file_name": audio_path.name,
        "sub_title": sub_title,
        "detailed_description": detailed_description,
        "summary": summary,
        "transcript": transcript
    }
    
    # アップロードしたファイルを削除（クォータの節約）
    client.files.delete(name=audio_file.name)
    print(f"アップロードファイルを削除: {audio_file.name}")
    
    return result

def save_results(result, output_dir):
    """結果をJSONファイルに保存（仕様準拠の構造）"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # エピソード番号からファイル名を生成
    episode_number = result["episode_number"]
    
    # JSON形式で全データを保存
    json_path = output_dir / f"ep{episode_number}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"JSONファイルを保存: {json_path}")

def move_to_backup(audio_file, backup_dir):
    """処理済み音声ファイルをバックアップフォルダに移動"""
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    
    destination = backup_path / audio_file.name
    shutil.move(str(audio_file), str(destination))
    print(f"音声ファイルをバックアップに移動: {destination}")

def main():
    """メイン処理"""
    # 絶対パスに変換（プロジェクトルートからの相対パスを解決）
    input_dir_path = Path(PODCAST_INPUT_DIR)
    if not input_dir_path.is_absolute():
        input_dir_path = PROJECT_ROOT / input_dir_path
    
    output_dir_path = Path(PODCAST_OUTPUT_DIR)
    if not output_dir_path.is_absolute():
        output_dir_path = PROJECT_ROOT / output_dir_path
    
    backup_dir_path = Path(PODCAST_BACKUP_DIR)
    if not backup_dir_path.is_absolute():
        backup_dir_path = PROJECT_ROOT / backup_dir_path

    # 入力フォルダが存在しない場合は作成を試みる
    if not input_dir_path.exists():
        print(f"[INFO] 入力フォルダ '{input_dir_path}' が見つかりません。作成します...")
        try:
            input_dir_path.mkdir(parents=True, exist_ok=True)
            print(f"[OK] 入力フォルダを作成しました: {input_dir_path}")
            print(f"[INFO] 音声ファイルを '{input_dir_path}' フォルダに配置してください。")
            return
        except Exception as e:
            print(f"エラー: 入力フォルダ '{input_dir_path}' の作成に失敗しました: {e}")
            print(f"      手動でフォルダを作成してから再実行してください。")
            return

    audio_extensions = [".m4a", ".mp3", ".wav", ".mp4"]
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(input_dir_path.glob(f"*{ext}"))

    if not audio_files:
        print(f"エラー: 入力フォルダ '{input_dir_path}' 内に音声ファイルが見つかりません。")
        print(f"       音声ファイル（.m4a, .mp3, .wav, .mp4）を '{input_dir_path}' フォルダに配置してください。")
        return

    print(f"\n[INFO] 入力フォルダ: {input_dir_path}")
    print(f"[INFO] 出力フォルダ: {output_dir_path}")
    print(f"[INFO] バックアップフォルダ: {backup_dir_path}\n")
    print(f"見つかった音声ファイル: {len(audio_files)}個")
    for audio_file in audio_files:
        print(f"  - {audio_file.name}")

    for audio_file in audio_files:
        try:
            result = process_audio_file(audio_file)
            save_results(result, output_dir_path)
            
            # 処理成功後、音声ファイルをバックアップフォルダに移動
            move_to_backup(audio_file, backup_dir_path)
            
            print(f"\n[OK] {audio_file.name} の処理が完了しました\n")
        except Exception as e:
            print(f"\n[ERROR] {audio_file.name} の処理中にエラーが発生しました: {e}\n")
            print(f"[INFO] {audio_file.name} は移動せずに {input_dir_path} に残します\n")
            import traceback
            traceback.print_exc()
            continue

    print(f"\n{'='*60}")
    print("全ての処理が完了しました")
    print(f"結果は '{output_dir_path}' フォルダに保存されています")
    print(f"処理済み音声ファイルは '{backup_dir_path}' に移動されました")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

