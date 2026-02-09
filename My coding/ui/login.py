import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageFilter, ImageDraw, ImageTk
from backend.auth import authenticate_user
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("600x800")
        self.title("Login")
        self.resizable(False, False)

        bg_source = Image.open("assets//lsbg.png").resize((600, 800))
        self.bg_image = ctk.CTkImage(bg_source, size=(600, 800))
        ctk.CTkLabel(self, image=self.bg_image, text="").place(x=0, y=0, relwidth=1, relheight=1)

        card_w, card_h = 480, 420
        card_x = (600 - card_w) // 2
        card_y = int(800 * 0.22)

        crop = bg_source.crop((card_x, card_y, card_x + card_w, card_y + card_h))
        blur = crop.filter(ImageFilter.GaussianBlur(20))
        overlay = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 100))
        blur = Image.alpha_composite(blur.convert("RGBA"), overlay)

        mask = Image.new("L", (card_w, card_h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (card_w, card_h)], 30, fill=255)

        final = crop.convert("RGBA")
        final.paste(blur, (0, 0), mask=mask)
        self.card = ImageTk.PhotoImage(final)

        canvas = tk.Canvas(self, width=card_w, height=card_h, bd=0, highlightthickness=0)
        canvas.place(x=card_x, y=card_y)
        canvas.create_image(0, 0, image=self.card, anchor="nw")
        canvas.create_text(card_w / 2, 40, text="Welcome Back", font=("Helvetica", 30, "bold"), fill="white")
        canvas.create_text(card_w / 2, 85, text="Login using your email", font=("Helvetica", 13), fill="#dddddd")

        self.email_entry = ctk.CTkEntry(self, width=360, height=45, placeholder_text="Email address",
                                       fg_color="#3a3a3a", border_width=0, text_color="white")
        self.email_entry.place(x=card_x + 60, y=card_y + 130)

        self.password_entry = ctk.CTkEntry(self, width=360, height=45, placeholder_text="Password",
                                          show="*", fg_color="#3a3a3a", border_width=0, text_color="white")
        self.password_entry.place(x=card_x + 60, y=card_y + 190)

        self.password_visible = False

        def toggle_password():
            self.password_entry.configure(show="" if not self.password_visible else "*")
            self.toggle_btn.configure(text="HIDE" if not self.password_visible else "SHOW")
            self.password_visible = not self.password_visible

        self.toggle_btn = ctk.CTkButton(self, text="SHOW", width=60, height=45,
                                        fg_color="#3a3a3a", hover_color="#4a4a4a",
                                        text_color="white", command=toggle_password)
        self.toggle_btn.place(x=card_x + 360, y=card_y + 190)

        ctk.CTkButton(self, text="Login", width=360, height=45,
                      fg_color="#1f538d", hover_color="#153860",
                      font=("Helvetica", 16, "bold"),
                      command=self.login_action).place(x=card_x + 60, y=card_y + 255)

        canvas.create_text(card_w / 2, 315, text="or", fill="#aaaaaa", font=("Arial", 12))
        canvas.create_line(110, 315, 210, 315, fill="#aaaaaa")
        canvas.create_line(270, 315, 370, 315, fill="#aaaaaa")

        ctk.CTkButton(self, text="Sign Up", width=360, height=45,
                      fg_color="#ffffff", text_color="#000000",
                      hover_color="#e6e6e6",
                      command=self.signup_action).place(x=card_x + 60, y=card_y + 345)

    def valid_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def login_action(self):
        from backend.database import get_user_id
        from ui.dashboard import DashboardApp

        email = self.email_entry.get()
        password = self.password_entry.get()
        if not email or not password:
            messagebox.showerror("Error", "All fields are required")
            return

        if not self.valid_email(email):
            messagebox.showerror("Error", "Please enter a valid email")
            return

        if authenticate_user(email, password):
            user_id = get_user_id(email)
            messagebox.showinfo("Success", "Login successful")

            self.destroy()
            app = DashboardApp(user_id)
            app.mainloop()
        else:
            messagebox.showerror("Error", "Invalid email or password")

    def signup_action(self):
        from ui.signup import SignupApp
        self.destroy()
        SignupApp().mainloop()

if __name__ == "__main__":
    LoginApp().mainloop()