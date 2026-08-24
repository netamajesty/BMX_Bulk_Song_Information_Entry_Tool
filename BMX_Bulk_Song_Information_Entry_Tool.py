import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# BMX Bulk Song Information Entry Tool
# Windows 7 (Python 3.8) ～ Windows 11 の標準環境で動作するコードです


class BMXBulkTool:

    def __init__(self, root):
        self.root = root
        self.root.title("BMX Bulk Song Information Entry Tool")
        self.root.geometry("915x800")

        # 13個の譜面スロットの内部定義
        self.slots_config = [
            # SP (シングルプレイ) 5項目
            {"key": "sp_beg", "label": "SP BEGINNER相当"},
            {"key": "sp_nor", "label": "SP NORMAL相当"},
            {"key": "sp_hyp", "label": "SP HYPER相当"},
            {"key": "sp_ano", "label": "SP ANOTHER相当"},
            {"key": "sp_leg", "label": "SP LEGGENDARIA相当"},
            # DP (ダブルプレイ) 4項目
            {"key": "dp_nor", "label": "DP NORMAL相当"},
            {"key": "dp_hyp", "label": "DP HYPER相当"},
            {"key": "dp_ano", "label": "DP ANOTHER相当"},
            {"key": "dp_leg", "label": "DP LEGGENDARIA相当"},
            # PMS (ポップン用) 4項目
            {"key": "pms_nor", "label": "PMS NORMAL相当"},
            {"key": "pms_hyp", "label": "PMS HYPER相当"},
            {"key": "pms_ex", "label": "PMS EX相当"},
            {"key": "pms_up", "label": "PMS UPPER-EX相当"},
        ]

        # 選択されたファイルパスを保持する辞書
        self.files_data = {config["key"]: "" for config in self.slots_config}

        # 各難易度のレベル入力ボックスを保持する辞書
        self.level_inputs = {}

        # 画面の構築を開始
        self.create_widgets()
    def create_widgets(self):
        # 項目が多いため、画面を縦スクロールできるようにする設定
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        # --- 1. 基本情報・共通設定エリア ---
        info_frame = ttk.LabelFrame(self.scrollable_frame, text="基本情報・共通設定")
        info_frame.pack(fill="x", padx=15, pady=15)

        # ジャンル名
        ttk.Label(info_frame, text="ジャンル名:").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_genre = ttk.Entry(info_frame, width=60)
        self.ent_genre.grid(row=0, column=1, sticky="w", pady=2)

        # 曲名
        ttk.Label(info_frame, text="曲名:").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_title = ttk.Entry(info_frame, width=60)
        self.ent_title.grid(row=1, column=1, sticky="w", pady=2)

        # アーティスト名
        ttk.Label(info_frame, text="アーティスト名:").grid(row=2, column=0, sticky="w", pady=2)
        self.ent_artist = ttk.Entry(info_frame, width=60)
        self.ent_artist.grid(row=2, column=1, sticky="w", pady=2)

        # 判定（RANK）
        ttk.Label(info_frame, text="判定 (RANK) [0-3]:").grid(row=3, column=0, sticky="w", pady=2)
        
        # 判定枠と注釈を横並びで密着させるための小さな枠
        rank_inline_frame = ttk.Frame(info_frame)
        rank_inline_frame.grid(row=3, column=1, sticky="w", pady=2)
        
        self.ent_rank = ttk.Entry(rank_inline_frame, width=4)
        self.ent_rank.pack(side="left", padx=(0, 5))
        
        ttk.Label(rank_inline_frame, text="※0：VERY HARD, 1：HARD, 2：NORMAL, 3：EASY (空欄時は2)", foreground="gray").pack(side="left")

        # 管理番号
        ttk.Label(info_frame, text="管理番号:").grid(row=4, column=0, sticky="w", pady=2)
        
        # ★管理番号枠と注釈を横並びで密着させるための小さな枠
        id_inline_frame = ttk.Frame(info_frame)
        id_inline_frame.grid(row=4, column=1, sticky="w", pady=2)
        
        # 管理番号の入力欄（横幅を適正な width=15 に調整）
        self.ent_id = ttk.Entry(id_inline_frame, width=15)
        self.ent_id.pack(side="left", padx=(0, 5))
        
        # 注釈を白枠のすぐ右隣に配置
        ttk.Label(id_inline_frame, text="※半角英数字と「 _ 」および「 - 」 のみ有効", foreground="gray").pack(side="left")

        # バックアップ作成用チェックボックス
        self.chk_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            info_frame,
            text="元のファイルのバックアップを作成する (_bms.bak)",
            variable=self.chk_backup_var,
        ).grid(row=5, column=0, columnspan=3, sticky="w", pady=2)

        # 曲名付加用チェックボックス
        self.chk_add_title_var = tk.BooleanVar()
        ttk.Checkbutton(
            info_frame,
            text="ファイル名の頭に曲名を付加する",
            variable=self.chk_add_title_var,
        ).grid(row=6, column=0, columnspan=3, sticky="w", pady=2)

        # 管理番号付加用チェックボックス
        self.chk_add_id_var = tk.BooleanVar()
        ttk.Checkbutton(
            info_frame,
            text="ファイル名の頭に管理番号を付加する",
            variable=self.chk_add_id_var,
        ).grid(row=7, column=0, columnspan=3, sticky="w", pady=2)

        # --- 2. ファイル選択 ＆ レベル入力エリア ---
        self.slots_frame = ttk.LabelFrame(self.scrollable_frame, text="譜面ファイル選択・レベル入力")
        self.slots_frame.pack(fill="x", padx=15, pady=15)

        # 内部で「左（SP）」「右（DP）」に分けるための2カラム用サブフレーム
        columns_frame = ttk.Frame(self.slots_frame)
        columns_frame.pack(fill="x", padx=5, pady=5)

        # 【左側：SPエリア】
        sp_frame = ttk.LabelFrame(columns_frame, text="SP (シングルプレイ)")
        sp_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # 【右側：DPエリア】
        dp_frame = ttk.LabelFrame(columns_frame, text="DP (ダブルプレイ)")
        dp_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # 【下側・真ん中：PMSエリア】
        pms_outer_frame = ttk.Frame(self.slots_frame)
        pms_outer_frame.pack(fill="x", padx=5, pady=5)
        
        pms_frame = ttk.LabelFrame(pms_outer_frame, text="PMS (ポップン)")
        # 横幅を広げすぎず、真ん中に寄せるために anchor="center" で配置
        pms_frame.pack(anchor="center", fill="none", expand=False, padx=5, pady=5)

        self.label_widgets = {}
        
        # 各エリアごとの行番号（グリッド）を管理するカウンタ
        sp_row = 0
        dp_row = 0
        pms_row = 0

        # 13スロット分の配置処理
        for config in self.slots_config:
            key = config["key"]
            label_text = config["label"]

            # 所属するプレイスタイル（SP/DP/PMS）によって、どの枠（親フレーム）に入れるかを自動分岐
            if "sp_" in key:
                parent = sp_frame
                row_idx = sp_row
                sp_row += 1
            elif "dp_" in key:
                parent = dp_frame
                row_idx = dp_row
                dp_row += 1
            else:
                parent = pms_frame
                row_idx = pms_row
                pms_row += 1

            # 各枠の最上行にだけ見出し（ヘッダー）を1度だけ配置
            if row_idx == 0:
                ttk.Label(parent, text="難易度項目", font=("", 9, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=2)
                ttk.Label(parent, text="選択ファイル名", font=("", 9, "bold")).grid(row=0, column=1, sticky="w", padx=5, pady=2)
                ttk.Label(parent, text="レベル", font=("", 9, "bold")).grid(row=0, column=3, sticky="w", padx=5, pady=2)
                # 見出しを置いたので、実際のデータ行は1行下からスタートさせる
                if "sp_" in key: sp_row += 1; row_idx = 1
                elif "dp_" in key: dp_row += 1; row_idx = 1
                else: pms_row += 1; row_idx = 1

            # 難易度名ラベル（例：SP HYPER相当）
            ttk.Label(parent, text=label_text).grid(row=row_idx, column=0, sticky="w", padx=5, pady=4)

            # ファイル名表示（左側・省略枠）
            lbl_file = ttk.Label(parent, text="未選択", width=25, anchor="w", relief="sunken")
            lbl_file.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=4)
            self.label_widgets[key] = lbl_file

            # ファイル選択ボタン（中央）
            btn = ttk.Button(parent, text="選択", command=lambda k=key: self.select_file(k), width=6)
            btn.grid(row=row_idx, column=2, padx=2, pady=4)

            # レベル入力欄（右側・0～99の整数）
            ent_lv = ttk.Entry(parent, width=4)
            ent_lv.grid(row=row_idx, column=3, padx=5, pady=4)
            self.level_inputs[key] = ent_lv

        # --- 3. 実行ボタンエリア ---
        action_frame = ttk.Frame(self.scrollable_frame, padding=10)
        action_frame.pack(fill="x", padx=5)

        btn_run = ttk.Button(
            action_frame,
            text="一括書き込みを実行",
            command=self.execute_bulk_write,
            width=30,
        )
        btn_run.pack(pady=10)

    # ----------------------------------------------------
    # ロジック処理パート
    # ----------------------------------------------------

    def parse_bms_header(self, file_path):
        """ZZ定義対策を施した、安全なヘッダー解析処理"""
        headers = {}
        typo_warnings = []

        # 表記揺れ・スペルミス検知用の正規表現
        patterns = {
            "genre": re.compile(r"^#(genre|genra|genere|genr)$", re.IGNORECASE),
            "title": re.compile(r"^#(title|titel|titl|titre)$", re.IGNORECASE),
            "artist": re.compile(r"^#(artist|artsit|artst)$", re.IGNORECASE),
            "player": re.compile(r"^#player$", re.IGNORECASE),
            "rank": re.compile(r"^#rank$", re.IGNORECASE),
        }

        try:
            # BMSで一般的な文字コード（Shift-JIS、UTF-8など）を順に試して安全に読み込む
            content = ""
            for encoding in ["cp932", "utf-8", "utf-8-sig"]:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            lines = content.splitlines()
            for i, line in enumerate(lines, start=1):
                line = line.strip()

                # ★強力なZZ定義ガード★ 
                # 譜面データパート（例: #00111:0102...）が登場した時点で解析を即終了
                if re.match(r"^#\d{3}\d{2}:", line):
                    break

                if not line.startswith("#"):
                    continue

                # スペースやタブでコマンド（#TITLEなど）と値を分割
                parts = re.split(r"\s+", line, maxsplit=1)
                cmd = parts[0]
                val = parts[1] if len(parts) > 1 else ""

                # 各項目のマッチングとスペルミス（タイポ）検知
                for key_name, regex in patterns.items():
                    if regex.match(cmd):
                        # 大文字小文字の揺れ、またはスペルミスがある場合
                        if cmd != f"#{key_name.upper()}":
                            typo_warnings.append(
                                f"行 {i}: '{cmd}' (想定: #{key_name.upper()})"
                            )
                        headers[key_name] = val
                        break

        except Exception:
            pass

        return headers, typo_warnings
    def select_file(self, target_key):
        """ファイル選択処理 ＆ 周辺ファイルの自動仕分け ＆ 逆引き入力"""
        file_path = filedialog.askopenfilename(
            filetypes=[
                (
                    "BMS Files",
                    "*.bms;*.bme;*.bml;*.pms;*.BMS;*.BME;*.BML;*.PMS",
                )
            ]
        )
        if not file_path:
            return

        # 選択されたファイルと同じフォルダ内にあるBMS関連ファイルをすべてリストアップ
        base_dir = os.path.dirname(file_path)
        all_files = [
            os.path.join(base_dir, f)
            for f in os.listdir(base_dir)
            if f.lower().endswith((".bms", ".bme", ".bml", ".pms"))
        ]

        detected_info_list = []  # 複数ファイルの逆引き情報・不一致チェック用
        assigned_count = 0

        for f_path in all_files:
            f_name = os.path.basename(f_path).lower()
            headers, typo_warns = self.parse_bms_header(f_path)

            # 担当者ミス・スペルミス警告ダイアログ（タイポ検知時）
            if typo_warns:
                msg = (
                    f"ファイル: {os.path.basename(f_path)}\n\n"
                    "ヘッダーに表記揺れ・スペルミスの可能性があります:\n"
                    + "\n".join(typo_warns)
                    + "\n\nこれを正しいヘッダーとして解釈し、読み込みを続行しますか？"
                )
                if not messagebox.askokcancel("ヘッダー警告", msg):
                    continue

            # プレイヤーモード（#PLAYER）の取得（1はSP、3はDP、未記入はSP扱い）
            player_mode = headers.get("player", "1").strip()
            is_dp = player_mode == "3"

            slot_key = None

            # 拡張子が .pms（ポップン）の場合の自動仕分け
            if f_name.endswith(".pms"):
                if "upper" in f_name or "up" in f_name:
                    slot_key = "pms_up"
                elif "ex" in f_name:
                    slot_key = "pms_ex"
                elif "hyper" in f_name or "_h" in f_name or "7h" in f_name:
                    slot_key = "pms_hyp"
                elif "normal" in f_name or "_n" in f_name or "7n" in f_name:
                    slot_key = "pms_nor"
            # 拡張子が bms/bme/bml の場合の自動仕分け（7n/7h/14n/14hやキー数、中身の#PLAYERから判定）
            else:
                if (
                    "beginner" in f_name
                    or "_b" in f_name
                    or "beg" in f_name
                    and not is_dp
                ):
                    slot_key = "sp_beg"
                elif (
                    "light7" in f_name
                    or "7n" in f_name
                    or "light14" in f_name
                    or "14n" in f_name
                    or "_n" in f_name
                    or "normal" in f_name
                ):
                    slot_key = "dp_nor" if is_dp else "sp_nor"
                elif (
                    "7keys" in f_name
                    or "7k" in f_name
                    or "7h" in f_name
                    or "14keys" in f_name
                    or "14k" in f_name
                    or "14h" in f_name
                    or "_h" in f_name
                    or "hyper" in f_name
                ):
                    slot_key = "dp_hyp" if is_dp else "sp_hyp"
                elif (
                    "7a" in f_name
                    or "14a" in f_name
                    or "_a" in f_name
                    or "another" in f_name
                ):
                    slot_key = "dp_ano" if is_dp else "sp_ano"
                elif (
                    "leggendaria" in f_name
                    or "_l" in f_name
                    or "leg" in f_name
                    or "_x" in f_name
                ):
                    slot_key = "dp_leg" if is_dp else "sp_leg"
            # 特定のスロットに割り当て可能と判定された場合
            if slot_key:
                self.files_data[slot_key] = f_path
                self.label_widgets[slot_key].config(
                    text=os.path.basename(f_path)
                )
                assigned_count += 1

                # 逆引き（画面への自動反映）のためのヘッダー情報を収集
                detected_info_list.append(
                    {
                        "file": os.path.basename(f_path),
                        "genre": headers.get("genre", "").strip(),
                        "title": headers.get("title", "").strip(),
                        "artist": headers.get("artist", "").strip(),
                    }
                )

        # --- 複数ファイル間の逆引き情報・表記不一致チェック ---
        if detected_info_list:
            final_genre, final_title, final_artist = "", "", ""
            genres = [
                d["genre"] for d in detected_info_list if d["genre"]
            ]
            titles = [
                d["title"] for d in detected_info_list if d["title"]
            ]
            artists = [
                d["artist"] for d in detected_info_list if d["artist"]
            ]

            # 重複を排除して、それぞれ何パターンの文字列が存在するか精査
            unique_genres = list(set(genres))
            unique_titles = list(set(titles))
            unique_artists = list(set(artists))

            # 【曲名の不一致チェック】
            if len(unique_titles) > 1:
                msg = "検出されたファイル間で『曲名』の表記が一致しません。どれを採用しますか？\n\n"
                for idx, t in enumerate(unique_titles, start=1):
                    msg += f"選択肢 {idx}: {t}\n"
                messagebox.showwarning("表記不一致の警告", msg)
                # 最初の候補を暫定採用
                final_title = unique_titles
            elif unique_titles:
                final_title = unique_titles

            # 【ジャンル名の不一致チェック】
            if len(unique_genres) > 1:
                msg = "検出されたファイル間で『ジャンル名』の表記が一致しません。どれを採用しますか？\n\n"
                for idx, g in enumerate(unique_genres, start=1):
                    msg += f"選択肢 {idx}: {g}\n"
                messagebox.showwarning("表記不一致の警告", msg)
                final_genre = unique_genres
            elif unique_genres:
                final_genre = unique_genres

            # 【アーティスト名の不一致チェック】
            if len(unique_artists) > 1:
                msg = "検出されたファイル間で『アーティスト名』の表記が一致しません。どれを採用しますか？\n\n"
                for idx, a in enumerate(unique_artists, start=1):
                    msg += f"選択肢 {idx}: {a}\n"
                messagebox.showwarning("表記不一致の警告", msg)
                final_artist = unique_artists
            elif unique_artists:
                final_artist = unique_artists

            # 画面の各メイン入力欄が空欄の場合に、吸い出した文字を自動セット
            if final_genre and not self.ent_genre.get():
                self.ent_genre.insert(0, final_genre)
            if final_title and not self.ent_title.get():
                self.ent_title.insert(0, final_title)
            if final_artist and not self.ent_artist.get():
                self.ent_artist.insert(0, final_artist)

        messagebox.showinfo(
            "自動仕分け完了",
            f"周辺ファイルを含め、{assigned_count}個の譜面ファイルを自動感知しました。",
        )
    def execute_bulk_write(self):
        """一括書き込みコア処理"""
        genre = self.ent_genre.get().strip()
        title = self.ent_title.get().strip()
        artist = self.ent_artist.get().strip()
        rank_input = self.ent_rank.get().strip()
        manage_id = self.ent_id.get().strip()

        # 1. バリデーションチェック（管理番号の文字制限）
        if manage_id and not re.match(r"^[A-Za-z0-9_-]+$", manage_id):
            messagebox.showerror(
                "入力エラー",
                "管理番号には半角英数字、アンダーバー(_)、ハイフン(-)のみを使用してください。",
            )
            return

        # 2. バリデーションチェック（RANK）
        if rank_input:
            if rank_input not in ["0", "1", "2", "3"]:
                messagebox.showerror(
                    "入力エラー", "判定(RANK)には 0 から 3 の数字を入力してください。"
                )
                return
            final_rank = rank_input
        else:
            final_rank = "2"  # 空欄時はデフォルト値 2（NORMAL）が適用される

        # 3. 選択されているアクティブなファイルの収集と各種制限チェック
        active_targets = {}
        for config in self.slots_config:
            key = config["key"]
            f_path = self.files_data[key]

            if f_path:  # ファイル未選択（空欄）の項目は自動無視
                # ファイル生存チェック
                if not os.path.exists(f_path):
                    messagebox.showerror(
                        "エラー",
                        f"「{config['label']}」に指定されたファイルが見つかりません。\n移動または削除された可能性があります。\nパス: {f_path}",
                    )
                    return

                # レベル入力制限チェック（0～99の整数のみ）
                lv_val = self.level_inputs[key].get().strip()
                if not lv_val.isdigit() or not (0 <= int(lv_val) <= 99):
                    messagebox.showerror(
                        "入力エラー",
                        f"「{config['label']}」のレベルには 0 〜 99 の整数を必ず入力してください。",
                    )
                    return

                active_targets[key] = {
                    "path": f_path,
                    "level": lv_val,
                    "label": config["label"],
                }

        if not active_targets:
            messagebox.showwarning(
                "警告", "ファイルが一つも選択されていません。"
            )
            return

        # パターンA：一括確認ダイアログの表示
        confirm_msg = f"選択された {len(active_targets)} 個のファイルを一括上書きしますか？"
        if not messagebox.askyesno("一括上書き確認", confirm_msg):
            return

        # 4. 実際のファイル書き込み＆リネームループ処理
        try:
            for key, target in active_targets.items():
                p = target["path"]
                lv = target["level"]

                # バックアップ作成（チェックマークがある場合のみ）
                if self.chk_backup_var.get():
                    shutil.copy2(p, p + ".bak")

                # ファイルの安全な読み込み
                encoding_used = "cp932"
                content = ""
                for enc in ["cp932", "utf-8", "utf-8-sig"]:
                    try:
                        with open(p, "r", encoding=enc) as f:
                            content = f.read()
                        encoding_used = enc
                        break
                    except UnicodeDecodeError:
                        continue

                lines = content.splitlines()
                new_lines = []
                main_start_idx = len(lines)
                # ★強力なZZ定義ガード★ 譜面パートの開始位置を正確に特定
                for idx, line in enumerate(lines):
                    if re.match(r"^#\d{3}\d{2}:", line.strip()):
                        main_start_idx = idx
                        break

                header_lines = lines[:main_start_idx]
                main_lines = lines[main_start_idx:]

                # ヘッダー領域内の既存タグの書き換えフラグ
                flags = {
                    "GENRE": False,
                    "TITLE": False,
                    "ARTIST": False,
                    "PLAYLEVEL": False,
                    "RANK": False,
                }

                # ヘッダー領域のみを検索・上書き（小文字やタイポ表記も逃さず上書き）
                for line in header_lines:
                    s_line = line.strip()
                    if s_line.startswith("#"):
                        parts = re.split(r"\s+", s_line, maxsplit=1)
                        cmd = parts[0].upper()

                        if (
                            cmd in ["#GENRE", "#GENRA", "#GENERE", "#GENR"]
                            and genre
                        ):
                            new_lines.append(f"#GENRE {genre}")
                            flags["GENRE"] = True
                        elif (
                            cmd in ["#TITLE", "#TITEL", "#TITL", "#TITRE"]
                            and title
                        ):
                            new_lines.append(f"#TITLE {title}")
                            flags["TITLE"] = True
                        elif (
                            cmd in ["#ARTIST", "#ARTSIT", "#ARTST"] and artist
                        ):
                            new_lines.append(f"#ARTIST {artist}")
                            flags["ARTIST"] = True
                        elif cmd == "#PLAYLEVEL":
                            new_lines.append(f"#PLAYLEVEL {lv}")
                            flags["PLAYLEVEL"] = True
                        elif cmd == "#RANK":
                            new_lines.append(f"#RANK {final_rank}")
                            flags["RANK"] = True
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)

                # ファイル内になかったヘッダーは、譜面パートの直前に新規追加（追記）
                if genre and not flags["GENRE"]:
                    new_lines.append(f"#GENRE {genre}")
                if title and not flags["TITLE"]:
                    new_lines.append(f"#TITLE {title}")
                if artist and not flags["ARTIST"]:
                    new_lines.append(f"#ARTIST {artist}")
                if not flags["PLAYLEVEL"]:
                    new_lines.append(f"#PLAYLEVEL {lv}")
                if not flags["RANK"]:
                    new_lines.append(f"#RANK {final_rank}")

                # 触れてはいけない譜面メインパートを無傷のまま再結合
                final_content = "\n".join(new_lines + main_lines)

                with open(p, "w", encoding=encoding_used, newline="") as f:
                    f.write(final_content)

                # --- ファイル名の変更（リネーム）処理 ---
                current_dir = os.path.dirname(p)
                old_filename = os.path.basename(p)
                new_filename = old_filename

                # ご指定通り「アンダーバー（_）」で連結
                if self.chk_add_title_var.get() and title:
                    new_filename = f"{title}_{new_filename}"
                if self.chk_add_id_var.get() and manage_id:
                    new_filename = f"{manage_id}_{new_filename}"

                # ファイル名に変更がある場合、安全を確認してリネーム
                if new_filename != old_filename:
                    new_full_path = os.path.join(current_dir, new_filename)
                    if not os.path.exists(new_full_path):
                        os.rename(p, new_full_path)
                        # 次の操作のために内部データも更新
                        self.files_data[key] = new_full_path
                        self.label_widgets[key].config(text=new_filename)

            messagebox.showinfo(
                "処理完了",
                "すべての対象ファイルの書き込み・リネームが完了しました！",
            )

        except Exception as e:
            messagebox.showerror(
                "システムエラー", f"書き込み中にエラーが発生しました:\n{str(e)}"
            )


# アプリケーションの起動処理
if __name__ == "__main__":
    root = tk.Tk()
    app = BMXBulkTool(root)
    root.mainloop()
