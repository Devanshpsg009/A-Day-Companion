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

        # 1. Load Background
        bg_path = os.path.join("assets", "lsbg.png")
        try:
            # Load and Resize Image
            bg_source = Image.open(bg_path).resize((600, 800))
            self.bg_image = ctk.CTkImage(bg_source, size=(600, 800))
            
            # Place Background
            bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

            # --- GENERATE GLASS EFFECT ---
            # Card Dimensions
            card_w, card_h = 480, 420
            
            # Calculate Center Position
            card_x = (600 - card_w) // 2
            card_y = int(800 * 0.22) # 22% from top

            # Crop the background where the card will be
            crop = bg_source.crop((card_x, card_y, card_x + card_w, card_y + card_h))
            
            # Apply Blur
            blur = crop.filter(ImageFilter.GaussianBlur(20))
            
            # Darken it slightly
            overlay = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 100))
            blur = Image.alpha_composite(blur.convert("RGBA"), overlay)

            # Round Corners
            mask = Image.new("L", (card_w, card_h), 0)
            ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (card_w, card_h)], 30, fill=255)

            final = crop.convert("RGBA")
            final.paste(blur, (0, 0), mask=mask)
            self.card_image_tk = ImageTk.PhotoImage(final)

            # --- CONTAINER FRAME (The Fix) ---
            # Instead of placing everything on 'self', we make a frame that holds everything together
            self.main_frame = ctk.CTkFrame(self, width=card_w, height=card_h, fg_color="transparent")
            self.main_frame.place(relx=0.5, rely=0.22, anchor="n") # Center horizontally, top anchored

            # 2. Draw Card Image inside Main Frame
            canvas = tk.Canvas(self.main_frame, width=card_w, height=card_h, bd=0, highlightthickness=0)
            canvas.place(x=0, y=0)
            canvas.create_image(0, 0, image=self.card_image_tk, anchor="nw")
            
            # Text on Canvas
            canvas.create_text(card_w / 2, 40, text="Welcome Back", font=("Helvetica", 30, "bold"), fill="white")
            canvas.create_text(card_w / 2, 85, text="Login using your email", font=("Helvetica", 13), fill="#dddddd")

            # 3. Inputs (Relative to Main Frame)
            # Notice x=60. Since main_frame is width 480, inputs width 360, (480-360)/2 = 60.
            # This ensures perfect centering inside the card.
            self.email_entry = ctk.CTkEntry(
                self.main_frame, width=360, height=45, 
                placeholder_text="Email address",
                fg_color="#3a3a3a", border_width=0, text_color="white"
            )
            self.email_entry.place(x=60, y=130)

            self.password_entry = ctk.CTkEntry(
                self.main_frame, width=360, height=45, 
                placeholder_text="Password", show="*", 
                fg_color="#3a3a3a", border_width=0, text_color="white"
            )
            self.password_entry.place(x=60, y=190)

            # Toggle Button
            self.password_visible = False
            self.toggle_btn = ctk.CTkButton(
                self.main_frame, text="SHOW", width=60, height=45,
                fg_color="#3a3a3a", hover_color="#4a4a4a",
                text_color="white", command=self.toggle_password
            )
            self.toggle_btn.place(x=360, y=190) # Aligned to right of password box

            # Login Button
            ctk.CTkButton(
                self.main_frame, text="Login", width=360, height=45,
                fg_color="#1f538d", hover_color="#153860",
                font=("Helvetica", 16, "bold"),
                command=self.login_action
            ).place(x=60, y=255)

            # Footer Lines
            canvas.create_text(card_w / 2, 315, text="or", fill="#aaaaaa", font=("Arial", 12))
            canvas.create_line(110, 315, 210, 315, fill="#aaaaaa")
            canvas.create_line(270, 315, 370, 315, fill="#aaaaaa")

            # Signup Button
            ctk.CTkButton(
                self.main_frame, text="Sign Up", width=360, height=45,
                fg_color="#ffffff", text_color="#000000",
                hover_color="#e6e6e6",
                command=self.signup_action
            ).place(x=60, y=345)

        except Exception as e:
            print(f"Error loading UI: {e}")
            self.configure(fg_color="#0f172a")

    def toggle_password(self):
        if self.password_visible:
            self.password_entry.configure(show="*")
            self.toggle_btn.configure(text="SHOW")
            self.password_visible = False
        else:
            self.password_entry.configure(show="")
            self.toggle_btn.configure(text="HIDE")
            self.password_visible = True

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