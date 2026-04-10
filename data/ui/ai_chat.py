import customtkinter as ctk
from tkinter import messagebox
from backend.ai import ask_ai, daily_count, MAX_DAILY_PROMPTS
from backend.profile_db import get_profile


class AIChat(ctk.CTkToplevel):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

        profile = get_profile(user_id)
        if profile is None:
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

    # ---------------- UI ----------------
    def build_ui(self):
        # HEADER
        header = ctk.CTkFrame(self, fg_color="#1e293b", height=70)
        header.pack(fill="x")

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(
            left,
            text="AI Companion",
            font=("Helvetica", 20, "bold"),
            text_color="white",
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=f"Hobbies: {self.hobbies}",
            font=("Helvetica", 12),
            text_color="#94a3b8",
        ).pack(anchor="w")

        self.prompt_label = ctk.CTkLabel(
            header,
            text=self.get_prompt_text(),
            font=("Helvetica", 13, "bold"),
            text_color="#38bdf8",
        )
        self.prompt_label.pack(side="right", padx=20)

        # CHAT AREA
        self.chat_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#020617",
            scrollbar_button_color="#334155",
        )
        self.chat_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # INPUT AREA
        bottom = ctk.CTkFrame(self, fg_color="#1e293b", height=70)
        bottom.pack(fill="x")

        self.input_box = ctk.CTkEntry(
            bottom,
            placeholder_text=f"Message {self.user_name}...",
            height=45,
            font=("Helvetica", 14),
            corner_radius=20,
            fg_color="#1f2937",
            text_color="white",
            border_width=0,
        )
        self.input_box.pack(side="left", padx=15, pady=15, fill="x", expand=True)
        self.input_box.bind("<Return>", self.on_enter_pressed)

        send_button = ctk.CTkButton(
            bottom,
            text="Send",
            width=100,
            height=45,
            corner_radius=20,
            fg_color="#38bdf8",
            hover_color="#0ea5e9",
            font=("Helvetica", 14, "bold"),
            command=self.send,
        )
        send_button.pack(side="right", padx=15)

        # WELCOME MESSAGE
        self.add_message(
            f"Hey {self.user_name}! 👋\nI'm your AI study companion.\nAsk me anything about studies, focus, or productivity.",
            is_user=False,
        )

    def get_prompt_text(self):
        remaining = MAX_DAILY_PROMPTS - daily_count(self.user_id)
        return f"{remaining} Prompts Left"

    # ---------------- MESSAGE UI (FIXED) ----------------
    def add_message(self, text, is_user=False):
        container = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        container.pack(fill="x", pady=6, padx=8)

        align = "e" if is_user else "w"
        bubble_color = "#2563eb" if is_user else "#1f2937"

        bubble = ctk.CTkFrame(
            container,
            fg_color=bubble_color,
            corner_radius=16
        )
        bubble.pack(anchor=align, padx=10)

        # ✅ FIX: using Label instead of Textbox (no big boxes now)
        label = ctk.CTkLabel(
            bubble,
            text=text,
            wraplength=400,
            justify="left",
            font=("Helvetica", 14),
            text_color="white" if is_user else "#e5e7eb"
        )
        label.pack(padx=12, pady=8)

        self.chat_frame.update_idletasks()
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    # ---------------- SEND ----------------
    def on_enter_pressed(self, event):
        self.send()

    def send(self):
        text = self.input_box.get().strip()
        if text == "":
            return

        self.input_box.delete(0, "end")

        # user message
        self.add_message(text, is_user=True)

        # typing indicator
        thinking_container = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        thinking_container.pack(fill="x", pady=6)

        thinking_label = ctk.CTkLabel(
            thinking_container,
            text="Thinking...",
            text_color="#94a3b8",
            font=("Helvetica", 12, "italic"),
        )
        thinking_label.pack(anchor="w", padx=15)

        self.chat_frame.update()

        # AI response
        reply = ask_ai(self.user_id, text)

        # remove typing
        thinking_container.destroy()

        # show reply
        self.add_message(reply, is_user=False)

        # update counter
        self.prompt_label.configure(text=self.get_prompt_text())