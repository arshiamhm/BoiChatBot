from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                        ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton)
from telebot import TeleBot
from database import Message, engine, Account
from sqlalchemy.orm import Session
from queries import *
from redis import Redis
import json


API_TOKEN = '5128541246:AAFGgLD-2wqSdICYg0Gn11E011aWldJapWg'
bot = TeleBot(API_TOKEN)
red = Redis("localhost", 6379, db=0, decode_responses=True)

user = None
# with Session(engine) as sess:
#     sess.query(Message).filter(Message.user_id==1).delete()
#     sess.commit()

def cancel_markup(text="انصراف"):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton(text))
    return markup

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(InlineKeyboardButton("پاسخ", callback_data="answer"),
                               InlineKeyboardButton("بلاک", callback_data="block"))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "answer":
            print(call.message)
            red.hset(f"{call.message.chat.id}", mapping={'pending_message':1, 'answering': 1, 'sending_to_messageid': call.message.id})
            # print(call.message.text)
            # red.hset(call.message.chat.id, "sending_to_messageid", call.message.id)
            bot.reply_to(call.message," ☝️ در حال پاسخ دادن به فرستنده این پیام هستی ... ؛ منتظریم بفرستی :)")

    elif call.data == "cb_no":
        bot.answer_callback_query(call.id, "Answer is No")

def back_to_default(message):
    markup = ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, "حاه! \n چه کاری برات انجام\
                        بدم؟", reply_markup=markup)
    red.hset(f"{message.chat.id}", mapping={'pending_message': 0, 'answering': 0})

    
@bot.message_handler(commands=["start", "help"])
def start(message):
    parameter = extract_parameter(message)
    save_user(message) 
    data = {
        "sending_to_uuid": parameter,
        "pending_message": 0,
        "answering": 0
    } 
    red.hset(f"{message.chat.id}", mapping=data)

    if parameter:
        user = query_uuid(Account, parameter)
        if user is None:
            bot.send_message(message.chat.id, "user you are trying to reach\
            is not reachable")
        else:
            #to-do: send message to the user (copy message)
            red.hset(f"{message.chat.id}", "pending_message", 1)
            bot.send_message(message.chat.id, "☝️ در حال پاسخ دادن به فرستنده این\
                            پیام هستی ... ؛ منتظریم بفرستی :)",\
                            reply_markup=cancel_markup())
        
              

@bot.message_handler(commands=['newmesg'])
def new_mesg(message):
    #query unread messages ordered by date added
    #loop through and send them all to the bot
    #update the read column to True
    all_messages = query_message(message)

    for mess in all_messages.order_by(Message.created_at):
        bot.send_message(message.chat.id, f"@{mess.sender_username} says:")
        bot.copy_message(message.chat.id, mess.sender_chat_id, mess.content_id, reply_markup=gen_markup())

    if all_messages.all():
        with Session(engine) as sess:
            # deleted_rows = all_messages.delete(synchronize_session=False)
            current_user = sess.query(Account).filter(Account.chat_id==message.chat.id).first()
            sess.query(Message).filter(Message.user_id == current_user.id).update({'read': True})
            sess.commit()
    else:
        bot.send_message(message.chat.id, "There are no new messages for you")



@bot.message_handler(content_types=['animation', 'audio', 'contact', 'dice', 'document', 'location', 'photo', 'poll', 'sticker', 'text', 'venue', 'video', 'video_note', 'voice'])
def send_anonymous_message(message):
    data = red.hgetall(f"{message.chat.id}")
    print('annon handler')
    print(data)
    if data['pending_message'] == '1':
        print('message pending')
        if data['answering'] == '1':
            answer_message(data["sending_to_messageid"], message)
        else:
            print('sendinig')
            save_message(data["sending_to_uuid"], message)

        back_to_default(message)
        bot.send_message(message.chat.id, "شما یک پیام ناشناس دارید!!")
   
    if message.text == "انصراف":
        back_to_default(message)




bot.infinity_polling()







