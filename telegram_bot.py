import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv
from competition_handler import join_competition, handle_answer, schedule_competition

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
    try:
        print("Initializing updater...")
        updater = Updater(BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        print("Registering handlers...")
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

        # Register competition handlers
        dispatcher.add_handler(CommandHandler("join", join_competition))
        dispatcher.add_handler(CommandHandler("answer", handle_answer))

        # Schedule the competition (starts 1 minute from now for testing)
        from datetime import datetime, timedelta
        current_time = datetime.now()
        test_time = current_time + timedelta(minutes=1)  # Starts in 1 minute
        schedule_competition(dispatcher, chat_id=-1, hour=test_time.hour, minute=test_time.minute)

        print("Starting bot...")
        updater.start_polling()
        updater.idle()
    except telegram.error.Conflict as e:
        logger.error("Bot conflict detected! Please stop all other instances of the bot.")
    except Exception as e:
        logger.exception("An unexpected error occurred: %s", e)

if __name__ == '__main__':
    main()
