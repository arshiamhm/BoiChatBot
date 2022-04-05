from email.policy import default
from sqlite3 import Date
from sqlalchemy import (Column, Integer, 
                        create_engine, Boolean, String, ForeignKey, DateTime)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid
import os

engine = create_engine('postgresql://euowcrcwvglzrl:74637ec61e6742e4d6229c5f6338226b14518c3f34e80da15811576b18d8f752@ec2-18-214-134-226.compute-1.amazonaws.com:5432/db3p5ooc109u67', echo=True, future=True)
# engine.connect()
# Session = sessionmaker(bind=engine)
# session = Session()
Base = declarative_base()

class Account(Base):

    __tablename__ = "account"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    name = Column(String)
    uuid = Column(String,  default=lambda: str(uuid.uuid4())[:12], unique=True)
    chat_id = Column(Integer)
    messages = relationship("Message", backref="account")        

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r},\ username={self.username!r})"

class Message(Base):

    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    content_id = Column(Integer)
    sender_username = Column(String)
    user_id = Column(Integer, ForeignKey('account.id'))
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    sender_chat_id = Column(Integer)


# Base.metadata.clear()
Base.metadata.create_all(engine)
# squidward = User(name="arshia", username="arshiamohammadii", chat_id="467845070")
# krabs = User(name="ehkrabs", username="Eugene H. Krabs")
# session.add(squidward)
# session.add(krabs)
# session.commit()
# query = session.query(User).filter(User.uuid=='948f0e77-20e').one()
# query2 = session.get(User, 1)
# if query is not None:
#     print(query.uuid)
