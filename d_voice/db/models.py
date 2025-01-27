from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class VoiceHistory(Base):
    __tablename__ = 'voice_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(20))
    guild_id = Column(String(20))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer)

class ActiveSession(Base):
    __tablename__ = 'active_sessions'
    user_id = Column(String(20), primary_key=True)
    guild_id = Column(String(20), primary_key=True)
    start_time = Column(DateTime)
    channel_id = Column(String(20))
