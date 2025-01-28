# python
from datetime import datetime
from sqlalchemy import func
from d_voice.db.models import VoiceHistory, ActiveSession
from d_voice.db.sessions import get_db

def get_or_create_active_session(
    user_id: str,
    guild_id: str,
    channel_id: str,
    self_mute: bool,
    server_mute: bool,
    self_deaf: bool,
    server_deaf: bool
    ):
    with get_db() as db_session:
        active = db_session.query(ActiveSession).filter_by(
            user_id=user_id, guild_id=guild_id
        ).first()
        if not active:
            active = ActiveSession(
                user_id=user_id,
                guild_id=guild_id,
                channel_id=channel_id,
                start_time=datetime.now(),
                is_self_muted=self_mute,
                is_server_muted=server_mute,
                is_self_deafened=self_deaf,
                is_server_deafened=server_deaf
            )
            db_session.add(active)
        db_session.commit()
        return active

def end_active_session(user_id: str, guild_id: str):
    now = datetime.now()
    with get_db() as db_session:
        active = db_session.query(ActiveSession).filter_by(
            user_id=user_id, guild_id=guild_id
        ).first()
        if active:
            new_history = VoiceHistory(
                user_id=active.user_id,
                guild_id=active.guild_id,
                channel_id=active.channel_id,
                start_time=active.start_time,
                end_time=now,
                duration=int((now - active.start_time).total_seconds()),
                was_self_muted=active.is_self_muted,
                was_server_muted=active.is_server_muted,
                was_self_deafened=active.is_self_deafened,
                was_server_deafened=active.is_server_deafened
            )
            db_session.add(new_history)
            db_session.delete(active)
        db_session.commit()

def get_aggregate_time(user_id: str, since=None) -> int:
    with get_db() as db_session:
        query = db_session.query(func.sum(VoiceHistory.duration)).filter(
            VoiceHistory.user_id == user_id
        )
        if since:
            query = query.filter(VoiceHistory.start_time >= since)
        total_history = query.scalar() or 0

        active = db_session.query(ActiveSession).filter_by(
            user_id=user_id
        ).first()

        total_active = 0
        if active:
            now = datetime.now()
            session_start = active.start_time
            if since and session_start < since:
                session_start = since
            if session_start < now:
                total_active = int((now - session_start).total_seconds())

        return total_history + total_active

def get_voice_ranking(guild_id: str, since, limit: int = 10):
    with get_db() as db_session:
        q = db_session.query(
            VoiceHistory.user_id,
            func.sum(VoiceHistory.duration).label("total_time")
        ).filter(VoiceHistory.guild_id == guild_id)
        if since:
            q = q.filter(VoiceHistory.start_time >= since)
        q = q.group_by(VoiceHistory.user_id)

        results = []
        for row in q.all():
            total = row.total_time or 0
            active_session = db_session.query(ActiveSession).filter_by(
                user_id=row.user_id, guild_id=guild_id
            ).first()
            active_time = 0
            if active_session:
                now = datetime.now()
                start_time = active_session.start_time
                if since and start_time < since:
                    start_time = since
                if start_time < now:
                    active_time = int((now - start_time).total_seconds())
            results.append((row.user_id, total + active_time))

        active_only = db_session.query(ActiveSession).filter_by(guild_id=guild_id).all()
        existing_users = {r[0] for r in results}
        for a in active_only:
            if a.user_id not in existing_users:
                now = datetime.now()
                start_time = a.start_time
                if since and start_time < since:
                    start_time = since
                active_time = int((now - start_time).total_seconds()) if start_time < now else 0
                results.append((a.user_id, active_time))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
