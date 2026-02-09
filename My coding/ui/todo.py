import customtkinter as ctk
import sqlite3
import threading
import time
import datetime
from plyer import notification
from tkinter import messagebox

class TodoApp(ctk.CTkToplevel):
    def __init__(self, user_id, on_update=None):
        super().__init__()
        self.user_id = user_id
        self.on_update = on_update
        
        self.geometry("600x800")
        self.title("My Tasks & Reminders")
        self.resizable(False, False)
        self.db_path = "todo.db"
        
        self.running = True
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.init_db()

        self.check_thread = threading.Thread(target=self.notification_loop, daemon=True)
        self.check_thread.start()

        header = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color="#1e293b")
        header.pack(fill="x")
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(pady=25, fill="x", padx=20)
        
        ctk.CTkLabel(title_frame, text="Tasks", font=("Helvetica", 24, "bold"), text_color="white").pack(side="left")
        ctk.CTkLabel(title_frame, text=" & Reminders", font=("Helvetica", 24), text_color="#94a3b8").pack(side="left")

        ctk.CTkButton(
            title_frame, text="Clear All", width=80, height=30, 
            fg_color="#ef4444", hover_color="#b91c1c",
            font=("Arial", 12, "bold"), command=self.clear_all_tasks
        ).pack(side="right")

        input_container = ctk.CTkFrame(self, fg_color="transparent")
        input_container.pack(pady=20, padx=20, fill="x")

        self.task_entry = ctk.CTkEntry(input_container, placeholder_text="What do you need to do?", height=50, font=("Helvetica", 14), border_width=0, fg_color="#334155", text_color="white")
        self.task_entry.pack(fill="x", pady=(0, 10))

        row2 = ctk.CTkFrame(input_container, fg_color="transparent")
        row2.pack(fill="x")

        self.time_entry = ctk.CTkEntry(row2, placeholder_text="Time (HH:MM)", width=150, height=50, font=("Helvetica", 14), border_width=0, fg_color="#334155", text_color="white")
        self.time_entry.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(row2, text="(Please use 24h format)", text_color="gray").pack(side="left")

        ctk.CTkButton(row2, text="+ Add Task", width=120, height=50, font=("Helvetica", 15, "bold"), fg_color="#3b82f6", hover_color="#2563eb", command=self.add_task).pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color="#334155")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.load_tasks()

    def notify_update(self):
        """Helper to trigger the dashboard update"""
        if self.on_update:
            self.on_update()

    def on_close(self):
        self.running = False
        self.destroy()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                task TEXT,
                time TEXT,
                status INTEGER DEFAULT 0,
                notified INTEGER DEFAULT 0
            )
        """)
        cur.execute("PRAGMA table_info(todos)")
        columns = [info[1] for info in cur.fetchall()]
        if 'time' not in columns: cur.execute("ALTER TABLE todos ADD COLUMN time TEXT")
        if 'notified' not in columns: cur.execute("ALTER TABLE todos ADD COLUMN notified INTEGER DEFAULT 0")
        if 'date' not in columns: cur.execute("ALTER TABLE todos ADD COLUMN date TEXT")
        conn.commit()
        conn.close()

    def add_task(self):
        task = self.task_entry.get().strip()
        time_str = self.time_entry.get().strip()
        if not task: return
        if time_str:
            try: datetime.datetime.strptime(time_str, "%H:%M")
            except ValueError:
                messagebox.showerror("Error", "Invalid Time Format.")
                return
        
        today_str = datetime.date.today().isoformat()
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO todos (user_id, task, time, date, status, notified) VALUES (?, ?, ?, ?, 0, 0)", 
                    (self.user_id, task, time_str, today_str))
        conn.commit()
        conn.close()
        
        self.task_entry.delete(0, "end")
        self.time_entry.delete(0, "end")
        self.load_tasks()
        self.notify_update() # TRIGGER UPDATE

    def load_tasks(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, task, time, status FROM todos WHERE user_id=? ORDER BY status ASC, time DESC", (self.user_id,))
        rows = cur.fetchall()
        conn.close()
        for tid, task, t_str, status in rows:
            self.create_item(tid, task, t_str, status)

    def create_item(self, tid, task, t_str, status):
        card_color = "#0f172a" if status else "#1e293b"
        frame = ctk.CTkFrame(self.scroll_frame, fg_color=card_color, corner_radius=10, border_width=1, border_color="#334155")
        frame.pack(fill="x", pady=5)
        
        is_done = ctk.IntVar(value=status)
        
        def toggle():
            new_s = is_done.get()
            conn = sqlite3.connect(self.db_path)
            conn.execute("UPDATE todos SET status=? WHERE id=?", (new_s, tid))
            conn.commit()
            conn.close()
            self.load_tasks()
            self.notify_update() # TRIGGER UPDATE

        ctk.CTkCheckBox(frame, text="", variable=is_done, command=toggle, width=24, height=24, corner_radius=12, border_color="#3b82f6", fg_color="#3b82f6").pack(side="left", padx=15, pady=15)
        
        text_frame = ctk.CTkFrame(frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, pady=10)
        
        task_color = "gray" if status else "white"
        task_font = ("Helvetica", 16, "overstrike") if status else ("Helvetica", 16)
        ctk.CTkLabel(text_frame, text=task, font=task_font, text_color=task_color, anchor="w").pack(fill="x")
        if t_str: ctk.CTkLabel(text_frame, text=f"⏰ {t_str}", font=("Arial", 12), text_color="#38bdf8", anchor="w").pack(fill="x")

        ctk.CTkButton(frame, text="✕", width=30, height=30, fg_color="transparent", hover_color="#ef4444", text_color="#ef4444", font=("Arial", 16, "bold"), command=lambda: self.delete_task(tid)).pack(side="right", padx=15)

    def delete_task(self, tid):
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM todos WHERE id=?", (tid,))
        conn.commit()
        conn.close()
        self.load_tasks()
        self.notify_update() # TRIGGER UPDATE

    def clear_all_tasks(self):
        if messagebox.askyesno("Confirm", "Delete ALL tasks?"):
            conn = sqlite3.connect(self.db_path)
            conn.execute("DELETE FROM todos WHERE user_id=?", (self.user_id,))
            conn.commit()
            conn.close()
            self.load_tasks()
            self.notify_update() # TRIGGER UPDATE

    def notification_loop(self):
        while self.running:
            try:
                now_str = datetime.datetime.now().strftime("%H:%M")
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("SELECT id, task FROM todos WHERE time=? AND notified=0 AND status=0", (now_str,))
                rows = cur.fetchall()
                for tid, task in rows:
                    notification.notify(title="Time to Focus!", message=f"Reminder: {task}", app_name="A Day Companion", timeout=10)
                    cur.execute("UPDATE todos SET notified=1 WHERE id=?", (tid,))
                conn.commit()
                conn.close()
            except: pass
            time.sleep(10)