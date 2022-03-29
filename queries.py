from sqlalchemy.orm import Session
from database import Account, Message, engine


def extract_parameter(text):
    value = text
    try:
        value = text.text.split()[1]
    except IndexError:
        value = None

    return value

    
def query_user(user, uuid):
    with Session(engine) as sess:
        user = sess.query(user).filter(user.uuid == uuid).first()
        return user

def save_user(message):
    with Session(engine) as sess:
        user = Account(name=message.chat.first_name, username=message.chat.username,\
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
        user = sess.query(Account).filter(Account.chat_id == message.chat.id).first()
        message_user = sess.query(Message).filter(Message.user_id == user.id, Message.read == False)
        return message_user
