import sqlite3, bcrypt, pyotp
from backend.database import DB_NAME

def create_users_table():
    with sqlite3.connect(DB_NAME, timeout=5) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password BLOB NOT NULL, otp_secret TEXT)")
        if "otp_secret" not in [c[1] for c in conn.execute("PRAGMA table_info(users)").fetchall()]:
            conn.execute("ALTER TABLE users ADD COLUMN otp_secret TEXT")

def authenticate_user(email, password):
    create_users_table()
    with sqlite3.connect(DB_NAME, timeout=5) as conn:
        row = conn.execute("SELECT password FROM users WHERE email=?", (email,)).fetchone()
        return bcrypt.checkpw(password.encode('utf-8'), row[0]) if row else False

def email_exists(email):
    create_users_table()
    with sqlite3.connect(DB_NAME, timeout=5) as conn:
        return conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone() is not None

def create_user(email, password):
    create_users_table()
    with sqlite3.connect(DB_NAME, timeout=5) as conn:
        if conn.execute("SELECT email FROM users WHERE email=?", (email,)).fetchone(): return None
        secret = pyotp.random_base32()
        conn.execute("INSERT INTO users (email, password, otp_secret) VALUES (?, ?, ?)", (email, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()), secret))
        return secret

def update_password(email, new_password):
    with sqlite3.connect(DB_NAME, timeout=5) as conn:
        return conn.execute("UPDATE users SET password=? WHERE email=?", (bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()), email)).rowcount > 0

def verify_totp(email, code):
    with sqlite3.connect(DB_NAME, timeout=5) as conn:
        row = conn.execute("SELECT otp_secret FROM users WHERE email=?", (email,)).fetchone()
        return pyotp.TOTP(row[0]).verify(code) if row and row[0] else False