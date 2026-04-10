import os
import sqlite3
import json
from datetime import date
from dotenv import load_dotenv
from openai import OpenAI
from backend.profile_db import get_profile

load_dotenv()

MAX_DAILY_PROMPTS = 30
DB_FILE = "ai_memory.db"
JOURNAL_DB = "journal.db"


def init_db():
    """Create the AI database tables if they are missing."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS ai_usage (user_id INTEGER, day TEXT, count INTEGER, PRIMARY KEY (user_id, day))"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS ai_memory (user_id INTEGER, role TEXT, content TEXT)"
        )


def daily_count(user_id):
    """Return the number of AI prompts used by the user today."""
    init_db()
    with sqlite3.connect(DB_FILE) as conn:
        row = conn.execute(
            "SELECT count FROM ai_usage WHERE user_id=? AND day=?",
            (user_id, date.today().isoformat()),
        ).fetchone()
        if row:
            return row[0]
    return 0


def increment_count(user_id):
    """Increase the prompt count for the current user and day."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT INTO ai_usage (user_id, day, count) VALUES (?, ?, 1) "
            "ON CONFLICT(user_id, day) DO UPDATE SET count = count + 1",
            (user_id, date.today().isoformat()),
        )


def save_memory(user_id, role, content):
    """Save a chat message for the user."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT INTO ai_memory VALUES (?, ?, ?)",
            (user_id, role, content),
        )


def load_memory(user_id, limit=10):
    """Load the latest AI chat history for the user."""
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute(
            "SELECT role, content FROM ai_memory WHERE user_id=? ORDER BY rowid DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()

    messages = []
    for role, content in reversed(rows):
        messages.append({"role": role, "content": content})
    return messages


def get_latest_journal_context(user_id):
    """Return the latest journal entry summary for AI context."""
    if not os.path.exists(JOURNAL_DB):
        return None

    try:
        with sqlite3.connect(JOURNAL_DB) as conn:
            row = conn.execute(
                "SELECT content, mood, score, date FROM journal WHERE user_id=? ORDER BY date DESC LIMIT 1",
                (user_id,),
            ).fetchone()

            if row:
                journal_text, journal_mood, journal_score, journal_date = row
                return (
                    f"LATEST JOURNAL ({journal_date}): Mood: {journal_mood} "
                    f"({journal_score}/10). Content: {journal_text[:500]}"
                )
    except Exception:
        return None

    return None


# ------------------ OPENROUTER SETUP ------------------

def get_client():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None

    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )


# ------------------ MAIN AI FUNCTION ------------------

def ask_ai(user_id, prompt):
    """Send the prompt to the AI and return the assistant reply."""
    init_db()

    client = get_client()
    if not client:
        return "AI Error: API Key missing."

    if daily_count(user_id) >= MAX_DAILY_PROMPTS:
        return "Daily limit reached (30)."

    profile = get_profile(user_id)

    if profile:
        profile_text = (
            f"User: {profile[0]}, Class: {profile[1]}, Hobbies: {profile[2]}, Goals: {profile[3]}"
        )
    else:
        profile_text = "User is a student."

    journal_context = get_latest_journal_context(user_id)

    system_message = "You are a supportive AI productivity companion. "
    system_message += f"Profile: {profile_text}\n"

    if journal_context:
        system_message += f"\nContext: {journal_context}\nBe empathetic to this mood."

    system_message += (
        "\nKeep answers concise and actionable. "
        "If the user asks anything unrelated to student life, studies, productivity, education, or wellbeing, "
        "respond politely with: Sorry, I can only help with study-related topics like exams, assignments, learning, and productivity. "
        "Do not try to answer off-topic or inappropriate questions."
    )

    messages = [{"role": "system", "content": system_message}]
    messages.extend(load_memory(user_id))
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",  # 🔥 good + cheap model
            messages=messages,
            temperature=0.7,
            max_tokens=600,
        )

        reply = response.choices[0].message.content

        save_memory(user_id, "user", prompt)
        save_memory(user_id, "assistant", reply)
        increment_count(user_id)

        return reply

    except Exception as error:
        return f"Connection Error: {str(error)}"


# ------------------ SENTIMENT ANALYSIS ------------------

def analyze_sentiment(user_id, journal_text):
    """Ask AI to analyze journal mood and return structured feedback."""

    if not journal_text or len(journal_text.split()) < 5:
        return None

    client = get_client()
    if not client:
        return None

    prompt = (
        f"Journal Entry: '{journal_text}'\n"
        "Return ONLY raw JSON with keys: mood (str), score (1-10), advice (str). Be warm and motivating."
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=250,
        )

        text_response = response.choices[0].message.content.strip()

        # Clean markdown if present
        cleaned_response = text_response.replace("```json", "").replace("```", "").strip()

        return json.loads(cleaned_response)

    except Exception:
        return None