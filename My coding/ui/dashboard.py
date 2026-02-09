import customtkinter as ctk
from PIL import Image
import datetime
import os
import random
from tkinter import messagebox
from backend.profile_db import get_profile, save_profile
from ui.ai_chat import AIChat
from ui.focus_timer import FocusTimerApp
from ui.calc import CalculatorApp
from ui.insights_ui import InsightsApp

class DashboardApp(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.geometry("1280x720")
        self.title("A Day Companion - Dashboard")
        self.resizable(False, False)
        self.configure(fg_color="#0f172a") 

        self.user_id = int(user_id)
        
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

    def show_profile_form(self):
        for w in self.winfo_children(): w.destroy()

        card = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=20, border_color="#334155", border_width=2)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            card, 
            text="A Day Companion Welcomes You!", 
            font=("Helvetica", 24, "bold"), 
            text_color="white"
        ).pack(pady=(30, 10), padx=50)

        ctk.CTkLabel(
            card, 
            text="Let's personalize your experience.", 
            font=("Helvetica", 14), 
            text_color="#94a3b8"
        ).pack(pady=(0, 20))

        self.name_entry = self.create_input(card, "Full Name (e.g. Devansh)")
        self.class_entry = self.create_input(card, "Class/Grade (e.g. B.Tech 2nd Year)")
        self.hobbies_entry = self.create_input(card, "Hobbies (e.g. Coding, Guitar)")
        self.goals_entry = self.create_input(card, "Top Goals (e.g. 9 CGPA, Learn AI)")

        ctk.CTkButton(
            card, 
            text="Save Profile", 
            width=200, 
            height=45,
            font=("Helvetica", 15, "bold"),
            fg_color="#3b82f6", 
            hover_color="#2563eb",
            command=self.save_profile_data
        ).pack(pady=30)

    def create_input(self, parent, placeholder):
        entry = ctk.CTkEntry(
            parent, 
            width=350, 
            height=45, 
            placeholder_text=placeholder,
            font=("Helvetica", 14)
        )
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
        for w in self.winfo_children():
            w.destroy()

        self.user_name = profile[0]

        name_font_size = 50

        if len(self.user_name) > 15:
            name_font_size = 32

        if len(self.user_name) > 25:
            name_font_size = 26

        self.grid_columnconfigure(0, weight=35)
        self.grid_columnconfigure(1, weight=65)
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        
        ctk.CTkLabel(
            self.left_frame, 
            text=f"Hello,\n{self.user_name}", 
            font=("Helvetica", name_font_size, "bold"),
            text_color="white",
            justify="left",
            anchor="w",
            wraplength=400
        ).pack(fill="x", pady=(20, 10))

        ctk.CTkFrame(self.left_frame, height=2, fg_color="#334155").pack(fill="x", pady=20)

        self.time_label = ctk.CTkLabel(
            self.left_frame, 
            text="00:00", 
            font=("Helvetica", 110, "bold"), 
            text_color="#38bdf8"
        )
        self.time_label.pack(anchor="w")

        self.date_label = ctk.CTkLabel(
            self.left_frame, 
            text="Monday, 1st Jan", 
            font=("Purisa", 28, "italic"), 
            text_color="#94a3b8"
        )
        self.date_label.pack(anchor="w", pady=(0, 40))

        random_quote = random.choice(self.quotes)
        ctk.CTkLabel(
            self.left_frame,
            text=random_quote,
            font=("Helvetica", 18, "italic"),
            text_color="#64748b",
            justify="left",
            wraplength=350,
            anchor="w"
        ).pack(side="bottom", fill="x", pady=20)

        self.right_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=30)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(1, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)

        self.load_assets()

        self.create_big_button(0, 0, self.ai_img, "AI Companion", lambda: AIChat(self.user_id))
        self.create_big_button(0, 1, self.calc_img, "Calculator", CalculatorApp)
        self.create_big_button(1, 0, self.clock_img, "Focus Timer", FocusTimerApp)
        self.create_big_button(1, 1, self.insights_img, "My Insights", lambda: InsightsApp(self.user_id))

        self.update_clock()

    def create_big_button(self, r, c, img, text, cmd):
        btn = ctk.CTkButton(
            self.right_frame,
            text=text,
            image=img,
            compound="top",
            font=("Helvetica", 24, "bold"),
            fg_color="#0f172a",
            hover_color="#334155",
            corner_radius=25,
            width=280,
            height=280,
            command=cmd
        )
        btn.grid(row=r, column=c, padx=20, pady=20)

    def load_assets(self):
        icon_size = (180, 180)
        def load(name):
            try:
                path = os.path.join("assets", name)
                return ctk.CTkImage(Image.open(path), size=icon_size)
            except:
                return None

        self.ai_img = load("Ai.png")
        self.calc_img = load("calc.png")
        self.clock_img = load("focus_timer.png")
        self.insights_img = load("insights.png")

    def update_clock(self):
        now = datetime.datetime.now()
        self.time_label.configure(text=now.strftime("%H:%M"))
        self.date_label.configure(text=now.strftime("%A, %d %B"))
        self.after(1000, self.update_clock)