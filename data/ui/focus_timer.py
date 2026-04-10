import customtkinter as ctk 
import datetime 
import os 
from tkinter import messagebox 
import pygame 

BASE_DIR =os .path .dirname (os .path .dirname (os .path .abspath (__file__ )))
ASSETS_DIR =os .path .join (BASE_DIR ,"assets")

class FocusTimerApp (ctk .CTkToplevel ):
    """Main class for the Focus Timer application with stopwatch, timer, and alarm features."""

    def __init__ (self ):
        super ().__init__ ()

        try :
            pygame .mixer .init ()
        except Exception :
            pass 


        self .geometry ("500x500")
        self .title ("Focus Timer")
        self .resizable (False ,False )


        self .tabs =ctk .CTkTabview (self )
        self .tabs .pack (expand =True ,fill ="both",padx =20 ,pady =20 )


        self .tabs .add ("Stopwatch")
        self .tabs .add ("Timer")
        self .tabs .add ("Alarm")


        self .build_stopwatch ()
        self .build_timer ()
        self .build_alarm ()

    def build_stopwatch (self ):
        """Build the stopwatch tab interface."""
        tab =self .tabs .tab ("Stopwatch")


        self .sw_seconds =0 
        self .sw_running =False 
        self .sw_after_id =None 


        self .sw_label =ctk .CTkLabel (tab ,text ="00:00:00",font =("Arial",50 ,"bold"))
        self .sw_label .pack (pady =40 )


        btn_frame =ctk .CTkFrame (tab ,fg_color ="transparent")
        btn_frame .pack ()


        self .sw_start_btn =ctk .CTkButton (btn_frame ,text ="Start",width =80 ,command =self .sw_start )
        self .sw_start_btn .pack (side ="left",padx =5 )

        ctk .CTkButton (btn_frame ,text ="Pause",width =80 ,command =self .sw_pause ).pack (side ="left",padx =5 )
        ctk .CTkButton (btn_frame ,text ="Reset",width =80 ,fg_color ="#C0392B",hover_color ="#A93226",command =self .sw_reset ).pack (side ="left",padx =5 )

    def sw_start (self ):
        """Start or resume the stopwatch."""
        if not self .sw_running :
            self .sw_running =True 
            self .sw_start_btn .configure (text ="Resume")

            self .sw_after_id =self .after (1000 ,self .update_sw )

    def sw_pause (self ):
        """Pause the stopwatch."""
        self .sw_running =False 
        if getattr (self ,"sw_after_id",None ):
            self .after_cancel (self .sw_after_id )
            self .sw_after_id =None 

    def sw_reset (self ):
        """Reset the stopwatch to zero."""
        self .sw_running =False 
        if getattr (self ,"sw_after_id",None ):
            self .after_cancel (self .sw_after_id )
            self .sw_after_id =None 


        self .sw_seconds =0 
        self .sw_label .configure (text ="00:00:00")
        self .sw_start_btn .configure (text ="Start")

    def update_sw (self ):
        """Update the stopwatch display every second."""
        if not self .winfo_exists ():
            return 

        if self .sw_running :
            self .sw_seconds +=1 

            hours =self .sw_seconds //3600 
            minutes =(self .sw_seconds %3600 )//60 
            seconds =self .sw_seconds %60 
            time_str =f"{hours :02}:{minutes :02}:{seconds :02}"
            self .sw_label .configure (text =time_str )


            self .sw_after_id =self .after (1000 ,self .update_sw )

    def build_timer (self ):
        """Build the countdown timer tab interface."""
        tab =self .tabs .tab ("Timer")


        self .timer_running =False 
        self .timer_total =0 
        self .timer_after_id =None 


        input_frame =ctk .CTkFrame (tab ,fg_color ="transparent")
        input_frame .pack (pady =20 )


        self .t_hr =ctk .CTkEntry (input_frame ,width =50 ,placeholder_text ="00",justify ="center")
        self .t_min =ctk .CTkEntry (input_frame ,width =50 ,placeholder_text ="00",justify ="center")
        self .t_sec =ctk .CTkEntry (input_frame ,width =50 ,placeholder_text ="00",justify ="center")


        self .t_hr .pack (side ="left",padx =5 )
        ctk .CTkLabel (input_frame ,text =":").pack (side ="left")
        self .t_min .pack (side ="left",padx =5 )
        ctk .CTkLabel (input_frame ,text =":").pack (side ="left")
        self .t_sec .pack (side ="left",padx =5 )


        self .timer_label =ctk .CTkLabel (tab ,text ="00:00:00",font =("Arial",50 ,"bold"))
        self .timer_label .pack (pady =20 )


        btn_frame =ctk .CTkFrame (tab ,fg_color ="transparent")
        btn_frame .pack ()


        self .timer_start_btn =ctk .CTkButton (btn_frame ,text ="Start",width =80 ,command =self .timer_start )
        self .timer_start_btn .pack (side ="left",padx =5 )

        ctk .CTkButton (btn_frame ,text ="Pause",width =80 ,command =self .timer_pause ).pack (side ="left",padx =5 )
        ctk .CTkButton (btn_frame ,text ="Reset",width =80 ,fg_color ="#C0392B",hover_color ="#A93226",command =self .timer_reset ).pack (side ="left",padx =5 )

    def timer_start (self ):
        """Start or resume the countdown timer."""
        if not self .timer_running :
            try :

                if self .timer_total ==0 :
                    hours =int (self .t_hr .get ()or 0 )
                    minutes =int (self .t_min .get ()or 0 )
                    seconds =int (self .t_sec .get ()or 0 )
                    self .timer_total =hours *3600 +minutes *60 +seconds 


                if self .timer_total >0 :
                    self .timer_running =True 
                    self .timer_start_btn .configure (text ="Resume")

                    self .timer_after_id =self .after (1000 ,self .update_timer )
            except ValueError :
                messagebox .showerror ("Error","Please enter valid numbers")

    def timer_pause (self ):
        """Pause the countdown timer."""
        self .timer_running =False 
        if getattr (self ,"timer_after_id",None ):
            self .after_cancel (self .timer_after_id )
            self .timer_after_id =None 

    def timer_reset (self ):
        """Reset the countdown timer."""
        self .timer_running =False 
        if getattr (self ,"timer_after_id",None ):
            self .after_cancel (self .timer_after_id )
            self .timer_after_id =None 


        self .timer_total =0 
        self .timer_label .configure (text ="00:00:00")
        self .timer_start_btn .configure (text ="Start")

    def update_timer (self ):
        """Update the countdown timer display every second."""
        if not self .winfo_exists ():
            return 

        if self .timer_running and self .timer_total >0 :
            self .timer_total -=1 


            hours =self .timer_total //3600 
            minutes =(self .timer_total %3600 )//60 
            seconds =self .timer_total %60 
            time_str =f"{hours :02}:{minutes :02}:{seconds :02}"
            self .timer_label .configure (text =time_str )

            if self .timer_total >0 :

                self .timer_after_id =self .after (1000 ,self .update_timer )
            else :

                self .timer_running =False 
                self .timer_start_btn .configure (text ="Start")
                self .trigger_alarm_sound ()

    def build_alarm (self ):
        """Build the alarm tab interface."""
        tab =self .tabs .tab ("Alarm")


        self .alarm_active =False 
        self .alarm_check_running =False 


        container =ctk .CTkFrame (tab ,fg_color ="transparent")
        container .pack (expand =True )


        time_row =ctk .CTkFrame (container ,fg_color ="transparent")
        time_row .pack (pady =10 )


        self .al_hr_entry =ctk .CTkEntry (time_row ,width =80 ,height =60 ,font =("Arial",40 ),justify ="center",placeholder_text ="07")
        self .al_hr_entry .pack (side ="left",padx =5 )

        ctk .CTkLabel (time_row ,text =":",font =("Arial",40 )).pack (side ="left",padx =5 )

        self .al_min_entry =ctk .CTkEntry (time_row ,width =80 ,height =60 ,font =("Arial",40 ),justify ="center",placeholder_text ="00")
        self .al_min_entry .pack (side ="left",padx =5 )


        self .al_ampm_seg =ctk .CTkSegmentedButton (container ,values =["AM","PM"],width =150 ,height =40 )
        self .al_ampm_seg .set ("AM")
        self .al_ampm_seg .pack (pady =15 )


        self .alarm_status =ctk .CTkLabel (tab ,text ="NO ALARM SET",font =("Arial",14 ),text_color ="gray")
        self .alarm_status .pack (pady =(0 ,20 ))


        ctk .CTkButton (tab ,text ="Set Alarm",width =200 ,height =40 ,font =("Arial",16 ,"bold"),command =self .set_alarm ).pack (side ="bottom",pady =30 )

    def set_alarm (self ):
        """Set the alarm time."""

        hr_str =self .al_hr_entry .get ()
        min_str =self .al_min_entry .get ()
        ampm =self .al_ampm_seg .get ()


        if not hr_str .isdigit ()or not min_str .isdigit ():
            return messagebox .showerror ("Error","Numbers only.")

        hr =int (hr_str )
        mn =int (min_str )

        if not (1 <=hr <=12 )or not (0 <=mn <=59 ):
            return messagebox .showerror ("Error","Invalid time.")


        display_time =f"{hr :02}:{mn :02} {ampm }"
        if ampm =="PM"and hr !=12 :
            hr +=12 
        if ampm =="AM"and hr ==12 :
            hr =0 


        self .alarm_target_time =f"{hr :02}:{mn :02}"
        self .alarm_active =True 
        self .alarm_status .configure (text =f"ALARM SET FOR {display_time }",text_color ="#2CC985")


        if not self .alarm_check_running :
            self .alarm_check_running =True 
            self .check_alarm_loop ()

    def check_alarm_loop (self ):
        """Check if it's time for the alarm every second."""
        if not self .winfo_exists ():
            return 

        if self .alarm_active :

            current_time =datetime .datetime .now ().strftime ("%H:%M")
            if current_time ==self .alarm_target_time :

                self .trigger_alarm_sound ()
                self .alarm_active =False 
                self .alarm_status .configure (text ="ALARM CLEARED",text_color ="gray")


        self .after (1000 ,self .check_alarm_loop )

    def trigger_alarm_sound (self ):
        """Play the alarm sound and show notification."""
        sound_path =os .path .join (ASSETS_DIR ,"alarm.mp3")
        if not os .path .exists (sound_path ):
            return messagebox .showerror ("Error","alarm.mp3 missing.")

        try :

            pygame .mixer .music .load (sound_path )
            pygame .mixer .music .play (loops =-1 )


            messagebox .showinfo ("ALARM","Time's up! Click OK to stop.")


            pygame .mixer .music .stop ()
        except Exception as e :
            messagebox .showerror ("Error",str (e ))