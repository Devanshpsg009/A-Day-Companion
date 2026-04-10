import customtkinter as ctk 
from PIL import Image ,ImageTk 
import os 

BASE_DIR =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))
ASSETS_DIR =os .path .join (BASE_DIR ,"assets")


ctk .set_appearance_mode ("dark")
ctk .set_default_color_theme ("dark-blue")


PAGES =[
{
"title":"Welcome",
"text":"Your intelligent daily companion for focus, balance, and productivity."
},
{
"title":"What is A Day Companion?",
"text":"A smart productivity system that helps you plan better, work deeper, and live calmer."
},
{
"title":"How It Helps",
"text":"> Smart task prioritization\n> Habit building & consistency\n> Focus & distraction tracking\n> Personalized AI suggestions"
},
{
"title":"Did You Know?",
"text":"> 2 in 3 students experience academic stress\n\n> Poor sleep reduces motivation by 40%\n\n> Time mismanagement is the #1 productivity killer"
},
{
"title":"Ready to Begin?",
"text":"Let's build a calmer, more productive routine - one day at a time.",
"final":True 
}
]

class App (ctk .CTk ):
    """Main class for the Welcome/Onboarding application."""

    def __init__ (self ):
        super ().__init__ ()
        self .geometry ("1200x600")
        self .title ("A Day Companion")
        self .configure (fg_color ="#0b132b")


        self .idx =0 
        self .frames =[]


        self .setup_sidebar ()
        self .setup_content_area ()
        self .create_pages ()


        self .bind ("<Right>",lambda e :self .next_page ())
        self .bind ("<Left>",lambda e :self .prev_page ())


        self .show_page ()

    def setup_sidebar (self ):
        """Set up the left sidebar with logo and title."""
        sidebar =ctk .CTkFrame (self ,fg_color ="#0a1128",width =420 )
        sidebar .pack (side ="left",fill ="y")
        sidebar .pack_propagate (False )


        try :
            logo_path =os .path .join (ASSETS_DIR ,"logo.png")
            img =Image .open (logo_path )
            img =img .resize ((240 ,240 ),Image .Resampling .LANCZOS )
            tk_img =ImageTk .PhotoImage (img )
            import tkinter as tk 
            label =tk .Label (sidebar ,image =tk_img ,bg ="#0a1128")
            label .image =tk_img 
            label .pack (pady =(90 ,25 ))
        except Exception :
            pass 


        ctk .CTkLabel (
        sidebar ,
        text ="Boost your productivity\n",
        font =("Helvetica",28 ,"bold"),
        text_color ="white"
        ).pack (padx =20 )

    def setup_content_area (self ):
        """Set up the main content area."""
        self .content =ctk .CTkFrame (
        self ,
        fg_color ="#1c2541",
        border_color ="#5bc0be",
        border_width =2 ,
        corner_radius =36 
        )
        self .content .pack (side ="right",expand =True ,fill ="both",padx =40 ,pady =40 )

    def create_pages (self ):
        """Create all the welcome tour pages."""
        for i ,page_data in enumerate (PAGES ):

            page_frame =ctk .CTkFrame (self .content ,fg_color ="transparent")
            self .frames .append (page_frame )


            inner =ctk .CTkFrame (page_frame ,fg_color ="transparent")
            inner .place (relx =0.5 ,rely =0.45 ,anchor ="center")


            ctk .CTkLabel (
            inner ,
            text =page_data ["title"],
            font =("Helvetica",36 ,"bold"),
            text_color ="white"
            ).pack (pady =(0 ,24 ))


            ctk .CTkLabel (
            inner ,
            text =page_data ["text"],
            font =("Helvetica",18 ),
            text_color ="#eaeaea",
            wraplength =520 
            ).pack (pady =(0 ,50 ))


            btns =ctk .CTkFrame (inner ,fg_color ="transparent")
            btns .pack ()


            if page_data .get ("final"):

                ctk .CTkButton (
                btns ,
                text ="Get Started",
                width =180 ,
                height =52 ,
                font =("Helvetica",16 ,"bold"),
                corner_radius =26 ,
                fg_color ="#3a86ff",
                hover_color ="#5fa8ff",
                command =self .open_signup 
                ).pack (side ="left",padx =12 )

                ctk .CTkButton (
                btns ,
                text ="I already have an account",
                width =220 ,
                height =52 ,
                fg_color ="transparent",
                border_width =2 ,
                border_color ="#9bbcd1",
                text_color ="#9bbcd1",
                hover_color ="#2b3a67",
                command =self .open_login 
                ).pack (side ="left",padx =12 )
            else :

                if i >0 :
                    ctk .CTkButton (
                    btns ,
                    text ="Back",
                    width =120 ,
                    height =48 ,
                    fg_color ="#2b3a67",
                    hover_color ="#3a86ff",
                    corner_radius =22 ,
                    command =self .prev_page 
                    ).pack (side ="left",padx =12 )

                ctk .CTkButton (
                btns ,
                text ="Next",
                width =120 ,
                height =48 ,
                fg_color ="#3a86ff",
                hover_color ="#5fa8ff",
                corner_radius =22 ,
                command =self .next_page 
                ).pack (side ="left",padx =12 )


            dots =ctk .CTkFrame (inner ,fg_color ="transparent")
            dots .pack (pady =(30 ,0 ))

            for j in range (len (PAGES )):

                dot_color ="#3a86ff"if j ==i else "#9bbcd1"
                ctk .CTkLabel (
                dots ,
                text ="*",
                font =("Helvetica",48 ),
                text_color =dot_color 
                ).pack (side ="left",padx =6 )

    def show_page (self ):
        """Display the current page."""

        for frame in self .frames :
            frame .pack_forget ()


        self .frames [self .idx ].pack (fill ="both",expand =True )

    def next_page (self ):
        """Navigate to the next page."""
        if self .idx <len (PAGES )-1 :
            self .idx +=1 
            self .show_page ()

    def prev_page (self ):
        """Navigate to the previous page."""
        if self .idx >0 :
            self .idx -=1 
            self .show_page ()

    def open_signup (self ):
        """Open the signup screen."""
        from ui .signup import SignupApp 
        self .destroy ()
        SignupApp ().mainloop ()

    def open_login (self ):
        """Open the login screen."""
        from ui .login import LoginApp 
        self .destroy ()
        LoginApp ().mainloop ()