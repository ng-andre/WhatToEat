import logging
import os
import telebot
import mapAPI
from telegram.ext import Updater
from telebot import types
from telebot.types import BotCommand

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    BotCommand('start', 'Starts the bot'),
    BotCommand('test', 'Show location results')
])


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Send Location", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Test", reply_markup=keyboard)

@bot.message_handler(commands=['test'])
def test(message):
    bot.send_message(message.chat.id, "Testing results")





@bot.message_handler(content_types=['location'])
def location(message):
    if message.location is not None:
        print(message.location)
        print(message)

bot.infinity_polling()
