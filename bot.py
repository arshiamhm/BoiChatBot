from click import command
from telebot import TeleBot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                        ReplyKeyboardRemove)
from database import Message, engine, User
from sqlalchemy.orm import Session


API_TOKEN = '5128541246:AAFGgLD-2wqSdICYg0Gn11E011aWldJapWg'
bot = TeleBot(API_TOKEN)

pending_message = False
user = None
# with Session(engine) as sess:
#     sess.query(Message).filter(Message.user_id==1).delete()
#     sess.commit()
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
    
def query_user(user, uuid):
    with Session(engine) as sess:
        user = sess.query(user).filter(user.uuid == uuid).first()
        return user

def save_user(message):
    with Session(engine) as sess:
        user = User(name=message.chat.first_name, username=message.chat.username,\
                    chat_id=message.chat.id)
        sess.add(user)
        sess.commit()
    # session.close()

def save_message(message, user_id):
    with Session(engine) as sess:
        message_sent = Message(content_id=message.id, sender_username=message.chat.username, user_id=user_id, sender_chat_id=message.chat.id)
        sess.add(message_sent)
        sess.commit()
    # session.close()

def query_message(message):
    with Session(engine) as sess:
        user = sess.query(User).filter(User.chat_id == message.chat.id).first()
        message_user = sess.query(Message).filter(Message.user_id == user.id, Message.read == False).order_by(Message.created_at).all()
        return message_user

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
    # save_user(message, session)
    user = query_user(User, parameter)
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
    print("newmesg print")
    #query unread messages ordered by date added
    #loop through and send them all to the bot
    #update the read column to True
    all_messages = query_message(message)
    print(all_messages)
    with Session(engine) as sess:
        for mess in all_messages:
            print(mess.id)
            bot.send_message(message.chat.id, f"{mess.sender_username} says:")
            bot.copy_message(message.chat.id, mess.sender_chat_id, mess.content_id)
            # mess.read = True
            # sess.commit()        
        

@bot.message_handler(content_types=['animation', 'audio', 'contact', 'dice', 'document', 'location', 'photo', 'poll', 'sticker', 'text', 'venue', 'video', 'video_note', 'voice'])
def send_anonymous_message(message):
    global user
    
    if pending_message:
        print("is this working?")
        save_message(message, user.id)
        # bot.copy_message(user.chat_id, message.chat.id, message.id)
        bot.send_message(user.chat_id, "شما یک پیام ناشناس دارید!!")
        back_to_default(message)
    if message.text == "انصراف":
        back_to_default(message)




bot.infinity_polling()







