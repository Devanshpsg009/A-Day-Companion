import sys, subprocess, importlib.util, os, shutil
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except: pass

PACKAGES = {"customtkinter": "customtkinter", "Pillow": "PIL", "bcrypt": "bcrypt", "python-dotenv": "dotenv", "groq": "groq", "pygame": "pygame", "matplotlib": "matplotlib", "plyer": "plyer", "pystray": "pystray", "pyotp": "pyotp", "qrcode": "qrcode"}

def missing_packages():
    return [p for p, i in PACKAGES.items() if importlib.util.find_spec(i) is None]

def installer(pkgs):
    import tkinter as tk
    from tkinter import ttk, messagebox
    root = tk.Tk(); root.title("Setting up"); root.geometry("420x200"); root.resizable(False, False)
    tk.Label(root, text="Setting up A Day Companion", font=("Helvetica", 16, "bold")).pack(pady=10)
    status = tk.Label(root, text="Preparing installation..."); status.pack(pady=5)
    bar = ttk.Progressbar(root, length=320, mode="determinate"); bar.pack(pady=15)
    root.update()

    for i, pkg in enumerate(pkgs, 1):
        status.config(text=f"Installing {pkg}..."); root.update()
        try: subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            messagebox.showerror("Setup Failed", f"Could not install {pkg}. Check your internet connection or Use Python 3.12.")
            root.destroy(); sys.exit(1)
        bar["value"] = i * (100 // len(pkgs)); root.update()

    status.config(text="Setup complete. Restarting..."); bar["value"] = 100; root.update()
    root.after(1500, root.destroy); root.mainloop()

def run():
    if pkgs := missing_packages():
        installer(pkgs); subprocess.call([sys.executable] + sys.argv); sys.exit()
    from backend.database import has_users
    from ui.login import LoginApp
    from ui.welcome import App
    (LoginApp() if has_users() else App()).mainloop()
    cleanup()
def cleanup():
        targets = ['backend', 'ui', '.']
        for target in targets:
            pycache_path = os.path.join(target, '__pycache__')
            if os.path.exists(pycache_path):
                try:
                    shutil.rmtree(pycache_path)
                except:
                    pass

if __name__ == "__main__":
    run()