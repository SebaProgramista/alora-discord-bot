from discord.ext import commands
from discord.utils import get
from discord import app_commands
import discord

from mysql.connector import Error

from datetime import datetime

class Topka(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.logger.info(f"Loaded {self.__class__.__name__} cog")
        self.db_manager = self.bot.db_manager
        self.logger = self.bot.logger
        self.cursor = self.db_manager.cursor

    @app_commands.command(name="topka", description="Sprawdź topke naszych użytkowników!")
    async def self(self, interaction: discord.Interaction):
        # Set embed
        embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
        embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
        embed.set_author(name=f"Topka użytkowników serwera {interaction.user.guild.name}", icon_url=interaction.user.guild.icon.url)

        try:
            self.cursor.execute(f"SELECT * FROM members")
        except Error as e:
            self.logger.error(f"{e}")
        members_rows = self.cursor.fetchall()

        # Debug members_rows
        self.logger.debug(f"members_list | {members_rows}")

        personal_rank = None
        top_members = ""
        for idx, member in enumerate(members_rows):
            # Debug idx member
            self.logger.debug(f"{idx} {member}")

            # Add new member to ranking
            top_members += f"\n{self.bot.EMPTY}{self.bot.BULLET}{idx+1}. `{interaction.user.guild.get_member(int(member["id"])).name}`: {member["xp"]} XP"

            # Check if member is an author of interaction
            if member["id"] == interaction.user.id: personal_rank = idx

        # Ref to firebase members collection and member doc
        try:
            self.cursor.execute(f"SELECT * FROM members WHERE id = %s", (interaction.user.id,))
        except Error as e:
            self.logger.error(f"{e}")
        member_row = self.cursor.fetchone()
            
        # Set personal variables
        if personal_rank != None:
            personal_xp = member_row["xp"]

        # Add fields to embed
        embed.add_field(name=f"<:emojired:1275843612566880309> **Personalny ranking**", value=f"{self.bot.EMPTY}{self.bot.BULLET}Przez cały swój pobyt na serwerze \n{self.bot.EMPTY}{self.bot.EMPTY}uzyskałeś `{personal_xp} xp` co usytuowało Cię na `{personal_rank+1}` miejscu", inline=False)
        embed.add_field(name=f"<:forumred:1275854320591704156> **Ranking 1-10**", value=top_members, inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Topka(bot))