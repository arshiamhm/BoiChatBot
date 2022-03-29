from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                        ReplyKeyboardRemove)
from telebot import TeleBot
from database import Message, engine, Account
from sqlalchemy.orm import Session
from queries import *


API_TOKEN = '5128541246:AAFGgLD-2wqSdICYg0Gn11E011aWldJapWg'
bot = TeleBot(API_TOKEN)

pending_message = False
user = None
# with Session(engine) as sess:
#     sess.query(Message).filter(Message.user_id==1).delete()
#     sess.commit()

def cancel_markup(text="انصراف"):
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton(text))
    return markup

def back_to_default(message):
    global pending_message
    markup = ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, "حاه! \n چه کاری برات انجام\
                        بدم؟", reply_markup=markup)
    pending_message = False
    
@bot.message_handler(commands=["start", "help"])
def start(message):
    global user, pending_message
    parameter = extract_parameter(message)
    save_user(message)
    user = query_user(Account, parameter)
    # bot.copy_message(user.chat_id, message.chat.id, 283)
    if user is None:
        bot.send_message(message.chat.id, "user you are trying to reach\
        is not reachable")
    else:
        #to-do: send message to the user (copy message)
        pending_message = True
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
        bot.copy_message(message.chat.id, mess.sender_chat_id, mess.content_id)

    if all_messages.all():
        with Session(engine) as sess:
            # deleted_rows = all_messages.delete(synchronize_session=False)
            sess.query(Message).delete()
            sess.commit()
    else:
        bot.send_message(message.chat.id, "There are no new messages for you")




@bot.message_handler(content_types=['animation', 'audio', 'contact', 'dice', 'document', 'location', 'photo', 'poll', 'sticker', 'text', 'venue', 'video', 'video_note', 'voice'])
def send_anonymous_message(message):
    global user
    
    if pending_message:
        save_message(message, user.id)
        # bot.copy_message(user.chat_id, message.chat.id, message.id)
        bot.send_message(user.chat_id, "شما یک پیام ناشناس دارید!!")
        back_to_default(message)
    if message.text == "انصراف":
        back_to_default(message)




bot.infinity_polling()







