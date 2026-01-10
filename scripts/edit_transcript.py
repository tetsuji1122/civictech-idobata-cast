#!/usr/bin/env python3
"""
書き起こしJSONエディタ

data/transcripts/ フォルダ内のJSONファイルを選択して編集できるGUIエディタ
"""

import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import sys
from datetime import datetime

# プロジェクトルートのパスを取得
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

TRANSCRIPTS_DIR = PROJECT_ROOT / 'data' / 'transcripts'
BACKUP_DIR = PROJECT_ROOT / 'data' / 'transcripts_backup'


class TranscriptEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("書き起こしJSONエディタ")
        self.root.geometry("1000x800")
        
        self.current_file = None
        self.data = {}
        
        self.create_widgets()
        self.load_file_list()
        
    def create_widgets(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ファイル選択フレーム
        file_frame = ttk.LabelFrame(main_frame, text="ファイル選択", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(file_frame, text="ファイル:").grid(row=0, column=0, padx=(0, 5))
        self.file_combo = ttk.Combobox(file_frame, width=40, state="readonly")
        self.file_combo.grid(row=0, column=1, padx=(0, 5))
        self.file_combo.bind("<<ComboboxSelected>>", self.on_file_selected)
        
        ttk.Button(file_frame, text="開く", command=self.load_selected_file).grid(row=0, column=2, padx=5)
        ttk.Button(file_frame, text="ファイルを選択", command=self.select_file).grid(row=0, column=3, padx=5)
        ttk.Button(file_frame, text="保存", command=self.save_file).grid(row=0, column=4, padx=5)
        ttk.Button(file_frame, text="リロード", command=self.load_file_list).grid(row=0, column=5, padx=5)
        
        # 検索・置換フレーム
        find_replace_frame = ttk.LabelFrame(main_frame, text="検索・置換", padding="10")
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
        ttk.Checkbutton(find_replace_frame, text="大文字小文字を区別", variable=self.case_sensitive).grid(row=0, column=4, padx=5)
        
        # ボタンフレーム
        button_frame = ttk.Frame(find_replace_frame)
        button_frame.grid(row=1, column=0, columnspan=5, pady=(10, 0))
        
        ttk.Button(button_frame, text="次を検索", command=self.find_next_inline).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="前を検索", command=self.find_prev_inline).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="置換", command=self.replace_one_inline).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="すべて置換", command=self.replace_all_inline).pack(side=tk.LEFT, padx=2)
        
        # タブフレーム（各フィールドを編集）
        notebook = ttk.Notebook(main_frame)
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
        
        # サブタイトルタブ
        subtitle_frame = ttk.Frame(notebook, padding="10")
        notebook.add(subtitle_frame, text="サブタイトル")
        
        self.sub_title = scrolledtext.ScrolledText(subtitle_frame, width=80, height=5, wrap=tk.WORD)
        self.sub_title.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        subtitle_frame.grid_rowconfigure(0, weight=1)
        subtitle_frame.grid_columnconfigure(0, weight=1)
        
        # 詳細説明タブ
        desc_frame = ttk.Frame(notebook, padding="10")
        notebook.add(desc_frame, text="詳細説明")
        
        self.detailed_description = scrolledtext.ScrolledText(desc_frame, width=80, height=15, wrap=tk.WORD)
        self.detailed_description.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        desc_frame.grid_rowconfigure(0, weight=1)
        desc_frame.grid_columnconfigure(0, weight=1)
        
        # 要約タブ
        summary_frame = ttk.Frame(notebook, padding="10")
        notebook.add(summary_frame, text="要約")
        
        self.summary = scrolledtext.ScrolledText(summary_frame, width=80, height=15, wrap=tk.WORD)
        self.summary.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        summary_frame.grid_rowconfigure(0, weight=1)
        summary_frame.grid_columnconfigure(0, weight=1)
        
        # 書き起こしタブ
        transcript_frame = ttk.Frame(notebook, padding="10")
        notebook.add(transcript_frame, text="全文書き起こし")
        
        self.transcript = scrolledtext.ScrolledText(transcript_frame, width=80, height=25, wrap=tk.WORD)
        self.transcript.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        transcript_frame.grid_rowconfigure(0, weight=1)
        transcript_frame.grid_columnconfigure(0, weight=1)
        
        # ステータスバー（画面下部）
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(
            status_frame,
            text="準備完了",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding="5"
        )
        self.status_label.pack(fill=tk.X)
        
        # グリッドの重み設定
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # ショートカットキー
        self.root.bind('<Control-f>', lambda e: self.find_entry.focus())
        self.root.bind('<Control-h>', lambda e: self.find_entry.focus())
        
        # 検索・置換関連の変数
        self.last_find_pos = 1.0
        
    def show_status(self, message, status_type="info"):
        """ステータスバーにメッセージを表示"""
        self.status_label.config(text=message)
        # ステータスタイプに応じて色を変更
        if status_type == "error":
            self.status_label.config(foreground="red")
        elif status_type == "warning":
            self.status_label.config(foreground="orange")
        elif status_type == "success":
            self.status_label.config(foreground="green")
        else:
            self.status_label.config(foreground="black")
        # 3秒後に自動的にクリア（成功メッセージの場合）
        if status_type == "success":
            self.root.after(3000, lambda: self.show_status("準備完了", "info"))
    
    def load_file_list(self):
        """ファイル一覧を読み込む"""
        if not TRANSCRIPTS_DIR.exists():
            self.show_status(f"エラー: フォルダが見つかりません: {TRANSCRIPTS_DIR}", "error")
            return
        
        files = sorted(TRANSCRIPTS_DIR.glob("*.json"))
        file_names = [f.name for f in files]
        self.file_combo['values'] = file_names
        
        if file_names:
            self.file_combo.current(0)
            self.load_selected_file()
    
    def select_file(self):
        """ファイルダイアログでファイルを選択"""
        initial_dir = str(TRANSCRIPTS_DIR) if TRANSCRIPTS_DIR.exists() else str(PROJECT_ROOT)
        file_path = filedialog.askopenfilename(
            title="書き起こしJSONファイルを選択",
            initialdir=initial_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.current_file = Path(file_path)
            self.load_file(file_path)
    
    def on_file_selected(self, event=None):
        """コンボボックスでファイルが選択された時"""
        self.load_selected_file()
    
    def load_selected_file(self):
        """選択されたファイルを読み込む"""
        selected = self.file_combo.get()
        if not selected:
            return
        
        file_path = TRANSCRIPTS_DIR / selected
        self.current_file = file_path
        self.load_file(file_path)
    
    def load_file(self, file_path):
        """ファイルを読み込んでエディタに表示"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            # 各フィールドをエディタに表示
            self.episode_number.delete(0, tk.END)
            self.episode_number.insert(0, self.data.get('episode_number', ''))
            
            self.file_name.delete(0, tk.END)
            self.file_name.insert(0, self.data.get('file_name', ''))
            
            self.sub_title.delete('1.0', tk.END)
            self.sub_title.insert('1.0', self.data.get('sub_title', ''))
            
            self.detailed_description.delete('1.0', tk.END)
            self.detailed_description.insert('1.0', self.data.get('detailed_description', ''))
            
            self.summary.delete('1.0', tk.END)
            self.summary.insert('1.0', self.data.get('summary', ''))
            
            self.transcript.delete('1.0', tk.END)
            self.transcript.insert('1.0', self.data.get('transcript', ''))
            
            self.root.title(f"書き起こしJSONエディタ - {Path(file_path).name}")
            self.show_status(f"ファイルを読み込みました: {Path(file_path).name}", "success")
            
        except Exception as e:
            self.show_status(f"エラー: ファイルの読み込みに失敗しました: {str(e)}", "error")
    
    def get_current_text_widget(self):
        """現在選択されているテキストウィジェットを取得"""
        # ノートブックの現在選択されているタブを取得
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
        
        # タブのインデックスに対応するテキストウィジェットを返す
        text_widgets = [
            self.sub_title,
            self.detailed_description,
            self.summary,
            self.transcript
        ]
        
        # 基本情報タブは除外（Entryウィジェットのため）
        if current_tab == 0:
            return None
        
        if 1 <= current_tab <= 4:
            return text_widgets[current_tab - 1]
        
        return None
    
    def find_next_inline(self):
        """次を検索"""
        search_text = self.find_entry.get()
        if not search_text:
            return
        
        text_widget = self.get_current_text_widget()
        if not text_widget:
            self.show_status("警告: 編集可能なテキストフィールドを選択してください", "warning")
            return
        
        # 現在のカーソル位置から検索
        start_pos = text_widget.index(tk.SEL_LAST) if text_widget.tag_ranges(tk.SEL) else text_widget.index(tk.INSERT)
        end_pos = tk.END
        
        # 検索オプション
        flags = []
        if not self.case_sensitive.get():
            flags.append("nocase")
        
        # 検索
        pos = text_widget.search(search_text, start_pos, end_pos, *flags)
        
        if not pos:
            # 最初から再検索
            pos = text_widget.search(search_text, "1.0", end_pos, *flags)
        
        if pos:
            # 見つかった位置を選択
            end_pos_found = f"{pos}+{len(search_text)}c"
            text_widget.mark_set(tk.INSERT, pos)
            text_widget.tag_remove(tk.SEL, "1.0", tk.END)
            text_widget.tag_add(tk.SEL, pos, end_pos_found)
            text_widget.see(pos)
            self.last_find_pos = pos
            self.show_status("検索結果が見つかりました", "success")
        else:
            self.show_status("検索: 見つかりませんでした", "warning")
            self.last_find_pos = "1.0"
    
    def find_prev_inline(self):
        """前を検索"""
        search_text = self.find_entry.get()
        if not search_text:
            return
        
        text_widget = self.get_current_text_widget()
        if not text_widget:
            self.show_status("警告: 編集可能なテキストフィールドを選択してください", "warning")
            return
        
        # 現在のカーソル位置より前を検索
        start_pos = text_widget.index(tk.SEL_FIRST) if text_widget.tag_ranges(tk.SEL) else text_widget.index(tk.INSERT)
        
        # 検索オプション
        flags = []
        if not self.case_sensitive.get():
            flags.append("nocase")
        
        # 最後に見つかった位置を探す（前方検索のため）
        pos = None
        current_pos = "1.0"
        
        while True:
            found = text_widget.search(search_text, current_pos, start_pos, *flags)
            if not found:
                break
            pos = found
            current_pos = f"{found}+1c"
        
        if pos:
            # 見つかった位置を選択
            end_pos_found = f"{pos}+{len(search_text)}c"
            text_widget.mark_set(tk.INSERT, pos)
            text_widget.tag_remove(tk.SEL, "1.0", tk.END)
            text_widget.tag_add(tk.SEL, pos, end_pos_found)
            text_widget.see(pos)
            self.last_find_pos = pos
            self.show_status("検索結果が見つかりました", "success")
        else:
            self.show_status("検索: 見つかりませんでした", "warning")
            self.last_find_pos = "1.0"
    
    def replace_one_inline(self):
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
            # 大文字小文字を区別しない場合
            if not self.case_sensitive.get():
                if sel_text.lower() == search_text.lower():
                    text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    text_widget.insert(tk.SEL_FIRST, replace_text)
                    self.find_next_inline()
                    return
        
        # 選択範囲が一致しない場合は次を検索してから置換
        self.find_next_inline()
        if text_widget.tag_ranges(tk.SEL):
            sel_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            if not self.case_sensitive.get():
                if sel_text.lower() == search_text.lower():
                    text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                    text_widget.insert(tk.SEL_FIRST, replace_text)
    
    def replace_all_inline(self):
        """すべて置換"""
        search_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        
        if not search_text:
            return
        
        text_widget = self.get_current_text_widget()
        if not text_widget:
            self.show_status("警告: 編集可能なテキストフィールドを選択してください", "warning")
            return
        
        # 全体のテキストを取得
        content = text_widget.get("1.0", tk.END)
        
        # 置換
        if self.case_sensitive.get():
            new_content = content.replace(search_text, replace_text)
        else:
            # 大文字小文字を区別しない置換
            import re
            new_content = re.sub(re.escape(search_text), replace_text, content, flags=re.IGNORECASE)
        
        # 変更があったかチェック
        if content == new_content:
            self.show_status("置換: 置換する文字列が見つかりませんでした", "warning")
            return
        
        # カウント
        count = content.count(search_text) if self.case_sensitive.get() else content.lower().count(search_text.lower())
        
        # 確認
        if not messagebox.askyesno("確認", f"{count}箇所を置換しますか？"):
            return
        
        # 置換実行
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", new_content)
        
        self.show_status(f"置換完了: {count}箇所を置換しました", "success")
    
    def save_file(self):
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
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = BACKUP_DIR / f"{self.current_file.stem}_{timestamp}.json"
            if self.current_file.exists():
                import shutil
                shutil.copy2(self.current_file, backup_file)
            
            # ファイルを保存
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            self.show_status(f"保存完了: {self.current_file.name} (バックアップ: {backup_file.name})", "success")
            
        except Exception as e:
            self.show_status(f"エラー: ファイルの保存に失敗しました: {str(e)}", "error")


def main():
    root = tk.Tk()
    app = TranscriptEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
