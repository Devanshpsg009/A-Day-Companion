import sys
import os
import subprocess
import importlib.util
import platform

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
os.chdir(script_dir)

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

PACKAGES = {
    "customtkinter": "customtkinter",
    "Pillow": "PIL",
    "bcrypt": "bcrypt",
    "python-dotenv": "dotenv",
    "groq": "groq",
    "pygame": "pygame",
    "matplotlib": "matplotlib",
    "plyer": "plyer",
    "pystray": "pystray"
}

def missing_packages():
    missing = []
    for pip_name, import_name in PACKAGES.items():
        if importlib.util.find_spec(import_name) is None:
            missing.append(pip_name)
    return missing

def installer(pkgs):
    import tkinter as tk
    from tkinter import ttk, messagebox

    root = tk.Tk()
    root.title("Setting up for first use")
    root.geometry("420x200")
    root.resizable(False, False)

    tk.Label(root, text="Setting up A Day Companion", font=("Helvetica", 16, "bold")).pack(pady=10)
    status = tk.Label(root, text="Preparing installation...")
    status.pack(pady=5)

    bar = ttk.Progressbar(root, length=320, mode="determinate")
    bar.pack(pady=15)

    step = 100 // len(pkgs)
    root.update()

    for i, pkg in enumerate(pkgs, 1):
        status.config(text=f"Installing {pkg}...")
        root.update()
        cmd = [sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", pkg]
       
        try:
            subprocess.check_call(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            messagebox.showerror(
                "Setup Failed",
                f"Could not install {pkg}.\n\nPlease check your internet connection."
            )
            root.destroy()
            sys.exit(1)

        bar["value"] = i * step
        root.update()

    bar["value"] = 100
    status.config(text="Setup complete. Restarting...")
    root.update()
    root.after(1500, root.destroy)
    root.mainloop()

def run():
    pkgs = missing_packages()
    if pkgs:
        installer(pkgs)
        subprocess.call([sys.executable, os.path.abspath(__file__)] + sys.argv[1:])
        sys.exit()
    from backend.database import has_users
    from ui.login import LoginApp
    from ui.welcome import App

    if has_users():
        LoginApp().mainloop()
    else:
        App().mainloop()

if __name__ == "__main__":
    run()
