import customtkinter as ctk
from PIL import Image
import datetime
import os
import random
import sqlite3
import threading
import pystray
import sys
import queue
from tkinter import messagebox
from backend.profile_db import get_profile, save_profile
from ui.ai_chat import AIChat
from ui.focus_timer import FocusTimerApp
from ui.calc import CalculatorApp
from ui.insights_ui import InsightsApp
from ui.todo import TodoApp
from ui.journal import JournalApp

class DashboardApp(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.geometry("1280x720")
        self.title("A Day Companion")
        self.resizable(False, False)
        self.configure(fg_color="#0f172a")

        self.user_id = int(user_id)
        self.insights_window = None
        self.tray_queue = queue.Queue()
        self.tray_icon = None
        self.tray_running = False

        self.quotes = [
            '"Focus on being productive instead of busy."',
            '"The secret of getting ahead is getting started."',
            '"Your future is created by what you do today, not tomorrow."',
            '"Don’t watch the clock; do what it does. Keep going."',
            '"Success is the sum of small efforts, repeated day in and day out."',
            '"The only way to do great work is to love what you do."',
            '"Discipline is choosing between what you want now and what you want most."'
        ]

        try:
            self.tray_image = Image.open("assets/Ai.png")
        except:
            self.tray_image = Image.new("RGB", (64, 64), "white")

        self.start_tray()
        self.check_tray_queue()

        profile = get_profile(self.user_id)
        if profile is None:
            self.show_profile_form()
        else:
            self.setup_main_dashboard(profile)

    # --- TRAY LOGIC ---
    def start_tray(self):
        if self.tray_running:
            return

        menu = pystray.Menu(
            pystray.MenuItem("Open", self.tray_open),
            pystray.MenuItem("Quit", self.tray_quit)
        )

        self.tray_icon = pystray.Icon(
            "adaycompanion",
            self.tray_image,
            "A Day Companion",
            menu
        )

        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        self.tray_running = True

    def tray_open(self, icon, item):
        self.tray_queue.put("OPEN")

    def tray_quit(self, icon, item):
        self.tray_queue.put("QUIT")

    def check_tray_queue(self):
        try:
            while True:
                msg = self.tray_queue.get_nowait()
                if msg == "OPEN":
                    self.restore_window()
                elif msg == "QUIT":
                    self.exit_app()
        except queue.Empty:
            pass
        self.after(100, self.check_tray_queue)

    def minimize_to_tray(self):
        self.withdraw()

    def restore_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def exit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()
        sys.exit(0)

    def setup_main_dashboard(self, profile):
        for w in self.winfo_children():
            w.destroy()

        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        self.user_name = profile[0]

        self.grid_columnconfigure(0, weight=35)
        self.grid_columnconfigure(1, weight=65)
        self.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)

        ctk.CTkLabel(left, text=f"Hello,\n{self.user_name}", font=("Helvetica", 42, "bold"), text_color="white", justify="left").pack(anchor="w", pady=(0, 20))

        self.time_label = ctk.CTkLabel(left, font=("Helvetica", 100, "bold"), text_color="#38bdf8")
        self.time_label.pack(anchor="w")

        self.date_label = ctk.CTkLabel(left, font=("Helvetica", 24), text_color="#94a3b8")
        self.date_label.pack(anchor="w", pady=(0, 30))

        self.streak_label = ctk.CTkLabel(left, text="", font=("Helvetica", 22, "bold"), anchor="w")
        self.streak_label.pack(fill="x", pady=(0, 20))
        self.update_streak_ui()

        ctk.CTkLabel(left, text="Up Next:", font=("Helvetica", 16, "bold"), text_color="#cbd5e1", anchor="w").pack(fill="x", pady=(0, 5))
        self.upcoming_frame = ctk.CTkFrame(left, fg_color="#1e293b", corner_radius=15)
        self.upcoming_frame.pack(fill="x", pady=(0, 20))
        self.update_upcoming_ui()

        ctk.CTkLabel(left, text=random.choice(self.quotes), font=("Helvetica", 16, "italic"), text_color="#64748b", wraplength=350, justify="left").pack(side="bottom", pady=20, anchor="w")

        right = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=30)
        right.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        right.grid_columnconfigure((0, 1), weight=1)
        right.grid_rowconfigure((0, 1, 2), weight=1)

        self.load_assets()

        self.create_btn(right, 0, 0, self.ai_img, "AI Companion", lambda: AIChat(self.user_id))
        self.create_btn(right, 0, 1, self.calc_img, "Calculator", CalculatorApp)
        self.create_btn(right, 1, 0, self.clock_img, "Focus Timer", FocusTimerApp)
        self.create_btn(right, 1, 1, self.insights_img, "Insights", self.open_insights)
        self.create_btn(right, 2, 0, self.todo_img, "To-Do List", self.open_todo)
        self.create_btn(right, 2, 1, self.journal_img, "Journal", lambda: JournalApp(self.user_id))
        
        self.update_clock()

    def refresh_global(self):
        self.update_streak_ui()
        self.update_upcoming_ui()
        if self.insights_window and self.insights_window.winfo_exists():
            try: self.insights_window.refresh_views()
            except: self.insights_window = None

    def update_streak_ui(self):
        streak = self.calculate_streak()
        color = "#f59e0b" if streak > 0 else "#64748b"
        text = f"🔥 {streak} Day Streak" if streak > 0 else "🔥 Start your streak!"
        self.streak_label.configure(text=text, text_color=color)

    def update_upcoming_ui(self):
        for w in self.upcoming_frame.winfo_children(): w.destroy()
        self.load_upcoming_tasks(self.upcoming_frame)

    def calculate_streak(self):
        try:
            if not os.path.exists("todo.db"): return 0
            conn = sqlite3.connect("todo.db")
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT date FROM todos WHERE user_id=? AND status=1 ORDER BY date DESC", (self.user_id,))
            dates = [row[0] for row in cur.fetchall() if row[0]]
            conn.close()
            if not dates: return 0
            
            comp_dates = set()
            for d in dates: 
                try: comp_dates.add(datetime.datetime.strptime(d, "%Y-%m-%d").date())
                except: pass
            
            today = datetime.date.today()
            streak = 0
            if today in comp_dates:
                streak = 1
                check = today - datetime.timedelta(days=1)
            elif (today - datetime.timedelta(days=1)) in comp_dates:
                streak = 1
                check = today - datetime.timedelta(days=2)
            else: return 0
            
            while check in comp_dates:
                streak += 1
                check -= datetime.timedelta(days=1)
            return streak
        except: return 0

    def load_upcoming_tasks(self, parent):
        try:
            if not os.path.exists("todo.db"): return
            conn = sqlite3.connect("todo.db")
            cur = conn.cursor()
            cur.execute("SELECT task, time FROM todos WHERE user_id=? AND status=0 ORDER BY time ASC LIMIT 3", (self.user_id,))
            tasks = cur.fetchall()
            conn.close()
            if not tasks: ctk.CTkLabel(parent, text="All caught up! 🎉", font=("Arial", 14), text_color="gray").pack(pady=15); return
            for task, time in tasks:
                r = ctk.CTkFrame(parent, fg_color="transparent")
                r.pack(fill="x", padx=10, pady=5)
                ctk.CTkLabel(r, text="•", text_color="#3b82f6", font=("Arial", 20)).pack(side="left", padx=5)
                ctk.CTkLabel(r, text=task, font=("Helvetica", 14), text_color="white", anchor="w").pack(side="left", fill="x", expand=True)
                if time: ctk.CTkLabel(r, text=time, font=("Arial", 12), text_color="#94a3b8").pack(side="right")
        except: pass

    def open_insights(self):
        if not self.insights_window or not self.insights_window.winfo_exists():
            self.insights_window = InsightsApp(self.user_id)
        else:
            self.insights_window.focus()

    def open_todo(self):
        TodoApp(self.user_id, on_update=self.refresh_global)

    def create_btn(self, p, r, c, img, txt, cmd):
        ctk.CTkButton(p, text=txt, image=img, compound="top", font=("Helvetica", 22, "bold"),
                      fg_color="#0f172a", hover_color="#334155",
                      corner_radius=25, width=280, height=200, command=cmd).grid(row=r, column=c, padx=20, pady=10)

    def load_assets(self):
        def load(n):
            try: return ctk.CTkImage(Image.open(os.path.join("assets", n)), size=(150, 150))
            except: return None
        self.ai_img = load("Ai.png")
        self.calc_img = load("calc.png")
        self.clock_img = load("focus_timer.png")
        self.insights_img = load("insights.png")
        self.todo_img = load("todo.png")
        self.journal_img = load("journal.png")

    def update_clock(self):
        now = datetime.datetime.now()
        self.time_label.configure(text=now.strftime("%H:%M"))
        self.date_label.configure(text=now.strftime("%A, %d %B"))
        self.after(1000, self.update_clock)
        
    def show_profile_form(self):
        for w in self.winfo_children(): w.destroy()
        card = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=20, border_color="#334155", border_width=2)
        card.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(card, text="Welcome to Your Companion", font=("Helvetica", 24, "bold"), text_color="white").pack(pady=(30, 10), padx=50)
        ctk.CTkLabel(card, text="Let's personalize your experience.", font=("Helvetica", 14), text_color="#94a3b8").pack(pady=(0, 20))
        self.name_entry = self.create_input(card, "Full Name (e.g. Devansh)")
        self.class_entry = self.create_input(card, "Class/Grade (e.g. B.Tech 2nd Year)")
        self.hobbies_entry = self.create_input(card, "Hobbies (e.g. Coding, Guitar)")
        self.goals_entry = self.create_input(card, "Top Goals (e.g. 9 CGPA, Learn AI)")
        ctk.CTkButton(card, text="Save Profile", width=200, height=45, font=("Helvetica", 15, "bold"), fg_color="#3b82f6", hover_color="#2563eb", command=self.save_profile_data).pack(pady=30)

    def create_input(self, parent, placeholder):
        entry = ctk.CTkEntry(parent, width=350, height=45, placeholder_text=placeholder, font=("Helvetica", 14))
        entry.pack(pady=10, padx=40)
        return entry

    def save_profile_data(self):
        name = self.name_entry.get().strip()
        cls = self.class_entry.get().strip()
        hobbies = self.hobbies_entry.get().strip()
        goals = self.goals_entry.get().strip()
        if name and cls:
            save_profile(self.user_id, name, cls, hobbies, goals)
            self.setup_main_dashboard(get_profile(self.user_id))
        else:
            messagebox.showerror("Required", "Please enter at least your Name and Class.")