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
        
    def calc_xp_gain(self, min, max, message: discord.Message):
        xp_gain = round(random.uniform(min, max), 4)
        self.logger.debug(f"[var: 'xp_gain' without any bonus] {xp_gain}")
        role = get(message.author.guild.roles, id=int(self.bot.REVIEWER_ROLE_ID))
        if role in message.author.roles:
            xp_gain *= 1.02
            self.logger.debug(f"[value: 'xp bonus from reviewer role'] {xp_gain * 0.02}")
        self.logger.debug(f"[var: 'xp_gain'] {xp_gain}")
        return xp_gain

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        self.logger.debug(f"[var: message] {message}")

        # Stop function if on dm channel
        if type(message.channel) == discord.channel.DMChannel: return

        # Stop function beacuse of bot's messages
        if message.author.bot == True: return

        # Mysql query
        query_result = self.session_manager.session.query(self.session_manager.member).filter_by(id=message.author.id).one_or_none()

        # Debug query_result
        self.logger.debug(f"[value: 'query_result'] {query_result}")

        if query_result != None:
            # Debug datetime.now()
            self.logger.debug(f"[value: 'datetime.now()'] {datetime.now()}")
            
            # Debug query_result.last_date
            self.logger.debug(f"[var: 'query_result.last_date'] {query_result.last_date}")

            # Calculate diff_sec
            diff_sec = (datetime.now() - query_result.last_date).seconds

            # Debug diff_sec
            self.logger.debug(f"[var: 'diff_sec'] {diff_sec}")

            # Update messages_count
            query_result.messages_count += 1


            if diff_sec > self.bot.MESSAGE_DELAY:
                # Set random xp gain
                xpGain = self.calc_xp_gain(self.bot.MIN_XP_GAIN, self.bot.MAX_XP_GAIN, message)

                # Debug xpGain
                self.logger.debug(f"[var: 'xpGain'] {xpGain}")
                
                # Update xp
                query_result.xp += xpGain

                # Update last_date
                query_result.last_date = datetime.now()

                # Get levels
                level_query_result = self.session_manager.session.query(self.session_manager.level).filter(self.session_manager.level.required_points <= query_result.xp).order_by(asc(self.session_manager.level.required_points)).limit(1).one_or_none()
                
                # Debug levels_query_result
                self.logger.debug(f"[var: 'level_query_result'] {level_query_result}")
                
                # Add new role and remove old one
                temp = 0
                if level_query_result != None:
                    new_role = get(message.author.guild.roles, id=int(level_query_result.role_id))   

                    # Debug new_role
                    self.logger.debug(f"[var: 'new_role'] {new_role}")

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
                new_member = self.session_manager.create_new_member(id=message.author.id, last_date=datetime.now(), xp=xpGain, messages_count=1)
                self.session_manager.session.add(new_member)
            except SQLAlchemyError as e:
                self.logger.error(f"{e}")
                return None
            else:
                self.session_manager.session.commit()

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMessage(bot))