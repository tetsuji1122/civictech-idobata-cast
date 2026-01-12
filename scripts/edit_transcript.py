#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
書き起こしJSONエディタ

data/transcripts/ フォルダ内のJSONファイルを選択して編集できるGUIエディタ
"""

import json
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import re

# 共通ユーティリティのインポート
from utils import natural_sort_key, create_backup, TRANSCRIPTS_DIR, PROJECT_ROOT

# バックアップディレクトリ
BACKUP_DIR = PROJECT_ROOT / 'data' / 'transcripts_backup'


class TranscriptEditor:
    """書き起こしJSONエディタGUIクラス"""
    
    def __init__(self, root: tk.Tk) -> None:
        """
        初期化
        
        Args:
            root: Tkインスタンス
        """
        self.root = root
        self.root.title("書き起こしJSONエディタ")
        self.root.geometry("1000x800")
        
        self.current_file: Optional[Path] = None
        self.data: Dict[str, Any] = {}
        self.file_list: list[Path] = []
        self.current_file_index: int = -1
        self.last_find_pos: str = "1.0"
        
        self.create_widgets()
        self.load_file_list()
    
    def create_widgets(self) -> None:
        """ウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ファイル選択フレーム
        self._create_file_selection_frame(main_frame)
        
        # 検索・置換フレーム
        self._create_find_replace_frame(main_frame)
        
        # タブフレーム（各フィールドを編集）
        self._create_editor_tabs(main_frame)
        
        # ステータスバー
        self._create_status_bar(main_frame)
        
        # グリッドの重み設定
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # ショートカットキーバインディング
        self._setup_shortcuts()
    
    def _create_file_selection_frame(self, parent: ttk.Frame) -> None:
        """ファイル選択フレームを作成"""
        file_frame = ttk.LabelFrame(parent, text="ファイル選択", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(file_frame, text="ファイル:").grid(row=0, column=0, padx=(0, 5))
        self.file_combo = ttk.Combobox(file_frame, width=40, state="readonly")
        self.file_combo.grid(row=0, column=1, padx=(0, 5))
        self.file_combo.bind("<<ComboboxSelected>>", self.on_file_selected)
        
        ttk.Button(file_frame, text="開く", command=self.load_selected_file).grid(row=0, column=2, padx=5)
        ttk.Button(file_frame, text="ファイルを選択", command=self.select_file).grid(row=0, column=3, padx=5)
        ttk.Button(file_frame, text="保存", command=self.save_file).grid(row=0, column=4, padx=5)
        ttk.Button(file_frame, text="リロード", command=self.load_file_list).grid(row=0, column=5, padx=5)
    
    def _create_find_replace_frame(self, parent: ttk.Frame) -> None:
        """検索・置換フレームを作成"""
        find_replace_frame = ttk.LabelFrame(parent, text="検索・置換", padding="10")
        find_replace_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 検索文字列
        ttk.Label(find_replace_frame, text="検索:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.find_entry = ttk.Entry(find_replace_frame, width=30)
        self.find_entry.grid(row=0, column=1, padx=5)
        self.find_entry.bind('<Return>', lambda e: self.find_next_inline())
        
        # 置換文字列
        ttk.Label(find_replace_frame, text="置換:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.replace_entry = ttk.Entry(find_replace_frame, width=30)
        self.replace_entry.grid(row=0, column=3, padx=5)
        self.replace_entry.bind('<Return>', lambda e: self.replace_one_inline())
        
        # オプション
        self.case_sensitive = tk.BooleanVar(value=False)
        ttk.Checkbutton(find_replace_frame, text="大文字小文字を区別", 
                       variable=self.case_sensitive).grid(row=0, column=4, padx=5)
        
        # ボタンフレーム
        button_frame = ttk.Frame(find_replace_frame)
        button_frame.grid(row=1, column=0, columnspan=5, pady=(10, 0))
        
        ttk.Button(button_frame, text="次を検索", command=self.find_next_inline).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="前を検索", command=self.find_prev_inline).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="置換", command=self.replace_one_inline).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="すべて置換", command=self.replace_all_inline).pack(side=tk.LEFT, padx=2)
    
    def _create_editor_tabs(self, parent: ttk.Frame) -> None:
        """エディタタブを作成"""
        notebook = ttk.Notebook(parent)
        notebook.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 基本情報タブ
        basic_frame = ttk.Frame(notebook, padding="10")
        notebook.add(basic_frame, text="基本情報")
        
        ttk.Label(basic_frame, text="エピソード番号:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.episode_number = ttk.Entry(basic_frame, width=50)
        self.episode_number.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(basic_frame, text="ファイル名:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.file_name = ttk.Entry(basic_frame, width=50)
        self.file_name.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # テキストエリアタブ
        self.sub_title = self._create_text_tab(notebook, "サブタイトル", height=5)
        self.detailed_description = self._create_text_tab(notebook, "詳細説明", height=15)
        self.summary = self._create_text_tab(notebook, "要約", height=15)
        self.transcript = self._create_text_tab(notebook, "全文書き起こし", height=25)
    
    def _create_text_tab(self, notebook: ttk.Notebook, title: str, height: int) -> scrolledtext.ScrolledText:
        """テキストエリアタブを作成"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text=title)
        
        text_widget = scrolledtext.ScrolledText(frame, width=80, height=height, wrap=tk.WORD)
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        return text_widget
    
    def _create_status_bar(self, parent: ttk.Frame) -> None:
        """ステータスバーを作成"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(
            status_frame, text="準備完了", relief=tk.SUNKEN,
            anchor=tk.W, padding="5"
        )
        self.status_label.pack(fill=tk.X)
    
    def _setup_shortcuts(self) -> None:
        """ショートカットキーを設定"""
        # ウィンドウレベルのショートカット
        self.root.bind('<Control-f>', lambda e: self.find_entry.focus())
        self.root.bind('<Control-h>', lambda e: self.find_entry.focus())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-Left>', lambda e: self.load_previous_file())
        self.root.bind('<Control-Right>', lambda e: self.load_next_file())
        
        # テキストウィジェットレベルのショートカット
        def save_on_ctrl_s(event):
            self.save_file()
            return "break"
        
        def load_prev_on_ctrl_left(event):
            self.load_previous_file()
            return "break"
        
        def load_next_on_ctrl_right(event):
            self.load_next_file()
            return "break"
        
        for text_widget in [self.sub_title, self.detailed_description, self.summary, self.transcript]:
            text_widget.bind('<Control-s>', save_on_ctrl_s)
            text_widget.bind('<Control-Left>', load_prev_on_ctrl_left)
            text_widget.bind('<Control-Right>', load_next_on_ctrl_right)
    
    def show_status(self, message: str, status_type: str = "info") -> None:
        """
        ステータスバーにメッセージを表示
        
        Args:
            message: 表示するメッセージ
            status_type: ステータスタイプ ("info", "success", "warning", "error")
        """
        self.status_label.config(text=message)
        
        # ステータスタイプに応じて色を変更
        color_map = {
            "error": "red",
            "warning": "orange",
            "success": "green",
            "info": "black"
        }
        self.status_label.config(foreground=color_map.get(status_type, "black"))
        
        # 成功メッセージは3秒後に自動クリア
        if status_type == "success":
            self.root.after(3000, lambda: self.show_status("準備完了", "info"))
    
    def load_file_list(self) -> None:
        """ファイル一覧を読み込む"""
        if not TRANSCRIPTS_DIR.exists():
            self.show_status(f"エラー: フォルダが見つかりません: {TRANSCRIPTS_DIR}", "error")
            return
        
        files = list(TRANSCRIPTS_DIR.glob("*.json"))
        files.sort(key=lambda f: natural_sort_key(f.name))
        self.file_list = files
        
        file_names = [f.name for f in files]
        self.file_combo['values'] = file_names
        
        if file_names:
            self.file_combo.current(0)
            self.current_file_index = 0
            self.load_selected_file()
    
    def select_file(self) -> None:
        """ファイルダイアログでファイルを選択"""
        initial_dir = str(TRANSCRIPTS_DIR) if TRANSCRIPTS_DIR.exists() else str(PROJECT_ROOT)
        file_path = filedialog.askopenfilename(
            title="書き起こしJSONファイルを選択",
            initialdir=initial_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            file_path = Path(file_path)
            self.current_file = file_path
            
            # ファイルリスト内のインデックスを更新
            file_name = file_path.name
            for i, f in enumerate(self.file_list):
                if f.name == file_name:
                    self.current_file_index = i
                    self.file_combo.current(i)
                    break
            
            self.load_file(file_path)
    
    def on_file_selected(self, event=None) -> None:
        """コンボボックスでファイルが選択された時"""
        selected_index = self.file_combo.current()
        if selected_index >= 0:
            self.current_file_index = selected_index
        self.load_selected_file()
    
    def load_selected_file(self) -> None:
        """選択されたファイルを読み込む"""
        selected = self.file_combo.get()
        if not selected:
            return
        
        file_path = TRANSCRIPTS_DIR / selected
        self.current_file = file_path
        
        # 現在のファイルのインデックスを更新
        for i, f in enumerate(self.file_list):
            if f.name == selected:
                self.current_file_index = i
                break
        
        self.load_file(file_path)
    
    def load_previous_file(self) -> None:
        """前のファイルを読み込む"""
        if not self.file_list or self.current_file_index <= 0:
            self.show_status("最初のファイルです", "warning")
            return
        
        self.current_file_index -= 1
        file_path = self.file_list[self.current_file_index]
        self.current_file = file_path
        self.file_combo.current(self.current_file_index)
        
        self.load_file(file_path)
        self.show_status(f"前のファイルを読み込みました: {file_path.name}", "success")
    
    def load_next_file(self) -> None:
        """次のファイルを読み込む"""
        if not self.file_list or self.current_file_index >= len(self.file_list) - 1:
            self.show_status("最後のファイルです", "warning")
            return
        
        self.current_file_index += 1
        file_path = self.file_list[self.current_file_index]
        self.current_file = file_path
        self.file_combo.current(self.current_file_index)
        
        self.load_file(file_path)
        self.show_status(f"次のファイルを読み込みました: {file_path.name}", "success")
    
    def load_file(self, file_path: Path) -> None:
        """
        ファイルを読み込んでエディタに表示
        
        Args:
            file_path: 読み込むファイルのパス
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            # 各フィールドをエディタに表示
            self.episode_number.delete(0, tk.END)
            self.episode_number.insert(0, self.data.get('episode_number', ''))
            
            self.file_name.delete(0, tk.END)
            self.file_name.insert(0, self.data.get('file_name', ''))
            
            # テキストエリアの更新
            self._update_text_widget(self.sub_title, self.data.get('sub_title', ''))
            self._update_text_widget(self.detailed_description, self.data.get('detailed_description', ''))
            self._update_text_widget(self.summary, self.data.get('summary', ''))
            self._update_text_widget(self.transcript, self.data.get('transcript', ''))
            
            self.root.title(f"書き起こしJSONエディタ - {file_path.name}")
            self.show_status(f"ファイルを読み込みました: {file_path.name}", "success")
            
        except Exception as e:
            self.show_status(f"エラー: ファイルの読み込みに失敗しました: {str(e)}", "error")
    
    def _update_text_widget(self, widget: scrolledtext.ScrolledText, content: str) -> None:
        """テキストウィジェットの内容を更新"""
        widget.delete('1.0', tk.END)
        widget.insert('1.0', content)
    
    def get_current_text_widget(self) -> Optional[scrolledtext.ScrolledText]:
        """現在選択されているテキストウィジェットを取得"""
        # ノートブックを取得
        notebook = None
        for widget in self.root.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ttk.Notebook):
                    notebook = child
                    break
            if notebook:
                break
        
        if not notebook:
            return None
        
        current_tab = notebook.index(notebook.select())
        
        # 基本情報タブ（index 0）は除外
        if current_tab == 0:
            return None
        
        text_widgets = [
            self.sub_title,
            self.detailed_description,
            self.summary,
            self.transcript
        ]
        
        if 1 <= current_tab <= 4:
            return text_widgets[current_tab - 1]
        
        return None
    
    def find_next_inline(self) -> None:
        """次を検索"""
        search_text = self.find_entry.get()
        if not search_text:
            return
        
        text_widget = self.get_current_text_widget()
        if not text_widget:
            self.show_status("警告: 編集可能なテキストフィールドを選択してください", "warning")
            return
        
        # 現在のカーソル位置から検索
        start_pos = (text_widget.index(tk.SEL_LAST) if text_widget.tag_ranges(tk.SEL) 
                    else text_widget.index(tk.INSERT))
        
        # 検索オプション
        flags = ["nocase"] if not self.case_sensitive.get() else []
        
        # 検索実行
        pos = text_widget.search(search_text, start_pos, tk.END, *flags)
        
        # 見つからない場合は最初から再検索
        if not pos:
            pos = text_widget.search(search_text, "1.0", tk.END, *flags)
        
        if pos:
            self._highlight_search_result(text_widget, pos, len(search_text))
            self.show_status("検索結果が見つかりました", "success")
        else:
            self.show_status("検索: 見つかりませんでした", "warning")
            self.last_find_pos = "1.0"
    
    def find_prev_inline(self) -> None:
        """前を検索"""
        search_text = self.find_entry.get()
        if not search_text:
            return
        
        text_widget = self.get_current_text_widget()
        if not text_widget:
            self.show_status("警告: 編集可能なテキストフィールドを選択してください", "warning")
            return
        
        # 現在のカーソル位置より前を検索
        start_pos = (text_widget.index(tk.SEL_FIRST) if text_widget.tag_ranges(tk.SEL) 
                    else text_widget.index(tk.INSERT))
        
        flags = ["nocase"] if not self.case_sensitive.get() else []
        
        # 最後に見つかった位置を探す
        pos = None
        current_pos = "1.0"
        
        while True:
            found = text_widget.search(search_text, current_pos, start_pos, *flags)
            if not found:
                break
            pos = found
            current_pos = f"{found}+1c"
        
        if pos:
            self._highlight_search_result(text_widget, pos, len(search_text))
            self.show_status("検索結果が見つかりました", "success")
        else:
            self.show_status("検索: 見つかりませんでした", "warning")
            self.last_find_pos = "1.0"
    
    def _highlight_search_result(self, widget: scrolledtext.ScrolledText, pos: str, length: int) -> None:
        """検索結果をハイライト"""
        end_pos = f"{pos}+{length}c"
        widget.mark_set(tk.INSERT, pos)
        widget.tag_remove(tk.SEL, "1.0", tk.END)
        widget.tag_add(tk.SEL, pos, end_pos)
        widget.see(pos)
        self.last_find_pos = pos
    
    def replace_one_inline(self) -> None:
        """1つだけ置換"""
        search_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        
        if not search_text:
            return
        
        text_widget = self.get_current_text_widget()
        if not text_widget:
            self.show_status("警告: 編集可能なテキストフィールドを選択してください", "warning")
            return
        
        # 選択されている範囲をチェック
        if text_widget.tag_ranges(tk.SEL):
            sel_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            # 大文字小文字の比較
            matches = (sel_text == search_text if self.case_sensitive.get() 
                      else sel_text.lower() == search_text.lower())
            
            if matches:
                text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                text_widget.insert(tk.SEL_FIRST, replace_text)
                self.find_next_inline()
                return
        
        # 選択範囲が一致しない場合は次を検索してから置換
        self.find_next_inline()
    
    def replace_all_inline(self) -> None:
        """すべて置換"""
        search_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        
        if not search_text:
            return
        
        text_widget = self.get_current_text_widget()
        if not text_widget:
            self.show_status("警告: 編集可能なテキストフィールドを選択してください", "warning")
            return
        
        content = text_widget.get("1.0", tk.END)
        
        # 置換実行
        if self.case_sensitive.get():
            new_content = content.replace(search_text, replace_text)
            count = content.count(search_text)
        else:
            new_content = re.sub(re.escape(search_text), replace_text, content, flags=re.IGNORECASE)
            count = content.lower().count(search_text.lower())
        
        if content == new_content:
            self.show_status("置換: 置換する文字列が見つかりませんでした", "warning")
            return
        
        # 確認
        if not messagebox.askyesno("確認", f"{count}箇所を置換しますか？"):
            return
        
        # 置換実行
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", new_content)
        
        self.show_status(f"置換完了: {count}箇所を置換しました", "success")
    
    def save_file(self) -> None:
        """ファイルを保存"""
        if not self.current_file:
            self.show_status("警告: ファイルが選択されていません", "warning")
            return
        
        try:
            # エディタの内容をデータに反映
            self.data['episode_number'] = self.episode_number.get()
            self.data['file_name'] = self.file_name.get()
            self.data['sub_title'] = self.sub_title.get('1.0', tk.END).rstrip('\n')
            self.data['detailed_description'] = self.detailed_description.get('1.0', tk.END).rstrip('\n')
            self.data['summary'] = self.summary.get('1.0', tk.END).rstrip('\n')
            self.data['transcript'] = self.transcript.get('1.0', tk.END).rstrip('\n')
            
            # バックアップを作成
            if self.current_file.exists():
                backup_path = create_backup(self.current_file, BACKUP_DIR)
                backup_name = backup_path.name
            else:
                backup_name = "なし"
            
            # ファイルを保存
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            self.show_status(
                f"保存完了: {self.current_file.name} (バックアップ: {backup_name})", 
                "success"
            )
            
        except Exception as e:
            self.show_status(f"エラー: ファイルの保存に失敗しました: {str(e)}", "error")


def main() -> None:
    """メイン処理"""
    root = tk.Tk()
    app = TranscriptEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
