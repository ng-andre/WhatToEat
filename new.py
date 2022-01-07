#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
import telebot

from telebot.types import BotCommand
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

locations = {}
central_location = {}
flags = {}

bot.set_my_commands([
    BotCommand('start', 'Starts the bot'),
    BotCommand('help', 'Get information on how to get started'),
    BotCommand('find', 'Find central location and nearby restaurants')
])


# Define a few command handlers. These usually take the two arguments update and
# context.
@bot.message_handler(commands=['start'])
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    user = update.effective_user
    update.message.reply_text('Please send your current location!')
    chat_id = update.message.chat_id
    if chat_id in locations:
        locations[chat_id].clear()


@bot.message_handler(commands=['help'])
def help(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Use the command /start to find a common place to eat')


@bot.message_handler(commands=['find'])
def find(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    print("Dictionary print...")
    print(locations)
    if chat_id not in locations:  # Case 1: bot is newly added to groupchat
        update.message.reply_text("Please upload at least one location")
    elif not locations[chat_id]:  # Case 2: Data for specific groupchat is empty
        update.message.reply_text("Please upload at least one location")
    else:  # Everything is working fine
        message = update.message
        chat_id = message.chat_id
        print("start of loop")
        first_pos = next(iter(locations[chat_id].values()))
        min_lat, max_lat = first_pos[0], first_pos[0]
        min_long, max_long = first_pos[1], first_pos[1]
        for x in locations[chat_id]:
            curr_lat = locations[chat_id][x][0]
            curr_long = locations[chat_id][x][1]
            if curr_lat > max_lat:
                max_lat = curr_lat
            elif curr_lat < min_lat:
                min_lat = curr_lat
            if curr_long > max_long:
                max_long = curr_long
            elif curr_long < min_long:
                min_long = curr_long

        central_lat = (min_lat + max_lat) / 2
        central_long = (min_long + max_long) / 2
        print(central_lat)
        print(central_long)  # coordinates for API
        update.message.reply_text("The central location is:", quote=False)
        update.message.reply_location(central_lat, central_long, quote=False)
        update.message.reply_text("Showing restaurants nearby", quote=False)


def location(update: Update, context: CallbackContext):
    message = update.message
    chat_type = message.chat.type
    print(chat_type)
    if chat_type == "private":
        print("is private")
        update.message.reply_text('This bot can only be used in a group!')
        return

    location_data = message.location
    user = message.from_user.username
    chat_id = message.chat_id
    current_pos = (location_data.latitude, location_data.longitude)
    update.message.reply_text("Received {name}'s location!".format(name=message.from_user.first_name))

    #  initialise container for groupchat in locations
    if chat_id in locations:
        locations[chat_id].update({user: current_pos})
    else:
        init_location = {chat_id: {user: current_pos}}
        locations.update(init_location)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv("TOKEN"))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("find", find))
    dispatcher.add_handler(CommandHandler("help", help))

    location_handler = MessageHandler(Filters.location, location)
    dispatcher.add_handler(location_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
