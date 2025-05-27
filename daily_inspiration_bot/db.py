import sqlite3
from pathlib import Path

# Define database path
DB_PATH = Path("data/inspiration.db")

def init_db():
    """Initialize the SQLite database and create tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            preferences TEXT DEFAULT 'both',
            time_pref TEXT DEFAULT '09:00',
            last_login TEXT
        )
    """)

    # Create content table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content (
            quote_id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            category TEXT CHECK(category IN ('quote', 'fact')) NOT NULL,
            source TEXT
        )
    """)

    # Create favorites table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            user_id INTEGER,
            quote_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(quote_id) REFERENCES content(quote_id)
        )
    """)

    conn.commit()
    conn.close()
def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_or_update_user(user_id, username, preferences="both", time_pref="09:00"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if get_user(user_id):
        cursor.execute(
            "UPDATE users SET username=?, last_login=datetime('now') WHERE user_id=?",
            (username, user_id)
        )
    else:
        cursor.execute(
            "INSERT INTO users (user_id, username, preferences, time_pref, last_login) VALUES (?, ?, ?, ?, datetime('now'))",
            (user_id, username, preferences, time_pref)
        )
    conn.commit()
    conn.close()

def update_preferences(user_id, preferences):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET preferences=? WHERE user_id=?", (preferences, user_id))
    conn.commit()
    conn.close()

def update_time_preference(user_id, time_pref):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET time_pref=? WHERE user_id=?", (time_pref, user_id))
    conn.commit()
    conn.close()
    
def seed_content():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO content (content, category) VALUES (?, ?)", ("Keep pushing forward!", "quote"))
    cursor.execute("INSERT INTO content (content, category) VALUES (?, ?)", ("Bananas are berries, but strawberries aren't!", "fact"))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_content()  # Run this only once
    print("Database initialized with sample data.")

