#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""発話セグメント化の共通ユーティリティ"""

import re
from typing import List, Dict, Any, Optional, Tuple

TIME_RE = r'(?:(\d{1,2}):(\d{2}):(\d{2})|(\d{1,2}):(\d{2}))'

def parse_time(time_str: Optional[str]) -> Tuple[Optional[int], Optional[str]]:
    if not time_str:
        return None, None
    parts = time_str.strip().split(':')
    try:
        if len(parts) == 2:
            m, s = int(parts[0]), int(parts[1])
            return m * 60 + s, f"{m}:{s:02d}"
        elif len(parts) == 3:
            h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
            sec = h * 3600 + m * 60 + s
            return sec, f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"
    except ValueError:
        pass
    return None, None

def normalize_speaker(spk: Optional[str]) -> Optional[str]:
    if not spk:
        return None
    s = spk.strip().replace('*', '').strip()
    if s.startswith('[') and s.endswith(']'):
        s = s[1:-1].strip()
    s = re.sub(r'[（\(][^）\)]*[）\)]', '', s).strip()
    s = re.sub(r'(?:さん|氏)$', '', s).strip()
    s = s.rstrip('：:').strip()
    return s if s else None

def is_meta_line(s: str) -> bool:
    if not s or s.startswith('###') or s.startswith('---') or s.startswith('==='):
        return True
    if re.match(r'^[\*\-]\s+(\*\*)?[^\n]+[:：]', s):
        return True
    prefixes = ('ご提示いただいた', 'この音声ファイル', '音声ファイルの内容', '「シビックテック', '承知いたしました', '以下は', '以下に')
    if any(s.startswith(p) for p in prefixes):
        return True
    if re.match(r'^話者[（は：:]', s):
        return True
    if re.match(r'^\*\*【?(?:文字起こし|シビックテック|話者一覧|出演者)[^】]*】?\*\*$', s):
        return True
    return False

def extract_line_pattern(line: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    # **00:27 - 01:05 【小俣】**
    m = re.match(r'^\*\*\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*\d{1,2}:\d{2}(?::\d{2})?\s*【([^】]+)】\s*\*\*\s*(.*)$', line)
    if m:
        return True, m.group(1), m.group(2), m.group(3)

    # **0:00 - 0:20 [石井]** / **0:00 - 0:20 石井** / **00:00 - 00:21 石井（ナレーション）**
    m = re.match(r'^\*\*\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*\d{1,2}:\d{2}(?::\d{2})?\s*(?:\[([^\]]+)\]|([^*]+))\*\*\s*(.*)$', line)
    if m:
        spk_candidate = (m.group(2) or m.group(3)).strip()
        # Check if it's pure section note like （ナレーション・BGM） or （イントロダクション） without speaker
        if spk_candidate in ('（ナレーション・BGM）', '(ナレーション・BGM)', '（イントロダクション）', '(イントロダクション)', '（BGM）'):
            return True, m.group(1), None, None
        return True, m.group(1), spk_candidate, m.group(4)

    # 1. セクション見出し (時刻範囲のみ) **00:00 - 00:25**
    m = re.match(r'^(?:#{1,6}\s+)?\*\*\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*\d{1,2}:\d{2}(?::\d{2})?\s*\*\*$', line)
    if m:
        return True, m.group(1), None, None

    # セクション見出し **[00:00] オープニング**
    m = re.match(r'^(?:#{1,6}\s+)?\*\*\s*\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*([^：:\*]+)\*\*$', line)
    if m and any(h in m.group(2) for h in ('オープニング', 'エンディング', '見出し', 'テーマ', 'BGM', 'イントロ')):
        return True, m.group(1), None, None

    # 時刻なしセクション見出し ** オープニング**
    if re.match(r'^\*\*\s*【?[^：:\*]{2,20}】?\s*\*\*$', line):
        raw = line.replace('*', '').strip()
        if any(h in raw for h in ('オープニング', 'エンディング', '見出し', 'テーマ', 'まとめ', '前半', '後半', 'おわりに')):
            return True, None, None, None

    # **[太田]** 本文 or **[太田]**
    m = re.match(r'^\*\*\s*\[([^\]]+)\]\s*\*\*\s*(.*)$', line)
    if m:
        return True, None, m.group(1), m.group(2)

    # **【小俣】** 本文 or **【小俣】**
    m = re.match(r'^\*\*\s*【([^】]+)】\s*\*\*\s*(.*)$', line)
    if m:
        return True, None, m.group(1), m.group(2)

    # **（太田・埼玉）** 本文 or **（太田）**
    m = re.match(r'^\*\*\s*[（\(]([^）\)]+)[）\)]\s*\*\*\s*(.*)$', line)
    if m:
        return True, None, m.group(1), m.group(2)

    # 2. [0:33] 石井：本文 / [0:33] 本文
    m = re.match(r'^\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*(?:([^：:\n]+)[：:])?\s*(.*)$', line)
    if m:
        return True, m.group(1), m.group(2), m.group(3)

    # 3. (0:09) **太田**: 本文
    m = re.match(r'^\((\d{1,2}:\d{2}(?::\d{2})?)\)\s*(?:\*\*([^*：:]+)\*\*|([^\s：:]+))[：:]\s*(.*)$', line)
    if m:
        return True, m.group(1), m.group(2) or m.group(3), m.group(4)

    # 4. **（00:08）石井：** 本文
    m = re.match(r'^\*\*\s*[（\(](\d{1,2}:\d{2}(?::\d{2})?)[）\)]\s*([^：:\*]+)(?:[：:]\*\*|\*\*[：:])\s*(.*)$', line)
    if m:
        return True, m.group(1), m.group(2), m.group(3)

    # 5. **[00:10] 石井：** / **[00:19] 石井**：本文
    m = re.match(r'^\*\*\s*\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*([^：:\*]+)(?:[：:]\*\*|\*\*[：:])\s*(.*)$', line)
    if m:
        return True, m.group(1), m.group(2), m.group(3)

    # 6. **0:00 - 0:20 [石井]** / **0:00 - 0:20 石井**
    m = re.match(r'^\*\*\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*\d{1,2}:\d{2}(?::\d{2})?\s*(?:\[([^\]]+)\]|([^*]+))\*\*\s*(.*)$', line)
    if m:
        return True, m.group(1), m.group(2) or m.group(3), m.group(4)

    # 7. **00:00 - 石井**
    m = re.match(r'^\*\*\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*([^*]+)\*\*\s*(.*)$', line)
    if m:
        return True, m.group(1), m.group(2), m.group(3)

    # 8. **00:09 [太田]**
    m = re.match(r'^\*\*\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*\[([^\]]+)\]\*\*\s*(.*)$', line)
    if m:
        return True, m.group(1), m.group(2), m.group(3)

    # 9. **00:10 石井さん：** / **00:10 石井**：本文 / **00:00 石井**
    m = re.match(r'^\*\*\s*(\d{1,2}:\d{2}(?::\d{2})?)\s+([^*:：\n]+?)(?:[：:]\*\*|\*\*[：:]|\*\*)\s*(.*)$', line)
    if m:
        return True, m.group(1), m.group(2), m.group(3)

    # 10. **[太田]**
    m = re.match(r'^\*\*\s*\[([^\]]+)\]\s*\*\*\s*$', line)
    if m:
        return True, None, m.group(1), ""

    # 11. **石井**: 本文 / **石井：** 本文
    m = re.match(r'^\*\*\s*([^*:：\n]{1,15})\s*(?:\*\*[：:]|[：:]\*\*)\s*(.*)$', line)
    if m:
        return True, None, m.group(1), m.group(2)

    # 12. 石井：本文
    m = re.match(r'^([^:：\s]{1,15})[：:]\s*(.*)$', line)
    if m and not m.group(1).startswith('http'):
        return True, None, m.group(1), m.group(2)

    return False, None, None, None

def parse_segments(transcript: str) -> List[Dict[str, Any]]:
    if not transcript or not transcript.strip():
        return []

    lines = transcript.split('\n')
    segments: List[Dict[str, Any]] = []
    current_sec = 0
    current_start: Optional[str] = None
    pending_speaker: Optional[str] = None
    pending_time_str: Optional[str] = None
    pending_sec: Optional[int] = None

    def flush_pending(text: str):
        nonlocal pending_speaker, pending_time_str, pending_sec
        txt = text.strip()
        if txt and pending_speaker is not None:
            segments.append({
                "start": pending_time_str,
                "start_sec": pending_sec if pending_sec is not None else current_sec,
                "speaker": pending_speaker,
                "text": txt
            })
        pending_speaker = None
        pending_time_str = None
        pending_sec = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line or is_meta_line(line):
            continue

        matched, t_raw, spk_raw, text = extract_line_pattern(line)

        if matched:
            if t_raw:
                s_sec, s_str = parse_time(t_raw)
                if s_sec is not None:
                    current_sec = s_sec
                    current_start = s_str

            spk = normalize_speaker(spk_raw) if spk_raw else None

            if spk is None and text is None:
                continue

            if not text and spk:
                pending_speaker = spk
                pending_time_str = current_start
                pending_sec = current_sec
                continue

            if text:
                segments.append({
                    "start": current_start,
                    "start_sec": current_sec,
                    "speaker": spk,
                    "text": text.strip()
                })
                pending_speaker = None
                pending_time_str = None
                pending_sec = None
                continue
            elif spk:
                pending_speaker = spk
                pending_time_str = current_start
                pending_sec = current_sec
                continue
        else:
            if pending_speaker is not None:
                flush_pending(line)
            elif segments:
                segments[-1]["text"] += "\n" + line

    return segments
