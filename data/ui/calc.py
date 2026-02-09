import customtkinter as ctk
import math

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class CalculatorApp(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.geometry("450x650")
        self.title("Calculator")
        self.resizable(False, False)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)

        self.expr = ""
        self.history_text = ""
        
        self.history_label = ctk.CTkLabel(
            self, 
            text="", 
            font=("Consolas", 14), 
            text_color="gray", 
            anchor="e"
        )
        self.history_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="ew")

        self.display = ctk.CTkEntry(
            self, 
            font=("Roboto Medium", 40), 
            justify="right", 
            fg_color="#1a1a1a", 
            border_color="#333333",
            text_color="#00ffcc"
        )
        self.display.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew", ipady=15)
        self.display.configure(state="readonly")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=15, pady=10, sticky="nsew")

        buttons = [
            ('C', 0, 0, 'danger'), ('(', 0, 1, 'func'), (')', 0, 2, 'func'), ('⌫', 0, 3, 'danger'),
            ('sin', 1, 0, 'func'), ('cos', 1, 1, 'func'), ('tan', 1, 2, 'func'), ('/', 1, 3, 'op'),
            ('7', 2, 0, 'num'),    ('8', 2, 1, 'num'),   ('9', 2, 2, 'num'),   ('*', 2, 3, 'op'),
            ('4', 3, 0, 'num'),    ('5', 3, 1, 'num'),   ('6', 3, 2, 'num'),   ('-', 3, 3, 'op'),
            ('1', 4, 0, 'num'),    ('2', 4, 1, 'num'),   ('3', 4, 2, 'num'),   ('+', 4, 3, 'op'),
            ('0', 5, 0, 'num'),    ('.', 5, 1, 'num'),   ('π', 5, 2, 'func'),  ('=', 5, 3, 'action'),
        ]

        styles = {
            'num':    {"fg": "#2b2b2b", "hover": "#3a3a3a", "text": "white"},
            'op':     {"fg": "#ff9900", "hover": "#ffb84d", "text": "black"},
            'func':   {"fg": "#404040", "hover": "#505050", "text": "#00ffcc"},
            'danger': {"fg": "#cc3333", "hover": "#ff4d4d", "text": "white"},
            'action': {"fg": "#00cc66", "hover": "#00ff80", "text": "black"}
        }

        for i in range(4): btn_frame.grid_columnconfigure(i, weight=1)
        for i in range(6): btn_frame.grid_rowconfigure(i, weight=1)

        for text, r, c, style_key in buttons:
            style = styles[style_key]
            cmd = lambda t=text: self.click(t)

            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                font=("Arial", 20, "bold"),
                fg_color=style["fg"],
                hover_color=style["hover"],
                text_color=style["text"],
                corner_radius=8,
                height=65,
                command=cmd
            )
            
            if text == '0':
                btn.grid(row=r, column=c, columnspan=1, sticky="nsew", padx=3, pady=3)
            else:
                btn.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)

        self.bind("<Return>", lambda e: self.click("="))
        self.bind("<KP_Enter>", lambda e: self.click("="))
        self.bind("<Escape>", lambda e: self.click("C"))
        self.bind("<BackSpace>", lambda e: self.click("⌫"))
        
        for key in "0123456789+-*/.()":
            self.bind(key, lambda e, k=key: self.click(k))

    def click(self, val):
        if val == "C":
            self.expr = ""
            self.history_text = ""
        
        elif val == "⌫":
            self.expr = self.expr[:-1]
            
        elif val == "=":
            self.calculate()
            return
            
        elif val == "π":
            self.expr += "math.pi"
            
        elif val in ["sin", "cos", "tan"]:
            self.expr += f"math.{val}("
            
        elif val == "√":
            self.expr += "math.sqrt("
            
        else:
            self.expr += val
            
        self.update_display()

    def update_display(self):
        self.display.configure(state="normal")
        self.display.delete(0, "end")
        
        display_text = self.expr.replace("math.", "").replace("**", "^")
        self.display.insert(0, display_text)
        
        self.history_label.configure(text=self.history_text)
        self.display.configure(state="readonly")

    def calculate(self):
        try:
            if any(x in self.expr for x in ["import", "exec", "eval", "os", "sys"]):
                self.expr = ""
                self.display.configure(state="normal")
                self.display.delete(0, "end")
                self.display.insert(0, "Illegal Input")
                self.display.configure(state="readonly")
                return

            open_count = self.expr.count('(')
            close_count = self.expr.count(')')
            if open_count > close_count:
                self.expr += ')' * (open_count - close_count)

            val = eval(self.expr, {"__builtins__": None}, {"math": math, "abs": abs})
            
            if isinstance(val, float):
                val = round(val, 12)
            
            result = str(val)
            
            if result.endswith(".0"):
                result = result[:-2]
                
            display_expr = self.expr.replace("math.", "")
            self.history_text = f"{display_expr} ="
            
            self.expr = result
            self.update_display()
            
        except ZeroDivisionError:
            self.expr = ""
            self.display.configure(state="normal")
            self.display.delete(0, "end")
            self.display.insert(0, "Don't divide by zero")
            self.display.configure(state="readonly")
        except Exception:
            self.display.configure(state="normal")
            self.display.delete(0, "end")
            self.display.insert(0, "Error")
            self.display.configure(state="readonly")
            self.expr = ""