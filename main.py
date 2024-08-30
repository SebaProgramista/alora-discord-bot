from google.cloud.firestore_v1.base_query import FieldFilter
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import db, credentials
import firebase_admin
import discord
from datetime import datetime
import datetime
import math
import random
from operator import itemgetter
from discord.utils import get
from discord import EventStatus

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import json
from discord.ui import Select, View, TextInput
from discord.ext import commands
from discord.ui import Button
import discord.utils
from discord.utils import get
from discord import CategoryChannel, app_commands
import discord
from discord.ext.commands import has_permissions
from datetime import datetime

import json
from discord.ui import Select, View
from discord.ext import commands, tasks
from discord.ui import Button
from discord import app_commands

from datetime import datetime
from datetime import timedelta

from loguru import logger

import mysql.connector
from mysql.connector import Error

# Get hidden values from .config.json
config = json.load(open(".config.json"))
discordToken = config["discordToken"]
aloraID = config["serverID"]
firstWarnRole = config["serverRoles"]["firstWarnRoleID"]
secWarnRole = config["serverRoles"]["secWarnRoleID"]

# Get emojis values from .config.json
subentryID = config["statics"]["emojisIDs"]["subentry"]
bulletID = config["statics"]["emojisIDs"]["bullet"]
dividerID = config["statics"]["emojisIDs"]["divider"]
emptyID = config["statics"]["emojisIDs"]["empty"]
debugMode = config["debugMode"]

# Get values for database
host = config["database"]["host"]
user = config["database"]["user"]
passwd = config["database"]["passwd"]
database = config["database"]["database"]

# Config firebase
cred = credentials.Certificate(".serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

mysqldb = mysql.connector.connect(
    host=host,
    user=user,
    passwd=passwd,
    database=database
)
cursor = mysqldb.cursor(dictionary=True, buffered=True)

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False
        self.index_of_update_houses_channels_name_loop = 1

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=aloraID))
            self.synced = True

        # try:
        #     cursor.execute("CREATE")
        # except Error as e:
        #     logger.error(f"{e}")
        #     return None



        if debugMode == True: logger.warning(f"Debug mode is on, remember about it")
        logger.info(f"We have logged in as {self.user}")
        logger.info(f"Servers:")
        for idx, guild in enumerate(self.guilds):
            logger.info(f"{idx+1}. {guild.name}({guild.id})")
            for member in guild.members:
                try:
                    cursor.execute(f"UPDATE members SET voice_join_time = %s WHERE id = %s", (datetime.now(), member.id))
                except Error as e:
                    logger.error(f"{e}")
                else:
                    mysqldb.commit()

            # for doc in db.collection("levels").get():
            #     levels_dict = db.collection("levels").document(doc.id).get().to_dict() 
            #     try:
            #         cursor.execute("INSERT INTO levels (role_id, required_points) VALUES (%s, %s)", (levels_dict["role_id"], math.floor(levels_dict["required_points"])))
            #     except Error as e:
            #         logger.error(f"{e}")
            #         return None
            #     else:
            #         mysqldb.commit()

            # temp = 1000
            # sum = 0
            # for role in guild.roles:
            #     if "Poziom" in role.name:
            #         sum += temp
            #         temp *= 1.10
            #         try:
            #             cursor.execute("INSERT INTO levels (role_id, required_points) VALUES (%s, %s)", (role.id, sum))
            #         except Error as e:
            #             logger.error(f"{e}")
            #             return None
            #         else:
            #             mysqldb.commit()
            #         print(role)

    async def on_member_join(self, member: discord.Member):
        # Create embed
        embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23), description=f"<:channelred:1275856145847681055> **Witaj w Alorze wędrowcze. Nazywam się Eliora, jestem opiekunką ognia. Troszczę się o płomień i troszczę się o Ciebie.\n\n<:addred:1275861013606174730> Pamiętaj, by wybrać swą ścieżkę na <#1253278302039179374>. Kieruj się tym co w Tobie drzemie.**")
        embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")

        # Send dm to member
        await member.create_dm()
        await member.dm_channel.send(embed=embed)

    async def on_voice_state_update(self, member, before, after):
        # Debug member.id
        if debugMode: logger.debug(f"member.id | {member.id} {type(member.id)}")

        if before.channel == None and after.channel != None:
            # Debug check join channel
            if debugMode: logger.info(f"{member.name}({member.id}) Joined {after.channel.name}")

            # Update messages count
            try:
                cursor.execute("UPDATE members SET voice_join_time = %s WHERE id = %s", (datetime.now(), member.id))
            except Error as e:
                logger.error(f"{e}")
                return None
            else:
                mysqldb.commit()

        elif before.channel != None and after.channel == None:
            # Debug check join channel
            if debugMode: logger.info(f"{member.name}({member.id}) Left {before.channel.name}")
        
            # Get member
            try:
                cursor.execute("SELECT * FROM members WHERE id = %s", (member.id,))
            except Error as e:
                logger.error(f"{e}")
                return None
            query_result = cursor.fetchone()

            seconds_on_voice = (datetime.now() - query_result["voice_join_time"]).seconds

            try:
                cursor.execute(f"UPDATE members SET voice_join_time = NULL WHERE id = %s", (member.id,))
            except Error as e:
                logger.error(f"{e}")
                return None
            else:
                mysqldb.commit()
            
            # Set month and year
            month = datetime.now().month
            year = datetime.now().year
            name = f"top_for_{month}_{year}"
            
            try:
                cursor.execute(f"SELECT * FROM {name} WHERE member_id = %s", (member.id,))
            except Error as e:
                logger.error(f"{e}")
                return None
            query_result = cursor.fetchone()

            try:
                cursor.execute(f"UPDATE {name} SET voice_time = %s WHERE member_id = %s", (query_result["voice_time"] + seconds_on_voice, member.id))
            except Error as e:
                logger.error(f"{e}")
                return None
            else:
                logger.info(f"{member.name}({member.id}) Got {seconds_on_voice} seconds on voice")
                mysqldb.commit()

    async def on_member_update(self, before, after):
        # Check if member has house role
        for role in before.roles:
            if role.name in ["Odwaga", "Empatia", "Równowaga"]:
                return

        # Debug after
        logger.debug(f"after | {after.roles}")

        for role in after.roles:
            if role.name in ["Odwaga", "Empatia", "Równowaga"]:
                try:
                    cursor.execute(f"UPDATE members SET send = TRUE WHERE id = %s", (member.id,))
                except Error as e:
                    logger.error(f"{e}")
                else:
                    mysqldb.commit()
                    
                # Create embed
                embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23), description=f"<:channelred:1275856145847681055> **Widzę że już wybrałeś swoją ścieżke\n\nNastępnie możesz udać się na <#1276250999513808968>, gdzie będziesz w stanie dobrać sobie dodatkowe role.\nKanał <#1275864080124739624> pozwoli Ci na wybór koloru.\n\n<:addred:1275861013606174730> Gdy skończysz z personalizacją, na kanale <#1271608578503086204> możesz powiedzieć nam kim jesteś.\nNaszym centrum życia jest <#1271608659415138335>, gdzie możesz przywitać się z innymi i rozpocząć swoją przygodę.\n\n<:emojired:1275843612566880309> Żegnaj i kieruj się płomieniem, {after.mention}.**")
                embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")

                # Send dm to member
                await after.create_dm()
                await after.dm_channel.send(embed=embed)

    async def on_scheduled_event_create(self, event):
        for member in client.get_guild(event.guild_id).members:
            if member.bot != True:
                await member.create_dm()
                async for message in member.dm_channel.history():
                    await message.delete()
                embed = discord.Embed(description=f"**<:channelred:1275856145847681055> Na serwerze `{client.get_guild(event.guild_id).name}` zostało zaplanowane nowe wydarzenie. Jeśli jesteś zainteresowany dostaniesz również podobne przypomnienie jak sie zacznie.**", color=discord.Colour.from_rgb(212, 83, 23), type="link")
                # embed.add_field(name=f"**<:channelred:1275856145847681055> Nazwa eventu**", value=f"{event.name}")
                # embed.add_field(name=f"**<:channelred:1275856145847681055> Odbędzie się**", value=f"{event.start_time}")
                embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
                await member.send(embed=embed, nonce="event")
                await member.send(f"{event.url}", nonce="event")

    async def on_scheduled_event_update(self, before, after):
        if debugMode == True: logger.debug(f"scheduled_event_update | {self} | {before.status} | {after.status}")
        
        if before.status == EventStatus.scheduled:
            if after.status == EventStatus.active:
                async for member in after.users():
                    if member.bot != True:
                        await member.create_dm()
                        async for message in member.dm_channel.history():
                            await message.delete()
                        embed = discord.Embed(description=f"**<:channelred:1275856145847681055> Na serwerze `{client.get_guild(after.guild_id).name}` zaczęło się już wydarzenie, którym byłeś zainteresowany!**", color=discord.Colour.from_rgb(212, 83, 23), type="link")
                        # embed.add_field(name=f"**<:channelred:1275856145847681055> Nazwa eventu**", value=f"{event.name}")
                        # embed.add_field(name=f"**<:channelred:1275856145847681055> Odbędzie się**", value=f"{event.start_time}")
                        embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
                        await member.send(embed=embed)
                        await member.send(f"{after.url}")
        
    async def on_message(self, message):
        # Debug message
        if debugMode == True: logger.debug(f"message | {message}")

        # Stop function if on dm channel
        if type(message.channel) == discord.channel.DMChannel: return

        # Stop function beacuse of bot's messages
        if message.author.bot == True: return
        
        # Set random xp gain
        xpGain = math.floor(random.randint(config["serverConfig"]["minXpGain"], config["serverConfig"]["maxXpGain"]))

        # Debug xpGain
        if debugMode == True: logger.debug(f"xpGain | {xpGain}")

        # Mysql query
        try:
            cursor.execute(f"SELECT * FROM members WHERE id = {message.author.id}")
        except Error as e:
            logger.error(f"{e}")
            return None
        query_result = cursor.fetchone()

        if query_result != None:
            # Debug datetime.now()
            if debugMode: logger.debug(f"datetime.now() | {datetime.now()}")
            
            # Debug query_result["last_date"]
            if debugMode: logger.debug(f"query_result['last_date'] | f{query_result["last_date"]}")

            # Calculate diff_sec
            diff_sec = (datetime.now() - query_result["last_date"]).seconds

            # Debug diff_sec
            if debugMode: logger.debug(f"diff_sec | {diff_sec}")

            if diff_sec > config["serverConfig"]["messageDelay"]:
                # Set member_xp
                member_xp = query_result["xp"] + xpGain

                # Update xp
                try:
                    cursor.execute(f"UPDATE members SET xp = %s, last_date = %s WHERE id = %s", (member_xp, datetime.now(), query_result["id"]))
                except Error as e:
                    logger.error(f"{e}")
                    return None
                else:
                    logger.info(f"{message.author.name}({message.author.id}): Got {xpGain} xp")
                    mysqldb.commit()

                # Get levels
                try:
                    cursor.execute(f"SELECT * from levels WHERE required_points < {member_xp} ORDER BY required_points DESC")
                except Error as e:
                    logger.error(f"{e}")
                    return None
                query_result = cursor.fetchone()
                
                # Debug lowest
                if debugMode == True: logger.debug(f"lowest | {query_result}")
                
                # Add new role and remove old one
                temp = 0
                if query_result != None:
                    new_role = get(message.author.guild.roles, id=int(query_result["role_id"]))   

                    # Debug new_role
                    if debugMode: logger.debug(f"new_role | {new_role}")

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
                                embed.add_field(name="**<:education:1274147113353089064> Gratulacje, udało Ci się zdobyć nowy poziom!**", value=f"{emptyID}{bulletID}`{new_role.name}`")
                                embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
                                embed.set_author(name=f"Nowy poziom", icon_url=message.author.avatar.url)

                                await message.channel.send(embed=embed)

                                break
                    if temp == 0:
                        # Add new role
                        await message.author.add_roles(new_role)

                        # Make embed
                        embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
                        embed.add_field(name="**<:education:1274147113353089064> Gratulacje, udało Ci się zdobyć nowy poziom!**", value=f"{emptyID}{bulletID}`{new_role.name}`")
                        embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
                        embed.set_author(name=f"Nowy poziom", icon_url=message.author.avatar.url)

                        await message.channel.send(embed=embed)
                else:
                    logger.info(f"{message.author.name}({message.author.id}): Need to wait {config["serverConfig"]["messageDelay"] - diff_sec}")
        else: 
            try:
                cursor.execute(f"INSERT INTO members (id, last_date, xp) VALUES (%s, %s, %s)", (message.author.id, datetime.now(), xpGain))
            except Error as e:
                logger.error(f"{e}")
                return None
            else:
                logger.warning(f"New member was added to database! ({message.author})")
                logger.info(f"{message.author.name}({message.author.id}): Got {xpGain} xp")
                mysqldb.commit()
                
        # Set month and year
        month = datetime.now().month
        year = datetime.now().year
        name = f"top_for_{month}_{year}"
        
        # Debug name
        if debugMode: logger.debug

        try:
            cursor.execute(f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{name}'")
        except Error as e:
            logger.error(f"{e}")
            return None
        query_result = cursor.fetchone()
        
        if query_result != None:
            # Mysql query
            try:
                cursor.execute(f"SELECT * FROM {name} WHERE member_id = {message.author.id}")
            except Error as e:
                logger.error(f"{e}")
                return None
            query_result = cursor.fetchone()

            if query_result != None:
                # Update messages count
                try:
                    cursor.execute(f"UPDATE {name} SET messages_count = %s WHERE member_id = %s", (query_result["messages_count"] + 1, message.author.id))
                except Error as e:
                    logger.error(f"{e}")
                    return None
                else:
                    logger.info(f"{message.author.name}({message.author.id}): Got 1 message count in {name}")
                    mysqldb.commit()
            else:
                try:
                    cursor.execute(f"INSERT INTO {name} (member_id, messages_count) VALUES (%s, %s)", (message.author.id, 1))
                except Error as e:
                    logger.error(f"{e}")
                    return None
                else:
                    mysqldb.commit()
                    logger.warning(f"New member was added to {name} table! ({message.author})")
        else:
            try:
                cursor.execute(f"CREATE TABLE {name} (`member_id` VARCHAR(18) NOT NULL, `messages_count` INT(10) NOT NULL, `voice_time` INT(10) NOT NULL DEFAULT 0, PRIMARY KEY (`member_id`));")
            except Error as e:
                logger.error(f"{e}")
                return None
            else:
                mysqldb.commit()
                logger.warning(f"New table {name} was added to database!")
            
            try:
                cursor.execute(f"INSERT INTO {name} (member_id, messages_count) VALUES (%s, %s)", (message.author.id, 1))
            except Error as e:
                logger.error(f"{e}")
                return None
            else:
                mysqldb.commit()
                logger.warning(f"New member was added to {name} table! ({message.author})")
            
            logger.info(f"{message.author.name}({message.author.id}): Got 1 message in month {month}.{year}")

client = aclient()
tree = app_commands.CommandTree(client)

@tree.command(name="topka", guild=discord.Object(id=aloraID), description="Sprawdź topke naszych użytkowników!")
async def self(interaction: discord.Interaction):
    # Set embed
    embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
    embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
    embed.set_author(name=f"Topka użytkowników serwera {interaction.user.guild.name}", icon_url=interaction.user.guild.icon.url)

    try:
        cursor.execute(f"SELECT * FROM members")
    except Error as e:
        logger.error(f"{e}")
    members_rows = cursor.fetchall()

    # Debug members_rows
    if debugMode == True: logger.debug(f"members_list | {members_rows}")

    personal_rank = None
    top_members = ""
    for idx, member in enumerate(members_rows):
        # Debug idx member
        if debugMode == True: logger.debug(f"{idx} {member}")

        # Add new member to ranking
        top_members += f"\n{emptyID}{bulletID}{idx+1}. `{interaction.user.guild.get_member(int(member["id"])).name}`: {member["xp"]} XP"

        # Check if member is an author of interaction
        if member["id"] == interaction.user.id: personal_rank = idx

    # Ref to firebase members collection and member doc
    try:
        cursor.execute(f"SELECT * FROM members WHERE id = %s", (interaction.user.id,))
    except Error as e:
        logger.error(f"{e}")
    member_row = cursor.fetchone()
        
    # Set personal variables
    if personal_rank != None:
        personal_xp = member_row["xp"]

    # Add fields to embed
    embed.add_field(name=f"<:emojired:1275843612566880309> **Personalny ranking**", value=f"{emptyID}{bulletID}Przez cały swój pobyt na serwerze \n{emptyID}{emptyID}uzyskałeś `{personal_xp} xp` co usytuowało Cię na `{personal_rank+1}` miejscu", inline=False)
    embed.add_field(name=f"<:forumred:1275854320591704156> **Ranking 1-10**", value=top_members, inline=False)

    await interaction.response.send_message(embed=embed)

@tree.command(name="topka_miesieczna", guild=discord.Object(id=aloraID), description="Sprawdź topke naszych użytkowników!")
async def self(interaction: discord.Interaction):
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
        cursor.execute(f"SELECT * FROM {name}")
    except Error as e:
        logger.error(f"{e}")
    members_rows = cursor.fetchall()

    # Debug members_list
    if debugMode == True: logger.debug(f"members_rows | {members_rows}")

    personal_rank_text = None
    top_text_members = ""
    for idx, member in enumerate(members_rows):
        # Debug idx member
        if debugMode == True: logger.debug(f"{idx} {member}")

        # Add new member to ranking
        top_text_members += f"\n{emptyID}{bulletID}{idx+1}. `{interaction.user.guild.get_member(int(member["member_id"])).name}`: {member["messages_count"]} wiadomosci"

        # Check if member is an author of interaction
        if member["member_id"] == interaction.user.id: personal_rank_text = idx

    # Sort all members
    try:
        cursor.execute(f"SELECT * FROM {name}")
    except Error as e:
        logger.error(f"{e}")
    members_rows = cursor.fetchall()

    # Debug members_list
    if debugMode == True: logger.debug(f"members_list | {members_rows}")

    personal_rank_voice = None
    top_voice_members = ""
    for idx, member in enumerate(members_rows):
        # Debug idx member
        if debugMode == True: logger.debug(f"{idx} {member}")

        # Add new member to ranking
        top_voice_members += f"\n{emptyID}{bulletID}{idx+1}. `{interaction.user.guild.get_member(int(member["member_id"])).name}`: {(timedelta(seconds=member["voice_time"]))}"

        # Check if member is an author of interaction
        if member["member_id"] == interaction.user.id: personal_rank_voice = idx

    # Get member
    try:
        cursor.execute(f"SELECT * FROM {name} WHERE member_id = %s", (interaction.user.id,))
    except Error as e:
        logger.error(f"{e}")
    member_row = cursor.fetchone()
        
    # Set personal variables
    if personal_rank_text != None and personal_rank_voice != None:
        # Get member
        try:
            cursor.execute(f"SELECT * FROM {name} WHERE member_id = %s", (interaction.user.id,))
        except Error as e:
            logger.error(f"{e}")
        data = cursor.fetchone()

        # Add fields to embed
        embed.add_field(name=f"<:emojired:1275843612566880309> **Personalny ranking**", value=f"{emptyID}{bulletID}Podczas aktualnego miesiąca udało Ci się wysłać `{data["messages_count"]} wiadomości` co usytuowało Cię na `{personal_rank_text+1}` miejscu oraz rozmawiałeś `{data["voice_time"]} sekund` ze znajomymi, że skończyłeś na miejscu `{personal_rank_voice+1}`", inline=False)
        embed.add_field(name=f"<:forumred:1275854320591704156> **Ranking tekstowy 1-10**", value=top_text_members, inline=False)
        embed.add_field(name=f"<:forumred:1275854320591704156> **Ranking voicechat 1-10**", value=top_voice_members, inline=False)

    await interaction.response.send_message(embed=embed)

@tree.command(name="profile", guild=discord.Object(id=aloraID), description="Sprawdź swój profil!")
async def self(interaction: discord.Interaction):

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
    if debugMode: logger.debug(f"level_role | {level_role}")

    # Get user data
    try:
        cursor.execute(f"SELECT * FROM members WHERE id = {interaction.user.id}")
    except Error as e:
        logger.error(f"{e}")
        return None
    query_result = cursor.fetchone()

    # Set user xp
    user_xp = query_result["xp"]

    # Get levels list
    try:
        cursor.execute("SELECT * from levels ORDER BY required_points ASC")
    except Error as e:
        logger.error(f"{e}")
        return None
    levels_list = cursor.fetchall()

    # Debug levels_list
    if debugMode: logger.debug(levels_list)

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
    if debugMode: logger.debug(f"next_level | {next_level}")

    if level_role != None:
        # Tworzenie embedu z informacją o aktualnym poziomie
        embed.add_field(name="<:emojired:1275843612566880309> **Aktualny poziom**", value=f"{emptyID}{bulletID}`{level_role.name}`!", inline=False)

    # Dodanie informacji o kolejnym poziomie (jeśli istnieje)
    if next_level:
        embed.add_field(name=f"<:7956education:1275828349301948467> **Postęp kolejnego poziomu** {"●" * math.floor((user_xp/next_level["required_points"])*10)}{"○" * (10 - math.floor((user_xp/next_level["required_points"])*10))} {math.floor((user_xp/next_level["required_points"])*100)}%", value="", inline=False)

    await interaction.response.send_message(embed=embed)


# @tree.command(name="history", description="Pokazuje historię warnów", guild=discord.Object(id=aloraID))
# async def self(interaction: discord.Interaction, member: discord.User):

#     if interaction.permissions.administrator == False and member.id is not interaction.user.id:
#         embed = discord.Embed(
#             description="Nie masz uprawnień do sprawdzenia historii kar innego użytkownika!", color=discord.Colour.red())
#         embed.set_author(
#             name=f"Historia użytkownika {member.name}", icon_url=member.avatar.url)
#         embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
#         await interaction.response.send_message(embed=embed)
#         return

#     # Set embed
#     embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))

#     sum_of_points = 0
#     description = ""

#     user_ref = db.collection("warns").document(
#         str(member.id))

#     if user_ref.get().exists:
#         # Get history ref
#         history_ref = user_ref.collection("history")

#         query = history_ref.order_by(
#             "date", direction=firestore.Query.DESCENDING)
#         history_results = query.stream()

#         for idx, history_result in enumerate(history_results):
#             history_item_dict = history_result.to_dict()

#             key = history_result.id
#             date = datetime.fromtimestamp(
#                 history_item_dict['date'].timestamp()).strftime('%d/%m/%Y, %H:%M:%S')
#             reason = history_item_dict["reason"]
#             added_points = history_item_dict["new_points"] - \
#                 history_item_dict["old_points"]

#             if interaction.permissions.administrator:
#                 embed.add_field(name=f"<:channelred:1275856145847681055> `Index: {idx + 1} | Key: {key}`", value=f"<:eventred:1275861012100288553> **Date:** {date}\n<:announcementattentionred:1275861014872854592> **Powód:** {reason}\n<:addred:1275861013606174730> **Punktacja:** {added_points}\n\n", inline=False)
#             else:
#                 embed.add_field(name=f"<:channelred:1275856145847681055> `Index: {idx + 1}`", value=f"<:eventred:1275861012100288553> **Date:** {date}\n<:announcementattentionred:1275861014872854592> **Powód:** {reason}\n<:addred:1275861013606174730> **Punktacja:** {added_points}\n\n", inline=False)

#             sum_of_points += history_item_dict["new_points"] - \
#                 history_item_dict["old_points"]

#         # Set embed
#         embed.description = f"Suma punktów: {sum_of_points}"
#         embed.set_author(
#             name=f"Historia użytkownika {member.name}", icon_url=member.avatar.url)
#         embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")

#         await interaction.response.send_message(embed=embed)

#     else:
#         embed = discord.Embed(
#             description="Podany użytkownik nie posiada żadnych wprowadzonych warnów do bazy danych", color=discord.Colour.red())
#         embed.set_author(
#             name=f"Historia użytkownika {member.name}", icon_url=member.avatar.url)
#         await interaction.response.send_message(embed=embed)


# @tree.command(name="add_points", description="Dodaje warna użytkownikowi", guild=discord.Object(id=aloraID))
# @app_commands.default_permissions(administrator=True)
# async def self(interaction: discord.Interaction, member: discord.User, points: int, reason: str):

#     # Set user ref
#     user_ref = db.collection("warns").document(str(member.id))

#     # Get actual points
#     if user_ref.get().exists:
#         actual_points = user_ref.get().to_dict()["points"]
#     else:
#         actual_points = 0

#     # Set embed
#     embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
#     embed.set_author(
#         name=f"Dodanie warna użytkownikowi {member.name}", icon_url=member.avatar.url)
#     embed.add_field(name=f"<:announcementattentionred:1275861014872854592> Powód:", value=f"{reason}", inline=False)
#     embed.add_field(name=f"<:addred:1275861013606174730> Punkty za warna: `{points}`", value="", inline=False)
#     embed.add_field(name=f"<:channelred:1275856145847681055> Aktualne punkty:`{actual_points}`", value="", inline=False)
#     embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")

#     btn_confirm = Button(
#         label="Confirm", style=discord.ButtonStyle.green, emoji="✔️")
#     btn_cancel = Button(
#         label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")

#     async def btn_confirm_callback(interaction: discord.Interaction):
#         # Get variables
#         nonlocal embed, actual_points, user_ref

#         actual_points = actual_points + points
#         user_data = user_ref.get()
#         if user_data.exists:
#             # Set user's points
#             user_points = user_data.to_dict()["points"]
#             user_ref.set({
#                 "points": user_points + points
#             })

#             # Add item to history
#             user_ref.collection("history").add({
#                 "new_points": user_points + points,
#                 "old_points": user_points,
#                 "reason": reason,
#                 "date": datetime.now()
#             })

#             if user_points + points >= 30 and user_points + points < 60:
#                 await member.add_roles(discord.Object(id=firstWarnRole))
#             elif user_points + points >= 60:
#                 await member.remove_roles(discord.Object(id=firstWarnRole))
#                 await member.add_roles(discord.Object(id=secWarnRole))

#         else:
#             # Create new user
#             user_ref.set({"points": points})
#             user_ref.collection("history").add({
#                 "new_points": points,
#                 "old_points": 0,
#                 "reason": reason,
#                 "date": datetime.now()
#             })
#             actual_points = points

#         # Set new embed
#         embed = discord.Embed(description="**<:channelred:1275856145847681055> Warn został dodany pomyślnie**",color=discord.Colour.from_rgb(212, 83, 23))
#         embed.set_author(
#             name=f"Dodanie warna użytkownikowi {member.name}", icon_url=member.avatar.url)
#         embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
#         await interaction.response.edit_message(embed=embed, view=None)

#     async def btn_cancel_callback(interaction: discord.Interaction):
#         await interaction.response.edit_message(content="canceled", embed=None, view=None)

#     btn_confirm.callback = btn_confirm_callback
#     btn_cancel.callback = btn_cancel_callback

#     # Set view
#     view = View()
#     view.add_item(btn_confirm)
#     view.add_item(btn_cancel)

#     await interaction.response.send_message(view=view, embed=embed)


# @tree.command(name="remove_points", description="Usuwa warna użytkownikowi", guild=discord.Object(id=aloraID))
# @app_commands.default_permissions(administrator=True)
# async def self(interaction: discord.Interaction, member: discord.User, key: str):

#     history_ref = db.collection("warns").document(
#         str(member.id)).collection("history").document(str(key))
#     if history_ref.get().exists:
#         reason = history_ref.get().to_dict()["reason"]
#         date = datetime.fromtimestamp(
#             history_ref.get().to_dict()['date'].timestamp()).strftime('%d/%m/%Y, %H:%M:%S')
#         points = history_ref.get().to_dict(
#         )["new_points"] - history_ref.get().to_dict()["old_points"]

#         embed = discord.Embed(
#             description=f"**ID:** {key}\n**Data:** {date}\n**Powód kary:** {reason}\n**Punktacja:** {points}", type="article")
#         embed.set_author(
#             name=f"Usunięcie warna użytkownikowi {member.name}", icon_url=member.avatar.url)

#         btn_confirm = Button(
#             label="Confirm", style=discord.ButtonStyle.green, emoji="✔️")
#         btn_cancel = Button(
#             label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")

#         async def btn_confirm_callback(interaction):
#             history_ref.delete()
#             embed = discord.Embed(
#                 description=f"Pomyślnie usunięto warna użytkownika {member.name}", color=discord.Colour.green())
#             embed.set_author(
#                 name=f"Usunięcie warna użytkownika {member.name}", icon_url=member.avatar.url)
#             await interaction.response.edit_message(embed=embed, view=None)

#         async def btn_cancel_callback(interaction):
#             await interaction.response.edit_message(
#                 content="canceled", view=None, embed=None)

#         btn_confirm.callback = btn_confirm_callback
#         btn_cancel.callback = btn_cancel_callback

#         view = View()
#         view.add_item(btn_confirm)
#         view.add_item(btn_cancel)

#         await interaction.response.send_message(view=view, embed=embed)
#     else:
#         embed = discord.Embed(
#             description="Podany użytkownik nie posiada warna o takim ID", color=discord.Colour.red())
#         embed.set_author(
#             name=f"Usunięcie warna użytkownikowi {member.name}", icon_url=member.avatar.url)
#         await interaction.response.send_message(embed=embed)



# Run bot
client.run(discordToken)

# Get member
try:
    cursor.execute("SELECT * FROM members WHERE voice_join_time != 'NULL'")
except Error as e:
    logger.error(f"{e}")
query_result = cursor.fetchall()

# Debug all members on voice
if debugMode: logger.debug(f"members on voice | {query_result}")

for member in query_result:
    seconds_on_voice = (datetime.now() - member["voice_join_time"]).seconds

    try:
        cursor.execute(f"UPDATE members SET voice_join_time = NULL WHERE id = %s", (member["id"],))
    except Error as e:
        logger.error(f"{e}")
    else:
        mysqldb.commit()

    # Set month and year
    month = datetime.now().month
    year = datetime.now().year
    name = f"top_for_{month}_{year}"

    try:
        cursor.execute(f"SELECT * FROM {name} WHERE member_id = %s", (member["id"],))
    except Error as e:
        logger.error(f"{e}")
    top_for_row = cursor.fetchone()

    try:
        cursor.execute(f"UPDATE {name} SET voice_time = %s WHERE member_id = %s", (top_for_row["voice_time"] + seconds_on_voice, member["id"]))
    except Error as e:
        logger.error(f"{e}")
    else:
        mysqldb.commit()

# Close database connection
mysqldb.close()
