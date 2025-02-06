import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime
import requests


load_dotenv()

# Retrieve sensitive info from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL")
print(f"Loaded BOT_TOKEN: {BOT_TOKEN}")

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

# Main function
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_expense))

    # Start polling
    application.run_polling()

if __name__ == "__main__":
    main()
