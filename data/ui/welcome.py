import customtkinter as ctk
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class Theme:
    MAIN_BG = "#0b132b"
    SIDEBAR = "#0a1128"
    GLASS = "#1c2541"
    BORDER = "#5bc0be"
    BTN = "#3a86ff"
    BTN_HOV = "#5fa8ff"
    BTN_BACK = "#2b3a67"
    TEXT = "#eaeaea"
    MUTED = "#9bbcd1"

    FONT_TITLE = ("Helvetica", 36, "bold")
    FONT_BODY = ("Helvetica", 18)
    FONT_SIDE = ("Helvetica", 28, "bold")

class PageData:
    PAGES = [
        {
            "title": "Welcome",
            "text": "Your intelligent daily companion for focus, balance, and productivity."
        },
        {
            "title": "What is A Day Companion?",
            "text": "A smart productivity system that helps you plan better, work deeper, and live calmer."
        },
        {
            "title": "How It Helps",
            "text": "> Smart task prioritization\n"
                    "> Habit building & consistency\n"
                    "> Focus & distraction tracking\n"
                    "> Personalized AI suggestions"
        },
        {
            "title": "Did You Know?",
            "text": "> 2 in 3 students experience academic stress\n\n"
                    "> Poor sleep reduces motivation by 40%\n\n"
                    "> Time mismanagement is the #1 productivity killer"
        },
        {
            "title": "Ready to Begin?",
            "text": "Let's build a calmer, more productive routine - one day at a time.",
            "is_final": True
        }
    ]

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1200x600")
        self.title("A Day Companion")
        self.configure(fg_color=Theme.MAIN_BG)
        self.resizable(True, True)

        self.current_page = 0

        self.build_sidebar()
        self.build_content()
        self.bind_keys()
        self.show_page(0)

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=Theme.SIDEBAR, width=420)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        try:
            self.logo_img = ctk.CTkImage(Image.open("assets//logo.png"), size=(240, 240))
            ctk.CTkLabel(self.sidebar, image=self.logo_img, text="").pack(pady=(90, 25))
        except Exception:
            pass

        ctk.CTkLabel(
            self.sidebar,
            text="Boost your productivity\n",
            font=Theme.FONT_SIDE,
            text_color="white",
            justify="center"
        ).pack(padx=20)

    def build_content(self):
        self.content = ctk.CTkFrame(
            self,
            fg_color=Theme.GLASS,
            border_color=Theme.BORDER,
            border_width=2,
            corner_radius=36
        )
        self.content.pack(side="right", expand=True, fill="both", padx=40, pady=40)

    def show_page(self, index):
        for w in self.content.winfo_children():
            w.destroy()

        data = PageData.PAGES[index]

        self.inner = ctk.CTkFrame(self.content, fg_color="transparent")
        self.inner.place(relx=0.5, rely=0.45, anchor="center")

        ctk.CTkLabel(
            self.inner,
            text=data["title"],
            font=Theme.FONT_TITLE,
            text_color="white"
        ).pack(pady=(0, 24))

        ctk.CTkLabel(
            self.inner,
            text=data["text"],
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT,
            wraplength=520,
            justify="center"
        ).pack(pady=(0, 50))

        self.build_buttons(data)
        self.build_progress()

    def build_buttons(self, data):
        btns = ctk.CTkFrame(self.inner, fg_color="transparent")
        btns.pack()

        if data.get("is_final"):
            ctk.CTkButton(
                btns,
                text="Get Started",
                width=180,
                height=52,
                font=("Helvetica", 16, "bold"),
                corner_radius=26,
                fg_color=Theme.BTN,
                hover_color=Theme.BTN_HOV,
                command=self.open_signup
            ).pack(side="left", padx=12)

            ctk.CTkButton(
                btns,
                text="I already have an account",
                width=220,
                height=52,
                fg_color="transparent",
                border_width=2,
                border_color=Theme.MUTED,
                text_color=Theme.MUTED,
                hover_color=Theme.BTN_BACK,
                command=self.open_login
            ).pack(side="left", padx=12)
        else:
            if self.current_page > 0:
                ctk.CTkButton(
                    btns,
                    text="Back",
                    width=120,
                    height=48,
                    fg_color=Theme.BTN_BACK,
                    hover_color=Theme.BTN,
                    corner_radius=22,
                    command=self.prev_page
                ).pack(side="left", padx=12)

            ctk.CTkButton(
                btns,
                text="Next",
                width=120,
                height=48,
                fg_color=Theme.BTN,
                hover_color=Theme.BTN_HOV,
                corner_radius=22,
                command=self.next_page
            ).pack(side="left", padx=12)

    def build_progress(self):
        dots = ctk.CTkFrame(self.inner, fg_color="transparent")
        dots.pack(pady=(30, 0))

        for i in range(len(PageData.PAGES)):
            color = Theme.BTN if i == self.current_page else Theme.MUTED
            ctk.CTkLabel(dots, text="*", font=("Helvetica", 48), text_color=color).pack(side="left", padx=6)

    def next_page(self):
        if self.current_page < len(PageData.PAGES) - 1:
            self.current_page += 1
            self.show_page(self.current_page)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page(self.current_page)

    def bind_keys(self):
        self.bind("<Right>", lambda e: self.next_page())
        self.bind("<Left>", lambda e: self.prev_page())

    def open_signup(self):
        from ui.signup import SignupApp
        self.destroy()
        app = SignupApp()
        app.mainloop()

    def open_login(self):
        from ui.login import LoginApp
        self.destroy()
        app = LoginApp()
        app.mainloop()