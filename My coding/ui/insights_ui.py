import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from backend.insights import (
    has_started,
    start_insights,
    get_streak,
    get_weekly_data,
    get_monthly_data,
    set_debug_date
)
import datetime

class InsightsApp(ctk.CTkToplevel):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

        self.geometry("1000x750")
        self.title("Productivity Insights")
        self.configure(fg_color="#020617")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.current_view = "Weekly"

        if has_started(self.user_id):
            self.show_dashboard()
        else:
            self.show_intro()

        self.build_dev_tools()

    def show_intro(self):
        self.clear_container()

        ctk.CTkLabel(
            self.container,
            text="🚀 Unlock Your Potential",
            font=("Helvetica", 32, "bold"),
            text_color="white"
        ).pack(pady=(40, 20))

        benefits = (
            "Why turn on Insights?\n\n"
            "✅ Track your daily consistency\n"
            "✅ Visualize your focus trends\n"
            "✅ Build disciplined habits\n\n"
            "We analyze your activity securely to help you grow."
        )

        ctk.CTkLabel(
            self.container,
            text=benefits,
            font=("Helvetica", 18),
            text_color="#94a3b8",
            justify="left"
        ).pack(pady=20)

        ctk.CTkButton(
            self.container,
            text="Start Tracking Now",
            font=("Helvetica", 16, "bold"),
            height=50,
            width=220,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=self.handle_start
        ).pack(pady=40)

    def handle_start(self):
        start_insights(self.user_id)
        self.show_dashboard()

    def show_dashboard(self):
        self.clear_container()

        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header, text="Activity Analysis", font=("Helvetica", 24, "bold"), text_color="white"
        ).pack(side="left")

        streak = get_streak(self.user_id)
        streak_color = "#ef4444" if streak > 0 else "#64748b"
        
        ctk.CTkLabel(
            header, 
            text=f"🔥 Streak: {streak} Day(s)", 
            font=("Helvetica", 20, "bold"), 
            text_color=streak_color
        ).pack(side="right")

        self.view_selector = ctk.CTkSegmentedButton(
            self.container,
            values=["Weekly", "Monthly"],
            command=self.change_view_mode,
            width=200
        )
        self.view_selector.set(self.current_view)
        self.view_selector.pack(pady=10)

        self.graph_frame = ctk.CTkFrame(self.container, fg_color="#0f172a", corner_radius=15)
        self.graph_frame.pack(fill="both", expand=True)
        self.graph_frame.update()

        self.plot_graph()

    def change_view_mode(self, value):
        self.current_view = value
        self.plot_graph()

    def plot_graph(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        if self.current_view == "Weekly":
            data = get_weekly_data(self.user_id)
            title = "Activity This Week"
        else:
            data = get_monthly_data(self.user_id)
            title = "Last 30 Days Activity"

        days = [x[0] for x in data]
        values = [x[1] for x in data]

        fig = Figure(figsize=(8, 5), dpi=100)
        fig.patch.set_facecolor('#0f172a')
        
        ax = fig.add_subplot(111)
        ax.set_facecolor('#0f172a')

        colors = ['#22c55e' if v >= 1 else '#334155' for v in values]
        
        ax.bar(days, values, color=colors, width=0.6)

        ax.set_title(title, color="white", pad=15, fontsize=14)
        
        ax.tick_params(axis='x', colors='#cbd5e1', labelsize=9, rotation=45 if self.current_view == "Monthly" else 0)
        ax.tick_params(axis='y', colors='#cbd5e1', labelsize=10)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#334155')
        ax.spines['left'].set_visible(False)
        
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["Off", "On"])
        ax.set_ylim(0, 1.2)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()

    def build_dev_tools(self):
        dev_frame = ctk.CTkFrame(self, height=50, fg_color="#1e1e1e")
        dev_frame.pack(side="bottom", fill="x")

        ctk.CTkLabel(dev_frame, text="[DEV] Time Travel:", text_color="yellow").pack(side="left", padx=15)

        self.date_entry = ctk.CTkEntry(dev_frame, width=120, placeholder_text="YYYY-MM-DD")
        self.date_entry.pack(side="left", padx=5)
        self.date_entry.insert(0, datetime.date.today().isoformat())

        ctk.CTkButton(
            dev_frame, 
            text="Jump Date", 
            width=100, 
            fg_color="#444", 
            command=self.apply_fake_date
        ).pack(side="left", padx=10)

    def apply_fake_date(self):
        date_str = self.date_entry.get()
        try:
            set_debug_date(date_str)
            
            from backend.insights import log_app_open
            log_app_open(self.user_id)
            
            if has_started(self.user_id):
                self.show_dashboard()
            else:
                self.show_intro()
                
        except ValueError:
            print("Invalid Date Format")