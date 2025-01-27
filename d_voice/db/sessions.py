from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import d_voice.env as env

engine = create_engine(env.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
