from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import db, credentials
from google.cloud.firestore_v1.base_query import FieldFilter
import firebase_admin
import discord
from datetime import datetime
import math
import random
from pprint import pprint
from operator import itemgetter
from discord.utils import get
from discord import EventStatus

import json
from discord.ui import Select, View, TextInput
from discord.ext import commands
from discord.ui import Button
import discord.utils
from discord.utils import get
from discord import CategoryChannel, app_commands
from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin
import discord
from discord.ext.commands import has_permissions
from datetime import datetime

import json
from discord.ui import Select, View
from discord.ext import commands, tasks
from discord.ui import Button
from discord import app_commands

from datetime import datetime

import os

# Firebase setup
cred = credentials.Certificate(".serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

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

# Code for debug
from loguru import logger

def error_handler(interaction, error):
    db.collection("errors").document().set({
        "commandName": interaction.command.name,
        "error": str(error),
        "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    })

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
        logger.warning(f"Debug mode is on, remember about it")
        logger.info(f"We have logged in as {self.user}")
        logger.info(f"Servers:")
        for idx, guild in enumerate(self.guilds):
            logger.info(f"{idx+1}. {guild.name}({guild.id})")
            # start_xp = 1000
            # sum = start_xp
            # idx = 1
            # for role in guild.roles:
            #     if "Poziom" in role.name:
            #         await role.edit(hoist=True)
            #         print(role)
            #         print(f"{role.name} ({role.id}) xp {start_xp}")
            #         start_xp = math.floor(start_xp)
            #         level_ref = db.collection("levels").document()
            #         level_ref.set({
            #             "role_id": role.id,
            #             "idx": idx,
            #             "required_points": sum
            #         })
            #         start_xp = start_xp * 1.10
            #         idx += 1
            #         sum += start_xp

        # Houses functionality
        channelID = config["statics"]["housesFunctioniality"]["channelID"]
        messageID = config["statics"]["housesFunctioniality"]["messageID"]
        redRoleID = config["statics"]["housesFunctioniality"]["roles"]["redRoleID"]
        greenRoleID = config["statics"]["housesFunctioniality"]["roles"]["greenRoleID"]
        yellowRoleID = config["statics"]["housesFunctioniality"]["roles"]["yellowRoleID"]

        # await self.get_channel(int(channelID)).purge()

        red_embed = discord.Embed(
            title="Czerwony Dom",
            color=discord.Color.from_rgb(213, 222, 245),
        )
        red_embed.set_image(url="https://cdn.discordapp.com/attachments/1207776901280833558/1253348469129744394/3ae3eaaa34d9e094ab0d7a085f29d8e5.jpg?ex=66758739&is=667435b9&hm=b4a6c875a08fcb39fcd44c486c8f127f9568b5d3807344012ff08ed2f08d57b6&")
        red_embed.add_field(name="Opis", value=f"{bulletID}Czerwony Dom jest miejscem pełnym energii, pasji i odwagi. To grupa, która ceni sobie ryzyko, działanie i determinację. Wszyscy członkowie Czerwonego Domu są jak płomień – nie boją się wyzwań, a ich entuzjazm jest zaraźliwy. To miejsce, gdzie każda osoba jest gotowa walczyć za swoje przekonania i nigdy się nie poddaje.")
        red_embed.add_field(name="Cechy charakteru", value=f"{emptyID}{bulletID}**Odważni**: Nigdy nie unikają trudnych sytuacji, stawiając czoła każdemu wyzwaniu.\n{emptyID}{bulletID}**Pasjonaci**: Ich działania są napędzane silnymi emocjami i głęboką pasją.\n{emptyID}{bulletID}**Liderzy**: Naturalnie przewodzą innym, motywując i inspirując swoim przykładem.\n{emptyID}{bulletID}**Zdeterminowani**: Nie zrażają się porażkami i zawsze dążą do osiągnięcia celu.")
        green_embed = discord.Embed(
            title="Zielony Dom",
            color=discord.Color.from_rgb(213, 222, 245),
        )
        green_embed.set_image(url="https://cdn.discordapp.com/attachments/1207776901280833558/1253350203772375170/green.jpg?ex=667588d6&is=66743756&hm=ab4ff4db05e28885a0fb8424cf4124d4c44be4c6c32d303509981a09e1bdb5aa&")
        green_embed.add_field(name="Opis", value=f"{bulletID}Zielony Dom to oaza spokoju, harmonii i zrozumienia natury. Członkowie tego domu są zrównoważeni, troskliwi i mądrzy. Cenią sobie równowagę między pracą a odpoczynkiem, oraz głęboką więź z naturą. Wspólnota w Zielonym Domu jest silna, oparta na wzajemnym wsparciu i zrozumieniu.")
        green_embed.add_field(name="Cechy charakteru", value=f"{emptyID}{bulletID}**Spokojni**: Zachowują spokój i opanowanie nawet w trudnych sytuacjach.\n{emptyID}{bulletID}**Empatyczni**: Z łatwością rozumieją i wspierają innych, tworząc silne więzi.\n{emptyID}{bulletID}**Mądrzy**: Kierują się logiką i doświadczeniem, podejmując przemyślane decyzje.\n{emptyID}{bulletID}**Zrównoważeni**: Dbają o harmonię w swoim życiu i relacjach z innymi.")
        yellow_embed = discord.Embed(
            title="Żółty Dom",
            color=discord.Color.from_rgb(213, 222, 245),
        )
        yellow_embed.set_image(url="https://cdn.discordapp.com/attachments/1207776901280833558/1253350212798382171/yellow.jpg?ex=667588d8&is=66743758&hm=79128d00a81a99c586cef6ae970992b99fdc787c52bc475315123738b9588dcf&")
        yellow_embed.add_field(name="Opis", value=f"{bulletID}Żółty Dom jest symbolem radości, optymizmu i kreatywności. To miejsce pełne życia, gdzie każda osoba czuje się wolna, aby wyrazić siebie. Członkowie Żółtego Domu są pełni pomysłów, zawsze gotowi do zabawy i odkrywania nowych rzeczy. Ich entuzjazm i pozytywne podejście do życia sprawiają, że są duszą towarzystwa.")
        yellow_embed.add_field(name="Cechy charakteru", value=f"{emptyID}{bulletID}**Optymistyczni**: Zawsze widzą jasną stronę życia i potrafią znaleźć pozytywy w każdej sytuacji.\n{emptyID}{bulletID}**Kreatywni**: Mają mnóstwo pomysłów i lubią eksperymentować, tworząc nowe rozwiązania.\n{emptyID}{bulletID}**Towarzyscy**: Uwielbiają przebywać wśród ludzi, dzielić się radością i energią.\n{emptyID}{bulletID}**Entuzjastyczni**: Ich zapał jest zaraźliwy, potrafią zachęcić innych do działania i zabawy.")
        main_embed = discord.Embed(
            title="Wybierz dom, który najbardziej pasuje do twojego charakteru",
            color=discord.Color.from_rgb(213, 222, 245)
        )

        btn_red = Button(
            label="Czerwony", emoji="🔴"
        )
        btn_green = Button(
            label="Zielony", emoji="🟢"
        )
        btn_yellow = Button(
            label="Żółty", emoji="🟡"
        )
        async def btn_red_callback(interaction: discord.Interaction):
            await interaction.user.remove_roles(get(guild.roles, id=greenRoleID))
            await interaction.user.remove_roles(get(guild.roles, id=yellowRoleID))
            await interaction.user.add_roles(get(guild.roles, id=redRoleID))
            await interaction.response.send_message("Pomyślnie wybrałeś czerwony dom, przynależność do innego z domów została usunięta!", ephemeral=True)

        async def btn_green_callback(interaction: discord.Interaction):
            await interaction.user.add_roles(get(guild.roles, id=greenRoleID))
            await interaction.user.remove_roles(get(guild.roles, id=yellowRoleID))
            await interaction.user.remove_roles(get(guild.roles, id=redRoleID))
            await interaction.response.send_message("Pomyślnie wybrałeś zielony dom, przynależność do innego z domów została usunięta!", ephemeral=True)

        async def btn_yellow_callback(interaction: discord.Interaction):
            await interaction.user.remove_roles(get(guild.roles, id=greenRoleID))
            await interaction.user.add_roles(get(guild.roles, id=yellowRoleID))
            await interaction.user.remove_roles(get(guild.roles, id=redRoleID))
            await interaction.response.send_message("Pomyślnie wybrałeś żółty dom, przynależność do innego z domów została usunięta!", ephemeral=True)

        btn_red.callback = btn_red_callback
        btn_green.callback = btn_green_callback
        btn_yellow.callback = btn_yellow_callback

        view = View()
        view.add_item(btn_red)
        view.add_item(btn_green)
        view.add_item(btn_yellow)

        # await self.get_channel(int(channelID)).send(embeds=[red_embed, green_embed, yellow_embed, main_embed], view=view)

        self.update_houses_channels_name.start()

    @tasks.loop(seconds=5.0)
    async def update_houses_channels_name(self):
        houses_ref = db.collection("houses")
        # print(f"{self.application.name}(Client) Loop: Command 'update_houses_channels_name' was executed by loop {self.index_of_update_houses_channels_name_loop} times")
        self.index_of_update_houses_channels_name_loop += 1
        await client.get_channel(1275531576649973791).edit(name=f"🔴│{houses_ref.document('red').get().to_dict()['points']}")
        await client.get_channel(1275531489211056161).edit(name=f"🔵│{houses_ref.document('green').get().to_dict()['points']}")
        await client.get_channel(1275531534828437574).edit(name=f"🟢│{houses_ref.document('yellow').get().to_dict()['points']}")

        # embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
        # embed.add_field(name="**<:education:1274147113353089064> Gratulacje, udało Ci się zdobyć nowy poziom!**", value=f"{emptyID}{bulletID}`{new_role.name}`")
        # embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
        # embed.set_author(name=f"Nowy poziom", icon_url=message.author.avatar.url)

    async def on_member_join(self, member: discord.Member):
        # Create embed
        embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23), description=f"<:channelred:1275856145847681055> **Witaj w Alorze wędrowcze. Nazywam się Eliora, jestem opiekunką ognia. Troszczę się o płomień i troszczę się o Ciebie.\n\n<:addred:1275861013606174730> Pamiętaj, by wybrać swą ścieżkę na <#1253278302039179374>. Kieruj się tym co w Tobie drzemie.**")
        embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")

        # Send dm to member
        await member.create_dm()
        await member.dm_channel.send(embed=embed)

    async def on_member_update(self, before, after):
        # Debug before
        logger.debug(f"before | {before.roles}")

        # Check if member has house role
        for role in before.roles:
            if role.name in ["Odwaga", "Empatia", "Równowaga"]:
                return

        # Debug after
        logger.debug(f"after | {after.roles}")

        for role in after.roles:
            if role.name in ["Odwaga", "Empatia", "Równowaga"]:
                # Ref to firebase members collection and member doc
                members_col = db.collection("members")
                member_query = db.collection("members").where(filter=FieldFilter("member_id", "==", after.id))

                # Stop if message doc exist
                if len(member_query.get()) == 1: 
                    member_doc = member_query.get()[0]
                    if member_doc.to_dict()["send"] == True:
                        return
                    
                # Create embed
                embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23), description=f"<:channelred:1275856145847681055> **Widzę że już wybrałeś swoją ścieżke\n\nNastępnie możesz udać się na <#1276250999513808968>, gdzie będziesz w stanie dobrać sobie dodatkowe role.\nKanał <#1275864080124739624> pozwoli Ci na wybór koloru.\n\n<:addred:1275861013606174730> Gdy skończysz z personalizacją, na kanale <#1271608578503086204> możesz powiedzieć nam kim jesteś.\nNaszym centrum życia jest <#1271608659415138335>, gdzie możesz przywitać się z innymi i rozpocząć swoją przygodę.\n\n<:emojired:1275843612566880309> Żegnaj i kieruj się płomieniem, {after.mention}.**")
                embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")

                # Send dm to member
                await after.create_dm()
                await after.dm_channel.send(embed=embed)

                members_col.document(member_doc.id).update({
                    "send": True
                })

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

        # Ref to firebase members collection and member doc
        members_col = db.collection("members")
        member_query = db.collection("members").where(filter=FieldFilter("member_id", "==", message.author.id))
        
        if len(member_query.get()) == 1:
            # Get member doc from query
            member_doc = member_query.get()[0]

            # Calculate diff_sec
            diff_sec = (datetime.now() - datetime.strptime(member_doc.to_dict()["lastDate"], "%Y-%m-%d %H:%M:%S")).seconds

            # Debug diff_sec
            if debugMode == True: logger.debug(f"diff_sec | {diff_sec}")

            if diff_sec > config["serverConfig"]["messageDelay"]:
                logger.info(f"{message.author.name}({message.author.id}): Got {xpGain} xp")

                # Update xp
                members_col.document(member_doc.id).update({
                    "xp": member_doc.to_dict()["xp"] + xpGain,
                    "lastDate": datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                })

                # Debug display new doc
                if debugMode == True: logger.debug(f"display_new_doc | {members_col.document(member_doc.id).get().to_dict()}")

                # Get user xp
                user_xp = member_doc.to_dict()["xp"] + xpGain

                # Get levels, make list and sort it
                levels_list = sorted((level.to_dict() for level in db.collection("levels").get()), key=itemgetter("idx"))

                # Find the lowest
                lowest = max((level for level in levels_list if user_xp > level["required_points"]), key=itemgetter("idx"), default=None)

                # Debug lowest
                if debugMode == True: logger.debug(f"lowest | {lowest}")
                
                # Add new role and remove old one
                temp = 0
                if lowest:
                    new_role = get(message.author.guild.roles, id=lowest["role_id"])   
                    for author_role in message.author.roles:
                        if "Poziom" in author_role.name:
                            temp = 1
                            if author_role.id != lowest["role_id"]:

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
                logger.info(f"{message.author.name}({message.author.id}): You need to wait {config["serverConfig"]["messageDelay"]-diff_sec} sec")
        else:
            logger.warning(f"New member was added to database! ({message.author})")
            members_col.document().set(
                {
                    "send": False,
                    "member_id": message.author.id,
                    "xp": xpGain,
                    "lastDate": datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            logger.info(f"{message.author.name}({message.author.id}): Got {xpGain} xp")
            
        # Set month and year
        month = datetime.now().month
        year = datetime.now().year

        # Ref to firebase members collection and member doc
        topMonths_col = db.collection("topMonths").document(f"{month}.{year}").collection("members")
        topMonths_query = topMonths_col.where(filter=FieldFilter("member_id", "==", message.author.id))
        
        if len(topMonths_query.get()) == 1:
            # Get member doc from query
            member_doc = topMonths_query.get()[0]

            logger.info(f"{message.author.name}({message.author.id}): Got 1 message in month {month}.{year}")

            # Update xp
            topMonths_col.document(member_doc.id).update({
                "messages_count": member_doc.to_dict()["messages_count"] + 1,
            })

            # Debug display new doc
            if debugMode == True: logger.debug(f"display_new_doc | {topMonths_col.document(member_doc.id).get().to_dict()}")
        else:
            logger.warning(f"New member was added to topMonths database! ({message.author})")
            topMonths_col.document().set(
                {
                    "member_id": message.author.id,
                    "messages_count": 1,
                }
            )
            logger.info(f"{message.author.name}({message.author.id}): Got 1 message in month {month}.{year}")

client = aclient()
tree = app_commands.CommandTree(client)

@tree.command(name="topka", guild=discord.Object(id=aloraID), description="Sprawdź topke naszych użytkowników!")
async def self(interaction: discord.Interaction):
    # Set embed
    embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
    embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
    embed.set_author(name=f"Topka użytkowników serwera {interaction.user.guild.name}", icon_url=interaction.user.guild.icon.url)

    # Sort all members
    members_list = sorted((member.to_dict() for member in db.collection("members").get()), key=itemgetter("xp"), reverse=True)

    # Debug members_list
    if debugMode == True: logger.debug(f"members_list | {members_list}")

    personal_rank = None
    top_members = ""
    for idx, member in enumerate(members_list):
        # Debug idx member
        if debugMode == True: logger.debug(f"{idx} {member}")

        # Add new member to ranking
        top_members += f"\n{emptyID}{bulletID}{idx+1}. `{interaction.user.guild.get_member(int(member["member_id"])).name}`: {member["xp"]} XP"

        # Check if member is an author of interaction
        if member["member_id"] == interaction.user.id: personal_rank = idx

    # Ref to firebase members collection and member doc
    member_query = db.collection("members").where(filter=FieldFilter("member_id", "==", interaction.user.id))
        
    # Set personal variables
    if personal_rank != None and len(member_query.get()) == 1:
        personal_xp = member_query.get()[0].to_dict()["xp"]

    # Add fields to embed
    embed.add_field(name=f"<:emojired:1275843612566880309> **Personalny ranking**", value=f"{emptyID}{bulletID}Przez cały swój pobyt na serwerze \n{emptyID}{emptyID}uzyskałeś `{personal_xp} xp` co usytuowało Cię na `{personal_rank+1}` miejscu", inline=False)
    embed.add_field(name=f"<:forumred:1275854320591704156> **Ranking 1-10**", value=top_members, inline=False)

    await interaction.response.send_message(embed=embed)

@tree.command(name="topka_miesieczna", guild=discord.Object(id=aloraID), description="Sprawdź topke naszych użytkowników!")
async def self(interaction: discord.Interaction):
    # Set month and year
    month = datetime.now().month
    year = datetime.now().year

    # Ref to firebase members collection and member doc
    topMonths_col = db.collection("topMonths").document(f"{month}.{year}").collection("members")

    # Set embed
    embed = discord.Embed(color=discord.Colour.from_rgb(212, 83, 23))
    embed.set_footer(text="W razie jakichkolwiek błędów proszę zgłosić to do administracji lub wysłać ticket")
    embed.set_author(name=f"Topka użytkowników serwera {interaction.user.guild.name} na miesiac {month}.{year}", icon_url=interaction.user.guild.icon.url)

    # Sort all members
    members_list = sorted((member.to_dict() for member in topMonths_col.get()), key=itemgetter("messages_count"), reverse=True)

    # Debug members_list
    if debugMode == True: logger.debug(f"members_list | {members_list}")

    personal_rank = None
    top_members = ""
    for idx, member in enumerate(members_list):
        # Debug idx member
        if debugMode == True: logger.debug(f"{idx} {member}")

        # Add new member to ranking
        top_members += f"\n{emptyID}{bulletID}{idx+1}. `{interaction.user.guild.get_member(int(member["member_id"])).name}`: {member["messages_count"]} wiadomosci"

        # Check if member is an author of interaction
        if member["member_id"] == interaction.user.id: personal_rank = idx

    # Ref to firebase members collection and member doc
    member_query = topMonths_col.where(filter=FieldFilter("member_id", "==", interaction.user.id))
        
    # Set personal variables
    if personal_rank != None and len(member_query.get()) == 1:
        # Debug member_query.get()[0].to_dict()
        if  debugMode == True: logger.debug(f"{member_query.get()[0].to_dict()}")

        messages_count = member_query.get()[0].to_dict()["messages_count"]

        # Add fields to embed
        embed.add_field(name=f"<:emojired:1275843612566880309> **Personalny ranking**", value=f"{emptyID}{bulletID}Podczas aktualnego miesiąca udało Ci się wysłać `{messages_count} wiadomości` co usytuowało Cię na `{personal_rank+1}` miejscu", inline=False)
        embed.add_field(name=f"<:forumred:1275854320591704156> **Ranking 1-10**", value=top_members, inline=False)

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

    # Ref to firebase members collection and member doc
    member_query = db.collection("members").where(filter=FieldFilter("member_id", "==", interaction.user.id))
        
    # Set personal variables
    if len(member_query.get()) == 1:
        member_doc = member_query.get()[0]

    # Pobranie danych użytkownika tylko raz, zamiast wielokrotnych zapytań
    user_xp = member_doc.to_dict().get("xp", 0)

    # Pobranie poziomów, przekształcenie na listę i posortowanie
    levels_list = sorted((level.to_dict() for level in db.collection("levels").get()), key=itemgetter("idx"))

    # Znalezienie aktualnego i następnego poziomu
    current_level = None
    next_level = None

    if level_role == None:
        next_level = levels_list[0]
    else:
        for i, level in enumerate(levels_list):
            if level_role and level["role_id"] == level_role.id:
                current_level = level
                # Sprawdzenie, czy istnieje następny poziom
                if i + 1 < len(levels_list):
                    next_level = levels_list[i + 1]
                break

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
