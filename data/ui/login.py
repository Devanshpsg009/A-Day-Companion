
import customtkinter as ctk
import os
from tkinter import messagebox
from PIL import Image ,ImageTk
from backend.auth import authenticate_user ,update_password ,email_exists ,verify_totp


BASE_DIR =os.path.dirname (os.path.dirname (os.path.abspath (__file__ )))
ASSETS_DIR =os.path.join (BASE_DIR ,"assets")


ctk.set_appearance_mode ("dark")
ctk.set_default_color_theme ("dark-blue")

class LoginApp (ctk.CTk ):

    def __init__ (self ):
        super ().__init__ ()
        self.geometry ("900x600")
        self.title ("A Day Companion - Login")
        self.resizable (False ,False )


        self.setup_layout ()
        self.setup_image_frame ()
        self.setup_form_frame ()



        self.show_login_form ()

    def setup_layout (self ):
        self.grid_columnconfigure (0 ,weight =1 )
        self.grid_columnconfigure (1 ,weight =1 )
        self.grid_rowconfigure (0 ,weight =1 )

    def setup_image_frame (self ):
        self.image_frame =ctk.CTkFrame (self ,corner_radius =0 ,fg_color ="#000000")
        self.image_frame.grid (row =0 ,column =0 ,sticky ="nsew")


        img_loaded =False

        try :
            lsbg_path =os.path.join (ASSETS_DIR ,"lsbg.png")
            img =Image.open (lsbg_path )
            img =img.resize ((450 ,600 ),Image.Resampling.LANCZOS )

            tk_img =ImageTk.PhotoImage (img )
            import tkinter as tk
            label =tk.Label (self.image_frame ,image =tk_img ,bg ="#000000")
            label.image =tk_img
            label.place (x =0 ,y =0 ,relwidth =1 ,relheight =1 )
            img_loaded =True
        except Exception :
            pass


        if not img_loaded :
            ctk.CTkLabel (
            self.image_frame ,
            text ="A Day Companion",
            font =("Helvetica",30 ,"bold"),
            text_color ="white"
            ).place (relx =0.5 ,rely =0.5 ,anchor ="center")

    def setup_form_frame (self ):
        self.form_frame =ctk.CTkFrame (self ,corner_radius =0 ,fg_color ="#0f172a")
        self.form_frame.grid (row =0 ,column =1 ,sticky ="nsew")


        self.center_box =ctk.CTkFrame (self.form_frame ,fg_color ="transparent")
        self.center_box.place (relx =0.5 ,rely =0.5 ,anchor ="center")

    def show_login_form (self ):


        for widget in self.center_box.winfo_children ():
            widget.destroy ()


        ctk.CTkLabel (
        self.center_box ,

        text ="Welcome Back",
        font =("Helvetica",32 ,"bold"),
        text_color ="white"
        ).pack (pady =(0 ,10 ))


        ctk.CTkLabel (
        self.center_box ,
        text ="Please sign in to continue",
        font =("Helvetica",14 ),
        text_color ="#94a3b8"
        ).pack (pady =(0 ,30 ))


        self.email_entry =ctk.CTkEntry (
        self.center_box ,
        width =300 ,
        height =50 ,
        placeholder_text ="Email Address",
        fg_color ="#1e293b",
        border_color ="#334155",
        text_color ="white"
        )
        self.email_entry.pack (pady =10 )


        pass_frame =ctk.CTkFrame (self.center_box ,fg_color ="transparent")
        pass_frame.pack (pady =10 )

        self.password_entry =ctk.CTkEntry (
        pass_frame ,
        width =220 ,
        height =50 ,
        placeholder_text ="Password",
        show ="*",
        fg_color ="#1e293b",
        border_color ="#334155",
        text_color ="white"
        )
        self.password_entry.pack (side ="left",padx =(0 ,10 ))

        self.toggle_btn =ctk.CTkButton (
        pass_frame ,
        text ="SHOW",
        width =70 ,
        height =50 ,
        fg_color ="#1e293b",
        hover_color ="#334155",
        border_color ="#334155",
        border_width =2 ,
        command =self.toggle_pwd
        )
        self.toggle_btn.pack (side ="left")


        ctk.CTkButton (
        self.center_box ,
        text ="Forgot Password?",
        fg_color ="transparent",
        text_color ="#94a3b8",
        hover_color ="#0f172a",
        command =self.show_forgot_form
        ).pack (pady =(0 ,10 ))


        ctk.CTkButton (
        self.center_box ,
        text ="Login",
        width =300 ,
        height =50 ,
        fg_color ="#3b82f6",
        hover_color ="#2563eb",
        font =("Helvetica",15 ,"bold"),
        command =self.login_action
        ).pack (pady =10 )


        footer =ctk.CTkFrame (self.center_box ,fg_color ="transparent")
        footer.pack (pady =20 )

        ctk.CTkLabel (footer ,text ="Don't have an account?",text_color ="#94a3b8").pack (side ="left")
        ctk.CTkButton (
        footer ,
        text ="Sign Up",
        width =60 ,
        fg_color ="transparent",
        text_color ="#38bdf8",
        hover_color ="#1e293b",
        command =self.signup_action
        ).pack (side ="left")

    def show_forgot_form (self ):

        for widget in self.center_box.winfo_children ():
            widget.destroy ()


        ctk.CTkLabel (

        self.center_box ,
        text ="Reset Password",
        font =("Helvetica",28 ,"bold"),
        text_color ="white"
        ).pack (pady =(0 ,10 ))


        self.reset_email_entry =ctk.CTkEntry (
        self.center_box ,
        width =300 ,
        height =50 ,
        placeholder_text ="Enter your email",
        fg_color ="#1e293b",
        text_color ="white"
        )
        self.reset_email_entry.pack (pady =10 )


        ctk.CTkButton (
        self.center_box ,
        text ="Verify Authenticator",
        width =300 ,
        height =50 ,
        fg_color ="#3b82f6",
        command =self.action_verify_user
        ).pack (pady =20 )


        ctk.CTkButton (
        self.center_box ,
        text ="Back to Login",
        fg_color ="transparent",
        text_color ="#94a3b8",
        command =self.show_login_form
        ).pack ()

    def show_new_password_form (self ):

        for widget in self.center_box.winfo_children ():
            widget.destroy ()



        ctk.CTkLabel (
        self.center_box ,
        text ="New Password",
        font =("Helvetica",28 ,"bold"),
        text_color ="white"
        ).pack (pady =(0 ,10 ))


        new_pass_frame =ctk.CTkFrame (self.center_box ,fg_color ="transparent")
        new_pass_frame.pack (pady =10 )

        self.new_pass_entry =ctk.CTkEntry (
        new_pass_frame ,
        width =220 ,
        height =50 ,
        placeholder_text ="New Password",
        show ="*",
        fg_color ="#1e293b",
        border_color ="#334155",
        text_color ="white"
        )
        self.new_pass_entry.pack (side ="left",padx =(0 ,10 ))

        self.new_toggle_btn =ctk.CTkButton (
        new_pass_frame ,
        text ="SHOW",
        width =70 ,
        height =50 ,
        fg_color ="#1e293b",
        hover_color ="#334155",
        border_color ="#334155",
        border_width =2 ,
        command =self.toggle_new_pwd
        )
        self.new_toggle_btn.pack (side ="left")


        ctk.CTkButton (
        self.center_box ,
        text ="Update Password",
        width =300 ,
        height =50 ,
        fg_color ="#3b82f6",
        command =self.action_update_password
        ).pack (pady =20 )

    def action_verify_user (self ):
        email =self.reset_email_entry.get ().strip ()


        if not email_exists (email ):

            return messagebox.showerror ("Error","Email not registered.")


        code =ctk.CTkInputDialog (text ="Enter 6-digit code:",title ="Security Check").get_input ()
        if code :

            if verify_totp (email ,code ):
                self.reset_email =email
                self.show_new_password_form ()
            else :
                messagebox.showerror ("Error","Invalid Code.")

    def toggle_new_pwd (self ):
        show =""if self.new_pass_entry.cget ("show")=="*"else "*"
        self.new_pass_entry.configure (show =show )
        self.new_toggle_btn.configure (text ="HIDE"if show ==""else "SHOW")


    def action_update_password (self ):
        new_pass =self.new_pass_entry.get ().strip ()



        if len (new_pass )<4 :
            return messagebox.showerror ("Error","Password too short")


        if update_password (self.reset_email ,new_pass ):
            messagebox.showinfo ("Success","Password updated!")
            self.show_login_form ()
        else :
            messagebox.showerror ("Error","Update failed.")

    def toggle_pwd (self ):
        show =""if self.password_entry.cget ("show")=="*"else "*"

        self.password_entry.configure (show =show )
        self.toggle_btn.configure (text ="HIDE"if show ==""else "SHOW")

    def login_action (self ):

        from backend.database import get_user_id
        from ui.dashboard import DashboardApp

        email =self.email_entry.get ()
        pwd =self.password_entry.get ()


        if authenticate_user (email ,pwd ):
            uid =get_user_id (email )
            self.destroy ()
            DashboardApp (uid ).mainloop ()
        else :
            messagebox.showerror ("Login Failed","Invalid credentials")


    def signup_action (self ):
        from ui.signup import SignupApp
        self.destroy ()
        SignupApp ().mainloop ()

if __name__ =="__main__":
    LoginApp ().mainloop ()