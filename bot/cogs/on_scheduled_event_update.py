from discord.ext import commands
import discord
from discord import EventStatus

class OnScheduledEventUpdate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.logger.info(f"Loaded {self.__class__.__name__} cog")
        self.logger = self.bot.logger

    @commands.Cog.listener()
    async def on_scheduled_event_update(self, before, after):
        self.logger.debug(f"scheduled_event_update | {self} | {before.status} | {after.status}")
        
        if before.status == EventStatus.scheduled:
            if after.status == EventStatus.active:
                async for member in after.users():
                    if member.bot != True:
                        try:
                            await member.create_dm()
                            async for message in member.dm_channel.history():
                                await message.delete()
                            embed = discord.Embed(description=f"**<:channelred:1275856145847681055> Na serwerze `{self.bot.get_guild(after.guild_id).name}` zaczęło się już wydarzenie, którym byłeś zainteresowany!**", color=discord.Colour.from_rgb(212, 83, 23), type="link")
                            # embed.add_field(name=f"**<:channelred:1275856145847681055> Nazwa eventu**", value=f"{event.name}")
                            # embed.add_field(name=f"**<:channelred:1275856145847681055> Odbędzie się**", value=f"{event.start_time}")
                            embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
                            await member.send(embed=embed)
                            await member.send(f"{after.url}")
                        except:
                            self.logger.info(f"I cannot send message to {member.name}({member.id})")


async def setup(bot: commands.Bot):
    await bot.add_cog(OnScheduledEventUpdate(bot))