import customtkinter as ctk
from PIL import Image
import os
from tkinter import PhotoImage
import io

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

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

PAGES = [
    {"title": "Welcome", "text": "Your intelligent daily companion for focus, balance, and productivity."},
    {"title": "What is A Day Companion?", "text": "A smart productivity system that helps you plan better, work deeper, and live calmer."},
    {"title": "How It Helps", "text": "> Smart task prioritization\n> Habit building & consistency\n> Focus & distraction tracking\n> Personalized AI suggestions"},
    {"title": "Did You Know?", "text": "> 2 in 3 students experience academic stress\n\n> Poor sleep reduces motivation by 40%\n\n> Time mismanagement is the #1 productivity killer"},
    {"title": "Ready to Begin?", "text": "Let's build a calmer, more productive routine - one day at a time.", "final": True}
]

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1200x600"); self.title("A Day Companion"); self.configure(fg_color="#0b132b")
        self.idx, self.frames = 0, []
        
        sidebar = ctk.CTkFrame(self, fg_color="#0a1128", width=420)
        sidebar.pack(side="left", fill="y"); sidebar.pack_propagate(False)
        
        # Try to load logo image
        try:
            logo_path = os.path.join(ASSETS_DIR, "logo.png")
            img = Image.open(logo_path)
            # Convert to tkinter PhotoImage
            tk_img = pil_image_to_tkinter(img, size=(240, 240))
            if tk_img:
                import tkinter as tk
                label = tk.Label(sidebar, image=tk_img, bg="#0a1128")
                label.image = tk_img  # Keep a reference
                label.pack(pady=(90, 25))
        except Exception:
            pass
        ctk.CTkLabel(sidebar, text="Boost your productivity\n", font=("Helvetica", 28, "bold"), text_color="white").pack(padx=20)
        
        self.content = ctk.CTkFrame(self, fg_color="#1c2541", border_color="#5bc0be", border_width=2, corner_radius=36)
        self.content.pack(side="right", expand=True, fill="both", padx=40, pady=40)
        
        for i, p in enumerate(PAGES):
            f = ctk.CTkFrame(self.content, fg_color="transparent")
            self.frames.append(f)
            inner = ctk.CTkFrame(f, fg_color="transparent")
            inner.place(relx=0.5, rely=0.45, anchor="center")
            ctk.CTkLabel(inner, text=p["title"], font=("Helvetica", 36, "bold"), text_color="white").pack(pady=(0, 24))
            ctk.CTkLabel(inner, text=p["text"], font=("Helvetica", 18), text_color="#eaeaea", wraplength=520).pack(pady=(0, 50))
            
            btns = ctk.CTkFrame(inner, fg_color="transparent"); btns.pack()
            if p.get("final"):
                ctk.CTkButton(btns, text="Get Started", width=180, height=52, font=("Helvetica", 16, "bold"), corner_radius=26, fg_color="#3a86ff", hover_color="#5fa8ff", command=self.open_signup).pack(side="left", padx=12)
                ctk.CTkButton(btns, text="I already have an account", width=220, height=52, fg_color="transparent", border_width=2, border_color="#9bbcd1", text_color="#9bbcd1", hover_color="#2b3a67", command=self.open_login).pack(side="left", padx=12)
            else:
                if i > 0: ctk.CTkButton(btns, text="Back", width=120, height=48, fg_color="#2b3a67", hover_color="#3a86ff", corner_radius=22, command=self.prev_page).pack(side="left", padx=12)
                ctk.CTkButton(btns, text="Next", width=120, height=48, fg_color="#3a86ff", hover_color="#5fa8ff", corner_radius=22, command=self.next_page).pack(side="left", padx=12)
            
            dots = ctk.CTkFrame(inner, fg_color="transparent"); dots.pack(pady=(30, 0))
            for j in range(len(PAGES)): ctk.CTkLabel(dots, text="*", font=("Helvetica", 48), text_color="#3a86ff" if j == i else "#9bbcd1").pack(side="left", padx=6)

        self.bind("<Right>", lambda e: self.next_page()); self.bind("<Left>", lambda e: self.prev_page())
        self.show_page()

    def show_page(self):
        for f in self.frames: f.pack_forget()
        self.frames[self.idx].pack(fill="both", expand=True)

    def next_page(self):
        if self.idx < len(PAGES) - 1: self.idx += 1; self.show_page()
        
    def prev_page(self):
        if self.idx > 0: self.idx -= 1; self.show_page()
        
    def open_signup(self): 
        from ui.signup import SignupApp
        self.destroy(); SignupApp().mainloop()
        
    def open_login(self): 
        from ui.login import LoginApp
        self.destroy(); LoginApp().mainloop()