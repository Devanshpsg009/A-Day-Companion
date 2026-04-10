import customtkinter as ctk 
import os 
import re 
import webbrowser 
import qrcode 
import pyotp 
from tkinter import messagebox 
from PIL import Image ,ImageTk 
from backend .auth import create_user 
from backend .database import create_users_table 

BASE_DIR =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))
ASSETS_DIR =os .path .join (BASE_DIR ,"assets")


ctk .set_appearance_mode ("dark")
ctk .set_default_color_theme ("dark-blue")

class SignupApp (ctk .CTk ):
    """Main class for the Signup application."""

    def __init__ (self ):
        super ().__init__ ()
        self .geometry ("900x600")
        self .title ("A Day Companion - Sign Up")
        self .resizable (False ,False )


        self .setup_layout ()
        self .setup_image_frame ()
        self .setup_form_frame ()
        self .show_signup_form ()

    def setup_layout (self ):
        """Set up the main window grid layout."""
        self .grid_columnconfigure (0 ,weight =1 )
        self .grid_columnconfigure (1 ,weight =1 )
        self .grid_rowconfigure (0 ,weight =1 )

    def setup_image_frame (self ):
        """Set up the left image frame."""
        self .image_frame =ctk .CTkFrame (self ,corner_radius =0 ,fg_color ="#000000")
        self .image_frame .grid (row =0 ,column =0 ,sticky ="nsew")


        img_loaded =False 
        try :
            lsbg_path =os .path .join (ASSETS_DIR ,"lsbg.png")
            img =Image .open (lsbg_path )
            img =img .resize ((450 ,600 ),Image .Resampling .LANCZOS )
            tk_img =ImageTk .PhotoImage (img )
            import tkinter as tk 
            label =tk .Label (self .image_frame ,image =tk_img ,bg ="#000000")
            label .image =tk_img 
            label .place (x =0 ,y =0 ,relwidth =1 ,relheight =1 )
            img_loaded =True 
        except Exception :
            pass 


        if not img_loaded :
            ctk .CTkLabel (
            self .image_frame ,
            text ="Join Us",
            font =("Helvetica",30 ),
            text_color ="white"
            ).place (relx =0.5 ,rely =0.5 ,anchor ="center")

    def setup_form_frame (self ):
        """Set up the right form frame."""
        self .form_frame =ctk .CTkFrame (self ,corner_radius =0 ,fg_color ="#0f172a")
        self .form_frame .grid (row =0 ,column =1 ,sticky ="nsew")


        self .center_box =ctk .CTkFrame (self .form_frame ,fg_color ="transparent")
        self .center_box .place (relx =0.5 ,rely =0.5 ,anchor ="center")

    def show_signup_form (self ):
        """Display the signup form."""

        for widget in self .center_box .winfo_children ():
            widget .destroy ()


        ctk .CTkLabel (
        self .center_box ,
        text ="Create Account",
        font =("Helvetica",32 ,"bold"),
        text_color ="white"
        ).pack (pady =(0 ,10 ))


        self .email_entry =ctk .CTkEntry (
        self .center_box ,
        width =300 ,
        height =50 ,
        placeholder_text ="Email Address",
        fg_color ="#1e293b",
        text_color ="white"
        )
        self .email_entry .pack (pady =10 )


        pass_frame =ctk .CTkFrame (self .center_box ,fg_color ="transparent")
        pass_frame .pack (pady =10 )

        self .password_entry =ctk .CTkEntry (
        pass_frame ,
        width =220 ,
        height =50 ,
        placeholder_text ="Password",
        show ="*",
        fg_color ="#1e293b",
        text_color ="white"
        )
        self .password_entry .pack (side ="left",padx =(0 ,10 ))

        self .toggle_btn =ctk .CTkButton (
        pass_frame ,
        text ="SHOW",
        width =70 ,
        height =50 ,
        fg_color ="#1e293b",
        border_width =2 ,
        command =self .toggle_pwd 
        )
        self .toggle_btn .pack (side ="left")


        ctk .CTkButton (
        self .center_box ,
        text ="Create Account",
        width =300 ,
        height =50 ,
        fg_color ="#3b82f6",
        font =("Helvetica",15 ,"bold"),
        command =self .signup_action 
        ).pack (pady =20 )


        footer =ctk .CTkFrame (self .center_box ,fg_color ="transparent")
        footer .pack (pady =10 )

        ctk .CTkLabel (footer ,text ="Already a member?",text_color ="#94a3b8").pack (side ="left")
        ctk .CTkButton (
        footer ,
        text ="Login",
        width =60 ,
        fg_color ="transparent",
        text_color ="#38bdf8",
        command =self .login_action 
        ).pack (side ="left")

    def toggle_pwd (self ):
        """Toggle visibility of the password field."""
        show =""if self .password_entry .cget ("show")=="*"else "*"
        self .password_entry .configure (show =show )
        self .toggle_btn .configure (text ="HIDE"if show ==""else "SHOW")

    def signup_action (self ):
        """Handle the signup action."""
        email =self .email_entry .get ()
        pwd =self .password_entry .get ()


        if not email or not pwd :
            return messagebox .showerror ("Error","All fields required")

        if not re .match (r"[^@]+@[^@]+\.[^@]+",email ):
            return messagebox .showerror ("Error","Invalid email")


        create_users_table ()


        secret_key =create_user (email ,pwd )
        if secret_key :

            self .show_qr_popup (email ,secret_key )
        else :
            messagebox .showerror ("Error","User already exists")

    def show_qr_popup (self ,email ,secret ):
        """Display the QR code popup for 2FA setup."""
        qr_path ="temp_qr.png"


        totp =pyotp .TOTP (secret )
        uri =totp .provisioning_uri (name =email ,issuer_name ="A Day Companion")
        qrcode .make (uri ).save (qr_path )


        top =ctk .CTkToplevel (self )
        top .geometry ("400x550")
        top .title ("Setup 2FA Recovery")
        top .attributes ("-topmost",True )
        top .resizable (False ,False )


        ctk .CTkLabel (
        top ,
        text ="Scan with Google Authenticator",
        font =("Helvetica",18 ,"bold")
        ).pack (pady =20 )


        try :
            img =Image .open (qr_path )
            img =img .resize ((250 ,250 ),Image .Resampling .LANCZOS )
            tk_img =ImageTk .PhotoImage (img )
            import tkinter as tk 
            label =tk .Label (top ,image =tk_img ,bg ="#0f172a")
            label .image =tk_img 
            label .pack (pady =10 )
        except :
            ctk .CTkLabel (top ,text ="[QR Code Error]").pack ()


        ctk .CTkLabel (
        top ,
        text ="This is your Recovery Key for password resets.",
        text_color ="gray"
        ).pack (pady =10 )


        def close_and_login ():
            if os .path .exists (qr_path ):
                os .remove (qr_path )
            top .destroy ()
            self .login_action ()

        ctk .CTkButton (
        top ,
        text ="I Scanned It -> Login",
        command =close_and_login ,
        fg_color ="#22c55e"
        ).pack (pady =20 )

    def login_action (self ):
        """Switch to the login screen."""
        from ui .login import LoginApp 
        self .destroy ()
        LoginApp ().mainloop ()

if __name__ =="__main__":
    SignupApp ().mainloop ()