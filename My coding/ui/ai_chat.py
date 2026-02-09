import customtkinter as ctk
from tkinter import messagebox
from ai import ask_ai, daily_count, MAX_DAILY_PROMPTS
from backend.profile_db import get_profile

class AIChat(ctk.CTkToplevel):
    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
        profile = get_profile(user_id)

        if not profile:
            messagebox.showerror("Error", "Profile not found")
            self.destroy()
            return

        self.user_name = profile[0]
        self.hobbies = profile[2]

        self.title("AI Companion")
        self.geometry("900x700")
        self.resizable(False, False)
        self.configure(fg_color="#0f172a")

        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="#1e293b", height=80, corner_radius=0)
        header.pack(fill="x")

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(
            title_frame,
            text=f"AI Companion",
            font=("Helvetica", 20, "bold"),
            text_color="white"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text=f"Context Active: {self.hobbies}",
            font=("Helvetica", 12),
            text_color="#94a3b8"
        ).pack(anchor="w")

        self.prompt_label = ctk.CTkLabel(
            header,
            text=self.get_prompt_text(),
            font=("Helvetica", 14, "bold"),
            text_color="#38bdf8"
        )
        self.prompt_label.pack(side="right", padx=20)

        self.chat_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#020617",
            scrollbar_button_color="#334155",
            scrollbar_button_hover_color="#475569"
        )
        self.chat_frame.pack(fill="both", expand=True, padx=20, pady=20)

        bottom = ctk.CTkFrame(self, fg_color="#1e293b", height=80, corner_radius=0)
        bottom.pack(fill="x")

        self.input_box = ctk.CTkEntry(
            bottom,
            placeholder_text=f"Ask anything, {self.user_name}...",
            height=50,
            font=("Helvetica", 14),
            border_width=0,
            fg_color="#334155",
            text_color="white"
        )
        self.input_box.pack(side="left", padx=20, pady=15, fill="x", expand=True)
        self.input_box.bind("<Return>", lambda e: self.send())

        ctk.CTkButton(
            bottom,
            text="Send",
            width=100,
            height=50,
            fg_color="#38bdf8",
            hover_color="#0ea5e9",
            font=("Helvetica", 14, "bold"),
            command=self.send
        ).pack(side="right", padx=20)

        self.add_ai_message(
            f"Hello {self.user_name}! I'm ready.\n"
            "I know your goals and hobbies, so ask me how to balance them with your studies."
        )

    def get_prompt_text(self):
        used = daily_count(self.user_id)
        return f"{MAX_DAILY_PROMPTS - used} Prompts Left"

    def add_user_message(self, text):
        container = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        container.pack(fill="x", pady=10)

        bubble = ctk.CTkFrame(container, fg_color="#3b82f6", corner_radius=20)
        bubble.pack(anchor="e", padx=(50, 10))

        ctk.CTkLabel(
            bubble,
            text=text,
            wraplength=450,
            justify="left",
            text_color="white",
            font=("Helvetica", 15)
        ).pack(padx=15, pady=10)

    def add_ai_message(self, text):
        container = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        container.pack(fill="x", pady=10)

        bubble = ctk.CTkFrame(container, fg_color="#1e293b", corner_radius=20)
        bubble.pack(anchor="w", padx=(10, 50))

        ctk.CTkLabel(
            bubble,
            text=text,
            wraplength=450,
            justify="left",
            text_color="#e2e8f0",
            font=("Helvetica", 15)
        ).pack(padx=15, pady=10)

    def send(self):
        text = self.input_box.get().strip()
        if not text:
            return

        self.input_box.delete(0, "end")
        self.add_user_message(text)

        self.chat_frame.update() 

        reply = ask_ai(self.user_id, text)
        self.add_ai_message(reply)
        self.prompt_label.configure(text=self.get_prompt_text())

        self.chat_frame._parent_canvas.yview_moveto(1.0)