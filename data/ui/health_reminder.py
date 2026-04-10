import customtkinter as ctk 
from PIL import Image ,ImageTk 
import os 

BASE_DIR =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))
ASSETS_DIR =os .path .join (BASE_DIR ,"assets")

class AnimatedGifLabel (ctk .CTkLabel ):
    """A custom label that displays an animated GIF."""

    def __init__ (self ,master ,gif_path ,size =(180 ,180 ),**kwargs ):
        super ().__init__ (master ,text ="",**kwargs )
        self .frames =[]
        self .delay =100 
        self .current_frame =0 

        try :

            img =Image .open (gif_path )

            if 'duration'in img .info and img .info ['duration']>0 :
                self .delay =img .info ['duration']


            for i in range (img .n_frames ):
                img .seek (i )
                frame_image =img .copy ().convert ("RGBA").resize (size ,Image .Resampling .LANCZOS )
                ctk_frame =ctk .CTkImage (light_image =frame_image ,dark_image =frame_image ,size =size )
                if ctk_frame :
                    self .frames .append (ctk_frame )


            if self .frames :
                self .configure (image =self .frames [0 ])
                self .animate ()
        except Exception :

            pass 

    def animate (self ):
        """Animate the GIF by cycling through frames."""
        if not self .winfo_exists ()or not self .frames :
            return 

        self .current_frame =(self .current_frame +1 )%len (self .frames )
        self .configure (image =self .frames [self .current_frame ])

        self .after (self .delay ,self .animate )

class HealthReminderApp (ctk .CTkToplevel ):
    """Main class for the Health Tracker application."""

    def __init__ (self ,master =None ):
        super ().__init__ (master )
        self .title ("Health Tracker Settings")
        self .geometry ("450x450")


        self .running =False 
        self .time_elapsed =0 


        self .create_timer_display ()
        self .create_settings_frame ()
        self .create_button_frame ()


        self .protocol ("WM_DELETE_WINDOW",self .hide_window )
        self .withdraw ()
        self .start_tracking ()

    def create_timer_display (self ):
        """Create the timer display label."""
        self .time_lbl =ctk .CTkLabel (self ,text ="00:00:00",font =("Arial",40 ,"bold"))
        self .time_lbl .pack (pady =30 )

    def create_settings_frame (self ):
        """Create the settings frame with input fields."""
        self .settings_frame =ctk .CTkFrame (self )
        self .settings_frame .pack (pady =10 ,padx =20 ,fill ="x")


        ctk .CTkLabel (self .settings_frame ,text ="Water Interval (mins):").grid (row =0 ,column =0 ,padx =10 ,pady =10 )
        self .water_entry =ctk .CTkEntry (self .settings_frame ,width =60 )
        self .water_entry .insert (0 ,"60")
        self .water_entry .grid (row =0 ,column =1 ,padx =10 ,pady =10 )


        ctk .CTkLabel (self .settings_frame ,text ="Exercise Interval (mins):").grid (row =1 ,column =0 ,padx =10 ,pady =10 )
        self .exercise_entry =ctk .CTkEntry (self .settings_frame ,width =60 )
        self .exercise_entry .insert (0 ,"120")
        self .exercise_entry .grid (row =1 ,column =1 ,padx =10 ,pady =10 )

    def create_button_frame (self ):
        """Create the button frame with the start button."""
        self .btn_frame =ctk .CTkFrame (self ,fg_color ="transparent")
        self .btn_frame .pack (pady =20 )

        self .start_btn =ctk .CTkButton (self .btn_frame ,text ="Apply & Restart Timer",command =self .start_tracking )
        self .start_btn .pack (side ="left",padx =10 )

    def hide_window (self ):
        """Hide the window instead of closing it."""
        self .withdraw ()

    def show_window (self ):
        """Show the window and bring it to front."""
        self .deiconify ()
        self .lift ()

    def start_tracking (self ):
        """Start or restart the health tracking timer."""
        try :

            self .water_sec =int (self .water_entry .get ())*60 
            self .exercise_sec =int (self .exercise_entry .get ())*60 
        except ValueError :

            return 


        self .time_elapsed =0 
        if not self .running :
            self .running =True 
            self .update_timer ()

    def update_timer (self ):
        """Update the timer display and check for reminders."""
        if not self .running :
            return 


        self .time_elapsed +=1 


        hours ,remainder =divmod (self .time_elapsed ,3600 )
        minutes ,seconds =divmod (remainder ,60 )
        time_str =f"{hours :02d}:{minutes :02d}:{seconds :02d}"
        self .time_lbl .configure (text =time_str )


        if self .water_sec >0 and self .time_elapsed %self .water_sec ==0 :
            self .show_water_popup ()


        if self .exercise_sec >0 and self .time_elapsed %self .exercise_sec ==0 :
            self .show_exercise_popup ()


        self .after (1000 ,self .update_timer )

    def show_water_popup (self ):
        """Show the water reminder popup."""
        win =ctk .CTkToplevel (self )
        win .title ("Water Reminder")
        win .geometry ("350x400")
        win .attributes ("-topmost",True )


        ctk .CTkLabel (win ,text ="Time to drink water! 💧",font =("Arial",20 ,"bold")).pack (pady =20 )


        water_gif_path =os .path .join (ASSETS_DIR ,"water.gif")
        if os .path .exists (water_gif_path ):
            AnimatedGifLabel (win ,water_gif_path ,size =(200 ,200 )).pack (pady =10 )


        ctk .CTkButton (win ,text ="Hydrated",command =win .destroy ).pack (pady =20 )

    def show_exercise_popup (self ):
        """Show the exercise reminder popup with stretches."""
        win =ctk .CTkToplevel (self )
        win .title ("Exercise Break")
        win .geometry ("450x650")
        win .attributes ("-topmost",True )


        scroll =ctk .CTkScrollableFrame (win )
        scroll .pack (fill ="both",expand =True ,padx =10 ,pady =10 )


        ctk .CTkLabel (scroll ,text ="Time for a Quick Stretch!",font =("Arial",20 ,"bold")).pack (pady =10 )


        eye_gif_path =os .path .join (ASSETS_DIR ,"eye.gif")
        if os .path .exists (eye_gif_path ):
            AnimatedGifLabel (scroll ,eye_gif_path ,size =(150 ,150 )).pack (pady =10 )
        ctk .CTkLabel (scroll ,text ="Gently blink your eyes 20 times.",font =("Arial",14 )).pack (pady =5 )


        neck_gif_path =os .path .join (ASSETS_DIR ,"neck.gif")
        if os .path .exists (neck_gif_path ):
            AnimatedGifLabel (scroll ,neck_gif_path ,size =(150 ,150 )).pack (pady =10 )
        ctk .CTkLabel (scroll ,text ="Gently roll your neck left and right.",font =("Arial",14 )).pack (pady =5 )


        spine_gif_path =os .path .join (ASSETS_DIR ,"spine.gif")
        if os .path .exists (spine_gif_path ):
            AnimatedGifLabel (scroll ,spine_gif_path ,size =(150 ,150 )).pack (pady =10 )
        ctk .CTkLabel (scroll ,text ="Sit straight and stretch your spine.",font =("Arial",14 )).pack (pady =5 )


        ctk .CTkButton (scroll ,text ="Finished",command =win .destroy ).pack (pady =20 )