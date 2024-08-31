from discord.ext import commands
from discord.utils import get
from discord import app_commands
import discord

from mysql.connector import Error

from datetime import datetime
import math

class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.logger.info(f"Loaded {self.__class__.__name__} cog")
        self.db_manager = self.bot.db_manager
        self.logger = self.bot.logger
        self.cursor = self.db_manager.cursor
        

    @app_commands.command(name="profile", description="Sprawdź swój profil!")
    async def self(self, interaction: discord.Interaction):

        # Create embed
        embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
        embed.set_author(name=f"Profil użytkownika {interaction.user.name}", icon_url=interaction.user.avatar.url)
        embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")

        # Znalezienie aktualnego poziomu (jeśli użytkownik go ma)
        level_role = None
        for role in interaction.user.roles:
            if "Poziom" in role.name:
                level_role = role
                break  # Zakładamy, że użytkownik ma tylko jedną rolę poziomu

        # Debug level_role
        self.logger.debug(f"level_role | {level_role}")

        # Get user data
        try:
            self.cursor.execute(f"SELECT * FROM members WHERE id = {interaction.user.id}")
        except Error as e:
            self.logger.error(f"{e}")
            return None
        query_result = self.cursor.fetchone()

        # Set user xp
        user_xp = query_result["xp"]

        # Get levels list
        try:
            self.cursor.execute("SELECT * from levels ORDER BY required_points ASC")
        except Error as e:
            self.logger.error(f"{e}")
            return None
        levels_list = self.cursor.fetchall()

        # Debug levels_list
        self.logger.debug(levels_list)

        # Znalezienie aktualnego i następnego poziomu
        current_level = None
        next_level = None

        if level_role == None:
            next_level = levels_list[0]
        else:
            for i, level in enumerate(levels_list):
                if level["role_id"] == str(level_role.id):
                    if i + 1 < len(levels_list):
                        next_level = levels_list[i + 1]
                    break

        # Debug next_level
        self.logger.debug(f"next_level | {next_level}")

        if level_role != None:
            # Tworzenie embedu z informacją o aktualnym poziomie
            embed.add_field(name="<:emojired:1275843612566880309> **Aktualny poziom**", value=f"{self.bot.EMPTY}{self.bot.BULLET}`{level_role.name}`!", inline=False)

        # Dodanie informacji o kolejnym poziomie (jeśli istnieje)
        if next_level:
            embed.add_field(name=f"<:7956education:1275828349301948467> **Postęp kolejnego poziomu** {"●" * math.floor((user_xp/next_level["required_points"])*10)}{"○" * (10 - math.floor((user_xp/next_level["required_points"])*10))} {math.floor((user_xp/next_level["required_points"])*100)}%", value="", inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))