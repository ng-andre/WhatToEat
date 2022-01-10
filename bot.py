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
import mapAPI

from telebot.types import BotCommand
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, ForceReply, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, Filters, \
    PollAnswerHandler

PORT = int(os.environ.get('PORT', 8443))
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
    BotCommand('start', 'Starts a new session'),
    BotCommand('find', 'Find central location and nearby restaurants'),
    BotCommand('filter', 'Filters based on participants\' choices')
])


def request_start(chat_id):
    bot.send_message(chat_id=chat_id, text='Type /start to start a new session')
    return


def request_done(chat_id):
    bot.send_message(chat_id=chat_id, text='When everyone uploaded their location, type /find to find central location')
    return


def start_message_private(update):
    update.message.reply_text('Get Started \n '
                              '1. add @SGEatWhereBot into your group chat.\n '
                              '2. call the /start command in the group chat and follow the instructions.\n')


def start_message_group(update):
    update.message.reply_text('Get Started \n '
                              '1. Everyone uploads their location by clicking on the attach '
                              'symbol (\U0001F4CE) and selecting the Location option. \n'
                              '2. /find to find the central location'
                              '3. /filter to find nearby F&B outlets')


def find_central_lat_long(chat_id):
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
    return central_lat, central_long


# Define a few command handlers. These usually take the two arguments update and
# context.
@bot.message_handler(commands=['start'])
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    chat_type = update.message.chat.type
    if chat_type == "private":
        start_message_private(update)
        return

    start_message_group(update)
    chat_id = update.message.chat_id
    if chat_id in locations:
        locations[chat_id].clear()


@bot.message_handler(commands=['find'])
def find(update: Update, context: CallbackContext):
    chat_type = update.message.chat.type
    if chat_type == "private":
        update.message.reply_text('This bot should only be used in a group chat!')
        return

    chat_id = update.message.chat_id
    if chat_id not in locations:  # Case 1: bot is newly added to group chat
        update.message.reply_text("Please upload at least one location")
    elif not locations[chat_id]:  # Case 2: Data for specific group chat is empty
        update.message.reply_text("Please upload at least one location")
    else:  # Everything is working fine
        message = update.message
        chat_id = message.chat_id
        central_lat, central_long = find_central_lat_long(chat_id)
        central_location[chat_id] = [central_lat, central_long]
        update.message.reply_text("The central location is:", quote=False)
        update.message.reply_location(central_lat, central_long, quote=False)
        update.message.reply_text("Run /filter to start filtering and choosing restaurants near your central location"
                                  , quote=False)


@bot.message_handler(commands=['filter'])  # done
def filter_places(update: Update, context: CallbackContext):
    message = update.message
    chat_type = message.chat.type
    if chat_type == "private":
        update.message.reply_text('This bot should only be used in a group chat!')
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
            InlineKeyboardButton("Cafes", callback_data='cafes'),
        ]
    ]

    update.message.reply_text(
        text=chat_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def format_filtered_places(places):
    text = 'These are the food places matching your filtered results near the common central location.\n'
    index = 1
    for name, description in places.items():
        if index >= 6:
            break
        text += f'{index}. {name}, {description}\n'
        index += 1

    return text


# callbackquery handler for restaurants
def restaurants(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = update.callback_query.message.chat.id
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
    centre = central_location[update.callback_query.message.chat.id]
    query = update.callback_query
    query.answer()
    bars_map = mapAPI.getFoodPlaces("", "bar", centre[0], centre[1])
    query.edit_message_text(text=f'{format_filtered_places(bars_map)}')
    return


# callbackquery handler for cafes
def cafes(update: Update, context: CallbackContext):
    centre = central_location[update.callback_query.message.chat.id]
    query = update.callback_query
    query.answer()
    cafes_map = mapAPI.getFoodPlaces("", "cafe", centre[0], centre[1])
    query.edit_message_text(text=f'{format_filtered_places(cafes_map)}')
    return


# callbackquery handler for bars
def halal(update: Update, context: CallbackContext):
    centre = central_location[update.callback_query.message.chat.id]
    query = update.callback_query
    query.answer()
    halal_places = mapAPI.getFoodPlaces("Halal", "restaurant", centre[0], centre[1])
    query.edit_message_text(text=f'{format_filtered_places(halal_places)}')
    return


# callbackquery handler for cafes
def vegetarian(update: Update, context: CallbackContext):
    centre = central_location[update.callback_query.message.chat.id]
    query = update.callback_query
    query.answer()
    veg_places = mapAPI.getFoodPlaces("Vegetarian", "restaurant", centre[0], centre[1])
    query.edit_message_text(text=f'{format_filtered_places(veg_places)}')
    return


# callbackquery handler for cafes
def nil(update: Update, context: CallbackContext):
    centre = central_location[update.callback_query.message.chat.id]
    query = update.callback_query
    query.answer()
    places = mapAPI.getFoodPlaces("", "restaurant", centre[0], centre[1])
    query.edit_message_text(text=f'{format_filtered_places(places)}')
    return


def location(update: Update, context: CallbackContext):
    message = update.message
    chat_type = message.chat.type
    if chat_type == "private":
        update.message.reply_text('This bot should only be used in a group chat!')
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
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("find", find))
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
    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN,
                          webhook_url='https://sgeatwherebot.herokuapp.com/' + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
