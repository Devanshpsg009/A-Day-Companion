import sqlite3
import bcrypt
from backend.database import DB_NAME

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(stored_hash, user_input):
    return bcrypt.checkpw(user_input.encode('utf-8'), stored_hash)

def authenticate_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()
    if row:
        return check_password(row[0], password)
    return False

def create_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE email=?", (email,))
    if cur.fetchone():
        conn.close()
        return False
    hashed = hash_password(password)
    cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
    conn.commit()
    conn.close()
    return True

def update_password(email, new_password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    hashed = hash_password(new_password)
    cur.execute("UPDATE users SET password=? WHERE email=?", (hashed, email))
    updated = cur.rowcount > 0
    conn.commit()
    conn.close()
    return updated