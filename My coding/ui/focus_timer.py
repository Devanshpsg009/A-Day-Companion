import customtkinter as ctk
import datetime
import os
from tkinter import messagebox
import pygame

class FocusTimerApp(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        
        # Initialize mixer immediately with safe defaults
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Sound Error: {e}")

        self.geometry("500x500")
        self.title("Focus Timer")
        self.resizable(False, False)

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(expand=True, fill="both", padx=20, pady=20)

        self.tabs.add("Stopwatch")
        self.tabs.add("Timer")
        self.tabs.add("Alarm")

        self.build_stopwatch()
        self.build_timer()
        self.build_alarm()
    
    def build_stopwatch(self):
        tab = self.tabs.tab("Stopwatch")
        self.sw_seconds = 0
        self.sw_running = False

        self.sw_label = ctk.CTkLabel(tab, text="00:00:00", font=("Arial", 50, "bold"))
        self.sw_label.pack(pady=40)

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack()
        
        ctk.CTkButton(btn_frame, text="Start", width=80, command=self.sw_start).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Pause", width=80, command=self.sw_pause).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Reset", width=80, fg_color="#C0392B", hover_color="#A93226", command=self.sw_reset).pack(side="left", padx=5)

    def sw_start(self):
        if not self.sw_running:
            self.sw_running = True
            self.update_sw()

    def sw_pause(self):
        self.sw_running = False

    def sw_reset(self):
        self.sw_running = False
        self.sw_seconds = 0
        self.sw_label.configure(text="00:00:00")

    def update_sw(self):
        if self.sw_running:
            self.sw_seconds += 1
            h = self.sw_seconds // 3600
            m = (self.sw_seconds % 3600) // 60
            s = self.sw_seconds % 60
            self.sw_label.configure(text=f"{h:02}:{m:02}:{s:02}")
            self.after(1000, self.update_sw)
    
    def build_timer(self):
        tab = self.tabs.tab("Timer")
        self.timer_running = False
        self.timer_total = 0
        input_frame = ctk.CTkFrame(tab, fg_color="transparent")
        input_frame.pack(pady=20)

        self.t_hr = ctk.CTkEntry(input_frame, width=50, placeholder_text="00", justify="center")
        self.t_min = ctk.CTkEntry(input_frame, width=50, placeholder_text="00", justify="center")
        self.t_sec = ctk.CTkEntry(input_frame, width=50, placeholder_text="00", justify="center")

        self.t_hr.pack(side="left", padx=5)
        ctk.CTkLabel(input_frame, text=":").pack(side="left")
        self.t_min.pack(side="left", padx=5)
        ctk.CTkLabel(input_frame, text=":").pack(side="left")
        self.t_sec.pack(side="left", padx=5)

        self.timer_label = ctk.CTkLabel(tab, text="00:00:00", font=("Arial", 50, "bold"))
        self.timer_label.pack(pady=20)

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack()
        
        ctk.CTkButton(btn_frame, text="Start", width=80, command=self.timer_start).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Stop", width=80, command=self.timer_pause).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Reset", width=80, fg_color="#C0392B", hover_color="#A93226", command=self.timer_reset).pack(side="left", padx=5)

    def timer_start(self):
        if not self.timer_running:
            try:
                if self.timer_total == 0: 
                    h = int(self.t_hr.get() or 0)
                    m = int(self.t_min.get() or 0)
                    s = int(self.t_sec.get() or 0)
                    self.timer_total = h * 3600 + m * 60 + s
                
                if self.timer_total > 0:
                    self.timer_running = True
                    self.update_timer()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")

    def timer_pause(self):
        self.timer_running = False

    def timer_reset(self):
        self.timer_running = False
        self.timer_total = 0
        self.timer_label.configure(text="00:00:00")

    def update_timer(self):
        if self.timer_running and self.timer_total > 0:
            h = self.timer_total // 3600
            m = (self.timer_total % 3600) // 60
            s = self.timer_total % 60
            self.timer_label.configure(text=f"{h:02}:{m:02}:{s:02}")
            self.timer_total -= 1
            self.after(1000, self.update_timer)
        elif self.timer_total == 0 and self.timer_running:
            self.timer_running = False
            self.trigger_alarm_sound() 
            
    def build_alarm(self):
        tab = self.tabs.tab("Alarm")
        self.alarm_active = False
        self.alarm_check_running = False

        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.pack(expand=True)

        time_row = ctk.CTkFrame(container, fg_color="transparent")
        time_row.pack(pady=10)

        self.al_hr_entry = ctk.CTkEntry(
            time_row, width=80, height=60, 
            font=("Arial", 40), justify="center", placeholder_text="07"
        )
        self.al_hr_entry.pack(side="left", padx=5)

        ctk.CTkLabel(time_row, text=":", font=("Arial", 40)).pack(side="left", padx=5)

        self.al_min_entry = ctk.CTkEntry(
            time_row, width=80, height=60, 
            font=("Arial", 40), justify="center", placeholder_text="00"
        )
        self.al_min_entry.pack(side="left", padx=5)

        self.al_ampm_seg = ctk.CTkSegmentedButton(
            container, values=["AM", "PM"], width=150, height=40
        )
        self.al_ampm_seg.set("AM")
        self.al_ampm_seg.pack(pady=15)

        self.alarm_status = ctk.CTkLabel(tab, text="NO ALARM SET", font=("Arial", 14), text_color="gray")
        self.alarm_status.pack(pady=(0, 20))

        ctk.CTkButton(
            tab, text="Set Alarm", width=200, height=40,
            font=("Arial", 16, "bold"), command=self.set_alarm
        ).pack(side="bottom", pady=30)

    def set_alarm(self):
        hr_str = self.al_hr_entry.get()
        min_str = self.al_min_entry.get()
        ampm = self.al_ampm_seg.get()

        if not hr_str.isdigit() or not min_str.isdigit():
            messagebox.showerror("Error", "Please enter valid numbers only.")
            return

        hr = int(hr_str)
        mn = int(min_str)
        if not (1 <= hr <= 12):
            messagebox.showerror("Error", "Hour must be between 1 and 12.")
            return
        if not (0 <= mn <= 59):
            messagebox.showerror("Error", "Minute must be between 0 and 59.")
            return
        display_time = f"{hr:02}:{mn:02} {ampm}"

        if ampm == "PM" and hr != 12: hr += 12
        if ampm == "AM" and hr == 12: hr = 0
        
        self.alarm_target_time = f"{hr:02}:{mn:02}"
        self.alarm_active = True
        
        self.alarm_status.configure(text=f"ALARM SET FOR {display_time}", text_color="#2CC985")
        
        if not self.alarm_check_running:
            self.alarm_check_running = True
            self.check_alarm_loop()

    def check_alarm_loop(self):
        if self.alarm_active:
            now = datetime.datetime.now().strftime("%H:%M")
            if now == self.alarm_target_time:
                self.trigger_alarm_sound()
                self.alarm_active = False
                self.alarm_status.configure(text="ALARM CLEARED", text_color="gray")
        
        self.after(1000, self.check_alarm_loop)

    def trigger_alarm_sound(self):
        # 1. ROBUST PATH FINDING
        # This looks for 'assets' relative to the main project folder
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sound_path = os.path.join(base_dir, "assets", "alarm.mp3")

        print(f"DEBUG: Looking for sound at: {sound_path}") # Debug print

        if not os.path.exists(sound_path):
            messagebox.showerror("Audio Error", f"Could not find alarm.mp3 at:\n{sound_path}")
            return

        try:
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play(loops=-1) # Loop forever
            
            # This popup BLOCKS the code, so the music keeps playing 
            # until the user clicks OK.
            messagebox.showinfo("ALARM", "Wake Up! Time to go!")
            
            # Once OK is clicked, music stops
            pygame.mixer.music.stop()
            
        except Exception as e:
            messagebox.showerror("Sound Error", f"Failed to play sound: {e}")