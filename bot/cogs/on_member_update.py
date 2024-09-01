from discord.ext import commands
from discord.utils import get
import discord

from mysql.connector import Error

from datetime import datetime

class OnMemberUpdate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.logger.info(f"Loaded {self.__class__.__name__} cog")
        self.db_manager = self.bot.db_manager
        self.logger = self.bot.logger
        self.cursor = self.db_manager.cursor

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # Check if member has house role
        for role in before.roles:
            if role.name in ["Odwaga", "Empatia", "Równowaga"]:
                return

        # Debug after
        self.logger.debug(f"after | {after.roles}")

        for role in after.roles:
            if role.name in ["Odwaga", "Empatia", "Równowaga"]:
                try:
                    self.cursor.execute(f"UPDATE members SET send = TRUE WHERE id = %s", (after.id,))
                except Error as e:
                    self.logger.error(f"{e}")
                else:
                    self.db_manager.commit()
                    
                # Create embed
                embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23), description=f"<:channelred:1275856145847681055> **Widzę że już wybrałeś swoją ścieżke\n\nNastępnie możesz udać się na <#1276250999513808968>, gdzie będziesz w stanie dobrać sobie dodatkowe role.\nKanał <#1275864080124739624> pozwoli Ci na wybór koloru.\n\n<:addred:1275861013606174730> Gdy skończysz z personalizacją, na kanale <#1271608578503086204> możesz powiedzieć nam kim jesteś.\nNaszym centrum życia jest <#1271608659415138335>, gdzie możesz przywitać się z innymi i rozpocząć swoją przygodę.\n\n<:emojired:1275843612566880309> Żegnaj i kieruj się płomieniem, {after.mention}.**")
                embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")

                # Send dm to member
                await after.create_dm()
                await after.dm_channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMemberUpdate(bot))