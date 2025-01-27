from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class VoiceHistory(Base):
    __tablename__ = 'voice_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(20))
    guild_id = Column(String(20))
    channel_id = Column(String(20))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer)
    was_self_muted = Column(Boolean, default=False)
    was_server_muted = Column(Boolean, default=False)
    was_self_deafened = Column(Boolean, default=False)
    was_server_deafened = Column(Boolean, default=False)

class ActiveSession(Base):
    __tablename__ = 'active_sessions'
    user_id = Column(String(20), primary_key=True)
    guild_id = Column(String(20), primary_key=True)
    channel_id = Column(String(20))
    start_time = Column(DateTime)
    is_self_muted = Column(Boolean, default=False)
    is_server_muted = Column(Boolean, default=False)
    is_self_deafened = Column(Boolean, default=False)
    is_server_deafened = Column(Boolean, default=False)
