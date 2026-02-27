import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading
import os
import time
import json

# 🔑 SETTINGS (ENV TOKEN)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6411315434  # Apna Telegram ID

bot = telebot.TeleBot(BOT_TOKEN)

# 📁 Persistent Database File
DATA_FILE = "users.json"

# Load users from file (restart safe)
def load_users():
    try:
        with open(DATA_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

# Save users to file (permanent)
def save_users():
    with open(DATA_FILE, "w") as f:
        json.dump(list(users), f)

users = load_users()
broadcast_mode = set()

# 🌐 Dummy Web Server (Render + UptimeRobot)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running successfully!"

# 🎛 Main Menu (2 Buttons per Row)
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📘 Trading Basics", "📊 Market Concepts")
    markup.row("🧠 Risk Management", "📈 Chart Education")
    markup.row("❓ FAQ", "📩 Contact Support")
    markup.row("🔼 Open Menu")
    return markup

# 🚀 START + ADMIN NOTIFY + SINGLE PIN + PERMANENT SAVE
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username

    disclaimer = """⚠️ Disclaimer

This bot is created for educational purposes only.
Trading involves financial risk and may result in loss.
We do not provide financial advice, signals, or guaranteed results.

By continuing, you confirm that you understand and accept this."""

    is_new_user = user_id not in users

    # 🧠 Save user permanently
    if is_new_user:
        users.add(user_id)
        save_users()

        total_users = len(users)

        user_info = f"""🚀 New User Started the Bot!

👤 Name: {first_name}
🆔 User ID: {user_id}
🔗 Username: @{username if username else 'No Username'}

📊 Total Bot Users: {total_users}"""

        try:
            bot.send_message(ADMIN_ID, user_info)
        except Exception as e:
            print(f"Admin notify error: {e}")

    # Send disclaimer ONLY once
    sent_msg = bot.send_message(
        message.chat.id,
        disclaimer,
        reply_markup=main_menu()
    )

    # Pin only first time (no double pin)
    if is_new_user:
        try:
            bot.pin_chat_message(
                chat_id=message.chat.id,
                message_id=sent_msg.message_id,
                disable_notification=True
            )
        except:
            pass

# 📢 ADMIN BROADCAST COMMAND
@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
    
    broadcast_mode.add(message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"📢 Send the message to broadcast.\n\n👥 Total Users: {len(users)}\n\nSend /cancel to stop."
    )

# ❌ Cancel Broadcast
@bot.message_handler(commands=['cancel'])
def cancel_broadcast(message):
    if message.from_user.id in broadcast_mode:
        broadcast_mode.remove(message.from_user.id)
        bot.send_message(message.chat.id, "❌ Broadcast cancelled.")

# 📡 HANDLE BROADCAST (TEXT + MEDIA)
@bot.message_handler(func=lambda message: message.from_user.id in broadcast_mode, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def handle_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return

    total = len(users)
    success = 0
    failed = 0

    bot.send_message(message.chat.id, f"📢 Broadcasting to {total} users...")

    for user_id in list(users):
        try:
            bot.copy_message(user_id, message.chat.id, message.message_id)
            success += 1
        except:
            failed += 1

    broadcast_mode.remove(message.from_user.id)

    bot.send_message(
        message.chat.id,
        f"""✅ Broadcast Completed!

👥 Total Users: {total}
📤 Sent: {success}
❌ Failed: {failed}"""
    )

# 🔼 Reopen Menu Button
@bot.message_handler(func=lambda message: message.text == "🔼 Open Menu")
def reopen_menu(message):
    bot.send_message(
        message.chat.id,
        "📚 Main Menu Opened. Choose a topic below:",
        reply_markup=main_menu()
    )

# 📘 Trading Basics
@bot.message_handler(func=lambda message: message.text == "📘 Trading Basics")
def trading_basics(message):
    text = """📘 Trading Basics

Trading is the process of buying and selling assets in financial markets.

Key concepts:
• Buy & Sell
• Price movement
• Timeframes
• Candlestick charts

Trading is not gambling and does not guarantee profit.
Education and discipline are important."""
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

# 📊 Market Concepts
@bot.message_handler(func=lambda message: message.text == "📊 Market Concepts")
def market_concepts(message):
    text = """📊 Market Concepts

Markets move based on supply and demand.

Common concepts:
• Uptrend – higher highs and higher lows
• Downtrend – lower highs and lower lows
• Range – sideways movement

Understanding market structure helps traders analyze price behavior."""
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

# 🧠 Risk Management
@bot.message_handler(func=lambda message: message.text == "🧠 Risk Management")
def risk_management(message):
    text = """🧠 Risk Management

Risk management helps protect trading capital."""
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

# 📈 Chart Education
@bot.message_handler(func=lambda message: message.text == "📈 Chart Education")
def chart_education(message):
    text = """📈 Chart Education

Charts help visualize price movement and market structure."""
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

# ❓ FAQ
@bot.message_handler(func=lambda message: message.text == "❓ FAQ")
def faq(message):
    text = """❓ Frequently Asked Questions

This bot provides educational content only.
No signals. No guarantees. No financial advice."""
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

# 📩 Contact Support
@bot.message_handler(func=lambda message: message.text == "📩 Contact Support")
def support(message):
    text = """📩 Contact Support

For general questions related to the educational content,
please use this bot menu or review the FAQ section.

Please note:
We do not provide personal trading advice.

For educational purposes only - no guaranteed results.☝🏻
@jjtrader_00"""
    inline_markup = InlineKeyboardMarkup()
    inline_markup.add(
        InlineKeyboardButton(
            text="📚 LEARN MORE",
            url="https://t.me/+zOZC00MmUa40YmQ1"
        )
    )
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)
    bot.send_message(message.chat.id, "📚 Back to Main Menu:", reply_markup=main_menu())

print("Bot Running with Persistent Users + 409 Fix + Stable Polling")

# 🤖 409 CONFLICT FIX + SAFE POLLING (VERY IMPORTANT)
def run_bot():
    while True:
        try:
            bot.remove_webhook()  # 🔥 prevents 409 conflict
            time.sleep(1)
            print("Bot polling started safely...")
            bot.infinity_polling(
                timeout=60,
                long_polling_timeout=60,
                skip_pending=True
            )
        except Exception as e:
            print(f"Bot crashed or conflict: {e}")
            time.sleep(5)

# Run bot in background thread (Render safe)
threading.Thread(target=run_bot, daemon=True).start()

# Bind PORT for Render (MANDATORY)
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
