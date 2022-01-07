# DELETE ?
#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
import os
from uuid import uuid4

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update, InlineQueryResultLocation
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext
from telegram.utils.helpers import escape_markdown

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


locations = {}
central_location = {}


def request_start(update: Update):
    update.message.reply_text('Please start the bot by sending /start')


def request_done(update: Update):
    update.message.reply_text('Please indicate that all addresses have been entered by sending /done')


def random():
    # randomly generate a unique 5 char string for chat id
    return "mLzSd"


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    chat_id = random()
    locations[chat_id] = {}
    print(chat_id)
    update.message.reply_text('Hi!')


def done(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if chat_id not in locations:
        print('Location dictionary not yet initialised')
        request_start(update)
    print(chat_id)


def list_locations(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if chat_id not in central_location:
        if chat_id in locations:
            request_done(update)
        else:
            request_start(update)


# def help_command(update: Update, context: CallbackContext) -> None:
#     """Send a message when the command /help is issued."""
#     update.message.reply_text('Help!')


def inlinequery(update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    chat_id = update.message.chat_id
    user_id = update.inline_query.from_user.id
    print(chat_id)
    location = update.inline_query.location
    print(location.longitude)
    print(location.latitude)

    results = [
        InlineQueryResultLocation(
            id=chat_id,
            latitude=location.latitude,
            longitude=location.longitude,
            title="Send my location"
        ),
    ]

    if chat_id in locations:
        locations[chat_id].update({user_id: [location.latitude, location.longitude]})
    else:
        single_location = {chat_id: {user_id: [location.latitude, location.longitude]}}
        locations.update(single_location)

    print("stored dict")
    print(locations.get(chat_id))
    print("stored lat and long")
    print(locations[chat_id][user_id][0])
    print(locations[chat_id][user_id][1])

    update.inline_query.answer(results)


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv("TOKEN"))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("done", done))
    dispatcher.add_handler(CommandHandler("list", list_locations))
    # dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(InlineQueryHandler(inlinequery))

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()