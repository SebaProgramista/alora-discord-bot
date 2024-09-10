from discord.ext import commands
import discord

from logger_manager import *
from session_manager import SessionManager
from sqlalchemy.exc import SQLAlchemyError

import os
import json
from datetime import datetime

config = json.load(open(".config.json"))

session_manager = SessionManager

logger_manager = LoggerManager()
logger = logger_manager.logger

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
            self.refresh_levels(guild)
            self.set_voice_join_time(guild)
    
    # Set voice_join_time for members who are currently on voice
    def set_voice_join_time(self, guild: discord.Guild):
        for member in self.get_guild(guild.id).members:
            if member.voice != None:
                try:
                    query_result = session_manager.session.query(session_manager.member).filter_by(id=member.id).one_or_none()
                    query_result.voice_join_time = datetime.now()
                except SQLAlchemyError as e:
                    logger.error(f"{e}")
                    return None
                else:
                    session_manager.session.commit()
                    logger.info("Voice_join_time has been set for members who are currently using voice")

    def refresh_levels(self, guild: discord.Guild):
        try:
            levels = session_manager.session.query(session_manager.level).all()
            for level in levels:
                session_manager.session.delete(level)
            req = 0
            add = 1000
            for role in self.get_guild(guild.id).roles:
                if "Poziom" in role.name:
                    req += add
                    add *= 1.10
                    level = session_manager.create_new_level(role_id=role.id, required_points=req)
                    session_manager.session.add(level)
        except SQLAlchemyError as e:
            logger.error(e)
        else:
            session_manager.session.commit()
            logger.info("Levels have been refreshed")

bot = Bot()
# bot.db_manager = db_manager
bot.session_manager = session_manager
bot.logger = logger

# Constants
bot.MIN_XP_GAIN = config["serverConfig"]["minXpGain"]
bot.MAX_XP_GAIN = config["serverConfig"]["maxXpGain"]
bot.MESSAGE_DELAY = config["serverConfig"]["messageDelay"]

# Emojies
bot.EMPTY = config["statics"]["emojisIDs"]["empty"]
bot.BULLET = config["statics"]["emojisIDs"]["bullet"]
bot.DIVIDER = config["statics"]["emojisIDs"]["divider"]

print("run")
bot.run(config["discordToken"])

try:
    members_query = session_manager.session.query(session_manager.member).filter(session_manager.member.voice_join_time!=None).all()
    for member_query in members_query:
        member_query.voice_join_time = None
except SQLAlchemyError as e:
    logger.error(f"{e}")
else:
    session_manager.session.commit()
    logger.info("Voice_join_time has been set for members who are currently using voice")