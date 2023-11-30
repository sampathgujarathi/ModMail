import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from datetime import datetime
import json
from pydbjson.pydbjson import pydbjson
import time
import psutil
import platform
import config as config
bot = commands.Bot(command_prefix='.', intents=discord.Intents().all(), help_command=None)
db = pydbjson("database.json")
bot.launch_time = datetime.utcnow()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Workshop"))
    print(f'Bot is ready.')
    
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Commands",color=discord.Color.blurple())
    embed.description = "`.ban`\n`.kick`\n`.timeout`\n`.stats`\n"
    await ctx.send(embed=embed)
    
@bot.command(aliases=["b","B"])
@has_permissions(ban_members=True)
async def ban(ctx,user:discord.Member,reason=None):
    embed = discord.Embed(description=f"{user} is successfully banned.",color=discord.Color.green())
    await ctx.send(embed=embed)
    await user.ban(reason=reason)
    
@bot.command(aliases=["k","K"])
@has_permissions(kick_members=True)
async def kick(ctx,user:discord.Member,reason=None):
    embed = discord.Embed(description=f"{user} is successfully kicked.",color=discord.Color.green())
    await ctx.send(embed=embed)
    await user.kick(reason=reason)

@bot.command(aliases=["t","T"])
async def timeout(ctx,user:discord.Member,min=1440,reason=None):
    until = discord.utils.utcnow() + datetime.timedelta(minutes=min)
    embed = discord.Embed(description=f"{user} is successfully timeout till <t:{until}>.",color=discord.Color.green())
    await ctx.send(embed=embed)
    await user.timeout(until)

@bot.command()
async def status(ctx,status_type:str,status):
    if status == None:
        status = f"{ctx.guild.name}"
    if status_type == "w":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=status))
    elif status_type == "l":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name=status))
    elif status_type == "c":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing,name=status))
    elif status_type == "s":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming,name=status, url=f"twitch.tv/{status}"))
    embed = discord.Embed(description=f"Successfully changed my status to {status} in {status_type}.",color=discord.Color.green())
    await ctx.send(embed=embed)
    
@bot.command(aliases=['p'])
async def stats(ctx):
    embed = discord.Embed(color=discord.Color.green())
    users = len(bot.users)
    delta_uptime = datetime.utcnow() - bot.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    cpu_percent = psutil.cpu_percent()
    os_name = platform.system()
    os_release = platform.release()
    cpu_name = platform.processor()
    cpu_model = " ".join(cpu_name.split()[:3])
    cpu_speed = "{:.2f} GHz".format(psutil.cpu_freq().current/1000)
    uptime = f"{days} Days {hours} Hours {minutes} Minutes"    
    embed.add_field(name='General', value=f"**Users Count:** {users}\n**Ping:** {bot.ws.latency * 1000:.0f} ms\n**Pycord:** v2.4.1")
    embed.add_field(name='System', value=f"**Operating System:** {os_name}\n**CPU Info:**\n**Model:** {cpu_model}\n**Speed:** {cpu_speed}\n**Useage:** {cpu_percent}%")
    embed.add_field(name='Uptime', value=f"```{uptime}```",inline=False)
    embed.set_author(name=ctx.author.display_name,icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)
    
@bot.command(aliases=["c","C"])
@has_permissions(kick_members=True)
async def close(ctx,reason=None):
    data = db.find_one({"user":int(ctx.channel.name[7:])})
    print(data)
    embed = discord.Embed(description=f"Closing this thread.",color=discord.Color.green())
    await ctx.send(embed=embed)
    embed = discord.Embed(title=f"Ticket Closed",color=discord.Color.green())
    embed.add_field(name="Opened By",value=f"<@!{ctx.channel.name[7:]}>")
    embed.add_field(name="Closed By",value=f"{ctx.author.mention}")
    embed.add_field(name="Open Time",value=f"<t:{data[1]['created_time']}>")
    embed.add_field(name="Reason",value=f"{reason}")
    user = bot.get_user(int(ctx.channel.name[7:]))
    channel = bot.get_channel(int(data[1]['channel']))
    thread = channel.get_thread(int(data[1]['ticket']))
    await thread.edit(archived=True,locked=True)
    await user.send(embed=embed)
    db.delete_one(data[0])

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    

    if isinstance(message.channel, discord.DMChannel):
        guild = bot.get_guild(config.GUILD_ID)
        channel = bot.get_channel(config.TICKET_CHANNEL_ID)
        thread_id = db.find_one({'user':str(message.author.id)})
        if thread_id:
            threads = channel.get_thread(thread_id)
            if threads != None:
                embed = discord.Embed(description=message.content, colour=0xFEE75C)
                embed.set_author(name=message.author, icon_url=message.author.avatar.url)
                await threads.send(embed=embed)
                return

        await message.add_reaction('👍')
        stafembed = discord.Embed(description=f"{message.author.mention} has created a Thread", color=0x5865F2)
        stafembed.set_author(name=message.author, icon_url=message.author.avatar.url)
        stafembed.set_footer(text=f"User ID: {message.author.id}")
        stafembed.timestamp = datetime.now()
        msg = await channel.send(embed=stafembed)
        thread = await msg.create_thread(
            name=f"ticket-{message.author.id}"
        )
        roles_to_ping = ""
        for roles in config.TICKET_SUPPORT_IDS_TO_MENTION:
            try:
                role_ = guild.get_role(int(roles))
                roles_to_ping += f"{role_.mention},"
            except Exception as e:
                print(f"[ERROR] {e}")
        await thread.send(f"{roles_to_ping} {message.author.mention} has created a thread.")
        embed1 = discord.Embed(description=message.content, colour=0xFEE75C)
        embed1.set_author(name=message.author, icon_url=message.author.avatar.url)
        await threads.send(embed=embed1)

        db.insert_one({"user": message.author.id, "ticket": thread.id, "created_time":int(time.time()), "channel":channel.id})

        embed = discord.Embed(title="Thread Created", description="The staff team will get back to you as soon as possible.", color=0x5865F2)
        await message.author.send(embed=embed)
        return

    elif isinstance(message.channel, discord.Thread):
        if message.content.startswith(bot.command_prefix):
            pass
        else:
            topic = message.channel.name
            if topic.startswith("ticket-"):
                member = message.guild.get_member(int(topic[7:]))
                if member:
                    await message.add_reaction('👍')
                    embed = discord.Embed(description=message.content, colour=0x57F287)
                    embed.set_author(name=message.author, icon_url=message.author.avatar.url)
                    await member.send(embed=embed)
                    return
    await bot.process_commands(message)

bot.run(config.BOT_TOKEN)
