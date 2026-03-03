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
        ctk.CTkLabel(title_frame, text="Tasks & Reminders", font=("Helvetica", 24, "bold"), text_color="white").pack(side="left")
        ctk.CTkButton(title_frame, text="Clear All", width=80, height=30, fg_color="#ef4444", hover_color="#b91c1c", command=self.clear_all_tasks).pack(side="right")

        input_container = ctk.CTkFrame(self, fg_color="transparent")
        input_container.pack(pady=20, padx=20, fill="x")
        self.task_entry = ctk.CTkEntry(input_container, placeholder_text="What do you need to do?", height=50, fg_color="#334155", text_color="white")
        self.task_entry.pack(fill="x", pady=(0, 10))

        row2 = ctk.CTkFrame(input_container, fg_color="transparent")
        row2.pack(fill="x")
        self.time_entry = ctk.CTkEntry(row2, placeholder_text="Time (HH:MM)", width=150, height=50, fg_color="#334155", text_color="white")
        self.time_entry.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(row2, text="(24h format)", text_color="gray").pack(side="left")
        ctk.CTkButton(row2, text="+ Add", width=120, height=50, fg_color="#3b82f6", command=self.add_task).pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.load_tasks()

    def on_close(self):
        self.running = False
        self.destroy()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, task TEXT, time TEXT, status INTEGER DEFAULT 0, notified INTEGER DEFAULT 0, date TEXT
                )
            """)

    def add_task(self):
        task, time_str = self.task_entry.get().strip(), self.time_entry.get().strip()
        if not task: return
        if time_str:
            try: datetime.datetime.strptime(time_str, "%H:%M")
            except ValueError: return messagebox.showerror("Error", "Invalid Time.")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO todos (user_id, task, time, date, status, notified) VALUES (?, ?, ?, ?, 0, 0)", 
                         (self.user_id, task, time_str, datetime.date.today().isoformat()))
        
        self.task_entry.delete(0, "end")
        self.time_entry.delete(0, "end")
        self.load_tasks()
        if self.on_update: self.on_update()

    def load_tasks(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT id, task, time, status FROM todos WHERE user_id=? ORDER BY status ASC, time DESC", (self.user_id,)).fetchall()
        for tid, task, t_str, status in rows:
            self.create_item(tid, task, t_str, status)

    def create_item(self, tid, task, t_str, status):
        frame = ctk.CTkFrame(self.scroll_frame, fg_color="#0f172a" if status else "#1e293b", corner_radius=10, border_width=1, border_color="#334155")
        frame.pack(fill="x", pady=5)
        is_done = ctk.IntVar(value=status)
        
        def toggle():
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("UPDATE todos SET status=? WHERE id=?", (is_done.get(), tid))
            self.load_tasks()
            if self.on_update: self.on_update()

        ctk.CTkCheckBox(frame, text="", variable=is_done, command=toggle, width=24, height=24).pack(side="left", padx=15, pady=15)
        text_frame = ctk.CTkFrame(frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, pady=10)
        ctk.CTkLabel(text_frame, text=task, font=("Helvetica", 16, "overstrike" if status else "normal"), text_color="gray" if status else "white", anchor="w").pack(fill="x")
        if t_str: ctk.CTkLabel(text_frame, text=f"⏰ {t_str}", font=("Arial", 12), text_color="#38bdf8", anchor="w").pack(fill="x")
        ctk.CTkButton(frame, text="✕", width=30, height=30, fg_color="transparent", text_color="#ef4444", command=lambda: self.delete_task(tid)).pack(side="right", padx=15)

    def delete_task(self, tid):
        with sqlite3.connect(self.db_path) as conn: conn.execute("DELETE FROM todos WHERE id=?", (tid,))
        self.load_tasks()
        if self.on_update: self.on_update()

    def clear_all_tasks(self):
        if messagebox.askyesno("Confirm", "Delete ALL tasks?"):
            with sqlite3.connect(self.db_path) as conn: conn.execute("DELETE FROM todos WHERE user_id=?", (self.user_id,))
            self.load_tasks()
            if self.on_update: self.on_update()

    def notification_loop(self):
        while self.running:
            try:
                now_str = datetime.datetime.now().strftime("%H:%M")
                with sqlite3.connect(self.db_path) as conn:
                    rows = conn.execute("SELECT id, task FROM todos WHERE time=? AND notified=0 AND status=0", (now_str,)).fetchall()
                    for tid, task in rows:
                        notification.notify(title="Time to Focus!", message=f"Reminder: {task}", app_name="A Day Companion", timeout=10)
                        conn.execute("UPDATE todos SET notified=1 WHERE id=?", (tid,))
            except: pass
            time.sleep(10)