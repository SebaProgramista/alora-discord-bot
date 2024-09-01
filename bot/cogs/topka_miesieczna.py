from discord.ext import commands
from discord.utils import get
from discord import app_commands
import discord

from mysql.connector import Error

from datetime import datetime
from datetime import timedelta

class TopkaMiesieczna(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.logger.info(f"Loaded {self.__class__.__name__} cog")
        self.db_manager = self.bot.db_manager
        self.logger = self.bot.logger
        self.cursor = self.db_manager.cursor

    @app_commands.command(name="topka_miesieczna", description="Sprawdź topke naszych użytkowników!")
    async def self(self, interaction: discord.Interaction):
        # Set month and year
        month = datetime.now().month
        year = datetime.now().year
        name = f"top_for_{month}_{year}"   

        # Set embed
        embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
        embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
        embed.set_author(name=f"Topka użytkowników serwera {interaction.user.guild.name} na miesiac {month}.{year}", icon_url=interaction.user.guild.icon.url)

        # Sort all members
        try:
            self.cursor.execute(f"SELECT * FROM {name}")
        except Error as e:
            self.logger.error(f"{e}")
        members_rows = self.cursor.fetchall()

        # Debug members_list
        self.logger.debug(f"members_rows | {members_rows}")

        personal_rank_text = None
        top_text_members = ""
        for idx, member in enumerate(members_rows):
            # Debug idx member
            self.logger.debug(f"{idx} {member}")

            # Add new member to ranking
            top_text_members += f"\n{self.bot.EMPTY}{self.bot.BULLET}{idx+1}. `{interaction.user.guild.get_member(int(member["member_id"])).name}`: {member["messages_count"]} wiadomosci"

            # Check if member is an author of interaction
            if member["member_id"] == interaction.user.id: personal_rank_text = idx

        # Sort all members
        try:
            self.cursor.execute(f"SELECT * FROM {name}")
        except Error as e:
            self.logger.error(f"{e}")
        self.cursor.fetchall()

        # Debug members_list
        self.logger.debug(f"members_list | {members_rows}")

        personal_rank_voice = None
        top_voice_members = ""
        for idx, member in enumerate(members_rows):
            # Debug idx member
            self.logger.debug(f"{idx} {member}")

            # Add new member to ranking
            top_voice_members += f"\n{self.bot.EMPTY}{self.bot.BULLET}{idx+1}. `{interaction.user.guild.get_member(int(member["member_id"])).name}`: {(timedelta(seconds=member["voice_time"]))}"

            # Check if member is an author of interaction
            if member["member_id"] == interaction.user.id: personal_rank_voice = idx

        # Get member
        try:
            self.cursor.execute(f"SELECT * FROM {name} WHERE member_id = %s", (interaction.user.id,))
        except Error as e:
            self.logger.error(f"{e}")
        self.cursor.fetchone()
            
        # Set personal variables
        if personal_rank_text != None and personal_rank_voice != None:
            # Get member
            try:
                self.cursor.execute(f"SELECT * FROM {name} WHERE member_id = %s", (interaction.user.id,))
            except Error as e:
                self.logger.error(f"{e}")
            self.cursor.fetchone()

            # Add fields to embed
            embed.add_field(name=f"<:emojired:1275843612566880309> **Personalny ranking**", value=f"{self.bot.EMPTY}{self.bot.BULLET}Podczas aktualnego miesiąca udało Ci się wysłać `x wiadomości` co usytuowało Cię na `{personal_rank_text+1}` miejscu oraz rozmawiałeś `x sekund` ze znajomymi, że skończyłeś na miejscu `{personal_rank_voice+1}`", inline=False)
            embed.add_field(name=f"<:forumred:1275854320591704156> **Ranking tekstowy 1-10**", value=top_text_members, inline=False)
            embed.add_field(name=f"<:forumred:1275854320591704156> **Ranking voicechat 1-10**", value=top_voice_members, inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(TopkaMiesieczna(bot))