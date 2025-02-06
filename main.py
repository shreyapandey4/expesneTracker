import os
from dotenv import load_dotenv
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime
import requests
from flask import Flask
from threading import Thread

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL")  

# Initialize Flask app
app = Flask(__name__)

# Function to add expenses
async def add_expense(update: Update, context: CallbackContext):
    try:
        data = context.args
        if len(data) < 2:
            await update.message.reply_text("Usage: /add <amount> <category> [optional notes]")
            return

        amount = data[0]
        category = data[1]
        notes = " ".join(data[2:]) if len(data) > 2 else ""

        # Get current date and time
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        # Send data to Google Sheets via Apps Script Web App
        payload = {
            "date": date,
            "time": time,
            "amount": amount,
            "category": category,
            "notes": notes
        }
        response = requests.post(WEB_APP_URL, json=payload)

        if response.status_code == 200:
            await update.message.reply_text(f"✅ Expense added: {amount} in {category}")
        else:
            await update.message.reply_text(f"⚠️ Error: {response.text}")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

# Function to start the bot
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Use /add <amount> <category> [optional notes] to log an expense.")

# Set up the bot and start polling
def start_bot():
    # Create an Application instance
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_expense))

    # Start polling (blocking call)
    application.run_polling()

# Simple route to check if the server is running
@app.route('/')
def index():
    return "Bot is running."

# Main function to start the Flask server and the Telegram bot
def main():
    # Run the Flask server in a separate thread
    def run_flask():
        port = int(os.environ.get("PORT", 5080))
        app.run(host="0.0.0.0", port=port)

    # Start Flask server in background thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Run the Telegram bot in the main thread
    start_bot()

if __name__ == "__main__":
    main()
