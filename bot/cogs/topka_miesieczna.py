from discord.ext import commands
from discord.utils import get
from discord import app_commands
import discord

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc, desc

from datetime import datetime

class TopkaMiesieczna(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.logger.info(f"Loaded {self.__class__.__name__} cog")
        self.logger = self.bot.logger

        self.session_manager = self.bot.session_manager

    @app_commands.command(name="topka_miesieczna", description="Sprawdź topke naszych użytkowników!")
    async def self(self, interaction: discord.Interaction):

        # Set embed
        embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
        embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
        embed.set_author(name=f"Topka użytkowników serwera {interaction.user.guild.name} na miesiac {datetime.now().month}.{datetime.now().year}", icon_url=interaction.user.guild.icon.url)
        
        try:
            members_query = self.session_manager.session.query(self.session_manager.member).order_by(desc(self.session_manager.member.messages_count)).all()
            top_text_members = ""
            for idx, member in enumerate(members_query):
                top_text_members += f"\n{self.bot.EMPTY}{self.bot.BULLET}{idx+1}. `{interaction.user.guild.get_member(int(member.id)).name}`: {member.messages_count} wiadomosci"

                if member.id == interaction.user.id: 
                    personal_rank_text = idx
                    personal_count_text = member.messages_count
        except SQLAlchemyError as e:
            self.logger.error(f"{e}")
        else:
            self.session_manager.session.commit()
            self.logger.debug(f"top_text_members | {top_text_members}")
            self.logger.debug(f"personal_rank_text | {personal_rank_text}")
            self.logger.debug(f"personal_count_text | {personal_count_text}")

        try:
            members_query = self.session_manager.session.query(self.session_manager.member).order_by(desc(self.session_manager.member.voice_time)).all()
            top_voice_members = ""
            for idx, member in enumerate(members_query):
                top_voice_members += f"\n{self.bot.EMPTY}{self.bot.BULLET}{idx+1}. `{interaction.user.guild.get_member(int(member.id)).name}`: {member.voice_time} wiadomosci"

                if member.id == interaction.user.id: 
                    personal_rank_voice = idx
                    personal_count_voice = member.voice_time
        except SQLAlchemyError as e:
            self.logger.error(f"{e}")
        else:
            self.session_manager.session.commit()
            self.logger.debug(f"top_voice_members | {top_voice_members}")
            self.logger.debug(f"personal_rank_voice | {personal_rank_voice}")
            self.logger.debug(f"personal_count_voice | {personal_count_voice}")

            # Add fields to embed
            embed.add_field(name=f"<:emojired:1275843612566880309> **Personalny ranking**", value=f"{self.bot.EMPTY}{self.bot.BULLET}Podczas aktualnego miesiąca udało Ci się wysłać `{personal_count_text} wiadomości` co usytuowało Cię na `{personal_rank_text+1}` miejscu oraz rozmawiałeś `{personal_count_voice} sekund` ze znajomymi, że skończyłeś na miejscu `{personal_rank_voice+1}`", inline=False)
            embed.add_field(name=f"<:forumred:1275854320591704156> **Ranking tekstowy 1-10**", value=top_text_members, inline=False)
            embed.add_field(name=f"<:forumred:1275854320591704156> **Ranking voicechat 1-10**", value=top_voice_members, inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(TopkaMiesieczna(bot))