import customtkinter as ctk, os, re, webbrowser, qrcode, pyotp
from tkinter import messagebox, PhotoImage
from PIL import Image
import io
from backend.auth import create_user
from backend.database import create_users_table

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def pil_image_to_tkinter(pil_img, size=None):
    """Convert PIL Image to tkinter PhotoImage without needing ImageTk"""
    try:
        if size:
            pil_img = pil_img.resize(size, Image.Resampling.LANCZOS)
        # Convert to PPM format which tkinter understands
        with io.BytesIO() as output:
            pil_img.save(output, format="PPM")
            data = output.getvalue()
        return PhotoImage(data=data)
    except Exception:
        return None

ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("dark-blue")

class SignupApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("900x600"); self.title("A Day Companion - Sign Up"); self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1); self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        self.image_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#000000")
        self.image_frame.grid(row=0, column=0, sticky="nsew")
        
        # Try to load background image
        img_loaded = False
        try:
            lsbg_path = os.path.join(ASSETS_DIR, "lsbg.png")
            img = Image.open(lsbg_path)
            tk_img = pil_image_to_tkinter(img, size=(450, 600))
            if tk_img:
                import tkinter as tk
                label = tk.Label(self.image_frame, image=tk_img, bg="#000000")
                label.image = tk_img
                label.place(x=0, y=0, relwidth=1, relheight=1)
                img_loaded = True
        except Exception:
            pass
        
        if not img_loaded:
            ctk.CTkLabel(self.image_frame, text="Join Us", font=("Helvetica", 30), text_color="white").place(relx=0.5, rely=0.5, anchor="center")
        
        self.form_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#0f172a")
        self.form_frame.grid(row=0, column=1, sticky="nsew")
        self.center_box = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.center_box.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(self.center_box, text="Create Account", font=("Helvetica", 32, "bold"), text_color="white").pack(pady=(0, 10))
        self.email_entry = ctk.CTkEntry(self.center_box, width=300, height=50, placeholder_text="Email Address", fg_color="#1e293b", text_color="white")
        self.email_entry.pack(pady=10)
        pass_frame = ctk.CTkFrame(self.center_box, fg_color="transparent"); pass_frame.pack(pady=10)
        self.password_entry = ctk.CTkEntry(pass_frame, width=220, height=50, placeholder_text="Password", show="*", fg_color="#1e293b", text_color="white")
        self.password_entry.pack(side="left", padx=(0, 10))
        self.toggle_btn = ctk.CTkButton(pass_frame, text="SHOW", width=70, height=50, fg_color="#1e293b", border_width=2, command=self.toggle_pwd)
        self.toggle_btn.pack(side="left")
        ctk.CTkButton(self.center_box, text="Create Account", width=300, height=50, fg_color="#3b82f6", font=("Helvetica", 15, "bold"), command=self.signup_action).pack(pady=20)
        footer = ctk.CTkFrame(self.center_box, fg_color="transparent"); footer.pack(pady=10)
        ctk.CTkLabel(footer, text="Already a member?", text_color="#94a3b8").pack(side="left")
        ctk.CTkButton(footer, text="Login", width=60, fg_color="transparent", text_color="#38bdf8", command=self.login_action).pack(side="left")

    def toggle_pwd(self):
        show = "" if self.password_entry.cget("show") == "*" else "*"
        self.password_entry.configure(show=show); self.toggle_btn.configure(text="HIDE" if show == "" else "SHOW")

    def signup_action(self):
        email, pwd = self.email_entry.get(), self.password_entry.get()
        if not email or not pwd: return messagebox.showerror("Error", "All fields required")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email): return messagebox.showerror("Error", "Invalid email")
        create_users_table()
        if secret_key := create_user(email, pwd):
            self.ask_for_api_key(); self.show_qr_popup(email, secret_key)
        else: messagebox.showerror("Error", "User already exists")

    def show_qr_popup(self, email, secret):
        qr_path = "temp_qr.png"
        qrcode.make(pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="A Day Companion")).save(qr_path)
        top = ctk.CTkToplevel(self)
        top.geometry("400x550"); top.title("Setup 2FA Recovery"); top.attributes("-topmost", True); top.resizable(False, False)
        ctk.CTkLabel(top, text="Scan with Google Authenticator", font=("Helvetica", 18, "bold")).pack(pady=20)
        
        try:
            img = Image.open(qr_path)
            tk_img = pil_image_to_tkinter(img, size=(250, 250))
            if tk_img:
                import tkinter as tk
                label = tk.Label(top, image=tk_img, bg="#0f172a")
                label.image = tk_img
                label.pack(pady=10)
            else:
                ctk.CTkLabel(top, text="[QR Code Error]").pack()
        except:
            ctk.CTkLabel(top, text="[QR Code Error]").pack()
        
        ctk.CTkLabel(top, text="This is your Recovery Key for password resets.", text_color="gray").pack(pady=10)
        def close_and_login():
            if os.path.exists(qr_path): os.remove(qr_path)
            top.destroy(); self.login_action()
        ctk.CTkButton(top, text="I Scanned It -> Login", command=close_and_login, fg_color="#22c55e").pack(pady=20)

    def ask_for_api_key(self):
        if os.path.exists(".env") and "GROQ_API_KEY" in open(".env").read(): return
        if messagebox.askokcancel("Setup AI", "In order to run AI, you might need an API key. Click OK to open the website, then copy-paste the key here."):
            webbrowser.open("https://console.groq.com/keys")
            if api_key := ctk.CTkInputDialog(text="Paste your Groq API Key here:", title="API Setup").get_input():
                with open(".env", "a") as f: f.write(f"\nGROQ_API_KEY={api_key.strip()}\n")

    def login_action(self):
        from ui.login import LoginApp
        self.destroy(); LoginApp().mainloop()

if __name__ == "__main__": SignupApp().mainloop()