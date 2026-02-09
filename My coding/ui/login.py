import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import random
import smtplib
import ssl
from email.message import EmailMessage
from backend.auth import authenticate_user, update_password
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("900x600")
        self.title("A Day Companion - Login")
        self.resizable(False, False)
        self.reset_email = None
        self.generated_otp = None
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
            ctk.CTkLabel(self.image_frame, text="A Day Companion", font=("Helvetica", 30, "bold")).place(relx=0.5, rely=0.5, anchor="center")
        self.form_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#0f172a")
        self.form_frame.grid(row=0, column=1, sticky="nsew")
        self.center_box = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.center_box.place(relx=0.5, rely=0.5, anchor="center")
        self.show_login_form()

    def clear_center_box(self):
        for widget in self.center_box.winfo_children():
            widget.destroy()

    def show_login_form(self):
        self.clear_center_box()
        ctk.CTkLabel(self.center_box, text="Welcome Back", font=("Helvetica", 32, "bold"), text_color="white").pack(pady=(0, 10))
        ctk.CTkLabel(self.center_box, text="Please sign in to continue", font=("Helvetica", 14), text_color="#94a3b8").pack(pady=(0, 30))
        self.email_entry = ctk.CTkEntry(self.center_box, width=300, height=50, placeholder_text="Email Address", fg_color="#1e293b", border_color="#334155", text_color="white")
        self.email_entry.pack(pady=10)
        pass_frame = ctk.CTkFrame(self.center_box, fg_color="transparent")
        pass_frame.pack(pady=10)
        self.password_entry = ctk.CTkEntry(pass_frame, width=220, height=50, placeholder_text="Password", show="*", fg_color="#1e293b", border_color="#334155", text_color="white")
        self.password_entry.pack(side="left", padx=(0, 10))
        self.pass_visible = False
        self.toggle_btn = ctk.CTkButton(pass_frame, text="SHOW", width=70, height=50, fg_color="#1e293b", hover_color="#334155", border_color="#334155", border_width=2, command=self.toggle_login_password)
        self.toggle_btn.pack(side="left")
        ctk.CTkButton(self.center_box, text="Forgot Password?", fg_color="transparent", text_color="#94a3b8", hover_color="#0f172a", font=("Helvetica", 12), command=self.show_forgot_email_form).pack(pady=(0, 10))
        ctk.CTkButton(self.center_box, text="Login", width=300, height=50, fg_color="#3b82f6", hover_color="#2563eb", font=("Helvetica", 15, "bold"), command=self.login_action).pack(pady=10)
        footer = ctk.CTkFrame(self.center_box, fg_color="transparent")
        footer.pack(pady=20)
        ctk.CTkLabel(footer, text="Don't have an account?", text_color="#94a3b8").pack(side="left")
        ctk.CTkButton(footer, text="Sign Up", width=60, fg_color="transparent", text_color="#38bdf8", hover_color="#1e293b", command=self.signup_action).pack(side="left")

    def show_forgot_email_form(self):
        self.clear_center_box()
        ctk.CTkLabel(self.center_box, text="Reset Password", font=("Helvetica", 28, "bold"), text_color="white").pack(pady=(0, 10))
        ctk.CTkLabel(self.center_box, text="Enter your email to receive an OTP", font=("Helvetica", 14), text_color="#94a3b8").pack(pady=(0, 30))
        self.reset_email_entry = ctk.CTkEntry(self.center_box, width=300, height=50, placeholder_text="Enter your email", fg_color="#1e293b", border_color="#334155", text_color="white")
        self.reset_email_entry.pack(pady=10)
        ctk.CTkButton(self.center_box, text="Send OTP", width=300, height=50, fg_color="#3b82f6", hover_color="#2563eb", font=("Helvetica", 15, "bold"), command=self.action_send_otp).pack(pady=20)
        ctk.CTkButton(self.center_box, text="Back to Login", fg_color="transparent", text_color="#94a3b8", command=self.show_login_form).pack()

    def show_otp_form(self):
        self.clear_center_box()
        ctk.CTkLabel(self.center_box, text="Verify OTP", font=("Helvetica", 28, "bold"), text_color="white").pack(pady=(0, 10))
        ctk.CTkLabel(self.center_box, text=f"OTP sent to {self.reset_email}", font=("Helvetica", 12), text_color="#94a3b8").pack(pady=(0, 30))
        self.otp_entry = ctk.CTkEntry(self.center_box, width=300, height=50, placeholder_text="Enter 6-digit OTP", fg_color="#1e293b", border_color="#334155", text_color="white")
        self.otp_entry.pack(pady=10)
        ctk.CTkButton(self.center_box, text="Verify & Proceed", width=300, height=50, fg_color="#22c55e", hover_color="#16a34a", font=("Helvetica", 15, "bold"), command=self.action_verify_otp).pack(pady=20)
        ctk.CTkButton(self.center_box, text="Cancel", fg_color="transparent", text_color="#94a3b8", command=self.show_login_form).pack()

    def show_new_password_form(self):
        self.clear_center_box()
        ctk.CTkLabel(self.center_box, text="New Password", font=("Helvetica", 28, "bold"), text_color="white").pack(pady=(0, 10))
        ctk.CTkLabel(self.center_box, text="Set your new secure password", font=("Helvetica", 14), text_color="#94a3b8").pack(pady=(0, 30))
        self.new_pass_entry = ctk.CTkEntry(self.center_box, width=300, height=50, placeholder_text="New Password", show="*", fg_color="#1e293b", border_color="#334155", text_color="white")
        self.new_pass_entry.pack(pady=10)
        ctk.CTkButton(self.center_box, text="Update Password", width=300, height=50, fg_color="#3b82f6", hover_color="#2563eb", font=("Helvetica", 15, "bold"), command=self.action_update_password).pack(pady=20)

    def send_otp(self, email_address):
        otp = random.randint(100000, 999999)
        my_email = "adaycompanion@gmail.com"
        my_password = "ykpt ffkf fmcr lwmg"
        subject = "Your Login OTP"
        body = f"Your One-Time Password (OTP) is: {otp}\nDo not share this."
        msg = EmailMessage()
        msg["From"] = my_email
        msg["To"] = email_address
        msg["Subject"] = subject
        msg.set_content(body)
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(my_email, my_password)
                smtp.sendmail(my_email, email_address, msg.as_string())
            return otp
        except Exception as e:
            print(f"Email Error: {e}")
            return None

    def action_send_otp(self):
        email = self.reset_email_entry.get().strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Invalid Email Format")
            return
        otp = self.send_otp(email)
        if otp:
            self.reset_email = email
            self.generated_otp = otp
            messagebox.showinfo("OTP Sent", f"An OTP has been sent to {email}")
            self.show_otp_form()
        else:
            messagebox.showerror("Error", "Failed to send email.")

    def action_verify_otp(self):
        user_otp = self.otp_entry.get().strip()
        if user_otp == str(self.generated_otp):
            self.show_new_password_form()
        else:
            messagebox.showerror("Error", "Invalid OTP.")

    def action_update_password(self):
        new_pass = self.new_pass_entry.get().strip()
        if len(new_pass) < 4:
            messagebox.showerror("Error", "Password too short")
            return
        if update_password(self.reset_email, new_pass):
            messagebox.showinfo("Success", "Password updated! Login now.")
            self.show_login_form()
        else:
            messagebox.showerror("Error", "Update failed.")

    def toggle_login_password(self):
        if self.pass_visible:
            self.password_entry.configure(show="*")
            self.toggle_btn.configure(text="SHOW")
            self.pass_visible = False
        else:
            self.password_entry.configure(show="")
            self.toggle_btn.configure(text="HIDE")
            self.pass_visible = True

    def login_action(self):
        from backend.database import get_user_id
        from ui.dashboard import DashboardApp
        email = self.email_entry.get()
        password = self.password_entry.get()
        if authenticate_user(email, password):
            user_id = get_user_id(email)
            self.destroy()
            app = DashboardApp(user_id)
            app.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    def signup_action(self):
        from ui.signup import SignupApp
        self.destroy()
        SignupApp().mainloop()

if __name__ == "__main__":
    LoginApp().mainloop()