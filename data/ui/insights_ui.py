import customtkinter as ctk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from datetime import timedelta
import random

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class InsightsApp(ctk.CTkToplevel):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.geometry("1100x750")
        self.title("Analytics Command Center")
        self.resizable(False, False)
        
        self.todo_db = "todo.db"
        self.journal_db = "journal.db"
        self.ensure_db_schema()

        # Grid Layout: 2 Columns (Tasks vs Mood)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Tabs
        self.grid_rowconfigure(2, weight=0) # Dev Toggle

        # --- Header ---
        self.header = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#1e293b")
        self.header.grid(row=0, column=0, sticky="ew")
        
        ctk.CTkLabel(
            self.header, 
            text="Productivity & Wellness Insights", 
            font=("Helvetica", 24, "bold"), 
            text_color="white"
        ).pack(pady=15)

        # --- Tabs ---
        self.tabs = ctk.CTkTabview(self, fg_color="#0f172a", segmented_button_selected_color="#3b82f6")
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        self.tabs.add("Daily")
        self.tabs.add("Weekly")
        self.tabs.add("Monthly")

        self.build_daily_tab()
        self.build_weekly_tab()
        self.build_monthly_tab()

        # --- Dev Tools ---
        self.dev_frame = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="#020617")
        self.dev_frame.grid(row=2, column=0, sticky="ew")

        self.dev_var = ctk.BooleanVar(value=False)
        self.dev_switch = ctk.CTkSwitch(
            self.dev_frame, 
            text="Developer Mode", 
            command=self.toggle_dev_tools,
            variable=self.dev_var,
            progress_color="#22c55e" 
        )
        self.dev_switch.pack(side="left", padx=20, pady=10)

        self.dev_tools = ctk.CTkFrame(self.dev_frame, fg_color="transparent")
        
        ctk.CTkButton(
            self.dev_tools, 
            text="Inject Random Data", 
            fg_color="#ef4444", 
            hover_color="#b91c1c",
            width=150,
            command=self.inject_fake_data
        ).pack(side="left", padx=10)
        
    def toggle_dev_tools(self):
        if self.dev_var.get():
            self.dev_tools.pack(side="left", padx=10)
        else:
            self.dev_tools.pack_forget()

    def ensure_db_schema(self):
        """Auto-heals the database to support dates"""
        # 1. Todo DB
        conn = sqlite3.connect(self.todo_db)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                task TEXT,
                time TEXT,
                status INTEGER DEFAULT 0,
                notified INTEGER DEFAULT 0,
                date TEXT
            )
        """)
        # Migration check for older DBs
        cur.execute("PRAGMA table_info(todos)")
        cols = [info[1] for info in cur.fetchall()]
        if 'date' not in cols:
            try:
                cur.execute("ALTER TABLE todos ADD COLUMN date TEXT")
                today = datetime.date.today().isoformat()
                cur.execute("UPDATE todos SET date = ? WHERE date IS NULL", (today,))
            except: pass
        conn.commit()
        conn.close()

        # 2. Journal DB
        conn = sqlite3.connect(self.journal_db)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS journal (
                user_id INTEGER,
                date TEXT,
                content TEXT,
                tags TEXT,
                mood TEXT,
                score INTEGER,
                PRIMARY KEY (user_id, date)
            )
        """)
        conn.commit()
        conn.close()

    def inject_fake_data(self):
        """Generates random history for Tasks AND Mood"""
        # 1. Fake Tasks
        conn = sqlite3.connect(self.todo_db)
        cur = conn.cursor()
        tasks = ["Study AI", "Gym", "Code Python", "Read Book", "Meditation", "Project X"]
        
        for i in range(30):
            day_offset = datetime.date.today() - timedelta(days=i)
            day_str = day_offset.isoformat()
            
            for _ in range(random.randint(0, 5)):
                task = random.choice(tasks)
                status = 1 if random.random() > 0.3 else 0 
                cur.execute(
                    "INSERT INTO todos (user_id, task, date, status, notified) VALUES (?, ?, ?, ?, 1)",
                    (self.user_id, task, day_str, status)
                )
        conn.commit()
        conn.close()

        # 2. Fake Moods
        conn = sqlite3.connect(self.journal_db)
        cur = conn.cursor()
        moods = ["Happy", "Sad", "Productive", "Tired", "Anxious", "Excited"]
        
        for i in range(30):
            day_offset = datetime.date.today() - timedelta(days=i)
            day_str = day_offset.isoformat()
            
            score = random.randint(3, 9)
            mood = random.choice(moods)
            
            cur.execute("""
                INSERT OR REPLACE INTO journal (user_id, date, content, mood, score)
                VALUES (?, ?, 'Fake Entry', ?, ?)
            """, (self.user_id, day_str, mood, score))
            
        conn.commit()
        conn.close()
        
        self.refresh_views()

    def refresh_views(self):
        self.build_daily_tab()
        self.build_weekly_tab()
        self.build_monthly_tab()

    # --- DATA FETCHERS ---
    def get_task_stats(self, start_str, end_str):
        conn = sqlite3.connect(self.todo_db)
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT count(*) FROM todos WHERE user_id=? AND date(date) BETWEEN date(?) AND date(?)", 
                (self.user_id, start_str, end_str)
            )
            total = cur.fetchone()[0]
            cur.execute(
                "SELECT count(*) FROM todos WHERE user_id=? AND date(date) BETWEEN date(?) AND date(?) AND status=1", 
                (self.user_id, start_str, end_str)
            )
            done = cur.fetchone()[0]
        except:
            total, done = 0, 0
        conn.close()
        return total, done

    def get_mood_stats(self, start_date, days_count):
        conn = sqlite3.connect(self.journal_db)
        cur = conn.cursor()
        
        data = []
        labels = []
        
        current = start_date
        end_date = start_date + timedelta(days=days_count-1)
        
        while current <= end_date:
            d_str = current.isoformat()
            cur.execute("SELECT score FROM journal WHERE user_id=? AND date=?", (self.user_id, d_str))
            row = cur.fetchone()
            score = row[0] if row else 0 
            
            data.append(score)
            
            if days_count == 7:
                labels.append(current.strftime("%a"))
            else:
                # Show label for every 3rd day to avoid crowding
                labels.append(str(current.day) if current.day % 3 == 0 else "")
                
            current += timedelta(days=1)
            
        conn.close()
        return data, labels

    # --- UI BUILDERS ---
    def split_frame(self, tab):
        for w in tab.winfo_children(): w.destroy()
        left = ctk.CTkFrame(tab, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkFrame(tab, width=2, fg_color="#334155").pack(side="left", fill="y", pady=20)
        right = ctk.CTkFrame(tab, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        return left, right

    def build_daily_tab(self):
        left, right = self.split_frame(self.tabs.tab("Daily"))
        
        ctk.CTkLabel(left, text="Today's Productivity", font=("Arial", 16, "bold"), text_color="#3b82f6").pack(pady=10)
        today = datetime.date.today().isoformat()
        total, done = self.get_task_stats(today, today)
        
        kpi_frame = ctk.CTkFrame(left, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=10)
        self.create_kpi(kpi_frame, "Total", total, "#94a3b8", "left")
        self.create_kpi(kpi_frame, "Done", done, "#22c55e", "right")

        self.embed_chart(left, "pie", [done, total-done], ["Done", "Pending"], ["#22c55e", "#ef4444"])

        ctk.CTkLabel(right, text="Today's Mood", font=("Arial", 16, "bold"), text_color="#a855f7").pack(pady=10)
        
        conn = sqlite3.connect(self.journal_db)
        cur = conn.cursor()
        cur.execute("SELECT mood, score FROM journal WHERE user_id=? AND date=?", (self.user_id, today))
        row = cur.fetchone()
        conn.close()
        
        mood_text = row[0] if row else "No Data"
        score_val = row[1] if row else 0
        
        canvas = ctk.CTkCanvas(right, width=200, height=200, bg="#0f172a", highlightthickness=0)
        canvas.pack(pady=30)
        color = "#a855f7" if score_val > 0 else "#334155"
        canvas.create_oval(20, 20, 180, 180, outline=color, width=8)
        canvas.create_text(100, 80, text=str(score_val), fill="white", font=("Arial", 60, "bold"))
        canvas.create_text(100, 130, text="/ 10", fill="gray", font=("Arial", 20))
        ctk.CTkLabel(right, text=mood_text, font=("Helvetica", 24, "bold"), text_color="white").pack(pady=10)

    def build_weekly_tab(self):
        left, right = self.split_frame(self.tabs.tab("Weekly"))
        
        ctk.CTkLabel(left, text="Task Completion (Last 7 Days)", font=("Arial", 14, "bold"), text_color="gray").pack()
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=6)
        
        days = []
        counts = []
        current = start_date
        while current <= end_date:
            d_str = current.isoformat()
            _, done = self.get_task_stats(d_str, d_str)
            days.append(current.strftime("%a"))
            counts.append(done)
            current += timedelta(days=1)
            
        self.embed_chart(left, "bar", counts, days, "#3b82f6")

        ctk.CTkLabel(right, text="Mood Trend (Last 7 Days)", font=("Arial", 14, "bold"), text_color="gray").pack()
        scores, labels = self.get_mood_stats(start_date, 7)
        self.embed_chart(right, "line", scores, labels, "#a855f7")

    def build_monthly_tab(self):
        left, right = self.split_frame(self.tabs.tab("Monthly"))

        ctk.CTkLabel(left, text="Productivity Month View", font=("Arial", 14, "bold"), text_color="gray").pack()
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=29)
        
        dates = []
        counts = []
        current = start_date
        while current <= end_date:
            d_str = current.isoformat()
            _, done = self.get_task_stats(d_str, d_str)
            dates.append(str(current.day) if current.day % 3 == 0 else "")
            counts.append(done)
            current += timedelta(days=1)

        self.embed_chart(left, "line", counts, dates, "#3b82f6")

        ctk.CTkLabel(right, text="Mental Health Trend (30 Days)", font=("Arial", 14, "bold"), text_color="gray").pack()
        scores, labels = self.get_mood_stats(start_date, 30)
        self.embed_chart(right, "line", scores, labels, "#a855f7")

    def create_kpi(self, parent, title, value, color, side):
        card = ctk.CTkFrame(parent, fg_color="#1e293b", width=120)
        card.pack(side=side, padx=10, expand=True, fill="both")
        ctk.CTkLabel(card, text=title, text_color="gray").pack(pady=(5,0))
        ctk.CTkLabel(card, text=str(value), font=("Arial", 24, "bold"), text_color=color).pack(pady=(0,5))

    def embed_chart(self, parent, type, data, labels, color):
        fig = plt.Figure(figsize=(4, 3), dpi=100, facecolor="#0f172a")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#0f172a")
        
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.tick_params(axis='x', colors='white', labelsize=8)
        ax.tick_params(axis='y', colors='white', labelsize=8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if type == "pie":
            if sum(data) == 0: data = [0, 1]; color = ["#22c55e", "#334155"]
            ax.pie(data, labels=labels, colors=color, autopct='%1.1f%%', textprops={'color':"white"})
            
        elif type == "bar":
            ax.bar(labels, data, color=color)
            
        elif type == "line":
            # BUG FIX: Use indices [0, 1, 2...] for X-axis to force linearity
            x_indices = range(len(data))
            ax.plot(x_indices, data, color=color, marker='o', linewidth=2)
            
            # Map labels to the indices
            ax.set_xticks(x_indices)
            ax.set_xticklabels(labels)
            
            ax.grid(color='#334155', linestyle='--', linewidth=0.5)
            if color == "#a855f7": 
                ax.set_ylim(0, 10)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)