import customtkinter as ctk 
import math 

ctk .set_appearance_mode ("Dark")
ctk .set_default_color_theme ("dark-blue")

class CalculatorApp (ctk .CTkToplevel ):
    def __init__ (self ):
        super ().__init__ ()
        self .geometry ("450x650")
        self .title ("Calculator")
        self .resizable (False ,False )

        self .expr =""
        self .history_text =""

        self .grid_columnconfigure (0 ,weight =1 )
        self .grid_rowconfigure (0 ,weight =0 )
        self .grid_rowconfigure (1 ,weight =0 )
        self .grid_rowconfigure (2 ,weight =1 )

        self .history_label =ctk .CTkLabel (
        self ,
        text ="",
        font =("Consolas",14 ),
        text_color ="gray",
        anchor ="e",
        )
        self .history_label .grid (row =0 ,column =0 ,padx =20 ,pady =(10 ,0 ),sticky ="ew")

        self .display =ctk .CTkEntry (
        self ,
        font =("Roboto Medium",40 ),
        justify ="right",
        fg_color ="#1a1a1a",
        border_color ="#333333",
        text_color ="#00ffcc",
        )
        self .display .grid (row =1 ,column =0 ,padx =20 ,pady =(0 ,20 ),sticky ="ew",ipady =15 )
        self .display .configure (state ="readonly")

        self .button_frame =ctk .CTkFrame (self ,fg_color ="transparent")
        self .button_frame .grid (row =2 ,column =0 ,padx =15 ,pady =10 ,sticky ="nsew")

        for i in range (4 ):
            self .button_frame .grid_columnconfigure (i ,weight =1 )
        for i in range (6 ):
            self .button_frame .grid_rowconfigure (i ,weight =1 )

        self .create_buttons ()
        self .setup_key_bindings ()

    def create_buttons (self ):
        """Create all calculator buttons and place them on the screen."""
        buttons =[
        ("C",0 ,0 ,"danger"),
        ("(",0 ,1 ,"func"),
        (")",0 ,2 ,"func"),
        ("⌫",0 ,3 ,"danger"),
        ("sin",1 ,0 ,"func"),
        ("cos",1 ,1 ,"func"),
        ("tan",1 ,2 ,"func"),
        ("/",1 ,3 ,"op"),
        ("7",2 ,0 ,"num"),
        ("8",2 ,1 ,"num"),
        ("9",2 ,2 ,"num"),
        ("*",2 ,3 ,"op"),
        ("4",3 ,0 ,"num"),
        ("5",3 ,1 ,"num"),
        ("6",3 ,2 ,"num"),
        ("-",3 ,3 ,"op"),
        ("1",4 ,0 ,"num"),
        ("2",4 ,1 ,"num"),
        ("3",4 ,2 ,"num"),
        ("+",4 ,3 ,"op"),
        ("0",5 ,0 ,"num"),
        (".",5 ,1 ,"num"),
        ("π",5 ,2 ,"func"),
        ("=",5 ,3 ,"action"),
        ]

        styles ={
        "num":{"fg":"#2b2b2b","hover":"#3a3a3a","text":"white"},
        "op":{"fg":"#ff9900","hover":"#ffb84d","text":"black"},
        "func":{"fg":"#404040","hover":"#505050","text":"#00ffcc"},
        "danger":{"fg":"#cc3333","hover":"#ff4d4d","text":"white"},
        "action":{"fg":"#00cc66","hover":"#00ff80","text":"black"},
        }

        for text ,row ,column ,style_key in buttons :
            style =styles [style_key ]
            button =ctk .CTkButton (
            self .button_frame ,
            text =text ,
            font =("Arial",20 ,"bold"),
            fg_color =style ["fg"],
            hover_color =style ["hover"],
            text_color =style ["text"],
            corner_radius =8 ,
            height =65 ,
            command =lambda value =text :self .click (value ),
            )
            button .grid (row =row ,column =column ,sticky ="nsew",padx =3 ,pady =3 )

    def setup_key_bindings (self ):
        """Bind keyboard keys to calculator actions."""
        self .bind ("<Return>",self .on_enter_key )
        self .bind ("<KP_Enter>",self .on_enter_key )
        self .bind ("<Escape>",self .on_escape_key )
        self .bind ("<BackSpace>",self .on_backspace_key )

        valid_keys ="0123456789+-*/.()"
        for key in valid_keys :
            self .bind (key ,self .make_key_handler (key ))

    def on_enter_key (self ,event ):
        self .click ("=")

    def on_escape_key (self ,event ):
        self .click ("C")

    def on_backspace_key (self ,event ):
        self .click ("⌫")

    def make_key_handler (self ,key ):
        def handler (event ):
            self .click (key )

        return handler 

    def click (self ,value ):
        """Add a new value to the expression or perform an action."""
        if value =="C":
            self .expr =""
            self .history_text =""
        elif value =="⌫":
            self .expr =self .expr [:-1 ]
        elif value =="=":
            self .calculate ()
            return 
        elif value =="π":
            self .expr +="math.pi"
        elif value in ["sin","cos","tan"]:
            self .expr +=f"math.{value }("
        else :
            self .expr +=value 

        self .update_display ()

    def update_display (self ):
        """Update the calculator screen with current values."""
        self .display .configure (state ="normal")
        self .display .delete (0 ,"end")
        display_text =self .expr .replace ("math.","").replace ("**","^")
        self .display .insert (0 ,display_text )
        self .history_label .configure (text =self .history_text )
        self .display .configure (state ="readonly")

    def calculate (self ):
        """Evaluate the expression and show the result."""
        if self .expr =="":
            return 

        blocked_words =["import","exec","eval","os","sys"]
        for word in blocked_words :
            if word in self .expr :
                self .show_error ("Illegal Input")
                return 

        open_count =self .expr .count ("(")
        close_count =self .expr .count (")")
        if open_count >close_count :
            self .expr +=")"*(open_count -close_count )

        try :
            result_value =eval (
            self .expr ,
            {"__builtins__":None },
            {"math":math ,"abs":abs },
            )
            result_text =str (round (result_value ,12 )if isinstance (result_value ,float )else result_value )
            if result_text .endswith (".0"):
                result_text =result_text [:-2 ]

            self .history_text =f"{self .expr .replace ('math.','')} ="
            self .expr =result_text 
            self .update_display ()
        except ZeroDivisionError :
            self .show_error ("Don't divide by zero")
        except Exception :
            self .show_error ("Error")

    def show_error (self ,msg ):
        """Show an error message instead of a number."""
        self .expr =""
        self .display .configure (state ="normal")
        self .display .delete (0 ,"end")
        self .display .insert (0 ,msg )
        self .display .configure (state ="readonly")