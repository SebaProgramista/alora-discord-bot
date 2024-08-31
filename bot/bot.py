from discord.ext import commands
import discord

from logger_manager import *
from db_manager import DatabaseManager

import os
import typing
import json

config = json.load(open(".config.json"))

db_manager = DatabaseManager()
db_manager.connect()

logger_manager = LoggerManager()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
    
    async def setup_hook(self):
        for i in os.listdir("bot/cogs"):
            if i.endswith(".py"):
                await self.load_extension(f'cogs.{i[:-3]}')

        await self.tree.sync()

    async def on_ready(self):
        bot.logger.info(f"{self.user.name} is ready now!")
        for idx, guild in enumerate(self.guilds):
            bot.logger.info(f"{idx+1}. {guild.name}")

bot = Bot()
bot.db_manager = db_manager
bot.logger = logger_manager.logger

# Constants
bot.MIN_XP_GAIN = config["serverConfig"]["minXpGain"]
bot.MAX_XP_GAIN = config["serverConfig"]["maxXpGain"]
bot.MESSAGE_DELAY = config["serverConfig"]["messageDelay"]

# Emojies
bot.EMPTY = config["statics"]["emojisIDs"]["empty"]
bot.BULLET = config["statics"]["emojisIDs"]["bullet"]
bot.DIVIDER = config["statics"]["emojisIDs"]["divider"]

bot.run(config["discordToken"])