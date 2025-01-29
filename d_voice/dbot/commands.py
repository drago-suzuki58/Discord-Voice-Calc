from loguru import logger
import discord
from discord.app_commands import describe
from datetime import datetime, timedelta

from d_voice.util import get_voice_ranking, get_aggregate_time

def setup_commands(tree: discord.app_commands.CommandTree):
    logger.info("Setting up commands...")

    @tree.command(
        name="voice_day",
        description="Get the voice time for a specific day(s).",
    )
    @describe(
        days="The number of days to get the voice time for. (Default: 1)",
        id="The user ID to get the voice time for. (Default: Your own)",
    )
    async def voice_day(interaction: discord.Interaction, days: int = 1, id: str | None = None):
        await interaction.response.defer()
        logger.debug(f"{interaction.guild_id} - voice_day - {days} - {id}")

        user_id = await resolve_user_id(interaction, id)
        if user_id:
            await display_aggregate(interaction, user_id, "day", days)
        else:
            await interaction.followup.send("Failed to resolve user ID.")

    @tree.command(
        name="voice_week",
        description="Get the voice time for a specific week(s).",
    )
    @describe(
        weeks="The number of weeks to get the voice time for. (Default: 1)",
        id="The user ID to get the voice time for. (Default: Your own)",
    )
    async def voice_week(interaction: discord.Interaction, weeks: int = 1, id: str | None = None):
        await interaction.response.defer()
        logger.debug(f"{interaction.guild_id} - voice_week - {weeks} - {id}")

        user_id = await resolve_user_id(interaction, id)
        if user_id:
            await display_aggregate(interaction, user_id, "week", weeks)
        else:
            await interaction.followup.send("Failed to resolve user ID.")

    @tree.command(
        name="voice_month",
        description="Get the voice time for a specific month(s).",
    )
    @describe(
        months="The number of months to get the voice time for. (Default: 1)",
        id="The user ID to get the voice time for. (Default: Your own)",
    )
    async def voice_month(interaction: discord.Interaction, months: int = 1, id: str | None = None):
        await interaction.response.defer()
        logger.debug(f"{interaction.guild_id} - voice_month - {months} - {id}")

        user_id = await resolve_user_id(interaction, id)
        if user_id:
            await display_aggregate(interaction, user_id, "month", months)
        else:
            await interaction.followup.send("Failed to resolve user ID.")

    @tree.command(
        name="voice_year",
        description="Get the voice time for a specific year(s).",
    )
    @describe(
        years="The number of years to get the voice time for. (Default: 1)",
        id="The user ID to get the voice time for. (Default: Your own)",
    )
    async def voice_year(interaction: discord.Interaction, years: int = 1, id: str | None = None):
        await interaction.response.defer()
        logger.debug(f"{interaction.guild_id} - voice_year - {years} - {id}")

        user_id = await resolve_user_id(interaction, id)
        if user_id:
            await display_aggregate(interaction, user_id, "year", years)
        else:
            await interaction.followup.send("Failed to resolve user ID.")

    @tree.command(
        name="voice_total",
        description="Get the total voice time.",
    )
    @describe(
        id="The user ID to get the voice time for. (Default: Your own)",
    )
    async def voice_total(interaction: discord.Interaction, id: str | None = None):
        await interaction.response.defer()
        logger.debug(f"{interaction.guild_id} - voice_total - {id}")

        user_id = await resolve_user_id(interaction, id)
        if user_id:
            await display_aggregate(interaction, user_id, "all time", 0)
        else:
            await interaction.followup.send("Failed to resolve user ID.")

    @tree.command(
        name="voice_ranking",
        description="Get the voice time ranking",
    )
    async def voice_ranking(interaction: discord.Interaction):
        await interaction.response.defer()
        logger.debug(f"{interaction.guild_id} - voice_ranking")

        since = datetime.now() - timedelta(days=30)
        ranking = get_voice_ranking(guild_id=str(interaction.guild.id), since=since, limit=10)

        embed = discord.Embed(
            title="Voice Time Ranking (Last 30 Days)",
            description="DD:HH:MM (Total Minutes)",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )

        if not ranking:
            embed.description = "No data available."
        else:
            for i, row in enumerate(ranking, start=1):
                user_id = row[0]
                total_time = row[1]
                user = interaction.guild.get_member(int(user_id))
                username = user.display_name if user else f"User ID: {user_id}"

                voice_time_minutes = total_time // 60
                days = voice_time_minutes // (24 * 60)
                remainder = voice_time_minutes % (24 * 60)
                hours = remainder // 60
                mins = remainder % 60

                time_str = f"{days:02}:{hours:02}:{mins:02}"
                embed.add_field(name=f"{i}. {username}", value=f"{time_str} ({voice_time_minutes} min)", inline=False)

        await interaction.followup.send(embed=embed)

    @tree.command(
        name="voice_avarage",
        description="Get the voice time daily avarage",
    )
    @describe(
        id="The user ID to get the voice time for. (Default: Your own)",
        period="The period to calculate the average for. (Default: month)",
        amount="The amount of the period (e.g., 2 for 2 weeks, 3 for 3 months)."
    )
    async def voice_avarage(interaction: discord.Interaction, id: str | None = None, period: str = "month", amount: int = 1):
        await interaction.response.defer()
        logger.debug(f"{interaction.guild_id} - voice_avarage - {id} - {period} - {amount}")
        
        user_id = await resolve_user_id(interaction, id)
        if user_id:
            await display_average(interaction, user_id, period, amount)
        else:
            await interaction.followup.send("Failed to resolve user ID.")

    @voice_day.autocomplete("id")
    @voice_week.autocomplete("id")
    @voice_month.autocomplete("id")
    @voice_year.autocomplete("id")
    @voice_total.autocomplete("id")
    async def autocomplete_id(interaction: discord.Interaction, current: str):
        if interaction.guild:
            users = [
                f"{user.name}{'' if user.discriminator == '0' else f'#{user.discriminator}'}"
                async for user in interaction.guild.fetch_members()
                if current.lower() in f"{user.name}{'' if user.discriminator == '0' else f'#{user.discriminator}'}".lower()
            ]
            return [discord.app_commands.Choice(name=user, value=user) for user in users]
        else:
            return []

    @voice_avarage.autocomplete("period")
    async def period_autocomplete(interaction: discord.Interaction, current: str):
        return [discord.app_commands.Choice(name=period, value=period) for period in ["week", "month", "year"]]

    logger.info("Commands set up successfully!")

async def display_aggregate(interaction: discord.Interaction, user_id: str, period: str, amount: int):
    now = datetime.now()
    if period == "week":
        since = now - timedelta(weeks=amount)
    elif period == "month":
        since = now - timedelta(days=30 * amount)
    elif period == "year":
        since = now - timedelta(days=365 * amount)
    else:
        await interaction.followup.send("Invalid period specified. Please use [\"week\", \"month\", \"year\"]")

    total_sec = get_aggregate_time(user_id, interaction.guild.id, since)
    total_minutes = total_sec // 60
    days = total_minutes // (24 * 60)
    remainder = total_minutes % (24 * 60)
    hours = remainder // 60
    mins = remainder % 60

    time_str = f"{days:02}:{hours:02}:{mins:02}"
    await interaction.followup.send(
        f"Total voice time for <@{user_id}> in the {period}: {time_str} ({total_minutes} min)\n"
        f"(from {since} to now)"
    )

async def display_average(interaction: discord.Interaction, user_id: str, period: str, amount: int):
    now = datetime.now()
    if period == "week":
        since = now - timedelta(weeks=amount)
    elif period == "month":
        since = now - timedelta(days=30 * amount)
    elif period == "year":
        since = now - timedelta(days=365 * amount)
    elif period == "total":
        since = None
    else:
        await interaction.followup.send("Invalid period specified.")
        return

    total_sec = get_aggregate_time(user_id, interaction.guild.id, since)
    days = (now - since).days if since else 1
    average_time_minutes = (total_sec / 60) / days

    total_minutes = int(average_time_minutes)
    days = total_minutes // (24 * 60)
    hours = total_minutes // 60
    mins = total_minutes % 60

    time_str = f"{hours:02}:{mins:02}"
    await interaction.followup.send(
        f"Daily average voice time for <@{user_id}>: {time_str} ({average_time_minutes:.2f} min)\n"
        f"(from {since if since else 'all time'} to now)"
    )

async def resolve_user_id(interaction: discord.Interaction, username: str | None) -> str | None:
    if username:
        guild = interaction.guild
        if not guild:
            await interaction.followup.send("This command must be run in a guild.")
            return None

        if '#' in username:
            name, discriminator = username.split('#')
            matched_members = [member for member in guild.members if member.name == name and member.discriminator == discriminator]
        else:
            matched_members = [member for member in guild.members if member.name == username]

        if len(matched_members) == 0:
            await interaction.followup.send(f"Username '{username}' not found.")
            return None
        elif len(matched_members) > 1:
            await interaction.followup.send(f"Username '{username}' found multiple members.")
            return None
        else:
            return str(matched_members[0].id)
    else:
        return str(interaction.user.id)