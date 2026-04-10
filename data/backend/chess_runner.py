import customtkinter as ctk 
from ui .board import ChessGame 
import os 
import platform 
import urllib .request 
import zipfile 
import stat 

def main ():
    def engine_dir ():
        return os .path .join (os .getcwd (),"engine")

    def get_release_url ():
        system =platform .system ()
        machine =platform .machine ().lower ()
        if system =="Windows":
            return "https://github.com/Devanshpsg009/A-Day-Companion/releases/download/A_Day_Companion/engine_windows.zip"
        elif system =="Linux":
            return "https://github.com/Devanshpsg009/A-Day-Companion/releases/download/A_Day_Companion/engine_linux.zip"
        elif system =="Darwin":
            if "arm"in machine or "aarch64"in machine :
                return "https://github.com/Devanshpsg009/A-Day-Companion/releases/download/A_Day_Companion/engine_mac_m.zip"
            else :
                return "https://github.com/Devanshpsg009/A-Day-Companion/releases/download/A_Day_Companion/engine_mac_intel.zip"
        else :
            raise Exception ("Unsupported Operating System")

    def get_stockfish_path ():
        base =engine_dir ()
        system =platform .system ()
        machine =platform .machine ().lower ()
        if system =="Windows":
            return os .path .join (base ,"engine_windows","stockfish-windows-x86-64-avx2.exe")
        elif system =="Linux":
            return os .path .join (base ,"engine_linux","stockfish-ubuntu-x86-64-avx2")
        elif system =="Darwin":
            if "arm"in machine or "aarch64"in machine :
                return os .path .join (base ,"engine_mac_m","stockfish-macos-m1")
            else :
                return os .path .join (base ,"engine_mac_intel","stockfish-macos-intel")
        else :
            raise Exception ("Unsupported Operating System")

    def download_and_extract ():
        os .makedirs (engine_dir (),exist_ok =True )
        url =get_release_url ()
        zip_path =os .path .join (engine_dir (),"engine.zip")
        urllib .request .urlretrieve (url ,zip_path )
        with zipfile .ZipFile (zip_path ,'r')as zf :
            zf .extractall (engine_dir ())
        os .remove (zip_path )

    def ensure_engine ():
        path =get_stockfish_path ()
        if not os .path .exists (path ):
            download_and_extract ()
        return get_stockfish_path ()

    def ensure_executable (path ):
        if platform .system ()!="Windows":
            st =os .stat (path )
            os .chmod (path ,st .st_mode |stat .S_IEXEC )

    app =ctk .CTk ()
    app .geometry ("400x300")
    app .title ("Chess Configuration")
    app .resizable (False ,False )
    ctk .set_appearance_mode ("Dark")

    ctk .CTkLabel (app ,text ="Select AI ELO and Color",font =("Helvetica",18 ,"bold")).pack (pady =20 )

    difficulty_var =ctk .StringVar (value ="1500")
    difficulty_menu =ctk .CTkOptionMenu (
    app ,
    values =["500","800","1000","1200","1500","1800","2000","2200","2500","2800","3000","max"],
    variable =difficulty_var 
    )
    difficulty_menu .pack (pady =10 )

    color_var =ctk .StringVar (value ="White")
    color_menu =ctk .CTkOptionMenu (
    app ,
    values =["White","Black"],
    variable =color_var 
    )
    color_menu .pack (pady =10 )

    def start_game ():
        if os .path .exists ("engine")and os .listdir ("engine"):
            level =difficulty_var .get ()
            global color 
            color =color_var .get ().lower ()
            stockfish_path =ensure_engine ()
            if not os .path .exists (stockfish_path ):
                print ("Stockfish not found:",stockfish_path )
                return 
            ensure_executable (stockfish_path )
            app .destroy ()
            game =ChessGame (
            800 ,
            800 ,
            "Chess",
            60 ,
            engine_path =stockfish_path ,
            level =level 
            )
            game .run ()
        else :
            import tkinter .messagebox 
            tkinter .messagebox .showinfo ("Wait","Please wait while the chess engine is being set up. This only happens on the first run.")
            ensure_engine ()

    ctk .CTkButton (
    app ,
    text ="Start Game",
    font =("Arial",16 ),
    fg_color ="#00cc66",
    hover_color ="#00ff80",
    text_color ="black",
    corner_radius =8 ,
    height =50 ,
    command =start_game 
    ).pack (pady =20 )

    app .mainloop ()

if __name__ =="__main__":
    main ()