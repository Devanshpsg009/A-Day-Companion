import sqlite3
import bcrypt
import pyotp
from backend.database import DB_NAME

def get_connection():
    return sqlite3.connect(DB_NAME, timeout=5)

def create_users_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password BLOB NOT NULL,
            otp_secret TEXT
        )
    """)
    cur.execute("PRAGMA table_info(users)")
    if "otp_secret" not in [c[1] for c in cur.fetchall()]:
        cur.execute("ALTER TABLE users ADD COLUMN otp_secret TEXT")
    conn.commit()
    conn.close()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(stored_hash, user_input):
    return bcrypt.checkpw(user_input.encode('utf-8'), stored_hash)

def email_exists(email):
    create_users_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE email=?", (email,))
    result = cur.fetchone()
    conn.close()
    return result is not None

def authenticate_user(email, password):
    create_users_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()
    if row:
        return check_password(row[0], password)
    return False

def create_user(email, password):
    create_users_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE email=?", (email,))
    if cur.fetchone():
        conn.close()
        return None
    
    user_secret = pyotp.random_base32()
    hashed = hash_password(password)
    cur.execute("INSERT INTO users (email, password, otp_secret) VALUES (?, ?, ?)", (email, hashed, user_secret))
    conn.commit()
    conn.close()
    return user_secret

def update_password(email, new_password):
    conn = get_connection()
    cur = conn.cursor()
    hashed = hash_password(new_password)
    cur.execute("UPDATE users SET password=? WHERE email=?", (hashed, email))
    updated = cur.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def verify_totp(email, user_input_code):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT otp_secret FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()

    if row and row[0]:
        totp = pyotp.TOTP(row[0])
        return totp.verify(user_input_code)
    return False