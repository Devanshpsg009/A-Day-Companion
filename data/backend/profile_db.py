
import sqlite3

DB_NAME = "profiles.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                user_class TEXT,
                hobbies TEXT,
                goals TEXT
            )
        """
        )


def save_profile(user_id, name, user_class, hobbies, goals):

    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO profiles
            (user_id, full_name, user_class, hobbies, goals)
            VALUES (?, ?, ?, ?, ?)
        """,
            (user_id, name, user_class, hobbies, goals),
        )



def get_profile(user_id):
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute(
            "SELECT full_name, user_class, hobbies, goals FROM profiles WHERE user_id=?",
            (user_id,),
        ).fetchone()
