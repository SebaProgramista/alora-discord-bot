from sqlalchemy.orm import sessionmaker

from models import Member, Level, engine

class SessionManager():
    Session = sessionmaker(bind=engine)
    session = Session()

    member = Member
    level = Level

    def create_new_level(role_id, required_points):
        return Level(role_id=role_id, required_points=required_points)
    
    def create_new_member(id, last_date, send=False, xp=0, voice_join_time=None, voice_time=0, messages_count=0):
        return Member(id=id, last_date=last_date, send=send, xp=xp, voice_join_time=voice_join_time, voice_time=voice_time, messages_count=messages_count)
        