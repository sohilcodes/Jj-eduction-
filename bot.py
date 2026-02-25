from flask import Flask
import threading
import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# 🔑 SETTINGS
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6411315434  # Apna Telegram ID

bot = telebot.TeleBot(BOT_TOKEN)

# 🌐 Dummy Web Server for Render + UptimeRobot
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running successfully!"

users = set()

# 🎛 Main Menu (2 Buttons per Row)
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📘 Trading Basics", "📊 Market Concepts")
    markup.row("🧠 Risk Management", "📈 Chart Education")
    markup.row("❓ FAQ", "📩 Contact Support")
    markup.row("🔼 Open Menu")
    return markup

# 🚀 START + ADMIN NOTIFY + AUTO PIN (FIRST TIME ONLY)
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

    # New user notify + first time pin logic
    if user_id not in users:
        users.add(user_id)

        user_info = f"""🚀 New User Started the Bot!

👤 Name: {first_name}
🆔 User ID: {user_id}
🔗 Username: @{username if username else 'No Username'}"""
        try:
            bot.send_message(ADMIN_ID, user_info)
        except:
            pass

        # Send disclaimer
        sent_msg = bot.send_message(
            message.chat.id,
            disclaimer,
            reply_markup=main_menu()
        )

        # 🔒 Auto pin only first time
        try:
            bot.pin_chat_message(
                chat_id=message.chat.id,
                message_id=sent_msg.message_id,
                disable_notification=True
            )
        except:
            pass
    else:
        # Old users - no pin again
        bot.send_message(
            message.chat.id,
            disclaimer,
            reply_markup=main_menu()
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

Risk management helps protect trading capital.

Basic principles:
• Never risk money you cannot afford to lose
• No strategy works 100% of the time
• Emotional control is important
• Discipline matters more than profit

Professional traders focus on risk first, profit second."""
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

# 📈 Chart Education
@bot.message_handler(func=lambda message: message.text == "📈 Chart Education")
def chart_education(message):
    text = """📈 Chart Education

Charts help visualize price movement.

Common tools:
• Candlestick patterns
• Support & resistance
• Indicators (RSI, Moving Average)

Indicators and patterns do not predict the market.
They are tools to help understand price behavior."""
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

# ❓ FAQ
@bot.message_handler(func=lambda message: message.text == "❓ FAQ")
def faq(message):
    text = """❓ Frequently Asked Questions

Q: Do you provide trading signals?
A: No. This bot is for educational purposes only.

Q: Can trading guarantee profit?
A: No. Trading always involves risk.

Q: Is this financial advice?
A: No. All content is educational.

Q: Who is this bot for?
A: Beginners who want to learn trading basics."""
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

# 📩 Contact Support (WITH INLINE BUTTON + USERNAME + CHANNEL REDIRECT)
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
    learn_btn = InlineKeyboardButton(
        text="📚 LEARN MORE",
        url="https://t.me/+zOZC00MmUa40YmQ1"
    )
    inline_markup.add(learn_btn)

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=inline_markup
    )

    bot.send_message(
        message.chat.id,
        "📚 Back to Main Menu:",
        reply_markup=main_menu()
    )

print("Bot Running with Auto Pin Disclaimer + Admin Notify + Inline Channel Button + Menu System")

def run_bot():
    print("Bot Running with Auto Pin Disclaimer + Admin Notify + Inline Channel Button + Menu System")
    bot.infinity_polling()

# Run bot in separate thread (for Web Service)
threading.Thread(target=run_bot).start()

# Bind port for Render Web Service (IMPORTANT)
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
