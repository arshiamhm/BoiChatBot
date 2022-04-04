from telebot.types import (ReplyKeyboardMarkup, KeyboardButton, Update,
                        ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton)
from telebot import TeleBot
from database import Message, engine, Account
from sqlalchemy.orm import Session
from queries import *
from redis import Redis
import flask
import time
import os

WEBHOOK_HOST = 'rocky-springs-24453.herokuapp.com'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

bot = TeleBot(os.getenv( "BOT_API_TOKEN"))
app = flask.Flask(__name__)
red = Redis(os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0, password=os.getenv("REDIS_PASSWORD"))
WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (os.getenv( "BOT_API_TOKEN"))




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

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


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
    data = red.hgetall(f"{message.chat.id}")
    user = query_uuid(Account, data["sending_to_uuid"])
    
    if data['pending_message'] == '1':
        if data['answering'] == '1':
            answer_message(data["sender_chat_id"], message)
            bot.send_message(data["sender_chat_id"], "شما یک پیام ناشناس دارید!!")
        else:
            save_message(data["sending_to_uuid"], message)
            bot.send_message(user.chat_id, "شما یک پیام ناشناس دارید!!")

        back_to_default(message)
   
    if message.text == "انصراف":
        back_to_default(message)




bot.remove_webhook()

time.sleep(0.1)

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

if __name__ == "__main__":
# Start flask server
    app.run(host=WEBHOOK_HOST,
            port=WEBHOOK_PORT,
            ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
            debug=True)





