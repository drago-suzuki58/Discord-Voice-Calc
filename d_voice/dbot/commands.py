from loguru import logger
import discord
from discord.app_commands import describe

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
        pass

    @tree.command(
        name="voice_week",
        description="Get the voice time for a specific week(s).",
    )
    @describe(
        weeks="The number of weeks to get the voice time for. (Default: 1)",
        id="The user ID to get the voice time for. (Default: Your own)",
    )
    async def voice_week(interaction: discord.Interaction, weeks: int = 1, id: str | None = None):
        pass

    @tree.command(
        name="voice_month",
        description="Get the voice time for a specific month(s).",
    )
    @describe(
        months="The number of months to get the voice time for. (Default: 1)",
        id="The user ID to get the voice time for. (Default: Your own)",
    )
    async def voice_month(interaction: discord.Interaction, months: int = 1, id: str | None = None):
        pass

    @tree.command(
        name="voice_year",
        description="Get the voice time for a specific year(s).",
    )
    @describe(
        years="The number of years to get the voice time for. (Default: 1)",
        id="The user ID to get the voice time for. (Default: Your own)",
    )
    async def voice_year(interaction: discord.Interaction, years: int = 1, id: str | None = None):
        pass

    @tree.command(
        name="voice_total",
        description="Get the total voice time.",
    )
    @describe(
        id="The user ID to get the voice time for. (Default: Your own)",
    )
    async def voice_total(interaction: discord.Interaction, id: str | None = None):
        pass

    @tree.command(
        name="voice_ranking",
        description="Get the voice time ranking",
    )
    async def voice_ranking(interaction: discord.Interaction):
        pass

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

    logger.info("Commands set up successfully!")
