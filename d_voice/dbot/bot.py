from loguru import logger
import discord

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

initialize_fetch_jsons = False

def bot_setup(bot: discord.Client, tree: discord.app_commands.CommandTree):
    @bot.event
    async def on_ready():
        logger.info(f"Logged in as {bot.user}")

        logger.info("Started tasks Successfully")

        await tree.sync()
        logger.info("Synced commands Successfully")

        await load_voice_channels()

    @bot.event
    async def on_voice_state_update(member, before, after):
        if before.channel is None and after.channel is not None:
            logger.info(f"{member} joined {after.channel}")
            log_voice_state(member, after)
        elif before.channel is not None and after.channel is None:
            logger.info(f"{member} left {before.channel}")
        elif before.channel != after.channel:
            logger.info(f"{member} moved from {before.channel} to {after.channel}")
            log_voice_state(member, after)

        if before.self_mute != after.self_mute:
            if after.self_mute:
                logger.info(f"{member} has been self-muted")
            else:
                logger.info(f"{member} has been un-self-muted")

        if before.mute != after.mute:
            if after.mute:
                logger.info(f"{member} has been server-muted")
            else:
                logger.info(f"{member} has been un-server-muted")

        if before.self_deaf != after.self_deaf:
            if after.self_deaf:
                logger.info(f"{member} has been self-speaker-muted")
            else:
                logger.info(f"{member} has been un-self-speaker-muted")

        if before.deaf != after.deaf:
            if after.deaf:
                logger.info(f"{member} has been server-speaker-muted")
            else:
                logger.info(f"{member} has been un-server-speaker-muted")

    async def load_voice_channels():
        for guild in bot.guilds:
            for channel in guild.voice_channels:
                members = channel.members
                if members:
                    logger.info(f"Voice channel '{channel.name}' has members: {[member.name for member in members]}")
                    for member in members:
                        log_voice_state(member, member.voice)
                else:
                    logger.info(f"Voice channel '{channel.name}' is empty")

    def log_voice_state(member, voice_state):
        if voice_state.self_mute:
            logger.info(f"{member} is currently self-muted")
        if voice_state.mute:
            logger.info(f"{member} is currently server-muted")
        if voice_state.self_deaf:
            logger.info(f"{member} is currently self-deafened")
        if voice_state.deaf:
            logger.info(f"{member} is currently server-deafened")
