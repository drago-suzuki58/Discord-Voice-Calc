from dotenv import load_dotenv
import os

load_dotenv()

# DISCORD
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN') or "YOUR_DISCORD_BOT_TOKEN"

# DB
DATABASE_URL = os.getenv('DATABASE_URL') or "sqlite+aiosqlite:///data/voice_time.db"
