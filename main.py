from loguru import logger

import d_voice.env as env
from d_voice.dbot.commands import setup_commands
from d_voice.dbot.bot import bot_setup, bot, tree


if __name__ == "__main__":
    logger.add("logs/file_{time}.log", rotation="1 week", enqueue=True)
    setup_commands(tree)
    bot_setup(bot, tree)

    try:
        logger.info("Starting bot...")
        bot.run(env.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
