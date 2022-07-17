import asyncio
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import random
import sqlite3
from flask import Flask
from threading import Thread
from discord.ext import tasks
from itertools import cycle
from discord.ext.commands import cooldown, BucketType
from discord.ext.commands import has_permissions, MissingPermissions

app = Flask('')


@app.route('/')
def main():
    return "Your Bot Is Ready"


def run():
    app.run(host="0.0.0.0", port=8000)


def keep_alive():
    server = Thread(target=run)
    server.start()


intents = discord.Intents().all()
load_dotenv()
bot = commands.Bot(
    command_prefix=["n?" , "N?"],
    intents=intents,
)
bot.remove_command('help')

status = cycle(['n?help', 'n?h'])


@bot.event
async def on_ready():
    print("My name is {0.user} and i am ready to go".format(bot))
    change_status.start()
    print("Your bot is ready")
    conn = sqlite3.connect('user_level_data.sqlite')
    cur = conn.cursor()
    try:
        cur.execute(
            'CREATE TABLE rankings (rank INTEGER, user_id STRING, level INTEGER, xp INTEGER, awarded_role INTEGER, rank_role INTEGER)'
        )
    except:
        print("database exists")
    conn.close()


@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))


@bot.command(aliases=['h'], case_insensitive=True)
async def help(ctx: commands.Context):

    embed = discord.Embed(
        title="🤖 Help has arrived",
        description=
        "Hello! I am a bot made for Imperial Japan, developed and deployed by Nikkk",
        color=0xFF5733)
    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
    embed.add_field(name="Prefix", value="My prefix is `n?`\n\n", inline=False)
    embed.add_field(name="Commands",
                    value="`n?rank` or `n?rank @user` \n `n?leaderboard`",
                    inline=False)
    embed.add_field(
        name="Admin only commands",
        value=
        "`n?givexp @user ammount`\n `n?resetxp @user`\n `n?setlevel @user level`",
        inline=False)
    embed.set_thumbnail(
        url=
        "https://cdn.discordapp.com/avatars/708412887915298910/2840c49ac54bf671deca31f77e14d993.webp?size=1024"
    )
    embed.set_image(url="https://c.tenor.com/5hKPyupKGWMAAAAC/robot-hello.gif")
    embed.set_footer(text="Nice to meet you!")
    await ctx.send(embed=embed)


@commands.cooldown(1, 30, commands.BucketType.user)
@bot.command(aliases=['lb'], case_insensitive=True)
async def leaderboard(ctx):

    conn = sqlite3.connect('user_level_data.sqlite', timeout=10)
    cur = conn.cursor()
    test = 'SELECT user_id, level from rankings ORDER BY rank ASC LIMIT 10'

    list_limit = 0
    mem_str = " "

    for row in cur.execute(test):
        list_limit = list_limit + 1
        if list_limit == 1:
            mem_str = mem_str + '\n\n' + ':first_place:  ' + '`lvl: {level}` - '.format(
                level=row[1]) + '<@{user}>'.format(user=str(row[0]))
        if list_limit == 2:
            mem_str = mem_str + '\n' + ':second_place:  ' + '`lvl: {level}` - '.format(
                level=row[1]) + '<@{user}>'.format(user=str(row[0]))
        if list_limit == 3:
            mem_str = mem_str + '\n' + ':third_place:  ' + '`lvl: {level}` - '.format(
                level=row[1]) + '<@{user}>'.format(user=str(row[0]))
        elif list_limit > 3 and list_limit < 11:
            mem_str = mem_str + '\n' + ':small_blue_diamond:  ' + '`lvl: {level}` - '.format(
                level=row[1]) + '<@{user}>'.format(user=str(row[0]))
        elif list_limit > 11:
            break
    conn.commit()
    cur.close()

    embed = discord.Embed(title="Leaderboard",
                          description=mem_str,
                          colour=0xFF5733)
    embed.set_image(
        url=
        "https://c.tenor.com/JwxZhUN9MKgAAAAM/4%C2%BApr%C3%AAmio-bloxy-anual.gif"
    )
    embed.set_footer(text="Top 10 members of the server")

    await ctx.send(embed=embed)


@leaderboard.error
async def leaderboard_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(
            title=f"Slow it down bro!",
            description=f"Try again in {error.retry_after:.2f}s.",
            color=0xFF5733)
        timeout = await ctx.send(embed=em)
        await asyncio.sleep(error.retry_after)
        await timeout.delete()


@commands.cooldown(1, 10, commands.BucketType.user)
@bot.command(aliases=['r'], case_insensitive=True)
async def rank(ctx:commands.Context, user: discord.Member = None):
  if user is None :
        conn = sqlite3.connect('user_level_data.sqlite', timeout=30)
        cur = conn.cursor()
        def get_formatted_xp():
            conn = sqlite3.connect('user_level_data.sqlite', timeout=60)
            cur = conn.cursor()
            cur.execute('SELECT xp FROM rankings WHERE user_id = ?',
                        (str(ctx.author.id), ))
            xp = cur.fetchone()
            cur.execute('SELECT level FROM rankings WHERE user_id = ?',
                        (str(ctx.author.id), ))
            level = cur.fetchone()
            xp_required = (int(level[0]) + 1)**4 - (int(level[0]))**4
            output = "`{xp}/{xp_required}`".format(xp=(int(xp[0]) - (int(level[0]))**4),
                                                   xp_required=xp_required)
            cur.close()
            return output
    
        def get_formatted_level():
            conn = sqlite3.connect('user_level_data.sqlite', timeout=60)
            cur = conn.cursor()
            cur.execute('SELECT level FROM rankings WHERE user_id = ?',
                        (str(ctx.author.id), ))
            level = cur.fetchone()
            output = "`{level}`".format(level=int(level[0]))
            cur.close()
            return output
    
        def get_formatted_rank():
            conn = sqlite3.connect('user_level_data.sqlite', timeout=60)
            cur = conn.cursor()
            cur.execute('SELECT rank FROM rankings WHERE user_id = ?',
                        (str(ctx.author.id), ))
            rank = cur.fetchone()
            output = "`{rank}`".format(rank=int(rank[0]))
            cur.close()
            return output
    
        cur.execute('SELECT awarded_role FROM rankings WHERE user_id= ?',
                    (str(ctx.author.id), ))
        awarded_role_rank = cur.fetchone()
        if awarded_role_rank is None :
          await ctx.channel.send("You don't have a rank yet please chat a bit more to gain more xp !")
        else :
            formatted_role_Rank = "<@&{awarded_role}>".format(
                awarded_role=awarded_role_rank[0])
            cur.execute('SELECT rank_role FROM rankings WHERE user_id= ?',
                        (str(ctx.author.id), ))
            rank_role = cur.fetchone()
            if int(rank_role[0]) == 0:
                awarded_rank_role = '`No awarded rank role...yet!`'
        
            else:
                awarded_rank_role = '<@&{rank_role}>'.format(
                    rank_role=str(rank_role[0]))
        
            total_award_ranks = '{level_role}\n{rank_role}'.format(
                level_role=formatted_role_Rank, rank_role=awarded_rank_role)
        
            xp_rank = get_formatted_xp()
            level_rank = get_formatted_level()
            rank_rank = get_formatted_rank()
            embed = discord.Embed(
                title="*Server Rank of -* " + str(ctx.author),
                description=
                "**Your server rank increases as you chat, increase your rank to get high reward roles and flex on your friends** <:2940coolpepe:988766350430322738> ",
                colour=0xFF5733)
            embed.add_field(name="Rank", value=rank_rank, inline=False)
            embed.add_field(name="Current level", value=level_rank, inline=True)
            embed.add_field(name="xp", value=xp_rank, inline=True)
            embed.add_field(name="Awarded role", value=total_award_ranks, inline=False)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_image(url="https://i.imgur.com/cerqOld.gif")
            await ctx.send(embed=embed)
  else : 
      human_memebers = []
      for bot_check in list(ctx.guild.members):
          if bot_check.bot:
                continue
          else:
                human_memebers.append(bot_check)
      if user in human_memebers :
        
        print("user mentioned")
        conn = sqlite3.connect('user_level_data.sqlite', timeout=30)
        cur = conn.cursor()
        def get_formatted_xp():
            conn = sqlite3.connect('user_level_data.sqlite', timeout=60)
            cur = conn.cursor()
            cur.execute('SELECT xp FROM rankings WHERE user_id = ?',
                        (str(user.id), ))
            xp = cur.fetchone()
            cur.execute('SELECT level FROM rankings WHERE user_id = ?',
                        (str(user.id), ))
            level = cur.fetchone()
            xp_required = (int(level[0]) + 1)**4 - (int(level[0]))**4
            output = "`{xp}/{xp_required}`".format(xp=(int(xp[0]) - (int(level[0]))**4),
                                                   xp_required=xp_required)
            cur.close()
            return output
    
        def get_formatted_level():
            conn = sqlite3.connect('user_level_data.sqlite', timeout=60)
            cur = conn.cursor()
            cur.execute('SELECT level FROM rankings WHERE user_id = ?',
                        (str(user.id), ))
            level = cur.fetchone()
            output = "`{level}`".format(level=int(level[0]))
            cur.close()
            return output
    
        def get_formatted_rank():
            conn = sqlite3.connect('user_level_data.sqlite', timeout=60)
            cur = conn.cursor()
            cur.execute('SELECT rank FROM rankings WHERE user_id = ?',
                        (str(user.id), ))
            rank = cur.fetchone()
            output = "`{rank}`".format(rank=int(rank[0]))
            cur.close()
            return output
    
        cur.execute('SELECT awarded_role FROM rankings WHERE user_id= ?',
                    (str(user.id), ))
        awarded_role_rank = cur.fetchone()
        if awarded_role_rank is None :
          await ctx.channel.send("The user doesn't have a rank yet please ask them to chat a bit more to gain more xp !")
        else :
            formatted_role_Rank = "<@&{awarded_role}>".format(
                awarded_role=awarded_role_rank[0])
            cur.execute('SELECT rank_role FROM rankings WHERE user_id= ?',
                        (str(user.id), ))
            rank_role = cur.fetchone()
            if int(rank_role[0]) == 0:
                awarded_rank_role = '`No awarded rank role...yet!`'
        
            else:
                awarded_rank_role = '<@&{rank_role}>'.format(
                    rank_role=str(rank_role[0]))
        
            total_award_ranks = '{level_role}\n{rank_role}'.format(
                level_role=formatted_role_Rank, rank_role=awarded_rank_role)
        
            xp_rank = get_formatted_xp()
            level_rank = get_formatted_level()
            rank_rank = get_formatted_rank()
            embed = discord.Embed(
                title="*Server Rank of -* " + str(user),
                description=
                "**Your server rank increases as you chat, increase your rank to get high reward roles and flex on your friends** <:2940coolpepe:988766350430322738> ",
                colour=0xFF5733)
            embed.add_field(name="Rank", value=rank_rank, inline=False)
            embed.add_field(name="Current level", value=level_rank, inline=True)
            embed.add_field(name="xp", value=xp_rank, inline=True)
            embed.add_field(name="Awarded role", value=total_award_ranks, inline=False)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_image(url="https://i.imgur.com/cerqOld.gif")
            await ctx.send(embed=embed)


      else :
        await ctx.channel.send("Bots don't have levels stupid !")
@rank.error
async def rank_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(
            title=f"Slow it down bro!",
            description=f"Try again in {error.retry_after:.2f}s.",
            color=0xFF5733)
        timeout = await ctx.send(embed=em)
        await asyncio.sleep(error.retry_after)
        await timeout.delete()
      

@bot.event
async def on_message(context):
  
    if int(context.channel.id) == 988711128106430484:
        await asyncio.sleep(2)
        context.content = context.content.lower()
        await bot.process_commands(context)
        return
    else:
        human_memebers = []
        for user in list(context.guild.members):
            if user.bot:
                continue
            else:
                human_memebers.append(user)
        conn = sqlite3.connect('user_level_data.sqlite', timeout=2)
        cur = conn.cursor()
        cur.execute('SELECT xp FROM rankings WHERE user_id = ?',
                    (str(context.author.id), ))
        row = cur.fetchone()
        cur.execute('SELECT level FROM rankings WHERE user_id = ?',
                    (str(context.author.id), ))
        level_exp_upgrade = cur.fetchone()
        if context.author in human_memebers:

            if context.content.startswith("n?") or context.content.startswith("N?"):
                context.content = context.content.lower()
                await bot.process_commands(context)
                print('commands')
            else:

                if row is None:
                    cur.execute('INSERT INTO rankings (rank, user_id, level, xp, awarded_role, rank_role) VALUES (0, {user}, 1, 1, 0, 0)'.format(user=str(context.author.id)))
                    role = context.guild.get_role(989839086036611092)
                    await context.author.add_roles(role)

                if row is not None:
                    xp_upgrade = random.randint(int(level_exp_upgrade[0])*5, int(level_exp_upgrade[0])*10)
                    new_level = int(int(int(row[0]))**(1 / 4))

                    cur.execute('SELECT level FROM rankings WHERE user_id = ?',
                                (str(context.author.id), ))
                    level = cur.fetchone()
                    cur.execute(
                        'UPDATE rankings SET xp = xp + {xp_upgrade} WHERE user_id = ? '
                        .format(xp_upgrade=xp_upgrade),
                        (str(context.author.id), ))
                    cur.execute(
                        'UPDATE rankings SET level = {new_level} WHERE user_id = ? '
                        .format(new_level=new_level),
                        (str(context.author.id), ))
                    if new_level > int(level[0]):
                        channel = bot.get_channel(988718132841562112)
                        await channel.send(
                            'Congratulations!! <@{user}> you have leveled up to **lvl.{level}**'
                            .format(user=str(context.author.id),
                                    level=new_level))

                    rank_list = []
                    rank_num = 0
                    for rank_extract in cur.execute('SELECT xp, user_id from rankings ORDER BY xp'):
                        
                        rank_list.append(rank_extract)
                        rank_num = rank_num + 1
                    rank_list.sort(reverse=True)
                    for i in range(rank_num):
                        user_id = rank_list[i][1]
                        new_rank = i + 1
                        cur.execute(
                            'UPDATE rankings SET rank = {new_rank} WHERE user_id = ? '
                            .format(new_rank=new_rank), (str(user_id), ))

                    level_list = [
                        989839086036611092, 988789087542607882,
                        988789558642638869, 988794780584669236,
                        988795209104097320, 988795128753827941,
                        988795479426998402, 988795479477325855,
                        988796013328359484, 988796151081869372,
                        988796343986298890
                    ]
                    cur.execute('SELECT level FROM rankings WHERE user_id = ?',
                                (str(context.author.id), ))
                    current_level = cur.fetchone()
                    for level_role in level_list:
                        if level_list.index(level_role) == 0:
                            if int(int(current_level[0]) / 10) == 0:
                                role = context.guild.get_role(level_role)
                                await context.author.add_roles(role)
                                cur.execute(
                                    'UPDATE rankings SET awarded_role = {new_awarded_role} WHERE user_id= ?'
                                    .format(new_awarded_role=level_role),
                                    (str(context.author.id), ))

                        if level_list.index(level_role) > 0:
                            if (int(level_list.index(level_role)))*10 <= int(current_level[0]) and (int(level_list.index(level_role)) + 1) * 10 > int(current_level[0]) :

                                role = context.guild.get_role(int(level_role))
                                await context.author.add_roles(role)
                                role = context.guild.get_role(
                                    989839086036611092)
                                await context.author.remove_roles(role)
                                cur.execute(
                                    'UPDATE rankings SET awarded_role = {new_awarded_role} WHERE user_id= ?'
                                    .format(new_awarded_role=level_role),
                                    (str(context.author.id), ))
                            else:
                                role = context.guild.get_role(level_role)
                                await context.author.remove_roles(role)
                    rank_role_list = [
                        991300695863083048, 991301125833756753,
                        991301308965457961, 991301900794351726]
                    cur.execute('SELECT rank FROM rankings WHERE user_id = ?',
                                (str(context.author.id), ))
                    current_rank = cur.fetchone()
                    for rank_role_check in rank_role_list:
                        if rank_role_list.index(rank_role_check) < 3:
                            if (int(rank_role_list.index(rank_role_check)) +
                                    1) == int(current_rank[0]):
                                role = context.guild.get_role(rank_role_check)
                                await context.author.add_roles(role)
                                cur.execute(
                                    'UPDATE rankings SET rank_role = {new_rank_role} WHERE user_id= ?'
                                    .format(new_rank_role=rank_role_check),
                                    (str(context.author.id), ))
                                print("samurai  role added")
                            else:
                                role = context.guild.get_role(rank_role_check)
                                await context.author.remove_roles(role)

                        elif rank_role_list.index(rank_role_check) == 3:
                            if 3 < int(current_rank[0]) <= 10:

                                role = context.guild.get_role(
                                    int(rank_role_check))
                                await context.author.add_roles(role)
                                cur.execute(
                                    'UPDATE rankings SET rank_role = {new_rank_role} WHERE user_id= ?'
                                    .format(new_rank_role=rank_role_check),
                                    (str(context.author.id), ))
                                print("ronin role added")
                            else:
                                role = context.guild.get_role(rank_role_check)
                                await context.author.remove_roles(role)
                        else:
                            role = context.guild.get_role(rank_role_check)
                            await context.author.remove_roles(role)

        conn.commit()
        cur.close()


@bot.command(aliases=['gx'])
@commands.has_permissions(administrator=True)
async def givexp(context, user: discord.Member = None, *, xp_addition):
  if user is None :
   print('Please mention a user')
  else :
        print("xp given {xp_add}".format(xp_add=xp_addition))
        human_memebers = []
        for bot_check in list(context.guild.members):
            if bot_check.bot:
                continue
            else:
                human_memebers.append(bot_check)
    
        conn = sqlite3.connect('user_level_data.sqlite', timeout=20)
        cur = conn.cursor()
        cur.execute('SELECT xp FROM rankings WHERE user_id = ?', (str(user.id), ))
        xp = cur.fetchone()
        print(user)
        if user in human_memebers:
            if xp is None:
                await context.channel.send('User <@{user_id}> is not registered, you need to have texted atleast once in the server to register yourself !'.format(user_id=int(user.id)))
            else:
                print('updating')
                cur.execute('UPDATE rankings SET xp = xp + {xp_addition} WHERE user_id = ? '.format(xp_addition=xp_addition), (str(user.id), ))
                new_level = int((int(int(xp[0])) + int(xp_addition))**(1 / 4))
                cur.execute('SELECT level FROM rankings WHERE user_id = ?',(str(user.id), ))
                level = cur.fetchone()
                cur.execute('UPDATE rankings SET level = {new_level} WHERE user_id = ? '.format(new_level=new_level), (str(user.id), ))
                if new_level > int(level[0]):
                    channel = bot.get_channel(988718132841562112)
                    await channel.send('Congratulations!! <@{user}> you have leveled up to **lvl.{level}**'.format(user=str(user.id), level=new_level))
                rank_list = []
                rank_num = 0
                for rank_extract in cur.execute('SELECT xp, user_id from rankings ORDER BY xp'):
                    rank_list.append(rank_extract)
                    rank_num = rank_num + 1
                rank_list.sort(reverse=True)
                for i in range(rank_num):
                    new_rank = i + 1
                    cur.execute('UPDATE rankings SET rank = {new_rank} WHERE user_id = ? '.format(new_rank=new_rank), (str(user.id), ))
                await context.channel.send('Added {xp_addition} xp to <@{user_id}> !'.format(user_id=int(user.id), xp_addition=xp_addition))
    
            conn.commit()
            cur.close()
        else:
            await context.channel.send("Can't give xp to a bot")


@givexp.error
async def givexp_error(ctx, error):
    if isinstance(error, MissingPermissions):
        em = discord.Embed(title=f"Watch out !",
                           description="This is a admin only command !",
                           color=0xFF5733)
        await ctx.send(embed=em)


@bot.command(aliases=['rx'], case_insensitive=True)
@commands.has_permissions(administrator=True)
async def resetxp(context, user: discord.Member = None):
  if user is None :
    await context.channel.send('Please mention a user')
  else :
        print("xp reseted")
        human_memebers = []
        for bot_check in list(context.guild.members):
            if bot_check.bot:
                continue
            else:
                human_memebers.append(bot_check)
    
        conn = sqlite3.connect('user_level_data.sqlite', timeout=20)
        cur = conn.cursor()
        cur.execute('SELECT xp FROM rankings WHERE user_id = ?', (str(user.id), ))
        xp = cur.fetchone()
        print("line 1")
        if user in human_memebers:
            if xp is None:
                await context.channel.send('User <@{user_id}> is not registered, you need to have texted atleast once in the server to register yourself !'.format(user_id=int(user.id)))
            else:
                print("line 2")
                cur.execute('DELETE FROM rankings WHERE user_id = ?',(str(user.id), ))
                print("line 3")
                conn.commit
                print("line 4")
                cur.execute('INSERT INTO rankings (rank, user_id, level, xp, awarded_role, rank_role) VALUES (0, {user}, 1, 1, 989839086036611092, 0)'.format(user=str(user.id)))
                print("line 5")
                role = context.guild.get_role(989839086036611092)
                print("line 6")
                await user.add_roles(role)
                print("line 7")
                await context.channel.send('Succsefullly reseted xp info of user <@{user}>'.format(user=str(user.id)))
        else:
            await context.channel.send("Can't reset bot's xp")
        conn.commit()
        cur.close()



@resetxp.error
async def resetxp_error(ctx, error):
    if isinstance(error, MissingPermissions):
        em = discord.Embed(title=f"Watch out !",
                           description="This is a admin only command !",
                           color=0xFF5733)
        await ctx.send(embed=em)


@bot.command(aliases=['sl'], case_insensitive=True)
@commands.has_permissions(administrator=True)
async def setlevel(context, user: discord.Member = None, *, set_level = None):
  if user is None :
   await context.channel.send('Please mention a user')
  elif set_level is None :
    await context.channel.send('Please mention Level')
  else :
        print("level setted to {set_level}".format(set_level=set_level))
        human_memebers = []
        for bot_check in list(context.guild.members):
            if bot_check.bot:
                continue
            else:
                human_memebers.append(bot_check)
    
        conn = sqlite3.connect('user_level_data.sqlite', timeout=20)
        cur = conn.cursor()
        cur.execute('SELECT xp FROM rankings WHERE user_id = ?', (str(user.id), ))
        xp = cur.fetchone()
        if user in human_memebers :
          if xp is None:
              await context.channel.send('User <@{user_id}> is not registered, you need to have texted atleast once in the server to register yourself!'.format(user_id=int(user.id)))
          else:
              print('setting')
              new_xp = int(set_level)**4
              cur.execute('UPDATE rankings SET xp = {new_xp} WHERE user_id = ? '.format(new_xp=new_xp),(str(user.id),))
              new_level = int(set_level)
              cur.execute('SELECT level FROM rankings WHERE user_id = ?',(str(user.id), ))
              level = cur.fetchone()
              cur.execute('UPDATE rankings SET level = {new_level} WHERE user_id = ? '.format(new_level=new_level),(str(user.id), ))
              if new_level > int(level[0]):
                  channel = bot.get_channel(988718132841562112)
                  await channel.send('Congratulations!! <@{user}> you have leveled up to **{level}**'.format(user=str(user.id), level=new_level))    
              conn.commit()
              rank_list = []
              rank_num = 0
              for rank_extract in cur.execute('SELECT xp, user_id from rankings ORDER BY xp'):
                        
                        rank_list.append(rank_extract)
                        rank_num = rank_num + 1
              rank_list.sort(reverse=True)
              for i in range(rank_num):
                        user_id = rank_list[i][1]
                        new_rank = i + 1
                        cur.execute('UPDATE rankings SET rank = {new_rank} WHERE user_id = ? '.format(new_rank=new_rank), (str(user_id), ))
              
              await context.channel.send("Succsesfully set level <@{user_id}> to {set_level} !".format(user_id=int(user.id), set_level=set_level))
              
          conn.commit()
          cur.close()


        else :
          await context.channel.send("Can't set a bot's level !")
@setlevel.error
async def setlevel_error(ctx, error):
    if isinstance(error, MissingPermissions):
        em = discord.Embed(title=f"Watch out !",
                           description="This is a admin only command !",
                           color=0xFF5733)
        await ctx.send(embed=em)


keep_alive()
token = os.environ['TOKEN']
bot.run(token)
