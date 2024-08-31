from discord.ext import commands
from discord.utils import get
import discord

import random
import math
from datetime import datetime

from mysql.connector import Error

class OnMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.logger.info(f"Loaded {self.__class__.__name__} cog")
        self.db_manager = self.bot.db_manager
        self.logger = self.bot.logger
        self.cursor = self.db_manager.cursor

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        self.logger.debug(f"message | {message}")

        # Stop function if on dm channel
        if type(message.channel) == discord.channel.DMChannel: return

        # Stop function beacuse of bot's messages
        if message.author.bot == True: return
        
        # Set random xp gain
        xpGain = math.floor(random.randint(self.bot.MIN_XP_GAIN, self.bot.MAX_XP_GAIN))

        # Debug xpGain
        self.logger.debug(f"xpGain | {xpGain}")

        # Mysql query
        try:
            self.cursor.execute(f"SELECT * FROM members WHERE id = {message.author.id}")
        except Error as e:
            self.logger.error(f"{e}")
            return None
        query_result = self.cursor.fetchone()

        if query_result != None:
            # Debug datetime.now()
            self.logger.debug(f"datetime.now() | {datetime.now()}")
            
            # Debug query_result["last_date"]
            self.logger.debug(f"query_result['last_date'] | f{query_result["last_date"]}")

            # Calculate diff_sec
            diff_sec = (datetime.now() - query_result["last_date"]).seconds

            # Debug diff_sec
            self.logger.debug(f"diff_sec | {diff_sec}")

            if diff_sec > self.bot.MESSAGE_DELAY:
                # Set member_xp
                member_xp = query_result["xp"] + xpGain

                # Update xp
                try:
                    self.cursor.execute(f"UPDATE members SET xp = %s, last_date = %s WHERE id = %s", (member_xp, datetime.now(), query_result["id"]))
                except Error as e:
                    self.logger.error(f"{e}")
                    return None
                else:
                    self.logger.info(f"{message.author.name}({message.author.id}): Got {xpGain} xp")
                    self.db_manager.commit()

                # Get levels
                try:
                    self.cursor.execute(f"SELECT * from levels WHERE required_points < {member_xp} ORDER BY required_points DESC")
                except Error as e:
                    self.logger.error(f"{e}")
                    return None
                query_result = self.cursor.fetchone()
                
                # Debug lowest
                self.logger.debug(f"lowest | {query_result}")
                
                # Add new role and remove old one
                temp = 0
                if query_result != None:
                    new_role = get(message.author.guild.roles, id=int(query_result["role_id"]))   

                    # Debug new_role
                    self.logger.debug(f"new_role | {new_role}")

                    for author_role in message.author.roles:
                        if "Poziom" in author_role.name:
                            temp = 1
                            if author_role.id != query_result["role_id"]:

                                # Add new role
                                await message.author.add_roles(new_role)

                                # Remove old one
                                await message.author.remove_roles(author_role)

                                # Make embed
                                embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
                                embed.add_field(name="**<:education:1274147113353089064> Gratulacje, udało Ci się zdobyć nowy poziom!**", value=f"{self.bot.EMPTYID}{self.bot.BULLETID}`{new_role.name}`")
                                embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
                                embed.set_author(name=f"Nowy poziom", icon_url=message.author.avatar.url)

                                await message.channel.send(embed=embed)

                                break
                    if temp == 0:
                        # Add new role
                        await message.author.add_roles(new_role)

                        # Make embed
                        embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
                        embed.add_field(name="**<:education:1274147113353089064> Gratulacje, udało Ci się zdobyć nowy poziom!**", value=f"{self.bot.EMPTYID}{self.bot.BULLETID}`{new_role.name}`")
                        embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
                        embed.set_author(name=f"Nowy poziom", icon_url=message.author.avatar.url)

                        await message.channel.send(embed=embed)
                else:
                    self.logger.info(f"{message.author.name}({message.author.id}): Need to wait {self.bot.MESSAGE_DELAY - diff_sec}")
        else: 
            try:
                self.cursor.execute(f"INSERT INTO members (id, last_date, xp) VALUES (%s, %s, %s)", (message.author.id, datetime.now(), xpGain))
            except Error as e:
                self.logger.error(f"{e}")
                return None
            else:
                self.logger.warning(f"New member was added to database! ({message.author})")
                self.logger.info(f"{message.author.name}({message.author.id}): Got {xpGain} xp")
                self.db_manager.commit()
                
        # Set month and year
        month = datetime.now().month
        year = datetime.now().year
        name = f"top_for_{month}_{year}"
        
        # Debug name
        self.logger.debug(f"name | {name}")

        try:
            self.cursor.execute(f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{name}'")
        except Error as e:
            self.logger.error(f"{e}")
            return None
        query_result = self.cursor.fetchone()
        
        if query_result != None:
            # Mysql query
            try:
                self.cursor.execute(f"SELECT * FROM {name} WHERE member_id = {message.author.id}")
            except Error as e:
                self.logger.error(f"{e}")
                return None
            query_result = self.cursor.fetchone()

            if query_result != None:
                # Update messages count
                try:
                    self.cursor.execute(f"UPDATE {name} SET messages_count = %s WHERE member_id = %s", (query_result["messages_count"] + 1, message.author.id))
                except Error as e:
                    self.logger.error(f"{e}")
                    return None
                else:
                    self.logger.info(f"{message.author.name}({message.author.id}): Got 1 message count in {name}")
                    self.db_manager.commit()
            else:
                try:
                    self.cursor.execute(f"INSERT INTO {name} (member_id, messages_count) VALUES (%s, %s)", (message.author.id, 1))
                except Error as e:
                    self.logger.error(f"{e}")
                    return None
                else:
                    self.db_manager.commit()
                    self.logger.warning(f"New member was added to {name} table! ({message.author})")
        else:
            try:
                self.cursor.execute(f"CREATE TABLE {name} (`member_id` VARCHAR(18) NOT NULL, `messages_count` INT(10) NOT NULL, `voice_time` INT(10) NOT NULL DEFAULT 0, PRIMARY KEY (`member_id`));")
            except Error as e:
                self.logger.error(f"{e}")
                return None
            else:
                self.db_manager.commit()
                self.logger.warning(f"New table {name} was added to database!")
            
            try:
                self.cursor.execute(f"INSERT INTO {name} (member_id, messages_count) VALUES (%s, %s)", (message.author.id, 1))
            except Error as e:
                self.logger.error(f"{e}")
                return None
            else:
                self.db_manager.commit()
                self.logger.warning(f"New member was added to {name} table! ({message.author})")
            
            self.logger.info(f"{message.author.name}({message.author.id}): Got 1 message in month {month}.{year}")

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMessage(bot))