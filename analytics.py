import json
import os
import sqlite3
from datetime import datetime, timedelta
from config import TWILIO_TO, TWILIO_FROM
from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

DB_FILE = "data/analytics.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts_found (
            id TEXT PRIMARY KEY,
            subreddit TEXT,
            score INTEGER,
            keywords TEXT,
            competitor_mention INTEGER,
            found_at TEXT,
            post_type TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS responses_sent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT,
            subreddit TEXT,
            mode TEXT,
            method TEXT,
            sent_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS trends (
            keyword TEXT,
            subreddit TEXT,
            count INTEGER,
            week TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_post_found(post):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT OR IGNORE INTO posts_found
            (id, subreddit, score, keywords, competitor_mention, found_at, post_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            post.get("id"),
            post.get("subreddit"),
            post.get("score", 0),
            json.dumps([k[0] for k in post.get("matched_keywords", [])]),
            1 if post.get("competitor_mention") else 0,
            datetime.now().isoformat(),
            post.get("type", "post"),
        ))
        conn.commit()
    except Exception as e:
        print(f"[Analytics] DB error: {e}")
    finally:
        conn.close()

def log_response_sent(post_id, subreddit, mode, method):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO responses_sent (post_id, subreddit, mode, method, sent_at)
        VALUES (?, ?, ?, ?, ?)
    """, (post_id, subreddit, mode, method, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_weekly_stats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()

    c.execute("SELECT COUNT(*) FROM posts_found WHERE found_at > ?", (week_ago,))
    total_found = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM responses_sent WHERE sent_at > ?", (week_ago,))
    total_sent = c.fetchone()[0]

    c.execute("""
        SELECT subreddit, COUNT(*) as cnt
        FROM posts_found WHERE found_at > ?
        GROUP BY subreddit ORDER BY cnt DESC LIMIT 5
    """, (week_ago,))
    top_subs = c.fetchall()

    c.execute("""
        SELECT subreddit, COUNT(*) as cnt
        FROM responses_sent WHERE sent_at > ?
        GROUP BY subreddit ORDER BY cnt DESC LIMIT 5
    """, (week_ago,))
    top_converting = c.fetchall()

    conn.close()
    return {
        "total_found": total_found,
        "total_sent": total_sent,
        "top_subreddits": top_subs,
        "top_converting": top_converting,
    }

def send_weekly_report():
    stats = get_weekly_stats()
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    message = "📊 PEPTI REDDIT WEEKLY REPORT\n\n"
    message += f"Posts found: {stats['total_found']}\n"
    message += f"Responses sent: {stats['total_sent']}\n\n"

    if stats['top_subreddits']:
        message += "Top subreddits this week:\n"
        for sub, count in stats['top_subreddits']:
            message += f"  r/{sub}: {count} posts\n"

    if stats['top_converting']:
        message += "\nTop converting subreddits:\n"
        for sub, count in stats['top_converting']:
            message += f"  r/{sub}: {count} responses\n"

    try:
        twilio_client.messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=TWILIO_TO,
        )
        print("[Analytics] Weekly report sent")
    except Exception as e:
        print(f"[Analytics] Report send error: {e}")
