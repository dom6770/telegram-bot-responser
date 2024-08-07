import os, json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters

# Load environment variables from .env file
load_dotenv()

# Set up your bot token and other variables from the environment
BOT_TOKEN = os.getenv('BOT_TOKEN')
TRIGGER_WORDS = os.getenv('TRIGGER_WORDS').split(',')
ADMIN_USERS = os.getenv('ADMIN_USERS').split(',')
STATS_FILE = os.getenv('STATS_FILE')

RESPONSE_MESSAGE = os.getenv('RESPONSE_MESSAGE')
RESPONSE_GIF_URL = os.getenv('RESPONSE_GIF_URL')

SPECIAL_RESPONSE_NUMBER_1 = os.getenv('SPECIAL_RESPONSE_NUMBER_1')
SPECIAL_RESPONSE_MESSAGE_1 = os.getenv('SPECIAL_RESPONSE_MESSAGE_1')
SPECIAL_RESPONSE_GIF_URL_1 = os.getenv('SPECIAL_RESPONSE_GIF_URL_1')

SPECIAL_RESPONSE_NUMBER_2 = os.getenv('SPECIAL_RESPONSE_NUMBER_2')
SPECIAL_RESPONSE_MESSAGE_2 = os.getenv('SPECIAL_RESPONSE_MESSAGE_2')
SPECIAL_RESPONSE_GIF_URL_2 = os.getenv('SPECIAL_RESPONSE_GIF_URL_2')

# Load the statistics from the JSON file
def load_statistics():
    try:
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save the statistics to the JSON file
def save_statistics(statistics):
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    with open(STATS_FILE, 'w') as f:
        json.dump(statistics, f, indent=2)

# Define the function to handle messages
async def message_handler(update: Update, context: CallbackContext):
    # Determine if the message is a new message or an edited message
    message = update.message or update.edited_message

    # If both message and edited_message are None, return early
    if message is None:
        return

    # Get the username of the user who sent or edited the message
    user = message.from_user.username

    # Get the text of the message
    message_text = message.text.lower()

    # Check if the trigger word is in the message
    if any(word in message_text for word in TRIGGER_WORDS):
        if user not in ADMIN_USERS:
            await handle_response(update, context, user)

# Define the function to handle /warn command
async def warn_command(update: Update, context: CallbackContext):
    # Determine if the message is a new message or an edited message
    message = update.message or update.edited_message

    # If both are None, return early
    if message is None or message.from_user.username is None:
        return

    user = message.from_user.username

    if len(context.args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /warn @username")
        return
    
    if user not in ADMIN_USERS:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You are not authorized to use this command.")
        return
    
    target_username = context.args[0].lstrip('@')
    await handle_response(update, context, target_username)

# Common response handler
async def handle_response(update: Update, context: CallbackContext, target_username):
    # Determine if the message is a new message or an edited message
    message = update.message or update.edited_message

    # If both are None, return early
    if message is None:
        return

    # Get the group chat ID
    group_id = str(message.chat.id)

    print(f"Group {group_id} - Target: {target_username}")

    # Load the statistics
    statistics = load_statistics()

    # Ensure the group exists in the statistics
    if group_id not in statistics:
        statistics[group_id] = {}

    # Increment the counter for the user or initialize it to 1
    user_counter = statistics[group_id].get(target_username, 0) + 1
    statistics[group_id][target_username] = user_counter

    # Save the updated statistics
    save_statistics(statistics)

    # Determine the response based on the counter
    if user_counter == int(SPECIAL_RESPONSE_NUMBER_1):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=SPECIAL_RESPONSE_MESSAGE_1.format(target_username, user_counter))
        await context.bot.send_animation(chat_id=update.effective_chat.id, animation=SPECIAL_RESPONSE_GIF_URL_1)
    elif user_counter == int(SPECIAL_RESPONSE_NUMBER_2):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=SPECIAL_RESPONSE_MESSAGE_2.format(target_username, user_counter))
        await context.bot.send_animation(chat_id=update.effective_chat.id, animation=SPECIAL_RESPONSE_GIF_URL_2)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=RESPONSE_MESSAGE.format(target_username, user_counter))
        await context.bot.send_animation(chat_id=update.effective_chat.id, animation=RESPONSE_GIF_URL)

def main():
    # Set up the bot
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add the message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Add the /warn command handler
    application.add_handler(CommandHandler('warn', warn_command))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
