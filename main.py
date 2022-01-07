import logging
import os
import telebot

from telegram.ext import Updater
from telebot import types
from telebot.types import BotCommand

# can import from database
locations = {}
central_location = {}

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    BotCommand('start', 'Starts the bot'),
    BotCommand('done', 'Indicate that all participants have sent their address'),
    BotCommand('list', 'Lists food places near central location')
])


# start command; once run, bot will listen for addresses from group
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    # initialise key value pair for curr chat_id
    locations[chat_id] = {}
    print(chat_id)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Send Location", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Test", reply_markup=keyboard)


def request_start(chat_id):
    bot.send_message(chat_id=chat_id, text='Please start the bot by sending /start')
    return


def request_done(chat_id):
    bot.send_message(chat_id=chat_id, text='Please indicate that all addresses have been entered by sending /done')
    return


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


@bot.message_handler(commands=['list'])
def list_locations(message):
    curr_chat_id = message.chat.id

    if curr_chat_id not in central_location:
        if curr_chat_id in locations:  # if user enters /list after start but before /done
            request_done(curr_chat_id)
        else:  # if user enters /list before /start
            request_start(curr_chat_id)


@bot.message_handler(content_types=['location'])
def location(message):
    if message.location is not None:
        print(message.location)
        print(message)


bot.infinity_polling()
