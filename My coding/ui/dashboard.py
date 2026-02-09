import customtkinter as ctk
from PIL import Image
import datetime
import os
import random
import sqlite3
from tkinter import messagebox
from backend.profile_db import get_profile, save_profile
from ui.ai_chat import AIChat
from ui.focus_timer import FocusTimerApp
from ui.calc import CalculatorApp
from ui.insights_ui import InsightsApp
from ui.todo import TodoApp

class DashboardApp(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.geometry("1280x720")
        self.title("A Day Companion - Dashboard")
        self.resizable(False, False)
        self.configure(fg_color="#0f172a")
        self.user_id = int(user_id)
        self.insights_window = None
        
        self.quotes = [
            '"Focus on being productive instead of busy."',
            '"The secret of getting ahead is getting started."',
            '"Your future is created by what you do today, not tomorrow."',
            '"Don’t watch the clock; do what it does. Keep going."',
            '"Success is the sum of small efforts, repeated day in and day out."',
            '"The only way to do great work is to love what you do."',
            '"Discipline is choosing between what you want now and what you want most."'
        ]

        profile = get_profile(self.user_id)
        if profile is None:
            self.show_profile_form()
        else:
            self.setup_main_dashboard(profile)

    def refresh_global(self):
        self.update_streak_ui()
        self.update_upcoming_ui()
        if self.insights_window and self.insights_window.winfo_exists():
            try:
                self.insights_window.refresh_views()
            except Exception:
                self.insights_window = None

    def update_streak_ui(self):
        streak = self.calculate_streak()
        color = "#f59e0b" if streak > 0 else "#64748b"
        text = f"🔥 {streak} Day Streak" if streak > 0 else "🔥 Start your streak!"
        self.streak_label.configure(text=text, text_color=color)

    def update_upcoming_ui(self):
        for widget in self.upcoming_frame.winfo_children():
            widget.destroy()
        self.load_upcoming_tasks(self.upcoming_frame)

    def open_insights(self):
        if self.insights_window is None or not self.insights_window.winfo_exists():
            self.insights_window = InsightsApp(self.user_id)
        else:
            self.insights_window.focus()

    def open_todo(self):
        TodoApp(self.user_id, on_update=self.refresh_global)

    def setup_main_dashboard(self, profile):
        for w in self.winfo_children(): w.destroy()

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

    def setup_main_dashboard(self, profile):
        for w in self.winfo_children(): w.destroy()
        
        self.user_name = profile[0]
        name_font_size = 50 
        if len(self.user_name) > 15: name_font_size = 32
        if len(self.user_name) > 25: name_font_size = 26

        self.grid_columnconfigure(0, weight=35)
        self.grid_columnconfigure(1, weight=65)
        self.grid_rowconfigure(0, weight=1)
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        
        ctk.CTkLabel(self.left_frame, text=f"Hello,\n{self.user_name}", font=("Helvetica", name_font_size, "bold"), text_color="white", justify="left", anchor="w", wraplength=400).pack(fill="x", pady=(20, 10))
        ctk.CTkFrame(self.left_frame, height=2, fg_color="#334155").pack(fill="x", pady=20)
        self.time_label = ctk.CTkLabel(self.left_frame, text="00:00", font=("Helvetica", 100, "bold"), text_color="#38bdf8")
        self.time_label.pack(anchor="w")

        self.date_label = ctk.CTkLabel(self.left_frame, text="Monday, 1st Jan", font=("Purisa", 24, "italic"), text_color="#94a3b8")
        self.date_label.pack(anchor="w", pady=(0, 30))
        self.streak_label = ctk.CTkLabel(self.left_frame, text="", font=("Helvetica", 22, "bold"), anchor="w")
        self.streak_label.pack(fill="x", pady=(0, 20))
        self.update_streak_ui()
        ctk.CTkLabel(self.left_frame, text="Up Next:", font=("Helvetica", 16, "bold"), text_color="#cbd5e1", anchor="w").pack(fill="x", pady=(0, 5))
        self.upcoming_frame = ctk.CTkFrame(self.left_frame, fg_color="#1e293b", corner_radius=15)
        self.upcoming_frame.pack(fill="x", pady=(0, 20))
        self.update_upcoming_ui()

        random_quote = random.choice(self.quotes)
        ctk.CTkLabel(self.left_frame, text=random_quote, font=("Helvetica", 16, "italic"), text_color="#64748b", justify="left", wraplength=350, anchor="w").pack(side="bottom", fill="x", pady=20)
        self.right_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=30)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(1, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_rowconfigure(2, weight=1)
        self.load_assets()

        self.create_big_button(0, 0, self.ai_img, "AI Companion", lambda: AIChat(self.user_id))
        self.create_big_button(0, 1, self.calc_img, "Calculator", CalculatorApp)
        self.create_big_button(1, 0, self.clock_img, "Focus Timer", FocusTimerApp)
        self.create_big_button(1, 1, self.insights_img, "My Insights", self.open_insights)
        self.create_big_button(2, 0, self.todo_img, "To-Do List", self.open_todo)

        self.update_clock()

    def calculate_streak(self):
        try:
            if not os.path.exists("todo.db"): return 0
            conn = sqlite3.connect("todo.db")
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT date FROM todos WHERE user_id=? AND status=1 ORDER BY date DESC", (self.user_id,))
            dates = [row[0] for row in cur.fetchall() if row[0]]
            conn.close()

            if not dates: return 0

            completed_dates = set()
            for d_str in dates:
                try: completed_dates.add(datetime.datetime.strptime(d_str, "%Y-%m-%d").date())
                except: pass

            today = datetime.date.today()
            streak = 0
            if today in completed_dates:
                streak = 1
                check_date = today - datetime.timedelta(days=1)
            elif (today - datetime.timedelta(days=1)) in completed_dates:
                streak = 1
                check_date = today - datetime.timedelta(days=2)
            else:
                return 0

            while check_date in completed_dates:
                streak += 1
                check_date -= datetime.timedelta(days=1)
            
            return streak
        except Exception:
            return 0

    def load_upcoming_tasks(self, parent):
        try:
            if not os.path.exists("todo.db"):
                ctk.CTkLabel(parent, text="No tasks yet.", text_color="gray").pack(pady=10)
                return

            conn = sqlite3.connect("todo.db")
            cur = conn.cursor()
            cur.execute("SELECT task, time FROM todos WHERE user_id=? AND status=0 ORDER BY time ASC LIMIT 3", (self.user_id,))
            tasks = cur.fetchall()
            conn.close()

            if not tasks:
                ctk.CTkLabel(parent, text="All caught up! 🎉", font=("Arial", 14), text_color="gray").pack(pady=15)
                return

            for task, time in tasks:
                row = ctk.CTkFrame(parent, fg_color="transparent")
                row.pack(fill="x", padx=10, pady=5)
                ctk.CTkLabel(row, text="•", text_color="#3b82f6", font=("Arial", 20)).pack(side="left", padx=(5, 5))
                ctk.CTkLabel(row, text=task, font=("Helvetica", 14), text_color="white", anchor="w").pack(side="left", fill="x", expand=True)
                if time:
                    ctk.CTkLabel(row, text=time, font=("Arial", 12), text_color="#94a3b8").pack(side="right")
        except Exception:
            ctk.CTkLabel(parent, text="Error loading tasks", text_color="red").pack(pady=10)

    def create_big_button(self, r, c, img, text, cmd):
        btn = ctk.CTkButton(
            self.right_frame, text=text, image=img, compound="top",
            font=("Helvetica", 24, "bold"), fg_color="#0f172a", hover_color="#334155",
            corner_radius=25, width=280, height=200, command=cmd
        )
        if r == 2:
            btn.grid(row=r, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        else:
            btn.grid(row=r, column=c, padx=20, pady=10)

    def load_assets(self):
        icon_size = (150, 150)
        def load(name):
            try: return ctk.CTkImage(Image.open(os.path.join("assets", name)), size=icon_size)
            except: return None
        self.ai_img = load("Ai.png")
        self.calc_img = load("calc.png")
        self.clock_img = load("focus_timer.png")
        self.insights_img = load("insights.png")
        self.todo_img = load("todo.png")

    def update_clock(self):
        now = datetime.datetime.now()
        self.time_label.configure(text=now.strftime("%H:%M"))
        self.date_label.configure(text=now.strftime("%A, %d %B"))
        self.after(1000, self.update_clock)