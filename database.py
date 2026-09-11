"""
database.py
Lightweight SQLite persistence layer for EmotiSense Pro.
Stores every analyzed entry so we can power the History and
Statistics dashboards without any external database service.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from collections import Counter
import re

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "emotisense.db")

STOPWORDS = {
    "the", "a", "an", "is", "am", "are", "was", "were", "to", "of", "and",
    "in", "on", "for", "it", "i", "my", "me", "this", "that", "at", "so",
    "with", "but", "be", "have", "has", "had", "not", "no", "just", "you",
    "he", "she", "they", "we", "as", "if", "or", "do", "did", "does", "up",
    "out", "too", "very", "can", "will", "would", "could", "about", "than",
}


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            top_emotion TEXT NOT NULL,
            top_score REAL NOT NULL,
            all_scores TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_entry(text, top_emotion, top_score, all_scores_json):
    conn = get_connection()
    conn.execute(
        "INSERT INTO entries (text, top_emotion, top_score, all_scores, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (text, top_emotion, top_score, all_scores_json, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_recent_entries(limit=50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM entries ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_entry(entry_id):
    conn = get_connection()
    conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()


def clear_all():
    conn = get_connection()
    conn.execute("DELETE FROM entries")
    conn.commit()
    conn.close()


def get_all_entries():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM entries ORDER BY id ASC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_emotion_distribution():
    """Count how many times each emotion was the top prediction."""
    entries = get_all_entries()
    counts = Counter(e["top_emotion"] for e in entries)
    return dict(counts)


def get_daily_trend(days=7):
    """Return count of entries per day for the last N days, per emotion."""
    entries = get_all_entries()
    today = datetime.utcnow().date()
    date_range = [today - timedelta(days=i) for i in range(days - 1, -1, -1)]
    trend = {str(d): Counter() for d in date_range}

    for e in entries:
        entry_date = datetime.fromisoformat(e["created_at"]).date()
        key = str(entry_date)
        if key in trend:
            trend[key][e["top_emotion"]] += 1

    return {
        "labels": [d.strftime("%a %d") for d in date_range],
        "raw_dates": [str(d) for d in date_range],
        "series": trend,
    }


def get_top_words(emotion=None, limit=10):
    """Simple frequency count of meaningful words, optionally filtered by emotion."""
    entries = get_all_entries()
    if emotion:
        entries = [e for e in entries if e["top_emotion"] == emotion]

    word_counter = Counter()
    for e in entries:
        words = re.findall(r"[a-zA-Z']+", e["text"].lower())
        words = [w for w in words if w not in STOPWORDS and len(w) > 2]
        word_counter.update(words)

    return word_counter.most_common(limit)


def get_summary_stats():
    entries = get_all_entries()
    if not entries:
        return {
            "total_entries": 0,
            "most_common_emotion": None,
            "avg_confidence": 0,
            "first_entry_date": None,
        }

    distribution = get_emotion_distribution()
    most_common = max(distribution, key=distribution.get) if distribution else None
    avg_conf = sum(e["top_score"] for e in entries) / len(entries)

    return {
        "total_entries": len(entries),
        "most_common_emotion": most_common,
        "avg_confidence": round(avg_conf, 1),
        "first_entry_date": entries[0]["created_at"][:10],
    }
