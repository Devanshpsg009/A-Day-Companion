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
        self.geometry("1000x750")
        self.title("Analytics Command Center")
        self.resizable(False, False)
        
        self.db_path = "todo.db"
        self.ensure_db_schema()

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Tabs
        self.grid_rowconfigure(2, weight=0) # Dev Toggle

        # 1. Header
        self.header = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#1e293b")
        self.header.grid(row=0, column=0, sticky="ew")
        
        ctk.CTkLabel(
            self.header, 
            text="Productivity Insights", 
            font=("Helvetica", 24, "bold"), 
            text_color="white"
        ).pack(pady=15)

        # 2. Tabs (Daily, Weekly, Monthly)
        self.tabs = ctk.CTkTabview(self, fg_color="#0f172a", segmented_button_selected_color="#3b82f6")
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        self.tabs.add("Daily")
        self.tabs.add("Weekly")
        self.tabs.add("Monthly")

        # 3. Build Views
        self.build_daily_tab()
        self.build_weekly_tab()
        self.build_monthly_tab()

        # 4. Dev Mode Toggle (Bottom Bar)
        self.dev_frame = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="#020617")
        self.dev_frame.grid(row=2, column=0, sticky="ew")

        self.dev_var = ctk.BooleanVar(value=False)
        # FIX: Changed 'on_color' to 'progress_color'
        self.dev_switch = ctk.CTkSwitch(
            self.dev_frame, 
            text="Developer Mode", 
            command=self.toggle_dev_tools,
            variable=self.dev_var,
            progress_color="#22c55e" 
        )
        self.dev_switch.pack(side="left", padx=20, pady=10)

        # Hidden Dev Tools (Initially hidden)
        self.dev_tools = ctk.CTkFrame(self.dev_frame, fg_color="transparent")
        
        # Tool 1: Bulk Inject
        ctk.CTkButton(
            self.dev_tools, 
            text="Inject Random History", 
            fg_color="#ef4444", 
            hover_color="#b91c1c",
            width=150,
            command=self.inject_fake_data
        ).pack(side="left", padx=10)
        
        # Tool 2: Specific Time Travel
        ctk.CTkLabel(self.dev_tools, text="|  Add Task for:", text_color="gray").pack(side="left", padx=5)
        
        self.days_ago_entry = ctk.CTkEntry(self.dev_tools, width=50, placeholder_text="5")
        self.days_ago_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(self.dev_tools, text="days ago", text_color="gray").pack(side="left")
        
        ctk.CTkButton(
            self.dev_tools,
            text="Add Done Task",
            fg_color="#3b82f6",
            width=100,
            command=self.add_backdated_task
        ).pack(side="left", padx=10)

    def toggle_dev_tools(self):
        if self.dev_var.get():
            self.dev_tools.pack(side="left", padx=10)
        else:
            self.dev_tools.pack_forget()

    # --- DATABASE INTELLIGENCE ---
    def ensure_db_schema(self):
        """Auto-heals the database to support dates"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("PRAGMA table_info(todos)")
        cols = [info[1] for info in cur.fetchall()]
        
        if 'date' not in cols:
            cur.execute("ALTER TABLE todos ADD COLUMN date TEXT")
            today = datetime.date.today().isoformat()
            cur.execute("UPDATE todos SET date = ? WHERE date IS NULL", (today,))
            conn.commit()
            
        conn.close()

    def inject_fake_data(self):
        """Generates random history for the past 30 days"""
        conn = sqlite3.connect(self.db_path)
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
        self.refresh_views()

    def add_backdated_task(self):
        """Adds a completed task for a specific number of days ago"""
        try:
            days = int(self.days_ago_entry.get())
            target_date = datetime.date.today() - timedelta(days=days)
            date_str = target_date.isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO todos (user_id, task, date, status, notified) VALUES (?, ?, ?, 1, 1)",
                (self.user_id, f"Manual Task ({days} days ago)", date_str)
            )
            conn.commit()
            conn.close()
            self.refresh_views()
        except ValueError:
            pass

    def refresh_views(self):
        self.build_daily_tab()
        self.build_weekly_tab()
        self.build_monthly_tab()

    # --- TAB 1: DAILY (Pie Chart) ---
    def build_daily_tab(self):
        tab = self.tabs.tab("Daily")
        for w in tab.winfo_children(): w.destroy()
        
        today = datetime.date.today().isoformat()
        total, done = self.get_stats_for_range(today, today)
        
        # Stats Cards
        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(fill="x", pady=10)
        
        self.create_kpi(frame, "Today's Tasks", total, "#3b82f6", "left")
        self.create_kpi(frame, "Completed", done, "#22c55e", "right")

        self.embed_chart(tab, "pie", [done, total-done], ["Done", "Pending"], ["#22c55e", "#ef4444"])

    # --- TAB 2: WEEKLY (Bar Chart) ---
    def build_weekly_tab(self):
        tab = self.tabs.tab("Weekly")
        for w in tab.winfo_children(): w.destroy()
        
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=6)
        
        days = []
        counts = []
        current = start_date
        while current <= end_date:
            d_str = current.isoformat()
            _, done = self.get_stats_for_range(d_str, d_str)
            days.append(current.strftime("%a")) # Mon, Tue...
            counts.append(done)
            current += timedelta(days=1)
            
        total_week = sum(counts)
        ctk.CTkLabel(tab, text=f"Total Completed This Week: {total_week}", font=("Arial", 18, "bold")).pack(pady=10)
        
        self.embed_chart(tab, "bar", counts, days, "#3b82f6")

    # --- TAB 3: MONTHLY (Line Chart) ---
    def build_monthly_tab(self):
        tab = self.tabs.tab("Monthly")
        for w in tab.winfo_children(): w.destroy()
        
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=29)
        
        dates = []
        counts = []
        current = start_date
        while current <= end_date:
            d_str = current.isoformat()
            _, done = self.get_stats_for_range(d_str, d_str)
            dates.append(str(current.day)) # 1, 2, 3...
            counts.append(done)
            current += timedelta(days=1)

        total_month = sum(counts)
        ctk.CTkLabel(tab, text=f"Total Completed This Month: {total_month}", font=("Arial", 18, "bold")).pack(pady=10)
        
        self.embed_chart(tab, "line", counts, dates, "#8b5cf6")

    # --- HELPERS ---
    def get_stats_for_range(self, start_str, end_str):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Use date(date) to ensure we are comparing just the date part if format is mixed
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
        conn.close()
        return total, done

    def create_kpi(self, parent, title, value, color, side):
        card = ctk.CTkFrame(parent, fg_color="#1e293b", width=200)
        card.pack(side=side, padx=20, expand=True, fill="both")
        ctk.CTkLabel(card, text=title, text_color="gray").pack(pady=(10,0))
        ctk.CTkLabel(card, text=str(value), font=("Arial", 30, "bold"), text_color=color).pack(pady=(0,10))

    def embed_chart(self, parent, type, data, labels, colors):
        fig = plt.Figure(figsize=(6, 4), dpi=100, facecolor="#0f172a")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#0f172a")
        
        # Style
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if type == "pie":
            if sum(data) == 0: data = [0, 1] 
            ax.pie(data, labels=labels, colors=colors, autopct='%1.1f%%', textprops={'color':"white"})
            
        elif type == "bar":
            ax.bar(labels, data, color=colors)
            
        elif type == "line":
            ax.plot(labels, data, color=colors, marker='o')
            ax.grid(color='#334155', linestyle='--', linewidth=0.5)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)