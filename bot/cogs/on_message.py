from discord.ext import commands
from discord.utils import get
import discord

import random
import math
from datetime import datetime

from sqlalchemy import asc, desc
from sqlalchemy.exc import SQLAlchemyError

class OnMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.logger.info(f"Loaded {self.__class__.__name__} cog")
        self.logger = self.bot.logger

        self.session_manager = self.bot.session_manager

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
        query_result = self.session_manager.session.query(self.session_manager.member).filter_by(id=message.author.id).one_or_none()

        # Debug query_result
        self.logger.debug(f"query_result | {query_result}")

        if query_result != None:
            # Debug datetime.now()
            self.logger.debug(f"datetime.now() | {datetime.now()}")
            
            # Debug query_result.last_date
            self.logger.debug(f"query_result.last_date | f{query_result.last_date}")

            # Calculate diff_sec
            diff_sec = (datetime.now() - query_result.last_date).seconds

            # Debug diff_sec
            self.logger.debug(f"diff_sec | {diff_sec}")

            # Update messages_count
            query_result.messages_count += 1


            if diff_sec > self.bot.MESSAGE_DELAY:
                # Update xp
                query_result.xp += xpGain

                # Update last_date
                query_result.last_date = datetime.now()

                # Get levels
                level_query_result = self.session_manager.session.query(self.session_manager.level).filter(self.session_manager.level.required_points <= query_result.xp).order_by(asc(self.session_manager.level.required_points)).limit(1).one_or_none()
                
                # Debug levels_query_result
                self.logger.debug(f"levels_query_result | {level_query_result}")
                
                # Add new role and remove old one
                temp = 0
                if level_query_result != None:
                    new_role = get(message.author.guild.roles, id=int(level_query_result.role_id))   

                    # Debug new_role
                    self.logger.debug(f"new_role | {new_role}")

                    for author_role in message.author.roles:
                        if "Poziom" in author_role.name:
                            temp = 1
                            if author_role.id != level_query_result.role_id:

                                # Add new role
                                await message.author.add_roles(new_role)

                                # Remove old one
                                await message.author.remove_roles(author_role)

                                # Make embed
                                embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
                                embed.add_field(name="**<:education:1274147113353089064> Gratulacje, udało Ci się zdobyć nowy poziom!**", value=f"{self.bot.EMPTY}{self.bot.BULLET}`{new_role.name}`")
                                embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
                                embed.set_author(name=f"Nowy poziom", icon_url=message.author.avatar.url)

                                await message.channel.send(embed=embed)

                                break
                    if temp == 0:
                        # Add new role
                        await message.author.add_roles(new_role)

                        # Make embed
                        embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
                        embed.add_field(name="**<:education:1274147113353089064> Gratulacje, udało Ci się zdobyć nowy poziom!**", value=f"{self.bot.EMPTY}{self.bot.BULLET}`{new_role.name}`")
                        embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
                        embed.set_author(name=f"Nowy poziom", icon_url=message.author.avatar.url)

                        await message.channel.send(embed=embed)
                else:
                    self.logger.info(f"{message.author.name}({message.author.id}): Need to wait {self.bot.MESSAGE_DELAY - diff_sec}")
                    
                # Commit changes
                self.session_manager.session.commit()
        else: 
            try:
                new_member = self.session_manager.create_new_member(id=message.author.id, last_date=datetime.now(), xp=xpGain)
                self.session_manager.session.add(new_member)
            except SQLAlchemyError as e:
                self.logger.error(f"{e}")
                return None
            else:
                self.session_manager.session.commit()

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMessage(bot))