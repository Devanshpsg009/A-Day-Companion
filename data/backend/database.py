import sqlite3

DB_NAME = "users.db"

def create_users_table():
    with sqlite3.connect(DB_NAME, timeout=5) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password BLOB NOT NULL)")

def has_users():
    create_users_table()
    with sqlite3.connect(DB_NAME, timeout=5) as conn:
        return conn.execute("SELECT 1 FROM users LIMIT 1").fetchone() is not None

def get_user_id(email):
    with sqlite3.connect(DB_NAME, timeout=5) as conn:
        row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        return row[0] if row else None