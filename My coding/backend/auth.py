import bcrypt
import sqlite3
from backend.database import get_connection

def create_user(email, password):
    conn = get_connection()
    cur = conn.cursor()

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cur.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hashed_password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT password FROM users WHERE email = ?",
        (email,)
    )
    row = cur.fetchone()
    conn.close()

    if row is None:
        return False

    return bcrypt.checkpw(password.encode(), row[0])