import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from backend.auth import create_user
from backend.database import create_users_table
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class SignupApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("900x600")
        self.title("A Day Companion - Sign Up")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.image_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#000000")
        self.image_frame.grid(row=0, column=0, sticky="nsew")

        try:
            bg_path = os.path.join("assets", "lsbg.png")
            pil_img = Image.open(bg_path)
            self.side_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(450, 600))
            img_label = ctk.CTkLabel(self.image_frame, image=self.side_image, text="")
            img_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            ctk.CTkLabel(self.image_frame, text="Join Us", font=("Helvetica", 30)).place(relx=0.5, rely=0.5)

        self.form_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#0f172a")
        self.form_frame.grid(row=0, column=1, sticky="nsew")

        self.center_box = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.center_box.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.center_box, text="Create Account", font=("Helvetica", 32, "bold"), text_color="white").pack(pady=(0, 10))
        ctk.CTkLabel(self.center_box, text="Start your productivity journey", font=("Helvetica", 14), text_color="#94a3b8").pack(pady=(0, 30))

        
        self.email_entry = ctk.CTkEntry(
            self.center_box, width=300, height=50, 
            placeholder_text="Email Address",
            fg_color="#1e293b", border_color="#334155", text_color="white"
        )
        self.email_entry.pack(pady=10)

        
        pass_frame = ctk.CTkFrame(self.center_box, fg_color="transparent")
        pass_frame.pack(pady=10)

        self.password_entry = ctk.CTkEntry(
            pass_frame, width=220, height=50, 
            placeholder_text="Password", show="*",
            fg_color="#1e293b", border_color="#334155", text_color="white"
        )
        self.password_entry.pack(side="left", padx=(0, 10))

        self.pass_visible = False
        self.toggle_btn = ctk.CTkButton(
            pass_frame, text="SHOW", width=70, height=50,
            fg_color="#1e293b", hover_color="#334155", border_color="#334155", border_width=2,
            command=self.toggle_password
        )
        self.toggle_btn.pack(side="left")

        
        ctk.CTkButton(
            self.center_box, text="Create Account", width=300, height=50,
            fg_color="#3b82f6", hover_color="#2563eb",
            font=("Helvetica", 15, "bold"),
            command=self.signup_action
        ).pack(pady=20)

        
        footer = ctk.CTkFrame(self.center_box, fg_color="transparent")
        footer.pack(pady=10)
        ctk.CTkLabel(footer, text="Already a member?", text_color="#94a3b8").pack(side="left")
        ctk.CTkButton(
            footer, text="Login", width=60, fg_color="transparent", 
            text_color="#38bdf8", hover_color="#1e293b",
            command=self.login_action
        ).pack(side="left")

    def toggle_password(self):
        if self.pass_visible:
            self.password_entry.configure(show="*")
            self.toggle_btn.configure(text="SHOW")
            self.pass_visible = False
        else:
            self.password_entry.configure(show="")
            self.toggle_btn.configure(text="HIDE")
            self.pass_visible = True

    def valid_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def signup_action(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showerror("Error", "All fields are required")
            return

        if not self.valid_email(email):
            messagebox.showerror("Error", "Invalid email address")
            return

        create_users_table()

        if create_user(email, password):
            res = messagebox.askyesno("Success", "Account created! Login now?")
            if res:
                self.login_action()
        else:
            messagebox.showerror("Error", "User already exists")

    def login_action(self):
        from ui.login import LoginApp
        self.destroy()
        LoginApp().mainloop()

if __name__ == "__main__":
    SignupApp().mainloop()