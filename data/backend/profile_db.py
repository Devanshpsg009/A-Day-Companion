import sqlite3

DB_NAME = "profiles.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_profile_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        user_class TEXT,
        hobbies TEXT,
        goals TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_profile(user_id, name, user_class, hobbies, goals):
    create_profile_table()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO profiles 
    (user_id, full_name, user_class, hobbies, goals)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, name, user_class, hobbies, goals))

    conn.commit()
    conn.close()

def get_profile(user_id):
    create_profile_table()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT full_name, user_class, hobbies, goals FROM profiles WHERE user_id=?",
        (user_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row