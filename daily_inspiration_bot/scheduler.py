import random
import sqlite3
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot
from config import BOT_TOKEN
from pathlib import Path
import asyncio
from pytz import timezone

DB_PATH = Path("data/inspiration.db")
bot = Bot(token=BOT_TOKEN)
scheduler = BackgroundScheduler()

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, preferences, time_pref FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_random_content(category):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM content WHERE category=?", (category,))
    results = cursor.fetchall()
    conn.close()
    return random.choice(results)[0] if results else None

async def send_daily_message(user_id, preferences):
    messages = []
    if preferences in ["quotes", "both"]:
        quote = get_random_content("quote")
        if quote:
            messages.append(f"💬 *Quote*: {quote}")
    if preferences in ["facts", "both"]:
        fact = get_random_content("fact")
        if fact:
            messages.append(f"💡 *Fun Fact*: {fact}")
    for msg in messages:
        await bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
    print(f"📨 Sent daily message to user {user_id} at {datetime.now()}")

def schedule_jobs():
    # Remove existing jobs before adding new ones
    scheduler.remove_all_jobs()
    users = get_all_users()
    for user_id, preferences, time_pref in users:
        hour, minute = map(int, time_pref.split(":"))
        scheduler.add_job(
            lambda uid=user_id, pref=preferences: asyncio.run(send_daily_message(uid, pref)),
            "cron",
            hour=hour,
            minute=minute,
            id=str(user_id),
            timezone="UTC"
        )
        print(f"⏰ Scheduled message for user {user_id} at {time_pref}")

# Start scheduler only once (call this when your bot starts)
def start_scheduler():
    if not scheduler.running:
        scheduler.start()
