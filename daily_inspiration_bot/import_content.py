import sqlite3
from pathlib import Path

DB_PATH = Path("data/inspiration.db")
QUOTES_PATH = Path("content/quotes.txt")
FACTS_PATH = Path("content/facts.txt")

def insert_content(file_path, category):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()]
        for line in lines:
            cursor.execute("INSERT INTO content (content, category) VALUES (?, ?)", (line, category))
    conn.commit()
    conn.close()
    print(f"✅ Imported {len(lines)} {category}s.")

def main():
    if not DB_PATH.exists():
        print("❌ Database not found. Please run db.py first.")
        return
    insert_content(QUOTES_PATH, "quote")
    insert_content(FACTS_PATH, "fact")

if __name__ == "__main__":
    main()
