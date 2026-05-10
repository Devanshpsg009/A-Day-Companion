import customtkinter as ctk
import psutil
import sqlite3
import threading
import time
import datetime
import getpass
import os
import queue
from tkinter import messagebox
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
popup_queue = queue.Queue()

def _import_matplotlib():
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    return plt, FigureCanvasTkAgg

def clean_app_name(raw_name):
    if not raw_name:
        return ""
    name = raw_name.lower().replace(".exe", "")
    name = name.replace("-", " ").replace("_", " ")
    return name.title()

def init_wellbeing_db():
    with sqlite3.connect("wellbeing.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wellbeing_apps (
                user_id INTEGER,
                app_name TEXT,
                limit_minutes INTEGER,
                used_seconds INTEGER DEFAULT 0,
                last_reset_date TEXT,
                PRIMARY KEY (user_id, app_name)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS app_usage_history (
                user_id INTEGER,
                app_name TEXT,
                date TEXT,
                used_seconds INTEGER,
                PRIMARY KEY (user_id, app_name, date)
            )
        """)

def get_user_running_apps():
    current_user = getpass.getuser().lower()
    app_list = set()
    for proc in psutil.process_iter(['name', 'username']):
        try:
            proc_user = proc.info.get('username')
            if proc_user and current_user in proc_user.lower():
                name = proc.info.get('name')
                if name and "python" not in name.lower() and "cmd" not in name.lower():
                    app_list.add(clean_app_name(name))
        except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
            pass
    return sorted(list(app_list))

class DigitalWellbeingDaemon:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db_path = "wellbeing.db"
        self.running = True
        self.warning_issued = set()
        init_wellbeing_db()

    def start(self):
        threading.Thread(target=self.monitor_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def monitor_loop(self):
        while self.running:
            today = datetime.date.today().isoformat()
            self._reset_daily_timers(today)
            running_apps = set()
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info.get('name')
                    if name:
                        running_apps.add(clean_app_name(name).lower())
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            with sqlite3.connect(self.db_path) as conn:
                tracked_apps = conn.execute(
                    "SELECT app_name, limit_minutes, used_seconds FROM wellbeing_apps WHERE user_id=?", 
                    (self.user_id,)
                ).fetchall()

                for app_name, limit_minutes, used_seconds in tracked_apps:
                    app_lower = app_name.lower()
                    if app_lower in running_apps:
                        new_used_seconds = used_seconds + 10
                        conn.execute(
                            "UPDATE wellbeing_apps SET used_seconds=? WHERE app_name=? AND user_id=?",
                            (new_used_seconds, app_name, self.user_id)
                        )
                        conn.execute("""
                            INSERT INTO app_usage_history (user_id, app_name, date, used_seconds)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(user_id, app_name, date) DO UPDATE SET used_seconds=?
                        """, (self.user_id, app_name, today, new_used_seconds, new_used_seconds))
                        conn.commit()
                        
                        limit_seconds = limit_minutes * 60
                        time_left = limit_seconds - new_used_seconds

                        if time_left > 120 and app_name in self.warning_issued:
                            self.warning_issued.remove(app_name)

                        if 0 < time_left <= 120 and app_name not in self.warning_issued:
                            popup_queue.put({"type": "warning", "app": app_name})
                            self.warning_issued.add(app_name)

                        if time_left <= 0:
                            self.kill_app(app_lower)
            time.sleep(10)

    def _reset_daily_timers(self, today):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE wellbeing_apps SET used_seconds=0, last_reset_date=? WHERE last_reset_date != ?",
                (today, today)
            )
            if cursor.rowcount > 0:
                self.warning_issued.clear()

    def kill_app(self, target_app_name):
        killed = False
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info.get('name')
                if name and clean_app_name(name).lower() == target_app_name:
                    proc.kill()
                    killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if killed:
            popup_queue.put({"type": "killed", "app": target_app_name})


class AnimatedGifLabel(ctk.CTkLabel):
    def __init__(self, master, gif_path, size=(180, 180), **kwargs):
        super().__init__(master, text="", **kwargs)
        self.frames = []
        self.delay = 100
        self.current_frame = 0
        try:
            img = Image.open(gif_path)
            if "duration" in img.info and img.info["duration"] > 0:
                self.delay = img.info["duration"]
            for i in range(img.n_frames):
                img.seek(i)
                frame_image = img.copy().convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                ctk_frame = ctk.CTkImage(light_image=frame_image, dark_image=frame_image, size=size)
                if ctk_frame:
                    self.frames.append(ctk_frame)
            if self.frames:
                self.configure(image=self.frames[0])
                self.animate()
        except Exception:
            pass

    def animate(self):
        if not self.winfo_exists() or not self.frames:
            return
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.configure(image=self.frames[self.current_frame])
        self.after(self.delay, self.animate)


class DigitalWellbeingApp(ctk.CTkToplevel):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.title("Digital Wellbeing & Health Tracker")
        self.geometry("900x700")
        self.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.withdraw()
        init_wellbeing_db()
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(expand=True, fill="both", padx=20, pady=20)
        self.tabs.add("App Limits")
        self.tabs.add("Usage Stats")
        self.tabs.add("Physical Health")
        self.app_widgets = {}
        self.build_app_limits_tab()
        self.build_usage_stats_tab()
        self.build_physical_health_tab()
        self.running = False
        self.time_elapsed = 0
        self.start_tracking()
        self.start_ui_updater()
        self.check_popups()

    def check_popups(self):
        if not self.winfo_exists():
            return
        try:
            while True:
                msg = popup_queue.get_nowait()
                if msg["type"] == "warning":
                    self.show_warning_popup(msg["app"])
                elif msg["type"] == "killed":
                    self.show_killed_popup(msg["app"])
        except queue.Empty:
            pass
        self.after(1000, self.check_popups)

    def show_warning_popup(self, app_name):
        dummy = ctk.CTkToplevel(self)
        dummy.attributes("-alpha", 0.0)
        dummy.attributes("-topmost", True)
        messagebox.showwarning(
            "⚠️ Time Limit Warning",
            f"SAVE YOUR WORK!\n\nYour time limit for {app_name.title()} is almost up.\nThe application will close forcefully in less than 2 minutes.",
            parent=dummy
        )
        dummy.destroy()

    def show_killed_popup(self, app_name):
        dummy = ctk.CTkToplevel(self)
        dummy.attributes("-alpha", 0.0)
        dummy.attributes("-topmost", True)
        messagebox.showinfo(
            "🛑 App Blocked",
            f"APP CLOSED\n\n{app_name.title()} has been locked for the rest of the day.\nTry again tomorrow.",
            parent=dummy
        )
        dummy.destroy()

    def start_ui_updater(self):
        self.refresh_progress_bars()
        self.after(5000, self.start_ui_updater) 

    def refresh_progress_bars(self):
        if not self.winfo_exists() or self.state() != "normal":
            return
            
        if self.tabs.get() == "App Limits":
            with sqlite3.connect("wellbeing.db") as conn:
                limits = conn.execute("SELECT app_name, used_seconds FROM wellbeing_apps WHERE user_id=?", (self.user_id,)).fetchall()
            for app_name, used_seconds in limits:
                if app_name in getattr(self, 'app_widgets', {}):
                    widgets = self.app_widgets[app_name]
                    limit_minutes = widgets["limit"]
                    mins_used = used_seconds // 60
                    fraction = min(1.0, used_seconds / (limit_minutes * 60))
                    if fraction < 0.5:
                        p_color = "#22c55e" 
                    elif fraction < 0.85:
                        p_color = "#eab308" 
                    else:
                        p_color = "#ef4444" 
                    widgets["pb"].set(fraction)
                    widgets["pb"].configure(progress_color=p_color)
                    widgets["time_lbl"].configure(text=f"{mins_used}/{limit_minutes}m")

    def build_app_limits_tab(self):
        tab = self.tabs.tab("App Limits")
        ctk.CTkLabel(tab, text="Limit Distracting Apps", font=("Arial", 20, "bold")).pack(pady=10)
        input_frame = ctk.CTkFrame(tab, fg_color="transparent")
        input_frame.pack(pady=10)
        self.app_var = ctk.StringVar()
        self.app_dropdown = ctk.CTkOptionMenu(input_frame, variable=self.app_var, values=["Loading..."], width=200)
        self.app_dropdown.grid(row=0, column=0, padx=5)
        self.refresh_btn = ctk.CTkButton(input_frame, text="Refresh Apps", width=100, command=self.trigger_refresh)
        self.refresh_btn.grid(row=0, column=1, padx=5)
        self.limit_entry = ctk.CTkEntry(input_frame, placeholder_text="Mins", width=60)
        self.limit_entry.grid(row=0, column=2, padx=5)
        ctk.CTkButton(input_frame, text="Add", width=60, command=self.add_app_limit).grid(row=0, column=3, padx=5)
        self.limits_frame = ctk.CTkScrollableFrame(tab)
        self.limits_frame.pack(fill="both", expand=True, pady=10)
        self.trigger_refresh()
        self.load_limits()

    def trigger_refresh(self):
        self.refresh_btn.configure(state="disabled", text="Scanning...")
        self.app_var.set("Scanning...")
        self.update_idletasks()
        self.after(50, self._perform_refresh)

    def _perform_refresh(self):
        apps = get_user_running_apps()
        if apps:
            self.app_dropdown.configure(values=apps)
            self.app_var.set(apps[0])
        else:
            self.app_dropdown.configure(values=["No apps found"])
            self.app_var.set("No apps found")
        self.refresh_btn.configure(state="normal", text="Refresh Apps")

    def add_app_limit(self):
        app_name = self.app_var.get()
        limit_str = self.limit_entry.get()
        if app_name in ["No apps found", "Scanning..."] or not limit_str.isdigit():
            return
        limit = int(limit_str)
        today = datetime.date.today().isoformat()
        with sqlite3.connect("wellbeing.db") as conn:
            conn.execute("""
                INSERT OR REPLACE INTO wellbeing_apps (user_id, app_name, limit_minutes, used_seconds, last_reset_date)
                VALUES (?, ?, ?, COALESCE((SELECT used_seconds FROM wellbeing_apps WHERE user_id=? AND app_name=?), 0), ?)
            """, (self.user_id, app_name, limit, self.user_id, app_name, today))
        self.limit_entry.delete(0, 'end')
        self.load_limits()

    def load_limits(self):
        for w in self.limits_frame.winfo_children():
            w.destroy()
        self.app_widgets = {}
        with sqlite3.connect("wellbeing.db") as conn:
            limits = conn.execute("SELECT app_name, limit_minutes, used_seconds FROM wellbeing_apps WHERE user_id=?", (self.user_id,)).fetchall()
        for app_name, limit_minutes, used_seconds in limits:
            row = ctk.CTkFrame(self.limits_frame)
            row.pack(fill="x", pady=5)
            mins_used = used_seconds // 60
            fraction = min(1.0, used_seconds / (limit_minutes * 60))
            if fraction < 0.5:
                p_color = "#22c55e" 
            elif fraction < 0.85:
                p_color = "#eab308" 
            else:
                p_color = "#ef4444" 
                
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            ctk.CTkLabel(info_frame, text=app_name, font=("Arial", 16, "bold")).pack(anchor="w")
            pb_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            pb_frame.pack(fill="x", pady=(5, 0))
            pb = ctk.CTkProgressBar(pb_frame, progress_color=p_color, height=12)
            pb.pack(side="left", fill="x", expand=True, padx=(0, 10))
            pb.set(fraction)
            time_lbl = ctk.CTkLabel(pb_frame, text=f"{mins_used}/{limit_minutes}m", text_color="gray", font=("Arial", 12))
            time_lbl.pack(side="right")
            ctk.CTkButton(row, text="X", width=30, height=40, fg_color="#ef4444", hover_color="#b91c1c", command=lambda a=app_name: self.remove_limit(a)).pack(side="right", padx=(5, 10))
            ctk.CTkButton(row, text="↺ Reset", width=60, height=40, fg_color="#f59e0b", hover_color="#d97706", command=lambda a=app_name: self.reset_timer(a)).pack(side="right", padx=5)
            self.app_widgets[app_name] = {
                "pb": pb,
                "time_lbl": time_lbl,
                "limit": limit_minutes
            }

    def reset_timer(self, app_name):
        with sqlite3.connect("wellbeing.db") as conn:
            conn.execute("UPDATE wellbeing_apps SET used_seconds=0 WHERE user_id=? AND app_name=?", (self.user_id, app_name))
            conn.execute("UPDATE app_usage_history SET used_seconds=0 WHERE user_id=? AND app_name=? AND date=?", (self.user_id, app_name, datetime.date.today().isoformat()))
        self.load_limits()
        if self.timeframe_seg.get() == "Today":
            self.load_stats("Today")

    def remove_limit(self, app_name):
        with sqlite3.connect("wellbeing.db") as conn:
            conn.execute("DELETE FROM wellbeing_apps WHERE user_id=? AND app_name=?", (self.user_id, app_name))
        self.load_limits()

    def build_usage_stats_tab(self):
        tab = self.tabs.tab("Usage Stats")
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header, text="App Usage Analytics", font=("Arial", 20, "bold")).pack(side="left", padx=10)
        self.timeframe_seg = ctk.CTkSegmentedButton(header, values=["Today", "Last 7 Days", "Last 30 Days"], command=self.load_stats)
        self.timeframe_seg.pack(side="right", padx=10)
        self.timeframe_seg.set("Today")        
        self.stats_container = ctk.CTkFrame(tab, fg_color="transparent")
        self.stats_container.pack(fill="both", expand=True)
        self.apps_list_frame = ctk.CTkScrollableFrame(self.stats_container, width=220)
        self.apps_list_frame.pack(side="left", fill="y", padx=(0, 10))
        self.app_detail_frame = ctk.CTkFrame(self.stats_container, fg_color="#1e293b", corner_radius=15)
        self.app_detail_frame.pack(side="right", fill="both", expand=True)
        self.load_stats("Today")

    def load_stats(self, timeframe):
        for w in self.apps_list_frame.winfo_children():
            w.destroy()
        for w in self.app_detail_frame.winfo_children():
            w.destroy()
        today = datetime.date.today()
        if timeframe == "Today":
            start_date = today
        elif timeframe == "Last 7 Days":
            start_date = today - datetime.timedelta(days=7)
        else:
            start_date = today - datetime.timedelta(days=30)
        with sqlite3.connect("wellbeing.db") as conn:
            rows = conn.execute("""
                SELECT app_name, SUM(used_seconds) FROM app_usage_history 
                WHERE user_id=? AND date >= ?
                GROUP BY app_name
                ORDER BY SUM(used_seconds) DESC
            """, (self.user_id, start_date.isoformat())).fetchall()            
        if not rows:
            ctk.CTkLabel(self.app_detail_frame, text="No usage data available.", font=("Arial", 16), text_color="gray").place(relx=0.5, rely=0.5, anchor="center")
            return            
        first_app = rows[0][0]        
        for app_name, total_sec in rows:
            mins = total_sec // 60
            hrs = mins // 60
            rem_mins = mins % 60
            time_str = f"{hrs}h {rem_mins}m" if hrs > 0 else f"{mins}m"            
            btn = ctk.CTkButton(
                self.apps_list_frame, 
                text=f"{app_name}\n{time_str}", 
                font=("Arial", 14),
                fg_color="#334155",
                hover_color="#475569",
                height=60,
                corner_radius=10,
                command=lambda a=app_name, t=timeframe, sd=start_date: self.show_app_details(a, t, sd)
            )
            btn.pack(fill="x", pady=5, padx=5)            
        self.show_app_details(first_app, timeframe, start_date)

    def show_app_details(self, app_name, timeframe, start_date):
        for w in self.app_detail_frame.winfo_children():
            w.destroy()            
        header = ctk.CTkFrame(self.app_detail_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)        
        with sqlite3.connect("wellbeing.db") as conn:
            total = conn.execute("SELECT SUM(used_seconds) FROM app_usage_history WHERE user_id=? AND app_name=? AND date >= ?", (self.user_id, app_name, start_date.isoformat())).fetchone()[0] or 0        
        mins = total // 60
        hrs = mins // 60
        rem_mins = mins % 60
        total_str = f"{hrs}h {rem_mins}m" if hrs > 0 else f"{mins}m"        
        ctk.CTkLabel(header, text=app_name, font=("Arial", 28, "bold"), text_color="white").pack(side="left")
        ctk.CTkLabel(header, text=f"Total: {total_str}", font=("Arial", 20, "bold"), text_color="#3b82f6").pack(side="right")        
        self.draw_app_chart(app_name, timeframe, start_date)

    def draw_app_chart(self, app_name, timeframe, start_date):
        try:
            plt, FigureCanvasTkAgg = _import_matplotlib()
        except ImportError:
            ctk.CTkLabel(self.app_detail_frame, text="Chart unavailable - Matplotlib not installed", text_color="gray").pack(pady=50)
            return
            
        dates = []
        usage_mins = []
        today = datetime.date.today()
        days_to_plot = 1 if timeframe == "Today" else (7 if timeframe == "Last 7 Days" else 30)
        with sqlite3.connect("wellbeing.db") as conn:
            for i in range(days_to_plot):
                current_date = start_date + datetime.timedelta(days=i)
                if current_date > today:
                    break
                    
                row = conn.execute("SELECT used_seconds FROM app_usage_history WHERE user_id=? AND app_name=? AND date=?", (self.user_id, app_name, current_date.isoformat())).fetchone()
                
                label = "Today" if days_to_plot == 1 else (current_date.strftime("%a") if days_to_plot == 7 else str(current_date.day))
                if days_to_plot == 30 and i % 3 != 0:
                    label = ""
                    
                dates.append(label)
                usage_mins.append((row[0] // 60) if row else 0)
        fig = plt.Figure(figsize=(5, 4), dpi=100, facecolor="#1e293b")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#1e293b")
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.tick_params(axis="x", colors="white", labelsize=9)
        ax.tick_params(axis="y", colors="white", labelsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.bar(range(len(usage_mins)), usage_mins, color="#3b82f6", width=0.6)
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates)
        ax.set_ylabel("Minutes", color="white")
        canvas = FigureCanvasTkAgg(fig, master=self.app_detail_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def build_physical_health_tab(self):
        tab = self.tabs.tab("Physical Health")
        self.time_lbl = ctk.CTkLabel(tab, text="00:00:00", font=("Arial", 40, "bold"))
        self.time_lbl.pack(pady=20)
        settings_frame = ctk.CTkFrame(tab)
        settings_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(settings_frame, text="Water Interval (mins):").grid(row=0, column=0, padx=10, pady=10)
        self.water_entry = ctk.CTkEntry(settings_frame, width=60)
        self.water_entry.insert(0, "60")
        self.water_entry.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkLabel(settings_frame, text="Exercise Interval (mins):").grid(row=1, column=0, padx=10, pady=10)
        self.exercise_entry = ctk.CTkEntry(settings_frame, width=60)
        self.exercise_entry.insert(0, "120")
        self.exercise_entry.grid(row=1, column=1, padx=10, pady=10)
        ctk.CTkButton(tab, text="Apply & Restart Timer", command=self.start_tracking).pack(pady=20)

    def hide_window(self):
        self.withdraw()

    def show_window(self):
        self.deiconify()
        self.lift()
        self.load_limits()
        self.load_stats(self.timeframe_seg.get())

    def start_tracking(self):
        try:
            self.water_sec = int(self.water_entry.get()) * 60
            self.exercise_sec = int(self.exercise_entry.get()) * 60
        except ValueError:
            return
        self.time_elapsed = 0
        if not self.running:
            self.running = True
            self.update_timer()

    def update_timer(self):
        if not self.running:
            return
        self.time_elapsed += 1
        hours, remainder = divmod(self.time_elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.time_lbl.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        if self.water_sec > 0 and self.time_elapsed % self.water_sec == 0:
            self.show_water_popup()
        if self.exercise_sec > 0 and self.time_elapsed % self.exercise_sec == 0:
            self.show_exercise_popup()
        self.after(1000, self.update_timer)

    def show_water_popup(self):
        win = ctk.CTkToplevel(self)
        win.title("Water Reminder")
        win.geometry("350x400")
        win.attributes("-topmost", True)
        ctk.CTkLabel(win, text="Time to drink water! 💧", font=("Arial", 20, "bold")).pack(pady=20)
        water_gif_path = os.path.join(ASSETS_DIR, "water.gif")
        if os.path.exists(water_gif_path):
            AnimatedGifLabel(win, water_gif_path, size=(200, 200)).pack(pady=10)
        ctk.CTkButton(win, text="Hydrated", command=win.destroy).pack(pady=20)
        
    def show_exercise_popup(self):
        win = ctk.CTkToplevel(self)
        win.title("Exercise Break")
        win.geometry("450x650")
        win.attributes("-topmost", True)
        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(scroll, text="Time for a Quick Stretch!", font=("Arial", 20, "bold")).pack(pady=10)
        eye_gif_path = os.path.join(ASSETS_DIR, "eye.gif")
        if os.path.exists(eye_gif_path):
            AnimatedGifLabel(scroll, eye_gif_path, size=(150, 150)).pack(pady=10)
        ctk.CTkLabel(scroll, text="Gently blink your eyes 20 times.", font=("Arial", 14)).pack(pady=5)
        neck_gif_path = os.path.join(ASSETS_DIR, "neck.gif")
        if os.path.exists(neck_gif_path):
            AnimatedGifLabel(scroll, neck_gif_path, size=(150, 150)).pack(pady=10)
        ctk.CTkLabel(scroll, text="Gently roll your neck left and right.", font=("Arial", 14)).pack(pady=5)
        spine_gif_path = os.path.join(ASSETS_DIR, "spine.gif")
        if os.path.exists(spine_gif_path):
            AnimatedGifLabel(scroll, spine_gif_path, size=(150, 150)).pack(pady=10)
        ctk.CTkLabel(scroll, text="Sit straight and stretch your spine.", font=("Arial", 14)).pack(pady=5)
        ctk.CTkButton(scroll, text="Finished", command=win.destroy).pack(pady=20)