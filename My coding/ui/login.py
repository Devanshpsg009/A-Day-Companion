import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageFilter, ImageDraw, ImageTk
from backend.auth import authenticate_user
import re
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("600x800")
        self.title("Login")
        self.resizable(False, False)

        bg_path = os.path.join("assets", "lsbg.png")
        try:
            pil_image = Image.open(bg_path)
            self.bg_image = ctk.CTkImage(pil_image, size=(600, 800))
            bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            self.configure(fg_color="#0f172a")

        self.container = ctk.CTkFrame(self, width=480, height=550, fg_color="transparent")
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        self.card_frame = ctk.CTkFrame(
            self.container, 
            width=480, 
            height=420, 
            corner_radius=30,
            fg_color="#1e293b", 
            bg_color="transparent"
        )
        self.card_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            self.card_frame, 
            text="Welcome Back", 
            font=("Helvetica", 30, "bold"), 
            text_color="white"
        ).pack(pady=(40, 10))

        ctk.CTkLabel(
            self.card_frame, 
            text="Login to continue", 
            font=("Helvetica", 14), 
            text_color="#94a3b8"
        ).pack(pady=(0, 40))

        self.email_entry = ctk.CTkEntry(
            self.card_frame, width=360, height=50, 
            placeholder_text="Email Address",
            fg_color="#334155", border_width=0, text_color="white"
        )
        self.email_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(
            self.card_frame, width=360, height=50, 
            placeholder_text="Password", show="*",
            fg_color="#334155", border_width=0, text_color="white"
        )
        self.password_entry.pack(pady=10)

        ctk.CTkButton(
            self.card_frame, text="Login", width=360, height=50,
            fg_color="#3b82f6", hover_color="#2563eb",
            font=("Helvetica", 16, "bold"),
            command=self.login_action
        ).pack(pady=30)

        ctk.CTkButton(
            self.card_frame, text="Create New Account", 
            fg_color="transparent", hover_color="#334155",
            text_color="#94a3b8",
            command=self.signup_action
        ).pack()

    def valid_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def login_action(self):
        from backend.database import get_user_id
        from ui.dashboard import DashboardApp

        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
             messagebox.showerror("Error", "Please fill all fields")
             return

        if authenticate_user(email, password):
            user_id = get_user_id(email)
            self.destroy()
            app = DashboardApp(user_id)
            app.mainloop()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def signup_action(self):
        from ui.signup import SignupApp
        self.destroy()
        SignupApp().mainloop()

if __name__ == "__main__":
    LoginApp().mainloop()