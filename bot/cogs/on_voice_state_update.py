from discord.ext import commands
from discord.utils import get
import discord

from mysql.connector import Error

from datetime import datetime

class OnVoiceStateUpdate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.logger.info(f"Loaded {self.__class__.__name__} cog")
        self.db_manager = self.bot.db_manager
        self.logger = self.bot.logger
        self.cursor = self.db_manager.cursor

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Debug member.id
        self.logger.debug(f"member.id | {member.id} {type(member.id)}")

        if before.channel == None and after.channel != None:
            # Debug check join channel
            self.logger.info(f"{member.name}({member.id}) Joined {after.channel.name}")

            # Update messages count
            try:
                self.cursor.execute("UPDATE members SET voice_join_time = %s WHERE id = %s", (datetime.now(), member.id))
            except Error as e:
                self.logger.error(f"{e}")
                return None
            else:
                self.db_manager.commit()

        elif before.channel != None and after.channel == None:
            # Debug check join channel
            self.logger.info(f"{member.name}({member.id}) Left {before.channel.name}")
        
            # Get member
            try:
                self.cursor.execute("SELECT * FROM members WHERE id = %s", (member.id,))
            except Error as e:
                self.logger.error(f"{e}")
                return None
            query_result = self.cursor.fetchone()

            seconds_on_voice = (datetime.now() - query_result["voice_join_time"]).seconds

            try:
                self.cursor.execute(f"UPDATE members SET voice_join_time = NULL WHERE id = %s", (member.id,))
            except Error as e:
                self.logger.error(f"{e}")
                return None
            else:
                self.db_manager.commit()
            
            # Set month and year
            month = datetime.now().month
            year = datetime.now().year
            name = f"top_for_{month}_{year}"
            
            try:
                self.cursor.execute(f"SELECT * FROM {name} WHERE member_id = %s", (member.id,))
            except Error as e:
                self.logger.error(f"{e}")
                return None
            query_result = self.cursor.fetchone()

            try:
                self.cursor.execute(f"UPDATE {name} SET voice_time = %s WHERE member_id = %s", (query_result["voice_time"] + seconds_on_voice, member.id))
            except Error as e:
                self.logger.error(f"{e}")
                return None
            else:
                self.logger.info(f"{member.name}({member.id}) Got {seconds_on_voice} seconds on voice")
                self.db_manager.commit()

async def setup(bot: commands.Bot):
    await bot.add_cog(OnVoiceStateUpdate(bot))