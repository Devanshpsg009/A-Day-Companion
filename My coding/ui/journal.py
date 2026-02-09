import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime
import json

class JournalApp(ctk.CTkToplevel):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.geometry("900x700")
        self.title("My Journal - Writer's Edition")
        
        self.current_date = datetime.date.today()
        self.db_path = "journal.db"
        
        self.current_font_family = "Georgia"
        self.current_font_size = 14
        
        self.init_db()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, height=50, fg_color="#1e293b", corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")

        nav = ctk.CTkFrame(header, fg_color="transparent")
        nav.pack(pady=10)

        ctk.CTkButton(nav, text="<", width=40, command=self.prev_day, fg_color="#334155").pack(side="left", padx=10)
        self.date_label = ctk.CTkLabel(nav, text=str(self.current_date), font=("Arial", 18, "bold"), text_color="white", width=200)
        self.date_label.pack(side="left", padx=10)
        ctk.CTkButton(nav, text=">", width=40, command=self.next_day, fg_color="#334155").pack(side="left", padx=10)

        toolbar = ctk.CTkFrame(self, height=50, fg_color="#0f172a", corner_radius=0)
        toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=(10,0))

        ctk.CTkButton(toolbar, text="B", width=40, font=("Times", 16, "bold"), fg_color="#334155", hover_color="#475569", command=self.on_bold).pack(side="left", padx=2)
        ctk.CTkButton(toolbar, text="I", width=40, font=("Times", 16, "italic"), fg_color="#334155", hover_color="#475569", command=self.on_italic).pack(side="left", padx=2)
        
        ctk.CTkFrame(toolbar, width=2, height=30, fg_color="gray").pack(side="left", padx=10)
        self.colors = ["#ffffff", "#ef4444", "#3b82f6", "#22c55e", "#f59e0b", "#a855f7"]
        for col in self.colors:
            ctk.CTkButton(
                toolbar, text="", width=25, height=25, 
                fg_color=col, hover_color=col, corner_radius=5,
                command=lambda c=col: self.on_color(c)
            ).pack(side="left", padx=3)

        ctk.CTkFrame(toolbar, width=2, height=30, fg_color="gray").pack(side="left", padx=10)
        ctk.CTkButton(toolbar, text="-", width=30, fg_color="#334155", command=lambda: self.change_size(-2)).pack(side="left", padx=2)
        ctk.CTkButton(toolbar, text="+", width=30, fg_color="#334155", command=lambda: self.change_size(2)).pack(side="left", padx=2)

        ctk.CTkButton(toolbar, text="Find", width=60, fg_color="#3b82f6", command=self.find_text).pack(side="right", padx=10)

        editor_frame = ctk.CTkFrame(self, fg_color="transparent")
        editor_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        
        self.text_editor = tk.Text(
            editor_frame,
            bg="#020617", 
            fg="#e2e8f0",
            insertbackground="white",
            font=(self.current_font_family, self.current_font_size),
            selectbackground="#3b82f6",
            selectforeground="white",
            wrap="word",
            bd=0,
            highlightthickness=0
        )
        self.text_editor.pack(fill="both", expand=True)

        sb = ctk.CTkScrollbar(editor_frame, command=self.text_editor.yview)
        sb.pack(side="right", fill="y")
        self.text_editor.config(yscrollcommand=sb.set)

        self.setup_tags()
        
        self.text_editor.bind("<KeyRelease>", self.on_key_release)

        status = ctk.CTkFrame(self, height=30, fg_color="transparent")
        status.grid(row=3, column=0, sticky="ew", padx=20, pady=(0,10))
        
        self.stats_label = ctk.CTkLabel(status, text="Words: 0 | Chars: 0", text_color="gray", font=("Arial", 12))
        self.stats_label.pack(side="right")
        
        self.msg_label = ctk.CTkLabel(status, text="Ready", text_color="#38bdf8", font=("Arial", 12))
        self.msg_label.pack(side="left")

        self.load_entry()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS journal (
                user_id INTEGER,
                date TEXT,
                content TEXT,
                tags TEXT,
                PRIMARY KEY (user_id, date)
            )
        """)
        cur.execute("PRAGMA table_info(journal)")
        if 'tags' not in [c[1] for c in cur.fetchall()]:
            cur.execute("ALTER TABLE journal ADD COLUMN tags TEXT")
        conn.commit()
        conn.close()

    def setup_tags(self):
        self.text_editor.tag_configure("bold", font=(self.current_font_family, self.current_font_size, "bold"))
        self.text_editor.tag_configure("italic", font=(self.current_font_family, self.current_font_size, "italic"))
        self.text_editor.tag_configure("found", background="#f59e0b", foreground="black")
        
        for col in self.colors:
            self.text_editor.tag_configure(f"color_{col}", foreground=col)

    def toggle_tag(self, tag_name):
        try:
            if not self.text_editor.tag_ranges("sel"):
                self.msg_label.configure(text="⚠ Select text first!", text_color="orange")
                return

            current_tags = self.text_editor.tag_names("sel.first")
            
            if tag_name in current_tags:
                self.text_editor.tag_remove(tag_name, "sel.first", "sel.last")
                self.msg_label.configure(text=f"Removed {tag_name}", text_color="gray")
            else:
                self.text_editor.tag_add(tag_name, "sel.first", "sel.last")
                self.msg_label.configure(text=f"Applied {tag_name}", text_color="#38bdf8")
            
            self.save_entry()
        except tk.TclError:
            pass

    def on_bold(self): self.toggle_tag("bold")
    def on_italic(self): self.toggle_tag("italic")
    
    def on_color(self, color):
        try:
            if not self.text_editor.tag_ranges("sel"):
                self.msg_label.configure(text="⚠ Select text first!", text_color="orange")
                return
            
            for c in self.colors:
                self.text_editor.tag_remove(f"color_{c}", "sel.first", "sel.last")
            
            self.text_editor.tag_add(f"color_{color}", "sel.first", "sel.last")
            self.msg_label.configure(text=f"Color applied", text_color=color)
            self.save_entry()
        except: pass

    def change_size(self, delta):
        self.current_font_size += delta
        if self.current_font_size < 10: self.current_font_size = 10
        
        base_font = (self.current_font_family, self.current_font_size)
        self.text_editor.configure(font=base_font)
        
        self.text_editor.tag_configure("bold", font=(self.current_font_family, self.current_font_size, "bold"))
        self.text_editor.tag_configure("italic", font=(self.current_font_family, self.current_font_size, "italic"))
        
        self.msg_label.configure(text=f"Font Size: {self.current_font_size}", text_color="white")

    def find_text(self):
        dialog = ctk.CTkInputDialog(text="Search for:", title="Find")
        s = dialog.get_input()
        if s:
            self.text_editor.tag_remove("found", "1.0", "end")
            start = "1.0"
            count = 0
            while True:
                pos = self.text_editor.search(s, start, stopindex="end")
                if not pos: break
                end = f"{pos}+{len(s)}c"
                self.text_editor.tag_add("found", pos, end)
                count += 1
                start = end
            self.msg_label.configure(text=f"Found {count} matches", text_color="#f59e0b")

    def on_key_release(self, event=None):
        content = self.text_editor.get("1.0", "end-1c")
        words = len(content.split()) if content.strip() else 0
        self.stats_label.configure(text=f"Words: {words} | Chars: {len(content)}")
        self.save_entry()

    def save_entry(self, event=None):
        content = self.text_editor.get("1.0", "end-1c")
        
        tags_data = []
        tags_to_check = ["bold", "italic"] + [f"color_{c}" for c in self.colors]
        
        for tag in tags_to_check:
            ranges = self.text_editor.tag_ranges(tag)
            for i in range(0, len(ranges), 2):
                tags_data.append({
                    "t": tag,
                    "s": str(ranges[i]),
                    "e": str(ranges[i+1])
                })

        json_tags = json.dumps(tags_data)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO journal (user_id, date, content, tags) VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET content=excluded.content, tags=excluded.tags
        """, (self.user_id, str(self.current_date), content, json_tags))
        conn.commit()
        conn.close()
        self.msg_label.configure(text="Saved", text_color="#22c55e")

    def load_entry(self):
        self.date_label.configure(text=self.current_date.strftime("%B %d, %Y"))
        self.text_editor.delete("1.0", "end")
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT content, tags FROM journal WHERE user_id=? AND date=?", (self.user_id, str(self.current_date)))
        row = cur.fetchone()
        conn.close()

        if row:
            content, json_tags = row
            self.text_editor.insert("1.0", content)
            if json_tags:
                try:
                    data = json.loads(json_tags)
                    for item in data:
                        self.text_editor.tag_add(item["t"], item["s"], item["e"])
                except: pass
        
        self.on_key_release()
        self.msg_label.configure(text="Loaded", text_color="#38bdf8")

    def prev_day(self):
        self.current_date -= datetime.timedelta(days=1)
        self.load_entry()

    def next_day(self):
        self.current_date += datetime.timedelta(days=1)
        self.load_entry()