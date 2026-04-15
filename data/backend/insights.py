
import sqlite3
import datetime

DB_NAME ="insights.db"

def today ():
    return datetime.date.today ()

def init_db ():
    with sqlite3.connect (DB_NAME )as conn :
        conn.execute ("""
        CREATE TABLE IF NOT EXISTS insights (

            user_id INTEGER,
            date TEXT,

            opened INTEGER,
            PRIMARY KEY (user_id, date)
        )
        """)
        conn.execute ("""
        CREATE TABLE IF NOT EXISTS streaks (
            user_id INTEGER PRIMARY KEY,
            current_streak INTEGER,
            last_opened TEXT,
            started INTEGER DEFAULT 0
        )
        """)

def has_started (user_id ):
    init_db ()
    with sqlite3.connect (DB_NAME )as conn :
        row =conn.execute ("SELECT started FROM streaks WHERE user_id=?",(user_id ,)).fetchone ()
        return row and row [0 ]==1


def start_insights (user_id ):
    init_db ()
    today_str =today ().isoformat ()
    with sqlite3.connect (DB_NAME )as conn :

        conn.execute ("""
        INSERT INTO streaks (user_id, current_streak, last_opened, started)
        VALUES (?, 1, ?, 1)
        ON CONFLICT(user_id) DO UPDATE SET started=1, current_streak=1, last_opened=?
        """,(user_id ,today_str ,today_str ))
        conn.execute ("INSERT OR IGNORE INTO insights (user_id, date, opened) VALUES (?, ?, 1)",(user_id ,today_str ))

def log_app_open (user_id ):
    if not has_started (user_id ):return
    today_date =today ()

    today_str =today_date.isoformat ()
    with sqlite3.connect (DB_NAME )as conn :
        row =conn.execute ("SELECT current_streak, last_opened FROM streaks WHERE user_id=?",(user_id ,)).fetchone ()

        if not row or row [1 ]==today_str :return
        streak ,last_opened =row
        if last_opened :
            delta =(today_date -datetime.date.fromisoformat (last_opened )).days

            streak =streak +1 if delta ==1 else 1
        else :
            streak =1
        conn.execute ("INSERT OR IGNORE INTO insights (user_id, date, opened) VALUES (?, ?, 1)",(user_id ,today_str ))
        conn.execute ("UPDATE streaks SET current_streak=?, last_opened=? WHERE user_id=?",(streak ,today_str ,user_id ))

def get_streak (user_id ):
    with sqlite3.connect (DB_NAME )as conn :

        row =conn.execute ("SELECT current_streak FROM streaks WHERE user_id=?",(user_id ,)).fetchone ()
        return row [0 ]if row else 0

def get_weekly_data (user_id ):

    curr =today ()
    start =curr -datetime.timedelta (days =curr.weekday ())
    end =start +datetime.timedelta (days =6 )
    with sqlite3.connect (DB_NAME )as conn :
        rows =conn.execute ("SELECT date, opened FROM insights WHERE user_id=? AND date >= ? AND date <= ? ORDER BY date",(user_id ,start.isoformat (),end.isoformat ())).fetchall ()
    data_map ={r [0 ]:r [1 ]for r in rows }
    days =["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    return [(days [i ],data_map.get ((start +datetime.timedelta (days =i )).isoformat (),0 ))for i in range (7 )]


def get_monthly_data (user_id ):
    start =today ()-datetime.timedelta (days =29 )
    with sqlite3.connect (DB_NAME )as conn :
        rows =conn.execute ("SELECT date, opened FROM insights WHERE user_id=? AND date >= ? ORDER BY date",(user_id ,start.isoformat ())).fetchall ()
    data_map ={r [0 ]:r [1 ]for r in rows }
    return [(str ((start +datetime.timedelta (days =i )).day )if i %2 ==0 else "",data_map.get ((start +datetime.timedelta (days =i )).isoformat (),0 ))for i in range (30 )]