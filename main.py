import logging
import os
import telebot

from telegram.ext import Updater
from telebot import types
from telebot.types import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

# can import from database
locations = {}
central_location = {}

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    BotCommand('start', 'Starts the bot'),
    BotCommand('done', 'Indicate that all participants have sent their address'),
    BotCommand('list', 'Lists food places near central location'),
    BotCommand('location', 'User sends current location'),
    BotCommand('filter', 'Filters based on participants')
])


def request_start(chat_id):
    bot.send_message(chat_id=chat_id, text='Please start the bot by sending /start')


def request_done(chat_id):
    bot.send_message(chat_id=chat_id, text='Please indicate that all addresses have been entered by sending /done')


def extract_arg(arg):
    return arg.split()[1:]


# start command; once run, bot will listen for addresses from group
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    # initialise key value pair for curr chat_id
    locations[chat_id] = {}
    print(chat_id)
    # keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    # button_geo = types.KeyboardButton(text="Send Location", request_location=True)
    # keyboard.add(button_geo)
    # bot.send_message(message.chat.id, "Test", reply_markup=keyboard)


@bot.message_handler(commands=['location'])
def send_location(message):
    curr_chat_id = message.chat.id

    # if user tries to send location without
    if curr_chat_id not in locations:
        request_start(curr_chat_id)
        return

    user_id = message.from_user.id
    user_location = extract_arg(message.text)

    locations[curr_chat_id].update({user_id: user_location})

    print(locations.get(curr_chat_id))

    bot.send_message(chat_id=curr_chat_id, text=f'Number of addresses: {len(locations[curr_chat_id])}')


# done command; once run, bot will calculate and return central location of all addresses entered
@bot.message_handler(commands=['done'])
def done(message):
    curr_chat_id = message.chat.id
    # if user enters /done before /start
    if curr_chat_id not in locations:
        # if not key value pair for curr_chat_id => request start
        print('Not Working')
        request_start(curr_chat_id)
        return
    print(curr_chat_id)

    # Run Le Zong algorithm to get central location with curr_chat_id as key


@bot.message_handler(commands=['list'])
def list_locations(message):
    curr_chat_id = message.chat.id
    if curr_chat_id not in central_location:
        if curr_chat_id in locations:  # if user enters /list after start but before /done
            request_done(curr_chat_id)
        else:  # if user enters /list before /start
            request_start(curr_chat_id)

    # once central location calculated


@bot.message_handler(commands=['filter'])
def filter_places(message):
    chat_id = message.chat.id

    if chat_id not in locations:
        request_start(chat_id)
        return

    # if chat_id not in central_location:
    #     request_done(chat_id)
    #     return

    chat_text = "Select where your group would like to dine."

    places = ['restaurants', 'bars', 'cafes']
    buttons = []

    for place in places:
        row = []
        button = InlineKeyboardButton(
            place,
            callback_data='place ' + place
        )
        row.append(button)
        buttons.append(row)

    bot.send_message(
        chat_id=chat_id,
        text=chat_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    data = call.data
    intent, extra_data = data.split()[0], data.split()[1:]

    if intent == 'place':
        view_place_selected(chat_id, extra_data)
        return
    if intent == 'restriction':
        view_restaurants_suitable(chat_id, extra_data)
        return

    print(f'{chat_id}: Callback not implemented')


def view_place_selected(chat_id, data):
    if data == ['cafes'] or data == ['bars']:
        display_places_results(chat_id, data)
        return
    else:
        # display restaurants: another format
        display_restaurants(chat_id, data)
        return


def display_places_results(chat_id, data):  # replace with lz actual function call
    bot.send_message(chat_id=chat_id, text=data)
    return


def display_restaurants(chat_id, data):
    buttons = []
    dietary_restrictions_chat_text = 'Please indicate any special dietary preferences i.e. Halal / Vegetarian. ' \
                                     'Select NIL'

    restrictions = ['Halal', 'Vegetarian', 'NIL']
    buttons = []

    for restriction in restrictions:
        row = []
        button = InlineKeyboardButton(
            restriction,
            callback_data='restriction ' + restriction
        )
        row.append(button)
        buttons.append(row)

    bot.send_message(
        chat_id=chat_id,
        text=dietary_restrictions_chat_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def view_restaurants_suitable(chat_id, data):
    if data == ['Halal'] or data == ['Vegetarian']:
        display_restrictions_results(chat_id, data)
        return
    else:
        print('cuisines')
        display_cuisines(chat_id, data)
        return


def display_restrictions_results(chat_id, data):  # replace with lz actual function call
    bot.send_message(chat_id=chat_id, text=data)
    return


def display_cuisines(chat_id, data):  # replace with lz actual function call
    bot.send_message(chat_id=chat_id, text=data)
    return


@bot.message_handler(content_types=['location'])
def location(message):
    if message.location is not None:
        print(message.location)
        print(message)


bot.infinity_polling()
