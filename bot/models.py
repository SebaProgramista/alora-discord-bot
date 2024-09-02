import sqlalchemy as db
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, DateTime

import json

config = json.load(open(".config.json"))

Base = declarative_base()

# url_object = URL.create(
#     "mysql",
#     host=config["database"]["host"],
#     username=config["database"]["user"],
#     password=config["database"]["passwd"],
#     database=config["database"]["database"]
# )

url_object = "sqlite:///database.db"

engine = create_engine(url_object)

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    last_date = Column(DateTime)
    send = Column(Boolean)
    xp = Column(Integer)
    voice_join_time = Column(DateTime)
    voice_time = Column(Integer)
    messages_count = Column(Integer)

    def __repr__(self) -> str:
        return f"<Member id: {self.id}, last_date: {self.last_date}, send: {self.send}, xp: {self.xp}, voice_join_time: {self.voice_join_time}>, voice_time: {self.voice_time}, messages_count: {self.messages_count}"

class Level(Base):
    __tablename__ = "levels"

    role_id = Column(Integer, primary_key=True)
    required_points = Column(Integer)

    def __repr__(self) -> str:
        return f"<Level role_id: {self.role_id}, required_points: {self.required_points}>"
    
Base.metadata.create_all(engine)