import sys 
import subprocess 
import importlib .util 
import os 
import shutil 

BASE_DIR =os .path .dirname (os .path .abspath (__file__ ))
os .chdir (BASE_DIR )
sys .path .insert (0 ,BASE_DIR )

try :
    from ctypes import windll 
    windll .shcore .SetProcessDpiAwareness (1 )
except Exception :
    pass 

PACKAGES ={
"customtkinter":"customtkinter",
"Pillow":"PIL",
"bcrypt":"bcrypt",
"python-dotenv":"dotenv",
"openai":"openai",
"pygame":"pygame",
"matplotlib":"matplotlib",
"plyer":"plyer",
"pystray":"pystray",
"pyotp":"pyotp",
"qrcode":"qrcode",
"chess":"chess",
}


def missing_packages ():
    """Return a list of packages that are not installed."""
    missing =[]
    for package_name ,import_name in PACKAGES .items ():
        if importlib .util .find_spec (import_name )is None :
            missing .append (package_name )
    return missing 


def install_packages (packages ):
    """Install missing Python packages before launching the app."""
    import tkinter as tk 
    from tkinter import ttk ,messagebox 

    root =tk .Tk ()
    root .title ("Setting up")
    root .geometry ("420x200")
    root .resizable (False ,False )

    tk .Label (root ,text ="Setting up A Day Companion",font =("Helvetica",16 ,"bold")).pack (pady =10 )
    status_label =tk .Label (root ,text ="Preparing installation...")
    status_label .pack (pady =5 )
    progress_bar =ttk .Progressbar (root ,length =320 ,mode ="determinate")
    progress_bar .pack (pady =15 )
    root .update ()

    total_packages =len (packages )
    for index ,package_name in enumerate (packages ,start =1 ):
        status_label .config (text =f"Installing {package_name }...")
        root .update ()

        try :
            subprocess .check_call (
            [
            sys .executable ,
            "-m",
            "pip",
            "install",
            "--user",
            "--break-system-packages",
            package_name ,
            ],
            stdout =subprocess .DEVNULL ,
            stderr =subprocess .DEVNULL ,
            )
        except subprocess .CalledProcessError :
            messagebox .showerror (
            "Setup Failed",
            f"Could not install {package_name }. Check your internet connection or use Python 3.12.",
            )
            root .destroy ()
            sys .exit (1 )

        progress_bar ["value"]=int (index *100 /total_packages )
        root .update ()

    status_label .config (text ="Setup complete. Restarting...")
    progress_bar ["value"]=100 
    root .update ()
    root .after (1500 ,root .destroy )
    root .mainloop ()


def cleanup_pycache ():
    """Remove temporary __pycache__ folders after the app closes."""
    folders =["backend","ui","."]
    for folder_name in folders :
        pycache_path =os .path .join (folder_name ,"__pycache__")
        if os .path .exists (pycache_path ):
            try :
                shutil .rmtree (pycache_path )
            except Exception :
                pass 


def run_app ():
    """Start the app after installing missing packages."""
    packages =missing_packages ()
    if packages :
        install_packages (packages )
        subprocess .call ([sys .executable ]+sys .argv )
        sys .exit ()

    from backend .database import has_users 
    from ui .login import LoginApp 
    from ui .welcome import App 

    if has_users ():
        app =LoginApp ()
    else :
        app =App ()

    app .mainloop ()
    cleanup_pycache ()


if __name__ =="__main__":
    run_app ()
