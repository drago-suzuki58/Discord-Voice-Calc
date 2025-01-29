from loguru import logger
import discord

from d_voice.util import get_or_create_active_session, end_active_session, get_db, is_rest_channel, ActiveSession

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

        await tree.sync()
        logger.info("Synced commands Successfully")

        await load_voice_channels()
        reconcile_sessions()

    @bot.event
    async def on_voice_state_update(member, before, after):
        if before.channel is None and after.channel is not None:
            logger.info(f"{member} has joined {after.channel}")
            get_or_create_active_session(
                user_id=str(member.id),
                guild_id=str(member.guild.id),
                channel_id=str(after.channel.id),
                rest=is_rest_channel(after.channel),
                self_mute=after.self_mute,
                server_mute=after.mute,
                self_deaf=after.self_deaf,
                server_deaf=after.deaf
            )
        elif before.channel is not None and after.channel is None:
            logger.info(f"{member} has left {before.channel}")
            end_active_session(user_id=str(member.id), guild_id=str(member.guild.id))
        elif before.channel != after.channel:
            logger.info(f"{member} has moved from {before.channel} to {after.channel}")
            end_active_session(user_id=str(member.id), guild_id=str(member.guild.id))
            get_or_create_active_session(
                user_id=str(member.id),
                guild_id=str(member.guild.id),
                channel_id=str(after.channel.id),
                rest=is_rest_channel(after.channel),
                self_mute=after.self_mute,
                server_mute=after.mute,
                self_deaf=after.self_deaf,
                server_deaf=after.deaf
            )

        if (before.self_mute != after.self_mute
            or before.mute != after.mute
            or before.self_deaf != after.self_deaf
            or before.deaf != after.deaf):

            end_active_session(user_id=str(member.id), guild_id=str(member.guild.id))

            if after.channel is not None:
                get_or_create_active_session(
                    user_id=str(member.id),
                    guild_id=str(member.guild.id),
                    channel_id=str(after.channel.id),
                    rest=is_rest_channel(after.channel),
                    self_mute=after.self_mute,
                    server_mute=after.mute,
                    self_deaf=after.self_deaf,
                    server_deaf=after.deaf
                )
            else:
                logger.warning(f"{member} is not in any voice channel while mute/deaf state changed.")


        if before.self_mute != after.self_mute:
            if after.self_mute:
                logger.debug(f"{member} has been self-muted")
            else:
                logger.debug(f"{member} has been un-self-muted")

        if before.mute != after.mute:
            if after.mute:
                logger.debug(f"{member} has been server-muted")
            else:
                logger.debug(f"{member} has been un-server-muted")

        if before.self_deaf != after.self_deaf:
            if after.self_deaf:
                logger.debug(f"{member} has been self-speaker-muted")
            else:
                logger.debug(f"{member} has been un-self-speaker-muted")

        if before.deaf != after.deaf:
            if after.deaf:
                logger.debug(f"{member} has been server-speaker-muted")
            else:
                logger.debug(f"{member} has been un-server-speaker-muted")

    def reconcile_sessions():
        logger.info("Reconciling ActiveSessions with current voice channel states...")
        with get_db() as db_session:
            active_sessions = db_session.query(ActiveSession).all()
            active_user_guild = set((s.user_id, s.guild_id) for s in active_sessions)

            current_user_guild = set()
            for guild in bot.guilds:
                for channel in guild.voice_channels:
                    for member in channel.members:
                        current_user_guild.add((str(member.id), str(guild.id)))

            users_to_remove = active_user_guild - current_user_guild
            users_to_add = current_user_guild - active_user_guild

            for user_id, guild_id in users_to_remove:
                logger.info(f"Ending ActiveSession for user_id={user_id}, guild_id={guild_id}")
                end_active_session(user_id=user_id, guild_id=guild_id)

            for user_id, guild_id in users_to_add:
                guild = bot.get_guild(int(guild_id))
                if not guild:
                    logger.warning(f"Guild with id {guild_id} not found.")
                    continue

                channel = None
                for ch in guild.voice_channels:
                    if any(str(m.id) == user_id for m in ch.members):
                        channel = ch
                        break

                if channel:
                    member = guild.get_member(int(user_id))
                    if member:
                        logger.info(f"Creating ActiveSession for user_id={user_id}, guild_id={guild_id}, channel_id={channel.id}")
                        get_or_create_active_session(
                            user_id=str(member.id),
                            guild_id=str(member.guild.id),
                            channel_id=str(channel.id),
                            rest=is_rest_channel(channel),
                            self_mute=member.voice.self_mute,
                            server_mute=member.voice.mute,
                            self_deaf=member.voice.self_deaf,
                            server_deaf=member.voice.deaf
                        )
                    else:
                        logger.warning(f"Member with id {user_id} not found in guild {guild_id}.")
                else:
                    logger.warning(f"User with id {user_id} not found in any voice channel of guild {guild_id}.")

            for session in active_sessions:
                guild = bot.get_guild(int(session.guild_id))
                if not guild:
                    logger.warning(f"Guild with id {session.guild_id} not found.")
                    continue

                channel = guild.get_channel(int(session.channel_id))
                if not channel or session.user_id not in [str(m.id) for m in channel.members]:
                    continue

                member = guild.get_member(int(session.user_id))
                if not member:
                    continue

                current_self_mute = member.voice.self_mute
                current_server_mute = member.voice.mute
                current_self_deaf = member.voice.self_deaf
                current_server_deaf = member.voice.deaf

                if (session.is_self_muted != current_self_mute or
                    session.is_server_muted != current_server_mute or
                    session.is_self_deafened != current_self_deaf or
                    session.is_server_deafened != current_server_deaf):

                    logger.info(f"Voice state changed for user_id={session.user_id}, guild_id={session.guild_id}. Updating session.")
                    end_active_session(user_id=session.user_id, guild_id=session.guild_id)

                    get_or_create_active_session(
                        user_id=session.user_id,
                        guild_id=session.guild_id,
                        channel_id=session.channel_id,
                        rest=session.is_rest,
                        self_mute=current_self_mute,
                        server_mute=current_server_mute,
                        self_deaf=current_self_deaf,
                        server_deaf=current_server_deaf
                    )


    async def load_voice_channels():
        for guild in bot.guilds:
            for channel in guild.voice_channels:
                members = channel.members
                if members:
                    logger.debug(f"Voice channel '{channel.name}' has members: {[member.name for member in members]}")
                else:
                    logger.info(f"Voice channel '{channel.name}' is empty")
