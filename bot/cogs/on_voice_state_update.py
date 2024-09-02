from discord.ext import commands

from sqlalchemy.exc import SQLAlchemyError

from datetime import datetime

class OnVoiceStateUpdate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.logger.info(f"Loaded {self.__class__.__name__} cog")
        self.logger = self.bot.logger

        self.session_manager = self.bot.session_manager

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Debug member.id
        self.logger.debug(f"member.id | {member.id} {type(member.id)}")

        if before.channel == None and after.channel != None:
            # Debug check join channel
            self.logger.info(f"{member.name}({member.id}) Joined {after.channel.name}")

            # Update voice_join_time
            try:
                query_result = self.session_manager.session.query(self.session_manager.member).filter_by(id=member.id).one_or_none()
                query_result.voice_join_time = datetime.now()
            except SQLAlchemyError as e:
                self.logger.error(f"{e}")
                return None
            else:
                self.session_manager.session.commit()

        elif before.channel != None and after.channel == None:
            # Debug check join channel
            self.logger.info(f"{member.name}({member.id}) Left {before.channel.name}")

            # Update voice_join_time
            try:
                query_result = self.session_manager.session.query(self.session_manager.member).filter_by(id=member.id).one_or_none()
                query_result.voice_time += (datetime.now() - query_result.voice_join_time).seconds
                query_result.voice_join_time = None
            except SQLAlchemyError as e:
                self.logger.error(f"{e}")
                return None
            else:
                self.session_manager.session.commit()

async def setup(bot: commands.Bot):
    await bot.add_cog(OnVoiceStateUpdate(bot))