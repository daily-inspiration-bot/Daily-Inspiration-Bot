import random
import sqlite3
import re
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from config import BOT_TOKEN
from db import update_time_preference, get_user
from pathlib import Path
import asyncio
import sys
from pytz import timezone

DB_PATH = Path("data/inspiration.db")
bot = Bot(token=BOT_TOKEN)
scheduler = BackgroundScheduler()

# --- Content and Messaging Functions ---
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

# --- Scheduler Functions ---
def schedule_jobs():
    scheduler.remove_all_jobs()
    users = get_all_users()

    for user_id, preferences, time_pref in users:
        hour, minute = map(int, time_pref.split(":"))

        async def job(uid=user_id, pref=preferences):
            await send_daily_message(uid, pref)

        def run_async_job():
            asyncio.run(job())

        scheduler.add_job(
            run_async_job,
            "cron",
            hour=hour,
            minute=minute,
            id=str(user_id),
            timezone=timezone("Asia/Kolkata")
        )

        print(f"⏰ Scheduled message for user {user_id} at {time_pref}")

def start_scheduler():
    if not scheduler.running:
        scheduler.start()

# --- Telegram Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🕒 When would you like to receive your daily message? (Format: HH:MM, 24-hour)")

async def handle_time_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    time_text = update.message.text.strip()

    if not re.match(r"^\d{2}:\d{2}$", time_text):
        await update.message.reply_text("⏰ Please send time in 24-hour format like `09:30` or `18:45`.", parse_mode="Markdown")
        return

    try:
        hour, minute = map(int, time_text.split(":"))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError()
    except ValueError:
        await update.message.reply_text("⚠️ Invalid time. Please use format like `08:00` or `20:30`.", parse_mode="Markdown")
        return

    update_time_preference(user_id, time_text)
    schedule_jobs()
    await update.message.reply_text(f"✅ Your daily message time has been set to {time_text}.")
    print(f"🔁 Rescheduled job for user {user_id} at new time {time_text}")

async def send_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"👤 Your user ID is: {user_id}")

# --- Main ---
async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^\d{2}:\d{2}$"), handle_time_input))
    application.add_handler(CommandHandler("id", send_user_id))

    # Scheduler setup
    start_scheduler()
    schedule_jobs()

    print("🚀 Bot is running...")
    return application

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application = loop.run_until_complete(main())
    application.run_polling()
