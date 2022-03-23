from sqlalchemy import (Column, Integer, 
                        create_engine, MetaData, String)
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import uuid

engine = create_engine("sqlite:///sqlite3.db", echo=True, future=True)
# engine.connect()
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class User(Base):

    __tablename__ = "user_account"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    name = Column(String)
    uuid = Column(String,  default=lambda: str(uuid.uuid4())[:12], unique=True)
    chat_id = Column(Integer)
        

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r},\
    username={self.username!r})"

# Base.metadata.clear()
Base.metadata.create_all(engine)
# squidward = User(name="squidward", username="Squidward Tentacles")
# krabs = User(name="ehkrabs", username="Eugene H. Krabs")
# session.add(squidward)
# session.add(krabs)
# session.commit()
# print(session.query(User).filter(User.uuid=='f803c256-b5c').all())
