from telebot import TeleBot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                        ReplyKeyboardRemove)
from database import engine, User
from sqlalchemy.orm import sessionmaker
import os

API_TOKEN = '5160093648:AAF02pSKyg_lpd97PeXp-KrxGKFfIUK0C2E'
bot = TeleBot(API_TOKEN)

Session = sessionmaker(bind=engine)
session = Session()
"""
start handler:
    
    -check for query parameter
    -extract the query parameter
    -check for the user in database
    -if user exists -> welcome message and ...
    -if user not exists -> create one and reply them with +
        the default welcome message
    -and show them the keyboard

"""
def extract_parameter(text):
    value = text
    try:
        value = text.text.split()[1]
    except IndexError:
        value = None

    return value

def cancel_markup(text="انصراف"):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton(text))
    return markup
    


def save_user(message, session):
    user = User(name=message.chat.first_name, username=message.chat.username,\
                chat_id=message.chat.id)
    session.add(user)
    session.commit()
    session.close()

@bot.message_handler(commands=["start", "help"])
def start(message):
    parameter = extract_parameter(message)
    user = session.query(User).filter(User.uuid == parameter).first()
    if user is None:
        bot.send_message(message.chat.id, "user you are trying to reach\
        is not reachable")
    else:
        #to-do: send message to the user (copy message)

        bot.send_message(message.chat.id, "☝️ در حال پاسخ دادن به فرستنده این\
                         پیام هستی ... ؛ منتظریم بفرستی :)",\
                         reply_markup=cancel_markup())
              
@bot.message_handler(content_types=["text"])
def cancel_handler(message):
    if message.text == "انصراف":
        markup = ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, "حاه! \n چه کاری برات انجام\
                         بدم؟", reply_markup=markup)

bot.infinity_polling()







