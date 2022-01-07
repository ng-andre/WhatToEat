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
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, Filters

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
    BotCommand('find', 'Find central location and nearby restaurants'),
    BotCommand('filter', 'Filters based on participants choices')
])


def request_start(chat_id):
    bot.send_message(chat_id=chat_id, text='Please start the bot by sending /start')
    return


def request_done(chat_id):
    bot.send_message(chat_id=chat_id, text='Please indicate that all addresses have been entered by sending /done')
    return


# Define a few command handlers. These usually take the two arguments update and
# context.
@bot.message_handler(commands=['start'])
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    chat_type = update.message.chat.type
    if chat_type == "private":
        print("is private")
        update.message.reply_text('Get Started \n '
                                  '1. add @SGEatWhereBot into your group chat.\n '
                                  '2. call the /start command in the group chat and follow the instructions.\n')
        return

    update.message.reply_text('Please send your current location! Click on the attach '
                              'symbol and select the Location option to do so!')
    chat_id = update.message.chat_id
    if chat_id in locations:
        locations[chat_id].clear()


@bot.message_handler(commands=['help'])
def help(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Use the command /start to find a common place to eat')
    chat_type = update.message.chat.type
    if chat_type == "private":
        print("is private")
        update.message.reply_text('This bot can only be used in a group chat!')
        return


@bot.message_handler(commands=['find'])
def find(update: Update, context: CallbackContext):
    chat_type = update.message.chat.type
    if chat_type == "private":
        print("is private")
        update.message.reply_text('This bot can only be used in a group chat!')
        return

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
        central_location[chat_id] = {central_lat, central_long}
        update.message.reply_text("The central location is:", quote=False)
        update.message.reply_location(central_lat, central_long, quote=False)
        update.message.reply_text("Showing restaurants nearby", quote=False)


@bot.message_handler(commands=['filter'])  # done
def filter_places(update: Update, context: CallbackContext):
    message = update.message
    chat_type = message.chat.type
    print(chat_type)
    if chat_type == "private":
        print("is private")
        update.message.reply_text('This bot can only be used in a group chat!')
        return

    chat_id = update.message.chat_id

    if chat_id not in locations:
        request_start(chat_id)
        return

    if chat_id not in central_location:
        request_done(chat_id)
        return

    chat_text = "Select where your group would like to dine."

    buttons = [
        [
            InlineKeyboardButton("Restaurants", callback_data='restaurants'),
            InlineKeyboardButton("Bars", callback_data='bars'),
            InlineKeyboardButton("Cafes", callback_data='cafes')
        ]
    ]

    update.message.reply_text(
        text=chat_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# callbackquery handler for restaurants
def restaurants(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    # new InlineKeyboardMarkup to account for dietary restrictions
    chat_text = 'Please indicate any special dietary preferences i.e. Halal / Vegetarian.' \
                'Select NIL otherwise'

    buttons = [
        [
            InlineKeyboardButton("Halal", callback_data='halal'),
            InlineKeyboardButton("Vegetarian", callback_data='vegetarian'),
            InlineKeyboardButton("NIL", callback_data='nil')
        ]
    ]

    query.edit_message_text(
        text=chat_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return


# callbackquery handler for bars
def bars(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f'{query.data}')  # replace with data from lz => return all bars
    return


# callbackquery handler for cafes
def cafes(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f'{query.data}')  # replace with data from lz => return all cafes
    return


# callbackquery handler for bars
def halal(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f'{query.data}')  # replace with data from lz => return all halal places
    return


# callbackquery handler for cafes
def vegetarian(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f'{query.data}')  # replace with data from lz => return all vegetarian places
    return


# callbackquery handler for cafes
def nil(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f'{query.data}')  # replace with data from lz
    return


def location(update: Update, context: CallbackContext):
    message = update.message
    chat_type = message.chat.type
    print(chat_type)
    if chat_type == "private":
        print("is private")
        update.message.reply_text('This bot can only be used in a group chat!')
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
    dispatcher.add_handler(CommandHandler("filter", filter_places))

    # Callback Query Handlers for filtering between restaurants, bars and cafes
    dispatcher.add_handler(CallbackQueryHandler(restaurants, pattern='^' + 'restaurants' + '$'))
    dispatcher.add_handler(CallbackQueryHandler(bars, pattern='^' + 'bars' + '$'))
    dispatcher.add_handler(CallbackQueryHandler(cafes, pattern='^' + 'cafes' + '$'))

    # Callback Query Handlers for dietary restrictions
    dispatcher.add_handler(CallbackQueryHandler(halal, pattern='^' + 'halal' + '$'))
    dispatcher.add_handler(CallbackQueryHandler(vegetarian, pattern='^' + 'vegetarian' + '$'))
    dispatcher.add_handler(CallbackQueryHandler(nil, pattern='^' + 'nil' + '$'))

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
