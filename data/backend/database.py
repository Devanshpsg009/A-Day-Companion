import sqlite3 

DB_NAME ="users.db"


def create_users_table ():
    """Create the users table if it does not already exist."""
    with sqlite3 .connect (DB_NAME ,timeout =5 )as conn :
        conn .execute (
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password BLOB NOT NULL)"
        )


def has_users ():
    """Return True if there is at least one user in the database."""
    create_users_table ()
    with sqlite3 .connect (DB_NAME ,timeout =5 )as conn :
        row =conn .execute ("SELECT 1 FROM users LIMIT 1").fetchone ()
        return row is not None 


def get_user_id (email ):
    """Return the user id for the given email address."""
    with sqlite3 .connect (DB_NAME ,timeout =5 )as conn :
        row =conn .execute ("SELECT id FROM users WHERE email = ?",(email ,)).fetchone ()
        if row :
            return row [0 ]
        return None 