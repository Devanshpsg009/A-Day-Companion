import customtkinter as ctk 
import sqlite3 
import datetime 
from datetime import timedelta 
import random 


def _import_matplotlib ():
    """Import matplotlib components for charting."""
    import matplotlib .pyplot as plt 
    from matplotlib .backends .backend_tkagg import FigureCanvasTkAgg 
    return plt ,FigureCanvasTkAgg 


ctk .set_appearance_mode ("dark")
ctk .set_default_color_theme ("dark-blue")

class InsightsApp (ctk .CTkToplevel ):
    """Main class for the Analytics and Insights application."""

    def __init__ (self ,user_id ):
        super ().__init__ ()
        self .user_id =user_id 
        self .geometry ("1100x750")
        self .title ("Analytics Command Center")
        self .resizable (False ,False )


        self .todo_db ="todo.db"
        self .journal_db ="journal.db"


        self .ensure_db_schema ()


        self .setup_layout ()
        self .setup_header ()
        self .setup_tabs ()
        self .setup_dev_tools ()


        self .build_daily_tab ()
        self .build_weekly_tab ()
        self .build_monthly_tab ()

    def setup_layout (self ):
        """Set up the main window grid layout."""
        self .grid_columnconfigure (0 ,weight =1 )
        self .grid_rowconfigure (1 ,weight =1 )

    def setup_header (self ):
        """Set up the header with title."""
        self .header =ctk .CTkFrame (self ,height =60 ,corner_radius =0 ,fg_color ="#1e293b")
        self .header .grid (row =0 ,column =0 ,sticky ="ew")

        ctk .CTkLabel (
        self .header ,
        text ="Productivity & Wellness Insights",
        font =("Helvetica",24 ,"bold"),
        text_color ="white"
        ).pack (pady =15 )

    def setup_tabs (self ):
        """Set up the tab view for different time periods."""
        self .tabs =ctk .CTkTabview (
        self ,
        fg_color ="#0f172a",
        segmented_button_selected_color ="#3b82f6"
        )
        self .tabs .grid (row =1 ,column =0 ,sticky ="nsew",padx =20 ,pady =10 )


        self .tabs .add ("Daily")
        self .tabs .add ("Weekly")
        self .tabs .add ("Monthly")

    def setup_dev_tools (self ):
        """Set up developer tools at the bottom."""
        self .dev_frame =ctk .CTkFrame (self ,height =50 ,corner_radius =0 ,fg_color ="#020617")
        self .dev_frame .grid (row =2 ,column =0 ,sticky ="ew")


        self .dev_var =ctk .BooleanVar (value =False )
        self .dev_switch =ctk .CTkSwitch (
        self .dev_frame ,
        text ="Developer Mode",
        command =self .toggle_dev_tools ,
        variable =self .dev_var ,
        progress_color ="#22c55e"
        )
        self .dev_switch .pack (side ="left",padx =20 ,pady =10 )


        self .dev_tools =ctk .CTkFrame (self .dev_frame ,fg_color ="transparent")
        ctk .CTkButton (
        self .dev_tools ,
        text ="Inject Random Data",
        fg_color ="#ef4444",
        hover_color ="#b91c1c",
        width =150 ,
        command =self .inject_fake_data 
        ).pack (side ="left",padx =10 )

    def toggle_dev_tools (self ):
        """Toggle visibility of developer tools."""
        if self .dev_var .get ():
            self .dev_tools .pack (side ="left",padx =10 )
        else :
            self .dev_tools .pack_forget ()

    def ensure_db_schema (self ):
        """Ensure the database tables have the correct schema."""

        with sqlite3 .connect (self .todo_db )as conn :
            conn .execute ("""
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    task TEXT,
                    time TEXT,
                    status INTEGER DEFAULT 0,
                    notified INTEGER DEFAULT 0,
                    date TEXT
                )
            """)


            cols =[info [1 ]for info in conn .execute ("PRAGMA table_info(todos)").fetchall ()]
            if 'date'not in cols :
                try :
                    conn .execute ("ALTER TABLE todos ADD COLUMN date TEXT")
                    conn .execute (
                    "UPDATE todos SET date = ? WHERE date IS NULL",
                    (datetime .date .today ().isoformat (),)
                    )
                except :
                    pass 


        with sqlite3 .connect (self .journal_db )as conn :
            conn .execute ("""
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

    def inject_fake_data (self ):
        """Inject fake data for testing purposes."""

        tasks =["Study AI","Gym","Code Python","Read Book","Meditation","Project X"]
        moods =["Happy","Sad","Productive","Tired","Anxious","Excited"]


        with sqlite3 .connect (self .todo_db )as conn :
            for i in range (30 ):
                date_str =(datetime .date .today ()-timedelta (days =i )).isoformat ()
                for _ in range (random .randint (0 ,5 )):
                    conn .execute ("""
                        INSERT INTO todos (user_id, task, date, status, notified)
                        VALUES (?, ?, ?, ?, 1)
                    """,(self .user_id ,random .choice (tasks ),date_str ,1 if random .random ()>0.3 else 0 ))


        with sqlite3 .connect (self .journal_db )as conn :
            for i in range (30 ):
                conn .execute ("""
                    INSERT OR REPLACE INTO journal (user_id, date, content, mood, score)
                    VALUES (?, ?, 'Fake Entry', ?, ?)
                """,(
                self .user_id ,
                (datetime .date .today ()-timedelta (days =i )).isoformat (),
                random .choice (moods ),
                random .randint (3 ,9 )
                ))


        self .refresh_views ()

    def refresh_views (self ):
        """Refresh all tab views with updated data."""
        self .build_daily_tab ()
        self .build_weekly_tab ()
        self .build_monthly_tab ()

    def get_task_stats (self ,start_str ,end_str ):
        """Get task statistics for a date range."""
        try :
            with sqlite3 .connect (self .todo_db )as conn :

                total =conn .execute ("""
                    SELECT count(*) FROM todos
                    WHERE user_id=? AND date(date) BETWEEN date(?) AND date(?)
                """,(self .user_id ,start_str ,end_str )).fetchone ()[0 ]


                done =conn .execute ("""
                    SELECT count(*) FROM todos
                    WHERE user_id=? AND date(date) BETWEEN date(?) AND date(?) AND status=1
                """,(self .user_id ,start_str ,end_str )).fetchone ()[0 ]

            return total ,done 
        except :
            return 0 ,0 

    def get_mood_stats (self ,start_date ,days_count ):
        """Get mood statistics for a date range."""
        data =[]
        labels =[]
        current =start_date 
        end_date =start_date +timedelta (days =days_count -1 )

        with sqlite3 .connect (self .journal_db )as conn :
            while current <=end_date :
                row =conn .execute ("""
                    SELECT score FROM journal
                    WHERE user_id=? AND date=?
                """,(self .user_id ,current .isoformat ())).fetchone ()


                data .append (row [0 ]if row else 0 )


                if days_count ==7 :
                    labels .append (current .strftime ("%a"))
                else :
                    labels .append (str (current .day )if current .day %3 ==0 else "")

                current +=timedelta (days =1 )

        return data ,labels 

    def split_frame (self ,tab ):
        """Split a tab into left and right sections with a divider."""

        for widget in tab .winfo_children ():
            widget .destroy ()


        left =ctk .CTkFrame (tab ,fg_color ="transparent")
        left .pack (side ="left",fill ="both",expand =True ,padx =10 ,pady =10 )


        ctk .CTkFrame (tab ,width =2 ,fg_color ="#334155").pack (side ="left",fill ="y",pady =20 )


        right =ctk .CTkFrame (tab ,fg_color ="transparent")
        right .pack (side ="right",fill ="both",expand =True ,padx =10 ,pady =10 )

        return left ,right 

    def build_daily_tab (self ):
        """Build the daily insights tab."""
        left ,right =self .split_frame (self .tabs .tab ("Daily"))


        ctk .CTkLabel (
        left ,
        text ="Today's Productivity",
        font =("Arial",16 ,"bold"),
        text_color ="#3b82f6"
        ).pack (pady =10 )

        today =datetime .date .today ().isoformat ()
        total ,done =self .get_task_stats (today ,today )


        kpi_frame =ctk .CTkFrame (left ,fg_color ="transparent")
        kpi_frame .pack (fill ="x",pady =10 )

        self .create_kpi (kpi_frame ,"Total",total ,"#94a3b8","left")
        self .create_kpi (kpi_frame ,"Done",done ,"#22c55e","right")


        self .embed_chart (left ,"pie",[done ,total -done ],["Done","Pending"],["#22c55e","#ef4444"])


        ctk .CTkLabel (
        right ,
        text ="Today's Mood",
        font =("Arial",16 ,"bold"),
        text_color ="#a855f7"
        ).pack (pady =10 )


        with sqlite3 .connect (self .journal_db )as conn :
            row =conn .execute ("""
                SELECT mood, score FROM journal
                WHERE user_id=? AND date=?
            """,(self .user_id ,today )).fetchone ()

        mood_text =row [0 ]if row and row [0 ]else "No Data"
        score_val =row [1 ]if row and row [1 ]else 0 


        canvas =ctk .CTkCanvas (right ,width =200 ,height =200 ,bg ="#0f172a",highlightthickness =0 )
        canvas .pack (pady =30 )


        circle_color ="#a855f7"if score_val >0 else "#334155"
        canvas .create_oval (20 ,20 ,180 ,180 ,outline =circle_color ,width =8 )


        canvas .create_text (100 ,80 ,text =str (score_val ),fill ="white",font =("Arial",60 ,"bold"))
        canvas .create_text (100 ,130 ,text ="/ 10",fill ="gray",font =("Arial",20 ))


        ctk .CTkLabel (
        right ,
        text =mood_text ,
        font =("Helvetica",24 ,"bold"),
        text_color ="white"
        ).pack (pady =10 )

    def build_weekly_tab (self ):
        """Build the weekly insights tab."""
        left ,right =self .split_frame (self .tabs .tab ("Weekly"))


        ctk .CTkLabel (
        left ,
        text ="Task Completion (Last 7 Days)",
        font =("Arial",14 ,"bold"),
        text_color ="gray"
        ).pack ()

        end_date =datetime .date .today ()
        start_date =end_date -timedelta (days =6 )

        days =[]
        counts =[]
        current =start_date 


        while current <=end_date :
            _ ,done =self .get_task_stats (current .isoformat (),current .isoformat ())
            days .append (current .strftime ("%a"))
            counts .append (done )
            current +=timedelta (days =1 )

        self .embed_chart (left ,"bar",counts ,days ,"#3b82f6")


        ctk .CTkLabel (
        right ,
        text ="Mood Trend (Last 7 Days)",
        font =("Arial",14 ,"bold"),
        text_color ="gray"
        ).pack ()

        scores ,labels =self .get_mood_stats (start_date ,7 )
        self .embed_chart (right ,"line",scores ,labels ,"#a855f7")

    def build_monthly_tab (self ):
        """Build the monthly insights tab."""
        left ,right =self .split_frame (self .tabs .tab ("Monthly"))


        ctk .CTkLabel (
        left ,
        text ="Productivity Month View",
        font =("Arial",14 ,"bold"),
        text_color ="gray"
        ).pack ()

        end_date =datetime .date .today ()
        start_date =end_date -timedelta (days =29 )

        dates =[]
        counts =[]
        current =start_date 


        while current <=end_date :
            _ ,done =self .get_task_stats (current .isoformat (),current .isoformat ())
            dates .append (str (current .day )if current .day %3 ==0 else "")
            counts .append (done )
            current +=timedelta (days =1 )

        self .embed_chart (left ,"line",counts ,dates ,"#3b82f6")


        ctk .CTkLabel (
        right ,
        text ="Mental Health Trend (30 Days)",
        font =("Arial",14 ,"bold"),
        text_color ="gray"
        ).pack ()

        scores ,labels =self .get_mood_stats (start_date ,30 )
        self .embed_chart (right ,"line",scores ,labels ,"#a855f7")

    def create_kpi (self ,parent ,title ,value ,color ,side ):
        """Create a KPI (Key Performance Indicator) card."""
        card =ctk .CTkFrame (parent ,fg_color ="#1e293b",width =120 )
        card .pack (side =side ,padx =10 ,expand =True ,fill ="both")

        ctk .CTkLabel (card ,text =title ,text_color ="gray").pack (pady =(5 ,0 ))
        ctk .CTkLabel (
        card ,
        text =str (value ),
        font =("Arial",24 ,"bold"),
        text_color =color 
        ).pack (pady =(0 ,5 ))

    def embed_chart (self ,parent ,chart_type ,data ,labels ,color ):
        """Embed a matplotlib chart into the tkinter interface."""
        try :
            plt ,FigureCanvasTkAgg =_import_matplotlib ()
        except ImportError :
            ctk .CTkLabel (
            parent ,
            text ="Chart unavailable - matplotlib issue",
            text_color ="gray"
            ).pack (pady =20 )
            return 


        fig =plt .Figure (figsize =(4 ,3 ),dpi =100 ,facecolor ="#0f172a")
        ax =fig .add_subplot (111 )
        ax .set_facecolor ("#0f172a")


        ax .spines ['bottom'].set_color ('white')
        ax .spines ['left'].set_color ('white')
        ax .tick_params (axis ='x',colors ='white',labelsize =8 )
        ax .tick_params (axis ='y',colors ='white',labelsize =8 )
        ax .spines ['top'].set_visible (False )
        ax .spines ['right'].set_visible (False )


        if chart_type =="pie":

            if sum (data )==0 :
                data =[0 ,1 ]
                color =["#22c55e","#334155"]

            ax .pie (data ,labels =labels ,colors =color ,autopct ='%1.1f%%',textprops ={'color':"white"})

        elif chart_type =="bar":
            ax .bar (labels ,data ,color =color )

        elif chart_type =="line":
            x_indices =range (len (data ))
            ax .plot (x_indices ,data ,color =color ,marker ='o',linewidth =2 )
            ax .set_xticks (x_indices )
            ax .set_xticklabels (labels )
            ax .grid (color ='#334155',linestyle ='--',linewidth =0.5 )


            if color =="#a855f7":
                ax .set_ylim (0 ,10 )


        canvas =FigureCanvasTkAgg (fig ,master =parent )
        canvas .draw ()
        canvas .get_tk_widget ().pack (fill ="both",expand =True ,padx =5 ,pady =5 )