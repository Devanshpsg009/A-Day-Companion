import sqlite3
import datetime

DB_NAME = "insights.db"

DEV_MODE = True 
_fake_today = None

def set_debug_date(date_str):
    global _fake_today
    _fake_today = datetime.date.fromisoformat(date_str)

def today():
    if DEV_MODE and _fake_today:
        return _fake_today
    return datetime.date.today()

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS insights (
        user_id INTEGER,
        date TEXT,
        opened INTEGER,
        PRIMARY KEY (user_id, date)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS streaks (
        user_id INTEGER PRIMARY KEY,
        current_streak INTEGER,
        last_opened TEXT,
        started INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def has_started(user_id):
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT started FROM streaks WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row and row[0] == 1

def start_insights(user_id):
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    
    today_str = today().isoformat()
    
    cur.execute("""
    INSERT INTO streaks (user_id, current_streak, last_opened, started)
    VALUES (?, 1, ?, 1)
    ON CONFLICT(user_id) DO UPDATE SET
        started=1,
        current_streak=1,
        last_opened=?
    """, (user_id, today_str, today_str))

    cur.execute("""
    INSERT OR IGNORE INTO insights (user_id, date, opened)
    VALUES (?, ?, 1)
    """, (user_id, today_str))

    conn.commit()
    conn.close()

def log_app_open(user_id):
    if not has_started(user_id):
        return

    conn = get_connection()
    cur = conn.cursor()

    today_date = today()
    today_str = today_date.isoformat()

    cur.execute("SELECT current_streak, last_opened FROM streaks WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        return

    streak, last_opened = row
    
    if last_opened == today_str:
        conn.close()
        return

    if last_opened:
        last_date = datetime.date.fromisoformat(last_opened)
        delta = (today_date - last_date).days

        if delta == 1:
            streak += 1
        elif delta > 1:
            streak = 1
    else:
        streak = 1

    cur.execute("""
    INSERT OR IGNORE INTO insights (user_id, date, opened)
    VALUES (?, ?, 1)
    """, (user_id, today_str))

    cur.execute("""
    UPDATE streaks 
    SET current_streak=?, last_opened=?
    WHERE user_id=?
    """, (streak, today_str, user_id))

    conn.commit()
    conn.close()

def get_streak(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT current_streak FROM streaks WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def get_weekly_data(user_id):
    conn = get_connection()
    cur = conn.cursor()
    
    curr = today()
    start_of_week = curr - datetime.timedelta(days=curr.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)

    cur.execute("""
    SELECT date, opened FROM insights
    WHERE user_id=? AND date >= ? AND date <= ?
    ORDER BY date
    """, (user_id, start_of_week.isoformat(), end_of_week.isoformat()))
    
    rows = cur.fetchall()
    conn.close()

    data_map = {row[0]: row[1] for row in rows}
    full_data = []
    days_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    for i in range(7):
        day_date = start_of_week + datetime.timedelta(days=i)
        day_str = day_date.isoformat()
        status = data_map.get(day_str, 0)
        full_data.append((days_labels[i], status))
        
    return full_data

def get_monthly_data(user_id):
    conn = get_connection()
    cur = conn.cursor()
    
    curr = today()
    start_date = curr - datetime.timedelta(days=29)

    cur.execute("""
    SELECT date, opened FROM insights
    WHERE user_id=? AND date >= ?
    ORDER BY date
    """, (user_id, start_date.isoformat()))
    
    rows = cur.fetchall()
    conn.close()

    data_map = {row[0]: row[1] for row in rows}
    full_data = []
    
    for i in range(30):
        day_date = start_date + datetime.timedelta(days=i)
        day_str = day_date.isoformat()
        status = data_map.get(day_str, 0)
        label = str(day_date.day) if i % 2 == 0 else ""
        full_data.append((label, status))
        
    return full_data