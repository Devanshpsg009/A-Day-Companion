import os
import sqlite3
import json
from datetime import date
from dotenv import load_dotenv
from groq import Groq
from backend.profile_db import get_profile 

load_dotenv()

MAX_DAILY_PROMPTS = 30
KEYWORDS_FILE = "backend/allowed_keywords.txt"
DB_FILE = "ai_memory.db"
JOURNAL_DB = "journal.db"

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
    if not ALLOWED_KEYWORDS: return True
    t = text.lower()
    return any(k in t for k in ALLOWED_KEYWORDS)

def daily_count(user_id):
    init_db()
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT count FROM ai_usage WHERE user_id=? AND day=?", (user_id, today))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def increment_count(user_id):
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ai_usage (user_id, day, count) VALUES (?, ?, 1)
        ON CONFLICT(user_id, day) DO UPDATE SET count = count + 1
    """, (user_id, today))
    conn.commit()
    conn.close()

def save_memory(user_id, role, content):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO ai_memory VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()
    conn.close()

def load_memory(user_id, limit=10):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT role, content FROM ai_memory WHERE user_id=? ORDER BY rowid DESC LIMIT ?", (user_id, limit))
    rows = cur.fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in reversed(rows)]

def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def get_latest_journal_context(user_id):
    """Fetches the latest journal entry to give the AI context on how the user is feeling."""
    if not os.path.exists(JOURNAL_DB):
        return None
        
    try:
        conn = sqlite3.connect(JOURNAL_DB)
        cur = conn.cursor()
        cur.execute("""
            SELECT content, mood, score, date 
            FROM journal 
            WHERE user_id=? 
            ORDER BY date DESC LIMIT 1
        """, (user_id,))
        row = cur.fetchone()
        conn.close()
        
        if row:
            content, mood, score, entry_date = row
            mood_str = f"{mood} ({score}/10)" if mood else "Unknown"
            return (
                f"LATEST JOURNAL ENTRY ({entry_date}):\n"
                f"Mood: {mood_str}\n"
                f"Content: {content[:500]}"
            )
    except Exception as e:
        print(f"Journal Read Error: {e}")
        return None
    return None

def ask_ai(user_id, prompt):
    init_db()
    
    client = get_client()
    if not client:
        return "AI Error: API Key missing. Please restart the app and enter your key."

    if daily_count(user_id) >= MAX_DAILY_PROMPTS:
        return "You've reached today's AI limit (30). Try again tomorrow please."
    profile = get_profile(user_id)
    if profile:
        name, u_class, hobbies, goals = profile
        context_str = f"User: {name}, Class: {u_class}, Hobbies: {hobbies}, Goals: {goals}"
    else:
        context_str = "User is a student."
    journal_context = get_latest_journal_context(user_id)
    
    journal_instruction = ""
    if journal_context:
        journal_instruction = (
            f"\n\n[IMPORTANT CONTEXT FROM USER'S JOURNAL]\n"
            f"{journal_context}\n"
            f"INSTRUCTION: The user might be feeling this way right now. "
            f"Be empathetic to their mood mentioned above."
        )

    system_prompt = (
        f"You are a supportive, warm AI productivity companion.\n"
        f"Profile: {context_str}"
        f"{journal_instruction}\n\n"
        "Keep answers concise, motivating, and actionable."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(load_memory(user_id))
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages)
        reply = response.choices[0].message.content
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"

    save_memory(user_id, "user", prompt)
    save_memory(user_id, "assistant", reply)
    increment_count(user_id)
    return reply

def analyze_sentiment(user_id, journal_text):
    if not journal_text or len(journal_text.split()) < 5:
        return None

    client = get_client()
    if not client:
        return None

    init_db()
    prompt = f"""
    You are a supportive, encouraging friend reading a student's journal.
    
    Journal Entry: "{journal_text}"
    
    Return ONLY a raw JSON object (no markdown) with keys: 
    1. mood (string)
    2. score (1-10)
    3. advice (string). 
    
    IMPORTANT: Write the advice DIRECTLY to the student using "You". 
    Be highly motivating, warm, and optimistic. Never use the third person.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        
        data = json.loads(content)
        return data
    except Exception as e:
        print(f"Sentiment Error: {e}")
        return None