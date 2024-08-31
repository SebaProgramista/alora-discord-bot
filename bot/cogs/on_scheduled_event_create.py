from discord.ext import commands
from discord.utils import get
import discord

from mysql.connector import Error

from datetime import datetime

class OnScheduledEventCreate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.logger.info(f"Loaded {self.__class__.__name__} cog")

    @commands.Cog.listener()
    async def on_scheduled_event_create(self, event):
        for member in self.bot.get_guild(event.guild_id).members:
            if member.bot != True:
                await member.create_dm()
                async for message in member.dm_channel.history():
                    await message.delete()
                embed = discord.Embed(description=f"**<:channelred:1275856145847681055> Na serwerze `{self.bot.get_guild(event.guild_id).name}` zostało zaplanowane nowe wydarzenie. Jeśli jesteś zainteresowany dostaniesz również podobne przypomnienie jak sie zacznie.**", color=discord.Colour.from_rgb(212, 83, 23), type="link")
                # embed.add_field(name=f"**<:channelred:1275856145847681055> Nazwa eventu**", value=f"{event.name}")
                # embed.add_field(name=f"**<:channelred:1275856145847681055> Odbędzie się**", value=f"{event.start_time}")
                embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
                await member.send(embed=embed, nonce="event")
                await member.send(f"{event.url}", nonce="event")


async def setup(bot: commands.Bot):
    await bot.add_cog(OnScheduledEventCreate(bot))