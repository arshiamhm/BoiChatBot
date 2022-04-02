from sqlalchemy.orm import Session
from database import Account, Message, engine


def extract_parameter(text):
    value = text
    try:
        value = text.text.split()[1]
    except IndexError:
        value = None

    return value

    
def query_uuid(user, uuid):
    with Session(engine) as sess:
        user = sess.query(user).filter(user.uuid == uuid).first()
        return user

def user_exists(sess, message) -> bool:
    user_exists = sess.query(Account.id).filter(Account.chat_id == message.chat.id).first() is not None
    return user_exists


def save_user(message):
    with Session(engine) as sess:
        if not user_exists(sess, message):
            user = Account(name=message.chat.first_name, username=message.chat.username,\
                        chat_id=message.chat.id)
            sess.add(user)
            sess.commit()
    # session.close()

def save_message(uuid, message):
    with Session(engine) as sess:
        to_user = sess.query(Account).filter(Account.uuid == uuid).first()
        message_sent = Message(content_id=message.id, sender_username=message.chat.username, user_id=to_user.id, sender_chat_id=message.chat.id)
        sess.add(message_sent)
        sess.commit()
    # session.close()

def answer_message(message_id, message):
    with Session(engine) as sess:
        # print(message.id)
        # print(message_id)
        mess = sess.query(Message).filter(Message.content_id == message_id).first()
        message_sent = Message(content_id=message.id, sender_username=message.chat.username, user_id=mess.user_id, sender_chat_id=message.chat.id)
        sess.add(message_sent)
        sess.commit()


def query_message(message):
    with Session(engine) as sess:
        user = sess.query(Account).filter(Account.chat_id == message.chat.id).first()
        message_user = sess.query(Message).filter(Message.user_id == user.id, Message.read == False)
        return message_user
