from discord.ext import commands
import discord

class OnMemberJoin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.logger.info(f"Loaded {self.__class__.__name__} cog")
        self.logger = self.bot.logger

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            # Create embed
            embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23), description=f"<:channelred:1275856145847681055> **Witaj w Alorze wędrowcze. Nazywam się Eliora, jestem opiekunką ognia. Troszczę się o płomień i troszczę się o Ciebie.\n\n<:addred:1275861013606174730> Pamiętaj, by wybrać swą ścieżkę na <#1253278302039179374>. Kieruj się tym co w Tobie drzemie.**")
            embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")

            # Send dm to member
            await member.create_dm()
            await member.dm_channel.send(embed=embed)
        except:
            self.logger.info(f"I cannot send message to {member.name}({member.id})")

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMemberJoin(bot))