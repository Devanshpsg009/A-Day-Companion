import sqlite3 
import bcrypt 
import pyotp 
from backend .database import DB_NAME 


def create_users_table ():
    """Create the users table and add missing columns if needed."""
    with sqlite3 .connect (DB_NAME ,timeout =5 )as conn :
        conn .execute (
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password BLOB NOT NULL, otp_secret TEXT)"
        )
        columns =[column [1 ]for column in conn .execute ("PRAGMA table_info(users)").fetchall ()]
        if "otp_secret"not in columns :
            conn .execute ("ALTER TABLE users ADD COLUMN otp_secret TEXT")


def authenticate_user (email ,password ):
    """Return True when email and password match a user record."""
    create_users_table ()
    with sqlite3 .connect (DB_NAME ,timeout =5 )as conn :
        row =conn .execute ("SELECT password FROM users WHERE email=?",(email ,)).fetchone ()
        if row :
            stored_password =row [0 ]
            return bcrypt .checkpw (password .encode ("utf-8"),stored_password )
        return False 


def email_exists (email ):
    """Return True if the email already exists in the database."""
    create_users_table ()
    with sqlite3 .connect (DB_NAME ,timeout =5 )as conn :
        result =conn .execute ("SELECT 1 FROM users WHERE email=?",(email ,)).fetchone ()
        return result is not None 


def create_user (email ,password ):
    """Create a new user and return the OTP secret."""
    create_users_table ()
    with sqlite3 .connect (DB_NAME ,timeout =5 )as conn :
        existing =conn .execute ("SELECT email FROM users WHERE email=?",(email ,)).fetchone ()
        if existing :
            return None 

        secret =pyotp .random_base32 ()
        hashed_password =bcrypt .hashpw (password .encode ("utf-8"),bcrypt .gensalt ())
        conn .execute (
        "INSERT INTO users (email, password, otp_secret) VALUES (?, ?, ?)",
        (email ,hashed_password ,secret ),
        )
        return secret 


def update_password (email ,new_password ):
    """Update a user's password in the database."""
    hashed_password =bcrypt .hashpw (new_password .encode ("utf-8"),bcrypt .gensalt ())
    with sqlite3 .connect (DB_NAME ,timeout =5 )as conn :
        updated_rows =conn .execute (
        "UPDATE users SET password=? WHERE email=?",
        (hashed_password ,email ),
        ).rowcount 
    return updated_rows >0 


def verify_totp (email ,code ):
    """Verify the 2FA code for the given user."""
    with sqlite3 .connect (DB_NAME ,timeout =5 )as conn :
        row =conn .execute ("SELECT otp_secret FROM users WHERE email=?",(email ,)).fetchone ()
        if row and row [0 ]:
            otp_secret =row [0 ]
            totp =pyotp .TOTP (otp_secret )
            return totp .verify (code )
    return False 