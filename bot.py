import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from languages import LANGUAGES, MESSAGES

# Environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
SUBSCRIBE_LINK = os.getenv("SUBSCRIBE_LINK")

# Verify environment variables
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing in your .env file")
if not GROUP_ID:
    raise ValueError("GROUP_ID is not set correctly in the .env file.")

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# User session data
user_data = {}

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(name, callback_data=lang)] for lang, name in LANGUAGES.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(MESSAGES["en"]["ask_language"], reply_markup=reply_markup)

# Language selection handler
async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    language = query.data
    user_data[user_id] = {"language": language}

    keyboard = [
        [InlineKeyboardButton(MESSAGES[language]["yes"], callback_data="yes")],
        [InlineKeyboardButton(MESSAGES[language]["no"], callback_data="no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(MESSAGES[language]["ask_age"], reply_markup=reply_markup)

# Age verification handler
async def verify_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    language = user_data.get(user_id, {}).get("language", "en")

    if query.data == "no":
        await query.message.reply_text(MESSAGES[language]["too_young"])
        return

    image_url = "https://upload.wikimedia.org/wikipedia/commons/2/2d/Michelangelo_Bacchus.jpg"
    keyboard = [
        [InlineKeyboardButton(MESSAGES[language]["subscribe"], callback_data="show_subscriptions")],
        [InlineKeyboardButton(MESSAGES[language]["work_with_us"], url="https://www.bacchuscreators.com/")],
        [InlineKeyboardButton(MESSAGES[language]["contact_us"], url="https://api.whatsapp.com/send/?phone=353899430659")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_photo(photo=image_url, caption=MESSAGES[language]["welcome"], reply_markup=reply_markup)

# Subscription menu handler
async def show_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📅 Free 24 hours trial - €Free", callback_data="trial")]
        [InlineKeyboardButton("📅 Monthly - €3", callback_data="subscribe_monthly")],
        [InlineKeyboardButton("📅 Quarterly - €6", callback_data="subscribe_quarterly")],
        [InlineKeyboardButton("📅 Annual - €10", callback_data="subscribe_annual")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text("💳 Choose a subscription plan:", reply_markup=reply_markup)

# Free-text handler: redirect any free text back to /start
async def free_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("")
    await start(update, context)

# Main function
if __name__ == "__main__":
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(select_language, pattern="^(en|pt|de|es|pl|ga)$"))
    application.add_handler(CallbackQueryHandler(verify_age, pattern="^(yes|no)$"))
    application.add_handler(CallbackQueryHandler(show_subscriptions, pattern="^show_subscriptions$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, free_text_handler))

    application.run_polling()

