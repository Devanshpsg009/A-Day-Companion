import os, sqlite3, json
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
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS ai_usage (user_id INTEGER, day TEXT, count INTEGER, PRIMARY KEY (user_id, day))")
        conn.execute("CREATE TABLE IF NOT EXISTS ai_memory (user_id INTEGER, role TEXT, content TEXT)")

def load_keywords():
    try:
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
            return set(w.strip().lower() for w in f if w.strip())
    except FileNotFoundError: return set()

ALLOWED_KEYWORDS = load_keywords()

def allowed_topic(text):
    if not ALLOWED_KEYWORDS: return True
    return any(k in text.lower() for k in ALLOWED_KEYWORDS)

def daily_count(user_id):
    init_db()
    with sqlite3.connect(DB_FILE) as conn:
        row = conn.execute("SELECT count FROM ai_usage WHERE user_id=? AND day=?", (user_id, date.today().isoformat())).fetchone()
        return row[0] if row else 0

def increment_count(user_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO ai_usage (user_id, day, count) VALUES (?, ?, 1) ON CONFLICT(user_id, day) DO UPDATE SET count = count + 1", (user_id, date.today().isoformat()))

def save_memory(user_id, role, content):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO ai_memory VALUES (?, ?, ?)", (user_id, role, content))

def load_memory(user_id, limit=10):
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute("SELECT role, content FROM ai_memory WHERE user_id=? ORDER BY rowid DESC LIMIT ?", (user_id, limit)).fetchall()
        return [{"role": r, "content": c} for r, c in reversed(rows)]

def get_latest_journal_context(user_id):
    if not os.path.exists(JOURNAL_DB): return None
    try:
        with sqlite3.connect(JOURNAL_DB) as conn:
            row = conn.execute("SELECT content, mood, score, date FROM journal WHERE user_id=? ORDER BY date DESC LIMIT 1", (user_id,)).fetchone()
            if row:
                return f"LATEST JOURNAL ({row[3]}): Mood: {row[1]} ({row[2]}/10). Content: {row[0][:500]}"
    except: return None
    return None

def ask_ai(user_id, prompt):
    init_db()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "AI Error: API Key missing."
    if daily_count(user_id) >= MAX_DAILY_PROMPTS: return "Daily limit reached (30)."
    
    client = Groq(api_key=api_key)
    profile = get_profile(user_id)
    ctx = f"User: {profile[0]}, Class: {profile[1]}, Hobbies: {profile[2]}, Goals: {profile[3]}" if profile else "User is a student."
    j_ctx = get_latest_journal_context(user_id)
    
    sys_msg = f"You are a supportive AI productivity companion. Profile: {ctx}\n"
    if j_ctx: sys_msg += f"\nContext: {j_ctx}\nBe empathetic to this mood."
    sys_msg += "\nKeep answers concise and actionable."

    msgs = [{"role": "system", "content": sys_msg}]
    msgs.extend(load_memory(user_id))
    msgs.append({"role": "user", "content": prompt})

    try:
        reply = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs).choices[0].message.content
        save_memory(user_id, "user", prompt)
        save_memory(user_id, "assistant", reply)
        increment_count(user_id)
        return reply
    except Exception as e: return f"Connection Error: {str(e)}"

def analyze_sentiment(user_id, journal_text):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or not journal_text or len(journal_text.split()) < 5: return None
    
    client = Groq(api_key=api_key)
    prompt = f"Journal Entry: '{journal_text}'\nReturn ONLY raw JSON with keys: mood (str), score (1-10), advice (str). Be warm and motivating."
    
    try:
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}]).choices[0].message.content.strip()
        return json.loads(res.replace("```json", "").replace("```", ""))
    except: return None