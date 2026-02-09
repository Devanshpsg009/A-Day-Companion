import os
import sqlite3
from datetime import date
from dotenv import load_dotenv
from groq import Groq
from backend.database import get_connection
from backend.profile_db import get_profile 

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

MAX_DAILY_PROMPTS = 30
KEYWORDS_FILE = "backend/allowed_keywords.txt"
DB_FILE = "ai_memory.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_usage (
            user_id INTEGER,
            day TEXT,
            count INTEGER,
            PRIMARY KEY (user_id, day)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_memory (
            user_id INTEGER,
            role TEXT,
            content TEXT
        )
    """)

    conn.commit()
    conn.close()


def load_keywords():
    try:
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
            return set(w.strip().lower() for w in f if w.strip())
    except FileNotFoundError:
        return set()


ALLOWED_KEYWORDS = load_keywords()


def allowed_topic(text):
    if not ALLOWED_KEYWORDS:
        return True
    t = text.lower()
    return any(k in t for k in ALLOWED_KEYWORDS)


def daily_count(user_id):
    init_db()
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT count FROM ai_usage WHERE user_id=? AND day=?",
        (user_id, today)
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0


def increment_count(user_id):
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ai_usage (user_id, day, count)
        VALUES (?, ?, 1)
        ON CONFLICT(user_id, day)
        DO UPDATE SET count = count + 1
    """, (user_id, today))
    conn.commit()
    conn.close()


def save_memory(user_id, role, content):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ai_memory VALUES (?, ?, ?)",
        (user_id, role, content)
    )
    conn.commit()
    conn.close()


def load_memory(user_id, limit=10):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT role, content FROM ai_memory
        WHERE user_id=?
        ORDER BY rowid DESC
        LIMIT ?
    """, (user_id, limit))
    rows = cur.fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in reversed(rows)]


def ask_ai(user_id, prompt):
    init_db()

    if daily_count(user_id) >= MAX_DAILY_PROMPTS:
        return "You've reached today's AI limit (30). Try again tomorrow please."

    profile = get_profile(user_id)
    
    if profile:
        name, u_class, hobbies, goals = profile
        context_str = (
            f"User Name: {name}\n"
            f"Class/Grade: {u_class}\n"
            f"Hobbies: {hobbies}\n"
            f"Goals: {goals}\n"
        )
    else:
        context_str = "User is a student."

    system_prompt = (
        f"You are a calm, supportive AI productivity companion for a student.\n"
        f"Here is the student's profile:\n{context_str}\n"
        "ALWAYS use this information to personalize your advice. "
        "For example, if they ask about stress, relate it to their specific exams or hobbies. "
        "Keep answers concise, motivating, and actionable."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(load_memory(user_id))
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )
        reply = response.choices[0].message.content
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"

    save_memory(user_id, "user", prompt)
    save_memory(user_id, "assistant", reply)
    increment_count(user_id)

    return reply