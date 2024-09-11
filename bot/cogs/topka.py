from discord.ext import commands
from discord import app_commands
import discord

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc, desc

class Topka(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.logger.info(f"Loaded {self.__class__.__name__} cog")
        self.logger = self.bot.logger

        self.session_manager = self.bot.session_manager

    @app_commands.command(name="topka", description="Sprawdź topke naszych użytkowników!")
    async def self(self, interaction: discord.Interaction):
        # Set embed
        embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
        embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
        embed.set_author(name=f"Topka użytkowników serwera {interaction.user.guild.name}", icon_url=interaction.user.guild.icon.url)

        try:
            members_query = self.session_manager.session.query(self.session_manager.member).order_by(desc(self.session_manager.member.xp)).limit(10).all()
            personal_rank = None
            top_members = ""
            for idx, member in enumerate(members_query):
                # Debug idx member
                self.logger.debug(f"{idx} {member}")

                # Add new member to ranking
                top_members += f"\n{self.bot.EMPTY}{self.bot.BULLET}{idx+1}. `{interaction.user.guild.get_member(member.id)}`: {member.xp} XP"

                # Check if member is an author of interaction and set variables
                if member.id == interaction.user.id: 
                    personal_rank = idx
                    personal_xp = member.xp
        except SQLAlchemyError as e:
            self.logger.error(f"{e}")
        else:
            self.session_manager.session.commit()

        # Add fields to embed
        embed.add_field(name=f"<:emojired:1275843612566880309> **Personalny ranking**", value=f"{self.bot.EMPTY}{self.bot.BULLET}Przez cały swój pobyt na serwerze \n{self.bot.EMPTY}{self.bot.EMPTY}uzyskałeś `{personal_xp} xp` co usytuowało Cię na `{personal_rank+1}` miejscu", inline=False)
        embed.add_field(name=f"<:forumred:1275854320591704156> **Ranking 1-10**", value=top_members, inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Topka(bot))