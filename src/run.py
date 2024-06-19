import os, json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters

# Load environment variables from .env file
load_dotenv()

# Set up your bot token and other variables from the environment
BOT_TOKEN = os.getenv('BOT_TOKEN')
TRIGGER_WORDS = os.getenv('TRIGGER_WORDS').split(',')
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
    # Get the text of the message
    message_text = update.message.text.lower()

    # Check if the trigger word is in the message
    if any(word in message_text for word in TRIGGER_WORDS):
        # Get the username of the sender
        username = update.message.from_user.username

        # Get the group chat ID
        group_id = str(update.message.chat.id)

        print(f"Group {group_id} - {username}: {message_text}")

        # Load the statistics
        statistics = load_statistics()

        # Ensure the group exists in the statistics
        if group_id not in statistics:
            statistics[group_id] = {}

        # Increment the counter for the user or initialize it to 1
        user_counter = statistics[group_id].get(username, 0) + 1
        statistics[group_id][username] = user_counter

        # Save the updated statistics
        save_statistics(statistics)

        # Determine the response based on the counter
        if user_counter == SPECIAL_RESPONSE_NUMBER_1:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=SPECIAL_RESPONSE_MESSAGE_1.format(username, user_counter))
            await context.bot.send_animation(chat_id=update.effective_chat.id, animation=SPECIAL_RESPONSE_GIF_URL_1)
        elif user_counter == SPECIAL_RESPONSE_NUMBER_2:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=SPECIAL_RESPONSE_MESSAGE_2.format(username, user_counter))
            await context.bot.send_animation(chat_id=update.effective_chat.id, animation=SPECIAL_RESPONSE_GIF_URL_2)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=RESPONSE_MESSAGE.format(username, user_counter))
            await context.bot.send_animation(chat_id=update.effective_chat.id, animation=RESPONSE_GIF_URL)

def main():
    # Set up the bot
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add the message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()