import shutil
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
import webbrowser
from tkinter import messagebox, PhotoImage
import io
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def pil_image_to_ctk(pil_img, size=None):
    """Convert PIL Image to ctk.CTkImage using PPM format"""
    try:
        if size:
            pil_img = pil_img.resize(size, Image.Resampling.LANCZOS)
        # Try to create CTkImage - will fail if ImageTk not available
        try:
            return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size if size else pil_img.size)
        except ImportError:
            # ImageTk not available, use PPM as fallback
            with io.BytesIO() as output:
                pil_img.save(output, format="PPM")
                data = output.getvalue()
            tk_img = PhotoImage(data=data)
            # Wrap PhotoImage in a lambda to keep reference alive
            pil_img._tk_image_ref = tk_img
            # Return None, let caller handle it
            return None
    except Exception:
        return None
from tkinter import messagebox
from backend.profile_db import get_profile, save_profile
from ui.ai_chat import AIChat
from ui.focus_timer import FocusTimerApp
from ui.calc import CalculatorApp
from ui.insights_ui import InsightsApp
from ui.todo import TodoApp
from ui.journal import JournalApp
from ui.health_reminder import HealthReminderApp

load_dotenv()

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
            '"Success is the sum of small efforts, repeated day in and day out."'
        ]

        try: self.tray_image = Image.open(os.path.join(ASSETS_DIR, "Ai.png"))
        except: self.tray_image = Image.new("RGB", (64, 64), "white")

        self.start_tray()
        self.check_tray_queue()
        profile = get_profile(self.user_id)
        if profile is None: self.show_profile_form()
        else: self.setup_main_dashboard(profile)

    def start_tray(self):
        if self.tray_running: return
        menu = pystray.Menu(pystray.MenuItem("Open", lambda *args: self.tray_queue.put("OPEN")),
                            pystray.MenuItem("Quit", lambda *args: self.tray_queue.put("QUIT")))
        self.tray_icon = pystray.Icon("adaycompanion", self.tray_image, "A Day Companion", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        self.tray_running = True

    def check_tray_queue(self):
        try:
            while True:
                msg = self.tray_queue.get_nowait()
                if msg == "OPEN": self.deiconify(); self.lift(); self.focus_force()
                elif msg == "QUIT": self.tray_icon.stop(); self.destroy(); self.cleanup(); sys.exit(0)
        except queue.Empty: pass
        self.after(100, self.check_tray_queue)

    def setup_main_dashboard(self, profile):
        for w in self.winfo_children(): w.destroy()
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.grid_columnconfigure(0, weight=35)
        self.grid_columnconfigure(1, weight=65)
        self.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        ctk.CTkLabel(left, text=f"Hello,\n{profile[0]}", font=("Helvetica", 42, "bold"), text_color="white", justify="left").pack(anchor="w", pady=(0, 20))
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
        for i in range(2): right.grid_columnconfigure(i, weight=1)
        for i in range(4): right.grid_rowconfigure(i, weight=1)
        self.load_assets()
        
        self.health_tracker = HealthReminderApp(self)
        
        btns = [
            (0, 0, self.ai_img, "AI Companion", self.open_ai_chat), 
            (0, 1, self.calc_img, "Calculator", CalculatorApp),
            (1, 0, self.clock_img, "Focus Timer", FocusTimerApp), 
            (1, 1, self.insights_img, "Insights", self.open_insights),
            (2, 0, self.todo_img, "To-Do List", lambda: TodoApp(self.user_id, self.refresh_global)), 
            (2, 1, self.journal_img, "Journal", lambda: JournalApp(self.user_id)),
            (3, 0, self.chess_img, "Chess", self.open_chess),
            (3, 1, self.health_img, "Health Tracker", self.health_tracker.show_window)
        ]
        for r, c, img, txt, cmd in btns:
            ctk.CTkButton(right, text=txt, image=img, compound="top", font=("Helvetica", 22, "bold"), fg_color="#0f172a", corner_radius=25, width=280, height=200, command=cmd).grid(row=r, column=c, padx=20, pady=10)
        self.update_clock()

    def open_ai_chat(self):
        key = os.getenv("GROQ_API_KEY")
        if key and key.strip(): AIChat(self.user_id)
        else:
            if messagebox.askokcancel("Setup AI", "Click OK to get a free key, then paste it here."):
                webbrowser.open("https://console.groq.com/keys")
                new_key = ctk.CTkInputDialog(text="Paste Groq API Key:", title="Setup").get_input()
                if new_key and new_key.strip():
                    with open(".env", "a") as f: f.write(f"\nGROQ_API_KEY={new_key.strip()}\n")
                    os.environ["GROQ_API_KEY"] = new_key.strip()
                    AIChat(self.user_id)

    def refresh_global(self):
        self.update_streak_ui()
        self.update_upcoming_ui()
        if self.insights_window and self.insights_window.winfo_exists():
            try: self.insights_window.refresh_views()
            except: self.insights_window = None

    def update_streak_ui(self):
        streak = self.calculate_streak()
        self.streak_label.configure(text=f"🔥 {streak} Day Streak" if streak > 0 else "🔥 Start your streak!", text_color="#f59e0b" if streak > 0 else "#64748b")

    def update_upcoming_ui(self):
        for w in self.upcoming_frame.winfo_children(): w.destroy()
        try:
            with sqlite3.connect("todo.db") as conn:
                tasks = conn.execute("SELECT task, time FROM todos WHERE user_id=? AND status=0 ORDER BY time ASC LIMIT 3", (self.user_id,)).fetchall()
            if not tasks: ctk.CTkLabel(self.upcoming_frame, text="All caught up! 🎉", text_color="gray").pack(pady=15); return
            for task, time_str in tasks:
                r = ctk.CTkFrame(self.upcoming_frame, fg_color="transparent")
                r.pack(fill="x", padx=10, pady=5)
                ctk.CTkLabel(r, text="•", text_color="#3b82f6", font=("Arial", 20)).pack(side="left", padx=5)
                ctk.CTkLabel(r, text=task, text_color="white", anchor="w").pack(side="left", fill="x", expand=True)
                if time_str: ctk.CTkLabel(r, text=time_str, text_color="#94a3b8").pack(side="right")
        except: pass

    def calculate_streak(self):
        try:
            with sqlite3.connect("todo.db") as conn:
                dates = [r[0] for r in conn.execute("SELECT DISTINCT date FROM todos WHERE user_id=? AND status=1 ORDER BY date DESC", (self.user_id,)).fetchall() if r[0]]
            comp_dates = {datetime.datetime.strptime(d, "%Y-%m-%d").date() for d in dates}
            today = datetime.date.today()
            streak, check = (1, today - datetime.timedelta(days=1)) if today in comp_dates else (1, today - datetime.timedelta(days=2)) if (today - datetime.timedelta(days=1)) in comp_dates else (0, None)
            while check and check in comp_dates:
                streak += 1; check -= datetime.timedelta(days=1)
            return streak
        except: return 0

    def open_insights(self):
        if not self.insights_window or not self.insights_window.winfo_exists(): self.insights_window = InsightsApp(self.user_id)
        else: self.insights_window.focus()

    def load_assets(self):
        def load(n):
            try:
                img = Image.open(os.path.join(ASSETS_DIR, n))
                return pil_image_to_ctk(img, size=(150, 150))
            except:
                return None
        self.ai_img, self.calc_img, self.clock_img, self.insights_img, self.todo_img, self.journal_img, self.chess_img, self.health_img = map(load, ["Ai.png", "calc.png", "focus_timer.png", "insights.png", "todo.png", "journal.png", "chess.png", "health.png"])

    def update_clock(self):
        now = datetime.datetime.now()
        self.time_label.configure(text=now.strftime("%H:%M"))
        self.date_label.configure(text=now.strftime("%A, %d %B"))
        self.after(1000, self.update_clock)
        
    def show_profile_form(self):
        for w in self.winfo_children(): w.destroy()
        card = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=20, border_width=2)
        card.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(card, text="Welcome to A Day Companion", font=("Helvetica", 24, "bold")).pack(pady=(30, 10), padx=50)
        self.name_entry = ctk.CTkEntry(card, width=350, height=45, placeholder_text="Full Name (e.g. James)"); self.name_entry.pack(pady=10)
        self.class_entry = ctk.CTkEntry(card, width=350, height=45, placeholder_text="Class/Grade (e.g. 10th/B.Tech 1st yr)"); self.class_entry.pack(pady=10)
        self.hobbies_entry = ctk.CTkEntry(card, width=350, height=45, placeholder_text="Hobbies"); self.hobbies_entry.pack(pady=10)
        self.goals_entry = ctk.CTkEntry(card, width=350, height=45, placeholder_text="Top Goals"); self.goals_entry.pack(pady=10)
        ctk.CTkButton(card, text="Save Profile", width=200, height=45, fg_color="#3b82f6", command=self.save_profile_data).pack(pady=30)

    def save_profile_data(self):
        name, cls = self.name_entry.get().strip(), self.class_entry.get().strip()
        if name and cls:
            save_profile(self.user_id, name, cls, self.hobbies_entry.get().strip(), self.goals_entry.get().strip())
            self.setup_main_dashboard(get_profile(self.user_id))
        else: messagebox.showerror("Required", "Please enter at least your Name and Class.")

    def open_chess(self):
        import backend.chess_runner as chess_runner
        chess_runner.main()
        
    def cleanup(self):
        targets = ['backend', 'ui', '.']
        for target in targets:
            pycache_path = os.path.join(target, '__pycache__')
            if os.path.exists(pycache_path):
                try: shutil.rmtree(pycache_path)
                except: pass