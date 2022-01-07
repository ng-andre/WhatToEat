import logging
import os
import telebot
from telegram import ParseMode

import mapAPI
from telegram.ext import Updater, updater, CommandHandler, PollHandler, CallbackContext, PollAnswerHandler
from telebot import types
from telebot.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update

from database import preferences

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    BotCommand('start', 'Starts the bot'),
    BotCommand('poll', 'Show all cuisines')
])


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Send Location", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Test", reply_markup=keyboard)


@bot.message_handler(commands=['poll'])
def poll(update: Update, context: CallbackContext) -> None:
    """Sends a predefined poll"""
    print("inside poll")
    cuisines = ["Chinese", "Indian", "Western", "Mexican", "Japanese", "Korean", "American", "Buffet", "BBQ",
                "Food Court"]
    message = bot.send_poll(
        update.chat.id,
        "What Cuisines?",
        cuisines,
        is_anonymous=False,
        allows_multiple_answers=True,
    )
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "cuisines": cuisines,
            "message_id": message.message_id,
            "chat_id": update.chat.id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)


def receive_poll_answer(update: Update, context: CallbackContext) -> None:
    """Summarize a users poll vote"""
    print("inside receive poll ans func")
    answer = update.poll_answer
    print(answer)
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]
    context.bot.send_message(
        context.bot_data[poll_id]["chat_id"],
        f"{update.effective_user.mention_html()} feels {answer_string}!",
        parse_mode=ParseMode.HTML,
    )
    context.bot_data[poll_id]["answers"] += 1
    # Close poll after three participants voted
    if context.bot_data[poll_id]["answers"] == 3:
        context.bot.stop_poll(
            context.bot_data[poll_id]["chat_id"], context.bot_data[poll_id]["message_id"]
        )


# @bot.message_handler(commands=['poll'])
# def poll(message):
#     bot.send_message(message.chat.id, "Testing Cuisines")
#     # cuisines = ["Chinese", "Indian", "Western", "Mexican", "Japanese", "Korean", "American", "Buffet", "BBQ",
#     #             "Food Court"]
#     # updater = Updater(TOKEN)
#     # dispatcher = updater.dispatcher
#     # dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
#
#     # bot.send_poll(
#     #     chat_id=message.chat.id,
#     #     question=f'What cuisine?',
#     #     options=cuisines,
#     #     allows_multiple_answers=True,
#     # )


@bot.message_handler(content_types=['location'])
def location(message):
    if message.location is not None:
        print(message.location)
        print(message)


updater = Updater(TOKEN)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('poll', poll))
print("added handler for poll")
dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))

bot.infinity_polling()
