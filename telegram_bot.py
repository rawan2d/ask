import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv
from competition_handler import join_competition, handle_answer, schedule_competition

# Load environment variables from .env file
load_dotenv()

# Get the bot token from the .env file
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in the .env file")

# Define a simple command (e.g., /start)
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your bot. Use /join to join a competition or /answer <your_answer> to respond to a question!')

# Handle text messages
def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'You said: {update.message.text}')

def main():
    # Initialize the updater and dispatcher
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Register command and message handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Register competition handlers
    dispatcher.add_handler(CommandHandler("join", join_competition))
    dispatcher.add_handler(CommandHandler("answer", handle_answer))

    # Schedule the competition (starts at 10 PM server time)
    chat_id = -1  # Replace with your specific chat ID
    schedule_competition(dispatcher, chat_id, hour=22, minute=0)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
