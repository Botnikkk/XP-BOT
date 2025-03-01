import asyncio
import random
import sqlite3
from itertools import cycle
import pickle as p

import discord
from discord.ext import commands, tasks
from discord.ext.commands import MissingPermissions

from dotenv import load_dotenv
import os


#<------------------------------------------------------------------ STARTUP BOT SETUP ------------------------------------------------------------------>

#setting prefix, removinb default help command, setting embed colour
intents = discord.Intents().all()
bot = commands.Bot(command_prefix=["n?" , "N?"],intents=intents,)
bot.remove_command('help')
embed_colour = 0xb8d4b4

#cycling bio status
status = cycle(['n?help', 'n?h'])
@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))

#building assets
servers = {}
def get_humans(context):
    human_members =[]
    for user in list(context.guild.members):
        if user.bot:
            continue
        else:
            human_members.append(user.id)
    return human_members

async def role_assign(context, server, mention=None):
    if mention is None :
        mention = context.author
    asset_file = open("assets", "rb+")
    assets = p.load(asset_file)
    level_roles, rank_roles = assets[server]['level_roles'], assets[server]['rank_roles']

    conn = sqlite3.connect('user_level_data.sqlite')
    cur = conn.cursor()
    cur.execute(f'SELECT rank, level FROM {server} WHERE user_id = ?',(str(mention.id), ))
    data = cur.fetchall()[0]
    cur.close()
    rank,level = data[0],data[1]

    user_roles = mention.roles
    total_roles = []
    for i in user_roles :
        total_roles.append(i.id)

    max_level = None
    if level_roles != None :

        myKeys = list(level_roles.keys())
        newKeys = []
        for i in myKeys :
            newKeys.append(int(i))
        myKeys = newKeys
        myKeys.sort()
        newKeys = []
        for i in myKeys :
            newKeys.append(str(i))
        myKeys = newKeys
        level_roles = {i: level_roles[i] for i in myKeys}

        for i in level_roles :
            if level >= int(i) :
                max_level = i

    if rank_roles != None :

        myKeys = list(rank_roles.keys())
        newKeys = []
        for i in myKeys :
            newKeys.append(int(i))
        myKeys = newKeys
        myKeys.sort()
        newKeys = []
        for i in myKeys :
            newKeys.append(str(i))
        myKeys = newKeys
        rank_roles = {i: rank_roles[i] for i in myKeys}
        rank_role_list = []
        for i in rank_roles :
        
            if rank == int(i) :
                role = context.guild.get_role(int(rank_roles[i]))
                conn = sqlite3.connect('user_level_data.sqlite')
                cur = conn.cursor()
                cur.execute(f'UPDATE {server} SET rank_role = {rank_roles[i]} WHERE user_id= ?',(str(mention.id), ))
                if max_level is not None :
                    cur.execute(f'UPDATE {server} SET awarded_role = {level_roles[max_level]} WHERE user_id= ?',(str(mention.id), ))
                conn.commit()
                cur.close()
                await mention.add_roles(role)
            else :
                if i in total_roles :
                    rank_role_list.append(context.guild.get_role(int(rank_roles[i])))
        await mention.remove_roles(*rank_role_list)
    if max_level is not None :
        roles = list(level_roles.values())

        role_list = []
        for i in roles :
            if i in total_roles and i != level_roles[max_level] :
                role_list.append(context.guild.get_role(int(i)))

        role_add = context.guild.get_role(int(level_roles[max_level]))
        await mention.add_roles(role_add)
        await mention.remove_roles(*role_list)

async def check_ranks(server) :
    conn = sqlite3.connect('user_level_data.sqlite')
    cur = conn.cursor()
    rank_list = []
    rank_num = 0
    for rank_extract in cur.execute(f'SELECT xp, user_id from {server} ORDER BY xp'):
        
        rank_list.append(rank_extract)
        rank_num = rank_num + 1
    rank_list.sort(reverse=True)
    for i in range(rank_num):
        user_id = rank_list[i][1]
        new_rank = i + 1
        cur.execute(f'UPDATE {server} SET rank = {new_rank} WHERE user_id = ? ', (str(user_id), ))
    conn.commit()
    cur.close()


#updating server lists
@tasks.loop(seconds=2)
async def update_servers() :
    global servers
    asset_file = open("assets", "ab+")
    asset_file.seek(0)
    assets = p.load(asset_file)
    asset_file.close()
    for guild in bot.guilds:
        name = str(guild.name)
        renamed = ""
        for i in name : 
            if i.isalpha() :
                renamed += i
        servers.update({name : renamed})
        try :
            assets[renamed]
        except :
            assets.update({renamed : {"spam" : None, "No_xp" : None, "level_up" : None, "level_roles" : None, "rank_roles" : None}})
    asset_file = open("assets", "wb+")
    p.dump(assets, asset_file)
    asset_file.close()

    conn = sqlite3.connect('user_level_data.sqlite')
    cur = conn.cursor()
    for i in servers :
        server = servers[i]
        try :
            cur.execute(f'CREATE TABLE {server} (rank INTEGER, user_id STRING, level INTEGER, xp INTEGER, awarded_role INTEGER, rank_role INTEGER)')
        except :
            continue
    conn.commit()
    cur.close()

#startup events initiation
@bot.event
async def on_ready():
    change_status.start()
    update_servers.start()

#<------------------------------------------------------------------ STARTUP BOT SETUP ------------------------------------------------------------------>










#<------------------------------------------------------------------ ON MESSAGE SETUP ------------------------------------------------------------------->


@bot.event
async def on_message(context):
    server = servers[context.guild.name]
    human_members = get_humans(context)
    asset_file = open("assets", "rb")
    assets = p.load(asset_file)
    if context.author.id in human_members  :
        no_xp = False
        for i in context.author.roles :
            if  assets[server]['No_xp'] == i.id :
                no_xp = True

        if int(context.channel.id) == assets[server]["spam"] or no_xp:

            context.content = context.content.lower()
            await bot.process_commands(context)
            return

        else:
        
            conn = sqlite3.connect('user_level_data.sqlite', timeout=2)
            cur = conn.cursor()
            cur.execute(f'SELECT xp, level FROM {server} WHERE user_id = ?',(str(context.author.id), ))
            data = cur.fetchall()
            cur.close()

            if context.author.id in human_members:
                if context.content.startswith("n?") or context.content.startswith("N?"):
                    context.content = context.content.lower()
                    await bot.process_commands(context)

                else:
                    chance = random.randint(1,3)
                    conn = sqlite3.connect('user_level_data.sqlite', timeout=2)
                    cur = conn.cursor()

                    if data == []:
                        user=str(context.author.id)

                        cur.execute(f'INSERT INTO {server} (rank, user_id, level, xp, awarded_role, rank_role) VALUES (0, {user}, 1, 1, 0, 0)')
                        conn.commit()
                        cur.close()


                    if data != [] and chance == 2 :
                        data = data[0]
                        row, level_exp_upgrade = data[0], data[1]
                        xp_upgrade = random.randint(int(level_exp_upgrade)*5, int(level_exp_upgrade)*10)
                        new_level = int(int(int(row))**(1 / 4))

                        cur.execute(f'SELECT level FROM {server} WHERE user_id = ?',(str(context.author.id), ))
                        level = cur.fetchone()
                        cur.execute(f'UPDATE {server} SET xp = xp + {xp_upgrade} WHERE user_id = ? ',(str(context.author.id), ))
                        cur.execute(f'UPDATE {server} SET level = {new_level} WHERE user_id = ? ',(str(context.author.id), ))
                        conn.commit()
                        cur.close()


                        if new_level > int(level[0]):

                            if assets[server]["level_up"] != None :
                                channel = bot.get_channel(assets[server]["level_up"])
                                await channel.send('Congratulations!! <@{user}> you have leveled up to **lvl.{level}**'.format(user=str(context.author.id),level=new_level))
                            else: 
                                await context.channel.send('Congratulations!! <@{user}> you have leveled up to **lvl.{level}**'.format(user=str(context.author.id),level=new_level))



#<------------------------------------------------------------------ ON MESSAGE SETUP ------------------------------------------------------------------->













#<------------------------------------------------------------------ COMMANDS SETUP --------------------------------------------------------------------->


# Help command
@bot.command(aliases=['h'], case_insensitive=True)
async def help(ctx, help = None):
    command_list = ["rank", "leaderboard","set_levelchannel", "set_rankrokle", "set_noxp", "set_levelrole", "set_spamchannel", "givexp", "resetxp", "setlevel"]
    embed = discord.Embed(title="🤖 Help has arrived",description="Hello! I am a bot made for managing Chat XP in various servers, developed and deployed by `botnikkk`",color=0xb8d4b4)
    if help is None :
            
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        embed.add_field(name="Prefix", value="My prefix is `n?`\n\n", inline=False)
        embed.add_field(name="General Commands",value="`n?rank/n?r` or `n?rank/n?r @user` \n `n?leaderboard/n?lb`",inline=False)
        embed.add_field(name="Roles related commands",value="`n?set_levelrole/n?slr @role level`\n `n?set_rankrole/n?srr @role rank`\n `n?set_noxp/n?snx @role`",inline=False)
        embed.add_field(name="channels related commands",value="`n?set_levelchannel/n?slc #channel`\n `n?set_spamchannel/n?ssc #channel`",inline=False)
        embed.add_field(name="Admin only commands",value="`n?givexp/n?gx @user ammount`\n `n?resetxp/n?rx @user`\n `n?setlevel/n?sl @user level`",inline=False)
    
    elif str(help).lower() not in command_list :
        embed = discord.Embed(
            title="🤖 Help has arrived",
            description="No such command was found ! please enter a valid command.\nMake sure to enter the full name of the command and not the short form.",
            color=embed_colour)

    else : 
        help = str(help).lower()
        if  help == command_list[0]  : 
            embed.add_field(name=f"Help with the {help} command command :", value="This command us used to check your or your friend's information in the server which inlcudes : Level, XP, Leaderboard Rank, Awarded rank and level roles.\nThe syntax for the command is : `n?rank/n?r` or `n?rank/n?r @user` ", inline=False)

        elif help == command_list[1] :
            embed.add_field(name=f"Help with the {help} command",value="This command is used to view the level of top 10 members of the server.\nThe syntax for the command is : `n?leaderboard/n?lb` ",inline=False)

        elif help == command_list[2] :
            embed.add_field(name=f"Help with the {help} command",value="This command is used to set the channel where the level up messages would be sent when a user achieves a new level.By default, it will be sent in the channel the user is chatting\nThe syntax for the command is : `n?set_levelchannel/n?slc #channel` ",inline=False)

        elif help == command_list[3] :
            embed.add_field(name=f"Help with the {help} command",value="This command is used to set a specific rank role for a specific rank on the leaderboard. A single rank can only have a single rank role.\nThe syntax for the command is : `n?set_rankrole/n?srr @role rank`",inline=False)

        elif help == command_list[4] :
            embed.add_field(name=f"Help with the {help} command",value="This command is used to set a specific role when which given to a user, blocks any XP being assigned to the user.\nThe syntax for the command is : `n?set_noxp/n?snx @role` ",inline=False)

        elif help == command_list[5] :
            embed.add_field(name=f"Help with the {help} command",value="This command is used to set a specific level role for a specific level. A single level can only have a single level role.\nThe syntax for the command is : `n?set_levelrole/n?slr @role level` ",inline=False)

        elif help == command_list[6] :
            embed.add_field(name=f"Help with the {help} command",value="This command is used to set a spam channel for the server, any user who texts in this channel will not recieve any xp. A single server can only have a single spam channel.\nThe syntax for the command is : `n?set_spamchannel/n?ssc #channel` ",inline=False)

        elif help == command_list[7] :
            embed.add_field(name=f"Help with the {help} command",value="This command is used to give a spicific ammount of xp to a user. This is a admin exclusive command.\nThe syntax for the command is : `n?givexp/n?gx @user ammount` ",inline=False)
            
        elif help == command_list[8] :
            embed.add_field(name=f"Help with the {help} command",value="This command is used to reser the XP progress of any user in the server.This is a admin exclusive command\nThe syntax for the command is : `n?resetxp/n?rx @user`",inline=False)
            
        elif help == command_list[9] :
            embed.add_field(name=f"Help with the {help} command",value="This command is used to set a specific level of a user, the XP of the user would be adjusted accordingly. This is a admin exclusive command.\nThe syntax for the command is :  `n?setlevel/n?sl @user level`",inline=False)
            
    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
    embed.set_image(url="https://c.tenor.com/5hKPyupKGWMAAAAC/robot-hello.gif")
    embed.set_footer(text="Nice to meet you!")
    await ctx.send(embed=embed)

# leaderboard command
@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command(aliases=['lb'], case_insensitive=True)
async def leaderboard(context):

    server = servers[context.message.guild.name]
    
    conn = sqlite3.connect('user_level_data.sqlite', timeout=10)
    cur = conn.cursor()
    cur.execute(f'SELECT user_id, level FROM {server} ORDER BY rank ASC')
    top_list = cur.fetchall()
    cur.close()

    await check_ranks(server)
    list_limit = 0
    leaderboard_content = " "

    for row in top_list:
        user , level = row[0] ,row[1]
        if list_limit < 11:  

                list_limit = list_limit + 1

                if list_limit == 1:
                    leaderboard_content += f"\n\n :first_place:  `lvl: {level}` - <@{user}>"

                if list_limit == 2:
                    leaderboard_content += f"\n :second_place:  `lvl: {level}` - <@{user}>"

                if list_limit == 3:
                    leaderboard_content += f"\n :third_place:  `lvl: {level}` - <@{user}>"

                elif list_limit > 3 and list_limit < 11:
                    leaderboard_content += f"\n :small_blue_diamond:  `lvl: {level}` - <@{user}>"

                elif list_limit > 11:
                    break
        else :
            break

    embed = discord.Embed(title="Leaderboard",description=leaderboard_content,colour=embed_colour)
    embed.set_image(url="https://c.tenor.com/JwxZhUN9MKgAAAAM/4%C2%BApr%C3%AAmio-bloxy-anual.gif")
    embed.set_footer(text=f"Top 10 members of {server}")
    await context.send(embed=embed)

@leaderboard.error
async def leaderboard_error(context, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(
            title=f"Slow it down bro!",
            description=f"Try again in {error.retry_after:.2f}s.",
            color=embed_colour)
        timeout = await context.send(embed=em)
        await asyncio.sleep(error.retry_after)
        await timeout.delete()


# Level_up channel command
@bot.command(aliases=['slc'], case_insensitive=True)
@commands.has_permissions(administrator=True)
async def set_levelchannel(context, channel: discord.TextChannel = None):

    server = servers[context.message.guild.name]
    if channel is None :
        await context.channel.send('Please mention a Channel')
    else :
        asset_file = open("assets","rb+")
        assets = p.load(asset_file)
        asset_file.close()

        assets[server]['level_up'] = channel.id
        asset_file = open("assets","wb+")
        assets = p.dump(assets,asset_file)
        asset_file.close()

        await context.channel.send(f'Level Up channel set to <#{channel.id}>')
@set_levelchannel.error
async def set_levelchannel_error(context, error):
    if isinstance(error, MissingPermissions):
        em = discord.Embed(title=f"Watch out !", description="This is a admin only command !",color=embed_colour)
        await context.send(embed=em)



# spam_up channel command
@bot.command(aliases=['ssc'], case_insensitive=True)
@commands.has_permissions(administrator=True)
async def set_spamchannel(context, channel: discord.TextChannel = None):

    server = servers[context.message.guild.name]
    if channel is None :
        await context.channel.send('Please mention a Channel')
    else :
        asset_file = open("assets","rb+")
        assets = p.load(asset_file)
        asset_file.close()
        assets[server]['spam'] = channel.id
        asset_file = open("assets","wb+")
        assets = p.dump(assets,asset_file)
        asset_file.close()

        await context.channel.send(f'spam channel set to <#{channel.id}>')
@set_spamchannel.error
async def set_spamchannel_error(context, error):
    if isinstance(error, MissingPermissions):
        em = discord.Embed(title=f"Watch out !", description="This is a admin only command !",color=embed_colour)
        await context.send(embed=em)



# Level_roles  command
@bot.command(aliases=['slr'], case_insensitive=True)
@commands.has_permissions(administrator=True)
async def set_levelrole(context, role : discord.Role = None , * , level = None):
    server = servers[context.message.guild.name]
    if role is None :
        await context.channel.send('Please mention a role')
    elif level is None :
        await context.channel.send('Please mention a level')
    elif 0 > int(level):
        await context.channel.send('Please mention a valid level')
    else :
        asset_file = open("assets","rb+")
        assets = p.load(asset_file)
        asset_file.close()
        try :
            assets[server]['level_roles'].update({level : role.id})
        except :
            assets[server]['level_roles'] = {level : role.id}
        asset_file = open("assets","wb+")
        p.dump(assets, asset_file)
        asset_file.close()

        await context.channel.send(f'<@&{role.id}> role added to level {level}')
@set_levelrole.error
async def set_levelrole_error(context, error):
    if isinstance(error, MissingPermissions):
        em = discord.Embed(title=f"Watch out !", description="This is a admin only command !",color=embed_colour)
        await context.send(embed=em)



# Rank_roles command
@bot.command(aliases=['srr'], case_insensitive=True)
@commands.has_permissions(administrator=True)
async def set_rankrole(context, role : discord.Role = None , * , rank = None):
    server = servers[context.message.guild.name]
    if role is None :
        await context.channel.send('Please mention a role')
    elif rank is None :
        await context.channel.send('Please mention a rank')
    elif 0 > int(rank) or int(rank) > 10:
        await context.channel.send('Please mention a rank between 1 and 10')
    else :
        asset_file = open("assets","rb+")
        assets = p.load(asset_file)
        asset_file.close()
        try :
            assets[server]['rank_roles'].update({rank : role.id})
        except :
            assets[server]['rank_roles'] = {rank : role.id}
        asset_file = open("assets","wb+")
        p.dump(assets, asset_file)
        asset_file.close()

        await context.channel.send(f'<@&{role.id}> role added to rank {rank}')
@set_rankrole.error
async def set_ranlrole_error(context, error):
    if isinstance(error, MissingPermissions):
        em = discord.Embed(title=f"Watch out !",description="This is a admin only command !",color=embed_colour)
        await context.send(embed=em)



# No_xp command
@bot.command(aliases=['snx'], case_insensitive=True)
@commands.has_permissions(administrator=True)
async def set_noxp(context, role : discord.Role = None):
    server = servers[context.message.guild.name]
    if role is None :
        await context.channel.send('Please mention a role')
    else :
        asset_file = open("assets","rb+")
        assets = p.load(asset_file)
        asset_file.close()
        assets[server]['No_xp'] = role.id
        asset_file = open("assets","wb+")
        p.dump(assets, asset_file)
        asset_file.close()

        await context.channel.send(f'<@&{role.id}> set as No XP role')
@set_noxp.error
async def set_noxp_error(context, error):
    if isinstance(error, MissingPermissions):
        em = discord.Embed(title=f"Watch out !",description="This is a admin only command !",color=embed_colour)
        await context.send(embed=em)


# Rank check command
@commands.cooldown(1, 20, commands.BucketType.user)
@bot.command(aliases=['r'], case_insensitive=True)
async def rank(context:commands.Context, user: discord.Member = None):
    server = servers[context.message.guild.name]

    def get_formatted_assets(user = context.author) :
        conn = sqlite3.connect('user_level_data.sqlite', timeout=60)
        cur = conn.cursor()
        cur.execute(f'SELECT xp, level, rank FROM {server} WHERE user_id = ?',(str(user.id), ))
        data = cur.fetchall()
        data = data[0]
        cur.close()

        xp, level, rank = int(data[0]), int(data[1]), int(data[2])

        xp_required = (level + 1)**4 - (level)**4
        xp = (xp) - (level**4)

        formated_xp = f"`{xp}/{xp_required}`"
        formated_level = f"`{level}`"
        formated_rank = f"`{rank}`"
        
        return [formated_xp, formated_level, formated_rank]

    if user is None :
        mention = context.author
    
    else :
        mention = user

    if mention.id in get_humans(context) :

        conn = sqlite3.connect('user_level_data.sqlite', timeout=30)
        cur = conn.cursor()
        cur.execute(f'SELECT xp FROM {server} WHERE user_id= ?',(str(mention.id), ))
        xp = cur.fetchall()
        cur.close()

        if xp == [] :
            
            await context.channel.send("You don't have a rank yet please chat a bit more to gain more xp !")

        else:
            await check_ranks(server)
            await role_assign(context,server,mention)

            conn = sqlite3.connect('user_level_data.sqlite', timeout=30)
            cur = conn.cursor()
            cur.execute(f'SELECT rank_role, awarded_role FROM {server} WHERE user_id= ?',(str(mention.id), ))
            data = cur.fetchall()[0]
            cur.close()

            rank_role , awarded_role = data[0], data[1]  

            if rank_role == 0 and awarded_role != 0 :
                rank_role, awarded_role =  '`No awarded rank role...yet!`', f"<@&{data[1]}>"

            elif awarded_role == 0 and rank_role != 0 :
                awarded_role, rank_role =  '`No awarded level role...yet!`', f"<@&{data[0]}>"
            
            elif rank_role != 0 and awarded_role != 0:
                rank_role , awarded_role = f"<@&{data[0]}>" , f"<@&{data[1]}>"

            else :
                rank_role , awarded_role = '`No awarded rank role...yet!`' ,'`No awarded level role...yet!`'
            
            total_award_ranks = f'{awarded_role}\n{rank_role}'

            data = get_formatted_assets(mention)
            xp , level ,rank = data[0], data[1], data[2]
            
            embed = discord.Embed(title=f"*Server Rank of -* {mention}" ,description="**Your server rank increases as you chat, increase your rank to get high reward roles and flex on your friends** <:2940coolpepe:988766350430322738> ",colour=embed_colour)

            embed.add_field(name="Rank", value=rank, inline=False)
            embed.add_field(name="Current level", value=level, inline=True)
            embed.add_field(name="xp", value=xp, inline=True)
            embed.add_field(name="Awarded role", value=total_award_ranks, inline=False)
            embed.set_author(name=mention, icon_url=mention.avatar)
            embed.set_thumbnail(url=mention.avatar)
            embed.set_image(url="https://i.imgur.com/cerqOld.gif")

            await context.send(embed=embed)

    else :
        await context.channel.send("Bots don't have levels stupid !")
@rank.error
async def rank_error(context, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title=f"Slow it down bro!",description=f"Try again in {error.retry_after:.2f}s.",color=embed_colour)
        timeout = await context.send(embed=em)
        await asyncio.sleep(error.retry_after)
        await timeout.delete()


# Set level command
@bot.command(aliases=['sl'], case_insensitive=True)
@commands.has_permissions(administrator=True)
async def setlevel(context, user: discord.Member = None, *, set_level = None):
    server = servers[context.message.guild.name]
    if user is None :
        await context.channel.send('Please mention a user')

    elif set_level is None :
        await context.channel.send('Please mention Level')

    else :

        if user.id in get_humans(context) :
            conn = sqlite3.connect('user_level_data.sqlite', timeout=20)
            cur = conn.cursor()
            cur.execute(f'SELECT xp FROM {server} WHERE user_id = ?', (str(user.id), ))
            xp = cur.fetchone()
            if xp == []:
                await context.channel.send(f'User <@{int(user.id)}> is not registered, you need to have texted atleast once in the server to register yourself!')

            else:
                new_xp = int(set_level)**4
                new_level = int(set_level)
                cur.execute(f'SELECT level FROM {server} WHERE user_id = ?',(str(user.id), ))
                level = cur.fetchone()
                cur.execute(f'UPDATE {server} SET xp = {new_xp}, level = {new_level} WHERE user_id = ? ',(str(user.id),))
                conn.commit()
                asset_file = open("assets", "rb")
                assets = p.load(asset_file)
                cur.close()

                if  new_level > int(level[0]) : 
                    if assets[server]["level_up"] != None :
                        channel = bot.get_channel(assets[server]["level_up"])
                        await channel.send(f'Congratulations!! <@{str(context.author.id)}> you have leveled up to **lvl.{new_level}**')
                    else: 
                        await context.channel.send(f'Congratulations!! <@{str(context.author.id)}> you have leveled up to **lvl.{new_level}**')
                await context.channel.send(f"Succsesfully set level of <@{user.id}> to {set_level} !")

        else :
            await context.channel.send("Can't set a bot's level !")
@setlevel.error
async def setlevel_error(context, error):
    if isinstance(error, MissingPermissions):
        em = discord.Embed(title=f"Watch out !",description="This is a admin only command !",color=embed_colour)
        await context.send(embed=em)


# Reset xp command
@bot.command(aliases=['rx'], case_insensitive=True)
@commands.has_permissions(administrator=True)
async def resetxp(context, user: discord.Member = None):
    server = servers[context.message.guild.name]    
    if user is None :
        await context.channel.send('Please mention a user')
    else :

        conn = sqlite3.connect('user_level_data.sqlite', timeout=20)
        cur = conn.cursor()
        cur.execute(f'SELECT xp FROM {server} WHERE user_id = ?', (str(user.id), ))
        xp = cur.fetchone()
        if user.id in get_humans(context):

            if xp == []:
                await context.channel.send(f'User <@{int(user.id)}> is not registered, you need to have texted atleast once in the server to register yourself !')

            else:
                cur.execute(f'DELETE FROM {server} WHERE user_id = ?',(str(user.id), ))
                conn.commit
                user=str(user.id)
                cur.execute(f'INSERT INTO {server} (rank, user_id, level, xp, awarded_role, rank_role) VALUES (0, {user}, 1, 1, 0, 0)')
                await context.channel.send(f'Succsefullly reseted xp info of user <@{user}>')
        else:
            await context.channel.send("Can't reset bot's xp")
        conn.commit()
        cur.close()
@resetxp.error
async def resetxp_error(context, error):
    if isinstance(error, MissingPermissions):
        em = discord.Embed(title=f"Watch out !",description="This is a admin only command !",color=embed_colour)
        await context.send(embed=em)


# Give_Xp Command
@bot.command(aliases=['gx'])
@commands.has_permissions(administrator=True)
async def givexp(context, user: discord.Member = None, *, xp_addition):
    server = servers[context.message.guild.name]
    if user is None :
        await context.channel.send('Please mention a user')

    else :

        if user.id in get_humans(context):
            conn = sqlite3.connect('user_level_data.sqlite', timeout=20)
            cur = conn.cursor()
            cur.execute(f'SELECT xp FROM {server} WHERE user_id = ?', (str(user.id), ))
            xp = cur.fetchone()
            if xp == []:

                await context.channel.send(f'User <@{int(user.id)}> is not registered, you need to have texted atleast once in the server to register yourself !')
            
            else:
                xp = int(xp[0])
                xp_addition = int(xp_addition)
                cur.execute(f'UPDATE {server} SET xp = xp + {xp_addition} WHERE user_id = ? ', (str(user.id), ))
                conn.commit()

                cur.execute(f'SELECT level FROM {server} WHERE user_id = ?',(str(user.id), ))

                level = cur.fetchone()[0]

                new_level = int((xp + xp_addition)**(1/4))

            
                cur.execute(f'UPDATE {server} SET level = {new_level} WHERE user_id = ? ', (str(user.id), ))

                asset_file = open("assets", "rb")
                assets = p.load(asset_file)
                if  new_level > int(level) : 
                    if assets[server]["level_up"] != None :
                        channel = bot.get_channel(assets[server]["level_up"])
                        await channel.send(f'Congratulations!! <@{str(context.author.id)}> you have leveled up to **lvl.{new_level}**')
                    else: 
                        await context.channel.send(f'Congratulations!! <@{str(context.author.id)}> you have leveled up to **lvl.{new_level}**')

                await context.channel.send(f'Added {xp_addition} xp to <@{user.id}> !')

            conn.commit()
            cur.close()
        else:
            await context.channel.send("Can't give xp to a bot")
@givexp.error
async def givexp_error(context, error):
    if isinstance(error, MissingPermissions):
        em = discord.Embed(title=f"Watch out !",description="This is a admin only command !",color=embed_colour)
        await context.send(embed=em)

#<------------------------------------------------------------------ COMMANDS SETUP --------------------------------------------------------------------->





0



#<------------------------------------------------------------------ RUNNING THE BOT -------------------------------------------------------------------->

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot.run(TOKEN)

#<------------------------------------------------------------------ RUNNING THE BOT -------------------------------------------------------------------->