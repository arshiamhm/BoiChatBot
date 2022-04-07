from telebot.types import (ReplyKeyboardMarkup, KeyboardButton, Update,
                        ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton)
from telebot import TeleBot
from database import Message, engine, Account
from sqlalchemy.orm import Session
from queries import *
from redis import Redis
from flask import Flask, request
import os

WEBHOOK_HOST = 'rocky-springs-24453.herokuapp.com'


bot = TeleBot(os.environ["BOT_API_TOKEN"])
app = Flask(__name__)
red = Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"),password=os.getenv("REDIS_PASSWORD"))


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
            red.hset(f"{call.message.chat.id}", mapping={'pending_message':1, 'answering': 1})
            print(call.message.text)
            bot.reply_to(call.message," ☝️ در حال پاسخ دادن به فرستنده این پیام هستی ... ؛ منتظریم بفرستی :)")

    elif call.data == "cb_no":
        bot.answer_callback_query(call.id, "Answer is No")


def back_to_default(message):
    print(message.chat.id)
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
        red.hset(f"{message.chat.id}", mapping={'sender_chat_id':mess.sender_chat_id})
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
    print("not working")
    data = red.hgetall(f"{message.chat.id}")
    print(data)
    user = query_uuid(Account, data["sending_to_uuid"])
    print(user)

    if data['pending_message'] == '1':
        print('conditions not working')
        if data['answering'] == '1':
            answer_message(data["sender_chat_id"], message)
            bot.send_message(data["sender_chat_id"], "شما یک پیام ناشناس دارید!!")
        else:
            print("this not workinggggggg")
            save_message(data["sending_to_uuid"], message)
            bot.send_message(user.chat_id, "شما یک پیام ناشناس دارید!!")

        back_to_default(message)
   
    if message.text == "انصراف":
        back_to_default(message)



@app.route('/' + os.environ['BOT_API_TOKEN'], methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://boichatbot.herokuapp.com/' + os.environ['BOT_API_TOKEN'])
    return "!", 200



if __name__ == "__main__":
# Start flask server
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))





