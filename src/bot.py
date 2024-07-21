from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ChatJoinRequestHandler
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define the bot token and MongoDB connection string
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MONGODB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')

# Connect to MongoDB
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client['telegram_bot_db']

# Define command handlers
async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf'Hi {user.mention_html()}!',
    )

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('Help!')

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    text = update.message.text
    logger.info(f"Received message: {text}")
    await update.message.reply_text(f'You said: {text}')

async def handle_join_request(update: Update, context: CallbackContext) -> None:
    if update.chat_join_request:
        chat_id = update.chat_join_request.chat.id
        user_id = update.chat_join_request.from_user.id
        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
        logger.info(f"Approved join request from {user_id}")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Handle join requests
    application.add_handler(ChatJoinRequestHandler(handle_join_request))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
