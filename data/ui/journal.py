
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime
import json
from backend.ai import analyze_sentiment

class JournalApp (ctk.CTkToplevel ):

    def __init__ (self ,user_id ):
        super ().__init__ ()
        self.user_id =user_id
        self.geometry ("900x700")
        self.title ("My Journal - AI Edition")


        self.current_date =datetime.date.today ()
        self.db_path ="journal.db"
        self.current_font_family ="Georgia"
        self.current_font_size =14


        self.init_db ()


        self.setup_layout ()
        self.setup_header ()
        self.setup_toolbar ()

        self.setup_editor ()
        self.setup_status_bar ()


        self.load_entry ()

    def init_db (self ):
        with sqlite3.connect (self.db_path )as conn :

            conn.execute ("""
                CREATE TABLE IF NOT EXISTS journal (
                    user_id INTEGER,
                    date TEXT,
                    content TEXT,
                    tags TEXT,
                    mood TEXT,
                    score INTEGER,
                    PRIMARY KEY (user_id, date)
                )
            """)


            cols =[c [1 ]for c in conn.execute ("PRAGMA table_info(journal)").fetchall ()]
            if 'mood'not in cols :

                conn.execute ("ALTER TABLE journal ADD COLUMN mood TEXT")
                conn.execute ("ALTER TABLE journal ADD COLUMN score INTEGER")

    def setup_layout (self ):
        self.grid_columnconfigure (0 ,weight =1 )
        self.grid_rowconfigure (2 ,weight =1 )

    def setup_header (self ):
        header =ctk.CTkFrame (self ,height =50 ,fg_color ="#1e293b",corner_radius =0 )
        header.grid (row =0 ,column =0 ,sticky ="ew")

        nav =ctk.CTkFrame (header ,fg_color ="transparent")
        nav.pack (pady =10 )


        ctk.CTkButton (nav ,text ="<",width =40 ,command =self.prev_day ,fg_color ="#334155").pack (side ="left",padx =10 )


        self.date_label =ctk.CTkLabel (nav ,text =str (self.current_date ),font =("Arial",18 ,"bold"),text_color ="white",width =200 )
        self.date_label.pack (side ="left",padx =10 )



        ctk.CTkButton (nav ,text =">",width =40 ,command =self.next_day ,fg_color ="#334155").pack (side ="left",padx =10 )


    def setup_toolbar (self ):
        toolbar =ctk.CTkFrame (self ,height =50 ,fg_color ="#0f172a",corner_radius =0 )
        toolbar.grid (row =1 ,column =0 ,sticky ="ew",padx =20 ,pady =(10 ,0 ))


        ctk.CTkButton (toolbar ,text ="B",width =40 ,font =("Times",16 ,"bold"),fg_color ="#334155",command =self.on_bold ).pack (side ="left",padx =2 )
        ctk.CTkButton (toolbar ,text ="I",width =40 ,font =("Times",16 ,"italic"),fg_color ="#334155",command =self.on_italic ).pack (side ="left",padx =2 )


        ctk.CTkFrame (toolbar ,width =2 ,height =30 ,fg_color ="gray").pack (side ="left",padx =10 )


        self.colors =["#ffffff","#ef4444","#3b82f6","#22c55e","#f59e0b","#a855f7"]
        for col in self.colors :
            ctk.CTkButton (toolbar ,text ="",width =25 ,height =25 ,fg_color =col ,hover_color =col ,corner_radius =5 ,command =lambda c =col :self.on_color (c )).pack (side ="left",padx =3 )



        ctk.CTkFrame (toolbar ,width =2 ,height =30 ,fg_color ="gray").pack (side ="left",padx =10 )


        ctk.CTkButton (toolbar ,text ="-",width =30 ,fg_color ="#334155",command =lambda :self.change_size (-2 )).pack (side ="left",padx =2 )
        ctk.CTkButton (toolbar ,text ="+",width =30 ,fg_color ="#334155",command =lambda :self.change_size (2 )).pack (side ="left",padx =2 )


        ctk.CTkButton (toolbar ,text ="✨ Analyze Mood",width =120 ,fg_color ="#8b5cf6",hover_color ="#7c3aed",font =("Helvetica",12 ,"bold"),command =self.run_analysis ).pack (side ="right",padx =10 )
        ctk.CTkButton (toolbar ,text ="Find",width =60 ,fg_color ="#3b82f6",command =self.find_text ).pack (side ="right",padx =5 )

    def setup_editor (self ):
        editor_frame =ctk.CTkFrame (self ,fg_color ="transparent")
        editor_frame.grid (row =2 ,column =0 ,sticky ="nsew",padx =20 ,pady =10 )


        self.text_editor =tk.Text (
        editor_frame ,
        bg ="#020617",
        fg ="#e2e8f0",
        insertbackground ="white",
        font =(self.current_font_family ,self.current_font_size ),
        selectbackground ="#3b82f6",
        selectforeground ="white",
        wrap ="word",

        bd =0 ,
        highlightthickness =0
        )
        self.text_editor.pack (fill ="both",expand =True )


        sb =ctk.CTkScrollbar (editor_frame ,command =self.text_editor.yview )
        sb.pack (side ="right",fill ="y")
        self.text_editor.config (yscrollcommand =sb.set )


        self.setup_tags ()


        self.text_editor.bind ("<KeyRelease>",self.on_key_release )

    def setup_status_bar (self ):
        status =ctk.CTkFrame (self ,height =30 ,fg_color ="transparent")
        status.grid (row =3 ,column =0 ,sticky ="ew",padx =20 ,pady =(0 ,10 ))


        self.stats_label =ctk.CTkLabel (status ,text ="Words: 0 | Chars: 0",text_color ="gray",font =("Arial",12 ))
        self.stats_label.pack (side ="right")


        self.mood_label =ctk.CTkLabel (status ,text ="",text_color ="#f472b6",font =("Arial",12 ,"bold"))
        self.mood_label.pack (side ="left",padx =10 )



        self.msg_label =ctk.CTkLabel (status ,text ="Ready",text_color ="#38bdf8",font =("Arial",12 ))
        self.msg_label.pack (side ="left")

    def setup_tags (self ):

        self.text_editor.tag_configure ("bold",font =(self.current_font_family ,self.current_font_size ,"bold"))
        self.text_editor.tag_configure ("italic",font =(self.current_font_family ,self.current_font_size ,"italic"))


        self.text_editor.tag_configure ("found",background ="#f59e0b",foreground ="black")


        for col in self.colors :
            self.text_editor.tag_configure (f"color_{col }",foreground =col )


    def run_analysis (self ):
        content =self.text_editor.get ("1.0","end-1c")


        if len (content.split ())<5 :
            return messagebox.showwarning ("Too Short","Please write at least 5 words to analyze.")


        self.msg_label.configure (text ="AI is thinking...",text_color ="#eab308")
        self.update ()



        result =analyze_sentiment (self.user_id ,content )

        if result :
            mood =result.get ("mood","Unknown")
            score =result.get ("score",5 )
            advice =result.get ("advice","Keep writing!")


            self.mood_label.configure (text =f"Mood: {mood } ({score }/10)")
            self.msg_label.configure (text ="Analysis Complete",text_color ="#22c55e")


            self.save_entry (mood =mood ,score =score )


            messagebox.showinfo (f"AI Insight: {mood }",f"Score: {score }/10\n\n💡 Advice:\n{advice }")
        else :
            self.msg_label.configure (text ="Analysis Failed",text_color ="#ef4444")
            messagebox.showerror ("Error","Could not connect to AI.")

    def toggle_tag (self ,tag_name ):
        try :

            if not self.text_editor.tag_ranges ("sel"):
                return


            if tag_name in self.text_editor.tag_names ("sel.first"):
                self.text_editor.tag_remove (tag_name ,"sel.first","sel.last")
            else :

                self.text_editor.tag_add (tag_name ,"sel.first","sel.last")


            self.save_entry ()
        except :
            pass

    def on_bold (self ):
        self.toggle_tag ("bold")

    def on_italic (self ):
        self.toggle_tag ("italic")

    def on_color (self ,color ):
        try :


            if not self.text_editor.tag_ranges ("sel"):
                return




            for c in self.colors :
                self.text_editor.tag_remove (f"color_{c }","sel.first","sel.last")


            self.text_editor.tag_add (f"color_{color }","sel.first","sel.last")


            self.save_entry ()
        except :
            pass

    def change_size (self ,delta ):
        self.current_font_size =max (10 ,self.current_font_size +delta )
        self.text_editor.configure (font =(self.current_font_family ,self.current_font_size ))
        self.setup_tags ()

    def find_text (self ):

        search_term =ctk.CTkInputDialog (text ="Search for:",title ="Find").get_input ()
        if search_term :

            self.text_editor.tag_remove ("found","1.0","end")



            start ="1.0"
            while True :
                pos =self.text_editor.search (search_term ,start ,stopindex ="end")
                if not pos :
                    break
                end =f"{pos }+{len (search_term )}c"
                self.text_editor.tag_add ("found",pos ,end )
                start =end

    def on_key_release (self ,event =None ):
        content =self.text_editor.get ("1.0","end-1c")



        word_count =len (content.split ())if content.strip ()else 0
        char_count =len (content )
        self.stats_label.configure (text =f"Words: {word_count } | Chars: {char_count }")


        self.save_entry ()

    def save_entry (self ,event =None ,mood =None ,score =None ):
        content =self.text_editor.get ("1.0","end-1c")



        tags_data =[]
        for tag_name in ["bold","italic"]+[f"color_{c }"for c in self.colors ]:
            ranges =self.text_editor.tag_ranges (tag_name )
            for i in range (0 ,len (ranges ),2 ):
                tags_data.append ({
                "t":tag_name ,
                "s":str (ranges [i ]),
                "e":str (ranges [i +1 ])
                })

        with sqlite3.connect (self.db_path )as conn :

            if mood is None :
                row =conn.execute (
                "SELECT mood, score FROM journal WHERE user_id=? AND date=?",
                (self.user_id ,str (self.current_date ))
                ).fetchone ()
                if row :
                    mood ,score =row


            conn.execute ("""
                INSERT INTO journal (user_id, date, content, tags, mood, score)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, date) DO UPDATE SET
                    content=excluded.content,
                    tags=excluded.tags,
                    mood=excluded.mood,
                    score=excluded.score
            """,(self.user_id ,str (self.current_date ),content ,json.dumps (tags_data ),mood ,score ))

        self.msg_label.configure (text ="Saved",text_color ="#22c55e")

    def load_entry (self ):


        self.date_label.configure (text =self.current_date.strftime ("%B %d, %Y"))


        self.text_editor.delete ("1.0","end")
        self.mood_label.configure (text ="")


        with sqlite3.connect (self.db_path )as conn :
            row =conn.execute (
            "SELECT content, tags, mood, score FROM journal WHERE user_id=? AND date=?",
            (self.user_id ,str (self.current_date ))
            ).fetchone ()

        if row :

            self.text_editor.insert ("1.0",row [0 ])


            if row [1 ]:
                try :
                    for item in json.loads (row [1 ]):
                        self.text_editor.tag_add (item ["t"],item ["s"],item ["e"])
                except :
                    pass


            if row [2 ]:
                self.mood_label.configure (text =f"Mood: {row [2 ]} ({row [3 ]}/10)")


        self.on_key_release ()
        self.msg_label.configure (text ="Loaded",text_color ="#38bdf8")

    def prev_day (self ):

        self.current_date -=datetime.timedelta (days =1 )
        self.load_entry ()


    def next_day (self ):
        self.current_date +=datetime.timedelta (days =1 )
        self.load_entry ()